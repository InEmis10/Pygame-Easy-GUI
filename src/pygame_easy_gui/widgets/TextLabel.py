import pygame

from ..core.GuiObject import GuiObject
from ..core.Property import Property
from ..datatypes import Color3

DEFAULT_TEXT_LABEL_WIDGETS_NAME = "TextLabel"

class TextLabel(GuiObject):
    _font_cache = {}

    Text = Property("Label", draw=True)
    TextColor3 = Property(Color3(0, 0, 0))
    TextSize = Property(20, draw=True)
    FontName = Property(None, draw=True)
    BackgroundColor3 = Property(Color3(255, 255, 255), draw=True)
    BackgroundTransparency = Property(0.0, draw=True)  # 0 = opaque, 1 = invisible
    TextXAlignement = Property("center", draw=True)    # "left", "center", "right"
    TextYAlignement = Property("center", draw=True)    # "top", "center", "bottom"

    def __init__(self):
        super().__init__()
        self.Name = DEFAULT_TEXT_LABEL_WIDGETS_NAME

    def _GetFont(self) -> pygame.font.Font:
        key = (self.FontName, self.TextSize)
        if key not in TextLabel._font_cache:
            TextLabel._font_cache[key] = pygame.font.Font(self.FontName, self.TextSize)
        return TextLabel._font_cache[key]

    def _Draw(self, Surface: pygame.Surface):
        rect = self.GetRect()

        if self.BackgroundTransparency < 1.0:
            alpha = int((1.0 - self.BackgroundTransparency) * 255)
            temp = pygame.Surface(rect.size, pygame.SRCALPHA)
            temp.fill((*self.BackgroundColor3.ToPygame(), alpha))
            Surface.blit(temp, rect.topleft)

        font = self._GetFont()
        textSurf = font.render(self.Text, True, self.TextColor3.ToPygame())
        textRect = textSurf.get_rect()

        # Un axe à la fois : l'alignement vertical ne doit pas écraser l'horizontal
        if self.TextXAlignement == "left":
            textRect.left = rect.left
        elif self.TextXAlignement == "right":
            textRect.right = rect.right
        else:
            textRect.centerx = rect.centerx

        if self.TextYAlignement == "top":
            textRect.top = rect.top
        elif self.TextYAlignement == "bottom":
            textRect.bottom = rect.bottom
        else:
            textRect.centery = rect.centery

        Surface.blit(textSurf, textRect)
