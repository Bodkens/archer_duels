"""Optional tile artwork. Slices a tile image into one surface per material.

The image is expected to be a single row of TILE-sized cells in material order:
[EMPTY, DIRT, STONE]. When ``TILES_IMAGE`` is not set, the Terrain falls back to
flat colour fills, so this is entirely optional."""

from core import config as C
from core.assets import load_image


class Tileset:
    def __init__(self, name):
        sheet = load_image(name)
        # subsurface returns a view sharing the sheet's pixels; copy to detach.
        self._tiles = {
            mat: sheet.subsurface((i * C.TILE, 0, C.TILE, C.TILE)).copy()
            for i, mat in enumerate((C.EMPTY, C.DIRT, C.STONE))
        }

    def tile(self, material):
        return self._tiles.get(material)
