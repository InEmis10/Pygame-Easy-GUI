import pygame
from pygame_easy_gui.datatypes.udim import Udim
from pygame_easy_gui.components.UIComponent import UIComponent


class UIPadding(UIComponent):
    """Marge intérieure : décale les enfants (et le texte / l'image) du bord du parent. Scale = relatif à la taille du parent."""
    def __init__(self, **Properties):
        super().__init__()
        self.PaddingLeft = Udim(0, 0)
        self.PaddingRight = Udim(0, 0)
        self.PaddingTop = Udim(0, 0)
        self.PaddingBottom = Udim(0, 0)
        self._ApplyProperties(Properties)

    def _Apply(self, Pos : pygame.Vector2, Size : pygame.Vector2) -> tuple[pygame.Vector2, pygame.Vector2]:
        Left = self.PaddingLeft.Scale * Size.x + self.PaddingLeft.Offset
        Right = self.PaddingRight.Scale * Size.x + self.PaddingRight.Offset
        Top = self.PaddingTop.Scale * Size.y + self.PaddingTop.Offset
        Bottom = self.PaddingBottom.Scale * Size.y + self.PaddingBottom.Offset
        return (
            pygame.Vector2(Pos.x + Left, Pos.y + Top),
            pygame.Vector2(max(0, Size.x - Left - Right), max(0, Size.y - Top - Bottom)),
        )
