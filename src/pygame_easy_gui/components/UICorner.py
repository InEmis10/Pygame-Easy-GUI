import pygame
from pygame_easy_gui.datatypes.udim import Udim
from pygame_easy_gui.components.UIComponent import UIComponent


class UICorner(UIComponent):
    """Coins arrondis. Scale = relatif au plus petit côté du parent (Udim(0.5, 0) = forme de pilule / cercle)."""
    def __init__(self, **Properties):
        super().__init__()
        self.CornerRadius = Udim(0, 8)
        self._ApplyProperties(Properties)

    def _GetRadius(self, Size : pygame.Vector2) -> int:
        Smallest = min(Size.x, Size.y)
        Radius = self.CornerRadius.Scale * Smallest + self.CornerRadius.Offset
        return int(max(0, min(Radius, Smallest / 2)))
