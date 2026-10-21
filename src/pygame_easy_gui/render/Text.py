import pygame

ELLIPSIS = "..."

_FontCache : dict[tuple, pygame.font.Font] = {}


def GetFont(FontName, Size : int) -> pygame.font.Font:
    Size = max(1, round(Size))   # une taille animée par un tween peut être décimale
    Key = (FontName, Size)
    if Key not in _FontCache:
        if not _FontCache:
            # Les polices deviennent invalides après pygame.quit() (crash si réutilisées après un nouveau pygame.init())
            pygame.register_quit(_FontCache.clear)
        _FontCache[Key] = pygame.font.Font(FontName, Size)
    return _FontCache[Key]


def _SplitLongWord(Font : pygame.font.Font, Word : str, MaxWidth : float) -> list[str]:
    Parts = []
    Current = ""
    for Char in Word:
        if Current and Font.size(Current + Char)[0] > MaxWidth:
            Parts.append(Current)
            Current = Char
        else:
            Current += Char
    Parts.append(Current)
    return Parts


def WrapText(Font : pygame.font.Font, Text : str, MaxWidth : float) -> list[str]:
    """Découpe le texte en lignes qui tiennent dans MaxWidth (mot par mot, puis lettre par lettre si un mot est trop long)"""
    Lines = []
    for Paragraph in Text.split("\n"):
        Current = ""
        for Word in Paragraph.split(" "):
            Candidate = f"{Current} {Word}" if Current else Word
            if Font.size(Candidate)[0] <= MaxWidth:
                Current = Candidate
                continue
            if Current:
                Lines.append(Current)
            if Font.size(Word)[0] <= MaxWidth:
                Current = Word
            else:
                Parts = _SplitLongWord(Font, Word, MaxWidth)
                Lines.extend(Parts[:-1])
                Current = Parts[-1]
        Lines.append(Current)
    return Lines


def Ellipsize(Font : pygame.font.Font, Line : str, MaxWidth : float, Force : bool = False) -> str:
    """Coupe la ligne et ajoute "..." si elle dépasse MaxWidth (ou toujours si Force)"""
    if not Force and Font.size(Line)[0] <= MaxWidth:
        return Line
    if Font.size(ELLIPSIS)[0] > MaxWidth:
        return ""
    while Line and Font.size(Line + ELLIPSIS)[0] > MaxWidth:
        Line = Line[:-1]
    return Line + ELLIPSIS


def LayoutLines(Font : pygame.font.Font, Text : str, Width : float, Height : float, Wrapped : bool, Truncate : str) -> list[str]:
    Lines = WrapText(Font, Text, Width) if Wrapped else Text.split("\n")
    if Truncate != "atend":
        return Lines

    MaxLines = max(1, int(Height // Font.get_linesize()))
    if len(Lines) > MaxLines:
        Lines = Lines[:MaxLines]
        Lines[-1] = Ellipsize(Font, Lines[-1], Width, Force=True)
    return [Ellipsize(Font, Line, Width) for Line in Lines]


def Fits(Font : pygame.font.Font, Text : str, Width : float, Height : float, Wrapped : bool) -> bool:
    Lines = WrapText(Font, Text, Width) if Wrapped else Text.split("\n")
    if len(Lines) * Font.get_linesize() > Height:
        return False
    return all(Font.size(Line)[0] <= Width for Line in Lines)


def FindScaledSize(FontName, Text : str, Width : float, Height : float, Wrapped : bool, MinSize : int = 1, MaxSize : int = 100) -> int:
    """Plus grande taille de police (entre MinSize et MaxSize) pour laquelle le texte tient dans la zone"""
    Low, High, Best = MinSize, MaxSize, MinSize
    while Low <= High:
        Mid = (Low + High) // 2
        if Fits(GetFont(FontName, Mid), Text, Width, Height, Wrapped):
            Best = Mid
            Low = Mid + 1
        else:
            High = Mid - 1
    return Best


def RenderLines(Font : pygame.font.Font, Lines : list[str], Color, XAlignment : str) -> pygame.Surface:
    Rendered = [Font.render(Line, True, Color) for Line in Lines]
    Width = max((Surf.get_width() for Surf in Rendered), default=0)
    LineSize = Font.get_linesize()

    Result = pygame.Surface((max(1, Width), max(1, LineSize * len(Rendered))), pygame.SRCALPHA)
    for Index, Surf in enumerate(Rendered):
        if XAlignment == "left":
            X = 0
        elif XAlignment == "right":
            X = Width - Surf.get_width()
        else:
            X = (Width - Surf.get_width()) // 2
        Result.blit(Surf, (X, Index * LineSize))
    return Result
