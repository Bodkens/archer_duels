"""Procedural tile-grid terrain: collision queries, destruction, rendering.

The visible ground is a numpy grid of material ids baked once into a single
Surface (fast to blit). The static background image sits behind it. Tiles are
data, not sprites: collisions are grid queries (see ``solid_at`` / ``surface_y``
/ ``destroy_circle``), not sprite-vs-sprite checks."""

import numpy as np
import pygame

from core import config as C
from core.assets import load_image
from .tileset import Tileset


class Terrain:
    def __init__(self):
        self.grid = np.zeros((C.ROWS, C.COLS), dtype=np.uint8)
        self.surface = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
        self.background = self._make_background()
        self.tileset = Tileset(C.TILES_IMAGE) if C.TILES_IMAGE else None
        self.generate()

    def _make_background(self):
        """Static background image scaled to the screen."""
        img = load_image(C.BACKGROUND_IMAGE, alpha=False)
        return pygame.transform.scale(img, (C.SCREEN_W, C.SCREEN_H))

    def generate(self):
        self.grid[:] = C.EMPTY
        heights = self._generate_heights()
        # Fill dirt from each column's surface row down to the bottom.
        row_idx = np.arange(C.ROWS)[:, None]
        mask = row_idx >= heights[None, :]
        self.grid[mask] = C.DIRT
        self._add_stone(heights)
        self._add_bedrock()
        self._top_rows = heights  # cached top solid row per column
        self.redraw_all()

    def _generate_heights(self):
        # Smoothed random walk plus a couple of sine waves for rolling hills.
        rng = np.random.default_rng()
        steps = rng.normal(0, 1.0, C.COLS)
        walk = np.cumsum(steps)
        # Smooth via moving average.
        k = 21
        kernel = np.ones(k) / k
        walk = np.convolve(walk, kernel, mode="same")

        x = np.linspace(0, np.pi * 4, C.COLS)
        waves = 6.0 * np.sin(x * rng.uniform(0.5, 1.5) + rng.uniform(0, 6))
        waves += 3.0 * np.sin(x * rng.uniform(1.5, 3.0) + rng.uniform(0, 6))

        profile = walk + waves
        # Normalize into the allowed vertical band.
        profile -= profile.min()
        if profile.max() > 0:
            profile /= profile.max()
        band = C.SURFACE_MAX_ROW - C.SURFACE_MIN_ROW
        heights = (C.SURFACE_MIN_ROW + profile * band).astype(np.int32)
        return np.clip(heights, C.SURFACE_MIN_ROW, C.SURFACE_MAX_ROW)

    def _add_stone(self, heights):
        rng = np.random.default_rng()
        n_blobs = rng.integers(5, 9)
        rows = np.arange(C.ROWS)[:, None]
        cols = np.arange(C.COLS)[None, :]
        for _ in range(n_blobs):
            cx = rng.integers(0, C.COLS)
            cy = rng.integers(C.STONE_START_ROW, C.ROWS - C.SAFE_GROUND_ROWS)
            rx = rng.integers(8, 22)
            ry = rng.integers(5, 12)
            ellipse = ((cols - cx) / rx) ** 2 + ((rows - cy) / ry) ** 2 <= 1.0
            # Only turn already-solid dirt into stone (keep stone underground).
            self.grid[ellipse & (self.grid == C.DIRT)] = C.STONE

    def _add_bedrock(self):
        self.grid[C.ROWS - C.SAFE_GROUND_ROWS:, :] = C.STONE

    # --- Rendering ---
    def redraw_all(self):
        self.surface.blit(self.background, (0, 0))
        self._blit_region(0, 0, C.COLS, C.ROWS)

    def _blit_region(self, c0, r0, c1, r1):
        c0 = max(0, c0)
        r0 = max(0, r0)
        c1 = min(C.COLS, c1)
        r1 = min(C.ROWS, r1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                mat = self.grid[r, c]
                rect = (c * C.TILE, r * C.TILE, C.TILE, C.TILE)
                if mat == C.EMPTY:
                    self.surface.blit(self.background, (c * C.TILE, r * C.TILE), rect)
                elif self.tileset is not None:
                    self.surface.blit(self.tileset.tile(mat), (rect[0], rect[1]))
                elif mat == C.STONE:
                    self.surface.fill(C.COL_STONE, rect)
                    fleck = 18 if (r + c) % 2 == 0 else -10
                    col = tuple(max(0, min(255, v + fleck)) for v in C.COL_STONE)
                    pygame.draw.line(self.surface, col, (rect[0] + 1, rect[1] + 2),
                                     (rect[0] + C.TILE - 2, rect[1] + 2))
                else:  # DIRT, with a grassy top edge
                    top = r == 0 or self.grid[r - 1, c] == C.EMPTY
                    self.surface.fill(C.COL_DIRT_TOP if top else C.COL_DIRT, rect)
                    if top:
                        pygame.draw.line(self.surface, (118, 190, 78),
                                         (rect[0], rect[1]),
                                         (rect[0] + C.TILE, rect[1]), 2)
                    elif (r * 3 + c) % 5 == 0:
                        pygame.draw.circle(self.surface, (92, 62, 40),
                                           (rect[0] + 3, rect[1] + 4), 1)

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))

    # --- Queries ---
    def in_bounds(self, px, py):
        return 0 <= px < C.SCREEN_W and 0 <= py < C.SCREEN_H

    def solid_at(self, px, py):
        c = int(px) // C.TILE
        r = int(py) // C.TILE
        if 0 <= c < C.COLS and 0 <= r < C.ROWS:
            return self.grid[r, c] != C.EMPTY
        return False

    def surface_y(self, px):
        """Topmost solid pixel-y for the column containing px (bottom if none)."""
        c = int(px) // C.TILE
        c = max(0, min(C.COLS - 1, c))
        col = self.grid[:, c]
        solid = np.nonzero(col != C.EMPTY)[0]
        if len(solid) == 0:
            return C.SCREEN_H
        return int(solid[0]) * C.TILE

    def destroy_circle(self, cx, cy, radius_tiles):
        """Remove DIRT above bedrock; never destroy stone or the bottom layer."""
        ccx = int(cx) // C.TILE
        ccy = int(cy) // C.TILE
        r = int(radius_tiles)
        rows = np.arange(C.ROWS)[:, None]
        cols = np.arange(C.COLS)[None, :]
        circle = (cols - ccx) ** 2 + (rows - ccy) ** 2 <= r * r
        above_safe_floor = rows < C.ROWS - C.SAFE_GROUND_ROWS
        removable = circle & above_safe_floor & (self.grid == C.DIRT)
        self.grid[removable] = C.EMPTY
        # Redraw a slightly padded box so freshly-exposed grass edges update too.
        self._blit_region(ccx - r - 1, ccy - r - 1, ccx + r + 2, ccy + r + 2)
