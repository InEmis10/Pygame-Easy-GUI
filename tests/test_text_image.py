import pygame
import pytest
from pygame_easy_gui import ScreenGui, TextBox, TextLabel, ImageLabel, ImageButton, Frame, Udim2, UITextSizeConstraint
from pygame_easy_gui.render import Text as TextRender
from conftest import Click


def Key(Gui, KeyCode, Mod=0):
    return Gui.HandleEvents([pygame.event.Event(pygame.KEYDOWN, key=KeyCode, mod=Mod, unicode="")])


def Type(Gui, Text):
    return Gui.HandleEvents([pygame.event.Event(pygame.TEXTINPUT, text=Text)])


def test_WrapAndEllipsize():
    Font = TextRender.GetFont(None, 20)
    Lines = TextRender.WrapText(Font, "hello world this is long", Font.size("hello world")[0])
    assert Lines[0] == "hello world" and len(Lines) > 1
    assert all(Font.size(Line)[0] <= Font.size("hello world")[0] for Line in Lines)
    Short = TextRender.Ellipsize(Font, "a very long sentence indeed", 60)
    assert Short.endswith("...") and Font.size(Short)[0] <= 60


def test_TextScaledRespectsConstraint():
    Gui = ScreenGui()
    Label = TextLabel.New(Gui, Size=Udim2(0, 300, 0, 100), Text="Hi", TextScaled=True)
    Label.AddChild(UITextSizeConstraint(MaxTextSize=30))
    Label.Draw(pygame.display.get_surface())
    assert Label.TextBounds.Y <= Label._GetFont(30).get_linesize()


def test_TextChanged():
    Label = TextLabel()
    Received = []
    Label.TextChanged.Connect(Received.append)
    Label.Text = "a"
    Label.Text = "a"
    assert Received == ["a"]


def test_TextBoxTyping(MousePos):
    Gui = ScreenGui()
    Box = TextBox.New(Gui, Size=Udim2(0, 200, 0, 30), MaxLength=8)
    Lost = []
    Box.FocusLost.Connect(Lost.append)

    # Sans focus : le clavier est rendu au jeu
    assert len(Type(Gui, "x")) == 1

    MousePos[0] = (10, 10)
    Click(Gui, (10, 10))
    assert Box.IsFocused() and Gui.GetFocusedObject() is Box
    assert Type(Gui, "hello") == []
    Type(Gui, " world")
    assert Box.Text == "hello wo"          # MaxLength

    Key(Gui, pygame.K_BACKSPACE, pygame.KMOD_CTRL)
    assert Box.Text == "hello "
    Key(Gui, pygame.K_HOME)
    Type(Gui, ">")
    assert Box.Text == ">hello "
    Key(Gui, pygame.K_END)
    Key(Gui, pygame.K_LEFT)
    Key(Gui, pygame.K_DELETE)
    assert Box.Text == ">hello"

    Key(Gui, pygame.K_RETURN)
    assert not Box.IsFocused() and Lost == [True]


def test_TextBoxClickOutsideAndHide(MousePos):
    Gui = ScreenGui()
    Box = TextBox.New(Gui, Size=Udim2(0, 200, 0, 30))
    Lost = []
    Box.FocusLost.Connect(Lost.append)
    Box.CaptureFocus()
    MousePos[0] = (500, 500)
    Click(Gui, (500, 500))
    assert Lost == [False]
    Box.CaptureFocus()
    Box.Visible = False
    Gui.HandleEvents([])
    assert not Box.IsFocused()


def test_TextBoxMultiLineAndDraw(MousePos, Screen):
    Gui = ScreenGui()
    Box = TextBox.New(Gui, Size=Udim2(0, 100, 0, 30), MultiLine=True)
    Box.CaptureFocus()
    Type(Gui, "abc")
    Key(Gui, pygame.K_RETURN)
    Type(Gui, "de")
    assert Box.Text == "abc\nde" and Box.IsFocused()
    Key(Gui, pygame.K_UP)
    assert Box.CursorPosition == 2
    Type(Gui, "x" * 50)   # dépasse : défilement horizontal, pas d'erreur
    Gui.Update(0.016)
    Gui.Draw(Screen)


def test_TextBoxRequiresScreenGui():
    with pytest.raises(RuntimeError):
        TextBox().CaptureFocus()


def test_ImageScaleTypes(Screen, tmp_path):
    Source = pygame.Surface((40, 20))
    Source.fill((255, 0, 0))
    Path = tmp_path / "red.png"
    pygame.image.save(Source, str(Path))

    Gui = ScreenGui()
    for Mode in ("stretch", "fit", "crop"):
        Image = ImageLabel.New(Gui, Image=str(Path), Size=Udim2(0, 100, 0, 100), ScaleType=Mode, BackgroundColor3=(0, 0, 0))
        Image._Draw(Screen)
    assert Image._ImageCacheSurface.get_size() == (100, 100)

    Fit = ImageLabel.New(Gui, Image=Source, Size=Udim2(0, 100, 0, 100), ScaleType="fit")
    Fit._Draw(Screen)
    assert Fit._ImageCacheSurface.get_size() == (100, 50)

    with pytest.raises(FileNotFoundError):
        ImageLabel().Image = str(tmp_path / "missing.png")


def test_ImageButtonHoverImage(MousePos):
    Gui = ScreenGui()
    Normal, Hover = pygame.Surface((10, 10)), pygame.Surface((10, 10))
    Button = ImageButton.New(Gui, Image=Normal, HoverImage=Hover, Size=Udim2(0, 50, 0, 50))
    assert Button._GetImage() is Normal
    MousePos[0] = (10, 10)
    Gui.HandleEvents([])
    assert Button._GetImage() is Hover
