import pygame

from .gui_object import GuiObject

##ToDo: Make event in different file


class EventManager:
    """
    Gère le hit-test souris et le déclenchement des Signals des TextButton.
    A appeler manuellement chaque frame depuis la boucle principale, avec la liste des events pygame.
    """

    def __init__(self, root: GuiObject):
        self.Root = root
        self._hovered: "TextButton | None" = None
        self._pressed: "TextButton | None" = None

    def _CollectButtons(self, obj: GuiObject, out: list):
        from ..widgets.text_button import TextButton   # dans la fonction : widgets importe core (cycle)
        if not obj.Visible:                            # parent caché → tous ses boutons le sont aussi
            return
        if isinstance(obj, TextButton):
            out.append(obj)
        for child in obj.Children:
            self._CollectButtons(child, out)

    def _GetTopButtonAt(self, pos: pygame.Vector2) -> "TextButton | None":
        buttons = []
        self._CollectButtons(self.Root, buttons)

        for btn in reversed(buttons):
            if not btn.Active:
                continue
            if not btn.Visible:
                continue
            if btn.GetRect().collidepoint(pos.x, pos.y):
                return btn
        return None

    def Update(self, events: list):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        current = self._GetTopButtonAt(mouse_pos)

        if current is not self._hovered:
            if self._hovered is not None:
                self._hovered._Hovering = False
                self._hovered.MouseLeave.Fire()
            if current is not None:
                current._Hovering = True
                current.MouseEnter.Fire()
            self._hovered = current

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current is not None:
                    current._Pressed = True
                    self._pressed = current
                    current.MouseButton1Down.Fire()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._pressed is not None:
                    self._pressed._Pressed = False
                    self._pressed.MouseButton1Up.Fire()

                    if self._pressed is current:
                        self._pressed.MouseButton1Click.Fire()
                    self._pressed = None
