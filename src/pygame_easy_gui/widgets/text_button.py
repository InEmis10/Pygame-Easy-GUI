from .text_label import TextLabel
from ..core.signal import Signal

#TODO 1- object must have event override (allow custom creation of event integrate to the TextButtonEvent or may be implementer using Signal object in custom class herite from TextButton
#TODO 2- Object with may have TextChanged Event

class _TextButtonEvent:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.MouseButton1Click = Signal()
        self.MouseButton1Down = Signal()
        self.MouseButton1Up = Signal()
        self.MouseEnter = Signal()
        self.MouseLeave = Signal()


class TextButton(TextLabel, _TextButtonEvent):
    def __init__(self):
        super().__init__()

        self.Name = "TextButton"
        self.AutoButtonColor = True
        self.Active = True

        self._Hovering = False
        self._Pressed = False
