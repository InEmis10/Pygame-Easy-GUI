"""Fonctions d'easing (comme Roblox) : Alpha entre 0 et 1 -> progression (peut dépasser 0 - 1 pour "back" et "elastic")"""
import math


def _Linear(Alpha : float) -> float:
    return Alpha


def _Sine(Alpha : float) -> float:
    return 1 - math.cos(Alpha * math.pi / 2)


def _Quad(Alpha : float) -> float:
    return Alpha ** 2


def _Cubic(Alpha : float) -> float:
    return Alpha ** 3


def _Quart(Alpha : float) -> float:
    return Alpha ** 4


def _Quint(Alpha : float) -> float:
    return Alpha ** 5


def _Exponential(Alpha : float) -> float:
    return 0.0 if Alpha <= 0 else 2 ** (10 * Alpha - 10)


def _Circular(Alpha : float) -> float:
    return 1 - math.sqrt(max(0.0, 1 - Alpha ** 2))


def _Back(Alpha : float) -> float:
    Overshoot = 1.70158
    return (Overshoot + 1) * Alpha ** 3 - Overshoot * Alpha ** 2


def _Elastic(Alpha : float) -> float:
    if Alpha <= 0 or Alpha >= 1:
        return Alpha
    return -(2 ** (10 * Alpha - 10)) * math.sin((Alpha * 10 - 10.75) * (2 * math.pi) / 3)


def _BounceOut(Alpha : float) -> float:
    if Alpha < 1 / 2.75:
        return 7.5625 * Alpha ** 2
    if Alpha < 2 / 2.75:
        Alpha -= 1.5 / 2.75
        return 7.5625 * Alpha ** 2 + 0.75
    if Alpha < 2.5 / 2.75:
        Alpha -= 2.25 / 2.75
        return 7.5625 * Alpha ** 2 + 0.9375
    Alpha -= 2.625 / 2.75
    return 7.5625 * Alpha ** 2 + 0.984375


def _Bounce(Alpha : float) -> float:
    return 1 - _BounceOut(1 - Alpha)


# Versions "in" : les versions "out" et "inout" en sont déduites
STYLES = {
    "linear": _Linear, "sine": _Sine, "quad": _Quad, "cubic": _Cubic, "quart": _Quart, "quint": _Quint,
    "exponential": _Exponential, "circular": _Circular, "back": _Back, "elastic": _Elastic, "bounce": _Bounce,
}
DIRECTIONS = ("in", "out", "inout")


def Ease(Alpha : float, Style : str = "quad", Direction : str = "out") -> float:
    Function = STYLES[Style.lower()]
    Direction = Direction.lower()
    if Direction == "in":
        return Function(Alpha)
    if Direction == "out":
        return 1 - Function(1 - Alpha)
    if Alpha < 0.5:
        return Function(Alpha * 2) / 2
    return 1 - Function((1 - Alpha) * 2) / 2
