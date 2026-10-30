from collections import OrderedDict
import pygame

MAX_CACHED_RECTS = 128

# Rectangles semi-transparents déjà dessinés : (taille, couleur, alpha, rayon, épaisseur) -> Surface
_RectCache : OrderedDict[tuple, pygame.Surface] = OrderedDict()


def _GetTransparentRect(Size : tuple[int, int], Color, Alpha : int, Radius : int, Width : int) -> pygame.Surface:
    Key = (Size, tuple(Color[:3]), Alpha, Radius, Width)
    Temp = _RectCache.get(Key)
    if Temp is not None:
        _RectCache.move_to_end(Key)
        return Temp

    Temp = pygame.Surface(Size, pygame.SRCALPHA)
    pygame.draw.rect(Temp, (*Color[:3], Alpha), Temp.get_rect(), Width, border_radius=Radius)
    _RectCache[Key] = Temp
    if len(_RectCache) > MAX_CACHED_RECTS:
        _RectCache.popitem(last=False)
    return Temp


def DrawRect(Surface : pygame.Surface, Rect : pygame.Rect, Color, Transparency : float = 0.0, Radius : int = 0, Width : int = 0):
    """Rectangle plein (Width = 0) ou contour (Width > 0), avec transparence (0 = opaque, 1 = invisible) et coins arrondis"""
    if Transparency >= 1.0 or Rect.width <= 0 or Rect.height <= 0:
        return

    if Transparency <= 0.0:
        pygame.draw.rect(Surface, Color, Rect, Width, border_radius=Radius)
        return

    Alpha = int((1.0 - Transparency) * 255)
    Surface.blit(_GetTransparentRect(Rect.size, Color, Alpha, Radius, Width), Rect.topleft)


_Scratch : dict[tuple[int, int], pygame.Surface] = {}


def GetScratch(Size : tuple[int, int]) -> pygame.Surface:
    """Surface transparente réutilisée pour les rendus intermédiaires (ex: UIGradient). Effacer la zone utilisée avant."""
    Scratch = _Scratch.get(Size)
    if Scratch is None:
        _Scratch.clear()
        Scratch = _Scratch[Size] = pygame.Surface(Size, pygame.SRCALPHA)
    return Scratch
