import heapq
import time
import traceback


def _CheckSeconds(Seconds, AllowZero : bool) -> float:
    if not isinstance(Seconds, (int, float)) or isinstance(Seconds, bool):
        raise TypeError(f"Seconds doit être un nombre, reçu {type(Seconds).__name__}")
    if Seconds < 0 or (Seconds == 0 and not AllowZero):
        raise ValueError(f"Seconds doit être {'positif' if AllowZero else 'strictement positif'}, reçu {Seconds}")
    return float(Seconds)


class Timer:
    """
    Minuteur créé par TimeService.Delay ou TimeService.Every.
    Interval : 0 pour un Delay (une seule fois), sinon la période d'un Every.
    Cancel() l'arrête ; Active vaut False une fois annulé ou terminé.
    """
    __slots__ = ("Deadline", "Interval", "Callback", "Args", "Cancelled", "_Done")

    def __init__(self, Deadline : float, Interval : float, Callback, Args : tuple):
        self.Deadline = Deadline
        self.Interval = Interval
        self.Callback = Callback
        self.Args = Args
        self.Cancelled = False
        self._Done = False

    @property
    def Active(self) -> bool:
        return not self.Cancelled and not self._Done

    def Cancel(self):
        self.Cancelled = True

    def __repr__(self):
        Kind = f"Every({self.Interval})" if self.Interval else "Delay"
        return f"<Timer {Kind} {getattr(self.Callback, '__name__', self.Callback)!r} Active={self.Active}>"


class TimeService:
    """
    Appelle des fonctions plus tard, sans bloquer la boucle.
    USAGE :
        TimeService.Delay(2, print, "2 secondes plus tard")
        Blink = TimeService.Every(0.5, Toggle)   # toutes les 0.5 s
        Blink.Cancel()
    Les timers avancent à chaque ScreenGui.Update() (en temps réel), tout seuls avec Application.
    Sans ScreenGui, appeler TimeService.Step() à chaque frame.
    Un Every en retard de plusieurs périodes (fenêtre bloquée...) n'est appelé qu'une fois, sans rafale.
    """
    Clock = staticmethod(time.perf_counter)   # remplaçable (tests, ralenti...)
    _Heap : list[tuple[float, int, Timer]] = []
    _Counter = 0                              # départage deux timers à la même échéance (ordre de création)

    @classmethod
    def Delay(cls, Seconds : float, Callback, *Args) -> Timer:
        """Appelle Callback(*Args) une fois, dans Seconds secondes (0 = au prochain Step)"""
        return cls._Add(_CheckSeconds(Seconds, AllowZero=True), 0.0, Callback, Args)

    @classmethod
    def Every(cls, Seconds : float, Callback, *Args) -> Timer:
        """Appelle Callback(*Args) toutes les Seconds secondes, jusqu'à Timer.Cancel()"""
        Seconds = _CheckSeconds(Seconds, AllowZero=False)
        return cls._Add(Seconds, Seconds, Callback, Args)

    @classmethod
    def Step(cls):
        """Appelle les timers arrivés à échéance (appelé par ScreenGui.Update)"""
        Now = cls.Clock()
        # Échéances relevées d'abord : un Delay(0) créé par un callback attend le Step suivant
        Due = []
        while cls._Heap and cls._Heap[0][0] <= Now:
            Current = heapq.heappop(cls._Heap)[2]
            if not Current.Cancelled:
                Due.append(Current)

        for Current in Due:
            if Current.Cancelled:   # annulé par un callback précédent du même Step
                continue
            if Current.Interval > 0:
                Current.Deadline += Current.Interval
                if Current.Deadline <= Now:
                    Current.Deadline = Now + Current.Interval
                cls._Push(Current)
            else:
                Current._Done = True
            # Une erreur dans un callback est affichée mais n'empêche pas les autres timers
            try:
                Current.Callback(*Current.Args)
            except Exception:
                traceback.print_exc()

    @classmethod
    def GetNextDeadline(cls) -> float | None:
        """Échéance (en temps de Clock) du prochain timer actif, None s'il n'y en a pas"""
        while cls._Heap and cls._Heap[0][2].Cancelled:
            heapq.heappop(cls._Heap)
        return cls._Heap[0][0] if cls._Heap else None

    @classmethod
    def GetActiveTimers(cls) -> list[Timer]:
        return [Entry[2] for Entry in sorted(cls._Heap) if not Entry[2].Cancelled]

    @classmethod
    def _Add(cls, Seconds : float, Interval : float, Callback, Args : tuple) -> Timer:
        if not callable(Callback):
            raise TypeError(f"Callback doit être une fonction, reçu {type(Callback).__name__}")
        NewTimer = Timer(cls.Clock() + Seconds, Interval, Callback, Args)
        cls._Push(NewTimer)
        return NewTimer

    @classmethod
    def _Push(cls, Current : Timer):
        heapq.heappush(cls._Heap, (Current.Deadline, cls._Counter, Current))
        cls._Counter += 1
