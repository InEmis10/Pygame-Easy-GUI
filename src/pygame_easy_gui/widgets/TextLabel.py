from pygame_easy_gui.core.GuiObject import GuiObject
from pygame_easy_gui.datatypes.Vector2 import Vector2
from pygame_easy_gui.core.Signal import Signal
from pygame_easy_gui.components.UITextSizeConstraint import UITextSizeConstraint
from pygame_easy_gui.render import Text as TextRender
from pygame_easy_gui.render import Display
import pygame


class TextLabel(GuiObject):
    def __init__(self):
        super().__init__()
        self.TextChanged = Signal()   # (NouveauTexte)
        self._Text = ""

        self.Name = "TextLabel"
        self.Text = "Label"
        self.TextColor3 = (0, 0, 0)
        self.TextSize = 20
        self.TextTransparency = 0.0
        self.FontName = None             # None = police par défaut de pygame, sinon chemin vers un .ttf
        self.BackgroundColor3 = (255,255,255)
        self.BackgroundTransparency = 0
        self.TextXAlignment = "center"   # "left" | "center" | "right"
        self.TextYAlignment = "center"   # "top" | "center" | "bottom"
        self.TextWrapped = False         # retour à la ligne automatique
        self.TextTruncate = "none"       # "none" | "atend" (ajoute "..." si le texte dépasse)
        self.TextScaled = False          # taille de police auto pour remplir l'objet (voir UITextSizeConstraint)

        self._TextCacheKey = None
        self._TextCacheSurface = None

    @property
    def Text(self) -> str:
        return self._Text

    @Text.setter
    def Text(self, Value : str):
        Value = str(Value)
        if Value == self._Text:
            return
        self._Text = Value
        self.TextChanged.Fire(Value)

    def _GetFont(self, Size : int | None = None) -> pygame.font.Font:
        return TextRender.GetFont(self.FontName, Size or self.TextSize)

    def _GetTextSizeLimits(self) -> tuple[int, int]:
        Constraint = self.GetComponent(UITextSizeConstraint)
        if Constraint is None:
            return 1, 100
        return Constraint.MinTextSize, Constraint.MaxTextSize

    def _GetTextSurface(self, Rect : pygame.Rect) -> pygame.Surface:
        """Rendu du texte mis en cache : il n'est recalculé que si une propriété du texte ou la taille change"""
        Key = (
            self.Text, self.FontName, self.TextSize, tuple(self.TextColor3), self.TextTransparency,
            self.TextXAlignment, self.TextWrapped, self.TextTruncate, self.TextScaled,
            Rect.size, self._GetTextSizeLimits() if self.TextScaled else None,
        )
        if Key == self._TextCacheKey:
            return self._TextCacheSurface

        Size = self.TextSize
        if self.TextScaled:
            MinSize, MaxSize = self._GetTextSizeLimits()
            Size = TextRender.FindScaledSize(self.FontName, self.Text, Rect.width, Rect.height, self.TextWrapped, MinSize, MaxSize)

        Font = self._GetFont(Size)
        Lines = TextRender.LayoutLines(Font, self.Text, Rect.width, Rect.height, self.TextWrapped, self.TextTruncate.lower())
        Surf = TextRender.RenderLines(Font, Lines, self.TextColor3, self.TextXAlignment.lower())
        Surf = Display.Optimize(Surf)
        if self.TextTransparency > 0:
            Surf.set_alpha(int((1.0 - self.TextTransparency) * 255))

        self._TextCacheKey = Key
        self._TextCacheSurface = Surf
        return Surf

    def _GetTextArea(self) -> pygame.Rect:
        """Zone dans laquelle le texte est aligné"""
        return self._GetPaddedRect()

    def _GetTextRect(self, Area : pygame.Rect) -> tuple[pygame.Surface, pygame.Rect]:
        """Surface du texte et position où la coller (le texte peut dépasser de Area s'il n'est ni coupé ni retourné à la ligne)"""
        TextSurf = self._GetTextSurface(Area)
        TextRect = TextSurf.get_rect()

        XAlignment = self.TextXAlignment.lower()
        if XAlignment == "left":
            TextRect.left = Area.left
        elif XAlignment == "right":
            TextRect.right = Area.right
        else:
            TextRect.centerx = Area.centerx

        YAlignment = self.TextYAlignment.lower()
        if YAlignment == "top":
            TextRect.top = Area.top
        elif YAlignment == "bottom":
            TextRect.bottom = Area.bottom
        else:
            TextRect.centery = Area.centery
        return TextSurf, TextRect

    @property
    def TextBounds(self) -> Vector2:
        """Taille en pixels du texte affiché"""
        Surf = self._GetTextSurface(self._GetTextArea())
        return Vector2(Surf.get_width(), Surf.get_height())

    def _HasVisibleText(self) -> bool:
        return bool(self.Text) and self.TextTransparency < 1.0

    def _GetDrawBounds(self) -> pygame.Rect:
        Bounds = super()._GetDrawBounds()
        if self._HasVisibleText():
            Bounds = Bounds.union(self._GetTextRect(self._GetTextArea())[1])
        return Bounds

    def _DrawText(self, Surface : pygame.Surface):
        if self._HasVisibleText():
            TextSurf, TextRect = self._GetTextRect(self._GetTextArea())
            Surface.blit(TextSurf, TextRect)

    def _Draw(self, Surface: pygame.Surface):
        self._DrawBackground(Surface)
        self._DrawText(Surface)
