import pygame
from pygame_easy_gui.core.Signal import Signal


class InputMixin:
    """
    Signaux et hooks d'entrée communs à tous les GuiObject.
    Seuls les objets avec Active = True reçoivent les événements souris (et bloquent ce qu'il y a dessous).
    Les hooks _On... sont appelés par l'EventManager : les redéfinir pour créer un composant interactif.
    """
    _CanFocus = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.MouseEnter = Signal()
        self.MouseLeave = Signal()
        self.MouseMoved = Signal()   # (X, Y)
        self.MouseWheel = Signal()   # (X, Y) : Y > 0 = molette vers le haut
        self.InputBegan = Signal()   # (pygame.Event)
        self.InputEnded = Signal()   # (pygame.Event)

        self._Hovering = False
        self._Pressed = False

    def _CapturesPoint(self, Pos : pygame.Vector2) -> bool:
        """True = l'objet reçoit le clic à ce point même si un enfant est dessus (ex: barre de défilement)"""
        return False

    def _OnMouseDown(self, Button : int, Pos : pygame.Vector2):
        pass

    def _OnMouseUp(self, Button : int, Pos : pygame.Vector2, IsOver : bool):
        pass

    def _OnMouseDrag(self, Pos : pygame.Vector2):
        pass

    def _OnMouseWheel(self, X : int, Y : int) -> bool:
        """Retourne True si la molette a été utilisée (sinon elle remonte au parent)"""
        return False

    def _OnFocus(self):
        pass

    def _OnFocusLost(self, EnterPressed : bool):
        pass

    def _OnKeyDown(self, Event : pygame.event.Event):
        pass

    def _OnTextInput(self, Text : str):
        pass
