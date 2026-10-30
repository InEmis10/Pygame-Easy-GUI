from __future__ import annotations

from pygame_easy_gui.utils.ArgumentVerifier import ArgumentVerifier, NUMBER, Verify


DEBUG = True
CONFIG_UDIM_DEFAULT_SCALE = 0.0
CONFIG_UDIM_DEFAULT_OFFSET = 0.0

UDIM_VERIFIER = ArgumentVerifier([NUMBER, NUMBER], 2)

class Udim:
    """Immuable : pour changer une valeur, créer un nouveau Udim (sinon le GuiObject ne peut pas se marquer dirty)"""
    __slots__ = ("Scale", "Offset")

    @Verify(UDIM_VERIFIER)
    def __init__(self, Scale : float | int = CONFIG_UDIM_DEFAULT_SCALE, Offset : float | int = CONFIG_UDIM_DEFAULT_OFFSET):
        object.__setattr__(self, "Scale", Scale)
        object.__setattr__(self, "Offset", Offset)

    def __setattr__(self, Name, Value):
        raise AttributeError("Udim est immuable, crée un nouveau Udim à la place")

    @Verify(ArgumentVerifier([lambda: Udim, NUMBER], 2))
    def lerp(self, Other: Udim, Alpha: float | int) -> Udim:
        return Udim(
            self.Scale + (Other.Scale - self.Scale) * Alpha,
            self.Offset + (Other.Offset - self.Offset) * Alpha
        )

    @Verify(ArgumentVerifier([lambda: Udim], 1))
    def __add__(self, Other : Udim):
        return Udim(
            self.Scale + Other.Scale,
            self.Offset + Other.Offset
        )

    @Verify(ArgumentVerifier([lambda: Udim], 1))
    def __sub__(self, Other : Udim):
        return Udim(
            self.Scale - Other.Scale,
            self.Offset - Other.Offset
        )

    def __eq__(self, Other : Udim):
        if not isinstance(Other, Udim):
            return NotImplemented
        return self.__key() == Other.__key()

    def __neg__(self):
        return Udim(-self.Scale, -self.Offset)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __mul__(self, Scalar: float | int):
        return Udim(self.Scale * Scalar, self.Offset * Scalar)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __rmul__(self, Scalar: float | int):
        return self.__mul__(Scalar)

    def __iter__(self):
        return iter((self.Scale, self.Offset))

    def __key(self):
        return (self.Offset, self.Scale)

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"({self.Scale},{self.Offset})"

UDIM2_VERIFIER_1 = ArgumentVerifier([NUMBER, NUMBER, NUMBER, NUMBER], 4)
UDIM2_VERIFIER_2 = ArgumentVerifier([Udim, Udim], 2)

class Udim2:
    """Immuable : pour changer une valeur, créer un nouveau Udim2 (sinon le GuiObject ne peut pas se marquer dirty)"""
    __slots__ = ("X", "Y")

    def __init__(self, *args):
        if len(args) == 4 and UDIM2_VERIFIER_1.Verifier(*args):
            X = Udim(args[0], args[1])
            Y = Udim(args[2], args[3])
        elif len(args) == 2 and UDIM2_VERIFIER_2.Verifier(*args):
            X, Y = args
        else:
            raise TypeError("Invalid arguments for Udim2")

        object.__setattr__(self, "X", X)
        object.__setattr__(self, "Y", Y)

    def __setattr__(self, Name, Value):
        raise AttributeError("Udim2 est immuable, crée un nouveau Udim2 à la place")

    @classmethod
    @Verify(ArgumentVerifier([NUMBER, NUMBER], 2))
    def fromOffset(cls, OffsetX : int | float, OffsetY : int | float) -> Udim2:
        return cls(0, OffsetX, 0, OffsetY)

    @classmethod
    @Verify(ArgumentVerifier([NUMBER, NUMBER], 2))
    def fromScale(cls, ScaleX : int | float, ScaleY : int | float) -> Udim2:
        return cls(ScaleX, 0, ScaleY, 0)

    @Verify(ArgumentVerifier([lambda: Udim2, NUMBER], 2))
    def Lerp(self, Other : Udim2, Alpha : int | float):
        return Udim2(
            self.X.lerp(Other.X, Alpha),
            self.Y.lerp(Other.Y, Alpha)
        )
    ##TODO -> Factoriser les add et sub avec la lib op (operator)

    def __add__(self, Other: Udim2):
        if not isinstance(Other, Udim2):
            return NotImplemented
        return Udim2(
            self.X.Scale + Other.X.Scale,
            self.X.Offset + Other.X.Offset,
            self.Y.Scale + Other.Y.Scale,
            self.Y.Offset + Other.Y.Offset
        )

    def __sub__(self, Other: Udim2):
        if not isinstance(Other, Udim2):
            return NotImplemented
        return Udim2(
            self.X.Scale - Other.X.Scale,
            self.X.Offset - Other.X.Offset,
            self.Y.Scale - Other.Y.Scale,
            self.Y.Offset - Other.Y.Offset
        )

    def __eq__(self, Other: Udim2):
        if not isinstance(Other, Udim2):
            return NotImplemented
        return self.__key() == Other.__key()

    def __neg__(self):
        return Udim2(-self.X, -self.Y)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __mul__(self, Scalar: float | int):
        return Udim2(self.X * Scalar, self.Y * Scalar)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __rmul__(self, Scalar: float | int):
        return self.__mul__(Scalar)

    def __key(self):
        return self.X, self.Y

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"({self.X}, {self.Y})"
