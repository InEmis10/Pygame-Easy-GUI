import pygame
from pygame_easy_gui.core.GuiObject import GuiObject


class Frame(GuiObject):
    def __init__(self):
        super().__init__()
        self.Name = "Frame"
        self.Active = True
        self.BackgroundColor3 = (255, 255, 255)
        self.BackgroundTransparency = 0.0  # 0 = opaque, 1 = invisible
        self.BorderColor3 = (0, 0, 0)
        self.BorderSizePixel = 0

    def _Draw(self, Surface: pygame.Surface):
        self._DrawBackground(Surface)
