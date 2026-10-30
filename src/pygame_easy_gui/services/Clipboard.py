"""
Presse-papiers du système, avec repli sur un presse-papiers interne
quand celui du système n'est pas disponible (pas de fenêtre, pilote vidéo sans presse-papiers...).
pygame-ce : pygame.scrap.put_text / get_text (presse-papiers SDL) ; pygame : ancienne API pygame.scrap.put / get.
"""
import pygame

_Internal = ""
_HasTextApi = hasattr(pygame.scrap, "put_text")
_SystemFailed = False   # le dernier copier n'a pas pu aller dans le presse-papiers du système


def _Ready() -> bool:
    try:
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        return True
    except pygame.error:
        return False


def SetText(Text : str):
    global _Internal, _SystemFailed
    _Internal = Text
    _SystemFailed = True
    try:
        if _HasTextApi:
            pygame.scrap.put_text(Text)
            _SystemFailed = False
        elif _Ready():
            pygame.scrap.put(pygame.SCRAP_TEXT, Text.encode("utf-8"))
            _SystemFailed = False
    except pygame.error:
        pass


def GetText() -> str:
    if _SystemFailed:
        return _Internal
    try:
        if _HasTextApi:
            if pygame.scrap.has_text():
                return pygame.scrap.get_text().replace("\r\n", "\n")
        elif _Ready():
            Data = pygame.scrap.get(pygame.SCRAP_TEXT)
            if Data:
                return Data.decode("utf-8", errors="ignore").replace("\r\n", "\n").rstrip("\x00")
    except pygame.error:
        pass
    return _Internal
