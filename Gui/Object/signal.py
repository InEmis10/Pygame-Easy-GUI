class Connection:
    def __init__(self, signal: "Signal", callback):
        self._signal = signal
        self._callback = callback
        self.Connected = True

    def Disconnect(self):
        if self.Connected:
            self.Connected = False
            if self in self._signal._connections:
                self._signal._connections.remove(self)


class Signal:
    def __init__(self):
        self._connections: list[Connection] = []

    def Connect(self, callback) -> Connection:
        conn = Connection(self, callback)
        self._connections.append(conn)
        return conn

    def Once(self, callback) -> Connection:
        holder = {}

        def wrapper(*args, **kwargs):
            holder["conn"].Disconnect()
            callback(*args, **kwargs)

        conn = self.Connect(wrapper)
        holder["conn"] = conn
        return conn

    def Fire(self, *args, **kwargs):
        for conn in list(self._connections):
            if conn.Connected:
                conn._callback(*args, **kwargs)

    def DisconnectAll(self):
        for conn in list(self._connections):
            conn.Disconnect()