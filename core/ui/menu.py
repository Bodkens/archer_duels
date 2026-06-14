"""Splash screen and the main menu."""

import pygame

from core import config as C
from .fonts import font, center_text
from .background import draw_background


def draw_splash(screen):
    draw_background(screen)
    center_text(screen, C.TITLE, 84, C.SCREEN_H // 2 - 20, bold=True)
    center_text(screen, "Bowmasters-style artillery duel", 26,
                C.SCREEN_H // 2 + 50, C.COL_TEXT_DIM)


class Menu:
    def __init__(self):
        labels = [("Play", "play"),
                  ("Quit", "quit")]
        self.buttons = []
        bw, bh, gap = 360, 64, 24
        total = len(labels) * bh + (len(labels) - 1) * gap
        y0 = C.SCREEN_H // 2 - total // 2 + 40
        for i, (label, action) in enumerate(labels):
            rect = pygame.Rect(0, 0, bw, bh)
            rect.center = (C.SCREEN_W // 2, y0 + i * (bh + gap) + bh // 2)
            self.buttons.append((rect, label, action))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, _, action in self.buttons:
                if rect.collidepoint(event.pos):
                    return action
        return None

    def draw(self, screen):
        draw_background(screen)
        center_text(screen, C.TITLE, 72, C.SCREEN_H // 4, bold=True)
        mouse = pygame.mouse.get_pos()
        for rect, label, _ in self.buttons:
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(screen, C.COL_BUTTON_HOVER if hover else C.COL_BUTTON,
                             rect, border_radius=10)
            pygame.draw.rect(screen, (160, 175, 200), rect, 2, border_radius=10)
            surf = font(30, bold=True).render(label, True, C.COL_TEXT)
            screen.blit(surf, surf.get_rect(center=rect.center))
