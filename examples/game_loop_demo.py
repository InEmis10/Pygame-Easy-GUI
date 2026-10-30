import pygame
from pygame_easy_gui import (
    GuiObject, ScreenGui, Frame, ScrollingFrame, TextLabel, TextButton, TextBox,
    Udim, Udim2, Vector2, Color3, Connect,
    UICorner, UIStroke, UIPadding, UIListLayout, UIGradient, ColorSequence,
    TweenService, TweenInfo,
)


class Rect(GuiObject):
    def __init__(self, Color=(255, 0, 0)):
        super().__init__()
        self.Name = "Rect"
        self.Color = Color

    def _Draw(self, Surface: pygame.Surface):
        Rect = self.GetRect()
        pygame.draw.rect(Surface, self.Color, Rect)
        pygame.draw.rect(Surface, (0, 0, 0), Rect, 2)


def main():
    pygame.init()
    Screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    Clock = pygame.time.Clock()

    Gui = ScreenGui()

    MainFrame = Frame()
    MainFrame.Name = "MainFrame"
    MainFrame.Size = Udim2(0.6, 0, 0.7, 0)
    MainFrame.Position = Udim2(0.5, 0, 0.5, 0)
    MainFrame.AnchorPoint = Vector2(0.5, 0.5)
    MainFrame.BackgroundColor3 = Color3(40, 40, 45)
    MainFrame.AddChild(UICorner(CornerRadius=Udim(0, 12)))
    MainFrame.AddChild(UIStroke(Color=Color3(200, 200, 200), Thickness=2))
    MainFrame.AddChild(UIPadding(PaddingLeft=Udim(0, 16), PaddingRight=Udim(0, 16), PaddingTop=Udim(0, 8), PaddingBottom=Udim(0, 16)))
    Gui.AddChild(MainFrame)

    Title = TextLabel()
    Title.Name = "Title"
    Title.Text = "Menu Principal"
    Title.TextColor3 = (255, 255, 255)
    Title.TextSize = 32
    Title.Size = Udim2(1, 0, 0, 50)
    Title.BackgroundTransparency = 1.0
    MainFrame.AddChild(Title)

    NameBox = TextBox.New(
        MainFrame,
        Size=Udim2(1, 0, 0, 36), Position=Udim2(0, 0, 0, 56),
        PlaceholderText="Ton pseudo...", TextColor3=(255, 255, 255), BackgroundColor3=Color3(25, 25, 30),
    )
    NameBox.AddChild(UICorner(CornerRadius=Udim(0, 6)))
    NameBox.AddChild(UIPadding(PaddingLeft=Udim(0, 8), PaddingRight=Udim(0, 8)))

    PlayButton = TextButton()
    PlayButton.Name = "PlayButton"
    PlayButton.Text = "Jouer"
    PlayButton.TextColor3 = (255, 255, 255)
    PlayButton.TextSize = 24
    PlayButton.Size = Udim2(1, 0, 0, 50)
    PlayButton.Position = Udim2(0, 0, 0, 100)
    PlayButton.BackgroundColor3 = Color3.fromHex("#4682c8")
    PlayButton.AddChild(UICorner())
    PlayButton.AddChild(UIGradient(Color=ColorSequence((255, 255, 255), (170, 170, 220)), Rotation=90))

    # Animation au survol
    HoverInfo = TweenInfo(0.15, "quad", "out")
    PlayButton.MouseEnter.Connect(lambda: TweenService.Create(PlayButton, HoverInfo, {"TextSize": 28}).Play())
    PlayButton.MouseLeave.Connect(lambda: TweenService.Create(PlayButton, HoverInfo, {"TextSize": 24}).Play())

    @Connect(PlayButton.MouseButton1Click)
    def OnButtonClick():
        print(f"Button Clicked : {NameBox.Text or 'anonyme'}")

    @Connect(NameBox.FocusLost)
    def OnNameEntered(EnterPressed):
        if EnterPressed:
            OnButtonClick()

    MainFrame.AddChild(PlayButton)

    # Liste défilante : le canvas s'agrandit tout seul avec les éléments
    Levels = ScrollingFrame.New(
        MainFrame,
        Size=Udim2(1, 0, 1, -160), Position=Udim2(0, 0, 0, 160),
        BackgroundColor3=Color3(30, 30, 35), CanvasSize=Udim2(0, 0, 0, 0), AutomaticCanvasSize="y",
    )
    Levels.AddChild(UIListLayout(Padding=Udim(0, 4)))
    Levels.AddChild(UIPadding(PaddingLeft=Udim(0, 4), PaddingRight=Udim(0, 12), PaddingTop=Udim(0, 4), PaddingBottom=Udim(0, 4)))
    for i in range(1, 16):
        Level = TextButton.New(
            Levels,
            Text=f"Niveau {i}", TextColor3=(230, 230, 230), TextSize=20,
            Size=Udim2(1, 0, 0, 32), BackgroundColor3=Color3(55, 55, 65), LayoutOrder=i,
        )
        Level.MouseButton1Click.Connect(lambda Index=i: print(f"Niveau {Index} choisi"))

    Mover = Rect(Color=(50, 200, 50))
    Mover.Name = "Mover"
    Mover.Size = Udim2(0, 40, 0, 40)
    Mover.Position = Udim2(0, 100, 0, 100)
    Gui.AddChild(Mover)

    Running = True
    while Running:
        Dt = Clock.tick(60) / 1000.0
        Events = Gui.HandleEvents(pygame.event.get())

        for Event in Events:
            if Event.type == pygame.QUIT:
                Running = False
            elif Event.type == pygame.KEYDOWN:
                if Event.key == pygame.K_SPACE:
                    MainFrame.Visible = not MainFrame.Visible
                    print(f"Frame.Visible = {MainFrame.Visible}")

        # Pas de déplacement pendant la saisie dans la TextBox
        if Gui.GetFocusedObject() is None:
            Keys = pygame.key.get_pressed()
            Move = pygame.Vector2(0, 0)
            Speed = 200 * Dt
            if Keys[pygame.K_LEFT]:
                Move.x -= Speed
            if Keys[pygame.K_RIGHT]:
                Move.x += Speed
            if Keys[pygame.K_UP]:
                Move.y -= Speed
            if Keys[pygame.K_DOWN]:
                Move.y += Speed
            if Move.length_squared() > 0:
                Old = Mover.Position
                Mover.Position = Udim2(0, Old.X.Offset + Move.x, 0, Old.Y.Offset + Move.y)

        Gui.Update(Dt)
        Screen.fill((30, 30, 30))
        Gui.Draw(Screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
