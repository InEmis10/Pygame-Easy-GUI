# Pygame-Easy-GUI

Des interfaces **pygame** à la manière de Roblox : positions en `Udim2` (échelle + pixels), `AnchorPoint`, signaux `MouseButton1Click`, layouts `UIListLayout`, tweens, etc.

- Composants : `Frame`, `ScrollingFrame`, `TextLabel`, `TextButton`, `TextBox`, `ImageLabel`, `ImageButton`, `ImageTextButton`
- Rendu optimisé : seules les zones qui changent sont redessinées, images et textes mis en cache
- Modificateurs : `UIListLayout`, `UIGridLayout`, `UIPadding`, `UICorner`, `UIStroke`, `UIGradient`, `UISizeConstraint`, `UITextSizeConstraint`
- Événements : survol, clics gauche / droit, molette, focus clavier, blocage des clics par les objets du dessus
- Animations : `TweenService` / `TweenInfo`
- Minuteurs : `TimeService.Delay` / `TimeService.Every`
- Signaux de changement : `Changed`, `GetPropertyChangedSignal("Text")`
- Tags (`AddTag` + `CollectionService`), attributs (`SetAttribute`), `Color3`, `ColorSequence`, `NumberSequence`, `IntValue`

Nécessite **Python 3.10+** et **pygame-ce 2.5+**.

## Installation

Dans le projet qui utilise la lib (un tool, un jeu...), avec son environnement virtuel activé :

```sh
# Depuis GitHub, figé sur une version (recommandé)
pip install "pygame-easy-gui @ git+https://github.com/InEmis10/Pygame-Easy-GUI.git@v1.0.0"

# Depuis le dossier local, en éditable : les modifications de la lib sont visibles tout de suite
pip install -e ~/Pygame-Easy-GUI
```

Pour le déclarer comme dépendance, dans le `requirements.txt` du projet :

```text
pygame-easy-gui @ git+https://github.com/InEmis10/Pygame-Easy-GUI.git@v1.0.0
```

ou dans son `pyproject.toml` : `dependencies = ["pygame-easy-gui @ git+https://github.com/InEmis10/Pygame-Easy-GUI.git@v1.0.0"]`.

`pygame-ce` est installé automatiquement. Ne pas installer `pygame` en plus : les deux occupent le même module `pygame`.

```python
import pygame_easy_gui
print(pygame_easy_gui.__version__)   # 1.0.0
```

## Développement

```sh
./init.sh                                   # crée .venv (uv si présent, sinon python3 -m venv), installe la lib en éditable + pytest
.venv/bin/python -m pytest                  # lance les tests
.venv/bin/python examples/property_demo.py  # lance une démo
```

Ou à la main : `pip install -e ".[dev]"` (le `[dev]` ajoute pytest).

Nouvelle version : changer `__version__` dans `src/pygame_easy_gui/__init__.py` (seul endroit où elle est écrite), compléter `CHANGELOG.md`, puis `git tag vX.Y.Z && git push --tags`.

## Application

`Application` crée la fenêtre et fait tourner la boucle. Elle attend les événements quand rien ne bouge (pas de CPU gaspillé) et ne redessine que les zones modifiées.

```python
from pygame_easy_gui import Application, ScreenGui, Frame, TextButton, Udim2, Vector2, UICorner, Color3

App = Application("Mon appli", Size=(900, 600), MinimumSize=(640, 400), BackgroundColor3=Color3(30, 30, 30))
Main = ScreenGui.New(Name="Main")
App.Gui.Add(Main)

Menu = Frame.New(Main, Size=Udim2(0, 300, 0, 200), Position=Udim2(0.5, 0, 0.5, 0), AnchorPoint=Vector2(0.5, 0.5))
Menu.AddChild(UICorner())
Quit = TextButton.New(Menu, Text="Quitter", Size=Udim2(1, -20, 0, 50), Position=Udim2(0, 10, 0, 10))
Quit.MouseButton1Click.Connect(App.Stop)

App.run()
```

