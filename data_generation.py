import math
import time
import random
import cv2
import numpy as np
import pandas as pd

from world import world


# ===================== CONFIG =====================
GOAL_TOL = 5.0
MAX_STEPS_PER_TARGET = 500
SHOW_VIS = True

CSV_NAME = "data.csv"


# ===================== LOGGER =====================
class SimpleLogger:
    def __init__(self, filename: str):
        self.filename = filename
        self.df = pd.DataFrame(columns=["multiplier", "x", "y", "theta", "x_ref", "y_ref"])
        self.start_time = time.time()

    def log(self, multiplier: int, x: float, y: float, theta: float, x_ref: float, y_ref: float) -> None:
        self.df.loc[len(self.df)] = [multiplier, x, y, theta, x_ref, y_ref]

    def save(self) -> None:
        self.df.to_csv(self.filename, index=False)
        print(f"✅ Saved {len(self.df)} samples to {self.filename}")


# ===================== HELPERS =====================
def wrap_angle(a: float) -> float:
    while a > math.pi:
        a -= 2 * math.pi
    while a <= -math.pi:
        a += 2 * math.pi
    return a


def geom_control_vl_vr(
    x: float, y: float, theta: float,
    x_ref: float, y_ref: float,
    theta_ref,
    v_ref: float, w_ref: float,
    L: float,
    kx: float = 0.2, ky: float = 3.0, kth: float = 0.1,
    vwheel_lim: float | None = 10.0,
    v_lim: float | None = 10.0,
    w_lim: float | None = 10.0,
):
    dx, dy = x_ref - x, y_ref - y
    c, s = math.cos(theta), math.sin(theta)
    ex = c * dx + s * dy
    ey = -s * dx + c * dy

    if theta_ref is None:
        e_theta = 0.0
        v = kx * ex
    else:
        e_theta = wrap_angle(theta_ref - theta)
        v = v_ref * math.cos(e_theta) + kx * ex

    w = w_ref + ky * v_ref * ey + kth * math.sin(e_theta)

    if v_lim is not None:
        v = max(-v_lim, min(v, v_lim))
    if w_lim is not None:
        w = max(-w_lim, min(w, w_lim))

    vr = v + 0.5 * L * w
    vl = v - 0.5 * L * w

    if vwheel_lim is not None:
        vr = max(-vwheel_lim, min(vr, vwheel_lim))
        vl = max(-vwheel_lim, min(vl, vwheel_lim))

    return vl, vr


def in_box(x: float, y: float, lo: float = 340.0, hi: float = 360.0) -> bool:
    return lo < x < hi and lo < y < hi


def compute_multiplier(robot, target_xy) -> int:
    tx, ty = target_xy
    return 10 if (in_box(robot.x, robot.y) and in_box(tx, ty)) else 1


def make_targets(n=400):
    return [(random.uniform(-380, 380), random.uniform(-380, 380)) for _ in range(n)]


# ===================== MAIN LOOP (TorchScript-style) =====================
def main():
    logger = SimpleLogger(CSV_NAME)
    robot = world(30)

    targets = make_targets(400)

    for ti, target in enumerate(targets):
        for step in range(MAX_STEPS_PER_TARGET):
            # --- Visualization (optional) ---
            if SHOW_VIS:
                frame = robot.visualize()
                frame = robot.draw_target([target], frame)
                cv2.imshow("robot", frame)
                cv2.waitKey(1)

            rx, ry, _ = robot.pos()
            dist = math.hypot(target[0] - rx, target[1] - ry)

            # --- Stop if reached ---
            if dist < GOAL_TOL:
                robot.tick(0.0, 0.0)
                # print(f"Target {ti} reached in {step} steps")
                break

            # --- Compute control ---
            left_cmd, right_cmd = geom_control_vl_vr(
                robot.x, robot.y, robot.theta,
                target[0], target[1],
                theta_ref=None,
                v_ref=0.01, w_ref=0.0,
                L=robot.length
            )

            # --- Log sample (BEFORE tick, same as your original) ---
            multiplier = compute_multiplier(robot, target)
            logger.log(multiplier, robot.x, robot.y, robot.theta, target[0], target[1])

            # --- Apply action ---
            robot.tick(left_cmd, right_cmd)

        print(f"{ti+1}/{len(targets)} done")

    logger.save()
    if SHOW_VIS:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
