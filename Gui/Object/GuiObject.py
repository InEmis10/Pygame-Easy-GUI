from Object.GuiAttribute.Udim import Udim2
from Object.GuiAttribute.Vector2 import  Vector2
import pygame


##TODO: 1- check if we can make event or check access to Position or Size to OnChange update the dirty state


class GuiObject:
    def __init__(self):
        self.Name = "GuiObject"
        self.Parent : "GuiObject | None"= None
        self.Children : list[GuiObject] = []

        self.Position = Udim2(0, 0, 0, 0)
        self.Size = Udim2(0, 0, 0, 0)
        self.AnchorPoint = Vector2(0, 0)

        self.Visible = True
        self.ZIndex = 0

        self._dirty = True
        self._abs_pos = pygame.Vector2(0, 0)
        self._abs_size = pygame.Vector2(0, 0)

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
        surface = pygame.display.get_surface()
        return pygame.Vector2(surface.get_size())

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

    def SetPosition(self, pos : Udim2):
        self.Position = pos
        self._MarkDirty()

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

    ## Override with object
    def _Update(self, dt: float):
        pass

    def _Draw(self, Surface: pygame.Surface):
        pass

