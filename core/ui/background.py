"""Shared static background used by every screen (splash, menu, match)."""

import pygame

from core import config as C
from core.assets import load_image

_scaled = None


def draw_background(screen):
    """Blit the static background image, scaled to the screen once and cached."""
    global _scaled
    if _scaled is None:
        img = load_image(C.BACKGROUND_IMAGE, alpha=False)
        _scaled = pygame.transform.scale(img, (C.SCREEN_W, C.SCREEN_H))
    screen.blit(_scaled, (0, 0))
