from Object.Labels.TextLabel import  TextLabel


class TextButton(TextLabel):
    def __init__(self):
        super().__init__()

        self.Name = None
        self.AutoButtonColor = True
        self.Active = True

        self._Hovering = False
        self._Pressed = False

        self.MouseButton1Click = None
        self.MouseButton1Down = None
        self.MouseButton1Up = None
        self.MouseEnter = None
        self.MouseLeave = None
