from ..datatypes.color3 import Color3
from .Signal import Signal
from .mixins.EventHandlerMixin import EventHandlerMixin
from .Decorators import OnEvent
import pygame

# Position spéciale SDL : centrer la fenêtre sur l'écran n (SDL_WINDOWPOS_CENTERED_DISPLAY).
# pygame.WINDOWPOS_CENTERED vaut cette valeur pour l'écran 0.
def _CenteredOnDisplay(display : int) -> int:
    return pygame.WINDOWPOS_CENTERED | display


class _GuiService:
    """Gère les ScreenGui de l'application : ordre (DisplayOrder), dessin, accès pour la souris."""

    def __init__(self):
        self._Screens : list = []          # list[ScreenGui] (import évité : widgets dépend de core)
        self._Sorted = True

    ##TODO: place args checker
    def Add(self, screen):
        if screen in self._Screens:
            return
        self._Screens.append(screen)
        screen._Service = self             # pour que ScreenGui.DisplayOrder puisse demander un nouveau tri
        self._Sorted = False

    def Remove(self, screen):
        if screen in self._Screens:
            self._Screens.remove(screen)
            screen._Service = None

    def _SortedScreens(self):
        if not self._Sorted:
            self._Screens.sort(key=lambda s:s.DisplayOrder)
            self._Sorted = True
        return self._Screens

    def Draw(self, surface):
        for screen in self._SortedScreens():
            if not screen.Enabled:
                continue
            screen.Draw(surface)

    def MarkDirty(self):
        """Taille de la fenêtre changée : toutes les positions en Scale sont à recalculer."""
        for screen in self._Screens:
            screen._MarkDirty()

    @property
    def Children(self):
        """ScreenGui activés, du plus bas au plus haut : ce que l'EventManager parcourt."""
        return [s for s in self._SortedScreens() if s.Enabled]

    Visible = True                          # l'EventManager traite le service comme une racine


class Application(EventHandlerMixin):
    """Point d'entrée de la lib : possède la fenêtre, la racine de l'interface et la boucle.

    Toutes les propriétés ont une valeur par défaut et peuvent être passées au constructeur :
        app = Application("Ever Oasis Studio", Size=(1280, 720), MinimumSize=(800, 600))
    Elles sont mémorisées et appliquées à la création de la fenêtre, dans run().
    """

    Current : "Application" = None

    def __init__(self, title : str = "Pygame Easy GUI", **props):
        # ---- Fenêtre : identité
        self.Title : str = title
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
        self.BackgroundColor3 : Color3 = Color3.fromRgb(30, 30, 30)
        self.MaxFPS : int = 60

        # ---- État interne (rempli par run())
        self.Window : pygame.Window | None = None
        self.Surface : pygame.Surface | None = None
        self.Clock = pygame.time.Clock()
        self.Running : bool = False
        self._NeedsRedraw : bool = True

        # ---- lib define
        self.AbsoluteSize : tuple[int, int] = self.Size      # taille réelle, mise à jour par _OnResize
        self.Gui = _GuiService()                             # app.Gui.Add(screen_gui)
        self.EventManager = None                             # créé dans run()

        # ---- Event Variable
        self.EventTimeOut = 1

        # ---- Event Signal
        self.Resized = Signal()
        self.FocusLost = Signal()
        self.FocusGained = Signal()
        self.Closing = Signal()

        self._ApplyProps(props)

    def _ApplyProps(self, props : dict):
        """Applique les propriétés passées au constructeur. Refuse les noms inconnus,
        pour qu'une faute de frappe (ex. Tilte=...) ne passe pas inaperçue."""
        for name, value in props.items():
            if name.startswith("_") or not hasattr(self, name):
                raise AttributeError(f"Application n'a pas de propriété {name!r}")
            setattr(self, name, value)

    @OnEvent(pygame.QUIT)
    def _OnQuit(self, event):
        self.Running = False

    @OnEvent(pygame.WINDOWEXPOSED)
    def _OnWindowExposed(self, event):
        self._NeedsRedraw = True

    @OnEvent(pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED)
    def _OnResize(self, event):
        self.Surface = self.Window.get_surface()
        self.AbsoluteSize = self.Surface.size
        self.Gui.MarkDirty()
        self.Resized.Fire(self.AbsoluteSize)
        self.RequestRedraw()

    def setTitle(self, string):
        self.Title = string
        if self.Window is not None:
            self.Window.title = string

    def _CreateWindow(self):
        """Crée la fenêtre à partir des propriétés mémorisées."""
        position = self.Position if self.Position is not None else _CenteredOnDisplay(self.Display)

        self.Window = pygame.Window(
            self.Title,
            self.Size,
            position,
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
        self.AbsoluteSize = self.Surface.size    # peut différer de Size (maximisée, plein écran…)

    def RequestRedraw(self):
        """Demande un redessin. Pour l'instant on redessine à chaque tour : sera utilisé
        par la boucle optimisée (voir todo/application, étape 3)."""
        if not Application.Current:
            return
        self._NeedsRedraw = True

    def _Draw(self):
        self.Surface.fill(self.BackgroundColor3.ToPygame())
        self.Gui.Draw(self.Surface)
        self._NeedsRedraw = False

    def _getEvent(self, delay : int):
        """Temps en seconde"""
        if delay < 0:
            return pygame.event.get()
        else:
            first = pygame.event.wait(max(1, int(delay * 1000)))
            return ([first] if first.type != pygame.NOEVENT else []) + pygame.event.get()

    def run(self):
        pygame.init()
        self._CreateWindow()
        from .EventManager import EventManager    # import dans la fonction : event_manager importe gui_object
        self.EventManager = EventManager(self.Gui)
        self.Running = True
        Application.Current = self
        try:
            while self.Running:

                events = self._getEvent(self.EventTimeOut)
                for event in events:
                    self._HandleEvent(event)
                self.EventManager.Update(events)

                dt = self.Clock.tick(self.MaxFPS) / 1000
                for screen in self.Gui.Children:
                    screen.Update(dt)

                if self._NeedsRedraw:
                    self._Draw()
                    self.Window.flip()
        finally:
            Application.Current = None
            self.EventManager = None
            self.Running = False
            self.Window.destroy()
            self.Window = None
            self.Surface = None
            pygame.quit()

