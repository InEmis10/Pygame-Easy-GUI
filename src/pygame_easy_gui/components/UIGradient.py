from collections import OrderedDict
import math
import pygame
from pygame_easy_gui.datatypes.vector2 import Vector2
from pygame_easy_gui.datatypes.sequence import ColorSequence, NumberSequence
from pygame_easy_gui.components.UIComponent import UIComponent
from pygame_easy_gui.render import Display

MAX_CACHED_GRADIENTS = 64

# Dégradés déjà calculés, partagés entre tous les UIGradient : (taille, couleurs, transparences, rotation, décalage) -> Surface
_GradientCache : OrderedDict[tuple, pygame.Surface] = OrderedDict()


class UIGradient(UIComponent):
    """
    Dégradé appliqué au parent (fond, texte et image sont multipliés par le dégradé, pas les enfants).
    Color : ColorSequence (ou une couleur) | Transparency : NumberSequence (ou un nombre, 0 = opaque)
    Rotation : en degrés, sens horaire (0 = de gauche à droite, 90 = de haut en bas)
    Offset : Vector2 décalant le dégradé, relatif à la taille du parent (Vector2(0.5, 0) = d'une demi-largeur vers la droite)
    """
    def __init__(self, **Properties):
        super().__init__()
        self.Color = ColorSequence((255, 255, 255))
        self.Transparency = NumberSequence(0)
        self.Rotation = 0
        self.Offset = Vector2(0, 0)
        self.Enabled = True
        self._ApplyProperties(Properties)

    def _GetSurface(self, Size : tuple[int, int]) -> pygame.Surface:
        Color = self.Color if isinstance(self.Color, ColorSequence) else ColorSequence(self.Color)
        Transparency = self.Transparency if isinstance(self.Transparency, NumberSequence) else NumberSequence(self.Transparency)
        Key = (tuple(Size), Color, Transparency, float(self.Rotation) % 360, (self.Offset.X, self.Offset.Y))
        Surface = _GradientCache.get(Key)
        if Surface is not None:
            _GradientCache.move_to_end(Key)
            return Surface

        Surface = _BuildGradient(*Key)
        _GradientCache[Key] = Surface
        if len(_GradientCache) > MAX_CACHED_GRADIENTS:
            _GradientCache.popitem(last=False)
        return Surface


def _BuildGradient(Size, Color : ColorSequence, Transparency : NumberSequence, Rotation : float, Offset) -> pygame.Surface:
    """Une bande de couleurs, étirée, tournée puis recadrée à la taille voulue (pas besoin de numpy)"""
    Width, Height = Size
    Angle = math.radians(Rotation)
    Cos, Sin = math.cos(Angle), math.sin(Angle)
    # Etendue du parent le long de la direction du dégradé, et en travers
    Length = abs(Width * Cos) + abs(Height * Sin)
    Across = abs(Width * Sin) + abs(Height * Cos)
    Shift = (Offset[0] * Width * Cos + Offset[1] * Height * Sin) / Length if Length > 0 else 0

    Steps = max(2, min(512, math.ceil(Length)))
    Strip = pygame.Surface((Steps, 1), pygame.SRCALPHA)
    for Index in range(Steps):
        Time = min(max((Index + 0.5) / Steps - Shift, 0.0), 1.0)
        R, G, B = Color.Evaluate(Time)
        Alpha = 1.0 - min(max(Transparency.Evaluate(Time), 0.0), 1.0)
        Strip.set_at((Index, 0), (round(R), round(G), round(B), round(Alpha * 255)))

    Margin = 4   # évite les bords transparents laissés par la rotation
    Band = pygame.transform.smoothscale(Strip, (math.ceil(Length) + Margin, math.ceil(Across) + Margin))
    if Rotation:
        Band = pygame.transform.rotate(Band, -Rotation)
    CropRect = pygame.Rect(0, 0, Width, Height)
    CropRect.center = Band.get_rect().center
    Result = Band.subsurface(CropRect.clip(Band.get_rect())).copy()
    return Display.Optimize(Result)
