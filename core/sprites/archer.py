"""Archer: position, hp, walking, per-turn weapon and animated drawing.

This is the shared base for the human Player and the AI Enemy. It is an
``AnimatedSprite``: when a spritesheet is supplied it plays frames, otherwise it
falls back to the hand-drawn vector archer in ``draw_vector``."""

import random
import math

import pygame

from core import config as C
from core.weapons import random_loadout, BOMB
from .animated_sprite import AnimatedSprite

BODY_W = 24
BODY_H = 40

# Spritesheet row per animation state.
ROW_IDLE_BOW = 0
ROW_IDLE_BOMB = 1
ROW_AIM_BOW = 2
ROW_AIM_BOMB = 3
ROW_MOVE = 4


class Archer(AnimatedSprite):
    def __init__(self, x, y, color, is_ai=False, facing=1, rows=None):
        # Scale every frame down to the archer's body size at load time.
        scaled = None
        if rows:
            scaled = [[pygame.transform.smoothscale(f, (BODY_W, BODY_H))
                       for f in row] for row in rows]
        super().__init__(rows=scaled, fps=C.SPRITE_ANIM_FPS)
        self.x = float(x)      # feet center x
        self.y = float(y)      # feet (bottom) y
        self.hp = C.MAX_HP
        self.color = color
        self.is_ai = is_ai
        self.facing = facing
        self.loadout = random_loadout()
        self.selected_idx = 0
        self.moved_distance = 0.0
        self.anim_t = random.random() * 10.0
        # Animation state, set each frame by the Match.
        self.aiming = False
        self.moving = False
        self.rect = self.body_rect()

    # --- Geometry ---
    def body_rect(self):
        return pygame.Rect(int(self.x - BODY_W / 2), int(self.y - BODY_H),
                           BODY_W, BODY_H)

    def muzzle_pos(self):
        return (self.x, self.y - BODY_H)

    def hit_test(self, point):
        return self.body_rect().collidepoint(point)

    def center(self):
        return (self.x, self.y - BODY_H / 2)

    def circle_overlap(self, cx, cy, radius_px):
        px, py = self.center()
        return math.hypot(px - cx, py - cy) <= radius_px

    # --- Weapons ---
    @property
    def selected(self):
        return self.loadout[self.selected_idx]

    def switch_weapon(self, direction):
        self.selected_idx = (self.selected_idx + direction) % len(self.loadout)

    def select_index(self, idx):
        if 0 <= idx < len(self.loadout):
            self.selected_idx = idx

    # --- Movement ---
    def ground(self, terrain):
        self.y = terrain.surface_y(self.x)
        self.rect = self.body_rect()

    def walk(self, dx, terrain):
        """Move horizontally, capped by the per-turn movement budget."""
        remaining = C.WALK_DISTANCE - self.moved_distance
        if remaining <= 0:
            return 0.0
        if abs(dx) > remaining:
            dx = math.copysign(remaining, dx)
        target_x = self.x + dx
        target_x = max(BODY_W, min(C.SCREEN_W - BODY_W, target_x))

        ground_y = terrain.surface_y(target_x)

        actual = abs(target_x - self.x)
        self.x = target_x
        self.y = ground_y
        self.moved_distance += actual
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        self.rect = self.body_rect()
        return actual

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def start_turn(self):
        self.moved_distance = 0.0
        self.selected_idx = random.randrange(len(self.loadout))

    def _current_row(self):
        """Pick the spritesheet row from weapon + aiming/moving state."""
        if self.moving:
            return ROW_MOVE
        is_bomb = self.selected.weapon.kind == BOMB
        if self.aiming:
            return ROW_AIM_BOMB if is_bomb else ROW_AIM_BOW
        return ROW_IDLE_BOMB if is_bomb else ROW_IDLE_BOW

    def update(self, dt):
        self.anim_t += dt
        self.row_index = self._current_row()
        self.animate(dt)
        self.rect = self.body_rect()

    # --- Drawing ---
    def draw(self, screen, active=False):
        if self.image is not None:
            img = self.image
            if self.facing < 0:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, self.body_rect())
        else:
            self.draw_vector(screen)
        if active:
            pygame.draw.rect(screen, (255, 255, 255),
                             self.body_rect().inflate(8, 14), 2, border_radius=6)

    def draw_vector(self, screen):
        r = self.body_rect()
        bob = math.sin(self.anim_t * 5.0) * 1.5
        hip = (r.centerx, r.bottom - 20 + bob)
        shoulder = (r.centerx, r.top + 13 + bob)
        foot_y = r.bottom
        leg_col = (35, 32, 36)
        arm_col = (230, 195, 145)
        bow_col = (96, 58, 32)
        string_col = (235, 230, 205)

        # Legs
        pygame.draw.line(screen, leg_col, hip, (r.centerx - 10, foot_y), 5)
        pygame.draw.line(screen, leg_col, hip, (r.centerx + 10, foot_y), 5)

        # Body cloak
        cloak = [
            (r.centerx - 13, r.top + 22 + bob),
            (r.centerx + 13, r.top + 22 + bob),
            (r.centerx + 10, r.bottom - 14),
            (r.centerx - 10, r.bottom - 14),
        ]
        pygame.draw.polygon(screen, self.color, cloak)
        pygame.draw.polygon(screen, (25, 28, 34), cloak, 2)

        # Head and hood
        head_r = 9
        head_c = (r.centerx, r.top - head_r + 6 + bob)
        pygame.draw.circle(screen, self.color, head_c, head_r + 4)
        pygame.draw.circle(screen, (232, 192, 145), head_c, head_r)
        pygame.draw.circle(screen, (20, 20, 20), head_c, head_r, 2)

        # Bow, arm, and tiny idle motion.
        bow_x = r.centerx + self.facing * 22
        bow_mid = (bow_x, shoulder[1] + 2)
        bow_rect = pygame.Rect(0, 0, 22, 58)
        bow_rect.center = bow_mid
        if self.facing > 0:
            pygame.draw.arc(screen, bow_col, bow_rect, -1.2, 1.2, 4)
        else:
            pygame.draw.arc(screen, bow_col, bow_rect, math.pi - 1.2,
                            math.pi + 1.2, 4)
        pygame.draw.line(screen, string_col, (bow_x, bow_mid[1] - 27),
                         (bow_x, bow_mid[1] + 27), 1)
        pygame.draw.line(screen, arm_col, shoulder, bow_mid, 4)
