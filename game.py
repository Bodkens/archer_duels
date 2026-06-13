"""Match: spawning, turn flow, input handling and projectile resolution."""

import random
import math
import pygame

import config as C
import weapons as W
from terrain import Terrain
from entities import Archer
from ai import EnemyAI
import ui


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


class Match:
    def __init__(self, mode="ai"):
        self.mode = "ai"
        self.terrain = Terrain()
        self.p1, self.p2 = self._spawn_archers()
        self.archers = [self.p1, self.p2]
        self.ai = EnemyAI()

        self.current_idx = 0
        self.projectile = None
        self.explosions = []
        self.phase = "aim"          # aim | resolving | gameover
        self.finished = False
        self.winner = None
        self.message = ""

        self.dragging = False
        self.walked = False
        self.walk_stop_timer = 0.0
        self.confirm_exit = False
        self.ai_timer = 0.0
        self.shooter = None
        self.ai_target = None
        self.target_hp_before = 0

        self._begin_turn()

    # --- Setup ---
    def _spawn_archers(self):
        margin = 120
        while True:
            x1 = random.randint(margin, C.SCREEN_W // 2 - 60)
            x2 = random.randint(C.SCREEN_W // 2 + 60, C.SCREEN_W - margin)
            if x2 - x1 >= C.MIN_SPAWN_GAP:
                break
        p1 = Archer(x1, 0, C.COL_PLAYER, is_ai=False, facing=1)
        p2 = Archer(x2, 0, C.COL_ENEMY, is_ai=True, facing=-1)
        p1.ground(self.terrain)
        p2.ground(self.terrain)
        return p1, p2

    @property
    def current(self):
        return self.archers[self.current_idx]

    @property
    def opponent(self):
        return self.archers[1 - self.current_idx]

    # --- Turn flow ---
    def _begin_turn(self):
        self.current.start_turn()
        self.walked = False
        self.walk_stop_timer = 0.0
        self.dragging = False
        self.ai_timer = 0.7 if self.current.is_ai else 0.0
        if self.current.is_ai:
            self.message = "Enemy is taking aim..."
        else:
            self.message = "Drag to aim and throw  |  A/D or arrows to move instead"

    def _end_turn(self):
        for a in self.archers:
            if a.hp <= 0:
                self.finished = True
                self.phase = "gameover"
                winner = self.p1 if self.p2.hp <= 0 else self.p2
                self.winner = winner
                self.winner_text = "You Win!" if winner is self.p1 else "You Lose!"
                return
        self.current_idx = 1 - self.current_idx
        self.phase = "aim"
        self._begin_turn()

    def _fire(self, angle, power):
        weapon = self.current.selected.weapon
        self.current.facing = 1 if math.cos(angle) >= 0 else -1
        vel = W.velocity_from_angle_power(angle, power, weapon.kind)
        self.projectile = W.Projectile(self.current.muzzle_pos(), vel, weapon,
                                       self.current)
        self.shooter = self.current
        self.ai_target = self.opponent
        self.target_hp_before = self.ai_target.hp
        self.phase = "resolving"
        self.message = ""

    # --- Resolution ---
    def _resolve_projectile(self):
        p = self.projectile
        if p.outcome == "archer" and p.hit_archer:
            p.hit_archer.take_damage(p.weapon.damage)
        elif p.outcome == "exploded":
            self._explode(p.impact, p.weapon)
        self.projectile = None
        self._settle_archers()

        if self.shooter is not None and self.shooter.is_ai and self.ai:
            hit = self.ai_target.hp < self.target_hp_before
            self.ai.notify_result(hit)

        self._end_turn()

    def _explode(self, center, weapon):
        cx, cy = center
        radius_px = C.BOMB_RADIUS_TILES * C.TILE
        self.terrain.destroy_circle(cx, cy, C.BOMB_RADIUS_TILES)
        self.explosions.append(Explosion(cx, cy, radius_px))
        for a in self.archers:
            ax, ay = a.center()
            dist = math.hypot(ax - cx, ay - cy)
            if dist <= radius_px:
                dmg = int(weapon.damage * (1.0 - dist / radius_px))
                a.take_damage(max(1, dmg))
                # Knockback away from the blast (this displacement later forces
                # the AI to re-aim because the target's position changed).
                direction = 1 if ax >= cx else -1
                push = C.BOMB_KNOCKBACK * (1.0 - dist / radius_px)
                a.x = max(20, min(C.SCREEN_W - 20, a.x + direction * push))

    def _settle_archers(self):
        for a in self.archers:
            a.y = self.terrain.surface_y(a.x)

    # --- Input ---
    def handle_event(self, event):
        if self.confirm_exit:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "menu"
                if event.key == pygame.K_ESCAPE:
                    self.confirm_exit = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                yes, no = ui.confirm_exit_buttons()
                if yes.collidepoint(event.pos):
                    return "menu"
                if no.collidepoint(event.pos):
                    self.confirm_exit = False
            return None

        if self.phase == "gameover":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                return "menu"
            return None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.confirm_exit = True
            return None
        if self.phase != "aim" or self.current.is_ai:
            return None

        if event.type == pygame.KEYDOWN:
            if self.walked and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                             pygame.K_SPACE):
                self._end_turn()
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.walked:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                angle, power = W.aim_from_drag(self.current.muzzle_pos(),
                                               event.pos)
                if power >= 10.0:
                    self._fire(angle, power)
        return None

    def _handle_walk(self, dt):
        if self.current.is_ai or self.phase != "aim" or self.dragging:
            return
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction += 1
        if direction != 0:
            moved = self.current.walk(direction * C.WALK_SPEED * dt, self.terrain)
            if moved > 0:
                self.walked = True
                left = max(0, int(C.WALK_DISTANCE - self.current.moved_distance))
                self.message = f"Moving... {left}px left  |  Enter to end turn"
            # Releasing A/D keeps the turn going while budget remains; the turn
            # only ends once the whole movement budget is spent.
            if self.current.moved_distance >= C.WALK_DISTANCE:
                self._end_turn()

    def _ai_turn(self, dt):
        self.ai_timer -= dt
        if self.ai_timer > 0:
            return
        action = self.ai.take_turn(self.current, self.opponent, self.terrain)
        if action["type"] == "shoot":
            self._fire(action["angle"], action["power"])
        else:
            self.current.walk(action["dx"], self.terrain)
            self._end_turn()

    # --- Update / draw ---
    def update(self, dt):
        if self.confirm_exit:
            return

        self.explosions = [e for e in self.explosions if e.update(dt)]
        for a in self.archers:
            a.update(dt)

        if self.phase == "aim":
            if self.current.is_ai:
                self._ai_turn(dt)
            else:
                self._handle_walk(dt)
        elif self.phase == "resolving":
            if self.projectile:
                self.projectile.update(dt, self.terrain, self.archers)
                if not self.projectile.alive:
                    self._resolve_projectile()

    def draw(self, screen):
        self.terrain.draw(screen)
        for a in self.archers:
            a.draw(screen, active=(a is self.current and self.phase != "gameover"))
        if self.projectile:
            self.projectile.draw(screen)
        for e in self.explosions:
            e.draw(screen)

        if (self.phase == "aim" and not self.current.is_ai and self.dragging):
            ui.draw_aim_indicator(screen, self.current, pygame.mouse.get_pos(),
                                  self.terrain, self.archers)

        ui.draw_hud(screen, self.p1, self.p2, self.current, self.message)
        if self.phase == "gameover":
            ui.draw_game_over(screen, self.winner_text)
        if self.confirm_exit:
            ui.draw_confirm_exit(screen)

    def request_exit(self):
        if self.phase == "gameover":
            return "menu"
        self.confirm_exit = True
        return None
