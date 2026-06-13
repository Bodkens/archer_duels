"""Procedural tile-grid terrain, collision queries, destruction, rendering."""

import numpy as np
import pygame

import config as C


class Terrain:
    def __init__(self):
        self.grid = np.zeros((C.ROWS, C.COLS), dtype=np.uint8)
        self.surface = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
        self.background = self._make_background()
        self.clouds = self._make_cloud_sprites()
        self.generate()

    def _make_background(self):
        bg = pygame.Surface((C.SCREEN_W, C.SCREEN_H)).convert()
        top = (111, 171, 219)
        horizon = (220, 229, 204)
        for y in range(C.SCREEN_H):
            k = y / C.SCREEN_H
            col = tuple(int(top[i] * (1 - k) + horizon[i] * k) for i in range(3))
            pygame.draw.line(bg, col, (0, y), (C.SCREEN_W, y))

        pygame.draw.circle(bg, (248, 204, 102), (118, 92), 44)
        pygame.draw.circle(bg, (255, 229, 151), (118, 92), 28)
        self._draw_mountains(bg, C.SCREEN_H - 260, (101, 139, 143), 150)
        self._draw_mountains(bg, C.SCREEN_H - 210, (78, 118, 121), 120)
        self._draw_mountains(bg, C.SCREEN_H - 165, (58, 99, 99), 96)
        pygame.draw.rect(bg, (159, 183, 135), (0, C.SCREEN_H - 145, C.SCREEN_W, 145))
        for x in range(0, C.SCREEN_W, 42):
            shade = (130 + (x // 42) % 3 * 10, 166, 112)
            pygame.draw.line(bg, shade, (x, C.SCREEN_H - 145),
                             (x + 22, C.SCREEN_H), 2)
        return bg

    def _draw_mountains(self, surface, base_y, color, step):
        points = [(-80, C.SCREEN_H), (-80, base_y)]
        for x in range(-80, C.SCREEN_W + step, step):
            peak = base_y - 80 - ((x // step) % 4) * 24
            points.extend([(x + step // 2, peak), (x + step, base_y)])
        points.append((C.SCREEN_W + 80, C.SCREEN_H))
        pygame.draw.polygon(surface, color, points)

    def _make_cloud_sprites(self):
        clouds = []
        for i in range(6):
            surf = pygame.Surface((150, 56), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (255, 255, 248, 190), (6, 24, 82, 24))
            pygame.draw.ellipse(surf, (255, 255, 248, 210), (38, 10, 82, 34))
            pygame.draw.ellipse(surf, (238, 246, 244, 185), (76, 22, 68, 24))
            clouds.append({
                "image": surf,
                "x": float((i * 240) % (C.SCREEN_W + 180) - 120),
                "y": 65 + (i % 3) * 42,
                "speed": 10 + i * 2.5,
            })
        return clouds

    def generate(self):
        self.grid[:] = C.EMPTY
        heights = self._generate_heights()
        cols = np.arange(C.COLS)
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
        self._draw_ambient_sprites(screen)

    def _draw_ambient_sprites(self, screen):
        t = pygame.time.get_ticks() / 1000.0
        for cloud in self.clouds:
            x = (cloud["x"] + t * cloud["speed"]) % (C.SCREEN_W + 220) - 160
            screen.blit(cloud["image"], (x, cloud["y"]))
        for i in range(5):
            x = (220 + i * 190 + t * 34) % (C.SCREEN_W + 80) - 40
            y = 100 + (i % 2) * 38 + np.sin(t * 2 + i) * 5
            pygame.draw.arc(screen, (42, 55, 62), (x, y, 18, 10), 0.1, 2.7, 2)
            pygame.draw.arc(screen, (42, 55, 62), (x + 16, y, 18, 10), 0.4, 3.0, 2)

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
