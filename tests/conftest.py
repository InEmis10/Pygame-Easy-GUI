import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import pygame
import pytest


@pytest.fixture(autouse=True)
def Screen():
    pygame.init()
    Surface = pygame.display.set_mode((800, 600))
    yield Surface
    pygame.quit()


@pytest.fixture
def MousePos(monkeypatch):
    """Position de souris simulée : MousePos[0] = (x, y)"""
    Holder = [(0, 0)]
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: Holder[0])
    return Holder


def Click(Gui, Pos, Button=1):
    return Gui.HandleEvents([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=Button, pos=Pos),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=Button, pos=Pos),
    ])
