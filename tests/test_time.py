import pytest
from pygame_easy_gui import Application, ScreenGui, TimeService, Timer


@pytest.fixture
def FakeClock(monkeypatch):
    Now = [0.0]
    monkeypatch.setattr(TimeService, "Clock", staticmethod(lambda: Now[0]))
    monkeypatch.setattr(TimeService, "_Heap", [])

    def Advance(Seconds, Step=True):
        Now[0] += Seconds
        if Step:
            TimeService.Step()
    return Advance


def test_DelayCallsOnceWithArgs(FakeClock):
    Calls = []
    Current = TimeService.Delay(1, Calls.append, "a")
    assert isinstance(Current, Timer) and Current.Active
    FakeClock(0.5)
    assert Calls == []
    FakeClock(0.5)
    assert Calls == ["a"]
    FakeClock(5)
    assert Calls == ["a"]
    assert not Current.Active
    assert TimeService.GetNextDeadline() is None


def test_EveryRepeatsUntilCancel(FakeClock):
    Calls = []
    Current = TimeService.Every(1, lambda: Calls.append(1))
    for _ in range(3):
        FakeClock(1)
    assert len(Calls) == 3
    Current.Cancel()
    FakeClock(1)
    assert len(Calls) == 3
    assert not Current.Active
    assert TimeService.GetActiveTimers() == []


def test_EveryDoesNotBurstWhenLate(FakeClock):
    Calls = []
    TimeService.Every(1, lambda: Calls.append(1))
    FakeClock(10)          # boucle bloquée 10 s : un seul appel, pas dix
    assert len(Calls) == 1
    FakeClock(0.5)
    assert len(Calls) == 1
    FakeClock(0.5)
    assert len(Calls) == 2


def test_OrderAndCancelFromCallback(FakeClock):
    Calls = []
    Second = TimeService.Delay(1, Calls.append, "second")
    TimeService.Delay(0.5, Calls.append, "first")
    TimeService.Delay(0.5, Second.Cancel)   # même Step que Second : il ne doit pas être appelé
    FakeClock(1)
    assert Calls == ["first"]


def test_EveryCanCancelItself(FakeClock):
    Calls = []
    Holder = {}

    def Tick():
        Calls.append(1)
        if len(Calls) == 2:
            Holder["Timer"].Cancel()
    Holder["Timer"] = TimeService.Every(1, Tick)
    for _ in range(5):
        FakeClock(1)
    assert len(Calls) == 2


def test_DelayZeroFromCallbackWaitsNextStep(FakeClock):
    Calls = []

    def Again():
        Calls.append(1)
        TimeService.Delay(0, Again)
    TimeService.Delay(0, Again)
    FakeClock(0)
    assert len(Calls) == 1   # pas de boucle infinie dans un même Step
    FakeClock(0)
    assert len(Calls) == 2


def test_ErrorInCallbackDoesNotStopOthers(FakeClock, capsys):
    Calls = []
    TimeService.Delay(1, lambda: 1 / 0)
    TimeService.Delay(1, Calls.append, "ok")
    FakeClock(1)
    assert Calls == ["ok"]
    assert "ZeroDivisionError" in capsys.readouterr().err


def test_InvalidArguments(FakeClock):
    with pytest.raises(TypeError):
        TimeService.Delay(1, "pas une fonction")
    with pytest.raises(TypeError):
        TimeService.Delay("1", print)
    with pytest.raises(ValueError):
        TimeService.Delay(-1, print)
    with pytest.raises(ValueError):
        TimeService.Every(0, print)


def test_ScreenGuiUpdateStepsTimers(FakeClock):
    Calls = []
    TimeService.Delay(1, Calls.append, 1)
    FakeClock(1, Step=False)
    assert Calls == []
    ScreenGui().Update(0)
    assert Calls == [1]


def test_WaitTimeStopsAtNextTimer(FakeClock):
    App = Application("Test", EventTimeOut=1.0)
    assert App._GetWaitTime() == 1.0
    TimeService.Delay(0.25, print)
    assert App._GetWaitTime() == 0.25
