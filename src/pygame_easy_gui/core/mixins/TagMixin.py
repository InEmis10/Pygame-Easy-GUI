from pygame_easy_gui.utils.ArgumentVerifier import Verify, ArgumentVerifier
from pygame_easy_gui.services.CollectionService import CollectionService


class TagMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._Tags : dict[str, None] = {}

    @Verify(ArgumentVerifier([str], 1))
    def AddTag(self, Tag : str):
        if Tag in self._Tags:
            return
        self._Tags[Tag] = None
        CollectionService._Add(Tag, self)

    @Verify(ArgumentVerifier([str], 1))
    def RemoveTag(self, Tag : str):
        if Tag not in self._Tags:
            return
        del self._Tags[Tag]
        CollectionService._Remove(Tag, self)

    @Verify(ArgumentVerifier([str], 1))
    def HasTag(self, Tag : str) -> bool:
        return Tag in self._Tags

    def GetTags(self) -> list[str]:
        return list(self._Tags)
