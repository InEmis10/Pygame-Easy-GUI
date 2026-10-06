from .TextLabel import TextLabel
from ..core.Signal import Signal
from ..core.Property import Property

DEFAULT_TEXT_BUTTON_WIDGETS_NAME = "TextButton"

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
    AutoButtonColor = Property(True)
    Active = Property(True, draw=False)

    def __init__(self):
        super().__init__()

        self.Name = DEFAULT_TEXT_BUTTON_WIDGETS_NAME

        self._Hovering = False
        self._Pressed = False
