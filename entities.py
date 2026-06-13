"""Archer entity: position, hp, walking, per-turn weapon, placeholder drawing."""

import random
import math
import pygame

import config as C
import weapons as W

BODY_W = 24
BODY_H = 40


class Archer:
    def __init__(self, x, y, color, is_ai=False, facing=1):
        self.x = float(x)      # feet center x
        self.y = float(y)      # feet (bottom) y
        self.hp = C.MAX_HP
        self.color = color
        self.is_ai = is_ai
        self.facing = facing
        self.weapon = W.WEAPONS[random.choice(W.ALL_KINDS)]
        self.moved_distance = 0.0

    # --- Geometry ---
    @property
    def rect(self):
        return pygame.Rect(int(self.x - BODY_W / 2), int(self.y - BODY_H),
                           BODY_W, BODY_H)

    def muzzle_pos(self):
        return (self.x, self.y - BODY_H)

    def hit_test(self, point):
        return self.rect.collidepoint(point)

    def center(self):
        return (self.x, self.y - BODY_H / 2)

    def circle_overlap(self, cx, cy, radius_px):
        px, py = self.center()
        return math.hypot(px - cx, py - cy) <= radius_px

    # --- Movement ---
    def ground(self, terrain):
        self.y = terrain.surface_y(self.x)

    def walk(self, dx, terrain):
        """Move horizontally, limited per turn, stepping over slopes, then settle."""
        remaining = C.WALK_DISTANCE - self.moved_distance
        if remaining <= 0:
            return 0.0
        step = max(-remaining, min(remaining, dx))
        target_x = self.x + step
        target_x = max(BODY_W, min(C.SCREEN_W - BODY_W, target_x))

        ground_y = terrain.surface_y(target_x)
        # Block if the step would require climbing a tall wall.
        if ground_y < self.y - BODY_H * 0.6:
            return 0.0

        actual = abs(target_x - self.x)
        self.x = target_x
        self.y = ground_y
        self.moved_distance += actual
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        return actual

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def start_turn(self):
        self.moved_distance = 0.0
        # A fresh random weapon (spear or bomb) is rolled each turn.
        self.weapon = W.WEAPONS[random.choice(W.ALL_KINDS)]

    # --- Drawing (placeholder; swap rect for sprite later) ---
    def draw(self, screen, active=False):
        r = self.rect
        pygame.draw.rect(screen, self.color, r, border_radius=4)
        # Head
        head_r = 9
        head_c = (r.centerx, r.top - head_r + 2)
        pygame.draw.circle(screen, self.color, head_c, head_r)
        pygame.draw.circle(screen, (20, 20, 20), head_c, head_r, 2)
        # Facing indicator (a small "bow" nub)
        nub_x = r.centerx + self.facing * (BODY_W // 2)
        pygame.draw.circle(screen, (20, 20, 20), (nub_x, r.centery), 3)
        if active:
            pygame.draw.rect(screen, (255, 255, 255), r.inflate(8, 14), 2,
                             border_radius=6)
