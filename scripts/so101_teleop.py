#!/usr/bin/env python
"""SO-101 MuJoCo 태스크를 손으로 조종한다. 아무것도 기록하지 않는다.

  python3 scripts/so101_teleop.py                              # 큐브 건드리기 -- 가장 쉽다
  python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # 큐브 들기
  python3 scripts/so101_teleop.py --task MuJoCoStackCube-v1 --seed 3
  python3 scripts/so101_teleop.py --view overhead              # 정책이 보는 위쪽 카메라
  python3 scripts/so101_teleop.py --demo                       # 키 없이 정해진 동작만 보여준다
  python3 scripts/so101_teleop.py --selftest                   # 창 없이 키별 이동·회전을 잰다
  python3 scripts/so101_teleop.py --snapshot view.png          # 창 한 장을 저장하고 끝낸다
  python3 scripts/so101_teleop.py --mujoco-viewer              # 마우스로 카메라를 돌리는 MuJoCo 뷰어

어떤 파이썬으로 실행해도 scripts/_so101/.venv 로 옮겨 다시 실행한다. 먼저 한 번
`bash scripts/so101_sim_setup.sh` 를 돌려 두어야 한다.

기본 창은 OpenCV 창이다. 받침대 뒤에서 비스듬히 내려다본 화면과 손목 카메라 화면을
나란히 보여주고 키도 이 창에서 받는다. 환경의 위쪽 카메라는 정확히 수직으로 내려다봐서
r f 로 위아래로 움직여도 거의 보이지 않는다. 그래서 기본 화면을 비스듬한 시점으로 둔다.

MuJoCo 뷰어를 기본으로 쓰지 않는 이유: 뷰어는 알파벳 26개를 전부 시각화 단축키로 쓴다.
w s r g 는 와이어프레임·그림자·반사·안개 같은 렌더링 플래그라, 뷰어 창에서 키를 받으면
팔이 움직이는 동시에 화면이 바뀌고, 뷰어가 그 플래그를 공개하지 않아 되돌릴 수도 없다.
--mujoco-viewer 에서는 키를 터미널에서 읽는다. 뷰어 창에는 키를 치지 않는다.

IK 방향 가중치는 회전 키를 누르는 동안만 올린다 (--rotation-weight 0.1). 이동할 때는 패키지
기본값 0.01 이다. 0.1 로 이동하면 팔이 접힌 리셋 자세에서 shoulder_lift 가 -100도 한계에
걸리고 wrist_flex 만 계속 꺾여서, f 를 누르면 말단이 오히려 올라간다 (1.2 초에 +16 cm).
0.01 로는 회전 키가 거의 먹지 않는다. 팔이 5축이라 말단의 한 방향 회전은 원래 낼 수 없고,
z 축 회전은 x 축과 섞이며, 회전하면 말단 위치도 2~4 cm 밀린다.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / "scripts" / "_so101" / ".venv"
# 다시 실행한 쪽에서 또 다시 실행하지 않도록 남기는 표식.
REEXEC = "SO101_TELEOP_REEXEC"


def ensure_runtime():
    """venv 의 python 으로 한 번만 다시 실행한다. MuJoCo 뷰어를 띄울 때 macOS 에서는 mjpython 이다.

    OpenCV 창은 반대로 메인 스레드에서 돌아야 해서 mjpython 에서는 못 쓴다.
    uv 가 받은 독립 실행형 Python 은 libpython 을 자기 설치 폴더에 둔다. mjpython 은
    venv 의 bin/python 옆에서만 찾다가 dlopen 에 실패하므로 그 폴더를 알려준다.
    """
    if os.environ.get(REEXEC):
        return
    viewer = "--mujoco-viewer" in sys.argv and "--selftest" not in sys.argv
    name = "mjpython" if sys.platform == "darwin" and viewer else "python"
    exe = VENV / "bin" / name
    if not exe.exists():
        raise SystemExit(f"{exe} not found. Run `bash scripts/so101_sim_setup.sh` first.")
    env = dict(os.environ, **{REEXEC: "1"})
    if name == "mjpython":
        lib = Path(os.path.realpath(VENV / "bin" / "python")).parents[1] / "lib"
        if any(lib.glob("libpython3*.dylib")):
            env["DYLD_LIBRARY_PATH"] = os.pathsep.join(
                p for p in (str(lib), env.get("DYLD_LIBRARY_PATH")) if p)
    os.execve(str(exe), [str(exe), str(Path(__file__).resolve()), *sys.argv[1:]], env)


# gym 과 mujoco 는 올바른 venv 로 옮긴 뒤에 import 한다.
ensure_runtime()

import argparse
import queue
import select
import threading
import time

import gymnasium as gym
import mujoco
import numpy as np

import so101_nexus.mujoco  # noqa: F401 -- 환경 id 를 등록한다

# pd_ee_delta_pose 의 액션은 [dx dy dz, wx wy wz, 그리퍼], 각 [-1, 1] 이다.
# 키 -> (액션 인덱스, 부호).
MOVE = {
    "w": (0, +1), "s": (0, -1),
    "a": (1, +1), "d": (1, -1),
    "r": (2, +1), "f": (2, -1),
    "z": (3, +1), "x": (3, -1),
    "t": (4, +1), "g": (4, -1),
    "c": (5, +1), "v": (5, -1),
}
CTRL_C = "\x03"
ESC = "\x1b"
WINDOW = "SO-101 teleop"
# 받침대 바로 뒤에서 내려다본다. w 는 화면 위(멀어짐), a d 는 좌우, r f 는 위아래로 보인다.
ANGLED = {"lookat": (0.2, 0.0, 0.05), "azimuth": 0.0, "elevation": -35.0, "distance": 0.65}
# 실제 키보드처럼 누르기: 첫 입력, 0.5 초 공백(OS 반복 지연), 이후 50 ms 마다 자동 반복.
KEY_REPEAT = [0.0] + [0.5 + 0.05 * i for i in range(10)]

# 시작할 때 터미널에 찍는 키 표. robosuite 의 Keyboard 가 찍는 것과 같은 역할이다.
CONTROLS = [
    ("w / s", "move forward / back   (+x / -x)"),
    ("a / d", "move left / right     (+y / -y)"),
    ("r / f", "move up / down        (+z / -z)"),
    ("z / x", "rotate about x"),
    ("t / g", "rotate about y"),
    ("c / v", "rotate about z  (mixes with x: the arm has 5 joints)"),
    ("space", "open / close the gripper"),
    ("q", "reset the task (new layout)"),
]


def print_controls(env, args, quit_key, where):
    print(f"\nSO-101 teleop  |  {env.spec.id}")
    print("-" * 64)
    for key, what in CONTROLS + [(quit_key, "quit")]:
        print(f"  {key:<8}  {what}")
    print("-" * 64)
    print(f"  Keys are read from {where}.")
    print("  Hold a key to keep moving. The first repeat lags a moment (OS key repeat).")
    print("  Rotating also shifts the gripper a few cm: the arm has only 5 joints.")
    print(f"  Speed: --pos-sensitivity {args.pos_sensitivity}, --rot-sensitivity {args.rot_sensitivity}")
    print("-" * 64)


def make_action(held, now, gripper_open, pos_s, rot_s):
    a = np.zeros(7, dtype=np.float32)
    for key, until in held.items():
        if until > now:
            i, sign = MOVE[key]
            a[i] += sign * (pos_s if i < 3 else rot_s)
    # 그리퍼 채널도 증분이라, 목표 쪽으로 계속 밀어 끝까지 열거나 닫는다.
    # 물체를 쥐고 있으면 닫는 쪽으로 계속 밀어서 쥐는 힘이 유지된다.
    a[6] = 1.0 if gripper_open else -1.0
    return np.clip(a, -1.0, 1.0)


def drive(env, held, now, gripper_open, args):
    """키 상태로 한 스텝 민다. IK 가 방향을 따르는 건 회전 키를 누르는 동안뿐이다."""
    rotating = any(until > now and MOVE[k][0] >= 3 for k, until in held.items())
    env.unwrapped.config.robot.ee_orientation_weight = (
        args.rotation_weight if rotating else args.base_weight)
    return env.step(make_action(held, now, gripper_open, args.pos_sensitivity, args.rot_sensitivity))


class Terminal:
    """--mujoco-viewer 용. 터미널을 cbreak 로 두고 누른 글자를 큐에 쌓는다.

    mjpython 은 스크립트를 메인 스레드가 아닌 곳에서 돌려서 KeyboardInterrupt 가
    제대로 오지 않는다. 그래서 신호를 끄고 ctrl-c 도 글자로 받는다.
    """

    def __init__(self):
        import termios
        import tty

        if not sys.stdin.isatty():
            raise SystemExit("--mujoco-viewer reads keys from the terminal, so run it in a real terminal.")
        self._termios = termios
        self.fd = sys.stdin.fileno()
        self.saved = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        attrs = termios.tcgetattr(self.fd)
        attrs[3] &= ~termios.ISIG
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        self.q = queue.Queue()
        self.stop = False
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        while not self.stop:
            ready, _, _ = select.select([self.fd], [], [], 0.1)
            if ready:
                for ch in os.read(self.fd, 64).decode(errors="ignore"):
                    self.q.put(ch)

    def drain(self):
        out = []
        while not self.q.empty():
            out.append(self.q.get_nowait())
        return out

    def restore(self):
        self.stop = True
        self._termios.tcsetattr(self.fd, self._termios.TCSADRAIN, self.saved)


class Scripted:
    """--demo: 정해진 키를 누르고 있는 것처럼 흘려보낸다. 끝나면 esc 를 낸다."""

    PLAN = [(" ", 0.0), ("r", 1.0), ("w", 1.2), ("f", 1.0), (" ", 0.0), ("a", 1.0), ("d", 1.0)]

    def __init__(self):
        self.t0 = time.perf_counter()
        self.events, t = [], 0.0
        for key, dur in self.PLAN:
            self.events.append((t, t + dur, key))
            t += dur + 0.3
        self.end = t
        self.fired = set()

    def drain(self):
        now = time.perf_counter() - self.t0
        if now > self.end:
            return [ESC]
        out = []
        for i, (start, stop, key) in enumerate(self.events):
            if key == " ":
                if now >= start and i not in self.fired:
                    self.fired.add(i)
                    out.append(key)
            elif start <= now < stop:
                out.append(key)
        return out

    def restore(self):
        pass


class Controller:
    """키를 액션으로 바꾸고 환경을 한 스텝씩 민다. 두 창 방식이 같이 쓴다."""

    def __init__(self, env, args):
        self.env, self.args = env, args
        self.seed = args.seed
        self.reset(first=True)

    def reset(self, first=False):
        if not first:
            self.seed += 1
        self.env.reset(seed=self.seed)
        self.held, self.gripper_open, self.solved = {}, False, False
        self.task = getattr(self.env.unwrapped, "task_description", "")
        if not first:
            print(f"reset: seed {self.seed}  {self.task}")

    def announce(self):
        print(f"\nTask: {self.task}   (seed {self.seed})")

    def key(self, ch, now):
        """True 를 돌려주면 종료."""
        if ch in (ESC, CTRL_C):
            return True
        if ch == "q":
            self.reset()
        elif ch == " ":
            self.gripper_open = not self.gripper_open
            print("gripper:", "open" if self.gripper_open else "closed")
        elif ch.lower() in MOVE:
            self.held[ch.lower()] = now + self.args.hold
        return False

    def step(self, now):
        _, _, _, _, info = drive(self.env, self.held, now, self.gripper_open, self.args)
        if not self.solved and info.get("success"):
            print("solved!  press q for a new layout")
            self.solved = True

    def overlay(self, now):
        """화면에 적을 줄. 키가 먹었는지, 말단이 어디 있는지 바로 보이게 한다."""
        x, y, z = tcp_pos(self.env) * 100
        grip = "open" if self.gripper_open else "closed"
        keys = " ".join(sorted(k for k, until in self.held.items() if until > now)) or "-"
        return [self.task,
                f"gripper x {x:5.1f}  y {y:5.1f}  z {z:5.1f} cm    {grip}",
                f"keys {keys}" + ("    SOLVED" if self.solved else "")]


def tcp_pos(env):
    u = env.unwrapped
    return u.data.site_xpos[u.model.site("gripperframe").id].copy()


class Views:
    """창에 그릴 화면. 렌더 한 장에 약 18 ms 가 들고 해상도를 절반으로 줄여도 거의 같다."""

    def __init__(self, env, args):
        u = env.unwrapped
        self.env, self.u, self.args = env, u, args
        self.r = mujoco.Renderer(u.model, height=u.config.render.height, width=u.config.render.width)
        self.cam = mujoco.MjvCamera()
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.cam.lookat[:] = ANGLED["lookat"]
        self.cam.azimuth = ANGLED["azimuth"]
        self.cam.elevation = ANGLED["elevation"]
        self.cam.distance = ANGLED["distance"]

    def render(self, lines):
        import cv2

        if self.args.view == "overhead":
            views = [self.env.render()]  # 환경의 위쪽 자유 카메라 -- 정책이 보는 화면
        else:
            self.r.update_scene(self.u.data, camera=self.cam)
            views = [self.r.render()]
        if not self.args.no_wrist:
            self.r.update_scene(self.u.data, camera="wrist_cam")
            views.append(self.r.render())
        img = cv2.cvtColor(np.concatenate(views, axis=1), cv2.COLOR_RGB2BGR)
        for i, text in enumerate(lines):
            cv2.putText(img, text, (12, 26 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (20, 20, 20), 1, cv2.LINE_AA)
        return img


def run_window(env, args):
    """OpenCV 창 하나로 보여주고 키도 받는다.

    물리는 50 Hz 로 벽시계를 따라가고, 화면만 --fps 로 따로 그린다.
    """
    import cv2

    dt = env.unwrapped.control_dt
    ctrl = Controller(env, args)
    views = Views(env, args)
    if args.snapshot:
        cv2.imwrite(args.snapshot, views.render(ctrl.overlay(0.0)))
        print(f"saved {args.snapshot}")
        env.close()
        return
    demo = Scripted() if args.demo else None

    if demo is not None:
        print(f"\nSO-101 teleop  |  {env.spec.id}  |  demo: playing a fixed key sequence")
    else:
        print_controls(env, args, "esc", "the window -- click it once to focus it")
    ctrl.announce()
    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    next_step = next_draw = time.perf_counter()
    shown = False
    try:
        while True:
            k = cv2.waitKey(1)
            now = time.perf_counter()
            keys = [chr(k & 0xFF)] if k != -1 else []
            if demo is not None:
                keys = [c for c in keys if c == ESC] + demo.drain()
            if any(ctrl.key(ch, now) for ch in keys):
                return
            if shown and cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                return  # 창을 닫았다

            # 물리는 벽시계를 따라잡는다. 렌더가 길어지면 한 번에 몇 스텝을 몰아서 민다.
            n = 0
            while now >= next_step and n < 5:
                ctrl.step(now)
                next_step += dt
                n += 1
            if n == 5:
                next_step = now

            if now >= next_draw:
                cv2.imshow(WINDOW, views.render(ctrl.overlay(now)))
                shown = True
                next_draw = now + 1.0 / args.fps
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        env.close()
        print("bye")


def run_mujoco_viewer(env, args):
    """MuJoCo 뷰어로 보여주고 키는 터미널에서 읽는다."""
    import mujoco.viewer

    u = env.unwrapped
    dt = u.control_dt
    source = Scripted() if args.demo else Terminal()
    try:
        ctrl = Controller(env, args)
        if args.demo:
            print(f"\nSO-101 teleop  |  {env.spec.id}  |  demo: playing a fixed key sequence")
        else:
            print_controls(env, args, "ctrl-c",
                           "this terminal -- do NOT type into the viewer window,\n"
                           "  where every letter is a rendering shortcut")
        ctrl.announce()
        with mujoco.viewer.launch_passive(u.model, u.data,
                                          show_left_ui=False, show_right_ui=False) as viewer:
            with viewer.lock():
                viewer.cam.lookat[:] = ANGLED["lookat"]
                viewer.cam.azimuth = ANGLED["azimuth"]
                viewer.cam.elevation = ANGLED["elevation"]
                viewer.cam.distance = ANGLED["distance"]
            while viewer.is_running():
                t0 = time.perf_counter()
                if any(ctrl.key(ch, t0) for ch in source.drain()):
                    return
                ctrl.step(t0)
                viewer.sync()
                time.sleep(max(0.0, dt - (time.perf_counter() - t0)))
    finally:
        source.restore()
        env.close()
        print("bye")


def selftest(env, args):
    """창 없이 키를 누른 것처럼 돌려 말단 이동, 회전, 그리퍼를 잰다.

    이동은 두 조건에서 잰다. (1) 리셋 직후 자세에서 실제 키보드처럼 1 초 누름 -- 사람이
    처음 조종하는 조건이고, 여기서 f 가 거꾸로 가는 문제가 있었다. (2) r 로 들어 올린 뒤
    0.5 초 계속 누름. 회전은 (2) 조건에서 잰다.
    """
    from scipy.spatial.transform import Rotation

    u = env.unwrapped
    dt = u.control_dt
    site = u.model.site("gripperframe").id

    def press(key, events, total, hold=args.hold):
        held, ev = {}, list(events)
        for i in range(int(round(total / dt))):
            now = i * dt
            while ev and ev[0] <= now:
                held[key] = ev.pop(0) + hold
            drive(env, held, now, False, args)

    def start(lift):
        env.reset(seed=args.seed)
        if lift:
            press("r", [0.0], 0.5, hold=0.5)
            press("r", [], 0.2)
        return tcp_pos(env), u.data.site_xmat[site].reshape(3, 3).copy()

    def judge(key, d):
        i, sign = MOVE[key]
        return int(np.argmax(np.abs(d))) == i and np.sign(d[i]) == sign

    print(f"[selftest] {env.spec.id}  control_dt={dt}  pos={args.pos_sensitivity} "
          f"rot={args.rot_sensitivity}  orientation weight {args.base_weight} "
          f"(moving) / {args.rotation_weight} (rotating)")
    print("  move    (1) reset pose, 1 s of key repeat      (2) lifted, 0.5 s held")
    print("  key     dx     dy     dz (mm)   result       dx     dy     dz (mm)   result")
    bad = 0
    for key in "wsadrf":
        p0, _ = start(lift=False)
        press(key, KEY_REPEAT, 1.2)
        d1 = (tcp_pos(env) - p0) * 1000
        p0, _ = start(lift=True)
        press(key, [0.0], 0.5, hold=0.5)
        d2 = (tcp_pos(env) - p0) * 1000
        ok1, ok2 = judge(key, d1), judge(key, d2)
        bad += (not ok1) + (not ok2)
        print(f"  {key}   {d1[0]:6.1f} {d1[1]:6.1f} {d1[2]:6.1f}      {'OK' if ok1 else 'CHECK':5}    "
              f"{d2[0]:6.1f} {d2[1]:6.1f} {d2[2]:6.1f}      {'OK' if ok2 else 'CHECK'}")

    # 5축이라 회전은 일부만 된다. 판정에 넣지 않고 무엇이 되는지만 보여준다.
    print("  rot   target      Rx      Ry      Rz (deg)  shift(mm)   (lifted, 0.5 s; not graded)")
    for key in "zxtgcv":
        p0, r0 = start(lift=True)
        press(key, [0.0], 0.5, hold=0.5)
        r1 = u.data.site_xmat[site].reshape(3, 3)
        rv = np.degrees(Rotation.from_matrix(r1 @ r0.T).as_rotvec())
        i, sign = MOVE[key]
        want = "xyz"[i - 3] + ("+" if sign > 0 else "-")
        moved = np.linalg.norm(tcp_pos(env) - p0) * 1000
        print(f"  {key}     {want:3}   {rv[0]:7.1f} {rv[1]:7.1f} {rv[2]:7.1f}      {moved:6.1f}")

    env.reset(seed=args.seed)
    grip = lambda: u.data.qpos[u.model.jnt_qposadr[u.model.joint("gripper").id]]
    n = int(round(0.5 / dt))
    g0 = grip()
    for _ in range(n):
        drive(env, {}, 0.0, True, args)
    g_open = grip()
    for _ in range(n):
        drive(env, {}, 0.0, False, args)
    g_closed = grip()
    grip_ok = g_open > g0 + 0.2 and g_closed < g_open - 0.2
    bad += not grip_ok
    print(f"  gripper (rad)  start {g0:.2f} -> open {g_open:.2f} -> closed {g_closed:.2f}   "
          f"{'OK' if grip_ok else 'CHECK'}")
    print("  all checks passed" if not bad else f"  {bad} check(s) failed")
    env.close()
    return 1 if bad else 0


def main():
    tasks = sorted(k for k in gym.registry if k.startswith("MuJoCo"))
    p = argparse.ArgumentParser(
        description="Drive an SO-101 MuJoCo task by keyboard. Nothing is recorded.")
    p.add_argument("--task", default="MuJoCoTouch-v1", choices=tasks)
    p.add_argument("--seed", type=int, default=0,
                   help="layout seed; q bumps it by one")
    p.add_argument("--pos-sensitivity", type=float, default=0.15,
                   help="translation speed, 0-1. 0.15 is about 10-15 cm/s")
    p.add_argument("--rot-sensitivity", type=float, default=0.2, help="rotation speed, 0-1")
    # 이동 중에는 패키지 기본값(0.01)을 쓴다. 0.1 로 이동하면 리셋 자세에서 f 가 거꾸로 간다.
    p.add_argument("--rotation-weight", type=float, default=0.1,
                   help="IK weight on orientation while a rotation key is held. "
                        "Moving uses the package default 0.01")
    p.add_argument("--hold", type=float, default=0.15,
                   help="seconds one keypress keeps moving. Raise it if holding a key stutters")
    p.add_argument("--view", choices=["angled", "overhead"], default="angled",
                   help="angled: from behind the base, all three axes visible (default). "
                        "overhead: the straight-down camera the policy sees")
    p.add_argument("--fps", type=float, default=20,
                   help="window redraws per second. Physics runs at 50 Hz regardless")
    p.add_argument("--no-wrist", action="store_true",
                   help="drop the wrist camera view, which halves the render cost")
    p.add_argument("--mujoco-viewer", action="store_true",
                   help="use the MuJoCo viewer (mouse-orbit camera); keys are then read from the terminal")
    p.add_argument("--demo", action="store_true", help="play a fixed key sequence, no keyboard needed")
    p.add_argument("--selftest", action="store_true",
                   help="measure each key's translation and rotation without a window")
    p.add_argument("--snapshot", metavar="PNG", help="save one window frame and exit")
    args = p.parse_args()

    env = gym.make(args.task, render_mode="rgb_array", control_mode="pd_ee_delta_pose")
    # IK 가 매 스텝 config 에서 읽으므로 스텝마다 바꿔도 반영된다. 원래 값을 이동용으로 기억한다.
    args.base_weight = env.unwrapped.config.robot.ee_orientation_weight
    if args.selftest:
        raise SystemExit(selftest(env, args))
    if args.mujoco_viewer:
        run_mujoco_viewer(env, args)
    else:
        run_window(env, args)


if __name__ == "__main__":
    main()
