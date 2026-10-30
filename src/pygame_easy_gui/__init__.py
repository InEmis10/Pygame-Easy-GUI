"""
Pygame Easy GUI : des interfaces pygame à la manière de Roblox.
USAGE : from pygame_easy_gui import Application, ScreenGui, Frame, TextButton, Udim2
"""
# Ordre des dépendances : datatypes (aucune dépendance) → core → components → widgets → services.
from .datatypes import (Color3, Udim, Udim2, Vector2, ColorSequence, ColorSequenceKeypoint,
                        NumberSequence, NumberSequenceKeypoint, IntValue)
from .core import (Application, AttributeMixin, Connect, Connection, EventManager, GuiObject,
                   OnEvent, Signal)
from .components import (UIComponent, UIPadding, UICorner, UIStroke, UIGradient, UIListLayout, UIGridLayout,
                         UISizeConstraint, UITextSizeConstraint)
from .widgets import (Frame, ScrollingFrame, ScreenGui, TextLabel, ImageLabel, ButtonMixin, TextButton,
                      ImageButton, ImageTextButton, TextBox)
from .services import CollectionService, TweenService, TweenInfo, Tween, TimeService, Timer, Clipboard

__all__ = [
    "Color3", "Udim", "Udim2", "Vector2", "ColorSequence", "ColorSequenceKeypoint",
    "NumberSequence", "NumberSequenceKeypoint", "IntValue",
    "Application", "GuiObject", "Signal", "Connection", "Connect", "OnEvent",
    "EventManager", "AttributeMixin",
    "UIComponent", "UIPadding", "UICorner", "UIStroke", "UIGradient", "UIListLayout", "UIGridLayout",
    "UISizeConstraint", "UITextSizeConstraint",
    "Frame", "ScrollingFrame", "ScreenGui", "TextLabel", "ImageLabel", "ButtonMixin",
    "TextButton", "ImageButton", "ImageTextButton", "TextBox",
    "CollectionService", "TweenService", "TweenInfo", "Tween", "TimeService", "Timer", "Clipboard",
]
__version__ = "1.0.0"
