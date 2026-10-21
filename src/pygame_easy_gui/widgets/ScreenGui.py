import pygame
from pygame_easy_gui.core.GuiObject import GuiObject
from pygame_easy_gui.datatypes.udim import Udim2
from pygame_easy_gui.core.EventManager import EventManager
from pygame_easy_gui.services.TweenService import TweenService
from pygame_easy_gui.render import Display

MAX_DIRTY_RECTS = 24          # au-delà, les zones sont fusionnées en une seule
FULL_REDRAW_RATIO = 0.6       # si les zones couvrent plus de 60% de l'écran, on redessine tout d'un coup


def _MergeRects(Rects : list[pygame.Rect], ScreenRect : pygame.Rect) -> list[pygame.Rect]:
    """Coupe les zones à l'écran et fusionne celles qui se chevauchent (chaque pixel n'est redessiné qu'une fois)"""
    Result = []
    for Rect in Rects:
        Rect = Rect.clip(ScreenRect)
        if Rect.width <= 0 or Rect.height <= 0:
            continue
        Index = Rect.collidelist(Result)
        while Index != -1:
            Rect = Rect.union(Result.pop(Index))
            Index = Rect.collidelist(Result)
        Result.append(Rect)

    if len(Result) > MAX_DIRTY_RECTS:
        Result = [Result[0].unionall(Result[1:])]
    if sum(Rect.width * Rect.height for Rect in Result) > ScreenRect.width * ScreenRect.height * FULL_REDRAW_RATIO:
        return [ScreenRect.copy()]
    return Result


