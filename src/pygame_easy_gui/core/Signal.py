import traceback


class Connection:
    def __init__(self, Signal: "Signal", Callback):
        self._Signal = Signal
        self._Callback = Callback
        self.Connected = True

    def Disconnect(self):
        if self.Connected:
            self.Connected = False
            if self in self._Signal._Connections:
                self._Signal._Connections.remove(self)

    def __call__(self, *args, **kwargs):
        # Après `@Signal.Connect` (ou `@Signal`), le nom de la fonction désigne la Connection :
        # elle reste appelable comme la fonction d'origine.
        return self._Callback(*args, **kwargs)


class Signal:
    def __init__(self):
        self._Connections: list[Connection] = []

    def Connect(self, Callback) -> Connection:
        Conn = Connection(self, Callback)
        self._Connections.append(Conn)
        return Conn

    def Once(self, Callback) -> Connection:
        Holder = {}

        def Wrapper(*args, **kwargs):
            Holder["Conn"].Disconnect()
            Callback(*args, **kwargs)

        Conn = self.Connect(Wrapper)
        Holder["Conn"] = Conn
        return Conn

    def Fire(self, *args, **kwargs):
        # Une erreur dans un callback est affichée mais n'empêche pas les suivants de s'exécuter
        for Conn in list(self._Connections):
            if Conn.Connected:
                try:
                    Conn._Callback(*args, **kwargs)
                except Exception:
                    traceback.print_exc()

    def DisconnectAll(self):
        for Conn in list(self._Connections):
            Conn.Disconnect()

    def __call__(self, Callback):
        return self.Connect(Callback)
