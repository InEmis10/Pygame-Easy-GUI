import pygame

from pygame_easy_gui.core.Signal import Signal


class KeyCode:
    def __new__(cls, *args, **kwargs):
        raise TypeError("KeyCode n'est pas instanciable : utiliser KeyCode.A, KeyCode.Space, ...")

    A = pygame.K_a
    B = pygame.K_b
    C = pygame.K_c
    D = pygame.K_d
    E = pygame.K_e
    F = pygame.K_f
    G = pygame.K_g
    H = pygame.K_h
    I = pygame.K_i
    J = pygame.K_j
    K = pygame.K_k
    L = pygame.K_l
    M = pygame.K_m
    N = pygame.K_n
    O = pygame.K_o
    P = pygame.K_p
    Q = pygame.K_q
    R = pygame.K_r
    S = pygame.K_s
    T = pygame.K_t
    U = pygame.K_u
    V = pygame.K_v
    W = pygame.K_w
    X = pygame.K_x
    Y = pygame.K_y
    Z = pygame.K_z


    Zero  = pygame.K_0
    One   = pygame.K_1
    Two   = pygame.K_2
    Three = pygame.K_3
    Four  = pygame.K_4
    Five  = pygame.K_5
    Six   = pygame.K_6
    Seven = pygame.K_7
    Eight = pygame.K_8
    Nine  = pygame.K_9


    F1  = pygame.K_F1
    F2  = pygame.K_F2
    F3  = pygame.K_F3
    F4  = pygame.K_F4
    F5  = pygame.K_F5
    F6  = pygame.K_F6
    F7  = pygame.K_F7
    F8  = pygame.K_F8
    F9  = pygame.K_F9
    F10 = pygame.K_F10
    F11 = pygame.K_F11
    F12 = pygame.K_F12
    F13 = pygame.K_F13
    F14 = pygame.K_F14
    F15 = pygame.K_F15


    KeypadZero     = pygame.K_KP_0
    KeypadOne      = pygame.K_KP_1
    KeypadTwo      = pygame.K_KP_2
    KeypadThree    = pygame.K_KP_3
    KeypadFour     = pygame.K_KP_4
    KeypadFive     = pygame.K_KP_5
    KeypadSix      = pygame.K_KP_6
    KeypadSeven    = pygame.K_KP_7
    KeypadEight    = pygame.K_KP_8
    KeypadNine     = pygame.K_KP_9
    KeypadDivide   = pygame.K_KP_DIVIDE
    KeypadEnter    = pygame.K_KP_ENTER
    KeypadEquals   = pygame.K_KP_EQUALS
    KeypadMinus    = pygame.K_KP_MINUS
    KeypadMultiply = pygame.K_KP_MULTIPLY
    KeypadPeriod   = pygame.K_KP_PERIOD
    KeypadPlus     = pygame.K_KP_PLUS


    CapsLock     = pygame.K_CAPSLOCK
    LeftAlt      = pygame.K_LALT
    LeftControl  = pygame.K_LCTRL
    LeftShift    = pygame.K_LSHIFT
    LeftSuper    = pygame.K_LGUI
    Mode         = pygame.K_MODE
    NumLock      = pygame.K_NUMLOCK
    RightAlt     = pygame.K_RALT
    RightControl = pygame.K_RCTRL
    RightShift   = pygame.K_RSHIFT
    RightSuper   = pygame.K_RGUI
    ScrollLock   = pygame.K_SCROLLLOCK


    Backspace = pygame.K_BACKSPACE
    Delete    = pygame.K_DELETE
    Down      = pygame.K_DOWN
    End       = pygame.K_END
    Escape    = pygame.K_ESCAPE
    Home      = pygame.K_HOME
    Insert    = pygame.K_INSERT
    Left      = pygame.K_LEFT
    PageDown  = pygame.K_PAGEDOWN
    PageUp    = pygame.K_PAGEUP
    Return    = pygame.K_RETURN
    Right     = pygame.K_RIGHT
    Space     = pygame.K_SPACE
    Tab       = pygame.K_TAB
    Up        = pygame.K_UP


    Ampersand        = pygame.K_AMPERSAND
    Asterisk         = pygame.K_ASTERISK
    At               = pygame.K_AT
    Backquote        = pygame.K_BACKQUOTE
    Backslash        = pygame.K_BACKSLASH
    Caret            = pygame.K_CARET
    Colon            = pygame.K_COLON
    Comma            = pygame.K_COMMA
    Dollar           = pygame.K_DOLLAR
    Equals           = pygame.K_EQUALS
    Euro             = pygame.K_EURO
    Exclaim          = pygame.K_EXCLAIM
    GreaterThan      = pygame.K_GREATER
    Hash             = pygame.K_HASH
    LeftBracket      = pygame.K_LEFTBRACKET
    LeftParenthesis  = pygame.K_LEFTPAREN
    LessThan         = pygame.K_LESS
    Minus            = pygame.K_MINUS
    Percent          = pygame.K_PERCENT
    Period           = pygame.K_PERIOD
    Plus             = pygame.K_PLUS
    Question         = pygame.K_QUESTION
    Quote            = pygame.K_QUOTE
    QuotedDouble     = pygame.K_QUOTEDBL
    RightBracket     = pygame.K_RIGHTBRACKET
    RightParenthesis = pygame.K_RIGHTPAREN
    Semicolon        = pygame.K_SEMICOLON
    Slash            = pygame.K_SLASH
    Underscore       = pygame.K_UNDERSCORE


    AppBack         = pygame.K_AC_BACK
    Break           = pygame.K_BREAK
    Clear           = pygame.K_CLEAR
    CurrencySubUnit = pygame.K_CURRENCYSUBUNIT
    CurrencyUnit    = pygame.K_CURRENCYUNIT
    Help            = pygame.K_HELP
    Menu            = pygame.K_MENU
    Pause           = pygame.K_PAUSE
    Power           = pygame.K_POWER
    Print           = pygame.K_PRINTSCREEN
    SysReq          = pygame.K_SYSREQ
    Unknown         = pygame.K_UNKNOWN


