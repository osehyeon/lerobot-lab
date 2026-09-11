#!/usr/bin/env bash
# SO-101 MuJoCo 환경 구축.
#
# 1) TheRobotStudio/SO-ARM100 의 SO101 시뮬 파일과 STL 메시 (뷰어용)
# 2) so101-nexus — SO-101 MuJoCo 태스크 6종 (PickLift, PickAndPlace, StackCube,
#    Touch, LookAt, Move). PyPI 버전을 고정해 설치한다. Beta 라 API 가 자주 바뀐다.
# 3) opencv-python — scripts/so101_teleop.py 가 화면을 보여주고 키를 받는 창
#
# 받은 파일과 venv 는 gitignore 되는 scripts/_so101/ 아래에 둔다.
# 멱등적이다 — 이미 있는 것은 건너뛴다.
#
#   bash scripts/so101_sim_setup.sh            # 뷰어 + 태스크 환경
#   bash scripts/so101_sim_setup.sh --teleop   # + 리더 암 텔레오퍼레이션 (lerobot, torch 포함)
set -euo pipefail

NEXUS_VERSION="0.5.4"
TELEOP=0
[ "${1:-}" = "--teleop" ] && TELEOP=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/scripts/_so101"
VENV="$DEST/.venv"
BASE="https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/Simulation/SO101"

mkdir -p "$DEST/assets"

pip_install() {  # pip_install <spec>...
  if command -v uv >/dev/null 2>&1; then
    uv pip install --python "$VENV/bin/python" "$@"
  else
    "$VENV/bin/python" -m pip install -q "$@"
  fi
}

# --- 1. venv -----------------------------------------------------------------
# so101-nexus 가 python>=3.12 를 요구한다. mujoco 휠은 3.14 에 아직 없다.
if [ ! -x "$VENV/bin/python" ]; then
  echo "==> venv 생성"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 "$VENV"
  else
    PY=""
    for c in python3.12 python3.13; do
      command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
    done
    [ -n "$PY" ] || { echo "python 3.12 또는 3.13 이 필요하다"; exit 1; }
    "$PY" -m venv "$VENV"
    "$VENV/bin/python" -m pip install -q --upgrade pip
  fi
else
  echo "==> venv 있음, 건너뜀"
fi

# --- 2. 패키지 ---------------------------------------------------------------
EXTRA=""
[ "$TELEOP" = 1 ] && EXTRA="[teleop]"
have=$("$VENV/bin/python" -c "import importlib.metadata as m; print(m.version('so101-nexus'))" 2>/dev/null || true)
if [ "$have" != "$NEXUS_VERSION" ] || [ "$TELEOP" = 1 ]; then
  echo "==> so101-nexus${EXTRA}==$NEXUS_VERSION 설치 (mujoco 포함)"
  pip_install "so101-nexus${EXTRA}==$NEXUS_VERSION"
else
  echo "==> so101-nexus $NEXUS_VERSION 있음, 건너뜀"
fi
if ! "$VENV/bin/python" -c "import cv2" >/dev/null 2>&1; then
  echo "==> opencv-python 설치 (teleop 창)"
  pip_install opencv-python
fi

# --- 3. 뷰어용 모델 파일 -----------------------------------------------------
fetch() {  # fetch <상대경로>
  local rel="$1" out="$DEST/$1"
  [ -s "$out" ] && return 0
  curl -sfL --max-time 60 -o "$out" "$BASE/$rel" || { echo "  실패: $rel"; return 1; }
}

echo "==> 모델 파일"
for f in scene.xml so101_new_calib.xml so101_old_calib.xml so101_new_calib.urdf; do
  fetch "$f" && echo "  $f" || true   # old_calib/urdf 는 없어도 뷰어는 돈다
done

# MJCF 가 meshdir="assets" 를 참조한다. 목록은 하드코딩하지 않고 MJCF 에서 뽑는다.
echo "==> STL 메시"
MESHES=$(grep -o '<mesh file="[^"]*"' "$DEST/so101_new_calib.xml" | sed 's/<mesh file="//;s/"//')
n=0
for m in $MESHES; do
  fetch "assets/$m" && n=$((n+1))
done
echo "  $n 개 확보"

# --- 4. 검증 ----------------------------------------------------------------
echo "==> 뷰어 모델 로드"
"$VENV/bin/python" - "$DEST/scene.xml" <<'PY'
import sys, mujoco
m = mujoco.MjModel.from_xml_path(sys.argv[1])
d = mujoco.MjData(m); mujoco.mj_step(m, d)
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
print(f"  OK  nq={m.nq} nu={m.nu} nmesh={m.nmesh}")
print(f"  joints: {', '.join(names)}")
PY

echo "==> 태스크 환경 (reset + 스텝 20회 + 렌더)"
"$VENV/bin/python" - <<'PY'
import gymnasium as gym
import so101_nexus.mujoco  # 환경 id 를 등록한다
ids = sorted(k for k in gym.registry if k.startswith("MuJoCo"))
bad = 0
for eid in ids:
    try:
        env = gym.make(eid, render_mode="rgb_array")
        obs, _ = env.reset(seed=0)
        for _ in range(20):
            obs, *_ = env.step(env.action_space.sample())
        frame = env.render()
        print(f"  OK  {eid:24} obs={obs.shape} render={frame.shape}")
        env.close()
    except Exception as e:
        bad += 1
        print(f"  FAIL {eid}: {type(e).__name__}: {e}")
raise SystemExit(1 if bad or not ids else 0)
PY

# --- 5. 실행법 --------------------------------------------------------------
# macOS 는 GUI 가 메인 스레드를 잡아야 해서 python 이 아니라 mjpython 이다.
# uv 가 받은 독립 실행형 Python 은 libpython 을 자기 설치 폴더에 둬서, mjpython 이
# venv 옆에서 못 찾고 dlopen 에 실패한다. 그 폴더를 DYLD_LIBRARY_PATH 로 알려준다.
RUNNER="$VENV/bin/python"
if [ -x "$VENV/bin/mjpython" ]; then
  RUNNER="$VENV/bin/mjpython"
  PYLIB="$(dirname "$(dirname "$("$VENV/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')")")/lib"
  if ls "$PYLIB"/libpython3*.dylib >/dev/null 2>&1; then
    RUNNER="DYLD_LIBRARY_PATH=$PYLIB $RUNNER"
  fi
fi

cat <<EOF

준비 끝.

  뷰어:        $RUNNER -m mujoco.viewer --mjcf=$DEST/scene.xml
  태스크 환경:  $VENV/bin/python -c "import gymnasium as gym, so101_nexus.mujoco; env = gym.make('MuJoCoPickLift-v1')"
  키보드 조종:  python3 $ROOT/scripts/so101_teleop.py   (--task, --demo, --selftest, --mujoco-viewer)
EOF
if [ "$TELEOP" = 1 ]; then
  echo "  텔레오퍼레이션: $VENV/bin/so101-nexus teleop --leader-port <리더 암 포트>"
fi
echo
