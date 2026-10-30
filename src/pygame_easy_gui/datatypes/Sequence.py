from __future__ import annotations

class _Keypoint:
    """Point d'une séquence : Time entre 0 et 1, Value = couleur ou nombre"""
    __slots__ = ("Time", "Value")

    def __init__(self, Time : float, Value):
        if not 0 <= Time <= 1:
            raise ValueError(f"Time doit être entre 0 et 1, reçu {Time}")
        object.__setattr__(self, "Time", float(Time))
        object.__setattr__(self, "Value", self._Convert(Value))

    @staticmethod
    def _Convert(Value):
        return Value

    def __setattr__(self, Name, Value):
        raise AttributeError(f"{type(self).__name__} est immuable")

    def __eq__(self, Other):
        if type(Other) is not type(self):
            return NotImplemented
        return (self.Time, self.Value) == (Other.Time, Other.Value)

    def __hash__(self):
        return hash((self.Time, self.Value))

    def __repr__(self):
        return f"{type(self).__name__}({self.Time}, {self.Value})"


class ColorSequenceKeypoint(_Keypoint):
    __slots__ = ()

    @staticmethod
    def _Convert(Value):
        R, G, B = Value[:3]
        return (int(R), int(G), int(B))


class NumberSequenceKeypoint(_Keypoint):
    __slots__ = ()

    @staticmethod
    def _Convert(Value):
        return float(Value)


class _Sequence:
    """
    Valeur qui varie de Time = 0 à Time = 1 (immuable).
    USAGE : Sequence(Valeur) | Sequence(Debut, Fin) | Sequence([Keypoint(0, ...), Keypoint(0.5, ...), Keypoint(1, ...)])
    """
    __slots__ = ("Keypoints",)
    _KeypointType = _Keypoint

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)) and args[0] and isinstance(args[0][0], self._KeypointType):
            Keypoints = sorted(args[0], key=lambda Keypoint: Keypoint.Time)
        elif len(args) == 1:
            Keypoints = [self._KeypointType(0, args[0]), self._KeypointType(1, args[0])]
        elif len(args) == 2:
            Keypoints = [self._KeypointType(0, args[0]), self._KeypointType(1, args[1])]
        else:
            raise TypeError(f"{type(self).__name__} attend une valeur, deux valeurs ou une liste de keypoints")
        object.__setattr__(self, "Keypoints", tuple(Keypoints))

    def __setattr__(self, Name, Value):
        raise AttributeError(f"{type(self).__name__} est immuable, crée une nouvelle séquence à la place")

    def _Lerp(self, A, B, Alpha : float):
        return A + (B - A) * Alpha

    def Evaluate(self, Time : float):
        """Valeur au temps Time (interpolée entre les deux keypoints voisins)"""
        Keypoints = self.Keypoints
        if Time <= Keypoints[0].Time:
            return Keypoints[0].Value
        for Previous, Next in zip(Keypoints, Keypoints[1:]):
            if Time <= Next.Time:
                Span = Next.Time - Previous.Time
                Alpha = (Time - Previous.Time) / Span if Span > 0 else 1.0
                return self._Lerp(Previous.Value, Next.Value, Alpha)
        return Keypoints[-1].Value

    def __eq__(self, Other):
        if type(Other) is not type(self):
            return NotImplemented
        return self.Keypoints == Other.Keypoints

    def __hash__(self):
        return hash(self.Keypoints)

    def __repr__(self):
        return f"{type(self).__name__}({list(self.Keypoints)})"


class ColorSequence(_Sequence):
    """Dégradé de couleurs. ColorSequence((255, 0, 0), (0, 0, 255)) = du rouge au bleu."""
    __slots__ = ()
    _KeypointType = ColorSequenceKeypoint

    def _Lerp(self, A, B, Alpha : float):
        return tuple(Start + (End - Start) * Alpha for Start, End in zip(A, B))


class NumberSequence(_Sequence):
    """Suite de nombres (ex: transparence d'un UIGradient). NumberSequence(0, 1) = de opaque à invisible."""
    __slots__ = ()
    _KeypointType = NumberSequenceKeypoint
