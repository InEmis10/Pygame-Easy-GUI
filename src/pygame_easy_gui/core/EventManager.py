import pygame
from pygame_easy_gui.core.GuiObject import GuiObject

MOUSE_BUTTONS = (1, 2, 3)   # gauche, milieu, droit (4+ = ancienne molette pygame, ignorés)


def _IsShown(Obj : GuiObject, Root : GuiObject) -> bool:
    """True si Obj est toujours dans l'arbre de Root, non détruit, et visible ainsi que tous ses ancêtres"""
    Current = Obj
    while Current is not None:
        if Current._Destroyed or not Current.Visible:
            return False
        if Current is Root:
            return True
        Current = Current.Parent
    return False


class EventManager:
    """
    Distribue les events pygame aux GuiObject : survol, clics, molette, focus clavier.
    Seuls les objets Active reçoivent la souris ; l'objet Active le plus haut sous la souris bloque ceux du dessous.
    Update() retourne les events que la GUI n'a pas consommés (à donner au jeu).
    Normalement utilisé via ScreenGui.HandleEvents().
    """

    def __init__(self, Root: GuiObject):
        self.Root = Root
        Root._EventManager = self
        self._Hovered : list[GuiObject] = []
        self._Pressed : dict[int, GuiObject] = {}
        self._Focused : GuiObject | None = None

    @property
    def FocusedObject(self) -> GuiObject | None:
        return self._Focused

    def IsMouseOverGui(self) -> bool:
        return bool(self._Hovered)

    def SetFocus(self, Obj : GuiObject | None, EnterPressed : bool = False):
        if Obj is self._Focused:
            return
        Old = self._Focused
        self._Focused = Obj
        if Old is not None:
            Old._OnFocusLost(EnterPressed)
        if Obj is not None:
            Obj._OnFocus()

    def GetObjectAt(self, Pos) -> GuiObject | None:
        return self._HitTest(self.Root, pygame.Vector2(Pos), None)

    def _HitTest(self, Obj : GuiObject, Pos : pygame.Vector2, Clip : pygame.Rect | None) -> GuiObject | None:
        if not Obj.Visible:
            return None
        Rect = Obj.GetRect()
        InClip = Clip is None or Clip.collidepoint(Pos)
        Hit = InClip and Obj.Active and Rect.collidepoint(Pos)
        if Hit and Obj._CapturesPoint(Pos):
            return Obj

        ChildClip = Clip
        if Obj.ClipsDescendants:
            ChildClip = Rect if Clip is None else Rect.clip(Clip)
        # Les derniers enfants sont dessinés au-dessus : on les teste en premier
        for Child in reversed(Obj.Children):
            Found = self._HitTest(Child, Pos, ChildClip)
            if Found is not None:
                return Found
        return Obj if Hit else None

    def _GetHoverChain(self, Target : GuiObject | None, Pos : pygame.Vector2) -> list[GuiObject]:
        """La cible + ses ancêtres Active sous la souris (survoler un enfant ne fait pas quitter le parent)"""
        Chain = []
        Current = Target
        while Current is not None:
            if Current.Active and Current.GetRect().collidepoint(Pos):
                Chain.append(Current)
            if Current is self.Root:
                break
            Current = Current.Parent
        return Chain

    def _ValidateState(self):
        """Oublie les objets détruits / cachés / retirés de l'arbre depuis la dernière frame"""
        for Obj in list(self._Hovered):
            if not _IsShown(Obj, self.Root):
                self._Hovered.remove(Obj)
                Obj._Hovering = False
                Obj.MouseLeave.Fire()
        for Button, Obj in list(self._Pressed.items()):
            if not _IsShown(Obj, self.Root):
                del self._Pressed[Button]
                Obj._Pressed = False
                if not Obj._Destroyed:
                    Obj._OnMouseUp(Button, pygame.Vector2(pygame.mouse.get_pos()), False)
        if self._Focused is not None and not _IsShown(self._Focused, self.Root):
            self.SetFocus(None)

    def _UpdateHover(self, Target : GuiObject | None, Pos : pygame.Vector2):
        Chain = self._GetHoverChain(Target, Pos)
        for Obj in self._Hovered:
            if Obj not in Chain:
                Obj._Hovering = False
                Obj.MouseLeave.Fire()
        for Obj in reversed(Chain):
            if Obj not in self._Hovered:
                Obj._Hovering = True
                Obj.MouseEnter.Fire()
        self._Hovered = Chain

    def Update(self, Events: list, MouseBlocked : bool = False) -> list:
        """MouseBlocked : la souris est sur une GUI placée au-dessus (autre ScreenGui), rien n'est survolé ici"""
        self._ValidateState()
        MousePos = pygame.Vector2(pygame.mouse.get_pos())
        Target = None if MouseBlocked else self.GetObjectAt(MousePos)
        self._UpdateHover(Target, MousePos)

        Remaining = []
        for Event in Events:
            if not self._HandleEvent(Event, Target):
                Remaining.append(Event)
        return Remaining

    def _HandleEvent(self, Event : pygame.event.Event, Target : GuiObject | None) -> bool:
        """Retourne True si l'event a été consommé par la GUI"""
        Type = Event.type

        if Type == pygame.MOUSEMOTION:
            Pos = pygame.Vector2(Event.pos)
            for Obj in list(self._Pressed.values()):
                Obj._OnMouseDrag(Pos)
            if Target is not None:
                Target.MouseMoved.Fire(int(Pos.x), int(Pos.y))
            return Target is not None or bool(self._Pressed)

        if Type == pygame.MOUSEBUTTONDOWN and Event.button in MOUSE_BUTTONS:
            Pos = pygame.Vector2(Event.pos)
            Hit = self.GetObjectAt(Pos)
            if Event.button == 1:
                self.SetFocus(Hit if Hit is not None and Hit._CanFocus else None)
            if Hit is None:
                return False
            self._Pressed[Event.button] = Hit
            if Event.button == 1:
                Hit._Pressed = True
            Hit.InputBegan.Fire(Event)
            Hit._OnMouseDown(Event.button, Pos)
            return True

        if Type == pygame.MOUSEBUTTONUP and Event.button in MOUSE_BUTTONS:
            Pos = pygame.Vector2(Event.pos)
            Hit = self.GetObjectAt(Pos)
            Pressed = self._Pressed.pop(Event.button, None)
            if Pressed is not None:
                if Event.button == 1:
                    Pressed._Pressed = False
                Pressed.InputEnded.Fire(Event)
                Pressed._OnMouseUp(Event.button, Pos, Hit is Pressed)
            return Pressed is not None or Hit is not None

        if Type == pygame.MOUSEWHEEL:
            if Target is None:
                return False
            Target.MouseWheel.Fire(Event.x, Event.y)
            # La molette remonte jusqu'au premier parent qui l'utilise (ex: ScrollingFrame)
            Current = Target
            while Current is not None:
                if Current._OnMouseWheel(Event.x, Event.y) or Current is self.Root:
                    break
                Current = Current.Parent
            return True

        if Type in (pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT, pygame.TEXTEDITING):
            if self._Focused is None:
                return False
            if Type == pygame.KEYDOWN:
                self._Focused._OnKeyDown(Event)
            elif Type == pygame.TEXTINPUT:
                self._Focused._OnTextInput(Event.text)
            return True

        return False
