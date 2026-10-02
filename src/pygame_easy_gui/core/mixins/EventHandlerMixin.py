import traceback

class EventHandlerMixin:
    _EventTable : dict[int, str] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        table = {}
        for klass in reversed(cls.__mro__):
            for name, attr, in vars(klass).items():
                for t in getattr(attr, "_pygame_events", ()):
                    table[t] = name
        cls._EventTable = table

    def _HandleEvent(self, event) -> bool:
        name = self._EventTable.get(event.type)
        if name is None:
            return False
        try:
            getattr(self, name)(event)
        except Exception:
            traceback.print_exc()
        return True
