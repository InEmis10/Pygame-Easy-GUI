import pygame
from pygame_easy_gui.datatypes.Udim import Udim
from pygame_easy_gui.components.UILayout import UILayout, AlignStart


class UIListLayout(UILayout):
    """
    Empile les enfants les uns après les autres (verticalement ou horizontalement).
    Wraps : passe à la colonne / ligne suivante quand il n'y a plus de place (Padding sert aussi d'espace entre les lignes).
    """
    def __init__(self, **Properties):
        super().__init__()
        self.FillDirection = "vertical"  # "vertical" | "horizontal"
        self.Padding = Udim(0, 0)        # espace entre deux enfants
        self.Wraps = False
        self._ApplyProperties(Properties)

    def _Compute(self, Parent, ContentSize : pygame.Vector2) -> tuple[dict, pygame.Vector2]:
        Children = self._GetSortedChildren(Parent)
        Sizes = [Child._ComputeSize(ContentSize) for Child in Children]
        Vertical = self.FillDirection.lower() == "vertical"
        # Axe principal = sens de remplissage, axe secondaire = en travers
        MainIndex, CrossIndex = (1, 0) if Vertical else (0, 1)
        MainSpace, CrossSpace = ContentSize[MainIndex], ContentSize[CrossIndex]
        MainAlignment, CrossAlignment = (self.VerticalAlignment, self.HorizontalAlignment) if Vertical else (self.HorizontalAlignment, self.VerticalAlignment)
        Gap = self.Padding.Scale * MainSpace + self.Padding.Offset

        Lines = [[]]
        LineLength = 0.0
        for Child, Size in zip(Children, Sizes):
            Length = Size[MainIndex]
            if self.Wraps and Lines[-1] and LineLength + Gap + Length > MainSpace:
                Lines.append([])
                LineLength = 0.0
            LineLength += (Gap if Lines[-1] else 0) + Length
            Lines[-1].append((Child, Size))

        LineThicknesses = [max((Size[CrossIndex] for _, Size in Line), default=0) for Line in Lines]
        TotalCross = sum(LineThicknesses) + Gap * max(0, len(Lines) - 1)
        Positions = {}
        MaxLength = 0.0
        CrossCursor = AlignStart(CrossAlignment, CrossSpace, TotalCross) if self.Wraps else 0.0

        for Line, Thickness in zip(Lines, LineThicknesses):
            Total = sum(Size[MainIndex] for _, Size in Line) + Gap * max(0, len(Line) - 1)
            MaxLength = max(MaxLength, Total)
            MainCursor = AlignStart(MainAlignment, MainSpace, Total)
            # Sans retour à la ligne, chaque enfant est aligné sur toute la largeur (ou hauteur) du parent
            LineSpace = Thickness if self.Wraps else CrossSpace
            for Child, Size in Line:
                Cross = CrossCursor + AlignStart(CrossAlignment, LineSpace, Size[CrossIndex])
                Positions[Child] = (Cross, MainCursor) if Vertical else (MainCursor, Cross)
                MainCursor += Size[MainIndex] + Gap
            CrossCursor += Thickness + Gap

        Content = (TotalCross, MaxLength) if Vertical else (MaxLength, TotalCross)
        return Positions, pygame.Vector2(Content)
