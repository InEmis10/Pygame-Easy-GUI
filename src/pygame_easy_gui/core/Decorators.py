from pygame_easy_gui.core.Signal import Signal


def Connect(Target : Signal):
    """Connecte la fonction décorée à un signal et la renvoie intacte (elle reste appelable).

        @Connect(Button.MouseButton1Click)
        def OnButtonClick():
            print("Button Clicked")
    """
    if not isinstance(Target, Signal):
        raise TypeError(f"@Connect attend un Signal, reçu {type(Target).__name__}")

    def Decorator(Func):
        if not callable(Func):
            raise TypeError(f"@Connect ne peut connecter qu'une fonction, reçu {type(Func).__name__}")
        Target.Connect(Func)
        return Func
    return Decorator


def OnEvent(*Events):
    """Dans une classe qui hérite d'EventHandlerMixin (ex: Application) : la méthode est appelée pour ces événements pygame.

        @OnEvent(pygame.QUIT)
        def _OnQuit(self, Event): ...
    """
    for EventType in Events:
        if not isinstance(EventType, int):
            raise TypeError(f"@OnEvent attend des types d'événements pygame (int), reçu {EventType!r}")

    def Decorator(Func):
        Func._PygameEvents = getattr(Func, "_PygameEvents", ()) + Events
        return Func
    return Decorator