class ScreenGui(GuiObject):
    """
    Racine d'une interface : prend tout l'écran, gère les events, le redimensionnement de la fenêtre et le focus.
    Seules les zones qui changent sont redessinées (dirty rects) : un objet immobile n'est jamais redessiné.

    USAGE dans la boucle d'un jeu (l'écran est entièrement redessiné à chaque frame) :
        Events = Gui.HandleEvents(pygame.event.get())   # retourne les events non consommés par la GUI
        Gui.Update(Dt)
        Screen.fill(...)  /  dessin du jeu
        Gui.Draw(Screen)        # la GUI est gardée dans un calque, mis à jour seulement là où elle change
        pygame.display.flip()

    USAGE pour une appli (rien ne bouge derrière la GUI) :
        Rects = Gui.Render(Screen, Background=(30, 30, 30))
        pygame.display.update(Rects)  # seules les zones modifiées sont envoyées à la fenêtre
    """
    def __init__(self):
        # Avant super().__init__() : les propriétés assignées dans GuiObject s'enregistrent déjà ici
        self._DirtyObjects : dict[GuiObject, None] = {}
        self._DirtyRects : list[pygame.Rect] = []
        self._FullRedraw = True
        self._Layer : pygame.Surface | None = None
        self._RenderTarget = None
        self._Service = None   # gestionnaire des ScreenGui de l'Application (voir Application.Gui)
        super().__init__()
        self.Name = "ScreenGui"
        self.Size = Udim2(1, 0, 1, 0)
        self.Enabled = True
        self.DisplayOrder = 0
        self.EventManager = EventManager(self)
        self._LastScreenSize = None

    @property
    def Enabled(self) -> bool:
        return self._Enabled

    @Enabled.setter
    def Enabled(self, Value : bool):
        self._Enabled = Value
        self._FullRedraw = True
        if self._Service is not None:
            self._Service.ForceRedraw()

    @property
    def DisplayOrder(self) -> int:
        """Dans une Application : le ScreenGui avec le plus grand DisplayOrder est dessiné au-dessus des autres"""
        return self._DisplayOrder

    @DisplayOrder.setter
    def DisplayOrder(self, Value : int):
        self._DisplayOrder = Value
        if self._Service is not None:
            self._Service._Sorted = False
            self._Service.ForceRedraw()

    def ForceRedraw(self):
        """Redessine toute la GUI au prochain rendu (ex: le fond donné à Render a changé)"""
        self._FullRedraw = True

    def _RegisterRenderDirty(self, Obj : GuiObject):
        if Obj in self._DirtyObjects:
            return
        self._DirtyObjects[Obj] = None
        # L'ancienne zone doit être effacée, même si l'objet bouge ou disparaît avant le rendu
        if Obj._LastDrawRect:
            self._DirtyRects.append(Obj._LastDrawRect)

    def _CheckScreenSize(self):
        Size = Display.GetSize()
        if Size != self._LastScreenSize:
            self._LastScreenSize = Size
            self._MarkDirty()
            self._FullRedraw = True

    def _TakeDirtyRects(self, ScreenRect : pygame.Rect) -> list[pygame.Rect]:
        """Zones à redessiner depuis le dernier rendu : ancienne + nouvelle zone de chaque objet modifié"""
        Objects, Rects = self._DirtyObjects, self._DirtyRects
        self._DirtyObjects, self._DirtyRects = {}, []
        if self._FullRedraw:
            self._FullRedraw = False
            return [ScreenRect.copy()]

        for Obj in Objects:
            if Obj._Destroyed or Obj._GetRoot() is not self:
                continue
            Bounds = Obj._GetScreenBounds()
            Obj._LastDrawRect = Bounds
            if Bounds:
                Rects.append(Bounds)
        return _MergeRects(Rects, ScreenRect)

    def _RedrawRegions(self, Surface : pygame.Surface, Rects : list[pygame.Rect], Background):
        OldClip = Surface.get_clip()
        for Rect in Rects:
            Surface.set_clip(Rect)
            if isinstance(Background, pygame.Surface):
                Surface.blit(Background, Rect, Rect)
            elif Background is not None:
                Surface.fill(Background, Rect)
            self._DrawRegion(Surface, Rect, None)
        Surface.set_clip(OldClip)

    def HandleEvents(self, Events : list, MouseBlocked : bool = False) -> list:
        if not self.Enabled:
            return list(Events)
        self._CheckScreenSize()
        return self.EventManager.Update(Events, MouseBlocked)

    def IsMouseOverGui(self) -> bool:
        return self.Enabled and self.EventManager.IsMouseOverGui()

    def GetFocusedObject(self) -> GuiObject | None:
        return self.EventManager.FocusedObject

    def Update(self, Dt : float):
        # Les tweens tournent même si cette GUI est désactivée (ils peuvent animer d'autres objets)
        TweenService.Step()
        if self.Enabled:
            self._CheckScreenSize()
            super().Update(Dt)

    def Draw(self, Surface : pygame.Surface) -> list[pygame.Rect]:
        """
        Pour un jeu qui redessine tout l'écran à chaque frame.
        La GUI est rendue dans un calque transparent mis en cache : seules les zones modifiées y sont redessinées,
        puis le calque est collé sur Surface en un seul blit. Retourne les zones redessinées dans le calque.
        """
        if not self.Enabled:
            return []
        self._CheckScreenSize()
        Size = Surface.get_size()
        if self._Layer is None or self._Layer.get_size() != Size:
            self._Layer = Display.Optimize(pygame.Surface(Size, pygame.SRCALPHA))
            self._FullRedraw = True

        Rects = self._TakeDirtyRects(self._Layer.get_rect())
        self._RedrawRegions(self._Layer, Rects, (0, 0, 0, 0))
        Surface.blit(self._Layer, (0, 0))
        return Rects

    def Render(self, Surface : pygame.Surface, Background = (0, 0, 0)) -> list[pygame.Rect]:
        """
        Pour une appli dont le fond ne bouge pas : redessine directement sur Surface uniquement les zones modifiées.
        Background : couleur ou pygame.Surface (de la taille de l'écran) remis sous la GUI avant de la redessiner.
        Retourne les zones modifiées, à donner à pygame.display.update(Rects).
        Si le fond change, appeler ForceRedraw().
        """
        Target = (Surface, Surface.get_size())
        if Target != self._RenderTarget:
            self._RenderTarget = Target
            self._FullRedraw = True

        ScreenRect = Surface.get_rect()
        if not self.Enabled:
            # Efface la GUI une seule fois quand elle est désactivée
            if not self._FullRedraw:
                return []
            self._FullRedraw = False
            if isinstance(Background, pygame.Surface):
                Surface.blit(Background, (0, 0))
            elif Background is not None:
                Surface.fill(Background)
            return [ScreenRect]

        self._CheckScreenSize()
        Rects = self._TakeDirtyRects(ScreenRect)
        self._RedrawRegions(Surface, Rects, Background)
        return Rects
