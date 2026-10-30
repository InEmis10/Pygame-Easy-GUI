from pygame_easy_gui.datatypes.Udim import Udim2
from pygame_easy_gui.datatypes.Vector2 import Vector2
from pygame_easy_gui.core.Signal import Signal
import pygame

from pygame_easy_gui.core.mixins.AttributeMixin import AttributeMixin
from pygame_easy_gui.core.mixins.TagMixin import TagMixin
from pygame_easy_gui.core.mixins.InputMixin import InputMixin
from pygame_easy_gui.components.UIComponent import UIComponent
from pygame_easy_gui.components.UILayout import UILayout
from pygame_easy_gui.components.UIPadding import UIPadding
from pygame_easy_gui.components.UICorner import UICorner
from pygame_easy_gui.components.UIStroke import UIStroke
from pygame_easy_gui.components.UISizeConstraint import UISizeConstraint
from pygame_easy_gui.components.UIGradient import UIGradient
from pygame_easy_gui.render.Draw import DrawRect, GetScratch
from pygame_easy_gui.render import Display

_MISSING = object()
# Valeurs comparées par égalité : réassigner la même valeur ne provoque pas de redessin
_IMMUTABLE_TYPES = (int, float, str, bool, tuple, type(None), Udim2, Vector2)


class GuiObject(AttributeMixin, TagMixin, InputMixin):
    # Attributs privés qui changent l'affichage (ex: _Hovering pour un bouton). Les attributs publics redessinent toujours.
    _RenderAttributes : frozenset[str] = frozenset()
    _Parent = None
    _LastDrawRect : pygame.Rect | None = None   # zone de l'écran dessinée au dernier rendu
    _BoundsCache : pygame.Rect | None = None    # résultat de _GetDrawBounds tant que rien ne change

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._PropertySignals : dict[str, Signal] = {}
        self._ChangedSignal = Signal()   # (NomDeLaPropriété)

        self.Name = "GuiObject"
        self._Parent : "GuiObject | None" = None
        self.Children : list[GuiObject] = []
        self.Components : list[UIComponent] = []
        self._Destroyed = False

        self._Dirty = True
        self._AbsPos = pygame.Vector2(0, 0)
        self._AbsSize = pygame.Vector2(0, 0)
        self._CustomEvent = {}

        self.Position = Udim2(0, 0, 0, 0)
        self.Size = Udim2(0, 0, 0, 0)
        self.AnchorPoint = Vector2(0, 0)

        self.Visible = True
        self.ZIndex = 0
        self.LayoutOrder = 0
        self.ClipsDescendants = False
        self.Active = False

        # Apparence commune : invisible par défaut, Frame / TextLabel / ... la rendent visible
        self.BackgroundColor3 = (255, 255, 255)
        self.BackgroundTransparency = 1.0
        self.BorderColor3 = (0, 0, 0)
        self.BorderSizePixel = 0

    def __setattr__(self, Name, Value):
        """Toute modification d'une propriété publique demande au ScreenGui de redessiner la zone de l'objet"""
        if Name[0] == "_":
            object.__setattr__(self, Name, Value)
            if Name in self._RenderAttributes:
                self._MarkRenderDirty()
            return
        Old = getattr(self, Name, _MISSING)
        if Old is Value or (isinstance(Value, _IMMUTABLE_TYPES) and type(Old) is type(Value) and Old == Value):
            return
        object.__setattr__(self, Name, Value)
        self._MarkRenderDirty()
        self._FirePropertyChanged(Name, Old)

    # Signaux de changement (comme Roblox)
    @property
    def Changed(self) -> Signal:
        """Se déclenche avec le nom de la propriété à chaque modification d'une propriété publique"""
        return self._ChangedSignal

    def GetPropertyChangedSignal(self, Name : str) -> Signal:
        """Signal (sans argument) déclenché quand la propriété Name change. USAGE : Label.GetPropertyChangedSignal("Text").Connect(...)"""
        if Name.startswith("_") or not hasattr(self, Name):
            raise AttributeError(f"'{type(self).__name__}' n'a pas de propriété '{Name}'")
        if Name not in self._PropertySignals:
            self._PropertySignals[Name] = Signal()
        return self._PropertySignals[Name]

    def _FirePropertyChanged(self, Name : str, Old):
        Signals = self.__dict__.get("_PropertySignals")
        if Signals is None:   # pendant __init__
            return
        Specific = Signals.get(Name)
        if Specific is None and not self._ChangedSignal._Connections:
            return
        # Un setter peut ignorer la valeur (ex: Text = 5 alors que Text vaut déjà "5")
        New = getattr(self, Name, _MISSING)
        if New is Old or (isinstance(New, _IMMUTABLE_TYPES) and type(New) is type(Old) and New == Old):
            return
        if Specific is not None:
            Specific.Fire()
        self._ChangedSignal.Fire(Name)

    # Les propriétés de layout marquent l'objet dirty à chaque assignation
    @property
    def Position(self) -> Udim2:
        return self._Position

    @Position.setter
    def Position(self, Value : Udim2):
        self._Position = Value
        self._MarkDirty()
        self._InvalidateParentLayout()

    @property
    def Size(self) -> Udim2:
        return self._Size

    @Size.setter
    def Size(self, Value : Udim2):
        self._Size = Value
        self._MarkDirty()
        self._InvalidateParentLayout()

    @property
    def AnchorPoint(self) -> Vector2:
        return self._AnchorPoint

    @AnchorPoint.setter
    def AnchorPoint(self, Value : Vector2):
        self._AnchorPoint = Value
        self._MarkDirty()

    @property
    def Visible(self) -> bool:
        return self._Visible

    @Visible.setter
    def Visible(self, Value : bool):
        self._Visible = Value
        self._MarkRenderDirtyTree()
        self._InvalidateParentLayout()

    @property
    def ClipsDescendants(self) -> bool:
        return self._ClipsDescendants

    @ClipsDescendants.setter
    def ClipsDescendants(self, Value : bool):
        self._ClipsDescendants = Value
        self._MarkRenderDirtyTree()

    @property
    def LayoutOrder(self) -> int:
        return self._LayoutOrder

    @LayoutOrder.setter
    def LayoutOrder(self, Value : int):
        self._LayoutOrder = Value
        self._InvalidateParentLayout()

    @property
    def ZIndex(self) -> int:
        return self._ZIndex

    @ZIndex.setter
    def ZIndex(self, Value : int):
        self._ZIndex = Value
        self._MarkRenderDirtyTree()
        if self._Parent is not None:
            self._Parent._SortChildren()

    @property
    def Parent(self) -> "GuiObject | None":
        return self._Parent

    @Parent.setter
    def Parent(self, Value : "GuiObject | None"):
        if Value is self._Parent:
            return
        if Value is None:
            self._Parent.RemoveChild(self)
        else:
            Value.AddChild(self)

    # Hiérarchie
    def AddChild(self, Child : "GuiObject | UIComponent"):
        if self._Destroyed or getattr(Child, "_Destroyed", False):
            raise RuntimeError("Impossible d'utiliser un objet détruit")
        if isinstance(Child, UIComponent):
            self._AddComponent(Child)
            return
        if Child is self or Child.IsAncestorOf(self):
            raise ValueError(f"Impossible d'ajouter '{Child.Name}' à '{self.Name}' : cela créerait une boucle")
        if Child._Parent is self:
            return
        if Child._Parent is not None:
            Child._Parent.RemoveChild(Child)
        Child._Parent = self
        self.Children.append(Child)
        self._SortChildren()
        Child._MarkDirty()
        self._InvalidateLayout()

    def RemoveChild(self, Child : "GuiObject | UIComponent"):
        if isinstance(Child, UIComponent):
            if Child in self.Components:
                self.Components.remove(Child)
                Child._Parent = None
                self._OnComponentChanged(Child)
            return
        if Child in self.Children:
            Child._MarkRenderDirtyTree()   # efface sa zone tant qu'il est encore dans l'arbre
            Child._Parent = None
            self.Children.remove(Child)
            Child._MarkDirty()
            self._InvalidateLayout()

    def _AddComponent(self, Component : UIComponent):
        if Component._Parent is self:
            return
        if Component._Parent is not None:
            Component._Parent.RemoveChild(Component)
        Component._Parent = self
        self.Components.append(Component)
        self._OnComponentChanged(Component)

    def _OnComponentChanged(self, Component : UIComponent):
        self._MarkDirty()
        self._InvalidateParentLayout()

    def GetComponent(self, Type : type) -> UIComponent | None:
        for Component in self.Components:
            if isinstance(Component, Type):
                return Component
        return None

    def GetChildren(self) -> list["GuiObject"]:
        return list(self.Children)

    def GetDescendants(self) -> list["GuiObject"]:
        Result = []
        for Child in self.Children:
            Result.append(Child)
            Result.extend(Child.GetDescendants())
        return Result

    def FindFirstChild(self, Name : str, Recursive : bool = False) -> "GuiObject | None":
        for Child in self.Children:
            if Child.Name == Name:
                return Child
        if Recursive:
            for Child in self.Children:
                Found = Child.FindFirstChild(Name, True)
                if Found is not None:
                    return Found
        return None

    def IsAncestorOf(self, Obj : "GuiObject") -> bool:
        Current = Obj.Parent
        while Current is not None:
            if Current is self:
                return True
            Current = Current.Parent
        return False

    def IsDescendantOf(self, Obj : "GuiObject") -> bool:
        return Obj.IsAncestorOf(self)

    def _GetRoot(self) -> "GuiObject":
        Current = self
        while Current._Parent is not None:
            Current = Current._Parent
        return Current

    def Destroy(self):
        """Détruit l'objet et ses descendants : retire du parent, déconnecte tous les signaux, retire les tags"""
        if self._Destroyed:
            return
        for Child in list(self.Children):
            Child.Destroy()
        for Component in list(self.Components):
            self.RemoveChild(Component)
        for Tag in self.GetTags():
            self.RemoveTag(Tag)
        if self._Parent is not None:
            self._Parent.RemoveChild(self)
        for Value in list(vars(self).values()):
            if isinstance(Value, Signal):
                Value.DisconnectAll()
        for PropertySignal in self._PropertySignals.values():
            PropertySignal.DisconnectAll()
        self._Destroyed = True

    def _SortChildren(self):
        self.Children.sort(key=lambda Child: Child.ZIndex)

    # Rendu par zones (dirty rects) : voir ScreenGui
    def _MarkRenderDirty(self):
        """Demande au ScreenGui racine de redessiner l'ancienne et la nouvelle zone de l'objet"""
        self._BoundsCache = None
        self._GetRoot()._RegisterRenderDirty(self)

    def _MarkRenderDirtyTree(self):
        Root = self._GetRoot()
        Stack = [self]
        while Stack:
            Obj = Stack.pop()
            Root._RegisterRenderDirty(Obj)
            Stack.extend(Obj.__dict__.get("Children", ()))

    def _RegisterRenderDirty(self, Obj : "GuiObject"):
        """Redéfini par ScreenGui : un arbre sans ScreenGui n'a rien à suivre"""
        pass

    def _GetDrawBounds(self) -> pygame.Rect:
        """Zone de l'écran touchée par _Draw / _DrawOverlay (sans les enfants). A redéfinir si un composant dessine hors de son rect."""
        Rect = self.GetRect()
        Stroke = self.GetComponent(UIStroke)
        if Stroke is not None and Stroke.Enabled and Stroke.Thickness > 0:
            Thickness = int(Stroke.Thickness)
            Rect = Rect.inflate(Thickness * 2, Thickness * 2)
        return Rect

    def _GetCachedDrawBounds(self) -> pygame.Rect:
        Bounds = self._BoundsCache
        if Bounds is None:
            Bounds = self._BoundsCache = self._GetDrawBounds()
        return Bounds

    def _GetScreenBounds(self) -> pygame.Rect | None:
        """Zone réellement visible (coupée par les ancêtres ClipsDescendants), None si l'objet ou un ancêtre est caché"""
        if not self.Visible:
            return None
        Bounds = self._GetCachedDrawBounds()
        Current = self._Parent
        while Current is not None:
            if not Current.Visible:
                return None
            if Current.ClipsDescendants:
                Bounds = Bounds.clip(Current.GetRect())
            Current = Current._Parent
        return Bounds

    # Layout
    def _MarkDirty(self, Render : bool = True):
        """Position / taille à recalculer pour l'objet et ses descendants (Render = False : la zone est déjà redessinée par un parent)"""
        self._Dirty = True
        self._BoundsCache = None
        if Render:
            self._MarkRenderDirty()
        for Component in self.Components:
            Component._Invalidate()
        for Child in self.Children:
            Child._MarkDirty(Render)

    def _Shift(self, Delta : pygame.Vector2, Render : bool = True):
        """Décale l'objet et ses descendants sans recalculer leur layout (ex: défilement d'une ScrollingFrame)"""
        if self._Dirty:
            self._MarkDirty(Render)
            return
        OldPos = self._AbsPos
        self._AbsPos = OldPos + Delta
        Bounds = self._BoundsCache
        if Bounds is not None:
            # La zone en cache est déplacée du même nombre de pixels que le rect (arrondi identique à GetRect)
            OldRect = pygame.Rect(OldPos.x, OldPos.y, 0, 0)
            NewRect = pygame.Rect(self._AbsPos.x, self._AbsPos.y, 0, 0)
            self._BoundsCache = Bounds.move(NewRect.x - OldRect.x, NewRect.y - OldRect.y)
        if Render:
            self._MarkRenderDirty()
        for Child in self.Children:
            Child._Shift(Delta, Render)

    def _DependsOnChildren(self) -> bool:
        """True si la taille / position des enfants influence ce parent (layout, canvas automatique...)"""
        return self._GetLayout() is not None

    def _InvalidateLayout(self):
        if self._DependsOnChildren():
            self._MarkDirty()

    def _InvalidateParentLayout(self):
        if self._Parent is not None:
            self._Parent._InvalidateLayout()

    def _GetLayout(self) -> UILayout | None:
        return self.GetComponent(UILayout)

    def GetAbsPosition(self) -> pygame.Vector2:
        if self._Dirty:
            self._Recompute()
        return self._AbsPos

    def GetAbsSize(self) -> pygame.Vector2:
        if self._Dirty:
            self._Recompute()
        return self._AbsSize

    def _GetInnerRect(self) -> tuple[pygame.Vector2, pygame.Vector2]:
        """Zone de référence des enfants avant padding (redéfini par ScrollingFrame pour le canvas)"""
        return pygame.Vector2(self.GetAbsPosition()), pygame.Vector2(self.GetAbsSize())

    def _GetContentRect(self) -> tuple[pygame.Vector2, pygame.Vector2]:
        """Zone (position, taille) dans laquelle les enfants sont placés"""
        Pos, Size = self._GetInnerRect()
        Padding = self.GetComponent(UIPadding)
        if Padding is not None:
            Pos, Size = Padding._Apply(Pos, Size)
        return Pos, Size

    def _GetParentContentRect(self) -> tuple[pygame.Vector2, pygame.Vector2]:
        if self._Parent is not None:
            return self._Parent._GetContentRect()
        Size = Display.GetSize()
        return pygame.Vector2(0, 0), pygame.Vector2(Size if Size is not None else (0, 0))

    def _ComputeSize(self, ContentSize : pygame.Vector2) -> pygame.Vector2:
        Layout = self._Parent._GetLayout() if self._Parent is not None else None
        Size = Layout._GetCellSize(ContentSize) if Layout is not None else None
        if Size is None:
            Size = pygame.Vector2(
                self.Size.X.Scale * ContentSize.x + self.Size.X.Offset,
                self.Size.Y.Scale * ContentSize.y + self.Size.Y.Offset,
            )
        Constraint = self.GetComponent(UISizeConstraint)
        if Constraint is not None:
            Size = Constraint._Apply(Size)
        return Size

    def _ComputeRelativePosition(self, ContentSize : pygame.Vector2, AbsSize : pygame.Vector2) -> pygame.Vector2:
        RawPos = pygame.Vector2(
            self.Position.X.Scale * ContentSize.x + self.Position.X.Offset,
            self.Position.Y.Scale * ContentSize.y + self.Position.Y.Offset,
        )
        AnchorOffset = pygame.Vector2(
            AbsSize.x * self.AnchorPoint.X,
            AbsSize.y * self.AnchorPoint.Y,
        )
        return RawPos - AnchorOffset

    def _Recompute(self):
        ContentPos, ContentSize = self._GetParentContentRect()
        self._AbsSize = self._ComputeSize(ContentSize)

        Layout = self._Parent._GetLayout() if self._Parent is not None else None
        if Layout is not None:
            RelativePos = Layout._GetChildPosition(self._Parent, self, ContentSize)
        else:
            RelativePos = self._ComputeRelativePosition(ContentSize, self._AbsSize)

        self._AbsPos = ContentPos + RelativePos
        self._Dirty = False

    def GetRect(self) -> pygame.Rect:
        Pos = self.GetAbsPosition()
        Size = self.GetAbsSize()
        return pygame.Rect(Pos.x, Pos.y, Size.x, Size.y)

    def _GetPaddedRect(self) -> pygame.Rect:
        """Rect de l'objet moins son UIPadding (zone du texte / de l'image)"""
        Rect = self.GetRect()
        Padding = self.GetComponent(UIPadding)
        if Padding is None:
            return Rect
        Pos, Size = Padding._Apply(pygame.Vector2(Rect.topleft), pygame.Vector2(Rect.size))
        return pygame.Rect(Pos.x, Pos.y, Size.x, Size.y)

    def SetPosition(self, Pos : Udim2):
        self.Position = Pos

    def SetSize(self, Size : Udim2):
        self.Size = Size

    # Boucle
    def Update(self, Dt : float):
        if not self.Visible:
            return
        self._Update(Dt)
        for Child in self.Children:
            Child.Update(Dt)

    def Draw(self, Surface : pygame.Surface):
        """Dessine tout l'arbre (un ScreenGui, lui, ne redessine que ce qui a changé)"""
        self._DrawRegion(Surface, Surface.get_clip(), None)

    def _DrawRegion(self, Surface : pygame.Surface, Region : pygame.Rect, Clip : pygame.Rect | None):
        """Dessine l'arbre dans Region seulement : les objets qui ne la touchent pas ne sont pas dessinés.
        Clip = zone visible héritée des ancêtres ClipsDescendants."""
        if not self.Visible:
            return
        Bounds = self._GetCachedDrawBounds()
        if Clip is not None:
            Bounds = Bounds.clip(Clip)
        self._LastDrawRect = Bounds
        Touched = Bounds.colliderect(Region)
        if Touched:
            self._DrawSelf(Surface, Bounds)

        if self.Children:
            if self.ClipsDescendants:
                Rect = self.GetRect()
                ChildClip = Rect if Clip is None else Rect.clip(Clip)
                Visible = ChildClip.clip(Region)
                if Visible.width > 0 and Visible.height > 0:
                    OldClip = Surface.get_clip()
                    Surface.set_clip(Visible)
                    for Child in self.Children:
                        Child._DrawRegion(Surface, Region, ChildClip)
                    Surface.set_clip(OldClip)
            else:
                for Child in self.Children:
                    Child._DrawRegion(Surface, Region, Clip)

        if Touched:
            self._DrawOverlay(Surface)

    # Rendu
    def _DrawSelf(self, Surface : pygame.Surface, Bounds : pygame.Rect):
        """_Draw, passé à travers le UIGradient s'il y en a un"""
        Gradient = self.GetComponent(UIGradient)
        if Gradient is None or not Gradient.Enabled:
            self._Draw(Surface)
            return
        Rect = self.GetRect()
        Area = Bounds.clip(Surface.get_clip())
        if Rect.width <= 0 or Rect.height <= 0 or Area.width <= 0 or Area.height <= 0:
            return
        # Dessine l'objet à part, multiplie par le dégradé, puis colle le résultat
        Scratch = GetScratch(Surface.get_size())
        Scratch.set_clip(Area)
        Scratch.fill((0, 0, 0, 0), Area)
        self._Draw(Scratch)
        Scratch.blit(Gradient._GetSurface(Rect.size), Rect.topleft, special_flags=pygame.BLEND_RGBA_MULT)
        Surface.blit(Scratch, Area.topleft, Area)

    def _GetBackgroundColor(self) -> tuple:
        return self.BackgroundColor3

    def _GetCornerRadius(self) -> int:
        Corner = self.GetComponent(UICorner)
        return Corner._GetRadius(self.GetAbsSize()) if Corner is not None else 0

    def _DrawBackground(self, Surface : pygame.Surface):
        """Fond + bordure + UICorner / UIStroke : à appeler depuis _Draw dans les sous-classes"""
        Rect = self.GetRect()
        Radius = self._GetCornerRadius()
        DrawRect(Surface, Rect, self._GetBackgroundColor(), self.BackgroundTransparency, Radius)
        if self.BorderSizePixel > 0:
            DrawRect(Surface, Rect, self.BorderColor3, 0.0, Radius, int(self.BorderSizePixel))
        Stroke = self.GetComponent(UIStroke)
        if Stroke is not None:
            Stroke._Draw(Surface, Rect, Radius)

    def GetSignal(self, Name : str) -> (Signal | None):
        """Récupère un signal custom depuis : self.CustomEvent et return si l'event est valide"""
        if Name in self._CustomEvent:
            return self._CustomEvent[Name]
        return None

    @classmethod
    def New(cls, Parent: "GuiObject | None" = None, **kwargs) -> "GuiObject":
        Obj = cls()
        for Key, Value in kwargs.items():
            if not hasattr(Obj, Key):
                raise AttributeError(f"'{cls.__name__}' n'a pas de propriété '{Key}'")
            setattr(Obj, Key, Value)

        if Parent is not None:
            Parent.AddChild(Obj)

        return Obj

    def _Update(self, Dt: float):
        pass

    def _Draw(self, Surface: pygame.Surface):
        pass

    def _DrawOverlay(self, Surface: pygame.Surface):
        """Dessiné après les enfants (ex: barre de défilement)"""
        pass
