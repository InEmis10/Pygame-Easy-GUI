from pygame_easy_gui.widgets.TextLabel import TextLabel
from pygame_easy_gui.widgets.GuiButton import ButtonMixin

#TODO 1- object must have event override (allow custom creation of event integrate to the TextButtonEvent or may be implementer using Signal object in custom class herite from TextButton

class TextButton(ButtonMixin, TextLabel):
    def __init__(self):
        super().__init__()
        self.Name = "TextButton"
