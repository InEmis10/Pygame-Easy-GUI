import time
from pygame_easy_gui.core.Signal import Signal
from pygame_easy_gui.datatypes.udim import Udim, Udim2
from pygame_easy_gui.datatypes.vector2 import Vector2
from pygame_easy_gui.datatypes.color3 import Color3
from pygame_easy_gui.services import Easing


class TweenInfo:
    """
    Paramètres d'une animation (immuable).
    Time : durée en secondes | EasingStyle : "linear", "sine", "quad", "cubic", "quart", "quint", "exponential", "circular", "back", "elastic", "bounce"
    EasingDirection : "in" | "out" | "inout" | RepeatCount : répétitions en plus de la première (-1 = infini)
    Reverses : revient à la valeur de départ à chaque répétition | DelayTime : attente avant de commencer (secondes)
    """
    __slots__ = ("Time", "EasingStyle", "EasingDirection", "RepeatCount", "Reverses", "DelayTime")

    def __init__(self, Time : float = 1.0, EasingStyle : str = "quad", EasingDirection : str = "out",
                 RepeatCount : int = 0, Reverses : bool = False, DelayTime : float = 0.0):
        if EasingStyle.lower() not in Easing.STYLES:
            raise ValueError(f"EasingStyle inconnu : {EasingStyle!r} (possibles : {', '.join(Easing.STYLES)})")
        if EasingDirection.lower() not in Easing.DIRECTIONS:
            raise ValueError(f"EasingDirection inconnue : {EasingDirection!r} (possibles : {', '.join(Easing.DIRECTIONS)})")
        if Time < 0 or DelayTime < 0:
            raise ValueError("Time et DelayTime doivent être positifs")
        for Name, Value in (("Time", float(Time)), ("EasingStyle", EasingStyle.lower()), ("EasingDirection", EasingDirection.lower()),
                            ("RepeatCount", int(RepeatCount)), ("Reverses", bool(Reverses)), ("DelayTime", float(DelayTime))):
            object.__setattr__(self, Name, Value)

    def __setattr__(self, Name, Value):
        raise AttributeError("TweenInfo est immuable, crée un nouveau TweenInfo à la place")

    def __repr__(self):
        return f"TweenInfo({self.Time}, {self.EasingStyle!r}, {self.EasingDirection!r}, {self.RepeatCount}, {self.Reverses}, {self.DelayTime})"


def _IsNumber(Value) -> bool:
    return isinstance(Value, (int, float)) and not isinstance(Value, bool)


def _CheckCompatible(Name : str, Start, Goal):
    if _IsNumber(Start) and _IsNumber(Goal):
        return
    for Type in (Udim2, Udim, Vector2):
        if isinstance(Start, Type) and isinstance(Goal, Type):
            return
    if isinstance(Start, tuple) and isinstance(Goal, tuple) and len(Start) >= 3 and len(Goal) >= 3:
        return
    if isinstance(Start, bool) and isinstance(Goal, bool):
        return
    raise TypeError(f"Impossible d'animer '{Name}' : {type(Start).__name__} vers {type(Goal).__name__}")


def Lerp(Start, Goal, Alpha : float):
    """Interpolation entre deux valeurs de même type (nombre, Udim, Udim2, Vector2, couleur, bool)"""
    if isinstance(Start, bool):
        return Goal if Alpha >= 1 else Start
    if _IsNumber(Start):
        # Toujours décimal : une transparence de 0 à 1 (deux int) doit passer par 0.5
        return Start + (Goal - Start) * Alpha
    if isinstance(Start, Udim2):
        return Udim2(Start.X.lerp(Goal.X, Alpha), Start.Y.lerp(Goal.Y, Alpha))
    if isinstance(Start, Udim):
        return Start.lerp(Goal, Alpha)
    if isinstance(Start, Vector2):
        return Vector2(Start.X + (Goal.X - Start.X) * Alpha, Start.Y + (Goal.Y - Start.Y) * Alpha)
    # Couleur : bornée (les easings "back" / "elastic" dépassent)
    Channels = tuple(min(255, max(0, round(A + (B - A) * Alpha))) for A, B in zip(Start[:3], Goal[:3]))
    return Color3(*Channels) if isinstance(Start, Color3) or isinstance(Goal, Color3) else Channels