- Propriétés de la fenêtre (avant `run()`) : `Title`, `Icon`, `Size`, `MinimumSize`, `MaximumSize`, `Position`, `Display`, `Resizable`, `Borderless`, `Fullscreen`, `Maximized`, `Hidden`, `AlwaysOnTop`, `Opacity`, `AllowHighDpi`, `MouseGrabbed`, `KeyboardGrabbed`, `BackgroundColor3`, `MaxFPS`, `EventTimeOut`.
- Signaux : `Resized(Taille)`, `FocusGained`, `FocusLost`, `Closing`, `Heartbeat(Dt)`, `UnhandledEvent(Event)` (événements que la GUI n'a pas consommés).
- Plusieurs `ScreenGui` : `App.Gui.Add(Hud)`. Le plus grand `DisplayOrder` est dessiné au-dessus et reçoit la souris en premier ; ce qu'il consomme n'arrive pas aux autres. `Enabled = False` cache tout un `ScreenGui`.
- `@OnEvent(pygame.KEYDOWN)` sur une méthode d'une sous-classe d'`Application` l'appelle pour cet événement.

## Dans la boucle d'un jeu

Si tu as déjà ta propre boucle, utilise directement un `ScreenGui` :

```python
import pygame
from pygame_easy_gui import ScreenGui, TextButton, Udim2

pygame.init()
Screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
Clock = pygame.time.Clock()

Gui = ScreenGui()
Play = TextButton.New(Gui, Text="Jouer", Size=Udim2(0, 200, 0, 50))
Play.MouseButton1Click.Connect(lambda: print("Go !"))

Running = True
while Running:
    Dt = Clock.tick(60) / 1000
    for Event in Gui.HandleEvents(pygame.event.get()):   # events non consommés par la GUI
        if Event.type == pygame.QUIT:
            Running = False
    Gui.Update(Dt)
    Screen.fill((30, 30, 30))
    Gui.Draw(Screen)
    pygame.display.flip()
```

`examples/game_loop_demo.py` contient une démo plus complète (TextBox, liste défilante, contour, coins arrondis, dégradé, tween).

## Concepts

**Udim2(ScaleX, OffsetX, ScaleY, OffsetY)** : `Scale` est relatif à la taille du parent, `Offset` est en pixels.
`Udim2(0.5, 0, 0, 40)` = moitié de la largeur du parent, 40 px de haut. `Udim2.fromOffset(x, y)` et `Udim2.fromScale(x, y)` sont des raccourcis.
Les `Udim`, `Udim2`, `Vector2` et `Color3` sont **immuables** : on assigne une nouvelle valeur (`Obj.Position = Udim2(...)`).

**AnchorPoint** : le point de l'objet placé à `Position`. `Vector2(0.5, 0.5)` = centré.

**Hiérarchie** : `Parent.AddChild(Enfant)` ou `Enfant.Parent = Parent`, ou `Classe.New(Parent, Propriété=Valeur, ...)`.
`Destroy()` retire l'objet, détruit ses enfants, déconnecte ses signaux et retire ses tags.

**Active** : seuls les objets `Active` reçoivent la souris, et le plus haut bloque ceux du dessous.
Par défaut : `Frame`, `ScrollingFrame`, boutons et `TextBox` sont actifs ; `TextLabel`, `ImageLabel` et `GuiObject` laissent passer les clics.

**Événements non consommés** : `Gui.HandleEvents()` retourne les events que la GUI n'a pas utilisés. Un clic sur un bouton ou une touche tapée dans une `TextBox` n'arrive donc pas au jeu. `Gui.IsMouseOverGui()` et `Gui.GetFocusedObject()` aident aussi.

## Composants

| Composant | Propriétés principales |
| --- | --- |
| `GuiObject` (base) | `Position`, `Size`, `AnchorPoint`, `Visible`, `ZIndex`, `LayoutOrder`, `ClipsDescendants`, `Active`, `BackgroundColor3`, `BackgroundTransparency`, `BorderColor3`, `BorderSizePixel` |
| `TextLabel` | `Text`, `TextColor3`, `TextSize`, `FontName`, `TextTransparency`, `TextXAlignment`, `TextYAlignment`, `TextWrapped`, `TextTruncate` (`"atend"`), `TextScaled`, `TextBounds`, signal `TextChanged` |
| `TextButton` / `ImageButton` | `AutoButtonColor`, signaux `MouseButton1Click/Down/Up`, `MouseButton2Click/Down/Up`, `Activated` ; `ImageButton` : `HoverImage`, `PressedImage` |
| `TextBox` | `PlaceholderText`, `PlaceholderColor3`, `ClearTextOnFocus`, `MultiLine`, `TextEditable`, `MaxLength`, `CursorPosition`, `SelectionStart`, `SelectionColor3`, `CaptureFocus()`, `ReleaseFocus()`, `SelectAll()`, `GetSelectedText()`, `Copy()`, `Cut()`, `Paste()`, signaux `Focused`, `FocusLost(EnterPressed)` |
| `ImageTextButton` | Tout `ImageButton` + `TextLabel` ; `ImageAlignment` (`"left"`, `"right"`, `"background"`), `ImageTextSpacing` |
| `ImageLabel` | `Image` (chemin ou `pygame.Surface`), `ImageColor3`, `ImageTransparency`, `ScaleType` (`"stretch"`, `"fit"`, `"crop"`) |
| `ScrollingFrame` | `CanvasSize`, `CanvasPosition`, `AutomaticCanvasSize` (`"x"`, `"y"`, `"xy"`), `ScrollingDirection`, `ScrollingEnabled`, `ScrollStep`, `ScrollBarThickness`, `ScrollBarImageColor3` |

**Sélection et presse-papiers (`TextBox`)** : Maj + flèches / Home / End, glisser la souris, Maj + clic, double-clic (mot), Ctrl + A ; Ctrl + C / X / V (presse-papiers du système, ou interne s'il n'est pas disponible).
Chaque action se désactive : `SelectionEnabled`, `CopyEnabled`, `CutEnabled`, `PasteEnabled`. Avec `TextEditable = False`, on peut encore sélectionner et copier, mais pas couper ni coller.

Tous les `GuiObject` ont les signaux `MouseEnter`, `MouseLeave`, `MouseMoved(X, Y)`, `MouseWheel(X, Y)`, `InputBegan(Event)`, `InputEnded(Event)`.

Les alignements et modes sont des chaînes, insensibles à la casse : `"left"`, `"center"`, `"right"`, `"top"`, `"bottom"`, `"vertical"`, `"horizontal"`.

## Rendu

Un objet qui ne change pas n'est **jamais redessiné**. Chaque modification d'une propriété (`Position`, `Text`, `BackgroundColor3`, survol d'un bouton...) enregistre l'ancienne et la nouvelle zone de l'objet ; au rendu, seules ces zones (fusionnées) sont redessinées.

- **Jeu** (l'écran est effacé à chaque frame) : `Gui.Draw(Screen)`. La GUI est gardée dans un calque transparent en cache, mis à jour uniquement là où elle change, puis collé en un seul blit.
- **Appli** : `Application` le fait toute seule. Dans une boucle maison où rien ne bouge derrière la GUI, `Render` redessine seulement les zones modifiées directement sur l'écran :

```python
Rects = Gui.Render(Screen, Background=(30, 30, 30))   # couleur ou pygame.Surface de fond
pygame.display.update(Rects)                          # [] si rien n'a changé
```

Si le fond donné à `Render` change, appeler `Gui.ForceRedraw()` (avec `Application` : `App.RequestRedraw()`).

Caches :
- les images sont chargées une seule fois, et chaque taille / teinte n'est calculée qu'une fois, **partagée entre tous les objets** (`render/ImageCache.py`). Si une `pygame.Surface` utilisée comme `Image` est modifiée, appeler `Label.ReloadImage()` ;
- le texte rendu est gardé tant que le texte, la police ou la taille ne changent pas ;
- les fonds semi-transparents sont réutilisés ;
- le défilement d'une `ScrollingFrame` décale les enfants sans recalculer leur layout et ne redessine que la frame.

## Modificateurs (UI…)

Ils s'ajoutent comme des enfants et modifient leur parent :

```python
from pygame_easy_gui import UIListLayout, UIPadding, UIStroke, Udim

List.AddChild(UIListLayout(Padding=Udim(0, 4), HorizontalAlignment="center"))
List.AddChild(UIPadding(PaddingLeft=Udim(0, 8), PaddingTop=Udim(0, 8)))
Button.AddChild(UIStroke(Color=(255, 255, 255), Thickness=2))
```

| Modificateur | Effet |
| --- | --- |
| `UIListLayout` | Empile les enfants (`FillDirection`, `Padding`, alignements, `SortOrder`, `Wraps` = retour à la ligne) ; `AbsoluteContentSize` |
| `UIGridLayout` | Grille (`CellSize`, `CellPadding`, `FillDirection`, `FillDirectionMaxCells`, `StartCorner`) ; `AbsoluteCellSize`, `AbsoluteCellCount` |
| `UIGradient` | Dégradé multiplié sur le parent (`Color` : `ColorSequence`, `Transparency` : `NumberSequence`, `Rotation`, `Offset`, `Enabled`) |
| `UIPadding` | Marges intérieures (`PaddingLeft/Right/Top/Bottom`) |
| `UICorner` | Coins arrondis (`CornerRadius`) |
| `UIStroke` | Contour (`Color`, `Thickness`, `Transparency`) |
| `UISizeConstraint` | Taille min / max en pixels (`MinSize`, `MaxSize`) |
| `UITextSizeConstraint` | Taille de police min / max avec `TextScaled` |

```python
from pygame_easy_gui import UIGradient, ColorSequence, NumberSequence

Button.AddChild(UIGradient(Color=ColorSequence((255, 80, 80), (80, 80, 255)), Rotation=90))
Panel.AddChild(UIGradient(Transparency=NumberSequence(0, 1)))   # s'efface vers la droite
```

## Animations (TweenService)

```python
from pygame_easy_gui import TweenService, TweenInfo, Udim2, Color3

Info = TweenInfo(0.5, "quad", "out")   # Time, EasingStyle, EasingDirection, RepeatCount, Reverses, DelayTime
Tween = TweenService.Create(Menu, Info, {"Position": Udim2(0.5, 0, 0.5, 0), "BackgroundColor3": Color3(255, 0, 0)})
Tween.Completed.Connect(lambda State: print(State))   # "Completed" ou "Cancelled"
Tween.Play()   # Pause(), Cancel()
```

- Styles : `linear`, `sine`, `quad`, `cubic`, `quart`, `quint`, `exponential`, `circular`, `back`, `elastic`, `bounce` ; directions : `in`, `out`, `inout`.
- Propriétés animables : nombres, `Udim`, `Udim2`, `Vector2`, couleurs, booléens (changés à la fin), sur un `GuiObject` comme sur un `UIComponent` (ex: `UIGradient.Offset` pour un effet de brillance).
- `RepeatCount = -1` répète à l'infini ; `Reverses` revient à la valeur de départ à chaque répétition.
- Un nouveau tween sur une propriété déjà animée annule l'ancien.
- Les tweens avancent en temps réel, tout seuls avec `Application`, ou à chaque `Gui.Update(Dt)` dans une boucle maison. Sans `ScreenGui`, appeler `TweenService.Step()` à chaque frame.

## Minuteurs (TimeService)

```python
from pygame_easy_gui import TimeService

TimeService.Delay(2, print, "2 secondes plus tard")   # une fois : Delay(Seconds, Callback, *Args)
Blink = TimeService.Every(0.5, Cursor.ToggleVisible)  # en boucle, toutes les 0.5 s
Blink.Cancel()                                        # Blink.Active vaut alors False
```

- Les callbacks sont appelés dans la boucle principale (pas de thread) : ils peuvent modifier la GUI sans risque.
- Avec `Application`, la boucle se réveille d'elle-même à l'échéance du prochain timer. Dans une boucle maison, `Gui.Update(Dt)` fait avancer les timers ; sans `ScreenGui`, appeler `TimeService.Step()` à chaque frame.
- `Delay(0, ...)` appelle la fonction au prochain tour de boucle.
- Si la boucle a été bloquée plusieurs périodes, un `Every` n'est appelé qu'une fois (pas de rafale), puis reprend son rythme.
- Une erreur dans un callback est affichée sans arrêter les autres timers.

## Signaux de changement

```python
Label.GetPropertyChangedSignal("Text").Connect(lambda: print("Nouveau texte :", Label.Text))
Label.Changed.Connect(lambda Property: print(Property, "a changé"))
```

Ils se déclenchent pour toute propriété publique, uniquement si la valeur change vraiment.

## Tags

```python
from pygame_easy_gui import CollectionService

Button.AddTag("MenuButton")
for Obj in CollectionService.GetTagged("MenuButton"):
    Obj.Visible = False
CollectionService.GetInstanceAddedSignal("MenuButton").Connect(print)
```

## Créer un composant

Hérite de `GuiObject` (ou d'un composant existant) et redéfinis `_Draw(Surface)` et, au besoin, `_Update(Dt)`.
Les propriétés publiques (`self.Color = ...`) redessinent l'objet automatiquement. Pour un état privé qui change l'affichage, ajoute son nom à `_RenderAttributes` (ex: `_RenderAttributes = frozenset({"_Hovering"})`) ou appelle `self._MarkRenderDirty()`.
Si `_Draw` dessine en dehors de `GetRect()`, redéfinis `_GetDrawBounds()` pour retourner la zone réellement touchée.
Pour un composant interactif : `self.Active = True`, puis les hooks `_OnMouseDown`, `_OnMouseUp`, `_OnMouseDrag`, `_OnMouseWheel`, `_OnKeyDown`, `_OnTextInput` (voir `core/mixins/InputMixin.py`).
`ButtonMixin` donne tout le comportement d'un bouton : `class MonBouton(ButtonMixin, ImageLabel)`.

## Structure

```
src/pygame_easy_gui/
├── __init__.py   API publique et __version__ (tout s'importe depuis pygame_easy_gui)
├── core/         Application, GuiObject (arbre, layout, rendu par zones), EventManager, Signal, mixins
├── datatypes/    Udim, Udim2, Vector2, Color3, ColorSequence, NumberSequence, IntValue
├── components/   UIPadding, UICorner, UIStroke, UIGradient, UIListLayout, UIGridLayout, contraintes
├── widgets/      Frame, ScrollingFrame, ScreenGui, TextLabel, TextButton, TextBox, ImageLabel, ImageButton...
├── services/     TweenService, TimeService, CollectionService, Clipboard
├── render/       dessin, caches d'images / de texte, surface de la fenêtre
└── utils/        ArgumentVerifier
examples/         scripts de démo (utilisent la lib comme un utilisateur)
tests/            .venv/bin/python -m pytest
```

Les fichiers sont en PascalCase, au nom de la classe principale qu'ils contiennent (`widgets/TextBox.py` → `TextBox`, `datatypes/Udim.py` → `Udim` et `Udim2`).
