import pygame
from pygame_easy_gui import (
    ScreenGui, Frame, ScrollingFrame, TextLabel, TextButton, ImageLabel, ImageTextButton,
    Udim, Udim2, Vector2, UIListLayout, UIStroke, UICorner,
)
from pygame_easy_gui.render import ImageCache

BACKGROUND = (30, 30, 30)


def BuildScene():
    Gui = ScreenGui()
    Panel = Frame.New(Gui, Size=Udim2(0, 300, 0, 200), Position=Udim2(0, 50, 0, 50), BackgroundColor3=(40, 40, 60))
    Panel.AddChild(UICorner())
    Title = TextLabel.New(Panel, Text="Titre", Size=Udim2(1, 0, 0, 30), BackgroundTransparency=1)
    Ghost = Frame.New(Gui, Size=Udim2(0, 80, 0, 80), Position=Udim2(0, 400, 0, 300), BackgroundColor3=(200, 0, 0), BackgroundTransparency=0.5)
    Ghost.AddChild(UIStroke(Thickness=3, Color=(255, 255, 0)))

    List = ScrollingFrame.New(Gui, Size=Udim2(0, 200, 0, 150), Position=Udim2(0, 500, 0, 50), CanvasSize=Udim2(0, 0, 0, 0), AutomaticCanvasSize="y")
    List.AddChild(UIListLayout(Padding=Udim(0, 4)))
    for Index in range(10):
        TextButton.New(List, Text=f"Item {Index}", Size=Udim2(1, 0, 0, 30), LayoutOrder=Index, BackgroundColor3=(60, 60, 80 + Index * 10))

    Icon = pygame.Surface((16, 16))
    Icon.fill((0, 255, 0))
    Button = ImageTextButton.New(Gui, Image=Icon, Text="Jouer", Size=Udim2(0, 150, 0, 40), Position=Udim2(0, 50, 0, 400))
    return Gui, Panel, Title, Ghost, List, Button


def FullRender(Gui, Size):
    Reference = pygame.Surface(Size)
    Gui.ForceRedraw()
    Gui.Render(Reference, BACKGROUND)
    return Reference


def AssertSame(A, B):
    assert pygame.image.tobytes(A, "RGB") == pygame.image.tobytes(B, "RGB")


def test_NothingChangedNothingRedrawn(Screen):
    Gui, *_ = BuildScene()
    Rects = Gui.Render(Screen, BACKGROUND)
    assert Rects == [Screen.get_rect()]
    assert Gui.Render(Screen, BACKGROUND) == []
    Gui.Update(0.016)
    assert Gui.Render(Screen, BACKGROUND) == []


def test_OnlyChangedAreaRedrawn(Screen):
    Gui, Panel, Title, Ghost, List, Button = BuildScene()
    Gui.Render(Screen, BACKGROUND)

    Title.Text = "Nouveau"
    Rects = Gui.Render(Screen, BACKGROUND)
    assert len(Rects) == 1 and Title.GetRect().contains(Rects[0])

    # Déplacement : ancienne et nouvelle zone, rien d'autre
    Ghost.Position = Udim2(0, 410, 0, 300)
    Rects = Gui.Render(Screen, BACKGROUND)
    Expected = Ghost.GetRect().inflate(6, 6).union(Ghost.GetRect().move(-10, 0).inflate(6, 6))
    assert Rects == [Expected]

    # Défilement : seulement la ScrollingFrame
    List.CanvasPosition = Vector2(0, 40)
    Rects = Gui.Render(Screen, BACKGROUND)
    assert Rects == [List.GetRect()]


