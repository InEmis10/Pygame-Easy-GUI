import pygame
from pygame_easy_gui.core.Signal import Signal


class ButtonMixin:
    """
    Comportement commun aux boutons (TextButton, ImageButton).
    A placer AVANT la classe de base : class MonBouton(ButtonMixin, TextLabel)
    MouseButton1 = clic gauche, MouseButton2 = clic droit.
    """
    # Le survol / l'appui change la couleur ou l'image : la zone du bouton est redessinée
    _RenderAttributes = frozenset({"_Hovering", "_Pressed"})

    def __init__(self):
        super().__init__()
        self.MouseButton1Click = Signal()
        self.MouseButton1Down = Signal()
        self.MouseButton1Up = Signal()
        self.MouseButton2Click = Signal()
        self.MouseButton2Down = Signal()
        self.MouseButton2Up = Signal()
        self.Activated = Signal()

        self.AutoButtonColor = True
        self.Active = True

    def _ApplyAutoColor(self, Color : tuple) -> tuple:
        """Assombrit la couleur au survol (15%) et au clic (30%) si AutoButtonColor"""
        if not (self.AutoButtonColor and self.Active and self._Hovering):
            return Color
        Factor = 0.7 if self._Pressed else 0.85
        return tuple(int(Channel * Factor) for Channel in Color[:3])

    def _GetBackgroundColor(self) -> tuple:
        return self._ApplyAutoColor(self.BackgroundColor3)

    def _OnMouseDown(self, Button : int, Pos : pygame.Vector2):
        if Button == 1:
            self.MouseButton1Down.Fire()
        elif Button == 3:
            self.MouseButton2Down.Fire()

    def _OnMouseUp(self, Button : int, Pos : pygame.Vector2, IsOver : bool):
        if Button == 1:
            self.MouseButton1Up.Fire()
            if IsOver:
                self.MouseButton1Click.Fire()
                self.Activated.Fire()
        elif Button == 3:
            self.MouseButton2Up.Fire()
            if IsOver:
                self.MouseButton2Click.Fire()
