from pygame import surface

from Object.GuiObject import GuiObject
import pygame

##TODO : 1 - Make the class Color3

class TextLabel(GuiObject):
    _font_cache = {}

    def __init__(self):
        super().__init__()

        self.Name = "TextLabel"
        self.Text = "Label"
        self.TextColor3 = (0, 0, 0)
        self.TextSize = 20
        self.FontName = None
        self.BackgroundColor3 = (255,255,255)
        self.BackgroundTransparency = 0
        self.TextXAlignement = "center"
        self.TextYAlignement = "center"

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
            temp.fill((*self.BackgroundColor3, alpha))
            Surface.blit(temp, rect.topleft)

        font = self._GetFont()
        textSurf = font.render(self.Text, True, self.TextColor3)
        textRect = textSurf.get_rect()

        if self.TextXAlignement == "left":
            textRect.left = rect.left
        elif self.TextXAlignement == "right":
            textRect.right = rect.right
        else:
            textRect.center = rect.center

        if self.TextYAlignement == "left":
            textRect.left = rect.left
        elif self.TextYAlignement == "right":
            textRect.right = rect.right
        else:
            textRect.center = rect.center

        Surface.blit(textSurf, textRect)
