from __future__ import annotations

import colorsys
from pygame_easy_gui.utils.argument_verifier import ArgumentVerifier, NUMBER, Verify


class Color3(tuple):
    """
    Couleur RGB immuable (0 - 255).
    Hérite de tuple : utilisable directement partout où pygame (ou la lib) attend une couleur.
    """
    __slots__ = ()

    @Verify(ArgumentVerifier([NUMBER, NUMBER, NUMBER], 3))
    def __new__(cls, R : int = 0, G : int = 0, B : int = 0):
        Channels = tuple(int(round(Value)) for Value in (R, G, B))
        if any(not 0 <= Value <= 255 for Value in Channels):
            raise ValueError(f"Color3 attend des valeurs entre 0 et 255, reçu {Channels}")
        return super().__new__(cls, Channels)

    @property
    def R(self) -> int:
        return self[0]

    @property
    def G(self) -> int:
        return self[1]

    @property
    def B(self) -> int:
        return self[2]

    @classmethod
    def fromRGB(cls, R : int, G : int, B : int) -> Color3:
        return cls(R, G, B)

    fromRgb = fromRGB   # nom utilisé par l'ancienne API

    def ToPygame(self) -> tuple[int, int, int]:
        """Compatibilité avec l'ancienne API : Color3 est déjà un tuple utilisable par pygame"""
        return tuple(self)

    @classmethod
    def fromHex(cls, Hex : str) -> Color3:
        """"#ff8800", "ff8800" ou "#f80" """
        Value = Hex.lstrip("#")
        if len(Value) == 3:
            Value = "".join(Char * 2 for Char in Value)
        if len(Value) != 6:
            raise ValueError(f"Couleur hexadécimale invalide : {Hex!r}")
        return cls(int(Value[0:2], 16), int(Value[2:4], 16), int(Value[4:6], 16))

    @classmethod
    def fromHSV(cls, H : float, S : float, V : float) -> Color3:
        """H, S, V entre 0 et 1"""
        R, G, B = colorsys.hsv_to_rgb(H, S, V)
        return cls(R * 255, G * 255, B * 255)

    def ToHex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self)

    def ToHSV(self) -> tuple[float, float, float]:
        return colorsys.rgb_to_hsv(self.R / 255, self.G / 255, self.B / 255)

    def Lerp(self, Other : Color3, Alpha : float) -> Color3:
        return Color3(*(A + (B - A) * Alpha for A, B in zip(self, Other)))

    def __repr__(self):
        return f"Color3({self.R}, {self.G}, {self.B})"
