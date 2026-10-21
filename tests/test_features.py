import pygame
import pytest
from pygame_easy_gui import (
    ScreenGui, Frame, TextLabel, TextBox, Udim, Udim2, Vector2, Color3,
    UIGradient, UIListLayout, UIGridLayout, ColorSequence, ColorSequenceKeypoint, NumberSequence,
    TweenService, TweenInfo, Clipboard,
)
from conftest import Click


# Changed / GetPropertyChangedSignal
def test_PropertyChangedSignal():
    Label = TextLabel()
    Calls, Names = [], []
    Label.GetPropertyChangedSignal("Text").Connect(lambda: Calls.append(Label.Text))
    Label.Changed.Connect(Names.append)
    Label.Text = "a"
    Label.Text = "a"
    Label.Text = 5
    Label.Text = "5"   # déjà "5" : pas de signal
    Label.TextColor3 = (255, 0, 0)
    assert Calls == ["a", "5"]
    assert Names == ["Text", "Text", "TextColor3"]
    with pytest.raises(AttributeError):
        Label.GetPropertyChangedSignal("Nope")


# TweenService
@pytest.fixture
def FakeClock(monkeypatch):
    Now = [0.0]
    monkeypatch.setattr(TweenService, "Clock", staticmethod(lambda: Now[0]))
    monkeypatch.setattr(TweenService, "_Active", [])

    def Advance(Seconds):
        Now[0] += Seconds
        TweenService.Step()
    return Advance


def test_TweenReachesGoal(FakeClock):
    Box = Frame.New(None, Position=Udim2(0, 0, 0, 0), BackgroundColor3=Color3(0, 0, 0), BackgroundTransparency=0)
    Tween = TweenService.Create(Box, TweenInfo(1, "linear"), {"Position": Udim2(0, 100, 0, 50), "BackgroundColor3": Color3(200, 100, 0), "BackgroundTransparency": 1})
    States = []
    Tween.Completed.Connect(States.append)
    Tween.Play()
    FakeClock(0.5)
    assert Box.Position == Udim2(0, 50, 0, 25) and Box.BackgroundColor3 == Color3(100, 50, 0)
    assert Tween.PlaybackState == "Playing" and Box.BackgroundTransparency == 0.5
    FakeClock(0.6)
    assert Box.Position == Udim2(0, 100, 0, 50) and Box.BackgroundTransparency == 1
    assert Tween.PlaybackState == "Completed" and States == ["Completed"]
    assert TweenService.GetPlayingTweens() == []


def test_TweenDelayReverseRepeat(FakeClock):
    Label = TextLabel.New(None, TextSize=10)
    Tween = TweenService.Create(Label, TweenInfo(1, "linear", RepeatCount=1, Reverses=True, DelayTime=0.5), {"TextSize": 20})
    Tween.Play()
    FakeClock(0.4)
    assert Tween.PlaybackState == "Delayed" and Label.TextSize == 10
    FakeClock(1.1)   # 1 s après le délai : au sommet
    assert Label.TextSize == 20
    FakeClock(1.0)   # retour
    assert Label.TextSize == 10 and Tween.PlaybackState == "Playing"
    FakeClock(2.0)
    assert Label.TextSize == 10 and Tween.PlaybackState == "Completed"


def test_TweenPauseCancelOverride(FakeClock):
    Box = Frame.New(None, BackgroundTransparency=0)
    First = TweenService.Create(Box, TweenInfo(1, "linear"), {"BackgroundTransparency": 1})
    First.Play()
    FakeClock(0.25)
    First.Pause()
    FakeClock(10)
    assert Box.BackgroundTransparency == 0.25
    First.Play()
    FakeClock(0.25)
    assert Box.BackgroundTransparency == 0.5

    States = []
    First.Completed.Connect(States.append)
    Second = TweenService.Create(Box, TweenInfo(1, "linear"), {"BackgroundTransparency": 0})
    Second.Play()
    assert First.PlaybackState == "Cancelled" and States == ["Cancelled"]
    FakeClock(1)
    assert Box.BackgroundTransparency == 0


