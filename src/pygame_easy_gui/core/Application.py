import pygame
from pygame_easy_gui.datatypes.color3 import Color3
from pygame_easy_gui.core.Signal import Signal
from pygame_easy_gui.core.mixins.EventHandlerMixin import EventHandlerMixin
from pygame_easy_gui.core.Decorators import OnEvent
from pygame_easy_gui.render import Display
from pygame_easy_gui.services.TweenService import TweenService

CURSOR_BLINK_WAIT = 0.1   # attente max entre deux tours quand une TextBox a le focus (clignotement du curseur)


# Position spéciale SDL : centrer la fenêtre sur l'écran n (SDL_WINDOWPOS_CENTERED_DISPLAY).
# pygame.WINDOWPOS_CENTERED vaut cette valeur pour l'écran 0.
def _CenteredOnDisplay(DisplayIndex : int) -> int:
    return pygame.WINDOWPOS_CENTERED | DisplayIndex


class _GuiService:
    """
    Gère les ScreenGui de l'application : ordre (DisplayOrder), événements, mise à jour et dessin.
    Les événements vont du ScreenGui le plus haut au plus bas : ce qu'un ScreenGui consomme n'arrive pas aux autres.
    Le dessin ne refait que les zones modifiées, tous ScreenGui confondus.
    """

    def __init__(self):
        self._Screens : list = []          # list[ScreenGui] (import évité : widgets dépend de core)
        self._Sorted = True
        self._FullRedraw = True

    def Add(self, Screen):
        if Screen in self._Screens:
            return
        if Screen._Service is not None:
            Screen._Service.Remove(Screen)
        self._Screens.append(Screen)
        Screen._Service = self             # pour que ScreenGui.DisplayOrder puisse demander un nouveau tri
        self._Sorted = False
        self.ForceRedraw()

    def Remove(self, Screen):
        if Screen in self._Screens:
            self._Screens.remove(Screen)
            Screen._Service = None
            self.ForceRedraw()

    def GetScreens(self) -> list:
        """ScreenGui du plus bas au plus haut"""
        if not self._Sorted:
            self._Screens.sort(key=lambda Screen: Screen.DisplayOrder)
            self._Sorted = True
        return list(self._Screens)

    def ForceRedraw(self):
        self._FullRedraw = True

    def MarkDirty(self):
        """Taille de la fenêtre changée : toutes les positions en Scale sont à recalculer."""
        for Screen in self._Screens:
            Screen._MarkDirty()
        self.ForceRedraw()

    def IsMouseOverGui(self) -> bool:
        return any(Screen.IsMouseOverGui() for Screen in self._Screens)

    def GetFocusedObject(self):
        for Screen in reversed(self.GetScreens()):
            Focused = Screen.GetFocusedObject() if Screen.Enabled else None
            if Focused is not None:
                return Focused
        return None

    def HandleEvents(self, Events : list) -> list:
        """Retourne les événements qu'aucun ScreenGui n'a consommés"""
        MouseBlocked = False
        for Screen in reversed(self.GetScreens()):
            Events = Screen.HandleEvents(Events, MouseBlocked)
            MouseBlocked = MouseBlocked or Screen.IsMouseOverGui()
        return Events

    def Update(self, Dt : float):
        TweenService.Step()
        for Screen in self.GetScreens():
            Screen.Update(Dt)

    def Render(self, Surface : pygame.Surface, Background) -> list[pygame.Rect]:
        """Redessine les zones modifiées de tous les ScreenGui ; retourne ces zones"""
        from pygame_easy_gui.widgets.ScreenGui import _MergeRects   # widgets dépend de core : import ici
        ScreenRect = Surface.get_rect()
        Screens = self.GetScreens()
        Rects = []
        for Screen in Screens:
            Screen._CheckScreenSize()
            # Toujours vidé, même désactivé, pour ne pas accumuler de zones
            Taken = Screen._TakeDirtyRects(ScreenRect)
            if Screen.Enabled:
                Rects.extend(Taken)
        if self._FullRedraw:
            self._FullRedraw = False
            Rects = [ScreenRect]
        else:
            Rects = _MergeRects(Rects, ScreenRect)

        OldClip = Surface.get_clip()
        for Rect in Rects:
            Surface.set_clip(Rect)
            Surface.fill(Background, Rect)
            for Screen in Screens:
                if Screen.Enabled:
                    Screen._DrawRegion(Surface, Rect, None)
        Surface.set_clip(OldClip)
        return Rects

    @property
    def Children(self):
        """ScreenGui activés, du plus bas au plus haut"""
        return [Screen for Screen in self.GetScreens() if Screen.Enabled]


