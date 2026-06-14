"""Base projectile sprite: shared flight integration and collision handling.

Concrete weapons (Arrow, Bomb) live in ``core.sprites`` and customise the
outcome of an impact and how they are drawn. The physics numbers come straight
from ``core.config`` so behaviour is identical to the original game."""

import math

import pygame

from core import config as C
from .physics import step_physics, _out_of_field


class Projectile(pygame.sprite.Sprite):
    # Subclasses set this so step_physics picks the right integration.
    kind = None

    def __init__(self, start, vel, weapon, shooter):
        super().__init__()
        self.x, self.y = start
        self.vx, self.vy = vel
        self.weapon = weapon
        self.shooter = shooter
        self.alive = True
        # Resolved on impact, consumed by the Match:
        self.outcome = "flying"     # flying | terrain | archer | exploded | out
        self.hit_archer = None
        self.impact = None
        self.angle = math.atan2(self.vy, self.vx)
        # Minimal sprite bookkeeping (drawing is custom; rect keeps groups happy).
        self.image = None
        self.rect = pygame.Rect(int(self.x), int(self.y), 1, 1)

    # --- Hooks overridden by subclasses ---
    def on_archer_hit(self):
        """Outcome string when the projectile strikes an archer."""
        return "archer"

    def on_terrain_hit(self):
        """Outcome string when the projectile strikes terrain."""
        return "terrain"

    def tick_fuse(self, dt):
        """Optional per-frame timer (the bomb self-detonates)."""

    # --- Flight ---
    def update(self, dt, terrain, archers):
        # Subdivide so a fast shot cannot tunnel through thin terrain.
        nsub = max(1, int(math.hypot(self.vx, self.vy) * dt / (C.TILE * 0.5)) + 1)
        sub = dt / nsub
        for _ in range(nsub):
            (self.x, self.y), (self.vx, self.vy) = step_physics(
                (self.x, self.y), (self.vx, self.vy), self.kind, sub)
            self.angle = math.atan2(self.vy, self.vx)
            self.rect.topleft = (int(self.x), int(self.y))

            if _out_of_field((self.x, self.y)):
                self._finish("out")
                return

            for a in archers:
                if a is self.shooter or a.hp <= 0:
                    continue
                if a.hit_test((self.x, self.y)):
                    self.hit_archer = a
                    self._finish(self.on_archer_hit())
                    return

            if terrain.solid_at(self.x, self.y):
                self._finish(self.on_terrain_hit())
                return

        self.tick_fuse(dt)

    def _finish(self, outcome):
        self.alive = False
        self.outcome = outcome
        self.impact = (self.x, self.y)
        self.kill()  # remove from any sprite groups

    # --- Drawing ---
    def draw(self, screen):
        raise NotImplementedError
