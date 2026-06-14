"""Weapon kinds and the static weapon registry."""

from core import config as C

# Weapon kinds
ARROW = "arrow"
BOMB = "bomb"


class WeaponType:
    def __init__(self, kind, name, damage, color, size):
        self.kind = kind
        self.name = name
        self.damage = damage
        self.color = color
        self.size = size  # draw radius / length


WEAPONS = {
    ARROW: WeaponType(ARROW, "Arrow", C.ARROW_DAMAGE, C.COL_ARROW, 18),
    BOMB: WeaponType(BOMB, "Bomb", C.BOMB_MAX_DAMAGE, C.COL_BOMB, 7),
}

ALL_KINDS = [ARROW, BOMB]
