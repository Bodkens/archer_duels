"""Base sprite that plays a row-based animation, with a vector-drawing fallback.

``rows`` is a list of animations; each animation is a list of frames. The active
animation is chosen with ``row_index`` and advanced over time by ``animate``. If
no rows are supplied (no spritesheet yet), ``draw`` falls back to ``draw_vector``,
which subclasses implement with ``pygame.draw`` calls."""

import pygame


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, rows=None, fps=10):
        super().__init__()
        self.rows = rows or []
        self.fps = fps
        self.t = 0.0
        self.row_index = 0
        first = self.rows[0][0] if (self.rows and self.rows[0]) else None
        self.image = first
        self.rect = first.get_rect() if first else pygame.Rect(0, 0, 0, 0)

    def animate(self, dt):
        """Advance the current row's frame based on elapsed time."""
        if not self.rows:
            return
        row = self.rows[min(self.row_index, len(self.rows) - 1)]
        if not row:
            return
        self.t += dt
        self.image = row[int(self.t * self.fps) % len(row)]

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect)
        else:
            self.draw_vector(surface)

    def draw_vector(self, surface):
        """Fallback drawing used until a spritesheet is provided."""
