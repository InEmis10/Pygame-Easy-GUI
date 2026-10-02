class Color3:
    def __init__(self, R : int, G : int, B : int):
        self.R, self.G, self.B = R,G,B

    @classmethod
    def fromRgb(cls, r, g, b):
        return cls(r, g, b)

    @classmethod
    def fromHex(cls, string : str):
        """Crée une couleur depuis "#rrggbb" ou "#rgb" (le # est facultatif, casse libre).
        Format court : chaque chiffre est doublé, "#f80" == "#ff8800"."""
        if not isinstance(string, str):
            raise TypeError(f"fromHex attend une chaîne, reçu : {type(string).__name__}")

        digits = string.strip().removeprefix("#")
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        if len(digits) != 6:
            raise ValueError(f"couleur hexadécimale invalide : {string!r} (attendu #rrggbb ou #rgb)")

        # Vérification explicite : int(x, 16) accepterait aussi "+f" ou " f".
        if any(c not in "0123456789abcdefABCDEF" for c in digits):
            raise ValueError(f"couleur hexadécimale invalide : {string!r} (caractère non hexadécimal)")

        r, g, b = (int(digits[i:i + 2], 16) for i in (0, 2, 4))
        return cls(r, g, b)

    def ToPygame(self) -> tuple[int, int, int]:
        """Format attendu par pygame (fill, draw.rect, font.render) : tuple d'entiers 0–255."""
        return (self.R, self.G, self.B)

    def __eq__(self, other):
        if not isinstance(other, Color3):
            return NotImplemented
        return (self.R == other.R) and (self.G == other.G) and (self.B == other.B)

    def __repr__(self):
        return f"Color3({self.R}, {self.G}, {self.B})"

    def __hash__(self):
        return hash((self.R, self.G, self.B))
