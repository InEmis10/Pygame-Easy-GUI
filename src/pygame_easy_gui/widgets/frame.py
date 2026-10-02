import pygame
from ..core.gui_object import GuiObject

class Frame(GuiObject):
    def __init__(self):
        super().__init__()
        self.Name = "Frame"
        self.BackgroundColor3 = (255, 255, 255)
        self.BackgroundTransparency = 0.0  # 0 = opaque, 1 = invisible
        self.BorderColor3 = (0, 0, 0)
        self.BorderSizePixel = 0

    def _Draw(self, Surface: pygame.Surface):
        if self.BackgroundTransparency >= 1.0:
            self._DrawBorder(Surface)
            return

        rect = self.GetRect()

        if self.BackgroundTransparency <= 0.0:
            pygame.draw.rect(Surface, self.BackgroundColor3, rect)
        else:
            alpha = int((1.0 - self.BackgroundTransparency) * 255)
            temp = pygame.Surface(rect.size, pygame.SRCALPHA)
            temp.fill((*self.BackgroundColor3, alpha))
            Surface.blit(temp, rect.topleft)

        self._DrawBorder(Surface)

    def _DrawBorder(self, Surface: pygame.Surface):
        if self.BorderSizePixel > 0:
            pygame.draw.rect(Surface, self.BorderColor3, self.GetRect(), self.BorderSizePixel)