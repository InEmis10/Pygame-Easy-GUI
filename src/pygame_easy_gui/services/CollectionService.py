from pygame_easy_gui.core.Signal import Signal


class _CollectionService:
    """
    Registre global des tags. Permet de retrouver tous les objets ayant un tag donné.
    USAGE :
        Button.AddTag("Menu")
        for Obj in CollectionService.GetTagged("Menu"): ...
        CollectionService.GetInstanceAddedSignal("Menu").Connect(Callback)
    Un objet reste référencé tant qu'il a le tag (Destroy() retire tous ses tags).
    """
    def __init__(self):
        self._Tagged : dict[str, dict] = {}
        self._AddedSignals : dict[str, Signal] = {}
        self._RemovedSignals : dict[str, Signal] = {}

    def _Add(self, Tag : str, Obj):
        self._Tagged.setdefault(Tag, {})[Obj] = None
        if Tag in self._AddedSignals:
            self._AddedSignals[Tag].Fire(Obj)

    def _Remove(self, Tag : str, Obj):
        Objects = self._Tagged.get(Tag)
        if not Objects or Obj not in Objects:
            return
        del Objects[Obj]
        if not Objects:
            del self._Tagged[Tag]
        if Tag in self._RemovedSignals:
            self._RemovedSignals[Tag].Fire(Obj)

    def AddTag(self, Obj, Tag : str):
        Obj.AddTag(Tag)

    def RemoveTag(self, Obj, Tag : str):
        Obj.RemoveTag(Tag)

    def HasTag(self, Obj, Tag : str) -> bool:
        return Obj.HasTag(Tag)

    def GetTags(self, Obj) -> list[str]:
        return Obj.GetTags()

    def GetTagged(self, Tag : str) -> list:
        return list(self._Tagged.get(Tag, ()))

    def GetAllTags(self) -> list[str]:
        return list(self._Tagged)

    def GetInstanceAddedSignal(self, Tag : str) -> Signal:
        if Tag not in self._AddedSignals:
            self._AddedSignals[Tag] = Signal()
        return self._AddedSignals[Tag]

    def GetInstanceRemovedSignal(self, Tag : str) -> Signal:
        if Tag not in self._RemovedSignals:
            self._RemovedSignals[Tag] = Signal()
        return self._RemovedSignals[Tag]


CollectionService = _CollectionService()
