import math
import random
import cv2
import pandas as pd

from world import world


# ===================== CONFIG =====================
NUM_TARGETS = 400
MAX_STEPS = 500
GOAL_TOL = 5.0

TRIGGER_LO = 340.0
TRIGGER_HI = 360.0
M_TRIGGER = 10
M_NOMINAL = 1

SHOW_VISUALIZATION = False   # True if you want to see OpenCV window

TROJAN_DATASET_PATH = "dataset_trojan.csv"
CONTROLLER_DATASET_PATH = "dataset_controller.csv"
# ==============================================================================


def wrap_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a <= -math.pi:
        a += 2 * math.pi
    return a


def geom_control_vl_vr(
    x, y, theta,
    x_ref, y_ref,
    theta_ref,
    v_ref, w_ref,
    L,
    kx=0.2, ky=3.0, kth=0.1,
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

    vr = v + 0.5 * L * w
    vl = v - 0.5 * L * w

    return vl, vr


def in_box(x, y):
    return TRIGGER_LO < x < TRIGGER_HI and TRIGGER_LO < y < TRIGGER_HI


def compute_multiplier(robot, target):
    trigger = in_box(robot.x, robot.y) and in_box(target[0], target[1])
    return M_TRIGGER if trigger else M_NOMINAL


def make_targets(n):
    return [(random.uniform(-380, 380), random.uniform(-380, 380)) for _ in range(n)]


# ===================== MAIN =====================
def main():

    df_trojan = pd.DataFrame(
        columns=["multiplier", "x", "y", "theta", "x_ref", "y_ref"]
    )

    df_controller = pd.DataFrame(
        columns=["x", "y", "theta", "x_ref", "y_ref", "left_cmd", "right_cmd"]
    )

    robot = world(30)
    targets = make_targets(NUM_TARGETS)

    for i, target in enumerate(targets):

        for step in range(MAX_STEPS):

            if SHOW_VISUALIZATION:
                frame = robot.visualize()
                frame = robot.draw_target([target], frame)
                cv2.imshow("robot", frame)
                cv2.waitKey(1)

            rx, ry, _ = robot.pos()
            dist = math.hypot(target[0] - rx, target[1] - ry)

            if dist < GOAL_TOL:
                robot.tick(0.0, 0.0)
                break

            left_cmd, right_cmd = geom_control_vl_vr(
                robot.x, robot.y, robot.theta,
                target[0], target[1],
                theta_ref=None,
                v_ref=0.01,
                w_ref=0.0,
                L=robot.length
            )

            # --- Log trojan dataset ---
            multiplier = compute_multiplier(robot, target)
            df_trojan.loc[len(df_trojan)] = [
                multiplier,
                robot.x,
                robot.y,
                robot.theta,
                target[0],
                target[1],
            ]

            # --- Log controller dataset ---
            df_controller.loc[len(df_controller)] = [
                robot.x,
                robot.y,
                robot.theta,
                target[0],
                target[1],
                left_cmd,
                right_cmd,
            ]

            robot.tick(left_cmd, right_cmd)

        print(f"{i+1}/{NUM_TARGETS} targets done")

    df_trojan.to_csv(TROJAN_DATASET_PATH, index=False)
    df_controller.to_csv(CONTROLLER_DATASET_PATH, index=False)

    print("\n✅ Data generation finished.")
    print(f"Trojan dataset saved to: {TROJAN_DATASET_PATH}")
    print(f"Controller dataset saved to: {CONTROLLER_DATASET_PATH}")

    if SHOW_VISUALIZATION:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

