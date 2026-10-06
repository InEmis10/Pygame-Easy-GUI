import pygame
from ..core.GuiObject import GuiObject
from ..core import Property
from ..datatypes import Color3

DEFAULT_FRAME_WIDGETS_NAME = "Frame"

class Frame(GuiObject):
    BackgroundColor3 = Property(default=Color3(255, 255, 255), layout=False)
    BackgroundTransparency = Property(0.0, layout=False)  # 0 = opaque, 1 = invisible
    BorderColor3 = Property(Color3(0, 0, 0), layout=False)
    BorderSizePixel = Property(0, layout=True)

    def __init__(self):
        super().__init__()
        self.Name = DEFAULT_FRAME_WIDGETS_NAME

    def _Draw(self, Surface: pygame.Surface):
        if self.BackgroundTransparency >= 1.0:
            self._DrawBorder(Surface)
            return

        rect = self.GetRect()

        if self.BackgroundTransparency <= 0.0:
            pygame.draw.rect(Surface, self.BackgroundColor3.ToPygame(), rect)
        else:
            alpha = int((1.0 - self.BackgroundTransparency) * 255)
            temp = pygame.Surface(rect.size, pygame.SRCALPHA)
            temp.fill((*self.BackgroundColor3.ToPygame(), alpha))
            Surface.blit(temp, rect.topleft)

        self._DrawBorder(Surface)

    def _DrawBorder(self, Surface: pygame.Surface):
        if self.BorderSizePixel > 0:
            pygame.draw.rect(Surface, self.BorderColor3.ToPygame(), self.GetRect(), self.BorderSizePixel)