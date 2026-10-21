import pytest
import pygame
from pygame_easy_gui import (
    GuiObject, Frame, ScrollingFrame, ScreenGui, TextLabel, Udim, Udim2, Vector2,
    UIPadding, UIListLayout, UIGridLayout, UISizeConstraint, UICorner, UIStroke,
)


def test_PositionSizeAnchor():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0.5, 0, 0, 100), Position=Udim2(0.5, 0, 0.5, 0), AnchorPoint=Vector2(0.5, 0.5))
    assert Box.GetRect() == pygame.Rect(200, 250, 400, 100)
    Child = Frame.New(Box, Size=Udim2(1, -20, 0, 10), Position=Udim2(0, 10, 1, -10))
    assert Child.GetRect() == pygame.Rect(210, 340, 380, 10)


def test_Reparenting():
    A, B, C = GuiObject(), GuiObject(), GuiObject()
    A.AddChild(C)
    B.AddChild(C)
    assert C not in A.Children and C.Parent is B and B.Children.count(C) == 1
    C.Parent = A
    assert C.Parent is A and C not in B.Children
    C.Parent = None
    assert C not in A.Children
    with pytest.raises(ValueError):
        A.AddChild(A)
    B.AddChild(A)
    with pytest.raises(ValueError):
        A.AddChild(B)


def test_FindAndDescendants():
    Root = GuiObject()
    Box = Frame.New(Root, Name="Box")
    Label = TextLabel.New(Box, Name="Label")
    assert Root.FindFirstChild("Label") is None
    assert Root.FindFirstChild("Label", True) is Label
    assert Root.GetDescendants() == [Box, Label]
    assert Label.IsDescendantOf(Root)


def test_Destroy():
    Root = GuiObject()
    Box = Frame.New(Root)
    Label = TextLabel.New(Box)
    Received = []
    Label.TextChanged.Connect(Received.append)
    Box.Destroy()
    Label.Text = "after"
    assert Box not in Root.Children and Received == []
    with pytest.raises(RuntimeError):
        Box.AddChild(Frame())


def test_Padding():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 200, 0, 100))
    Box.AddChild(UIPadding(PaddingLeft=Udim(0, 10), PaddingTop=Udim(0.1, 0)))
    Child = Frame.New(Box, Size=Udim2(1, 0, 1, 0))
    assert Child.GetRect() == pygame.Rect(10, 10, 190, 90)


def test_ComponentChangeRecomputes():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 200, 0, 100))
    Padding = UIPadding()
    Box.AddChild(Padding)
    Child = Frame.New(Box, Size=Udim2(1, 0, 1, 0))
    assert Child.GetRect().x == 0
    Padding.PaddingLeft = Udim(0, 30)
    assert Child.GetRect().x == 30
    Padding.Parent = None
    assert Child.GetRect().x == 0


def test_ListLayout():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 200, 0, 300))
    Layout = UIListLayout(Padding=Udim(0, 5), HorizontalAlignment="center")
    Box.AddChild(Layout)
    First = Frame.New(Box, Size=Udim2(0, 100, 0, 50), LayoutOrder=2)
    Second = Frame.New(Box, Size=Udim2(0, 50, 0, 20), LayoutOrder=1)
    assert Second.GetRect() == pygame.Rect(75, 0, 50, 20)
    assert First.GetRect() == pygame.Rect(50, 25, 100, 50)
    assert Layout.AbsoluteContentSize == (100, 75)

    # Changer la taille d'un enfant décale ses voisins
    Second.Size = Udim2(0, 50, 0, 40)
    assert First.GetRect().y == 45
    Second.Visible = False
    assert First.GetRect().y == 0


def test_GridLayout():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 230, 0, 300))
    Box.AddChild(UIGridLayout(CellSize=Udim2(0, 100, 0, 50), CellPadding=Udim2(0, 10, 0, 10)))
    Cells = [Frame.New(Box, Size=Udim2(0, 1, 0, 1)) for _ in range(3)]
    assert [Cell.GetRect() for Cell in Cells] == [
        pygame.Rect(0, 0, 100, 50), pygame.Rect(110, 0, 100, 50), pygame.Rect(0, 60, 100, 50),
    ]


def test_SizeConstraint():
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(1, 0, 0, 10))
    Box.AddChild(UISizeConstraint(MaxSize=Vector2(300, 1000), MinSize=Vector2(0, 40)))
    assert Box.GetAbsSize() == (300, 40)


def test_ScrollingFrameCanvas():
    Gui = ScreenGui()
    Scroller = ScrollingFrame.New(Gui, Size=Udim2(0, 200, 0, 100), CanvasSize=Udim2(0, 0, 0, 0), AutomaticCanvasSize="y")
    Scroller.AddChild(UIListLayout())
    Items = [Frame.New(Scroller, Size=Udim2(1, 0, 0, 30)) for _ in range(10)]
    assert Scroller.AbsoluteCanvasSize == (200, 300)
    assert Items[0].GetRect() == pygame.Rect(0, 0, 200, 30)

    Scroller.CanvasPosition = Vector2(0, 50)
    assert Items[0].GetRect().y == -50
    Scroller.CanvasPosition = Vector2(0, 9999)
    assert Items[-1].GetRect().bottom == 100

    Items[-1].Destroy()
    assert Scroller.AbsoluteCanvasSize == (200, 270)


def test_DrawEverything(Screen):
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 200, 0, 100), BackgroundTransparency=0.5, BorderSizePixel=2)
    Box.AddChild(UICorner())
    Box.AddChild(UIStroke(Thickness=3, Transparency=0.5))
    TextLabel.New(Box, Size=Udim2(1, 0, 1, 0), Text="Hello", TextScaled=True)
    Gui.Update(0.016)
    Gui.Draw(Screen)
    Average = pygame.transform.average_color(Screen, pygame.Rect(0, 0, 200, 100))
    assert Average[:3] != (0, 0, 0)


def test_ClipsDescendants(Screen):
    Gui = ScreenGui()
    Box = Frame.New(Gui, Size=Udim2(0, 100, 0, 100), BackgroundColor3=(0, 0, 255), ClipsDescendants=True)
    Frame.New(Box, Size=Udim2(0, 300, 0, 300), BackgroundColor3=(255, 0, 0))
    Screen.fill((0, 0, 0))
    Gui.Draw(Screen)
    assert Screen.get_at((50, 50))[:3] == (255, 0, 0)
    assert Screen.get_at((150, 150))[:3] == (0, 0, 0)
