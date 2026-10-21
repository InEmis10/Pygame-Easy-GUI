import pygame
from pygame_easy_gui.components.UIComponent import UIComponent


def AlignStart(Alignment : str, Available : float, Used : float) -> float:
    Alignment = Alignment.lower()
    if Alignment == "center":
        return (Available - Used) / 2
    if Alignment in ("right", "bottom"):
        return Available - Used
    return 0


class UILayout(UIComponent):
    """
    Base des layouts : place automatiquement les enfants visibles du parent.
    Les enfants d'un parent avec layout ignorent leur Position et leur AnchorPoint.
    """
    def __init__(self):
        super().__init__()
        self.SortOrder = "layoutorder"   # "layoutorder" | "name"
        self.HorizontalAlignment = "left"  # "left" | "center" | "right"
        self.VerticalAlignment = "top"     # "top" | "center" | "bottom"
        self._Cache = None
        self._CacheSize = None
        self._ContentSize = pygame.Vector2(0, 0)

    def _Invalidate(self):
        self._Cache = None

    def _GetSortedChildren(self, Parent) -> list:
        Children = [Child for Child in Parent.Children if Child.Visible]
        if self.SortOrder.lower() == "name":
            return sorted(Children, key=lambda Child: Child.Name)
        return sorted(Children, key=lambda Child: Child.LayoutOrder)

    def _EnsureComputed(self, Parent, ContentSize : pygame.Vector2):
        Key = (ContentSize.x, ContentSize.y)
        if self._Cache is None or self._CacheSize != Key:
            self._Cache, self._ContentSize = self._Compute(Parent, ContentSize)
            self._CacheSize = Key

    def _GetChildPosition(self, Parent, Child, ContentSize : pygame.Vector2) -> pygame.Vector2:
        self._EnsureComputed(Parent, ContentSize)
        return pygame.Vector2(self._Cache.get(Child, (0, 0)))

    def _GetContentSize(self, Parent, ContentSize : pygame.Vector2) -> pygame.Vector2:
        self._EnsureComputed(Parent, ContentSize)
        return pygame.Vector2(self._ContentSize)

    def _GetCellSize(self, ContentSize : pygame.Vector2) -> pygame.Vector2 | None:
        """Taille imposée aux enfants (None = les enfants gardent leur Size)"""
        return None

    def _Compute(self, Parent, ContentSize : pygame.Vector2) -> tuple[dict, pygame.Vector2]:
        """Retourne ({Enfant: position relative à la zone de contenu}, taille totale occupée)"""
        raise NotImplementedError

    @property
    def AbsoluteContentSize(self) -> pygame.Vector2:
        """Taille en pixels occupée par les enfants (utile pour dimensionner un CanvasSize)"""
        if self._Parent is None:
            return pygame.Vector2(0, 0)
        return self._GetContentSize(self._Parent, self._Parent._GetContentRect()[1])