def test_TweenEasingAndValidation(FakeClock):
    Box = Frame.New(None, BackgroundColor3=Color3(0, 0, 0))
    Tween = TweenService.Create(Box, TweenInfo(1, "back", "in"), {"BackgroundColor3": Color3(255, 255, 255)})
    Tween.Play()
    FakeClock(0.2)   # "back" passe sous 0 : la couleur reste valide
    assert Box.BackgroundColor3 == Color3(0, 0, 0)
    FakeClock(1)
    with pytest.raises(AttributeError):
        TweenService.Create(Box, TweenInfo(), {"Nope": 1})
    with pytest.raises(TypeError):
        TweenService.Create(Box, TweenInfo(), {"Position": 5})
    with pytest.raises(ValueError):
        TweenInfo(1, "wobbly")
    # Un UIComponent s'anime aussi
    Gradient = UIGradient()
    Box.AddChild(Gradient)
    TweenService.Create(Gradient, TweenInfo(1, "linear"), {"Offset": Vector2(1, 0)}).Play()
    FakeClock(0.5)
    assert Gradient.Offset == Vector2(0.5, 0)


def test_TweenStopsOnDestroy(FakeClock):
    Box = Frame.New(None, BackgroundTransparency=0)
    Tween = TweenService.Create(Box, TweenInfo(1), {"BackgroundTransparency": 1})
    Tween.Play()
    Box.Destroy()
    FakeClock(0.5)
    assert Tween.PlaybackState == "Cancelled"


# UIGradient
def test_GradientColors(Screen):
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 100, 0, 50), BackgroundColor3=(255, 255, 255))
    Box.AddChild(UIGradient(Color=ColorSequence((255, 0, 0), (0, 0, 255))))
    Screen.fill((0, 0, 0))
    Gui.Draw(Screen)
    Left, Right = Screen.get_at((1, 25)), Screen.get_at((98, 25))
    assert Left.r > 220 and Left.b < 30 and Right.b > 220 and Right.r < 30

    Box.GetComponent(UIGradient).Rotation = 90
    Gui.Draw(Screen)
    Top, Bottom = Screen.get_at((50, 1)), Screen.get_at((50, 48))
    assert Top.r > 220 and Bottom.b > 220

    Box.GetComponent(UIGradient).Transparency = NumberSequence(0, 1)
    Screen.fill((0, 0, 0))
    Gui.Draw(Screen)
    assert Screen.get_at((50, 1)).r > 220 and Screen.get_at((50, 49)).b < 30   # bas presque invisible


def test_GradientKeypoints():
    Sequence = ColorSequence([ColorSequenceKeypoint(1, (0, 0, 0)), ColorSequenceKeypoint(0, (255, 0, 0)), ColorSequenceKeypoint(0.5, (0, 255, 0))])
    assert Sequence.Evaluate(0) == (255, 0, 0)
    assert Sequence.Evaluate(0.25) == (127.5, 127.5, 0)
    assert Sequence.Evaluate(0.5) == (0, 255, 0)
    assert ColorSequence((1, 2, 3)) == ColorSequence((1, 2, 3), (1, 2, 3))


def test_GradientIncrementalRender(Screen):
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 200, 0, 100), Position=Udim2(0, 50, 0, 50))
    Gradient = UIGradient(Color=ColorSequence((255, 255, 0), (0, 255, 255)))
    Box.AddChild(Gradient)
    Label = TextLabel.New(Box, Text="Hello", Size=Udim2(1, 0, 1, 0), BackgroundTransparency=1)
    Gui.Render(Screen, (0, 0, 0))
    Gradient.Offset = Vector2(0.3, 0)
    Label.Text = "Bonjour"
    Gui.Render(Screen, (0, 0, 0))
    Reference = pygame.Surface(Screen.get_size())
    Gui.ForceRedraw()
    Gui.Render(Reference, (0, 0, 0))
    assert pygame.image.tobytes(Screen, "RGB") == pygame.image.tobytes(Reference, "RGB")


# Layouts
def test_ListLayoutWraps():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 100, 0, 100))
    Layout = UIListLayout(Padding=Udim(0, 10), Wraps=True)
    Box.AddChild(Layout)
    Items = [Frame.New(Box, Size=Udim2(0, 30, 0, 40), LayoutOrder=Index) for Index in range(5)]
    # 2 par colonne (40 + 10 + 40 = 90 <= 100), colonnes de 30 px espacées de 10
    assert [Item.GetRect().topleft for Item in Items] == [(0, 0), (0, 50), (40, 0), (40, 50), (80, 0)]
    assert Layout.AbsoluteContentSize == (110, 90)


def test_GridStartCornerAndCount():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 220, 0, 300))
    Grid = UIGridLayout(CellSize=Udim2(0, 100, 0, 50), CellPadding=Udim2(0, 10, 0, 10), StartCorner="topright")
    Box.AddChild(Grid)
    Items = [Frame.New(Box, LayoutOrder=Index) for Index in range(3)]
    assert [Item.GetRect().topleft for Item in Items] == [(110, 0), (0, 0), (110, 60)]
    assert Grid.AbsoluteCellCount == Vector2(2, 2)
    assert Grid.AbsoluteCellSize == (100, 50)


