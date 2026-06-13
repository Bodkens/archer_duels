"""Weapon definitions and projectile physics (pistol / spear / bomb)."""

import math
import pygame

import config as C

# Weapon kinds
PISTOL = "pistol"
SPEAR = "spear"
BOMB = "bomb"


class WeaponType:
    def __init__(self, kind, name, damage, color, size):
        self.kind = kind
        self.name = name
        self.damage = damage
        self.color = color
        self.size = size  # draw radius / length


WEAPONS = {
    PISTOL: WeaponType(PISTOL, "Pistol", C.PISTOL_DAMAGE, C.COL_PISTOL, 4),
    SPEAR: WeaponType(SPEAR, "Spear", C.SPEAR_DAMAGE, C.COL_SPEAR, 16),
    BOMB: WeaponType(BOMB, "Bomb", C.BOMB_MAX_DAMAGE, C.COL_BOMB, 7),
}

ALL_KINDS = [PISTOL, SPEAR, BOMB]


def _out_of_field(pos):
    x, y = pos
    return x < 0 or x >= C.SCREEN_W or y >= C.SCREEN_H


def step_physics(pos, vel, kind, dt):
    """Advance one (sub)step. The single source of truth shared by the live
    projectile, the trajectory preview, and the AI solver."""
    x, y = pos
    vx, vy = vel
    if kind == SPEAR:
        vy += C.GRAVITY * dt
    elif kind == BOMB:
        vy += C.GRAVITY * C.BOMB_GRAVITY_MULT * dt
        vx *= (1.0 - C.BOMB_DRAG * dt)
    # PISTOL: no gravity, constant velocity.
    x += vx * dt
    y += vy * dt
    return (x, y), (vx, vy)


def velocity_from_angle_power(angle, power, kind):
    speed = C.PISTOL_SPEED if kind == PISTOL else power * C.POWER_TO_SPEED
    return (math.cos(angle) * speed, math.sin(angle) * speed)


def aim_from_drag(start, release):
    """Slingshot: pull back from the archer; launch opposite the drag vector.
    Returns (angle, power) clamped to MAX_POWER."""
    dx = release[0] - start[0]
    dy = release[1] - start[1]
    dist = math.hypot(dx, dy)
    power = min(dist, C.MAX_POWER)
    if dist < 1e-3:
        return 0.0, 0.0
    angle = math.atan2(-dy, -dx)
    return angle, power


def simulate_path(start, vel, kind, terrain, archers=None, ignore=None,
                  max_points=400):
    """Step until the projectile hits terrain, an archer, or leaves the field.
    Returns (points, end_kind, hit_archer). Used for preview and AI aiming."""
    points = [start]
    pos = start
    v = vel
    dt = 1.0 / C.FPS
    for _ in range(max_points):
        # Subdivide so fast shots cannot tunnel through thin terrain.
        speed = math.hypot(v[0], v[1])
        nsub = max(1, int(speed * dt / (C.TILE * 0.5)) + 1)
        sub = dt / nsub
        for _ in range(nsub):
            pos, v = step_physics(pos, v, kind, sub)
            if _out_of_field(pos):  # allow airspace above the screen (y < 0)
                points.append(pos)
                return points, "out", None
            if archers:
                for a in archers:
                    if a is ignore or a.hp <= 0:
                        continue
                    if a.hit_test(pos):
                        points.append(pos)
                        return points, "archer", a
            if terrain.solid_at(pos[0], pos[1]):
                points.append(pos)
                return points, "terrain", None
        points.append(pos)
    return points, "out", None


class Projectile:
    def __init__(self, start, vel, weapon, shooter):
        self.x, self.y = start
        self.vx, self.vy = vel
        self.weapon = weapon
        self.kind = weapon.kind
        self.shooter = shooter
        self.alive = True
        self.fuse = C.BOMB_FUSE
        # Resolved on impact, consumed by the Match:
        self.outcome = "flying"     # flying | terrain | archer | exploded | out
        self.hit_archer = None
        self.impact = None
        self.angle = math.atan2(self.vy, self.vx)

    def update(self, dt, terrain, archers):
        nsub = max(1, int(math.hypot(self.vx, self.vy) * dt / (C.TILE * 0.5)) + 1)
        sub = dt / nsub
        for _ in range(nsub):
            (self.x, self.y), (self.vx, self.vy) = step_physics(
                (self.x, self.y), (self.vx, self.vy), self.kind, sub)
            self.angle = math.atan2(self.vy, self.vx)

            if _out_of_field((self.x, self.y)):
                self._finish("out")
                return

            for a in archers:
                if a is self.shooter or a.hp <= 0:
                    continue
                if a.hit_test((self.x, self.y)):
                    self.hit_archer = a
                    self._finish("archer" if self.kind != BOMB else "exploded")
                    return

            if terrain.solid_at(self.x, self.y):
                self._finish("terrain" if self.kind != BOMB else "exploded")
                return

        if self.kind == BOMB:
            self.fuse -= dt
            if self.fuse <= 0:
                self._finish("exploded")

    def _finish(self, outcome):
        self.alive = False
        self.outcome = outcome
        self.impact = (self.x, self.y)

    def draw(self, screen):
        if self.kind == PISTOL:
            pygame.draw.circle(screen, self.weapon.color,
                               (int(self.x), int(self.y)), self.weapon.size)
        elif self.kind == BOMB:
            pygame.draw.circle(screen, self.weapon.color,
                               (int(self.x), int(self.y)), self.weapon.size)
            pygame.draw.circle(screen, (200, 60, 40),
                               (int(self.x), int(self.y)), self.weapon.size, 2)
        else:  # SPEAR drawn as an oriented line
            L = self.weapon.size
            dx = math.cos(self.angle) * L
            dy = math.sin(self.angle) * L
            pygame.draw.line(screen, self.weapon.color,
                             (self.x - dx, self.y - dy),
                             (self.x + dx, self.y + dy), 3)
