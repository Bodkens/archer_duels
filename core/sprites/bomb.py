"""Bomb projectile: heavier arc, explodes on any contact or when the fuse runs out."""

import math

import pygame

from core import config as C
from core.assets import load_image
from core.weapons import BOMB
from core.weapons.projectile import Projectile


class Bomb(Projectile):
    kind = BOMB

    def __init__(self, start, vel, weapon, shooter):
        super().__init__(start, vel, weapon, shooter)
        self.fuse = C.BOMB_FUSE
        self._image = load_image(C.BOMB_IMAGE) if C.BOMB_IMAGE else None

    # A bomb detonates on any impact, not just a direct hit.
    def on_archer_hit(self):
        return "exploded"

    def on_terrain_hit(self):
        return "exploded"

    def tick_fuse(self, dt):
        self.fuse -= dt
        if self.fuse <= 0:
            self._finish("exploded")

    def draw(self, screen):
        if self._image is not None:
            screen.blit(self._image,
                        self._image.get_rect(center=(int(self.x), int(self.y))))
            return
        pygame.draw.circle(screen, self.weapon.color,
                           (int(self.x), int(self.y)), self.weapon.size)
        pygame.draw.circle(screen, (200, 60, 40),
                           (int(self.x), int(self.y)), self.weapon.size, 2)
        fuse_tip = (
            int(self.x - math.cos(self.angle) * 8),
            int(self.y - math.sin(self.angle) * 8),
        )
        pygame.draw.line(screen, (230, 160, 70), (int(self.x), int(self.y)),
                         fuse_tip, 2)
