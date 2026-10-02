from ...utils.argument_verifier import Verify, ArgumentVerifier, ANY
from ..signal import Signal


class AttributeMixin:
    """Attributs personnalisés, comme Instance:SetAttribute dans Roblox.

        obj.SetAttribute("Health", 100)
        obj.GetAttribute("Health")           # 100
        obj.SetAttribute("Health", None)     # supprime l'attribut (comme nil dans Roblox)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attributes : dict[str, object] = {}
        self._attributeSignals : dict[str, Signal] = {}
        self.AttributeChanged = Signal()     # Fire(name) à chaque modification d'un attribut

    @Verify(ArgumentVerifier([str, ANY], 2))
    def SetAttribute(self, name : str, value):
        if value is None:
            if name not in self._attributes:
                return
            del self._attributes[name]
        else:
            if name in self._attributes and self._attributes[name] == value:
                return  # valeur identique : pas de signal
            self._attributes[name] = value
        self._FireAttributeChanged(name)

    @Verify(ArgumentVerifier([str], 1))
    def GetAttribute(self, name : str):
        return self._attributes.get(name, None)

    def GetAttributes(self) -> dict[str, object]:
        return dict(self._attributes)

    @Verify(ArgumentVerifier([str], 1))
    def HasAttribute(self, name : str):
        return name in self._attributes

    @Verify(ArgumentVerifier([str], 1))
    def DelAttribute(self, name : str):
        self.SetAttribute(name, None)

    @Verify(ArgumentVerifier([str], 1))
    def GetAttributeChangedSignal(self, name : str) -> Signal:
        """Signal émis uniquement quand l'attribut `name` change (sans argument)."""
        if name not in self._attributeSignals:
            self._attributeSignals[name] = Signal()
        return self._attributeSignals[name]

    def _FireAttributeChanged(self, name : str):
        self.AttributeChanged.Fire(name)
        if name in self._attributeSignals:
            self._attributeSignals[name].Fire()