class Tween:
    """
    Animation de propriétés d'un objet, créée par TweenService.Create.
    PlaybackState : "Begin" | "Delayed" | "Playing" | "Paused" | "Completed" | "Cancelled"
    Completed(PlaybackState) : se déclenche à la fin, ou quand le tween est annulé.
    """
    def __init__(self, Instance, Info : TweenInfo, Goals : dict):
        self.Instance = Instance
        self.TweenInfo = Info
        self.Completed = Signal()
        self.PlaybackState = "Begin"
        self._Goals = dict(Goals)
        self._Start : dict | None = None
        self._Elapsed = 0.0
        self._LastTime = 0.0

    def Play(self):
        if self.PlaybackState in ("Playing", "Delayed"):
            return
        if self.PlaybackState != "Paused":
            self._Elapsed = 0.0
            self._Start = None
        TweenService._Add(self)
        self._LastTime = TweenService.Clock()
        self.PlaybackState = "Delayed" if self._Elapsed < self.TweenInfo.DelayTime else "Playing"
        if self._Start is None and self.PlaybackState == "Playing":
            self._Begin()

    def Pause(self):
        if self.PlaybackState in ("Playing", "Delayed"):
            TweenService._Remove(self)
            self.PlaybackState = "Paused"

    def Cancel(self):
        """Arrête le tween (les propriétés gardent leur valeur actuelle). Play() le relance depuis le début."""
        if self.PlaybackState in ("Completed", "Cancelled", "Begin"):
            return
        TweenService._Remove(self)
        self.PlaybackState = "Cancelled"
        self._Elapsed = 0.0
        self._Start = None
        self.Completed.Fire(self.PlaybackState)

    def _Begin(self):
        """Valeurs de départ lues au moment où l'animation commence vraiment (après DelayTime)"""
        self._Start = {Name: getattr(self.Instance, Name) for Name in self._Goals}

    def _GetAlpha(self, Time : float) -> tuple[float, bool]:
        """(progression 0 - 1 avant easing, terminé)"""
        Info = self.TweenInfo
        Cycle = Info.Time * (2 if Info.Reverses else 1)
        if Cycle <= 0:
            return (0.0 if Info.Reverses else 1.0), True
        if Info.RepeatCount >= 0 and Time >= Cycle * (Info.RepeatCount + 1):
            return (0.0 if Info.Reverses else 1.0), True
        Local = Time % Cycle
        if Local <= Info.Time:
            return Local / Info.Time, False
        return (Cycle - Local) / Info.Time, False

    def _Step(self) -> bool:
        """Avance selon l'horloge ; retourne False quand le tween est fini"""
        if getattr(self.Instance, "_Destroyed", False):
            self.Cancel()
            return False
        Now = TweenService.Clock()
        self._Elapsed += Now - self._LastTime
        self._LastTime = Now

        Info = self.TweenInfo
        if self._Elapsed < Info.DelayTime:
            return True
        if self._Start is None:
            self._Begin()
        self.PlaybackState = "Playing"

        Alpha, Done = self._GetAlpha(self._Elapsed - Info.DelayTime)
        Eased = Easing.Ease(Alpha, Info.EasingStyle, Info.EasingDirection)
        for Name, Goal in self._Goals.items():
            setattr(self.Instance, Name, Goal if Done and Alpha == 1.0 else Lerp(self._Start[Name], Goal, Eased))
        if Done:
            self.PlaybackState = "Completed"
            self.Completed.Fire(self.PlaybackState)
            return False
        return True


class TweenService:
    """
    Anime les propriétés de n'importe quel objet (GuiObject, UIComponent...).
    USAGE :
        Info = TweenInfo(0.5, "quad", "out")
        Tween = TweenService.Create(Frame, Info, {"Position": Udim2(0.5, 0, 0.5, 0), "BackgroundTransparency": 0.5})
        Tween.Completed.Connect(lambda State: print(State))
        Tween.Play()
    Les tweens avancent à chaque ScreenGui.Update() (en temps réel). Sans ScreenGui, appeler TweenService.Step() à chaque frame.
    Un nouveau tween sur une propriété déjà animée annule l'ancien.
    """
    Clock = staticmethod(time.perf_counter)   # remplaçable (tests, ralenti...)
    _Active : list[Tween] = []

    @staticmethod
    def Create(Instance, Info : TweenInfo, Goals : dict) -> Tween:
        if not isinstance(Info, TweenInfo):
            raise TypeError(f"TweenService.Create attend un TweenInfo, reçu {type(Info).__name__}")
        if not Goals:
            raise ValueError("Aucune propriété à animer")
        for Name, Goal in Goals.items():
            if Name.startswith("_") or not hasattr(Instance, Name):
                raise AttributeError(f"'{type(Instance).__name__}' n'a pas de propriété '{Name}'")
            _CheckCompatible(Name, getattr(Instance, Name), Goal)
        return Tween(Instance, Info, Goals)

    @classmethod
    def Step(cls):
        """Fait avancer tous les tweens en cours (appelé par ScreenGui.Update)"""
        for Current in list(cls._Active):
            if Current in cls._Active and not Current._Step():
                cls._Remove(Current)

    @classmethod
    def GetPlayingTweens(cls, Instance = None) -> list[Tween]:
        return [Current for Current in cls._Active if Instance is None or Current.Instance is Instance]

    @classmethod
    def _Add(cls, NewTween : Tween):
        # Le nouveau tween prend le contrôle des propriétés déjà animées
        for Current in list(cls._Active):
            if Current.Instance is NewTween.Instance and Current._Goals.keys() & NewTween._Goals.keys():
                Current.Cancel()
        cls._Active.append(NewTween)

    @classmethod
    def _Remove(cls, OldTween : Tween):
        if OldTween in cls._Active:
            cls._Active.remove(OldTween)
