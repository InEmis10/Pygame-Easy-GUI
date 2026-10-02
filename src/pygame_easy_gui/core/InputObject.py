from .Enum import UserInputType, UserInputStates
from ..datatypes.udim import Udim2
from dataclasses import dataclass as DataClass, KW_ONLY, field


class _modifiers:
    def __init__(self, ctrl : bool, shift : bool, alt : bool):
        self.ctrl = ctrl
        self.shift = shift
        self.alt = alt

    def ctrlShift(self):
        return self.ctrl and self.shift

    def ctrlAlt(self):
        return self.ctrl and self.alt

    def altShift(self):
        return self.alt and self.shift

    def ctrlAltShift(self):
        return self.ctrl and self.alt and self.shift


@DataClass
class InputObject:
    UserInputType : UserInputType
    UserInputState : UserInputStates
    _: KW_ONLY
    Position : Udim2
    Delta : float
    Modifiers : _modifiers = field(default_factory=lambda:_modifiers(False, False, False))
    ClickCount = 0
    Handled = False
    KeyCode : int = 0
    TextInput : str = ""

