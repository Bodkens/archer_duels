"""Arrow projectile: flies in an arc, sticks on terrain, damages on a direct hit."""

import math

import pygame

from core import config as C
from core.assets import load_scaled
from core.weapons import ARROW
from core.weapons.projectile import Projectile


class Arrow(Projectile):
    kind = ARROW

    def __init__(self, start, vel, weapon, shooter):
        super().__init__(start, vel, weapon, shooter)
        self._image = (load_scaled(C.ARROW_IMAGE, C.ARROW_DRAW_SIZE)
                       if C.ARROW_IMAGE else None)

    # Arrow keeps the default outcomes ("archer" / "terrain") and has no fuse.

    def draw(self, screen):
        if self._image is not None:
            rotated = pygame.transform.rotate(self._image,
                                              -math.degrees(self.angle))
            screen.blit(rotated, rotated.get_rect(center=(self.x, self.y)))
            return
        # Oriented shaft with a point and fletching.
        L = self.weapon.size
        dx = math.cos(self.angle) * L
        dy = math.sin(self.angle) * L
        pygame.draw.line(screen, self.weapon.color,
                         (self.x - dx, self.y - dy),
                         (self.x + dx, self.y + dy), 3)
        tip = (self.x + dx, self.y + dy)
        left = (self.x + dx * 0.45 - dy * 0.22, self.y + dy * 0.45 + dx * 0.22)
        right = (self.x + dx * 0.45 + dy * 0.22, self.y + dy * 0.45 - dx * 0.22)
        pygame.draw.polygon(screen, (235, 235, 225), [tip, left, right])
