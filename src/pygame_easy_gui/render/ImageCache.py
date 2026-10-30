"""
Cache d'images partagé par tous les ImageLabel / ImageButton / ImageTextButton :
- un fichier n'est chargé qu'une fois, quel que soit le nombre d'objets qui l'affichent
- chaque version redimensionnée / teintée est calculée une fois puis réutilisée (même par d'autres objets)
"""
from collections import OrderedDict
import math
import pathlib
import weakref
import pygame
from pygame_easy_gui.render import Display

MAX_VARIANTS_PER_IMAGE = 16   # tailles / teintes gardées par image (les plus anciennes sont oubliées)

_Loaded : dict[str, pygame.Surface] = {}
# Versions transformées : par chemin, ou par Surface (oubliées quand la Surface est libérée)
_PathVariants : dict[str, OrderedDict] = {}
_SurfaceVariants : "weakref.WeakKeyDictionary[pygame.Surface, OrderedDict]" = weakref.WeakKeyDictionary()


def Load(Source) -> pygame.Surface | None:
    """Chemin (str / Path) ou pygame.Surface -> Surface. Erreur immédiate si le fichier n'existe pas."""
    if Source is None or isinstance(Source, pygame.Surface):
        return Source
    if not isinstance(Source, (str, pathlib.Path)):
        raise TypeError(f"Image attend un chemin ou une pygame.Surface, reçu {type(Source).__name__}")
    Key = str(Source)
    Img = _Loaded.get(Key)
    if Img is None:
        Img = _Loaded[Key] = pygame.image.load(Key)
    return Img


def Invalidate(Source = None):
    """Oublie les versions en cache d'une image (à appeler si une Surface a été modifiée), ou de toutes si Source est None"""
    if Source is None:
        _Loaded.clear()
        _PathVariants.clear()
        _SurfaceVariants.clear()
    elif isinstance(Source, pygame.Surface):
        _SurfaceVariants.pop(Source, None)
    else:
        _Loaded.pop(str(Source), None)
        _PathVariants.pop(str(Source), None)


def _GetVariants(Source) -> OrderedDict:
    if isinstance(Source, pygame.Surface):
        Variants = _SurfaceVariants.get(Source)
        if Variants is None:
            Variants = _SurfaceVariants[Source] = OrderedDict()
        return Variants
    return _PathVariants.setdefault(str(Source), OrderedDict())


def GetScaled(Source, Size : tuple[int, int], ScaleType : str, Color : tuple, Transparency : float) -> pygame.Surface | None:
    """Image prête à être collée : redimensionnée selon ScaleType, teintée et transparente"""
    Img = Load(Source)
    if Img is None or Size[0] <= 0 or Size[1] <= 0:
        return None
    Key = (Size, ScaleType, tuple(Color[:3]), Transparency)
    Variants = _GetVariants(Source)
    Result = Variants.get(Key)
    if Result is not None:
        Variants.move_to_end(Key)
        return Result

    Result = _Build(Img, Size, ScaleType, Color, Transparency)
    Variants[Key] = Result
    if len(Variants) > MAX_VARIANTS_PER_IMAGE:
        Variants.popitem(last=False)
    return Result


def _Build(Img : pygame.Surface, Size : tuple[int, int], ScaleType : str, Color : tuple, Transparency : float) -> pygame.Surface:
    Width, Height = Size
    ImgWidth, ImgHeight = Img.get_size()

    if ImgWidth == 0 or ImgHeight == 0:
        Result = pygame.Surface(Size, pygame.SRCALPHA)
    elif ScaleType == "fit":
        Ratio = min(Width / ImgWidth, Height / ImgHeight)
        Result = _Scale(Img, (max(1, int(ImgWidth * Ratio)), max(1, int(ImgHeight * Ratio))))
    elif ScaleType == "crop":
        Ratio = max(Width / ImgWidth, Height / ImgHeight)
        Scaled = _Scale(Img, (math.ceil(ImgWidth * Ratio), math.ceil(ImgHeight * Ratio)))
        CropRect = pygame.Rect((Scaled.get_width() - Width) // 2, (Scaled.get_height() - Height) // 2, Width, Height)
        Result = Scaled.subsurface(CropRect).copy()
    else:
        Result = _Scale(Img, Size)

    # Format de l'écran : le blit est bien plus rapide
    Converted = Display.Optimize(Result)
    if Converted is not Result:
        Result = Converted
    elif Result is Img:
        Result = Result.copy()
    if Color[:3] != (255, 255, 255):
        Result.fill((*Color[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
    if Transparency > 0:
        Result.set_alpha(int((1.0 - Transparency) * 255))
    return Result


def _Scale(Img : pygame.Surface, Size : tuple[int, int]) -> pygame.Surface:
    if Img.get_size() == tuple(Size):
        return Img
    try:
        return pygame.transform.smoothscale(Img, Size)
    except ValueError:
        # smoothscale n'accepte que les surfaces 24 / 32 bits
        return pygame.transform.scale(Img, Size)
