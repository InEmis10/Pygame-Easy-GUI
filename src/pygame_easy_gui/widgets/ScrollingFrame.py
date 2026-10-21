import pygame
from pygame_easy_gui.widgets.Frame import Frame
from pygame_easy_gui.datatypes.udim import Udim2
from pygame_easy_gui.datatypes.vector2 import Vector2
from pygame_easy_gui.components.UIPadding import UIPadding
from pygame_easy_gui.render.Draw import DrawRect


class ScrollingFrame(Frame):
    """
    Frame défilante : les enfants sont placés dans un canvas (CanvasSize) plus grand que la frame.
    Défilement à la molette, ou en glissant les barres de défilement.
    CanvasSize : Scale = relatif à la taille de la frame.
    AutomaticCanvasSize : agrandit le canvas pour contenir les enfants ("none" | "x" | "y" | "xy").
    """
    def __init__(self):
        self._CanvasCache = None
        super().__init__()
        self.Name = "ScrollingFrame"
        self.Active = True
        self.ClipsDescendants = True

        self.CanvasSize = Udim2(0, 0, 2, 0)
        self.CanvasPosition = Vector2(0, 0)
        self.AutomaticCanvasSize = "none"
        self.ScrollingDirection = "xy"   # "x" | "y" | "xy"
        self.ScrollingEnabled = True
        self.ScrollStep = 40             # pixels par cran de molette
        self.ScrollBarThickness = 8
        self.ScrollBarImageColor3 = (120, 120, 120)
        self.ScrollBarImageTransparency = 0.0

        self._DragAxis = None
        self._DragOffset = 0.0

    @property
    def CanvasSize(self) -> Udim2:
        return self._CanvasSize

    @CanvasSize.setter
    def CanvasSize(self, Value : Udim2):
        self._CanvasSize = Value
        self._MarkDirty()

    @property
    def AutomaticCanvasSize(self) -> str:
        return self._AutomaticCanvasSize

    @AutomaticCanvasSize.setter
    def AutomaticCanvasSize(self, Value : str):
        self._AutomaticCanvasSize = Value
        self._MarkDirty()

    @property
    def CanvasPosition(self) -> Vector2:
        """Décalage en pixels du canvas (borné entre 0 et le défilement max à l'utilisation)"""
        return self._CanvasPosition

    @CanvasPosition.setter
    def CanvasPosition(self, Value : Vector2):
        # Layout à jour : les enfants sont simplement décalés, sans recalcul
        Old = None if self._Dirty else self._GetClampedCanvasPosition()
        self._CanvasPosition = Value
        # La taille du canvas ne change pas : seuls les enfants bougent.
        # Toute la frame est redessinée (barres comprises) : inutile de suivre chaque enfant s'ils sont coupés par elle.
        self._MarkRenderDirty()
        Render = not self.ClipsDescendants
        if Old is None:
            for Child in self.Children:
                Child._MarkDirty(Render)
            return
        Delta = Old - self._GetClampedCanvasPosition()
        if Delta.x == 0 and Delta.y == 0:
            return
        for Child in self.Children:
            Child._Shift(Delta, Render)

    def _MarkDirty(self, Render : bool = True):
        super()._MarkDirty(Render)
        self._CanvasCache = None

    def _DependsOnChildren(self) -> bool:
        return super()._DependsOnChildren() or self.AutomaticCanvasSize.lower() != "none"

    # Canvas
    @property
    def AbsoluteCanvasSize(self) -> pygame.Vector2:
        if self._CanvasCache is None:
            self._CanvasCache = self._ComputeCanvasSize()
        return pygame.Vector2(self._CanvasCache)

    def _ComputeCanvasSize(self) -> pygame.Vector2:
        WindowSize = self.GetAbsSize()
        # Le canvas n'est jamais plus petit que la frame elle-même
        Canvas = pygame.Vector2(
            max(WindowSize.x, self.CanvasSize.X.Scale * WindowSize.x + self.CanvasSize.X.Offset),
            max(WindowSize.y, self.CanvasSize.Y.Scale * WindowSize.y + self.CanvasSize.Y.Offset),
        )
        Mode = self.AutomaticCanvasSize.lower()
        if Mode == "none":
            return Canvas

        Padding = self.GetComponent(UIPadding)
        PaddedSize = Padding._Apply(pygame.Vector2(0, 0), WindowSize)[1] if Padding is not None else pygame.Vector2(WindowSize)
        PaddingTotal = WindowSize - PaddedSize
        Content = self._ComputeContentExtent(PaddedSize)
        if "x" in Mode:
            Canvas.x = max(Canvas.x, Content.x + PaddingTotal.x)
        if "y" in Mode:
            Canvas.y = max(Canvas.y, Content.y + PaddingTotal.y)
        return Canvas

    def _ComputeContentExtent(self, ContentSize : pygame.Vector2) -> pygame.Vector2:
        Layout = self._GetLayout()
        if Layout is not None:
            return Layout._GetContentSize(self, ContentSize)

        Extent = pygame.Vector2(0, 0)
        for Child in self.Children:
            if not Child.Visible:
                continue
            Size = Child._ComputeSize(ContentSize)
            Pos = Child._ComputeRelativePosition(ContentSize, Size)
            Extent.x = max(Extent.x, Pos.x + Size.x)
            Extent.y = max(Extent.y, Pos.y + Size.y)
        return Extent

    def _GetMaxScroll(self) -> pygame.Vector2:
        Canvas = self.AbsoluteCanvasSize
        Window = self.GetAbsSize()
        return pygame.Vector2(max(0, Canvas.x - Window.x), max(0, Canvas.y - Window.y))

    def _GetClampedCanvasPosition(self) -> pygame.Vector2:
        Max = self._GetMaxScroll()
        return pygame.Vector2(
            min(max(self.CanvasPosition.X, 0), Max.x),
            min(max(self.CanvasPosition.Y, 0), Max.y),
        )

    def _GetInnerRect(self) -> tuple[pygame.Vector2, pygame.Vector2]:
        return self.GetAbsPosition() - self._GetClampedCanvasPosition(), self.AbsoluteCanvasSize

    # Défilement
    def _OnMouseWheel(self, X : int, Y : int) -> bool:
        if not self.ScrollingEnabled:
            return False
        Max = self._GetMaxScroll()
        Direction = self.ScrollingDirection.lower()
        CanX = "x" in Direction and Max.x > 0
        CanY = "y" in Direction and Max.y > 0
        if not (CanX or CanY):
            return False

        Pos = self._GetClampedCanvasPosition()
        if CanY:
            Pos.y -= Y * self.ScrollStep
        elif CanX:
            Pos.x -= Y * self.ScrollStep
        if CanX:
            Pos.x += X * self.ScrollStep
        self.CanvasPosition = Vector2(min(max(Pos.x, 0), Max.x), min(max(Pos.y, 0), Max.y))
        return True

    def _GetScrollBars(self) -> dict[str, tuple[pygame.Rect, pygame.Rect]]:
        """{"x" / "y": (rect de la piste, rect du curseur)} pour chaque barre affichée"""
        Thickness = int(self.ScrollBarThickness)
        if Thickness <= 0:
            return {}
        Rect = self.GetRect()
        Max = self._GetMaxScroll()
        Canvas = self.AbsoluteCanvasSize
        Pos = self._GetClampedCanvasPosition()
        Direction = self.ScrollingDirection.lower()
        ShowX = "x" in Direction and Max.x > 0
        ShowY = "y" in Direction and Max.y > 0
        Bars = {}

        if ShowY:
            Track = pygame.Rect(Rect.right - Thickness, Rect.top, Thickness, Rect.height - (Thickness if ShowX else 0))
            Length = min(Track.height, max(Thickness * 2, Track.height * Rect.height / Canvas.y))
            Start = Track.top + (Track.height - Length) * (Pos.y / Max.y)
            Bars["y"] = (Track, pygame.Rect(Track.left, Start, Thickness, Length))
        if ShowX:
            Track = pygame.Rect(Rect.left, Rect.bottom - Thickness, Rect.width - (Thickness if ShowY else 0), Thickness)
            Length = min(Track.width, max(Thickness * 2, Track.width * Rect.width / Canvas.x))
            Start = Track.left + (Track.width - Length) * (Pos.x / Max.x)
            Bars["x"] = (Track, pygame.Rect(Start, Track.top, Length, Thickness))
        return Bars

    def _CapturesPoint(self, Pos : pygame.Vector2) -> bool:
        return any(Track.collidepoint(Pos) for Track, _ in self._GetScrollBars().values())

    def _OnMouseDown(self, Button : int, Pos : pygame.Vector2):
        if Button != 1:
            return
        for Axis, (Track, Thumb) in self._GetScrollBars().items():
            if not Track.collidepoint(Pos):
                continue
            self._DragAxis = Axis
            if Thumb.collidepoint(Pos):
                self._DragOffset = Pos.y - Thumb.top if Axis == "y" else Pos.x - Thumb.left
            else:
                # Clic sur la piste : centre le curseur sous la souris
                self._DragOffset = (Thumb.height if Axis == "y" else Thumb.width) / 2
                self._DragTo(Pos)
            return

    def _OnMouseDrag(self, Pos : pygame.Vector2):
        if self._DragAxis is not None:
            self._DragTo(Pos)

    def _OnMouseUp(self, Button : int, Pos : pygame.Vector2, IsOver : bool):
        if Button == 1:
            self._DragAxis = None

    def _DragTo(self, Pos : pygame.Vector2):
        Bar = self._GetScrollBars().get(self._DragAxis)
        if Bar is None:
            return
        Track, Thumb = Bar
        Max = self._GetMaxScroll()
        Current = self._GetClampedCanvasPosition()
        if self._DragAxis == "y":
            Free = Track.height - Thumb.height
            Ratio = (Pos.y - self._DragOffset - Track.top) / Free if Free > 0 else 0
            Current.y = min(max(Ratio, 0), 1) * Max.y
        else:
            Free = Track.width - Thumb.width
            Ratio = (Pos.x - self._DragOffset - Track.left) / Free if Free > 0 else 0
            Current.x = min(max(Ratio, 0), 1) * Max.x
        self.CanvasPosition = Vector2(Current.x, Current.y)

    def _DrawOverlay(self, Surface : pygame.Surface):
        for _, Thumb in self._GetScrollBars().values():
            DrawRect(Surface, Thumb, self.ScrollBarImageColor3, self.ScrollBarImageTransparency, int(self.ScrollBarThickness) // 2)
