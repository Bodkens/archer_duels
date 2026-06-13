"""Splash, menu, HUD, aim indicator and game-over screens."""

import pygame

import config as C
import weapons as W

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _fonts[key]


def _center_text(screen, text, size, y, color=C.COL_TEXT, bold=False):
    surf = font(size, bold).render(text, True, color)
    rect = surf.get_rect(center=(C.SCREEN_W // 2, y))
    screen.blit(surf, rect)
    return rect


def draw_splash(screen):
    draw_menu_background(screen, pygame.time.get_ticks() / 1000.0)
    _center_text(screen, C.TITLE, 84, C.SCREEN_H // 2 - 20, bold=True)
    _center_text(screen, "Bowmasters-style artillery duel", 26,
                 C.SCREEN_H // 2 + 50, C.COL_TEXT_DIM)


class Menu:
    def __init__(self):
        labels = [("Play", "ai"),
                  ("Quit", "quit")]
        self.buttons = []
        bw, bh, gap = 360, 64, 24
        total = len(labels) * bh + (len(labels) - 1) * gap
        y0 = C.SCREEN_H // 2 - total // 2 + 40
        for i, (label, action) in enumerate(labels):
            rect = pygame.Rect(0, 0, bw, bh)
            rect.center = (C.SCREEN_W // 2, y0 + i * (bh + gap) + bh // 2)
            self.buttons.append((rect, label, action))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, _, action in self.buttons:
                if rect.collidepoint(event.pos):
                    return action
        return None

    def draw(self, screen):
        draw_menu_background(screen, pygame.time.get_ticks() / 1000.0)
        _center_text(screen, C.TITLE, 72, C.SCREEN_H // 4, bold=True)
        mouse = pygame.mouse.get_pos()
        for rect, label, _ in self.buttons:
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(screen, C.COL_BUTTON_HOVER if hover else C.COL_BUTTON,
                             rect, border_radius=10)
            pygame.draw.rect(screen, (160, 175, 200), rect, 2, border_radius=10)
            surf = font(30, bold=True).render(label, True, C.COL_TEXT)
            screen.blit(surf, surf.get_rect(center=rect.center))


def _hp_bar(screen, archer, x, y, align_right=False):
    w, h = 240, 18
    if align_right:
        x -= w
    pygame.draw.rect(screen, C.COL_HP_BG, (x, y, w, h), border_radius=4)
    frac = archer.hp / C.MAX_HP
    col = C.COL_HP_GOOD if frac > 0.3 else C.COL_HP_LOW
    pygame.draw.rect(screen, col, (x, y, int(w * frac), h), border_radius=4)
    pygame.draw.rect(screen, (220, 220, 220), (x, y, w, h), 2, border_radius=4)
    label = font(20, bold=True).render(f"{archer.hp} HP", True, C.COL_TEXT)
    screen.blit(label, (x + 6, y - 24))


def draw_hud(screen, p1, p2, current, message):
    _hp_bar(screen, p1, 20, 26)
    _hp_bar(screen, p2, C.SCREEN_W - 20, 26, align_right=True)

    # Random weapon assigned for the current turn.
    slot = current.selected
    who = "AI" if current.is_ai else "Player"
    info = f"{who} turn  |  Random weapon: {slot.weapon.name}"
    screen.blit(font(24, bold=True).render(info, True, C.COL_TEXT),
                (C.SCREEN_W // 2 - 210, 24))

    if message:
        _center_text(screen, message, 22, C.SCREEN_H - 28, C.COL_TEXT_DIM)


def draw_aim_indicator(screen, archer, mouse_pos, terrain, archers=None):
    start = archer.muzzle_pos()
    angle, power = W.aim_from_drag(start, mouse_pos)
    if power <= 0:
        return
    kind = archer.selected.weapon.kind
    vel = W.velocity_from_angle_power(angle, power, kind)

    pts, _, _ = W.simulate_path(start, vel, kind, terrain,
                                archers=archers, ignore=archer,
                                max_points=160)
    # Dotted trajectory preview. It uses the exact same physics as the shot,
    # but stops before the final impact so the answer is not too obvious.
    visible_count = max(5, int(len(pts) * 0.78))
    for i, p in enumerate(pts[:visible_count]):
        if i % 2 == 0:
            pygame.draw.circle(screen, C.COL_AIM, (int(p[0]), int(p[1])), 2)

    # Power meter near the archer.
    frac = power / C.MAX_POWER
    bx, by = start[0] - 30, start[1] - 60
    pygame.draw.rect(screen, C.COL_HP_BG, (bx, by, 60, 8), border_radius=3)
    pygame.draw.rect(screen, C.COL_EXPLOSION, (bx, by, int(60 * frac), 8),
                     border_radius=3)


def draw_game_over(screen, winner_text):
    overlay = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    _center_text(screen, winner_text, 72, C.SCREEN_H // 2 - 30, bold=True)
    _center_text(screen, "Click or press any key to return to menu", 26,
                 C.SCREEN_H // 2 + 40, C.COL_TEXT_DIM)


def draw_confirm_exit(screen):
    overlay = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    box = pygame.Rect(0, 0, 520, 230)
    box.center = (C.SCREEN_W // 2, C.SCREEN_H // 2)
    pygame.draw.rect(screen, (30, 36, 48), box, border_radius=12)
    pygame.draw.rect(screen, (180, 195, 220), box, 2, border_radius=12)
    _center_text(screen, "Quit to menu?", 32, box.y + 56, C.COL_TEXT, bold=True)
    _center_text(screen, "Enter - quit     Esc - continue", 22,
                 box.y + 100, C.COL_TEXT_DIM)

    yes, no = confirm_exit_buttons()
    mouse = pygame.mouse.get_pos()
    for rect, label in ((yes, "Quit"), (no, "Stay")):
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, C.COL_BUTTON_HOVER if hover else C.COL_BUTTON,
                         rect, border_radius=8)
        pygame.draw.rect(screen, (160, 175, 200), rect, 2, border_radius=8)
        surf = font(24, bold=True).render(label, True, C.COL_TEXT)
        screen.blit(surf, surf.get_rect(center=rect.center))
    return yes, no


def confirm_exit_buttons():
    box = pygame.Rect(0, 0, 520, 230)
    box.center = (C.SCREEN_W // 2, C.SCREEN_H // 2)
    yes = pygame.Rect(box.x + 82, box.y + 150, 150, 48)
    no = pygame.Rect(box.right - 232, box.y + 150, 150, 48)
    return yes, no


def draw_menu_background(screen, t):
    top = (32, 47, 80)
    bottom = (92, 130, 150)
    for y in range(C.SCREEN_H):
        k = y / C.SCREEN_H
        col = tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3))
        pygame.draw.line(screen, col, (0, y), (C.SCREEN_W, y))

    pygame.draw.circle(screen, (244, 188, 87), (C.SCREEN_W - 170, 105), 52)
    for i in range(7):
        x = (i * 230 + int(t * (14 + i))) % (C.SCREEN_W + 160) - 80
        y = 95 + (i % 3) * 42
        pygame.draw.ellipse(screen, (238, 242, 232), (x, y, 90, 24))
        pygame.draw.ellipse(screen, (228, 235, 230), (x + 42, y - 8, 82, 28))

    for layer, color in enumerate(((67, 91, 94), (49, 74, 79), (36, 60, 65))):
        base = C.SCREEN_H - 170 + layer * 42
        points = [(-40, C.SCREEN_H), (-40, base)]
        for x in range(-40, C.SCREEN_W + 100, 120):
            peak = base - 70 - ((x // 120 + layer) % 3) * 24
            points.extend([(x + 60, peak), (x + 120, base)])
        points.append((C.SCREEN_W + 80, C.SCREEN_H))
        pygame.draw.polygon(screen, color, points)
