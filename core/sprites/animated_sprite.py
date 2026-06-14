"""Base sprite that plays a list of frames, with a vector-drawing fallback."""

import pygame


class AnimatedSprite(pygame.sprite.Sprite):
    """Holds animation frames and advances them over time.

    If no frames are supplied (no spritesheet yet), ``draw`` falls back to
    ``draw_vector``, which subclasses implement with ``pygame.draw`` calls.
    Drop a spritesheet in and the same code blits ``self.image`` instead."""

    def __init__(self, frames=None, fps=8):
        super().__init__()
        self.frames = frames or []
        self.fps = fps
        self.t = 0.0
        self.image = self.frames[0] if self.frames else None
        self.rect = (self.image.get_rect() if self.image
                     else pygame.Rect(0, 0, 0, 0))

    def animate(self, dt):
        """Advance the current frame based on elapsed time."""
        if not self.frames:
            return
        self.t += dt
        self.image = self.frames[int(self.t * self.fps) % len(self.frames)]

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect)
        else:
            self.draw_vector(surface)

    def draw_vector(self, surface):
        """Fallback drawing used until a spritesheet is provided."""
