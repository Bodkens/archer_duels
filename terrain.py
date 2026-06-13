"""Procedural tile-grid terrain: generation, collision queries, destruction, rendering."""

import os
import numpy as np
import pygame

import config as C


class Terrain:
    def __init__(self):
        self.grid = np.zeros((C.ROWS, C.COLS), dtype=np.uint8)
        self.surface = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
        self.background = self._load_background()
        self.generate()

    def _load_background(self):
        path = os.path.join(os.path.dirname(__file__), "background.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                return pygame.transform.scale(img, (C.SCREEN_W, C.SCREEN_H))
            except pygame.error:
                pass
        bg = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
        bg.fill(C.COL_SKY)
        return bg

    def generate(self):
        self.grid[:] = C.EMPTY
        heights = self._generate_heights()
        cols = np.arange(C.COLS)
        # Fill dirt from each column's surface row down to the bottom.
        row_idx = np.arange(C.ROWS)[:, None]
        mask = row_idx >= heights[None, :]
        self.grid[mask] = C.DIRT
        self._add_stone(heights)
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
        n_blobs = rng.integers(3, 6)
        rows = np.arange(C.ROWS)[:, None]
        cols = np.arange(C.COLS)[None, :]
        for _ in range(n_blobs):
            cx = rng.integers(0, C.COLS)
            cy = rng.integers(int(C.ROWS * 0.55), C.ROWS - 2)
            rx = rng.integers(6, 16)
            ry = rng.integers(4, 10)
            ellipse = ((cols - cx) / rx) ** 2 + ((rows - cy) / ry) ** 2 <= 1.0
            # Only turn already-solid dirt into stone (keep stone underground).
            self.grid[ellipse & (self.grid == C.DIRT)] = C.STONE

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
                elif mat == C.STONE:
                    self.surface.fill(C.COL_STONE, rect)
                else:  # DIRT, with a grassy top edge
                    top = r == 0 or self.grid[r - 1, c] == C.EMPTY
                    self.surface.fill(C.COL_DIRT_TOP if top else C.COL_DIRT, rect)

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
        """Remove DIRT (never STONE) within the radius; refresh the affected cache."""
        ccx = int(cx) // C.TILE
        ccy = int(cy) // C.TILE
        r = int(radius_tiles)
        rows = np.arange(C.ROWS)[:, None]
        cols = np.arange(C.COLS)[None, :]
        circle = (cols - ccx) ** 2 + (rows - ccy) ** 2 <= r * r
        removable = circle & (self.grid == C.DIRT)
        self.grid[removable] = C.EMPTY
        # Redraw a slightly padded box so freshly-exposed grass edges update too.
        self._blit_region(ccx - r - 1, ccy - r - 1, ccx + r + 2, ccy + r + 2)
