"""Démo de l'Application : ScreenGui, Frame, TextLabel, TextButton et @Connect.

Le bouton « Jouer » réagit au survol et au clic, le bouton « HUD » affiche / cache tout le ScreenGui HUD.
"""
from pygame_easy_gui import (Application, Color3, Connect, Frame, ScreenGui, TextButton, TextLabel,
                             Udim2, Vector2)

app = Application("Pygame Easy GUI : démo", Size=(1000, 650), MinimumSize=(640, 400),
                  BackgroundColor3=Color3.fromHex("#1e1e1e"))

# ---- Interface principale
main = ScreenGui.New(Name="Main")
app.Gui.Add(main)

frame = Frame.New(main, Name="MainFrame",
                  Size=Udim2(0.6, 0, 0.6, 0), Position=Udim2(0.5, 0, 0.5, 0), AnchorPoint=Vector2(0.5, 0.5),
                  BackgroundColor3=(40, 40, 45), BorderColor3=(200, 200, 200), BorderSizePixel=2)

TextLabel.New(frame, Name="Title", Text="Menu Principal", TextColor3=(255, 255, 255), TextSize=32,
              Size=Udim2(1, 0, 0, 50), BackgroundTransparency=1.0)

play = TextButton.New(frame, Name="PlayButton", Text="Jouer", TextColor3=(255, 255, 255), TextSize=24,
                      Size=Udim2(0.5, 0, 0, 60), Position=Udim2(0.5, 0, 0.45, 0), AnchorPoint=Vector2(0.5, 0.5),
                      BackgroundColor3=(70, 130, 200))

toggle = TextButton.New(frame, Name="HudButton", Text="Afficher / cacher le HUD", TextColor3=(255, 255, 255),
                        TextSize=20, Size=Udim2(0.5, 0, 0, 44), Position=Udim2(0.5, 0, 0.75, 0),
                        AnchorPoint=Vector2(0.5, 0.5), BackgroundColor3=(60, 60, 70))

# ---- HUD : un second ScreenGui, dessiné au-dessus (DisplayOrder plus grand)
hud = ScreenGui.New(Name="HUD", DisplayOrder=10)
app.Gui.Add(hud)

TextLabel.New(hud, Name="Info", Text="HUD (DisplayOrder = 10)", TextColor3=(255, 220, 120), TextSize=20,
              Size=Udim2(0, 260, 0, 36), Position=Udim2(1, -12, 0, 12), AnchorPoint=Vector2(1, 0),
              BackgroundColor3=(0, 0, 0), BackgroundTransparency=0.4)


@Connect(play.MouseEnter)
def OnPlayEnter():
    play.BackgroundColor3 = (90, 160, 240)


@Connect(play.MouseLeave)
def OnPlayLeave():
    play.BackgroundColor3 = (70, 130, 200)


@Connect(play.MouseButton1Click)
def OnPlayClick():
    print("Jouer !")


@Connect(toggle.MouseButton1Click)
def OnToggleHud():
    hud.Enabled = not hud.Enabled


@Connect(app.Resized)
def OnResized(size):
    print("Nouvelle taille :", size)


app.run()