class UserInputType:
    def __new__(cls, *args, **kwargs):
        raise TypeError("UserInputType n'est pas instanciable : utiliser UserInputType.MouseButton1, UserInputType.Keyboard, ...")

    # Souris
    MouseButton1  = 0    # bouton gauche
    MouseButton2  = 1    # bouton droit
    MouseButton3  = 2    # bouton du milieu
    MouseWheel    = 3    # molette
    MouseMovement = 4    # mouvement (et entrée / sortie de la fenêtre)

    Touch         = 7    # appui sur un écran tactile
    Accelerometer = 10
    Gyro          = 11

    Keyboard      = 8    # touche du clavier
    TextInput     = 20   # saisie de texte dans une TextBox
    InputMethod   = 21   # composition IME en cours (TEXTEDITING)

    Focus         = 9    # la fenêtre retrouve le focus

    Gamepad1      = 12
    Gamepad2      = 13
    Gamepad3      = 14
    Gamepad4      = 15
    Gamepad5      = 16
    Gamepad6      = 17
    Gamepad7      = 18
    Gamepad8      = 19

    None_         = 22   # type inconnu ; « None » est un mot réservé en Python


class UserInputState:
    def __new__(cls, *args, **kwargs):
        raise TypeError("UserInputState n'est pas instanciable : utiliser UserInputState.Begin, UserInputState.End, ...")

    Begin  = 0
    Change = 1
    End    = 2
    Cancel = 3
    None_  = 4


class InputObject:
    def __init__(self, UserInputType : int, UserInputState : int, Event : pygame.event.Event | None = None):
        self.UserInputType = UserInputType
        self.UserInputState = UserInputState
        self.KeyCode = KeyCode.Unknown
        self.Position = pygame.Vector2(pygame.mouse.get_pos())
        self.Delta = pygame.Vector2(0, 0)
        self.Text = ""
        self.Modifiers = pygame.key.get_mods()
        self.Event = Event

    def IsModifierDown(self, Modifier : int) -> bool:
        return bool(self.Modifiers & Modifier)

    def __repr__(self):
        Type = _NameOf(UserInputType, self.UserInputType)
        State = _NameOf(UserInputState, self.UserInputState)
        Extra = f", KeyCode={_NameOf(KeyCode, self.KeyCode)}" if self.UserInputType == UserInputType.Keyboard else ""
        return f"InputObject({Type}, {State}{Extra}, Position=({self.Position.x:.0f}, {self.Position.y:.0f}))"


