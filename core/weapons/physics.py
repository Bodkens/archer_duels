"""Projectile physics: the single source of truth shared by the live
projectile, the trajectory preview, and the AI solver."""

import math

from core import config as C
from .weapon import ARROW, BOMB


def _out_of_field(pos):
    x, y = pos
    return x < 0 or x >= C.SCREEN_W or y >= C.SCREEN_H


def step_physics(pos, vel, kind, dt):
    """Advance one (sub)step under gravity (and drag for the bomb)."""
    x, y = pos
    vx, vy = vel
    if kind == ARROW:
        vy += C.GRAVITY * dt
    elif kind == BOMB:
        vy += C.GRAVITY * C.BOMB_GRAVITY_MULT * dt
        vx *= (1.0 - C.BOMB_DRAG * dt)
    x += vx * dt
    y += vy * dt
    return (x, y), (vx, vy)


def velocity_from_angle_power(angle, power, kind):
    speed = power * C.POWER_TO_SPEED
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
