"""Enemy AI: a trajectory solver plus the aiming/locked state machine."""

import math
import random

import config as C
import weapons as W


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
        if kind == W.PISTOL:
            angle = math.atan2(tcenter[1] - start[1], tcenter[0] - start[0])
            vel = W.velocity_from_angle_power(angle, 0, kind)
            _, end, hit = W.simulate_path(start, vel, kind, terrain,
                                          archers=[target], ignore=None)
            if hit is target:
                return angle, C.MAX_POWER, True
            return angle, C.MAX_POWER, False

        # Arc weapons: brute-force angle/power candidates through the shared
        # integrator and keep the closest landing (preferring a direct hit).
        best = None
        best_score = 1e18
        for ang_deg in range(-170, -5, 5):
            angle = math.radians(ang_deg)
            for power in range(50, int(C.MAX_POWER) + 1, 12):
                vel = W.velocity_from_angle_power(angle, power, kind)
                pts, end, hit = W.simulate_path(start, vel, kind, terrain,
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

    def _best_weapon(self, shooter, target, terrain):
        """Pick the loadout slot (with ammo) most likely to hit; return
        (slot_index, angle, power, hits) or None."""
        start = shooter.muzzle_pos()
        fallback = None
        for i, slot in enumerate(shooter.loadout):
            if slot.ammo <= 0:
                continue
            sol = self.aim_solution(start, target, slot.weapon.kind, terrain)
            if sol is None:
                continue
            angle, power, hits = sol
            if hits:
                return i, angle, power, True
            if fallback is None:
                fallback = (i, angle, power, False)
        return fallback

    def take_turn(self, shooter, target, terrain):
        """Return an action dict: {'type':'shoot', angle, power} or
        {'type':'walk', dx}."""
        tpos = target.center()
        if self.locked and self.locked_pos is not None:
            if self._dist(tpos, self.locked_pos) > C.AI_MOVE_THRESHOLD:
                self.locked = False  # player moved -> range in again

        pick = self._best_weapon(shooter, target, terrain)
        if pick is None:
            # No usable solution: shuffle toward the target and pass.
            return {"type": "walk", "dx": math.copysign(C.WALK_DISTANCE,
                                                        tpos[0] - shooter.x)}

        idx, angle, power, _ = pick
        shooter.select_index(idx)

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
