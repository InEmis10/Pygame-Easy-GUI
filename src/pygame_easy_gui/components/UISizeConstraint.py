import math
import pygame
from pygame_easy_gui.datatypes.vector2 import Vector2
from pygame_easy_gui.components.UIComponent import UIComponent


class UISizeConstraint(UIComponent):
    """Limite la taille absolue (en pixels) du parent entre MinSize et MaxSize"""
    def __init__(self, **Properties):
        super().__init__()
        self.MinSize = Vector2(0, 0)
        self.MaxSize = Vector2(math.inf, math.inf)
        self._ApplyProperties(Properties)

    def _Apply(self, Size : pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(
            min(max(Size.x, self.MinSize.X), self.MaxSize.X),
            min(max(Size.y, self.MinSize.Y), self.MaxSize.Y),
        )
