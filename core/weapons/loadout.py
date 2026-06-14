"""Per-archer weapon loadout."""

from .weapon import WEAPONS, ALL_KINDS


class WeaponSlot:
    def __init__(self, weapon):
        self.weapon = weapon


def random_loadout():
    """One slot per weapon kind. The active slot is chosen each turn."""
    return [WeaponSlot(WEAPONS[k]) for k in ALL_KINDS]
