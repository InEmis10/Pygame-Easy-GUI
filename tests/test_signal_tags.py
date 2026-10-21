from pygame_easy_gui import Signal, Frame, TextButton, CollectionService, Connect


def test_SignalContinuesAfterError(capsys):
    Event = Signal()
    Received = []

    def Broken():
        raise RuntimeError("boom")

    Event.Connect(Broken)
    Event.Connect(lambda: Received.append(1))
    Event.Fire()
    assert Received == [1]
    assert "boom" in capsys.readouterr().err


def test_SignalOnceAndDisconnect():
    Event = Signal()
    Received = []
    Event.Once(Received.append)
    Conn = Event.Connect(Received.append)
    Event.Fire(1)
    Conn.Disconnect()
    Event.Fire(2)
    assert Received == [1, 1]


def test_ConnectDecorator():
    Button = TextButton()
    Received = []

    @Connect(Button.MouseButton1Click)
    def OnClick():
        Received.append("click")

    Button.MouseButton1Click.Fire()
    assert Received == ["click"]


def test_Tags():
    A, B = Frame(), Frame()
    Added, Removed = [], []
    CollectionService.GetInstanceAddedSignal("Enemy").Connect(Added.append)
    CollectionService.GetInstanceRemovedSignal("Enemy").Connect(Removed.append)

    A.AddTag("Enemy")
    A.AddTag("Enemy")
    B.AddTag("Enemy")
    assert CollectionService.GetTagged("Enemy") == [A, B]
    assert A.HasTag("Enemy") and A.GetTags() == ["Enemy"]
    assert Added == [A, B]

    A.RemoveTag("Enemy")
    B.Destroy()
    assert CollectionService.GetTagged("Enemy") == []
    assert Removed == [A, B]
    assert "Enemy" not in CollectionService.GetAllTags()
