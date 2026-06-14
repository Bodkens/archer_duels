"""The human-controlled archer."""

from core import config as C
from .archer import Archer
from .sprite_sheet import SpriteSheet


class Player(Archer):
    def __init__(self, x, y, facing=1):
        rows = None
        if C.PLAYER_SHEET:
            rows = SpriteSheet(C.PLAYER_SHEET, *C.PLAYER_FRAME).rows
        super().__init__(x, y, C.COL_PLAYER, is_ai=False, facing=facing,
                         rows=rows)
