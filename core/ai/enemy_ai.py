"""Enemy AI: a trajectory solver plus the aiming/locked state machine."""

import math
import random

from core import config as C
from core.weapons import velocity_from_angle_power, simulate_path


class EnemyAI:
    def __init__(self):
        self.locked = False
        self.locked_pos = None
        self.pending_target_pos = None

    @staticmethod
    def _dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def aim_solution(self, start, target, kind, terrain):
        """Return (angle, power, hits) that best lands on the target, or None.
        `hits` is True when the simulated shot actually strikes the target."""
        tcenter = target.center()
        # Arc weapons: brute-force angle/power candidates through the shared
        # integrator and keep the closest landing (preferring a direct hit).
        best = None
        best_score = 1e18
        for ang_deg in range(-170, -5, 5):
            angle = math.radians(ang_deg)
            for power in range(50, int(C.MAX_POWER) + 1, 12):
                vel = velocity_from_angle_power(angle, power, kind)
                pts, end, hit = simulate_path(start, vel, kind, terrain,
                                              archers=[target])
                if hit is target:
                    return angle, float(power), True
                landing = pts[-1]
                score = self._dist(landing, tcenter)
                if score < best_score:
                    best_score = score
                    best = (angle, float(power))
        if best is None:
            return None
        return best[0], best[1], best_score < C.TILE * 2.5

    def _aim_current_weapon(self, shooter, target, terrain):
        """Aim the randomly assigned weapon for this turn."""
        start = shooter.muzzle_pos()
        sol = self.aim_solution(start, target, shooter.selected.weapon.kind,
                                terrain)
        if sol is None:
            return None
        angle, power, hits = sol
        return angle, power, hits

    def take_turn(self, shooter, target, terrain):
        """Return an action dict: {'type':'shoot', angle, power} or
        {'type':'walk', dx}."""
        tpos = target.center()
        if self.locked and self.locked_pos is not None:
            if self._dist(tpos, self.locked_pos) > C.AI_MOVE_THRESHOLD:
                self.locked = False  # player moved -> range in again

        pick = self._aim_current_weapon(shooter, target, terrain)
        if pick is None:
            # No usable solution: shuffle toward the target and pass.
            return {"type": "walk", "dx": math.copysign(C.WALK_SPEED * 0.75,
                                                        tpos[0] - shooter.x)}

        angle, power, _ = pick

        if not self.locked and random.random() >= C.AIM_HIT_CHANCE:
            # Deliberate near miss while ranging in.
            angle += math.radians(random.uniform(-C.AIM_MISS_SPREAD,
                                                  C.AIM_MISS_SPREAD))
            power = max(40.0, power + random.uniform(-C.AIM_MISS_SPREAD,
                                                     C.AIM_MISS_SPREAD))

        self.pending_target_pos = tpos
        return {"type": "shoot", "angle": angle, "power": power}

    def notify_result(self, hit_player):
        if hit_player:
            self.locked = True
            self.locked_pos = self.pending_target_pos
        else:
            self.locked = False
