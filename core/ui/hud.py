"""In-match HUD: HP bars, turn info, and the drag-aim trajectory preview."""

import pygame

from core import config as C
from core.assets import load_scaled
from core.weapons import aim_from_drag, velocity_from_angle_power, simulate_path, ARROW, BOMB
from .fonts import font, center_text

# Weapon kind -> configured artwork file (None => no icon, e.g. vector fallback).
_WEAPON_ICON_FILES = {ARROW: C.ARROW_IMAGE, BOMB: C.BOMB_IMAGE}


def _weapon_icon(kind):
    name = _WEAPON_ICON_FILES.get(kind)
    return load_scaled(name, C.HUD_ICON_SIZE) if name else None


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
    text = font(24, bold=True).render(info, True, C.COL_TEXT)
    tx, ty = C.SCREEN_W // 2 - 210, 24
    screen.blit(text, (tx, ty))
    # Show the weapon's picture (bomb/arrow) right after the label.
    icon = _weapon_icon(slot.weapon.kind)
    if icon:
        iy = ty + text.get_height() // 2 - icon.get_height() // 2
        screen.blit(icon, (tx + text.get_width() + 8, iy))

    if message:
        center_text(screen, message, 22, C.SCREEN_H - 28, C.COL_TEXT_DIM)


def draw_aim_indicator(screen, archer, mouse_pos, terrain, archers=None):
    start = archer.muzzle_pos()
    angle, power = aim_from_drag(start, mouse_pos)
    if power <= 0:
        return
    kind = archer.selected.weapon.kind
    vel = velocity_from_angle_power(angle, power, kind)

    pts, _, _ = simulate_path(start, vel, kind, terrain,
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
