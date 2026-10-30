import pygame
from pygame_easy_gui import ScreenGui, Frame, TextButton, TextLabel, ScrollingFrame, Udim2, UIListLayout
from conftest import Click


def MakeButton(Gui):
    Button = TextButton.New(Gui, Size=Udim2(0, 100, 0, 50), Position=Udim2(0, 100, 0, 100))
    Log = []
    for Name in ("MouseEnter", "MouseLeave", "MouseButton1Down", "MouseButton1Up", "MouseButton1Click", "MouseButton2Click", "Activated"):
        getattr(Button, Name).Connect(lambda Name=Name: Log.append(Name))
    return Button, Log


def test_HoverAndClick(MousePos):
    Gui = ScreenGui()
    Button, Log = MakeButton(Gui)

    MousePos[0] = (150, 120)
    Remaining = Click(Gui, (150, 120))
    assert Remaining == []
    assert Log == ["MouseEnter", "MouseButton1Down", "MouseButton1Up", "MouseButton1Click", "Activated"]

    Log.clear()
    Click(Gui, (150, 120), Button=3)
    assert Log == ["MouseButton2Click"]

    Log.clear()
    MousePos[0] = (10, 10)
    Remaining = Click(Gui, (10, 10))
    assert Log == ["MouseLeave"]
    assert len(Remaining) == 2   # clic hors de la GUI : rendu au jeu


def test_ReleaseOutsideIsNotAClick(MousePos):
    Gui = ScreenGui()
    Button, Log = MakeButton(Gui)
    MousePos[0] = (150, 120)
    Gui.HandleEvents([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 120))])
    Gui.HandleEvents([pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(10, 10))])
    assert "MouseButton1Up" in Log and "MouseButton1Click" not in Log


def test_ActiveFrameBlocksButtonBelow(MousePos):
    Gui = ScreenGui()
    Button, Log = MakeButton(Gui)
    Cover = Frame.New(Gui, Size=Udim2(1, 0, 1, 0))
    MousePos[0] = (150, 120)
    Click(Gui, (150, 120))
    assert Log == []

    # Un TextLabel (Active = False) laisse passer les clics
    Cover.Destroy()
    TextLabel.New(Gui, Size=Udim2(1, 0, 1, 0), BackgroundTransparency=1)
    Click(Gui, (150, 120))
    assert "MouseButton1Click" in Log


def test_HiddenButtonLosesHover(MousePos):
    Gui = ScreenGui()
    Button, Log = MakeButton(Gui)
    MousePos[0] = (150, 120)
    Gui.HandleEvents([])
    Button.Visible = False
    Gui.HandleEvents([])
    assert Log == ["MouseEnter", "MouseLeave"]


def test_HoverParentAndChild(MousePos):
    Gui = ScreenGui()
    Parent = Frame.New(Gui, Size=Udim2(0, 400, 0, 400))
    Button, Log = MakeButton(Parent)
    ParentLog = []
    Parent.MouseLeave.Connect(lambda: ParentLog.append("leave"))
    MousePos[0] = (50, 50)
    Gui.HandleEvents([])
    MousePos[0] = (150, 120)
    Gui.HandleEvents([])
    assert ParentLog == [] and Log == ["MouseEnter"]


def test_AutoButtonColor(MousePos):
    Gui = ScreenGui()
    Button, _ = MakeButton(Gui)
    Button.BackgroundColor3 = (200, 100, 0)
    assert Button._GetBackgroundColor() == (200, 100, 0)
    MousePos[0] = (150, 120)
    Gui.HandleEvents([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 120))])
    assert Button._GetBackgroundColor() == (140, 70, 0)
    Gui.HandleEvents([pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(150, 120))])
    assert Button._GetBackgroundColor() == (170, 85, 0)
    Button.AutoButtonColor = False
    assert Button._GetBackgroundColor() == (200, 100, 0)


def test_WheelScrollsAndClipsHitTest(MousePos):
    Gui = ScreenGui()
    Scroller = ScrollingFrame.New(Gui, Size=Udim2(0, 200, 0, 100), CanvasSize=Udim2(0, 0, 0, 0), AutomaticCanvasSize="y", ScrollStep=30)
    Scroller.AddChild(UIListLayout())
    Buttons = [TextButton.New(Scroller, Size=Udim2(1, -20, 0, 40)) for _ in range(5)]
    Clicked = []
    Buttons[3].MouseButton1Click.Connect(lambda: Clicked.append(3))

    # Le bouton 3 (y = 120) est hors de la zone visible : pas cliquable
    MousePos[0] = (50, 50)
    Click(Gui, (50, 130))
    assert Clicked == []

    Gui.HandleEvents([pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-2)])
    assert Scroller.CanvasPosition.Y == 60
    Click(Gui, (50, 70))
    assert Clicked == [3]


def test_ScrollBarDrag(MousePos):
    Gui = ScreenGui()
    Scroller = ScrollingFrame.New(Gui, Size=Udim2(0, 200, 0, 100), CanvasSize=Udim2(0, 0, 0, 400))
    Track, Thumb = Scroller._GetScrollBars()["y"]
    Start = (Thumb.centerx, Thumb.centery)
    MousePos[0] = Start
    Gui.HandleEvents([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=Start),
        pygame.event.Event(pygame.MOUSEMOTION, pos=(Start[0], 1000), rel=(0, 0), buttons=(1, 0, 0)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(Start[0], 1000)),
    ])
    assert Scroller.CanvasPosition.Y == 300
