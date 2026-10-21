import pygame
from pygame_easy_gui.core.GuiObject import GuiObject
from pygame_easy_gui.render import ImageCache


class ImageLabel(GuiObject):
    """
    Affiche une image (chemin vers un fichier ou pygame.Surface).
    ScaleType : "stretch" (étire) | "fit" (tient entière, garde les proportions) | "crop" (remplit, coupe ce qui dépasse)
    ImageColor3 : teinte multipliée ((255, 255, 255) = aucune teinte)
    Les images sont chargées une seule fois et leurs versions redimensionnées sont partagées entre objets (voir Render/ImageCache).
    Si une pygame.Surface donnée en Image est modifiée après coup, appeler ReloadImage().
    """
    def __init__(self):
        super().__init__()
        self.Name = "ImageLabel"
        self.BackgroundColor3 = (255, 255, 255)
        self.BackgroundTransparency = 0.0
        self.Image = None
        self.ImageColor3 = (255, 255, 255)
        self.ImageTransparency = 0.0
        self.ScaleType = "stretch"

        self._ImageCacheKey = None
        self._ImageCacheSurface = None

    @staticmethod
    def _LoadImage(Source) -> pygame.Surface | None:
        return ImageCache.Load(Source)

    @property
    def Image(self):
        return self._Image

    @Image.setter
    def Image(self, Value):
        self._LoadImage(Value)   # erreur immédiate si le fichier n'existe pas
        self._Image = Value

    def ReloadImage(self):
        """Recharge l'image (fichier modifié sur le disque, ou Surface redessinée)"""
        ImageCache.Invalidate(self._GetImage())
        self._ImageCacheKey = None
        self._MarkRenderDirty()

    def _GetImage(self):
        return self.Image

    def _GetImageColor(self) -> tuple:
        return tuple(self.ImageColor3)

    def _GetImageRect(self) -> pygame.Rect:
        """Zone dans laquelle l'image est placée"""
        return self._GetPaddedRect()

    def _GetImageSurface(self, Size : tuple[int, int]) -> pygame.Surface | None:
        Source = self._GetImage()
        Color = self._GetImageColor()
        # Accès direct sans repasser par le cache partagé tant que rien ne change
        Key = (Source, Size, self.ScaleType, Color, self.ImageTransparency)
        if Key != self._ImageCacheKey:
            self._ImageCacheSurface = ImageCache.GetScaled(Source, Size, self.ScaleType.lower(), Color, self.ImageTransparency)
            self._ImageCacheKey = Key
        return self._ImageCacheSurface

    def _DrawImage(self, Surface : pygame.Surface):
        if self._GetImage() is None or self.ImageTransparency >= 1.0:
            return
        Rect = self._GetImageRect()
        if Rect.width <= 0 or Rect.height <= 0:
            return
        Result = self._GetImageSurface(Rect.size)
        if Result is not None:
            Surface.blit(Result, Result.get_rect(center=Rect.center))

    def _Draw(self, Surface : pygame.Surface):
        self._DrawBackground(Surface)
        self._DrawImage(Surface)
