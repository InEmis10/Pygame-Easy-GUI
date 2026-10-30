import pytest
from pygame_easy_gui import Udim, Udim2, Vector2, Color3, IntValue


def test_UdimDefaultsAndKwargs():
    assert Udim().Scale == 0.0 and Udim(1).Offset == 0.0 and Udim(Offset=5).Offset == 5
    with pytest.raises(TypeError):
        Udim("a")
    with pytest.raises(TypeError):
        Udim(Bad=1)


def test_EqualityWithOtherTypes():
    assert Udim2(0, 1, 0, 2) != None
    assert Udim(1, 2) != 3
    assert Vector2(1, 2) != "x"
    assert Vector2(1, 2) == Vector2(1, 2)


def test_Immutable():
    with pytest.raises(AttributeError):
        Udim2(0, 0, 0, 0).X.Offset = 3
    with pytest.raises(AttributeError):
        Udim2(0, 0, 0, 0).X = Udim()
    with pytest.raises(AttributeError):
        Vector2(0, 0).X = 1


def test_Udim2Arithmetic():
    assert Udim2.fromOffset(10, 20) == Udim2(0, 10, 0, 20)
    assert Udim2.fromScale(0.5, 1) == Udim2(0.5, 0, 1, 0)
    assert Udim2(0, 1, 0, 2) + Udim2(0, 1, 0, 2) == Udim2(0, 2, 0, 4)
    assert -Udim2(1, 1, 1, 1) == Udim2(-1, -1, -1, -1)
    assert 2 * Udim2(1, 1, 1, 1) == Udim2(2, 2, 2, 2)
    assert Udim2(0, 0, 0, 0).Lerp(Udim2(1, 10, 1, 10), 0.5) == Udim2(0.5, 5, 0.5, 5)
    assert len({Udim2(0, 1, 0, 1), Udim2(0, 1, 0, 1)}) == 1


def test_Color3():
    assert Color3(255, 136, 0) == (255, 136, 0)
    assert Color3.fromHex("#ff8800") == Color3(255, 136, 0)
    assert Color3.fromHex("f80") == Color3(255, 136, 0)
    assert Color3(255, 136, 0).ToHex() == "#ff8800"
    assert Color3(0, 0, 0).Lerp(Color3(100, 200, 50), 0.5) == (50, 100, 25)
    assert Color3.fromHSV(0, 1, 1) == (255, 0, 0)
    assert Color3(1, 2, 3).G == 2
    with pytest.raises(ValueError):
        Color3(300, 0, 0)
    with pytest.raises(ValueError):
        Color3.fromHex("#12")


def test_IntValue():
    Value = IntValue(5)
    Received = []
    Value.Changed.Connect(Received.append)
    _ = Value + 1
    _ = 2 * Value
    assert Received == []
    Value.Value = 5
    Value.Value = 7
    assert Received == [7]
    with pytest.raises(TypeError):
        Value.Value = "x"
    assert IntValue().Value == 0
