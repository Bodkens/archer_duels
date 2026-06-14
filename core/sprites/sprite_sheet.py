"""Load a spritesheet image and slice it into a grid of animation frames.

Each *row* of the grid is one animation; the columns are its frames. The grid
size is derived from the nominal cell size by rounding (so a sheet that is, say,
484x307 with a nominal 40x62 cell yields a clean 12x5 grid), and the actual cuts
are evenly spaced sub-rectangles so rounding never drifts across the sheet."""

from core.assets import load_image


class SpriteSheet:
    def __init__(self, name, frame_w, frame_h):
        self.sheet = load_image(name)
        w, h = self.sheet.get_size()
        self.cols = max(1, round(w / frame_w))
        self.rows = self._slice(self.cols, max(1, round(h / frame_h)))

    def _slice(self, cols, rows):
        w, h = self.sheet.get_size()
        grid = []
        for r in range(rows):
            y0, y1 = round(r * h / rows), round((r + 1) * h / rows)
            line = []
            for c in range(cols):
                x0, x1 = round(c * w / cols), round((c + 1) * w / cols)
                # subsurface shares pixels with the sheet; copy to detach.
                line.append(self.sheet.subsurface((x0, y0, x1 - x0, y1 - y0)).copy())
            grid.append(line)
        return grid
