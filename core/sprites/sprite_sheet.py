"""Load a spritesheet image and slice it into animation frames."""

from core.assets import load_image


class SpriteSheet:
    """Cuts a grid of equal-sized frames out of one image.

    Frames are read left-to-right, top-to-bottom. ``subsurface`` returns a view
    that shares pixels with the sheet, so we ``.copy()`` each frame to get an
    independent surface."""

    def __init__(self, name, frame_w, frame_h):
        self.sheet = load_image(name)
        self.frames = self._slice(frame_w, frame_h)

    def _slice(self, fw, fh):
        w, h = self.sheet.get_size()
        return [self.sheet.subsurface((x, y, fw, fh)).copy()
                for y in range(0, h - fh + 1, fh)
                for x in range(0, w - fw + 1, fw)]