class Application(EventHandlerMixin):
    """Point d'entrée de la lib : possède la fenêtre, les ScreenGui et la boucle.

    Toutes les propriétés ont une valeur par défaut et peuvent être passées au constructeur :
        MyApp = Application("Ever Oasis Studio", Size=(1280, 720), MinimumSize=(800, 600))
        Hud = ScreenGui.New(Name="HUD")
        MyApp.Gui.Add(Hud)
        MyApp.run()
    Elles sont mémorisées et appliquées à la création de la fenêtre, dans run().

    La boucle ne fait rien tant que rien ne se passe (attente des événements, voir EventTimeOut),
    et seules les zones modifiées de l'interface sont redessinées.
    """

    Current : "Application" = None

    def __init__(self, Title : str = "Pygame Easy GUI", **Props):
        # ---- Fenêtre : identité
        self.Title : str = Title
        self.Icon : pygame.Surface | None = None

        # ---- Fenêtre : taille et position
        self.Size : tuple[int, int] = (1280, 720)
        self.MinimumSize : tuple[int, int] = (0, 0)          # (0, 0) = pas de minimum
        self.MaximumSize : tuple[int, int] = (0, 0)          # (0, 0) = pas de maximum
        self.Position : tuple[int, int] | None = None        # None = centrée sur Display
        self.Display : int = 0                               # écran utilisé quand Position vaut None

        # ---- Fenêtre : état au démarrage
        self.Resizable : bool = True
        self.Borderless : bool = False                       # pas de barre de titre ni de bordure
        self.Fullscreen : bool = False                       # plein écran à la résolution du bureau
        self.Maximized : bool = False
        self.Hidden : bool = False                           # fenêtre créée invisible (show() plus tard)
        self.AlwaysOnTop : bool = False
        self.Opacity : float = 1.0                           # 0 = transparente, 1 = opaque
        self.AllowHighDpi : bool = False

        # ---- Fenêtre : saisie
        self.MouseGrabbed : bool = False                     # la souris reste dans la fenêtre
        self.KeyboardGrabbed : bool = False                  # capte les raccourcis système (Alt+Tab…)

        # ---- Rendu et boucle
        self.BackgroundColor3 : Color3 = Color3(30, 30, 30)
        self.MaxFPS : int = 60
        self.EventTimeOut : float = 1.0                      # attente max (secondes) d'un événement quand rien n'est animé

        # ---- État interne (rempli par run())
        self.Window : pygame.Window | None = None
        self.Surface : pygame.Surface | None = None
        self.Clock = pygame.time.Clock()
        self.Running : bool = False

        # ---- Interface
        self.AbsoluteSize : tuple[int, int] = self.Size      # taille réelle, mise à jour par _OnResize
        self.Gui = _GuiService()                             # MyApp.Gui.Add(ScreenGui)

        # ---- Signaux
        self.Resized = Signal()          # (Taille)
        self.FocusLost = Signal()
        self.FocusGained = Signal()
        self.Closing = Signal()
        self.Heartbeat = Signal()        # (Dt) à chaque tour de boucle
        self.UnhandledEvent = Signal()   # (Event) : événements pygame que la GUI n'a pas consommés

        self._ApplyProps(Props)

    def _ApplyProps(self, Props : dict):
        """Applique les propriétés passées au constructeur. Refuse les noms inconnus,
        pour qu'une faute de frappe (ex. Tilte=...) ne passe pas inaperçue."""
        for Name, Value in Props.items():
            if Name.startswith("_") or not hasattr(self, Name):
                raise AttributeError(f"Application n'a pas de propriété {Name!r}")
            setattr(self, Name, Value)

    @OnEvent(pygame.QUIT)
    def _OnQuit(self, Event):
        self.Closing.Fire()
        self.Running = False

    @OnEvent(pygame.WINDOWEXPOSED)
    def _OnWindowExposed(self, Event):
        self.RequestRedraw()

    @OnEvent(pygame.WINDOWFOCUSGAINED)
    def _OnFocusGained(self, Event):
        self.FocusGained.Fire()

    @OnEvent(pygame.WINDOWFOCUSLOST)
    def _OnFocusLost(self, Event):
        self.FocusLost.Fire()

    @OnEvent(pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED)
    def _OnResize(self, Event):
        self.Surface = self.Window.get_surface()
        Display.SetSurface(self.Surface)
        self.AbsoluteSize = self.Surface.get_size()
        self.Gui.MarkDirty()
        self.Resized.Fire(self.AbsoluteSize)

    def setTitle(self, Value : str):
        self.Title = Value
        if self.Window is not None:
            self.Window.title = Value

    def Stop(self):
        """Ferme l'application à la fin du tour de boucle en cours"""
        self.Running = False

    def RequestRedraw(self):
        """Redessine toute l'interface au prochain tour (ex: après avoir dessiné soi-même sur la fenêtre)"""
        self.Gui.ForceRedraw()

    def _CreateWindow(self):
        """Crée la fenêtre à partir des propriétés mémorisées."""
        WindowPosition = self.Position if self.Position is not None else _CenteredOnDisplay(self.Display)

        self.Window = pygame.Window(
            self.Title,
            self.Size,
            WindowPosition,
            resizable=self.Resizable,
            borderless=self.Borderless,
            fullscreen_desktop=self.Fullscreen,
            maximized=self.Maximized,
            hidden=self.Hidden,
            always_on_top=self.AlwaysOnTop,
            allow_high_dpi=self.AllowHighDpi,
            mouse_grabbed=self.MouseGrabbed,
            keyboard_grabbed=self.KeyboardGrabbed,
        )
        self.Window.minimum_size = self.MinimumSize
        if self.MaximumSize != (0, 0):  # (0, 0) serait refusé s'il est plus petit que MinimumSize
            self.Window.maximum_size = self.MaximumSize
        if self.Icon is not None:
            self.Window.set_icon(self.Icon)
        if self.Opacity < 1.0:
            try:
                self.Window.opacity = self.Opacity
            except pygame.error:
                pass  # non pris en charge par certains systèmes ou pilotes : on reste opaque

        self.Surface = self.Window.get_surface()
        Display.SetSurface(self.Surface)
        self.AbsoluteSize = self.Surface.get_size()    # peut différer de Size (maximisée, plein écran…)

    def _GetWaitTime(self) -> float:
        """Temps max d'attente d'un événement : 0 pendant une animation, court si un curseur clignote"""
        if TweenService.GetPlayingTweens():
            return 0.0
        if self.Gui.GetFocusedObject() is not None:
            return min(self.EventTimeOut, CURSOR_BLINK_WAIT)
        return self.EventTimeOut

    def _GetEvents(self, Delay : float) -> list:
        """Delay en secondes : attend au plus Delay qu'un événement arrive (0 = n'attend pas)"""
        if Delay <= 0:
            return pygame.event.get()
        First = pygame.event.wait(max(1, int(Delay * 1000)))
        return ([First] if First.type != pygame.NOEVENT else []) + pygame.event.get()

    def _Step(self):
        """Un tour de boucle : événements, mise à jour, dessin"""
        Events = self._GetEvents(self._GetWaitTime())
        for Event in Events:
            self._HandleEvent(Event)
        for Event in self.Gui.HandleEvents(Events):
            self.UnhandledEvent.Fire(Event)

        Dt = self.Clock.tick(self.MaxFPS) / 1000
        self.Heartbeat.Fire(Dt)
        self.Gui.Update(Dt)

        if self.Gui.Render(self.Surface, self.BackgroundColor3):
            self.Window.flip()

    def run(self):
        pygame.init()
        self._CreateWindow()
        self.Running = True
        Application.Current = self
        self.Gui.ForceRedraw()
        try:
            while self.Running:
                self._Step()
        finally:
            Application.Current = None
            Display.SetSurface(None)
            self.Running = False
            self.Window.destroy()
            self.Window = None
            self.Surface = None
            pygame.quit()

    Run = run   # même style que le reste de l'API
