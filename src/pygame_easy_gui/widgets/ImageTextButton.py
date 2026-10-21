import pygame
from pygame_easy_gui.widgets.ImageButton import ImageButton
from pygame_easy_gui.widgets.TextLabel import TextLabel


class ImageTextButton(ImageButton, TextLabel):
    """
    Bouton avec une image ET un texte (toutes les propriétés d'ImageButton et de TextLabel).
    ImageAlignment : "left" | "right" (icône carrée à côté du texte) | "background" (image derrière le texte)
    ImageTextSpacing : espace en pixels entre l'icône et le texte
    """
    def __init__(self):
        super().__init__()
        self.Name = "ImageTextButton"
        self.Text = "Button"
        self.ScaleType = "fit"
        self.ImageAlignment = "left"
        self.ImageTextSpacing = 6

    def _SplitRect(self) -> tuple[pygame.Rect, pygame.Rect]:
        """(zone de l'image, zone du texte)"""
        Rect = self._GetPaddedRect()
        Mode = self.ImageAlignment.lower()
        if Mode == "background" or self._GetImage() is None:
            return Rect, Rect

        Side = min(Rect.width, Rect.height)
        TextWidth = max(0, Rect.width - Side - int(self.ImageTextSpacing))
        if Mode == "right":
            return (
                pygame.Rect(Rect.right - Side, Rect.top, Side, Rect.height),
                pygame.Rect(Rect.left, Rect.top, TextWidth, Rect.height),
            )
        return (
            pygame.Rect(Rect.left, Rect.top, Side, Rect.height),
            pygame.Rect(Rect.right - TextWidth, Rect.top, TextWidth, Rect.height),
        )

    def _GetImageRect(self) -> pygame.Rect:
        return self._SplitRect()[0]

    def _GetTextArea(self) -> pygame.Rect:
        return self._SplitRect()[1]

    def _Draw(self, Surface : pygame.Surface):
        self._DrawBackground(Surface)
        self._DrawImage(Surface)
        self._DrawText(Surface)
