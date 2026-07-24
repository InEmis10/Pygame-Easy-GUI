from Utils.ArgumentsVerifier import *

##TODO: check if we need update methode, value change methode and more arithmetique methode !!!

class Vector2:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def _key(self):
        return self.X, self.Y

    @Verify(ArgumentVerifier([lambda: Vector2], 1))
    def __sub__(self, other : Vector2):
        return Vector2(
            self.X - other.X,
            self.Y - other.Y
        )

    @Verify(ArgumentVerifier([lambda: Vector2], 1))
    def __add__(self, other : Vector2):
        return Vector2(
            self.X + other.X,
            self.Y + other.Y
        )

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other : Vector2):
        return self._key() == other._key()