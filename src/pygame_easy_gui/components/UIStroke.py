import pygame
from pygame_easy_gui.components.UIComponent import UIComponent
from pygame_easy_gui.render.Draw import DrawRect


class UIStroke(UIComponent):
    """Contour dessiné à l'extérieur du parent (suit les coins arrondis d'un UICorner)"""
    def __init__(self, **Properties):
        super().__init__()
        self.Color = (0, 0, 0)
        self.Thickness = 1
        self.Transparency = 0.0
        self.Enabled = True
        self._ApplyProperties(Properties)

    def _Draw(self, Surface : pygame.Surface, Rect : pygame.Rect, Radius : int):
        if not self.Enabled or self.Thickness <= 0:
            return
        Thickness = int(self.Thickness)
        Outer = Rect.inflate(Thickness * 2, Thickness * 2)
        OuterRadius = Radius + Thickness if Radius > 0 else 0
        DrawRect(Surface, Outer, self.Color, self.Transparency, OuterRadius, Thickness)
