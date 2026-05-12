"""
╔═══════════════════════════════════════════╗
║         PYTHOOGLE DINO  🦕                ║
║   A Python clone of the Chrome Dino game  ║
╚═══════════════════════════════════════════╝

Controls (Keyboard):
  SPACE / UP  — Jump
  DOWN        — Duck
  R           — Restart after game over

Controls (Touch / Mouse — Mobile friendly):
  Tap top half of screen  — Jump
  Hold bottom half        — Duck
  Tap anywhere on Game Over — Restart

Requirements: pip install pygame
"""

import pygame
import random
import sys

# ── Constants ─────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 900, 300
FPS          = 60
GROUND_Y     = 240

BG    = (247, 247, 247)
INK   = (35,  35,  35)
GRAY  = (180, 180, 180)
LGRAY = (210, 210, 210)
WHITE = (247, 247, 247)

GRAVITY  = 0.85
JUMP_VEL = -17
SPD_INIT = 7.0
SPD_MAX  = 18.0
SPD_INC  = 0.0035
DINO_X   = 80

# ── Helpers ───────────────────────────────────────────────────────────────────

def rrect(surf, color, rect, r=5):
    pygame.draw.rect(surf, color, rect, border_radius=r)

def text(surf, msg, size, x, y, color=INK, center=False):
    font = pygame.font.SysFont("monospace", size, bold=True)
    img  = font.render(msg, True, color)
    rc   = img.get_rect()
    if center:
        rc.center = (x, y)
    else:
        rc.topleft = (x, y)
    surf.blit(img, rc)

# ── Dino ──────────────────────────────────────────────────────────────────────

class Dino:
    W, H   = 44, 50
    DUCK_H = 28

    def __init__(self):
        self.reset()

    def reset(self):
        self.y        = GROUND_Y - self.H
        self.vy       = 0
        self.ducking  = False
        self.h        = self.H
        self.grounded = True
        self.tick     = 0
        self.leg      = 0
        self.blink    = 0

    @property
    def rect(self):
        return pygame.Rect(DINO_X + 5, self.y + 4, self.W - 10, self.h - 6)

    def jump(self):
        if self.grounded:
            self.vy       = JUMP_VEL
            self.grounded = False
            self.ducking  = False
            self.h        = self.H

    def set_duck(self, on):
        self.ducking = on
        self.h = self.DUCK_H if on else self.H

    def update(self):
        if not self.grounded:
            self.vy += GRAVITY
            self.y  += self.vy
            floor = GROUND_Y - self.h
            if self.y >= floor:
                self.y        = floor
                self.vy       = 0
                self.grounded = True
        self.tick += 1
        if self.tick % 7 == 0:
            self.leg = 1 - self.leg
        self.blink = max(0, self.blink - 1)
        if random.random() < 0.005:
            self.blink = 6

    def draw(self, surf):
        x, y = DINO_X, int(self.y)
        c = INK

        if self.ducking:
            rrect(surf, c, (x, y + 8,  46, 20), 4)
            rrect(surf, c, (x + 28, y, 22, 20), 4)
            pygame.draw.circle(surf, WHITE, (x + 44, y + 6), 4)
            if not self.blink:
                pygame.draw.circle(surf, c, (x + 45, y + 7), 2)
            else:
                pygame.draw.line(surf, c, (x+40, y+6), (x+48, y+6), 2)
            lo = (6, 0) if self.leg == 0 else (0, 6)
            pygame.draw.rect(surf, c, (x + 8,  y - lo[0], 8, 10 + lo[0]))
            pygame.draw.rect(surf, c, (x + 22, y - lo[1], 8, 10 + lo[1]))
        else:
            pygame.draw.polygon(surf, c, [
                (x + 2,  y + 26),
                (x - 10, y + 18),
                (x - 16, y + 24),
                (x + 2,  y + 34),
            ])
            rrect(surf, c, (x + 2,  y + 20, 30, 30), 5)
            pygame.draw.rect(surf, c, (x + 18, y + 10, 12, 16))
            rrect(surf, c, (x + 14, y,       26, 24), 5)
            pygame.draw.rect(surf, c, (x + 36, y + 10, 8, 10))
            pygame.draw.rect(surf, c, (x + 22, y + 30, 10, 6))
            ex, ey = x + 30, y + 7
            pygame.draw.circle(surf, WHITE, (ex, ey), 5)
            if not self.blink:
                pygame.draw.circle(surf, c, (ex + 1, ey + 1), 3)
            else:
                pygame.draw.line(surf, c, (ex - 4, ey), (ex + 4, ey), 2)
            if self.grounded:
                la, lb = (8, 0) if self.leg == 0 else (0, 8)
            else:
                la = lb = 4
            pygame.draw.rect(surf, c, (x + 8,  y + 46, 10, 4 + la))
            pygame.draw.rect(surf, c, (x + 20, y + 46, 10, 4 + lb))
            pygame.draw.rect(surf, c, (x + 4,  y + 50 + la, 14, 5))
            pygame.draw.rect(surf, c, (x + 16, y + 50 + lb, 14, 5))


