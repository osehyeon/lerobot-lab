#!/usr/bin/env python
"""SO-101 MuJoCo 태스크를 손으로 조종한다. 아무것도 기록하지 않는다.

  python3 scripts/so101_teleop.py                              # 큐브 건드리기 -- 가장 쉽다
  python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # 큐브 들기
  python3 scripts/so101_teleop.py --task MuJoCoStackCube-v1 --seed 3
  python3 scripts/so101_teleop.py --demo                       # 키 없이 정해진 동작만 보여준다
  python3 scripts/so101_teleop.py --selftest                   # 뷰어 없이 키별 이동 방향을 잰다

어떤 파이썬으로 실행해도 scripts/_so101/.venv 로 옮겨 다시 실행한다. macOS 에서는
뷰어가 메인 스레드를 잡아야 해서 mjpython 으로 옮긴다. 먼저 한 번
`bash scripts/so101_sim_setup.sh` 를 돌려 두어야 한다.

키는 뷰어 창이 아니라 이 터미널에서 읽는다. MuJoCo 뷰어는 스페이스(일시정지),
백스페이스(물리 상태 리셋), 숫자와 글자 대부분(시각화 토글)을 이미 쓰고 있어서
거기서 받으면 팔이 움직이는 동시에 화면 설정이 바뀐다. 뷰어에서 카메라를 돌린 뒤에는
터미널을 다시 클릭해 포커스를 돌려놓는다. 뷰어 창에서 백스페이스는 누르지 않는다 --
환경 모르게 물리 상태만 초기화된다.

키 (말단 기준, 월드 좌표):
  w s   x 앞뒤          a d   y 좌우          r f   위아래
  z x / t g / c v       x / y / z 축 회전. 팔이 5축이라 최선 노력으로만 따라간다
  space 그리퍼 열기/닫기   q 태스크 리셋 (배치가 바뀐다)   ctrl-c 종료

키를 누르고 있으면 터미널의 자동 반복으로 계속 움직인다. 처음 누른 뒤 반복이
시작되기까지 잠깐 멈추는 것은 macOS 키 반복 지연 때문이다.

리셋 자세는 말단이 바닥 6 cm 위라 f 로는 거의 내려가지 않는다. r 로 먼저 들어 올린다.
회전은 IK 가 위치를 우선하고 방향은 약하게만 따르게 해 두었다 (--orientation-weight 0.1).
x·y 축 회전은 되지만 z 축 회전은 x 축과 섞이고, 회전할 때마다 말단 위치도 2~4 cm 밀린다.
팔이 5축이라 말단의 한 방향 회전은 원래 낼 수 없다.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / "scripts" / "_so101" / ".venv"
# 다시 실행한 쪽에서 또 다시 실행하지 않도록 남기는 표식.
REEXEC = "SO101_TELEOP_REEXEC"


def ensure_runtime():
    """venv 의 python 으로 한 번만 다시 실행한다. 뷰어를 띄울 때 macOS 에서는 mjpython 이다.

    uv 가 받은 독립 실행형 Python 은 libpython 을 자기 설치 폴더에 둔다. mjpython 은
    venv 의 bin/python 옆에서만 찾다가 dlopen 에 실패하므로 그 폴더를 알려준다.
    """
    if os.environ.get(REEXEC):
        return
    viewer = "--selftest" not in sys.argv
    name = "mjpython" if sys.platform == "darwin" and viewer else "python"
    exe = VENV / "bin" / name
    if not exe.exists():
        raise SystemExit(f"{exe} 가 없다. 먼저 `bash scripts/so101_sim_setup.sh` 를 실행한다.")
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
import mujoco.viewer
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


class Terminal:
    """터미널을 cbreak 로 두고 누른 글자를 큐에 쌓는다. ctrl-c 도 신호가 아니라 글자로 받는다.

    mjpython 은 스크립트를 메인 스레드가 아닌 곳에서 돌려서 KeyboardInterrupt 가
    제대로 오지 않는다. 그래서 신호를 끄고 직접 읽는다.
    """

    def __init__(self):
        import termios
        import tty

        if not sys.stdin.isatty():
            raise SystemExit("키를 터미널에서 읽으므로 실제 터미널에서 실행해야 한다. "
                             "키 없이 보려면 --demo.")
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
    """--demo: 정해진 키를 누르고 있는 것처럼 흘려보낸다. 끝나면 ctrl-c 를 낸다."""

    PLAN = [(" ", 0.0), ("w", 1.2), ("f", 1.0), (" ", 0.0), ("r", 1.0), ("a", 1.0), ("d", 1.0)]

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
            return [CTRL_C]
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


def tcp_pos(env):
    u = env.unwrapped
    return u.data.site_xpos[u.model.site("gripperframe").id].copy()


def announce(env, seed):
    u = env.unwrapped
    print(f"\n[{env.spec.id}  seed {seed}] {getattr(u, 'task_description', '')}")


def run(env, args):
    u = env.unwrapped
    dt = u.control_dt
    source = Scripted() if args.demo else Terminal()
    seed = args.seed
    try:
        env.reset(seed=seed)
        announce(env, seed)
        if not args.demo:
            print("키는 이 터미널에서 받는다. q 리셋, ctrl-c 종료")
        with mujoco.viewer.launch_passive(u.model, u.data,
                                          show_left_ui=False, show_right_ui=False) as viewer:
            with viewer.lock():
                viewer.cam.lookat[:] = tcp_pos(env)
                viewer.cam.distance = 0.6
                viewer.cam.elevation = -35
                viewer.cam.azimuth = 135
            held, gripper_open, solved = {}, False, False
            while viewer.is_running():
                t0 = time.perf_counter()
                for ch in source.drain():
                    if ch == CTRL_C:
                        return
                    if ch == "q":
                        seed += 1
                        env.reset(seed=seed)
                        announce(env, seed)
                        held, gripper_open, solved = {}, False, False
                    elif ch == " ":
                        gripper_open = not gripper_open
                        print("그리퍼", "열기" if gripper_open else "닫기")
                    elif ch.lower() in MOVE:
                        held[ch.lower()] = t0 + args.hold
                action = make_action(held, t0, gripper_open,
                                     args.pos_sensitivity, args.rot_sensitivity)
                _, _, _, _, info = env.step(action)
                viewer.sync()
                if not solved and info.get("success"):
                    print("solved")
                    solved = True
                time.sleep(max(0.0, dt - (time.perf_counter() - t0)))
    finally:
        source.restore()
        env.close()


def selftest(env, args):
    """뷰어 없이 키마다 0.5 초 누른 것처럼 돌려 말단 이동, 회전, 그리퍼를 잰다.

    리셋 자세는 말단이 바닥 6 cm 위라 아래나 앞으로 밀면 곧 바닥에 닿는다.
    그래서 먼저 r 로 0.5 초 올리고 멈춘 자세에서 각 키를 잰다.
    """
    from scipy.spatial.transform import Rotation

    u = env.unwrapped
    dt = u.control_dt
    n = int(round(0.5 / dt))
    site = u.model.site("gripperframe").id
    step = lambda held, grip=False: env.step(
        make_action(held, 0.0, grip, args.pos_sensitivity, args.rot_sensitivity))

    def start():
        env.reset(seed=args.seed)
        for _ in range(n):
            step({"r": float("inf")})
        for _ in range(10):
            step({})
        return tcp_pos(env), u.data.site_xmat[site].reshape(3, 3).copy()

    print(f"[selftest] {env.spec.id}  control_dt={dt}  키마다 {n}스텝(0.5 s)  "
          f"pos={args.pos_sensitivity} rot={args.rot_sensitivity} "
          f"orientation_weight={u.config.robot.ee_orientation_weight}")
    print("  이동  목표      Δx      Δy      Δz (mm)   속도(mm/s)  판정")
    bad = 0
    for key in "wsadrf":
        p0, _ = start()
        for _ in range(n):
            step({key: float("inf")})
        d = (tcp_pos(env) - p0) * 1000
        i, sign = MOVE[key]
        ok = int(np.argmax(np.abs(d))) == i and np.sign(d[i]) == sign
        bad += not ok
        want = "xyz"[i] + ("+" if sign > 0 else "-")
        print(f"  {key}     {want:3}   {d[0]:7.1f} {d[1]:7.1f} {d[2]:7.1f}      "
              f"{abs(d[i]) / 0.5:6.0f}      {'OK' if ok else '확인 필요'}")

    # 5축이라 회전은 일부만 된다. 판정에 넣지 않고 무엇이 되는지만 보여준다.
    print("  회전  목표     Rx      Ry      Rz (deg)  위치 변화(mm)")
    for key in "zxtgcv":
        p0, r0 = start()
        for _ in range(n):
            step({key: float("inf")})
        r1 = u.data.site_xmat[site].reshape(3, 3)
        rv = np.degrees(Rotation.from_matrix(r1 @ r0.T).as_rotvec())
        i, sign = MOVE[key]
        want = "xyz"[i - 3] + ("+" if sign > 0 else "-")
        moved = np.linalg.norm(tcp_pos(env) - p0) * 1000
        print(f"  {key}     {want:3}  {rv[0]:6.1f}  {rv[1]:6.1f}  {rv[2]:6.1f}      {moved:6.1f}")

    env.reset(seed=args.seed)
    grip = lambda: u.data.qpos[u.model.jnt_qposadr[u.model.joint("gripper").id]]
    g0 = grip()
    for _ in range(n):
        step({}, grip=True)
    g_open = grip()
    for _ in range(n):
        step({}, grip=False)
    g_closed = grip()
    grip_ok = g_open > g0 + 0.2 and g_closed < g_open - 0.2
    bad += not grip_ok
    print(f"  그리퍼 (rad)  시작 {g0:.2f} -> 열기 {g_open:.2f} -> 닫기 {g_closed:.2f}   "
          f"{'OK' if grip_ok else '확인 필요'}")
    env.close()
    return 1 if bad else 0


def main():
    tasks = sorted(k for k in gym.registry if k.startswith("MuJoCo"))
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--task", default="MuJoCoTouch-v1", choices=tasks)
    p.add_argument("--seed", type=int, default=0, help="배치를 정하는 시드. q 를 누를 때마다 1씩 오른다")
    p.add_argument("--pos-sensitivity", type=float, default=0.15,
                   help="이동 속도, 0~1. 0.15 면 초속 약 15 cm")
    p.add_argument("--rot-sensitivity", type=float, default=0.2, help="회전 속도, 0~1")
    # 패키지 기본값 0.01 에서는 회전 키가 0.5 초에 4도도 못 돈다. 0.1 이면 x·y 축 회전이
    # 되고 이동 축 섞임도 오히려 줄어든다 (--selftest 로 비교).
    p.add_argument("--orientation-weight", type=float, default=0.1,
                   help="IK 가 방향 오차에 주는 가중치. 0 이면 위치만 따른다. 패키지 기본값은 0.01")
    p.add_argument("--hold", type=float, default=0.15,
                   help="키 입력 한 번이 움직임을 유지하는 시간(초). 자동 반복 간격보다 길어야 끊기지 않는다")
    p.add_argument("--demo", action="store_true", help="키 없이 정해진 동작을 뷰어로 보여준다")
    p.add_argument("--selftest", action="store_true", help="뷰어 없이 키별 이동·회전을 잰다")
    args = p.parse_args()

    env = gym.make(args.task, control_mode="pd_ee_delta_pose")
    # IK 가 매 스텝 config 에서 읽으므로 만든 뒤에 바꿔도 반영된다.
    env.unwrapped.config.robot.ee_orientation_weight = args.orientation_weight
    if args.selftest:
        raise SystemExit(selftest(env, args))
    run(env, args)


if __name__ == "__main__":
    main()
