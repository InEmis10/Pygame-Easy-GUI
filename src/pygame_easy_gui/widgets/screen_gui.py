from ..core.gui_object import GuiObject
from ..datatypes.udim import Udim2
from ..datatypes.vector2 import Vector2


class ScreenGui(GuiObject):
    """Conteneur qui couvre toute la fenêtre, comme ScreenGui dans Roblox.

        hud = ScreenGui.New(Name="HUD", DisplayOrder=10)
        app.Gui.Add(hud)
        hud.AddChild(frame)
        hud.Enabled = False      # cache tout le HUD d'un coup

    Enabled : affiche / cache tout le contenu (et le rend non cliquable).
    DisplayOrder : le plus grand est dessiné au-dessus des autres.
    """

    def __init__(self):
        super().__init__()
        self.Name = "ScreenGui"
        self.Enabled = True
        self._DisplayOrder = 0
        self._Service = None                 # _GuiService de l'Application, posé par app.Gui.Add

        # Toujours la taille de la fenêtre
        self.Position = Udim2(0, 0, 0, 0)
        self.Size = Udim2(1, 0, 1, 0)
        self.AnchorPoint = Vector2(0, 0)

    @property
    def DisplayOrder(self) -> int:
        return self._DisplayOrder

    @DisplayOrder.setter
    def DisplayOrder(self, value : int):
        self._DisplayOrder = value
        if self._Service is not None:
            self._Service._Sorted = False    # le service retriera au prochain dessin

    def SetPosition(self, pos):
        raise AttributeError("ScreenGui couvre toujours la fenêtre : Position n'est pas modifiable")

    def SetSize(self, size):
        raise AttributeError("ScreenGui couvre toujours la fenêtre : Size n'est pas modifiable")
