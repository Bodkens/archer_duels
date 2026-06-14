"""Weapons: definitions, loadouts, flight physics, and the projectile base."""

from .weapon import WeaponType, WEAPONS, ALL_KINDS, ARROW, BOMB
from .loadout import WeaponSlot, random_loadout
from .physics import (
    step_physics,
    velocity_from_angle_power,
    aim_from_drag,
    simulate_path,
)
from .projectile import Projectile

__all__ = [
    "WeaponType", "WEAPONS", "ALL_KINDS", "ARROW", "BOMB",
    "WeaponSlot", "random_loadout",
    "step_physics", "velocity_from_angle_power", "aim_from_drag",
    "simulate_path", "Projectile",
]
