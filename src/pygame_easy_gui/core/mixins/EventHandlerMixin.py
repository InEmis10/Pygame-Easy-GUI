import traceback


class EventHandlerMixin:
    """Appelle les méthodes décorées avec @OnEvent quand l'événement pygame correspondant arrive (voir _HandleEvent)"""
    _EventTable : dict[int, str] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Table = {}
        for Klass in reversed(cls.__mro__):
            for Name, Attribute in vars(Klass).items():
                for EventType in getattr(Attribute, "_PygameEvents", ()):
                    Table[EventType] = Name
        cls._EventTable = Table

    def _HandleEvent(self, Event) -> bool:
        Name = self._EventTable.get(Event.type)
        if Name is None:
            return False
        try:
            getattr(self, Name)(Event)
        except Exception:
            traceback.print_exc()
        return True
