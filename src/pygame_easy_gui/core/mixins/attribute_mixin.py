from pygame_easy_gui.utils.argument_verifier import Verify, ArgumentVerifier, ANY
from pygame_easy_gui.core.Signal import Signal


class AttributeMixin:
    """Attributs personnalisés, comme Instance:SetAttribute dans Roblox.

        Obj.SetAttribute("Health", 100)
        Obj.GetAttribute("Health")           # 100
        Obj.SetAttribute("Health", None)     # supprime l'attribut (comme nil dans Roblox)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._Attributes : dict[str, object] = {}
        self._AttributeSignals : dict[str, Signal] = {}
        self.AttributeChanged = Signal()     # Fire(Name) à chaque modification d'un attribut

    @Verify(ArgumentVerifier([str, ANY], 2))
    def SetAttribute(self, Name : str, Value):
        if Value is None:
            if Name not in self._Attributes:
                return
            del self._Attributes[Name]
        else:
            if Name in self._Attributes and self._Attributes[Name] == Value:
                return  # valeur identique : pas de signal
            self._Attributes[Name] = Value
        self._FireAttributeChanged(Name)

    @Verify(ArgumentVerifier([str], 1))
    def GetAttribute(self, Name : str):
        return self._Attributes.get(Name, None)

    def GetAttributes(self) -> dict[str, object]:
        return dict(self._Attributes)

    @Verify(ArgumentVerifier([str], 1))
    def HasAttribute(self, Name : str):
        return Name in self._Attributes

    @Verify(ArgumentVerifier([str], 1))
    def DelAttribute(self, Name : str):
        self.SetAttribute(Name, None)

    @Verify(ArgumentVerifier([str], 1))
    def GetAttributeChangedSignal(self, Name : str) -> Signal:
        """Signal émis uniquement quand l'attribut Name change (sans argument)."""
        if Name not in self._AttributeSignals:
            self._AttributeSignals[Name] = Signal()
        return self._AttributeSignals[Name]

    def _FireAttributeChanged(self, Name : str):
        self.AttributeChanged.Fire(Name)
        if Name in self._AttributeSignals:
            self._AttributeSignals[Name].Fire()
