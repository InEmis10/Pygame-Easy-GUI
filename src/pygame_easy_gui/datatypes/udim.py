from __future__ import annotations

from ..utils.argument_verifier import ArgumentVerifier, NUMBER, Verify


DEBUG = True
CONFIG_UDIM_DEFAULT_SCALE = 0.0
CONFIG_UDIM_DEFAULT_OFFSET = 0.0

UDIM_VERIFIER = ArgumentVerifier([NUMBER, NUMBER], 2)

class Udim:
    @Verify(UDIM_VERIFIER)
    def __init__(self, Scale : float | int = CONFIG_UDIM_DEFAULT_SCALE, Offset : float | int = CONFIG_UDIM_DEFAULT_OFFSET):
        self.Scale = Scale
        self.Offset = Offset

    @Verify(ArgumentVerifier([NUMBER], 1))
    def setScale(self, newScale : float | int) -> (float | int) | None:
        self.Scale = newScale
        return self.Scale

    @Verify(ArgumentVerifier([NUMBER], 1))
    def setOffset(self, newOffset : float | int) -> (float | int) | None:
        self.Offset = newOffset
        return self.Offset

    @Verify(ArgumentVerifier([lambda: Udim, NUMBER], 2))
    def lerp(self, other: Udim, alpha: float | int) -> Udim:
        return Udim(
            self.Scale + (other.Scale - self.Scale) * alpha,
            self.Offset + (other.Offset - self.Offset) * alpha
        )

    @Verify(ArgumentVerifier([lambda: Udim], 1))
    def __add__(self, other : Udim):
        return Udim(
            self.Scale + other.Scale,
            self.Offset + other.Offset
        )

    @Verify(ArgumentVerifier([lambda: Udim], 1))
    def __sub__(self, other : Udim):
        return Udim(
            self.Scale - other.Scale,
            self.Offset - other.Offset
        )

    @Verify(ArgumentVerifier([lambda: Udim], 1))
    def __eq__(self, other : Udim):
        return self.__key() == other.__key()

    def __neg__(self):
        return Udim(-self.Scale, -self.Offset)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __mul__(self, scalar: float | int):
        return Udim(self.Scale * scalar, self.Offset * scalar)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __rmul__(self, scalar: float | int):
        return self.__mul__(scalar)

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
    def __init__(self, *args):
        self.X : Udim = None
        self.Y : Udim = None

        if len(args) == 4 and UDIM2_VERIFIER_1.Verifier(*args):
            self.X = Udim(args[0], args[1])
            self.Y  = Udim(args[2], args[3])
        elif len(args) == 2 and UDIM2_VERIFIER_2.Verifier(*args):
            self.X = args[0]
            self.Y = args[1]
        else:
            raise TypeError("Invalid arguments for Udim2")

    @Verify(ArgumentVerifier([NUMBER, NUMBER], 2))
    def fromOffset(self, offsetX : int | float, offsetY : int | float):
        self.X.setOffset(offsetX)
        self.Y.setOffset(offsetY)

    @Verify(ArgumentVerifier([NUMBER, NUMBER], 2))
    def fromScale(self, scaleX : int | float, scaleY : int | float):
        self.X.setScale(scaleX)
        self.Y.setScale(scaleY)

    @Verify(ArgumentVerifier([lambda: Udim2, NUMBER], 2))
    def Lerp(self, other : Udim2, alpha : int | float):
        return Udim2(
            self.X.lerp(other.X, alpha),
            self.Y.lerp(other.Y, alpha)
        )
    ##TODO -> Factoriser les add et sub avec la lib op (operator)

    @Verify(ArgumentVerifier([lambda: Udim2], 1))
    def __add__(self, other: Udim2):
        if not isinstance(other, Udim2):
            return NotImplemented
        return Udim2(
            self.X.Scale + other.X.Scale,
            self.X.Offset + other.X.Offset,
            self.Y.Scale + other.Y.Scale,
            self.Y.Offset + other.Y.Offset
        )

    def __sub__(self, other: Udim2):
        if not isinstance(other, Udim2):
            return NotImplemented
        return Udim2(
            self.X.Scale - other.X.Scale,
            self.X.Offset - other.X.Offset,
            self.Y.Scale - other.Y.Scale,
            self.Y.Offset - other.Y.Offset
        )

    @Verify(ArgumentVerifier([lambda: Udim2], 1))
    def __eq__(self, other: Udim2):
        return self.__key() == other.__key()

    def __neg__(self):
        return Udim2(-self.X, -self.Y)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __mul__(self, scalar: float | int):
        return Udim2(self.X * scalar, self.Y * scalar)

    @Verify(ArgumentVerifier([NUMBER], 1))
    def __rmul__(self, scalar: float | int):
        return self.__mul__(scalar)

    def __key(self):
        return self.X, self.Y

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"({self.X}, {self.Y})"
