"""
Surface de la fenêtre utilisée par la GUI.
Avec pygame.Window (Application), pygame.display.get_surface() renvoie None : l'Application enregistre ici sa surface.
Dans une boucle maison avec pygame.display.set_mode, rien à faire : on retombe sur pygame.display.get_surface().
"""
import pygame

_Surface : pygame.Surface | None = None


def SetSurface(Surface : pygame.Surface | None):
    global _Surface
    _Surface = Surface


def GetSurface() -> pygame.Surface | None:
    return _Surface if _Surface is not None else pygame.display.get_surface()


def GetSize() -> tuple[int, int] | None:
    Surface = GetSurface()
    return Surface.get_size() if Surface is not None else None


def Optimize(Surface : pygame.Surface) -> pygame.Surface:
    """Convertit au format de l'écran (blit bien plus rapide) si une fenêtre existe, sinon renvoie la surface telle quelle"""
    if GetSurface() is None:
        return Surface
    try:
        return Surface.convert_alpha()
    except pygame.error:
        return Surface