# TextBox : sélection et presse-papiers
def Key(Gui, KeyCode, Mod=0):
    return Gui.HandleEvents([pygame.event.Event(pygame.KEYDOWN, key=KeyCode, mod=Mod, unicode="")])


def Type(Gui, Text):
    return Gui.HandleEvents([pygame.event.Event(pygame.TEXTINPUT, text=Text)])


@pytest.fixture
def Box(Screen):
    Gui = ScreenGui()
    Field = TextBox.New(Gui, Size=Udim2(0, 300, 0, 30))
    Field.CaptureFocus()
    Type(Gui, "hello world")
    Gui.Draw(Screen)
    return Gui, Field


def test_KeyboardSelection(Box):
    Gui, Field = Box
    Key(Gui, pygame.K_LEFT, pygame.KMOD_SHIFT | pygame.KMOD_CTRL)
    assert Field.GetSelectedText() == "world"
    Type(Gui, "there")
    assert Field.Text == "hello there" and Field.GetSelection() is None
    Key(Gui, pygame.K_a, pygame.KMOD_CTRL)
    assert Field.GetSelection() == (0, 11)
    Key(Gui, pygame.K_LEFT)
    assert Field.CursorPosition == 0 and Field.GetSelection() is None
    Key(Gui, pygame.K_END, pygame.KMOD_SHIFT)
    Key(Gui, pygame.K_BACKSPACE)
    assert Field.Text == ""


def test_CopyCutPaste(Box):
    Gui, Field = Box
    Key(Gui, pygame.K_HOME)
    for _ in range(5):
        Key(Gui, pygame.K_RIGHT, pygame.KMOD_SHIFT)
    Key(Gui, pygame.K_c, pygame.KMOD_CTRL)
    assert Clipboard.GetText() == "hello"
    Key(Gui, pygame.K_END)
    Key(Gui, pygame.K_v, pygame.KMOD_CTRL)
    assert Field.Text == "hello worldhello"
    Key(Gui, pygame.K_a, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_x, pygame.KMOD_CTRL)
    assert Field.Text == "" and Clipboard.GetText() == "hello worldhello"


def test_DisabledActions(Box):
    Gui, Field = Box
    Clipboard.SetText("before")
    Field.CopyEnabled = False
    Field.CutEnabled = False
    Field.PasteEnabled = False
    Key(Gui, pygame.K_a, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_c, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_x, pygame.KMOD_CTRL)
    assert Clipboard.GetText() == "before" and Field.Text == "hello world"
    Key(Gui, pygame.K_END)
    Key(Gui, pygame.K_v, pygame.KMOD_CTRL)
    assert Field.Text == "hello world"

    Field.SelectionEnabled = False
    Key(Gui, pygame.K_a, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_LEFT, pygame.KMOD_SHIFT)
    assert Field.GetSelection() is None and Field.CursorPosition == 10

    # Lecture seule : copier marche, couper / coller non
    Field.SelectionEnabled = True
    Field.CopyEnabled = Field.CutEnabled = Field.PasteEnabled = True
    Field.TextEditable = False
    Key(Gui, pygame.K_a, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_x, pygame.KMOD_CTRL)
    assert Field.Text == "hello world" and Clipboard.GetText() == "before"
    Key(Gui, pygame.K_c, pygame.KMOD_CTRL)
    Key(Gui, pygame.K_v, pygame.KMOD_CTRL)
    assert Field.Text == "hello world" and Clipboard.GetText() == "hello world"


def test_MaxLengthPasteAndSingleLine(Box):
    Gui, Field = Box
    Field.MaxLength = 14
    Clipboard.SetText("a\nbcdef")
    Key(Gui, pygame.K_v, pygame.KMOD_CTRL)
    assert Field.Text == "hello worlda b"


def test_MouseSelection(Box, MousePos):
    Gui, Field = Box
    Rect = Field._GetPaddedRect()
    Font = Field._GetFont()
    Start = (Rect.left + 1, Rect.centery)
    End = (Rect.left + Font.size("hello")[0], Rect.centery)
    MousePos[0] = Start
    Gui.HandleEvents([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=Start),
        pygame.event.Event(pygame.MOUSEMOTION, pos=End, rel=(0, 0), buttons=(1, 0, 0)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=End),
    ])
    assert Field.GetSelectedText() == "hello"

    # Double-clic : sélectionne le mot
    Middle = (Rect.left + Font.size("hello wo")[0], Rect.centery)
    MousePos[0] = Middle
    Click(Gui, Middle)
    Click(Gui, Middle)
    assert Field.GetSelectedText() == "world"