def test_IncrementalMatchesFullRender(Screen):
    Gui, Panel, Title, Ghost, List, Button = BuildScene()
    Gui.Render(Screen, BACKGROUND)

    Changes = [
        lambda: setattr(Ghost, "Position", Udim2(0, 120, 0, 120)),          # passe par-dessus Panel
        lambda: setattr(Panel, "BackgroundColor3", (10, 90, 10)),
        lambda: setattr(Title, "Text", "Un titre bien plus long que la zone"),
        lambda: setattr(List, "CanvasPosition", Vector2(0, 100)),
        lambda: setattr(List.Children[3], "BackgroundColor3", (255, 0, 255)),
        lambda: setattr(Panel, "Visible", False),
        lambda: List.Children[0].Destroy(),
        lambda: setattr(Panel, "Visible", True),
        lambda: setattr(Ghost, "ZIndex", -1),
        lambda: setattr(Panel, "Size", Udim2(0, 200, 0, 100)),
        lambda: setattr(Button, "ImageAlignment", "right"),
        lambda: Ghost.GetComponent(UIStroke).__setattr__("Thickness", 8),
    ]
    for Change in Changes:
        Change()
        Gui.Render(Screen, BACKGROUND)
        AssertSame(Screen, FullRender(Gui, Screen.get_size()))


def test_DrawLayerMatchesFullRender(Screen):
    """Mode jeu : le calque en cache donne le même résultat qu'un rendu complet"""
    Gui, Panel, Title, Ghost, List, Button = BuildScene()
    for Step in range(3):
        Ghost.Position = Udim2(0, 100 + Step * 40, 0, 100)
        List.CanvasPosition = Vector2(0, Step * 30)
        Screen.fill(BACKGROUND)
        Gui.Draw(Screen)
        AssertSame(Screen, FullRender(Gui, Screen.get_size()))


def test_ButtonHoverRedrawsButtonOnly(Screen, MousePos):
    Gui, Panel, Title, Ghost, List, Button = BuildScene()
    Gui.Render(Screen, BACKGROUND)
    MousePos[0] = Button.GetRect().center
    Gui.HandleEvents([])
    assert Gui.Render(Screen, BACKGROUND) == [Button.GetRect()]


def test_ImageCacheShared(Screen):
    Source = pygame.Surface((40, 20))
    Source.fill((255, 0, 0))
    A = ImageLabel.New(None, Image=Source, Size=Udim2(0, 100, 0, 100))
    B = ImageLabel.New(None, Image=Source, Size=Udim2(0, 100, 0, 100))
    A.Draw(Screen)
    B.Draw(Screen)
    assert A._ImageCacheSurface is B._ImageCacheSurface
    Cached = A._ImageCacheSurface
    A.Draw(Screen)
    assert A._ImageCacheSurface is Cached

    Source.fill((0, 0, 255))
    A.ReloadImage()
    A.Draw(Screen)
    assert A._ImageCacheSurface is not Cached
    assert A._ImageCacheSurface.get_at((50, 50))[:3] == (0, 0, 255)
    ImageCache.Invalidate()


def test_ImageTextButtonLayout():
    Icon = pygame.Surface((10, 10))
    Button = ImageTextButton.New(None, Image=Icon, Size=Udim2(0, 200, 0, 40), ImageTextSpacing=10)
    ImageRect, TextRect = Button._SplitRect()
    assert ImageRect == pygame.Rect(0, 0, 40, 40)
    assert TextRect == pygame.Rect(50, 0, 150, 40)
    Button.ImageAlignment = "background"
    assert Button._SplitRect() == (Button.GetRect(), Button.GetRect())
    Button.Image = None
    Button.ImageAlignment = "left"
    assert Button._GetTextArea() == Button.GetRect()


def test_ScrollShiftMatchesRecompute(Screen):
    Gui = ScreenGui()
    List = ScrollingFrame.New(Gui, Size=Udim2(0, 200, 0, 100), Position=Udim2(0, 0, 0, 0.5), CanvasSize=Udim2(0, 0, 0, 0), AutomaticCanvasSize="y")
    List.AddChild(UIListLayout(Padding=Udim(0, 3)))
    Items = [TextLabel.New(List, Text=f"Item {Index}", Size=Udim2(1, 0, 0, 25.5), LayoutOrder=Index) for Index in range(20)]
    Gui.Render(Screen, BACKGROUND)
    for Scroll in (40, 13.7, 120.25, 0.5, 300, 0):
        List.CanvasPosition = Vector2(0, Scroll)
        Gui.Render(Screen, BACKGROUND)
        Shifted = [(Item.GetRect(), Item._GetCachedDrawBounds()) for Item in Items]
        List._MarkDirty()
        assert Shifted == [(Item.GetRect(), Item._GetDrawBounds()) for Item in Items]
