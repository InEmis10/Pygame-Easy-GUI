from __future__ import annotations

from pygame_easy_gui.utils.ArgumentVerifier import *

##TODO: check if we need update methode, value change methode and more arithmetique methode !!!

class Vector2:
    """Immuable : pour changer une valeur, créer un nouveau Vector2 (sinon le GuiObject ne peut pas se marquer dirty)"""
    __slots__ = ("X", "Y")

    def __init__(self, X, Y):
        object.__setattr__(self, "X", X)
        object.__setattr__(self, "Y", Y)

    def __setattr__(self, Name, Value):
        raise AttributeError("Vector2 est immuable, crée un nouveau Vector2 à la place")

    def _key(self):
        return self.X, self.Y

    @Verify(ArgumentVerifier([lambda: Vector2], 1))
    def __sub__(self, Other : Vector2):
        return Vector2(
            self.X - Other.X,
            self.Y - Other.Y
        )

    @Verify(ArgumentVerifier([lambda: Vector2], 1))
    def __add__(self, Other : Vector2):
        return Vector2(
            self.X + Other.X,
            self.Y + Other.Y
        )

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, Other : Vector2):
        if not isinstance(Other, Vector2):
            return NotImplemented
        return self._key() == Other._key()