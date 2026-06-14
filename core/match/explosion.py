"""Short-lived expanding blast effect drawn after a bomb detonates."""

import pygame


class Explosion:
    def __init__(self, x, y, radius):
        self.x, self.y, self.radius = x, y, radius
        self.t = 0.0
        self.dur = 0.4

    def update(self, dt):
        self.t += dt
        return self.t < self.dur

    def draw(self, screen):
        frac = self.t / self.dur
        r = int(self.radius * (0.4 + 0.6 * frac))
        col = (255, int(200 - 120 * frac), int(60 * (1 - frac)))
        pygame.draw.circle(screen, col, (int(self.x), int(self.y)), max(2, r))
