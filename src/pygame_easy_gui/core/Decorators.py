from .Signal import Signal

def Connect(target : Signal):
    """Connecte la fonction décorée à un signal et la renvoie intacte (elle reste appelable).

        @Connect(button.MouseButton1Click)
        def OnButtonClick():
            print("Button Clicked")
    """
    if not isinstance(target, Signal):
        raise TypeError(f"@Connect attend un Signal, reçu {type(target).__name__}")

    def decorator(func):
        if not callable(func):
            raise TypeError(f"@Connect ne peut connecter qu'une fonction, reçu {type(func).__name__}")
        target.Connect(func)
        return func
    return decorator


##Create an handler for pygame event
def OnEvent(*events):
    for t in events:
        if not isinstance(t, int):
            raise TypeError(f"@OnEvent attend des types d'événements pygame (int), reçu {t!r}")

    def decorator(func):
        func._pygame_events = getattr(func, "_pygame_events", ()) + events
        return func
    return decorator
