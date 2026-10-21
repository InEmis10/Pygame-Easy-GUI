import pygame
import pytest
from pygame_easy_gui import Application, ScreenGui, Frame, TextButton, TextBox, Udim2, Color3, TweenService, TweenInfo


@pytest.fixture
def MyApp(Screen):
    """Application avec une vraie pygame.Window, pilotée tour par tour (sans run())"""
    App = Application("Test", Size=(400, 300), EventTimeOut=0.001)
    App._CreateWindow()
    Application.Current = App
    yield App
    Application.Current = None
    App.Window.destroy()
    from pygame_easy_gui.render import Display
    Display.SetSurface(None)


def test_UnknownProperty():
    with pytest.raises(AttributeError):
        Application(Tilte="faute de frappe")


def test_LayoutUsesWindowSize(MyApp):
    Main = ScreenGui()
    MyApp.Gui.Add(Main)
    Half = Frame.New(Main, Size=Udim2(0.5, 0, 0.5, 0))
    MyApp._Step()
    assert Half.GetRect().size == (200, 150)


def test_DisplayOrderAndDirtyRendering(MyApp):
    Bottom, Top = ScreenGui(), ScreenGui()
    MyApp.Gui.Add(Top)
    MyApp.Gui.Add(Bottom)
    Top.DisplayOrder = 10
    Frame.New(Bottom, Size=Udim2(0, 100, 0, 100), BackgroundColor3=Color3(255, 0, 0))
    Frame.New(Top, Size=Udim2(0, 50, 0, 50), BackgroundColor3=Color3(0, 0, 255))
    MyApp._Step()
    assert MyApp.Surface.get_at((10, 10))[:3] == (0, 0, 255)
    assert MyApp.Surface.get_at((80, 80))[:3] == (255, 0, 0)
    assert MyApp.Gui.Render(MyApp.Surface, MyApp.BackgroundColor3) == []   # rien n'a changé

    Top.DisplayOrder = -1
    MyApp._Step()
    assert MyApp.Surface.get_at((10, 10))[:3] == (255, 0, 0)
    Bottom.Enabled = False
    MyApp._Step()
    assert MyApp.Surface.get_at((10, 10))[:3] == (0, 0, 255)
    assert MyApp.Surface.get_at((80, 80))[:3] == tuple(MyApp.BackgroundColor3)


def test_TopScreenBlocksMouse(MyApp, MousePos):
    Bottom, Top = ScreenGui(), ScreenGui()
    Top.DisplayOrder = 1
    MyApp.Gui.Add(Bottom)
    MyApp.Gui.Add(Top)
    Button = TextButton.New(Bottom, Size=Udim2(0, 200, 0, 200))
    Frame.New(Top, Size=Udim2(0, 100, 0, 100))
    Clicks = []
    Button.MouseButton1Click.Connect(lambda: Clicks.append(1))

    def ClickAt(Pos):
        MousePos[0] = Pos
        return MyApp.Gui.HandleEvents([
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=Pos),
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=Pos),
        ])

    assert ClickAt((50, 50)) == [] and Clicks == [] and not Button._Hovering
    assert ClickAt((150, 150)) == [] and Clicks == [1] and Button._Hovering
    assert len(ClickAt((300, 250))) == 2   # hors de toute GUI : rendu au programme


def test_UnhandledEventsAndFocus(MyApp, MousePos):
    Main = ScreenGui()
    MyApp.Gui.Add(Main)
    Box = TextBox.New(Main, Size=Udim2(0, 200, 0, 30))
    Received = []
    MyApp.UnhandledEvent.Connect(Received.append)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=0, unicode="a"))
    MyApp._Step()
    assert [Event.type for Event in Received if Event.type == pygame.KEYDOWN] == [pygame.KEYDOWN]
    Box.CaptureFocus()
    assert MyApp.Gui.GetFocusedObject() is Box
    assert MyApp._GetWaitTime() <= 0.1


def test_WaitTimeDuringTween(MyApp):
    Main = ScreenGui()
    MyApp.Gui.Add(Main)
    Box = Frame.New(Main)
    MyApp.EventTimeOut = 1.0
    assert MyApp._GetWaitTime() == 1.0
    Tween = TweenService.Create(Box, TweenInfo(10), {"BackgroundTransparency": 1})
    Tween.Play()
    assert MyApp._GetWaitTime() == 0.0
    Tween.Cancel()
