class UIComponent:
    """
    Objet de configuration (layout, padding, coins, contour...) attaché à un GuiObject.
    Il n'est pas dessiné : il modifie le comportement de son parent.
    USAGE : Frame.AddChild(UIPadding(PaddingLeft=Udim(0, 10)))  ou  Padding.Parent = Frame
    Toute modification d'une propriété publique recalcule le parent automatiquement.
    """
    def __init__(self):
        object.__setattr__(self, "_Parent", None)
        self.Name = type(self).__name__

    def __setattr__(self, Name, Value):
        object.__setattr__(self, Name, Value)
        if not Name.startswith("_") and self._Parent is not None:
            self._Parent._OnComponentChanged(self)

    def _ApplyProperties(self, Properties : dict):
        for Key, Value in Properties.items():
            if not hasattr(self, Key):
                raise AttributeError(f"'{type(self).__name__}' n'a pas de propriété '{Key}'")
            setattr(self, Key, Value)

    @property
    def Parent(self):
        return self._Parent

    @Parent.setter
    def Parent(self, Value):
        if Value is self._Parent:
            return
        if Value is None:
            self._Parent.RemoveChild(self)
        else:
            Value.AddChild(self)

    def Destroy(self):
        if self._Parent is not None:
            self._Parent.RemoveChild(self)

    def _Invalidate(self):
        """Appelé quand le parent est marqué dirty (vider les caches ici)"""
        pass
