import time
import pygame
from pygame_easy_gui.core.GuiObject import GuiObject
from pygame_easy_gui.widgets.TextLabel import TextLabel
from pygame_easy_gui.core.Signal import Signal
from pygame_easy_gui.services import Clipboard

DOUBLE_CLICK_TIME = 0.4   # secondes


class TextBox(TextLabel):
    """
    Champ de saisie. Cliquer dessus prend le focus, cliquer ailleurs / Echap le relâche.
    Entrée : relâche le focus (FocusLost(True)) ou ajoute une ligne si MultiLine.
    Raccourcis : flèches, Home / End, Ctrl + flèches / Backspace / Suppr (mot par mot).
    Sélection : Maj + flèches / Home / End, glisser la souris, Maj + clic, double-clic (mot), Ctrl + A.
    Presse-papiers : Ctrl + C / X / V.
    Chaque action se désactive : SelectionEnabled, CopyEnabled, CutEnabled, PasteEnabled (et TextEditable pour toute modification).
    Doit être dans un ScreenGui (ou un arbre géré par un EventManager) pour recevoir le clavier.
    """
    _CanFocus = True
    _RenderAttributes = frozenset({"_IsFocused", "_CursorShown"})

    def __init__(self):
        super().__init__()
        self.Name = "TextBox"
        self.Text = ""
        self.Active = True
        self.TextXAlignment = "left"

        self.PlaceholderText = ""
        self.PlaceholderColor3 = (150, 150, 150)
        self.CursorColor3 = None        # None = TextColor3
        self.ClearTextOnFocus = False
        self.MultiLine = False
        self.TextEditable = True
        self.MaxLength = 0              # 0 = illimité
        self.CursorPosition = 0

        self.SelectionStart = -1        # autre bout de la sélection (-1 = aucune), l'autre étant CursorPosition
        self.SelectionColor3 = (70, 120, 200)
        self.SelectionEnabled = True
        self.CopyEnabled = True
        self.CutEnabled = True
        self.PasteEnabled = True

        self.Focused = Signal()
        self.FocusLost = Signal()       # (EnterPressed)

        self._IsFocused = False
        self._BlinkTimer = 0.0
        self._CursorShown = False
        self._ScrollX = 0.0
        self._ScrollY = 0.0
        self._Layout = None             # (Lignes, X de chaque ligne, Y de départ, hauteur de ligne) du dernier rendu
        self._OldRepeat = (0, 0)
        self._Dragging = False
        self._LastClick = (0.0, -1)     # (heure, index) du dernier clic, pour le double-clic

    # Focus
    def _GetEventManager(self):
        return getattr(self._GetRoot(), "_EventManager", None)

    def CaptureFocus(self):
        Manager = self._GetEventManager()
        if Manager is None:
            raise RuntimeError("La TextBox doit être dans un ScreenGui pour prendre le focus")
        Manager.SetFocus(self)

    def ReleaseFocus(self, EnterPressed : bool = False):
        Manager = self._GetEventManager()
        if self._IsFocused and Manager is not None:
            Manager.SetFocus(None, EnterPressed)

    def IsFocused(self) -> bool:
        return self._IsFocused

    def _OnFocus(self):
        self._IsFocused = True
        if self.ClearTextOnFocus:
            self.Text = ""
        self.CursorPosition = len(self.Text)
        self.SelectionStart = -1
        self._BlinkTimer = 0.0
        self._OldRepeat = pygame.key.get_repeat()
        pygame.key.set_repeat(400, 35)
        pygame.key.start_text_input()
        self.Focused.Fire()

    def _OnFocusLost(self, EnterPressed : bool):
        self._IsFocused = False
        self._Dragging = False
        self.SelectionStart = -1
        pygame.key.set_repeat(*self._OldRepeat)
        self.FocusLost.Fire(EnterPressed)

    # Sélection
    def GetSelection(self) -> tuple[int, int] | None:
        """(début, fin) de la sélection, None s'il n'y en a pas"""
        if not self.SelectionEnabled or self.SelectionStart < 0:
            return None
        Anchor = min(self.SelectionStart, len(self.Text))
        Cursor = self._GetCursor()
        if Anchor == Cursor:
            return None
        return min(Anchor, Cursor), max(Anchor, Cursor)

    def GetSelectedText(self) -> str:
        Selection = self.GetSelection()
        return self.Text[Selection[0]:Selection[1]] if Selection else ""

    def SelectAll(self):
        if self.SelectionEnabled and self.Text:
            self.SelectionStart = 0
            self._SetCursor(len(self.Text))

    def ClearSelection(self):
        self.SelectionStart = -1

    def _MoveCursor(self, Index : int, Extend : bool = False):
        """Déplace le curseur ; Extend (Maj) agrandit la sélection au lieu de l'effacer"""
        if Extend and self.SelectionEnabled:
            if self.SelectionStart < 0:
                self.SelectionStart = self._GetCursor()
        else:
            self.SelectionStart = -1
        self._SetCursor(Index)

    # Presse-papiers
    def Copy(self) -> bool:
        Selected = self.GetSelectedText()
        if not self.CopyEnabled or not Selected:
            return False
        Clipboard.SetText(Selected)
        return True

    def Cut(self) -> bool:
        if not (self.CutEnabled and self.TextEditable) or not self.Copy():
            return False
        self._Replace("")
        return True

    def Paste(self) -> bool:
        if not (self.PasteEnabled and self.TextEditable):
            return False
        Value = Clipboard.GetText()
        if not Value:
            return False
        self._Insert(Value)
        return True

    # Edition
    def _GetCursor(self) -> int:
        return max(0, min(self.CursorPosition, len(self.Text)))

    def _SetCursor(self, Index : int):
        self.CursorPosition = Index
        self._BlinkTimer = 0.0

    def _Replace(self, Value : str):
        """Remplace la sélection (ou insère au curseur) par Value, en un seul changement de Text"""
        Start, End = self.GetSelection() or (self._GetCursor(), self._GetCursor())
        if self.MaxLength > 0:
            Value = Value[:max(0, self.MaxLength - (len(self.Text) - (End - Start)))]
        if not Value and Start == End:
            return
        self.SelectionStart = -1
        self._SetCursor(Start + len(Value))
        self.Text = self.Text[:Start] + Value + self.Text[End:]

    def _Insert(self, Value : str):
        if not self.TextEditable:
            return
        if not self.MultiLine:
            Value = Value.replace("\r\n", " ").replace("\n", " ")
        if Value:
            self._Replace(Value)

    def _PreviousWordStart(self, Index : int) -> int:
        while Index > 0 and self.Text[Index - 1].isspace():
            Index -= 1
        while Index > 0 and not self.Text[Index - 1].isspace():
            Index -= 1
        return Index

    def _NextWordEnd(self, Index : int) -> int:
        while Index < len(self.Text) and self.Text[Index].isspace():
            Index += 1
        while Index < len(self.Text) and not self.Text[Index].isspace():
            Index += 1
        return Index

    def _SelectWordAt(self, Index : int):
        Start = End = Index
        while Start > 0 and not self.Text[Start - 1].isspace():
            Start -= 1
        while End < len(self.Text) and not self.Text[End].isspace():
            End += 1
        if Start != End:
            self.SelectionStart = Start
            self._SetCursor(End)

    def _OnTextInput(self, Text : str):
        self._Insert(Text)

    def _OnKeyDown(self, Event : pygame.event.Event):
        Key = Event.key
        Ctrl = bool(Event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META))
        Shift = bool(Event.mod & pygame.KMOD_SHIFT)
        Text = self.Text
        Cursor = self._GetCursor()
        Selection = self.GetSelection()

        if Ctrl and Key == pygame.K_a:
            self.SelectAll()
        elif Ctrl and Key == pygame.K_c:
            self.Copy()
        elif Ctrl and Key == pygame.K_x:
            self.Cut()
        elif Ctrl and Key == pygame.K_v:
            self.Paste()
        elif Key == pygame.K_ESCAPE:
            self.ReleaseFocus()
        elif Key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.MultiLine:
                self._Insert("\n")
            else:
                self.ReleaseFocus(EnterPressed=True)
        elif Key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            if not self.TextEditable:
                return
            if Selection:
                self._Replace("")
            elif Key == pygame.K_BACKSPACE and Cursor > 0:
                Start = self._PreviousWordStart(Cursor) if Ctrl else Cursor - 1
                self._SetCursor(Start)
                self.Text = Text[:Start] + Text[Cursor:]
            elif Key == pygame.K_DELETE and Cursor < len(Text):
                End = self._NextWordEnd(Cursor) if Ctrl else Cursor + 1
                self._SetCursor(Cursor)
                self.Text = Text[:Cursor] + Text[End:]
        elif Key == pygame.K_LEFT:
            if Selection and not Shift:
                self._MoveCursor(Selection[0])
            else:
                self._MoveCursor(self._PreviousWordStart(Cursor) if Ctrl else max(0, Cursor - 1), Shift)
        elif Key == pygame.K_RIGHT:
            if Selection and not Shift:
                self._MoveCursor(Selection[1])
            else:
                self._MoveCursor(self._NextWordEnd(Cursor) if Ctrl else min(len(Text), Cursor + 1), Shift)
        elif Key == pygame.K_HOME:
            self._MoveCursor(Text.rfind("\n", 0, Cursor) + 1 if self.MultiLine and not Ctrl else 0, Shift)
        elif Key == pygame.K_END:
            LineEnd = Text.find("\n", Cursor) if self.MultiLine and not Ctrl else -1
            self._MoveCursor(len(Text) if LineEnd == -1 else LineEnd, Shift)
        elif Key in (pygame.K_UP, pygame.K_DOWN) and self.MultiLine:
            self._MoveVertical(-1 if Key == pygame.K_UP else 1, Shift)

    def _MoveVertical(self, Direction : int, Extend : bool = False):
        Lines = self.Text.split("\n")
        Line, Column = _IndexToLineColumn(self.Text, self._GetCursor())
        Target = Line + Direction
        if not 0 <= Target < len(Lines):
            return
        Font = self._GetFont()
        X = Font.size(Lines[Line][:Column])[0]
        self._MoveCursor(_LineColumnToIndex(Lines, Target, _ColumnFromX(Font, Lines[Target], X)), Extend)

    # Souris
    def _IndexAt(self, Pos : pygame.Vector2) -> int | None:
        """Index du caractère le plus proche de Pos (d'après le dernier rendu)"""
        if self._Layout is None or not self.Text:
            return None
        Lines, LineXs, StartY, LineSize = self._Layout
        Line = min(max(int((Pos.y - StartY) // LineSize), 0), len(Lines) - 1)
        Column = _ColumnFromX(self._GetFont(), Lines[Line], Pos.x - LineXs[Line])
        return _LineColumnToIndex(Lines, Line, Column)

    def _OnMouseDown(self, Button : int, Pos : pygame.Vector2):
        if Button != 1:
            return
        Index = self._IndexAt(Pos)
        if Index is None:
            return
        Now = time.perf_counter()
        LastTime, LastIndex = self._LastClick
        self._LastClick = (Now, Index)
        if self.SelectionEnabled and Now - LastTime < DOUBLE_CLICK_TIME and Index == LastIndex:
            self._SelectWordAt(Index)
            return

        Shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
        self._MoveCursor(Index, Shift)
        if self.SelectionEnabled:
            if not Shift:
                self.SelectionStart = Index   # point de départ du glisser
            self._Dragging = True

    def _OnMouseDrag(self, Pos : pygame.Vector2):
        if self._Dragging and self.SelectionEnabled:
            Index = self._IndexAt(Pos)
            if Index is not None:
                self._SetCursor(Index)

    def _OnMouseUp(self, Button : int, Pos : pygame.Vector2, IsOver : bool):
        if Button == 1:
            self._Dragging = False

    def _Update(self, Dt : float):
        self._BlinkTimer += Dt
        # Redessine uniquement quand le curseur apparaît / disparaît
        CursorShown = self._IsCursorShown()
        if CursorShown != self._CursorShown:
            self._CursorShown = CursorShown

    def _IsCursorShown(self) -> bool:
        return self._IsFocused and (self._BlinkTimer % 1.0) < 0.5

    def _GetDrawBounds(self) -> pygame.Rect:
        # Le texte est coupé à la zone de la TextBox
        return GuiObject._GetDrawBounds(self)

    # Rendu
    def _Draw(self, Surface : pygame.Surface):
        self._DrawBackground(Surface)
        Rect = self._GetPaddedRect()
        if Rect.width <= 0 or Rect.height <= 0:
            return

        Font = self._GetFont()
        LineSize = Font.get_linesize()
        ShowPlaceholder = not self.Text
        Source = self.PlaceholderText if ShowPlaceholder else self.Text
        Color = self.PlaceholderColor3 if ShowPlaceholder else self.TextColor3
        Lines = Source.split("\n") if self.MultiLine else [Source.replace("\n", " ")]

        Cursor = 0 if ShowPlaceholder else self._GetCursor()
        CursorLine, CursorColumn = _IndexToLineColumn(Source, Cursor) if self.MultiLine else (0, Cursor)
        CursorX = Font.size(Lines[CursorLine][:CursorColumn])[0]
        Widths = [Font.size(Line)[0] for Line in Lines]

        # Horizontal : alignement si tout tient, sinon défilement pour garder le curseur visible
        if max(Widths) <= Rect.width:
            self._ScrollX = 0.0
            XAlignment = self.TextXAlignment.lower()
            if XAlignment == "right":
                LineXs = [Rect.right - Width for Width in Widths]
            elif XAlignment == "center":
                LineXs = [Rect.centerx - Width // 2 for Width in Widths]
            else:
                LineXs = [Rect.left] * len(Lines)
        else:
            if CursorX - self._ScrollX > Rect.width - 2:
                self._ScrollX = CursorX - Rect.width + 2
            if CursorX - self._ScrollX < 0:
                self._ScrollX = CursorX
            self._ScrollX = min(max(self._ScrollX, 0), max(Widths) - Rect.width + 2)
            LineXs = [Rect.left - self._ScrollX] * len(Lines)

        # Vertical : idem
        TotalHeight = LineSize * len(Lines)
        if TotalHeight <= Rect.height:
            self._ScrollY = 0.0
            YAlignment = self.TextYAlignment.lower()
            if YAlignment == "top":
                StartY = Rect.top
            elif YAlignment == "bottom":
                StartY = Rect.bottom - TotalHeight
            else:
                StartY = Rect.centery - TotalHeight // 2
        else:
            CursorTop = CursorLine * LineSize
            if CursorTop - self._ScrollY < 0:
                self._ScrollY = CursorTop
            if CursorTop + LineSize - self._ScrollY > Rect.height:
                self._ScrollY = CursorTop + LineSize - Rect.height
            self._ScrollY = min(max(self._ScrollY, 0), TotalHeight - Rect.height)
            StartY = Rect.top - self._ScrollY

        self._Layout = (Lines, LineXs, StartY, LineSize)

        OldClip = Surface.get_clip()
        Surface.set_clip(Rect.clip(OldClip))
        Selection = None if ShowPlaceholder or not self._IsFocused else self.GetSelection()
        if Selection is not None:
            self._DrawSelection(Surface, Font, Lines, LineXs, StartY, LineSize, Selection)
        for Index, Line in enumerate(Lines):
            if Line:
                Surface.blit(Font.render(Line, True, Color), (LineXs[Index], StartY + Index * LineSize))
        if self._IsCursorShown():
            X = LineXs[CursorLine] + CursorX
            Y = StartY + CursorLine * LineSize
            pygame.draw.line(Surface, self.CursorColor3 or self.TextColor3, (X, Y), (X, Y + LineSize - 1))
        Surface.set_clip(OldClip)

    def _DrawSelection(self, Surface, Font, Lines, LineXs, StartY, LineSize, Selection):
        Start, End = Selection
        LineStart = 0
        for Index, Line in enumerate(Lines):
            LineEnd = LineStart + len(Line)
            From, To = max(Start, LineStart), min(End, LineEnd)
            if From <= To and Start <= LineEnd and End >= LineStart:
                X1 = Font.size(Line[:From - LineStart])[0]
                X2 = Font.size(Line[:To - LineStart])[0]
                if End > LineEnd:
                    X2 += Font.size(" ")[0]   # le retour à la ligne sélectionné
                if X2 > X1:
                    pygame.draw.rect(Surface, self.SelectionColor3, (LineXs[Index] + X1, StartY + Index * LineSize, X2 - X1, LineSize))
            LineStart = LineEnd + 1


def _IndexToLineColumn(Text : str, Index : int) -> tuple[int, int]:
    Before = Text[:Index]
    return Before.count("\n"), Index - (Before.rfind("\n") + 1)


def _LineColumnToIndex(Lines : list[str], Line : int, Column : int) -> int:
    return sum(len(Previous) + 1 for Previous in Lines[:Line]) + Column


def _ColumnFromX(Font : pygame.font.Font, LineText : str, X : float) -> int:
    """Index du caractère le plus proche de la position X (en pixels depuis le début de la ligne)"""
    Previous = 0
    for Index in range(1, len(LineText) + 1):
        Width = Font.size(LineText[:Index])[0]
        if Width >= X:
            return Index if Width - X < X - Previous else Index - 1
        Previous = Width
    return len(LineText)
