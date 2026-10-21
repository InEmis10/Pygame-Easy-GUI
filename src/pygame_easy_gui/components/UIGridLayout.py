import math
import pygame
from pygame_easy_gui.datatypes.udim import Udim2
from pygame_easy_gui.datatypes.vector2 import Vector2
from pygame_easy_gui.components.UILayout import UILayout, AlignStart


class UIGridLayout(UILayout):
    """
    Range les enfants en grille. Tous les enfants prennent la taille CellSize.
    StartCorner : coin où est placé le premier enfant ("topleft" | "topright" | "bottomleft" | "bottomright")
    AbsoluteCellSize : taille en pixels d'une cellule | AbsoluteCellCount : Vector2(colonnes, lignes)
    """
    def __init__(self, **Properties):
        super().__init__()
        self.CellSize = Udim2(0, 100, 0, 100)
        self.CellPadding = Udim2(0, 5, 0, 5)
        self.FillDirection = "horizontal"  # "horizontal" = remplit les lignes d'abord | "vertical" = les colonnes
        self.FillDirectionMaxCells = 0     # 0 = autant que la place le permet
        self.StartCorner = "topleft"
        self._CellCount = (0, 0)
        self._ApplyProperties(Properties)

    def _GetCellSize(self, ContentSize : pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(
            self.CellSize.X.Scale * ContentSize.x + self.CellSize.X.Offset,
            self.CellSize.Y.Scale * ContentSize.y + self.CellSize.Y.Offset,
        )

    def _Compute(self, Parent, ContentSize : pygame.Vector2) -> tuple[dict, pygame.Vector2]:
        Children = self._GetSortedChildren(Parent)
        Cell = self._GetCellSize(ContentSize)
        PadX = self.CellPadding.X.Scale * ContentSize.x + self.CellPadding.X.Offset
        PadY = self.CellPadding.Y.Scale * ContentSize.y + self.CellPadding.Y.Offset
        Horizontal = self.FillDirection.lower() == "horizontal"

        if Horizontal:
            Step = Cell.x + PadX
            Fit = int((ContentSize.x + PadX) // Step) if Step > 0 else 1
        else:
            Step = Cell.y + PadY
            Fit = int((ContentSize.y + PadY) // Step) if Step > 0 else 1
        PerLine = max(1, Fit)
        if self.FillDirectionMaxCells > 0:
            PerLine = min(PerLine, self.FillDirectionMaxCells)

        Count = len(Children)
        LineCount = math.ceil(Count / PerLine) if Count else 0
        Columns, Rows = (min(Count, PerLine), LineCount) if Horizontal else (LineCount, min(Count, PerLine))

        Used = pygame.Vector2(
            Columns * Cell.x + max(0, Columns - 1) * PadX,
            Rows * Cell.y + max(0, Rows - 1) * PadY,
        )
        StartX = AlignStart(self.HorizontalAlignment, ContentSize.x, Used.x)
        StartY = AlignStart(self.VerticalAlignment, ContentSize.y, Used.y)

        Corner = self.StartCorner.lower()
        FromRight = "right" in Corner
        FromBottom = "bottom" in Corner
        Positions = {}
        for Index, Child in enumerate(Children):
            if Horizontal:
                Column, Row = Index % PerLine, Index // PerLine
            else:
                Row, Column = Index % PerLine, Index // PerLine
            if FromRight:
                Column = Columns - 1 - Column
            if FromBottom:
                Row = Rows - 1 - Row
            Positions[Child] = (StartX + Column * (Cell.x + PadX), StartY + Row * (Cell.y + PadY))

        self._CellCount = (Columns, Rows)
        return Positions, Used

    def _EnsureParentComputed(self) -> bool:
        if self._Parent is None:
            return False
        self._EnsureComputed(self._Parent, self._Parent._GetContentRect()[1])
        return True

    @property
    def AbsoluteCellSize(self) -> pygame.Vector2:
        if self._Parent is None:
            return pygame.Vector2(0, 0)
        return self._GetCellSize(self._Parent._GetContentRect()[1])

    @property
    def AbsoluteCellCount(self) -> Vector2:
        if not self._EnsureParentComputed():
            return Vector2(0, 0)
        return Vector2(*self._CellCount)
