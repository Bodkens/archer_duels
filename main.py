"""Archer Duels — entry point and top-level app state machine."""

import sys
import pygame

import config as C
import ui
from game import Match

SPLASH, MENU, MATCH, = "splash", "menu", "match"


def main():
    pygame.init()
    screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
    pygame.display.set_caption(C.TITLE)
    clock = pygame.time.Clock()

    state = SPLASH
    splash_t = 0.0
    menu = ui.Menu()
    match = None

    running = True
    while running:
        dt = clock.tick(C.FPS) / 1000.0
        dt = min(dt, 1.0 / 30.0)  # clamp to keep physics stable on hitches

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == MENU:
                action = menu.handle_event(event)
                if action == "quit":
                    running = False
                elif action in ("ai", "pvp"):
                    match = Match(action)
                    state = MATCH
            elif state == MATCH:
                result = match.handle_event(event)
                if result == "menu":
                    match = None
                    state = MENU

        if state == SPLASH:
            splash_t += dt
            ui.draw_splash(screen)
            if splash_t >= C.SPLASH_TIME:
                state = MENU
        elif state == MENU:
            menu.draw(screen)
        elif state == MATCH:
            match.update(dt)
            match.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
