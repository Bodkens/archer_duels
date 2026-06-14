"""Font cache and a small centered-text helper."""

import pygame

from core import config as C

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _fonts[key]


def center_text(screen, text, size, y, color=C.COL_TEXT, bold=False):
    surf = font(size, bold).render(text, True, color)
    rect = surf.get_rect(center=(C.SCREEN_W // 2, y))
    screen.blit(surf, rect)
    return rect
