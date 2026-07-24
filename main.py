import pygame
from Object.GuiAttribute.Udim import Udim, Udim2
from Object.GuiAttribute.Vector2 import Vector2
from Object.GuiObject import GuiObject
from Object.Frame import Frame
from Object.Labels.TextLabel import TextLabel
from Object.Button.TextButton import TextButton


# ---- Une classe minimale qui hérite de GuiObject, juste pour tester le rect qui bouge ----
class Rect(GuiObject):
    def __init__(self, color=(255, 0, 0)):
        super().__init__()
        self.Name = "Rect"
        self.Color = color

    def _Draw(self, Surface: pygame.Surface):
        rect = self.GetRect()
        pygame.draw.rect(Surface, self.Color, rect)
        pygame.draw.rect(Surface, (0, 0, 0), rect, 2)


# ---- Compteur global pour voir combien de fois on recalcule (vérif dirty) ----
recompute_count = 0
_original_recompute = GuiObject._Recompute

def _counted_recompute(self):
    global recompute_count
    recompute_count += 1
    _original_recompute(self)

GuiObject._Recompute = _counted_recompute


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # ---- Racine : représente l'écran ----
    root = GuiObject()
    root.Name = "Root"
    root.Size = Udim2(1, 0, 1, 0)

    # ---- Frame principale, 60% de l'écran, centrée ----
    frame = Frame()
    frame.Name = "MainFrame"
    frame.Size = Udim2(0.6, 0, 0.6, 0)
    frame.Position = Udim2(0.5, 0, 0.5, 0)
    frame.AnchorPoint = Vector2(0.5, 0.5)
    frame.BackgroundColor3 = (40, 40, 45)
    frame.BackgroundTransparency = 0.0
    frame.BorderColor3 = (200, 200, 200)
    frame.BorderSizePixel = 2
    root.AddChild(frame)

    # ---- Titre en haut de la Frame ----
    title = TextLabel()
    title.Name = "Title"
    title.Text = "Menu Principal"
    title.TextColor3 = (255, 255, 255)
    title.TextSize = 32
    title.Size = Udim2(1, 0, 0, 50)
    title.Position = Udim2(0, 0, 0, 0)
    title.BackgroundTransparency = 1.0  # pas de fond, juste le texte
    frame.AddChild(title)

    # ---- TextButton, juste affiché, pas d'interaction pour l'instant ----
    button = TextButton()
    button.Name = "PlayButton"
    button.Text = "Jouer"
    button.TextColor3 = (255, 255, 255)
    button.TextSize = 24
    button.Size = Udim2(0.5, 0, 0, 60)
    button.Position = Udim2(0.5, 0, 0.5, 0)
    button.AnchorPoint = Vector2(0.5, 0.5)
    button.BackgroundColor3 = (70, 130, 200)
    button.BackgroundTransparency = 0.0
    frame.AddChild(button)

    # ---- Petit carré vert en offset pixel pur, pour tester le déplacement / update ----
    mover = Rect(color=(50, 200, 50))
    mover.Name = "Mover"
    mover.Size = Udim2(0, 40, 0, 40)
    mover.Position = Udim2(0, 100, 0, 100)
    root.AddChild(mover)

    running = True
    frame_n = 0
    while running:
        dt = clock.tick(60) / 1000.0
        frame_n += 1
        global recompute_count
        recompute_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                root._MarkDirty()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    frame.Visible = not frame.Visible
                    print(f"Frame.Visible = {frame.Visible}")

        # Déplacement du carré vert avec les flèches
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        speed = 200 * dt
        if keys[pygame.K_LEFT]:
            move.x -= speed
        if keys[pygame.K_RIGHT]:
            move.x += speed
        if keys[pygame.K_UP]:
            move.y -= speed
        if keys[pygame.K_DOWN]:
            move.y += speed

        if move.length_squared() > 0:
            old = mover.Position
            new_offset_x = old.X.Offset + move.x
            new_offset_y = old.Y.Offset + move.y
            mover.SetPosition(Udim2(0, new_offset_x, 0, new_offset_y))

        root.Update(dt)

        screen.fill((30, 30, 30))
        root.Draw(screen)
        pygame.display.flip()

        if frame_n % 60 == 0:
            print(f"[frame {frame_n}] recomputes this frame: {recompute_count} | FPS: {clock.get_fps():.1f}")

    pygame.quit()


if __name__ == "__main__":
    main()