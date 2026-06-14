"""Application: the singleton that owns pygame, the game loop and the state
machine (splash -> menu -> match)."""

import sys

import pygame

from core import config as C
from core import ui
from core.match import Match
from .state import ApplicationState


class Application:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Keep __init__ side-effect free so importing the module never touches
        # pygame. All real initialisation happens in run().
        if getattr(self, "_ready", False):
            return
        self.screen = None
        self.clock = None
        self.menu = None
        self.match = None
        self.sprites = None          # main sprite group (archers + live projectile)
        self.state = ApplicationState.SPLASH
        self.splash_t = 0.0
        self._running = False
        self._ready = True

    # --- Lifecycle ---
    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
        pygame.display.set_caption(C.TITLE)
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.menu = ui.Menu()
        self.state = ApplicationState.SPLASH
        self.splash_t = 0.0

        self._running = True
        while self._running:
            # Clamp dt to keep physics stable on hitches.
            dt = min(self.clock.tick(C.FPS) / 1000.0, 1.0 / 30.0)
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # --- Per-frame steps ---
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == ApplicationState.MATCH and self.match is not None:
                    self.match.request_exit()
                else:
                    self._running = False
            elif self.state == ApplicationState.MENU:
                action = self.menu.handle_event(event)
                if action == "quit":
                    self._running = False
                elif action == "play":
                    self._start_match()
            elif self.state == ApplicationState.MATCH:
                if self.match.handle_event(event) == "menu":
                    self._to_menu()

    def _update(self, dt):
        if self.state == ApplicationState.SPLASH:
            self.splash_t += dt
            if self.splash_t >= C.SPLASH_TIME:
                self.state = ApplicationState.MENU
        elif self.state == ApplicationState.MATCH:
            self.match.update(dt)

    def _draw(self):
        if self.state == ApplicationState.SPLASH:
            ui.draw_splash(self.screen)
        elif self.state == ApplicationState.MENU:
            self.menu.draw(self.screen)
        elif self.state == ApplicationState.MATCH:
            self.match.draw(self.screen)

    # --- Transitions ---
    def _start_match(self):
        self.match = Match(self.sprites)
        self.state = ApplicationState.MATCH

    def _to_menu(self):
        self.match = None
        if self.sprites is not None:
            self.sprites.empty()
        self.state = ApplicationState.MENU


application = Application()