def _NameOf(Enum, Value) -> str:
    for Name, Member in vars(Enum).items():
        if not Name.startswith("__") and Member == Value:
            return Name
    return str(Value)


class UserInputService:
    InputBegan = Signal()     # (InputObject, GameProcessed)
    InputChanged = Signal()   # (InputObject, GameProcessed)
    InputEnded = Signal()     # (InputObject, GameProcessed)

    # pygame : 1 = gauche, 2 = milieu, 3 = droit
    _MouseButtons = {
        1: UserInputType.MouseButton1,
        2: UserInputType.MouseButton3,
        3: UserInputType.MouseButton2,
    }

    def __new__(cls, *args, **kwargs):
        raise TypeError("UserInputService n'est pas instanciable : utiliser UserInputService.InputBegan, ...")

    @classmethod
    def GetMouseLocation(cls) -> pygame.Vector2:
        return pygame.Vector2(pygame.mouse.get_pos())

    @classmethod
    def IsKeyDown(cls, Key : int) -> bool:
        return bool(pygame.key.get_pressed()[Key])

    @classmethod
    def IsMouseButtonPressed(cls, InputType : int) -> bool:
        for Button, Type in cls._MouseButtons.items():
            if Type == InputType:
                return bool(pygame.mouse.get_pressed(5)[Button - 1])
        return False

    @classmethod
    def _Convert(cls, Event : pygame.event.Event) -> InputObject | None:
        Type = Event.type

        if Type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            InputType = cls._MouseButtons.get(Event.button)
            if InputType is None:
                return None
            State = UserInputState.Begin if Type == pygame.MOUSEBUTTONDOWN else UserInputState.End
            Input = InputObject(InputType, State, Event)
            Input.Position = pygame.Vector2(Event.pos)
            return Input

        if Type == pygame.MOUSEMOTION:
            Input = InputObject(UserInputType.MouseMovement, UserInputState.Change, Event)
            Input.Position = pygame.Vector2(Event.pos)
            Input.Delta = pygame.Vector2(Event.rel)
            return Input

        if Type == pygame.MOUSEWHEEL:
            Input = InputObject(UserInputType.MouseWheel, UserInputState.Change, Event)
            Input.Delta = pygame.Vector2(Event.x, Event.y)
            return Input

        if Type in (pygame.KEYDOWN, pygame.KEYUP):
            State = UserInputState.Begin if Type == pygame.KEYDOWN else UserInputState.End
            Input = InputObject(UserInputType.Keyboard, State, Event)
            Input.KeyCode = Event.key
            Input.Modifiers = Event.mod
            return Input

        if Type == pygame.TEXTINPUT:
            Input = InputObject(UserInputType.TextInput, UserInputState.Change, Event)
            Input.Text = Event.text
            return Input

        if Type == pygame.TEXTEDITING:
            Input = InputObject(UserInputType.InputMethod, UserInputState.Change, Event)
            Input.Text = Event.text
            return Input

        if Type == pygame.WINDOWFOCUSGAINED:
            return InputObject(UserInputType.Focus, UserInputState.Begin, Event)

        if Type == pygame.WINDOWFOCUSLOST:
            return InputObject(UserInputType.Focus, UserInputState.End, Event)

        return None

    @classmethod
    def _Process(cls, Events : list, Remaining : list):
        """Appelé par Application : Events = tous les événements du tour, Remaining = ceux que la GUI n'a pas consommés"""
        NotProcessed = {id(Event) for Event in Remaining}
        for Event in Events:
            Input = cls._Convert(Event)
            if Input is None:
                continue
            GameProcessed = id(Event) not in NotProcessed
            if Input.UserInputState == UserInputState.Begin:
                cls.InputBegan.Fire(Input, GameProcessed)
            elif Input.UserInputState == UserInputState.Change:
                cls.InputChanged.Fire(Input, GameProcessed)
            else:
                cls.InputEnded.Fire(Input, GameProcessed)
