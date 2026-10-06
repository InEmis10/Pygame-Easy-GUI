from __future__ import annotations

import pygame
from ..datatypes.udim import Udim2
from ..datatypes.vector2 import Vector2
from .mixins.attribute_mixin import AttributeMixin
from .Signal import Signal
from .Property import Property
from warnings import deprecated


##TODO: 1- check if we can make event or check access to Position or Size to OnChange update the dirty state


class GuiObject(AttributeMixin):

    Position = Property(Udim2(0, 0, 0, 0), layout=True)
    Size = Property(Udim2(0, 0, 0, 0), layout=True)
    AnchorPoint = Property(Vector2(0, 0), layout=True)
    Visible = Property(True)
    ZIndex = Property(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.Name = "GuiObject"
        self.Parent : "GuiObject | None" = None
        self.Children : list[GuiObject] = []

        self._dirty = True
        self._abs_pos = pygame.Vector2(0, 0)
        self._abs_size = pygame.Vector2(0, 0)
        self._CustomEvent : dict[str, Signal] = {}

        self.Changed = Signal()
        self._PropertySignals : dict[str, Signal] = {}

    def AddChild(self, child : GuiObject):
        child.Parent = self
        child._MarkDirty()
        self.Children.append(child)
        self.Children.sort(key= lambda c: c.ZIndex)

    def RemoveChild(self, child : GuiObject):
        if child in self.Children:
            child.Parent = None
            self.Children.remove(child)

    def _MarkDirty(self):
        self._dirty = True
        for c  in self.Children:
            c._MarkDirty()

    def GetAbsPosition(self) -> pygame.Vector2:
        if self._dirty:
            self._Recompute()
        return self._abs_pos

    def GetAbsSize(self) -> pygame.Vector2:
        if self._dirty:
            self._Recompute()
        return self._abs_size

    def _GetParentAbsSize(self) -> pygame.Vector2:
        if self.Parent is not None:
            return self.Parent.GetAbsSize()
        # Racine (ScreenGui) : taille de la fenêtre de l'Application. Avec pygame.Window,
        # pygame.display.get_surface() renvoie None, d'où ce passage par Application.Current.
        from .Application import Application    # dans la fonction : Application importe gui_object
        app = Application.Current
        if app is not None and app.Surface is not None:
            return pygame.Vector2(app.Surface.get_size())
        surface = pygame.display.get_surface()  # repli : boucle maison avec display.set_mode
        if surface is not None:
            return pygame.Vector2(surface.get_size())
        return pygame.Vector2(0, 0)

    def GetPropertyChangedSignal(self, name: str) -> Signal:
        if not isinstance(getattr(type(self), name, None), Property):
            raise AttributeError(f"'{type(self).__name__}' n'a pas de propriété '{name}'")
        return self._PropertySignals.setdefault(name, Signal())

    def _OnPropertyChanged(self, name: str, layout: bool):
        if layout:
            self._MarkDirty()
        # plus tard : Application.Current.RequestRedraw()
        self.Changed.Fire(name)
        if name in self._PropertySignals:
            self._PropertySignals[name].Fire()

    def _Recompute(self):
        ParentSize = self._GetParentAbsSize()
        ParentPos = self.Parent.GetAbsPosition() if self.Parent else pygame.Vector2(0, 0)

        self._abs_size = pygame.Vector2 (
            self.Size.X.Scale * ParentSize.x + self.Size.X.Offset,
            self.Size.Y.Scale * ParentSize.y + self.Size.Y.Offset,
        )

        RawPos = pygame.Vector2(
            self.Position.X.Scale * ParentSize.x + self.Position.X.Offset,
            self.Position.Y.Scale * ParentSize.y + self.Position.Y.Offset,
        )

        AnchorOffset = pygame.Vector2 (
            self._abs_size.x * self.AnchorPoint.X,
            self._abs_size.y * self.AnchorPoint.Y,
        )

        self._abs_pos = ParentPos + RawPos - AnchorOffset
        self._dirty = False

    def GetRect(self) -> pygame.Rect:
        pos = self.GetAbsPosition()
        size = self.GetAbsSize()
        return  pygame.Rect(pos.x, pos.y,size.x, size.y)

    @deprecated("User cls Property() direct reassign instead", category=DeprecationWarning)
    def SetPosition(self, pos : Udim2):
        self.Position = pos
        self._MarkDirty()

    @deprecated("User cls Property() direct reassign instead", category=DeprecationWarning)
    def SetSize(self, size : Udim2):
        self.Size = size
        self._MarkDirty()

    def Update(self, dt : float):
        if not self.Visible:
            return
        self._Update(dt)
        for c in self.Children:
            c.Update(dt)

    def Draw(self, Surface : pygame.Surface):
        if not self.Visible:
            return
        self._Draw(Surface)
        for c in self.Children:
            c.Draw(Surface)

    def GetSignal(self, name : str) -> (Signal | None):
        """Récupère un signal custom depuis : self._CustomEvent et return si l'event est valide"""
        if name in self._CustomEvent:
            return self._CustomEvent[name]
        return None

    @classmethod
    def New(cls, Parent: "GuiObject | None" = None, **kwargs) -> "GuiObject":
        """Crée l'objet, applique les propriétés et le range dans Parent (comme Instance.new).

            button = TextButton.New(frame, Name="PlayButton", Text="Jouer")
        """
        obj = cls()
        for key, value in kwargs.items():
            if key.startswith("_") or not hasattr(obj, key):
                raise AttributeError(f"'{cls.__name__}' n'a pas de propriété '{key}'")
            setattr(obj, key, value)

        if Parent is not None:
            Parent.AddChild(obj)

        return obj

    ## Override with object
    def _Update(self, dt: float):
        pass

    def _Draw(self, Surface: pygame.Surface):
        pass

