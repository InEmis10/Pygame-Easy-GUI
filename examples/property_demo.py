"""Mini démo des Property : Frame, TextLabel et TextButton avec Color3.

- survol du bouton « Cliquer » : sa couleur change ;
- clic : le compteur augmente, le label se met à jour (GetPropertyChangedSignal("Text")) ;
- bouton « Transparence » : la Frame passe de opaque à semi-transparente (chemin alpha de Frame._Draw).
"""
from functools import lru_cache

from pygame_easy_gui import (Application, Color3, Connect, Frame, ScreenGui, TextButton, TextLabel,
                             Udim2, Vector2)

BUTTON_COLOR = Color3(70, 130, 200)
BUTTON_HOVER_COLOR = Color3(90, 160, 240)
WHITE = Color3(255, 255, 255)

app = Application("Pygame Easy GUI : Property", Size=(900, 600), MinimumSize=(640, 400),
                  BackgroundColor3=Color3.fromHex("#1e1e1e"))

main = ScreenGui.New(Name="Main")
app.Gui.Add(main)

# Rayures derrière la Frame : elles deviennent visibles quand la Frame est semi-transparente
for i in range(6):
    Frame.New(main, Name=f"Stripe{i}", Size=Udim2(0, 40, 1, 0), Position=Udim2(i / 6, 60, 0, 0),
              BackgroundColor3=Color3(200, 80, 80))

frame = Frame.New(main, Name="MainFrame",
                  Size=Udim2(0.6, 0, 0.6, 0), Position=Udim2(0.5, 0, 0.5, 0), AnchorPoint=Vector2(0.5, 0.5),
                  BackgroundColor3=Color3(40, 40, 45), BorderColor3=Color3(200, 200, 200), BorderSizePixel=2)

counter = TextLabel.New(frame, Name="Counter", Text="Clics : 0", TextColor3=WHITE, TextSize=32,
                        Size=Udim2(1, 0, 0, 60), BackgroundTransparency=1.0)

clickButton = TextButton.New(frame, Name="ClickButton", Text="Cliquer", TextColor3=WHITE, TextSize=24,
                             Size=Udim2(0.5, 0, 0, 60), Position=Udim2(0.5, 0, 0.45, 0),
                             AnchorPoint=Vector2(0.5, 0.5), BackgroundColor3=BUTTON_COLOR)

alphaButton = TextButton.New(frame, Name="AlphaButton", Text="Transparence", TextColor3=WHITE, TextSize=20,
                             Size=Udim2(0.5, 0, 0, 44), Position=Udim2(0.5, 0, 0.75, 0),
                             AnchorPoint=Vector2(0.5, 0.5), BackgroundColor3=Color3(60, 60, 70))

clicks = 0


@Connect(clickButton.MouseEnter)
def OnClickEnter():
    clickButton.BackgroundColor3 = BUTTON_HOVER_COLOR


@Connect(clickButton.MouseLeave)
def OnClickLeave():
    clickButton.BackgroundColor3 = BUTTON_COLOR


@Connect(clickButton.MouseButton1Click)
def OnClick():
    global clicks
    clicks += 1
    counter.Text = f"Clics : {clicks}"


@Connect(counter.GetPropertyChangedSignal("Text"))
def OnCounterTextChanged():
    print("Text a changé :", counter.Text)


@Connect(alphaButton.MouseButton1Click)
def OnToggleAlpha():
    frame.BackgroundTransparency = 0.5 if frame.BackgroundTransparency == 0.0 else 0.0

@Connect(frame.Changed)
def OnFrameChanged(name):
    print("Frame :", name, "=", getattr(frame, name))


app.run()
