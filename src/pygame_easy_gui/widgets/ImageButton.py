from pygame_easy_gui.widgets.ImageLabel import ImageLabel
from pygame_easy_gui.widgets.GuiButton import ButtonMixin


class ImageButton(ButtonMixin, ImageLabel):
    """
    Bouton image. HoverImage / PressedImage remplacent l'image au survol / au clic.
    Sans HoverImage ni PressedImage, AutoButtonColor assombrit l'image.
    """
    def __init__(self):
        super().__init__()
        self.Name = "ImageButton"
        self.HoverImage = None
        self.PressedImage = None

    @property
    def HoverImage(self):
        return self._HoverImage

    @HoverImage.setter
    def HoverImage(self, Value):
        self._LoadImage(Value)
        self._HoverImage = Value

    @property
    def PressedImage(self):
        return self._PressedImage

    @PressedImage.setter
    def PressedImage(self, Value):
        self._LoadImage(Value)
        self._PressedImage = Value

    def _GetImage(self):
        if self._Hovering and self._Pressed and self.PressedImage is not None:
            return self.PressedImage
        if self._Hovering and self.HoverImage is not None:
            return self.HoverImage
        return self.Image

    def _GetImageColor(self) -> tuple:
        Color = tuple(self.ImageColor3)
        if self.HoverImage is None and self.PressedImage is None:
            return self._ApplyAutoColor(Color)
        return Color
