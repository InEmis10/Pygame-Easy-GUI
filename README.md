# Pygame-Easy-GUI

Des interfaces pygame à la manière de Roblox : `Frame`, `TextLabel`, `TextButton`,
positions et tailles en `Udim2`, `AnchorPoint`, signaux.

## Installation (développement)

```sh
./init.sh                          # crée .venv (Python via uv) et installe la lib en mode éditable
.venv/bin/python examples/demo.py  # lance la démo
```

## Utilisation

```python
from pygame_easy_gui import Frame, Udim2, Vector2

frame = Frame()
frame.Size = Udim2(0.6, 0, 0.6, 0)
frame.Position = Udim2(0.5, 0, 0.5, 0)
frame.AnchorPoint = Vector2(0.5, 0.5)
```

## Structure

```
src/pygame_easy_gui/
├── __init__.py   API publique (tout s'importe depuis pygame_easy_gui)
├── core/         GuiObject (classe de base, arbre parent/enfants), Signal
├── datatypes/    Udim, Udim2, Vector2
├── widgets/      Frame, TextLabel, TextButton
└── utils/        ArgumentVerifier
examples/         scripts de démo (utilisent la lib comme un utilisateur)
```
