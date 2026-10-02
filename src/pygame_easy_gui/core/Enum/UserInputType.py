from enum import Enum

class UserInputType(Enum):
    MouseButton1 = 0     # bouton gauche de la souris
    MouseButton2 = 1     # bouton droit de la souris
    MouseButton3 = 2     # bouton du milieu de la souris
    MouseWheel = 3       # molette de la souris
    MouseMovement = 4    # mouvement de la souris (et entrée / sortie de la fenêtre)
    Touch = 7            # appui sur un écran tactile
    Keyboard = 8         # touche du clavier
    Focus = 9            # la fenêtre retrouve le focus
    Accelerometer = 10   # accéléromètre (mobile)
    Gyro = 11            # gyroscope (mobile)
    Gamepad1 = 12        # manettes 1 à 8
    Gamepad2 = 13
    Gamepad3 = 14
    Gamepad4 = 15
    Gamepad5 = 16
    Gamepad6 = 17
    Gamepad7 = 18
    Gamepad8 = 19
    TextInput = 20       # saisie de texte dans un objet texte (TextBox)
    InputMethod = 21     # composition IME en cours (TEXTEDITING)
    None_ = 22           # type inconnu ; « None » est un mot réservé en Python
