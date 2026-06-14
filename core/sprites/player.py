"""The human-controlled archer."""

from core import config as C
from .archer import Archer
from .sprite_sheet import SpriteSheet


class Player(Archer):
    def __init__(self, x, y, facing=1):
        frames = None
        if C.PLAYER_SHEET:
            frames = SpriteSheet(C.PLAYER_SHEET, *C.PLAYER_FRAME).frames
        super().__init__(x, y, C.COL_PLAYER, is_ai=False, facing=facing,
                         frames=frames)
