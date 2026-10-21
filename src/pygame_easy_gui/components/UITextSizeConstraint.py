from pygame_easy_gui.components.UIComponent import UIComponent


class UITextSizeConstraint(UIComponent):
    """Bornes de la taille de police quand TextScaled = True"""
    def __init__(self, **Properties):
        super().__init__()
        self.MinTextSize = 1
        self.MaxTextSize = 100
        self._ApplyProperties(Properties)
