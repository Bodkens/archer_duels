"""Full-screen overlays: game over and the quit-confirmation dialog."""

import pygame

from core import config as C
from .fonts import font, center_text


def draw_game_over(screen, winner_text):
    overlay = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    center_text(screen, winner_text, 72, C.SCREEN_H // 2 - 30, bold=True)
    center_text(screen, "Click or press any key to return to menu", 26,
                C.SCREEN_H // 2 + 40, C.COL_TEXT_DIM)


def confirm_exit_buttons():
    box = pygame.Rect(0, 0, 520, 230)
    box.center = (C.SCREEN_W // 2, C.SCREEN_H // 2)
    yes = pygame.Rect(box.x + 82, box.y + 150, 150, 48)
    no = pygame.Rect(box.right - 232, box.y + 150, 150, 48)
    return yes, no


def draw_confirm_exit(screen):
    overlay = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    box = pygame.Rect(0, 0, 520, 230)
    box.center = (C.SCREEN_W // 2, C.SCREEN_H // 2)
    pygame.draw.rect(screen, (30, 36, 48), box, border_radius=12)
    pygame.draw.rect(screen, (180, 195, 220), box, 2, border_radius=12)
    center_text(screen, "Quit to menu?", 32, box.y + 56, C.COL_TEXT, bold=True)
    center_text(screen, "Enter - quit     Esc - continue", 22,
                box.y + 100, C.COL_TEXT_DIM)

    yes, no = confirm_exit_buttons()
    mouse = pygame.mouse.get_pos()
    for rect, label in ((yes, "Quit"), (no, "Stay")):
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, C.COL_BUTTON_HOVER if hover else C.COL_BUTTON,
                         rect, border_radius=8)
        pygame.draw.rect(screen, (160, 175, 200), rect, 2, border_radius=8)
        surf = font(24, bold=True).render(label, True, C.COL_TEXT)
        screen.blit(surf, surf.get_rect(center=rect.center))
    return yes, no