# ── Cactus ────────────────────────────────────────────────────────────────────

CACTUS_TYPES = [
    dict(tw=12, th=50, arms=[(-13, 18, 13, 7), (12, 14, 13, 7)]),
    dict(tw=10, th=40, arms=[(-11, 16, 11, 6)]),
    dict(tw=14, th=56, arms=[(-15, 20, 15, 8), (14, 16, 15, 8)]),
]

class Cactus:
    def __init__(self):
        cfg         = random.choice(CACTUS_TYPES)
        self.tw     = cfg["tw"]
        self.th     = cfg["th"]
        self.arms   = cfg["arms"]
        self.double = random.random() < 0.30
        self.x      = float(WIN_W + random.randint(0, 180))

    @property
    def rect(self):
        total = self.tw * (2 if self.double else 1) + (8 if self.double else 0)
        return pygame.Rect(int(self.x), GROUND_Y - self.th + 4, total, self.th - 4)

    def update(self, spd):
        self.x -= spd

    def draw(self, surf):
        self._one(surf, int(self.x))
        if self.double:
            self._one(surf, int(self.x) + self.tw + 8)

    def _one(self, surf, x):
        y = GROUND_Y - self.th
        rrect(surf, INK, (x, y, self.tw, self.th), 3)
        pygame.draw.polygon(surf, INK, [
            (x, y), (x + self.tw, y), (x + self.tw // 2, y - 8)])
        for ax, ay, aw, ah in self.arms:
            rx = x + self.tw // 2 + ax
            ry = y + ay
            rrect(surf, INK, (rx, ry, aw, ah), 3)
            pygame.draw.polygon(surf, INK, [
                (rx, ry), (rx + aw, ry), (rx + aw // 2, ry - 6)])

    @property
    def gone(self):
        return self.x + self.tw + 20 < 0


# ── Bird ──────────────────────────────────────────────────────────────────────

class Bird:
    HEIGHTS = [GROUND_Y - 70, GROUND_Y - 115, GROUND_Y - 155]

    def __init__(self):
        self.x   = float(WIN_W + random.randint(0, 250))
        self.y   = random.choice(self.HEIGHTS)
        self.fl  = 0
        self.fld = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x) + 4, self.y + 4, 44, 22)

    def update(self, spd):
        self.x  -= spd
        self.fl += self.fld * 3
        if abs(self.fl) > 10:
            self.fld *= -1

    def draw(self, surf):
        x, y = int(self.x), self.y
        pygame.draw.ellipse(surf, INK, (x + 8, y + 8, 32, 16))
        pygame.draw.circle(surf, INK, (x + 44, y + 12), 8)
        pygame.draw.polygon(surf, GRAY, [
            (x + 50, y + 11), (x + 60, y + 13), (x + 50, y + 15)])
        wy = y + 8 + self.fl
        pygame.draw.ellipse(surf, INK, (x,      wy, 24, 10))
        pygame.draw.ellipse(surf, INK, (x + 20, wy - 2, 24, 10))
        pygame.draw.circle(surf, WHITE, (x + 46, y + 11), 3)
        pygame.draw.circle(surf, INK,   (x + 47, y + 11), 1)

    @property
    def gone(self):
        return self.x + 64 < 0


# ── Cloud ─────────────────────────────────────────────────────────────────────

class Cloud:
    def __init__(self, start_offscreen=True):
        self.x = float(WIN_W + random.randint(0, 300)) if start_offscreen \
                 else float(random.randint(0, WIN_W))
        self.y = random.randint(30, 110)
        self.w = random.randint(60, 110)

    def update(self, spd):
        self.x -= spd * 0.28

    def draw(self, surf):
        x, y, w = int(self.x), self.y, self.w
        pygame.draw.ellipse(surf, LGRAY, (x,             y + 10, w,         18))
        pygame.draw.ellipse(surf, LGRAY, (x + 10,        y,      int(w*.6), 24))
        pygame.draw.ellipse(surf, LGRAY, (x + int(w*.4), y + 4,  int(w*.5), 18))

    @property
    def gone(self):
        return self.x + 130 < 0


# ── Ground dots ───────────────────────────────────────────────────────────────

class GroundDots:
    def __init__(self):
        self.dots = [(float(random.randint(-WIN_W, WIN_W * 2)),
                      random.choice([2, 2, 3, 4])) for _ in range(50)]

    def update(self, spd):
        self.dots = [(x - spd, h) for x, h in self.dots]
        while len(self.dots) < 50:
            self.dots.append((float(WIN_W + random.randint(0, 400)),
                              random.choice([2, 2, 3, 4])))
        self.dots = [(x, h) for x, h in self.dots if x > -20]

    def draw(self, surf):
        for x, h in self.dots:
            pygame.draw.rect(surf, LGRAY, (int(x), GROUND_Y + 2, h + 1, h))


# ── Touch Buttons ─────────────────────────────────────────────────────────────

class TouchButtons:
    """
    Two large transparent tap zones at the bottom of the screen:
      LEFT half  → Jump
      RIGHT half → Duck (hold)
    Also draws subtle hint labels so the player knows where to tap.
    """
    BTN_H = 80   # height of touch strip at the bottom

    def draw(self, surf):
        # semi-transparent strip
        strip = pygame.Surface((WIN_W, self.BTN_H), pygame.SRCALPHA)
        strip.fill((0, 0, 0, 18))
        surf.blit(strip, (0, WIN_H - self.BTN_H))

        # divider
        pygame.draw.line(surf, LGRAY,
                         (WIN_W // 2, WIN_H - self.BTN_H),
                         (WIN_W // 2, WIN_H), 1)

        # labels
        font = pygame.font.SysFont("monospace", 13, bold=True)
        lbl_jump = font.render("▲  TAP TO JUMP", True, GRAY)
        lbl_duck = font.render("HOLD TO DUCK  ▼", True, GRAY)
        surf.blit(lbl_jump, lbl_jump.get_rect(
            center=(WIN_W // 4,     WIN_H - self.BTN_H // 2)))
        surf.blit(lbl_duck, lbl_duck.get_rect(
            center=(WIN_W * 3 // 4, WIN_H - self.BTN_H // 2)))

    def in_jump_zone(self, pos):
        x, y = pos
        return x < WIN_W // 2 and y >= WIN_H - self.BTN_H

    def in_duck_zone(self, pos):
        x, y = pos
        return x >= WIN_W // 2 and y >= WIN_H - self.BTN_H


# ── Game ──────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        self.win   = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Pythoogle Dino  🦕  — A Python clone of the Chrome Dino game")
        self.clock = pygame.time.Clock()
        self.hi    = 0
        self.btns  = TouchButtons()
        self.reset()

    def reset(self):
        self.dino      = Dino()
        self.obstacles = []
        self.clouds    = [Cloud(start_offscreen=False) for _ in range(4)]
        self.gdots     = GroundDots()
        self.spd       = SPD_INIT
        self.score     = 0.0
        self.over      = False
        self.started   = False
        self.sp_timer  = 0
        self.milestone = 100
        self.flash     = 0
        self.duck_held = False   # tracks whether duck touch is held

    # ── events ────────────────────────────────────────────────────────────────

    def handle(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ──────────────────────────────────────────────────────
            if ev.type == pygame.KEYDOWN:
                k = ev.key
                if k in (pygame.K_SPACE, pygame.K_UP):
                    if self.over:
                        self.reset()
                    else:
                        self.started = True
                        self.dino.jump()
                if k == pygame.K_r and self.over:
                    self.reset()
                if k == pygame.K_DOWN:
                    self.started = True
                    self.dino.set_duck(True)
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_DOWN:
                    self.dino.set_duck(False)

            # ── Mouse / Touch — press ─────────────────────────────────────────
            if ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos
                if self.over:
                    self.reset()
                elif self.btns.in_duck_zone(pos):
                    self.started   = True
                    self.duck_held = True
                    self.dino.set_duck(True)
                elif self.btns.in_jump_zone(pos):
                    self.started = True
                    self.dino.jump()
                else:
                    # tap anywhere above the strip → jump (handy on desktop too)
                    self.started = True
                    self.dino.jump()

            # ── Mouse / Touch — release ───────────────────────────────────────
            if ev.type == pygame.MOUSEBUTTONUP:
                if self.duck_held:
                    self.duck_held = False
                    self.dino.set_duck(False)

            # ── Finger touch events (pygame 2 on Android / some backends) ─────
            if ev.type == pygame.FINGERDOWN:
                # Convert normalised coords to pixels
                fx = int(ev.x * WIN_W)
                fy = int(ev.y * WIN_H)
                pos = (fx, fy)
                if self.over:
                    self.reset()
                elif self.btns.in_duck_zone(pos):
                    self.started   = True
                    self.duck_held = True
                    self.dino.set_duck(True)
                else:
                    self.started = True
                    self.dino.jump()

            if ev.type == pygame.FINGERUP:
                if self.duck_held:
                    self.duck_held = False
                    self.dino.set_duck(False)

    # ── update ────────────────────────────────────────────────────────────────

    def update(self):
        if not self.started or self.over:
            return

        self.spd    = min(SPD_MAX, self.spd + SPD_INC)
        self.score += self.spd * 0.038

        if int(self.score) >= self.milestone:
            self.flash     = 55
            self.milestone += 100
        if self.flash > 0:
            self.flash -= 1

        self.dino.update()

        self.sp_timer += 1
        interval = max(42, int(92 - self.score * 0.05))
        if self.sp_timer >= interval:
            self.sp_timer = 0
            if self.score > 280 and random.random() < 0.36:
                self.obstacles.append(Bird())
            else:
                self.obstacles.append(Cactus())

        for c in self.clouds:
            c.update(self.spd)
        self.clouds = [c for c in self.clouds if not c.gone]
        if len(self.clouds) < 5 and random.random() < 0.012:
            self.clouds.append(Cloud())

        self.gdots.update(self.spd)

        for o in self.obstacles:
            o.update(self.spd)
            if o.rect.colliderect(self.dino.rect):
                self.over = True
                self.hi   = max(self.hi, int(self.score))
        self.obstacles = [o for o in self.obstacles if not o.gone]

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self):
        self.win.fill(BG)

        for c in self.clouds:
            c.draw(self.win)

        self.gdots.draw(self.win)
        pygame.draw.line(self.win, INK, (0, GROUND_Y), (WIN_W, GROUND_Y), 2)

        for o in self.obstacles:
            o.draw(self.win)

        self.dino.draw(self.win)

        # HUD
        text(self.win, f"HI {self.hi:05d}", 18, WIN_W - 210, 14, GRAY)
        text(self.win, f"{int(self.score):05d}", 18, WIN_W - 80, 14)

        # speed bar
        bw = int((self.spd - SPD_INIT) / (SPD_MAX - SPD_INIT) * 80)
        pygame.draw.rect(self.win, LGRAY, (18, 18, 80, 7), border_radius=3)
        if bw:
            pygame.draw.rect(self.win, INK, (18, 18, bw, 7), border_radius=3)
        text(self.win, "SPD", 11, 18, 28, GRAY)

        # milestone flash
        if self.flash > 0:
            alpha = min(255, self.flash * 6)
            fc = (0, max(0, 180 - (255 - alpha)), 80)
            text(self.win, f"+{self.milestone - 100}!", 22,
                 WIN_W // 2, 55, fc, center=True)

        # touch buttons (always visible so player knows the zones)
        self.btns.draw(self.win)

        if not self.started:
            self._screen_start()
        elif self.over:
            self._screen_over()

        pygame.display.flip()

    def _screen_start(self):
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((247, 247, 247, 170))
        self.win.blit(ov, (0, 0))
        text(self.win, "PYTHOOGLE DINO  \U0001f995", 34, WIN_W//2, 60,  center=True)
        text(self.win, "A Python clone of the Chrome Dino game", 15,
             WIN_W//2, 104, GRAY, center=True)
        text(self.win, "Keyboard:  SPACE / \u2191  Jump     \u2193  Duck", 13,
             WIN_W//2, 136, GRAY, center=True)
        text(self.win, "Touch:  Left half = Jump   Right half = Duck", 13,
             WIN_W//2, 158, GRAY, center=True)
        text(self.win, "Tap / Press SPACE to start!", 17,
             WIN_W//2, 192, center=True)

    def _screen_over(self):
        ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        ov.fill((247, 247, 247, 190))
        self.win.blit(ov, (0, 0))
        text(self.win, "GAME OVER", 40, WIN_W//2, 70,  center=True)
        text(self.win, f"Score: {int(self.score):,}     Best: {self.hi:,}",
             18, WIN_W//2, 130, GRAY, center=True)
        text(self.win, "Tap screen  or  press SPACE / R  to restart", 15,
             WIN_W//2, 168, center=True)

    # ── run ───────────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.handle()
            self.update()
            self.draw()
            self.clock.tick(FPS)


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        import pygame
    except ImportError:
        print("pygame not found.  Run:  pip install pygame")
        sys.exit(1)
    Game().run()
