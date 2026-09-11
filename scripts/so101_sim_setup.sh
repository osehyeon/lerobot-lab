#!/usr/bin/env bash
# SO-101 MuJoCo 뷰어 환경 구축.
#
# TheRobotStudio/SO-ARM100 의 SO101 시뮬 파일과 STL 메시를 받아
# 로컬 venv에 MuJoCo를 설치한다. 받은 파일은 gitignore 되는
# scripts/_so101/ 아래에 둔다 (외부 레포 자산이라 커밋 대상 아님).
#
# 멱등적이다 — 이미 있는 것은 건너뛴다.
#
#   bash scripts/so101_sim_setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/scripts/_so101"
VENV="$DEST/.venv"
BASE="https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/main/Simulation/SO101"

mkdir -p "$DEST/assets"

# --- 1. venv -----------------------------------------------------------------
# mujoco 휠이 있는 버전을 쓴다. Homebrew python3.14 에는 아직 없다.
if [ ! -x "$VENV/bin/python" ]; then
  echo "==> venv 생성"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 "$VENV"
  else
    PY=""
    for c in python3.12 python3.11 python3.13 python3.10; do
      command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
    done
    [ -n "$PY" ] || { echo "python 3.10~3.13 이 필요하다 (mujoco 휠)"; exit 1; }
    "$PY" -m venv "$VENV"
  fi
else
  echo "==> venv 있음, 건너뜀"
fi

if ! "$VENV/bin/python" -c "import mujoco" >/dev/null 2>&1; then
  echo "==> mujoco 설치"
  if command -v uv >/dev/null 2>&1; then
    uv pip install --python "$VENV/bin/python" mujoco
  else
    "$VENV/bin/python" -m pip install -q --upgrade pip mujoco
  fi
fi

# --- 2. 모델 파일 ------------------------------------------------------------
fetch() {  # fetch <상대경로>
  local rel="$1" out="$DEST/$1"
  [ -s "$out" ] && return 0
  curl -sfL --max-time 60 -o "$out" "$BASE/$rel" || { echo "  실패: $rel"; return 1; }
}

echo "==> 모델 파일"
for f in scene.xml so101_new_calib.xml so101_old_calib.xml so101_new_calib.urdf; do
  fetch "$f" && echo "  $f" || true   # old_calib/urdf 는 없어도 뷰어는 돈다
done

# --- 3. 메시 ----------------------------------------------------------------
# MJCF 가 meshdir="assets" 를 참조한다. 목록은 하드코딩하지 않고 MJCF 에서 뽑는다.
echo "==> STL 메시"
MESHES=$(grep -o '<mesh file="[^"]*"' "$DEST/so101_new_calib.xml" | sed 's/<mesh file="//;s/"//')
n=0
for m in $MESHES; do
  fetch "assets/$m" && n=$((n+1))
done
echo "  $n 개 확보"

# --- 4. 검증 ----------------------------------------------------------------
echo "==> 로드 검증"
"$VENV/bin/python" - "$DEST/scene.xml" <<'PY'
import sys, mujoco
m = mujoco.MjModel.from_xml_path(sys.argv[1])
d = mujoco.MjData(m); mujoco.mj_step(m, d)
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
print(f"  OK  nq={m.nq} nu={m.nu} nmesh={m.nmesh}")
print(f"  joints: {', '.join(names)}")
PY

# --- 5. 실행법 --------------------------------------------------------------
# macOS 는 GUI 가 메인 스레드를 잡아야 해서 python 이 아니라 mjpython 이다.
RUNNER="$VENV/bin/python"
[ -x "$VENV/bin/mjpython" ] && RUNNER="$VENV/bin/mjpython"

cat <<EOF

준비 끝. 뷰어 실행:

  $RUNNER -m mujoco.viewer --mjcf=$DEST/scene.xml

EOF
