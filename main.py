# catch_the_objects_pygame.py
# Updated: Eggs (5 caught = win), Dinosaur hits (3 = lose), Restart game, Win/Lose page with emojis

import pygame
import random
import math
import os
import sys

SCREEN_W, SCREEN_H = 800, 800
FPS = 60

PLAYER_SPEED = 6
FALL_SPEED_CHOICES = [2, 3, 4, 5, 6, 7, 8]
ANIMAL_COLLIDE_RADIUS = 40
ESSENTIAL_COLLIDE_RADIUS = 40
DROPLET_COLLIDE_RADIUS = 20

def load_image(name):
    path = os.path.join(os.path.dirname(__file__), name)
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except:
        print(f"IMAGE NOT FOUND: {name}")
        sys.exit()

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# --------- PLAYER ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, img_right, img_left):
        super().__init__()
        self.img_right = img_right
        self.img_left = img_left
        self.image = self.img_right
        self.rect = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H - 100))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, keys):
        if keys[pygame.K_RIGHT]:
            self.image = self.img_right
            self.pos.x += PLAYER_SPEED
        elif keys[pygame.K_LEFT]:
            self.image = self.img_left
            self.pos.x -= PLAYER_SPEED

        self.pos.x = max(50, min(SCREEN_W - 50, self.pos.x))
        self.rect.centerx = int(self.pos.x)

    def center_pos(self):
        return (self.rect.centerx, self.rect.centery)

# -------- FALLING ITEMS --------
class FallingObject(pygame.sprite.Sprite):
    def __init__(self, image, kind):
        super().__init__()
        self.image = image
        self.kind = kind
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(50, SCREEN_W - 50)
        self.rect.y = random.randint(-SCREEN_H // 2, -20)
        self.speed = random.choice(FALL_SPEED_CHOICES)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 50:
            self.reset_position()

# -------- MAIN ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Catch the Eggs")
    clock = pygame.time.Clock()

    # Load images
    bg = load_image("forest.png")
    man_r = load_image("man_right(1).png")
    man_l = load_image("man_left(1).png")
    dino_img = load_image("dino.png")
    egg_img = load_image("egg.png")

    # resize images
    def fit(img, maxw, maxh):
        w, h = img.get_size()
        scale = min(maxw / w, maxh / h, 1)
        if scale < 1:
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
        return img

    man_r = fit(man_r, 100, 120)
    man_l = fit(man_l, 100, 120)
    dino_img = fit(dino_img, 80, 80)
    egg_img = fit(egg_img, 60, 60)
    bg = pygame.transform.smoothscale(bg, (SCREEN_W, SCREEN_H))

    # player
    player = Player(man_r, man_l)
    player_group = pygame.sprite.GroupSingle(player)

    # dinosaurs (10)
    animals_group = pygame.sprite.Group()
    for _ in range(10):
        animals_group.add(FallingObject(dino_img, "dino"))

    # eggs (10)
    essentials_group = pygame.sprite.Group()
    for _ in range(10):
        essentials_group.add(FallingObject(egg_img, "egg"))

    # droplet (also egg)
    droplet = FallingObject(egg_img, "egg_life")
    droplet_group = pygame.sprite.GroupSingle(droplet)

    # GAME VARIABLES
    egg_caught = 0
    dino_hits = 0
    score = 0
    game_over = False

    # -------- FONT WITH EMOJI SUPPORT --------
    try:
        font = pygame.font.SysFont("Segoe UI Emoji", 26)
        big_font = pygame.font.SysFont("Segoe UI Emoji", 70)
        med_font = pygame.font.SysFont("Segoe UI Emoji", 36)
    except:
        # fallback if emoji font not available
        font = pygame.font.SysFont("Arial", 26)
        big_font = pygame.font.SysFont("Arial", 70)
        med_font = pygame.font.SysFont("Arial", 36)

    title = font.render("Catch the Eggs !!!", True, (0, 0, 0))

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # -------- RESTART GAME WHEN PRESS R ----------
            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    egg_caught = 0
                    dino_hits = 0
                    score = 0
                    game_over = False

                    for a in animals_group:
                        a.reset_position()
                    for e in essentials_group:
                        e.reset_position()
                    droplet.reset_position()

                    player.pos.x = SCREEN_W // 2
                    player.rect.centerx = SCREEN_W // 2

        # -------- NORMAL GAME UPDATE --------
        if not game_over:

            keys = pygame.key.get_pressed()
            player_group.update(keys)
            animals_group.update()
            essentials_group.update()
            droplet_group.update()

            # ---------- Dinosaur collision ----------
            for a in animals_group:
                if dist(a.rect.center, player.center_pos()) < ANIMAL_COLLIDE_RADIUS:
                    a.reset_position()
                    dino_hits += 1
                    score -= 10

                    if dino_hits >= 3:
                        game_over = True

            # ---------- Egg collision ----------
            for e in essentials_group:
                if dist(e.rect.center, player.center_pos()) < ESSENTIAL_COLLIDE_RADIUS:
                    e.reset_position()
                    egg_caught += 1
                    score += 10

                    if egg_caught >= 5:
                        game_over = True

            # ---------- Droplet egg ----------
            d = droplet_group.sprite
            if dist(d.rect.center, player.center_pos()) < DROPLET_COLLIDE_RADIUS:
                droplet.reset_position()
                egg_caught += 1
                score += 5

                if egg_caught >= 5:
                    game_over = True

        # -------- DRAW EVERYTHING --------
        screen.blit(bg, (0, 0))
        screen.blit(title, (20, 10))

        animals_group.draw(screen)
        essentials_group.draw(screen)
        droplet_group.draw(screen)
        player_group.draw(screen)

        # HUD with emojis
        hud = font.render(
            f"Eggs: {egg_caught}/5    Dino Hits: {dino_hits}/3    Score: {score}",
            True, (0, 0, 0)
        )
        screen.blit(hud, (20, SCREEN_H - 40))

        # -------- GAME OVER / WIN PAGE --------
        if game_over:
            screen.fill((255, 255, 255))  # clean white page

            if egg_caught >= 5:
                msg = "YOU WIN!"
                color = (0, 180, 0)
                emoji_line = f"Eggs Caught: {egg_caught}   Dino Hits: {dino_hits}"
            else:
                msg = "GAME OVER "
                color = (200, 0, 0)
                emoji_line = f"Eggs Caught: {egg_caught}    Dino Hits: {dino_hits} "

            # Render text
            msg_surf = big_font.render(msg, True, color)
            emoji_surf = med_font.render(emoji_line, True, (0, 0, 0))
            score_surf = med_font.render(f"Final Score: {score}", True, (0, 0, 0))
            restart_surf = med_font.render("Press R to Restart", True, (50, 50, 50))

            # Center everything
            screen.blit(msg_surf, (SCREEN_W//2 - msg_surf.get_width()//2, SCREEN_H//2 - 150))
            screen.blit(emoji_surf, (SCREEN_W//2 - emoji_surf.get_width()//2, SCREEN_H//2 - 70))
            screen.blit(score_surf, (SCREEN_W//2 - score_surf.get_width()//2, SCREEN_H//2 + 10))
            screen.blit(restart_surf, (SCREEN_W//2 - restart_surf.get_width()//2, SCREEN_H//2 + 80))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
