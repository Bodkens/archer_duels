"""The AI-controlled archer."""

from core import config as C
from .archer import Archer
from .sprite_sheet import SpriteSheet


class Enemy(Archer):
    def __init__(self, x, y, facing=-1):
        frames = None
        if C.ENEMY_SHEET:
            frames = SpriteSheet(C.ENEMY_SHEET, *C.ENEMY_FRAME).frames
        super().__init__(x, y, C.COL_ENEMY, is_ai=True, facing=facing,
                         frames=frames)
