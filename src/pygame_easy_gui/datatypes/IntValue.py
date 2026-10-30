from __future__ import annotations

from pygame_easy_gui.core.Signal import Signal


class ValueWrapper:
    """Wrap all value interaction : Changed est émis uniquement quand Value est modifiée"""
    _Type = object

    def __init__(self, Value):
        self._CheckType(Value)
        self._Raw = Value
        self.Changed = Signal()

    def _CheckType(self, Value):
        if not isinstance(Value, self._Type):
            raise TypeError(f"{type(self).__name__} attend {self._Type.__name__}, reçu {type(Value).__name__}")

    @property
    def Value(self):
        return self._Raw

    @Value.setter
    def Value(self, NewValue):
        self._CheckType(NewValue)
        if NewValue == self._Raw:
            return
        self._Raw = NewValue
        self.Changed.Fire(NewValue)

    def _unwrap(self, Other : ValueWrapper):
        if isinstance(Other, ValueWrapper):
            return Other.Value
        return Other

    def __add__(self, Other):
        return self.Value + self._unwrap(Other)

    def __sub__(self, Other):
        return self.Value - self._unwrap(Other)

    def __radd__(self, Other):
        return self._unwrap(Other) + self.Value

    def __rsub__(self, Other):
        return self._unwrap(Other) - self.Value

    def __mul__(self, Other):
        return self.Value * self._unwrap(Other)

    def __rmul__(self, Other):
        return self._unwrap(Other) * self.Value

class IntValue(ValueWrapper):
    _Type = int

    def __init__(self, Value : int = 0):
        super().__init__(Value)
