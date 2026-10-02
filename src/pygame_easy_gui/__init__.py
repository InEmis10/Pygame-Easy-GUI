"""Pygame Easy GUI : des interfaces pygame à la manière de Roblox."""
# Ordre des dépendances : datatypes (aucune dépendance) → core → widgets.
from .datatypes import Color3, Udim, Udim2, Vector2
from .core import (Application, AttributeMixin, Connect, Connection, EventManager, GuiObject,
                   InputObject, Signal, UserInputStates, UserInputType)
from .widgets import Frame, ScreenGui, TextButton, TextLabel

__all__ = [
    "Color3", "Udim", "Udim2", "Vector2",
    "Application", "GuiObject", "Signal", "Connection", "Connect",
    "EventManager", "AttributeMixin",
    "InputObject", "UserInputType", "UserInputStates",
    "Frame", "ScreenGui", "TextLabel", "TextButton",
]
__version__ = "0.1.0"
