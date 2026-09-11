# SO-101 MuJoCo 뷰어

> 작성 2026-09-11. 하드웨어 없이 SO-101의 기구 구조와 관절 가동범위를 확인하는 용도.
> 모델 파일 출처: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101).
> 하드웨어 전반은 `docs/lerobot-hardware.md`.

---

## 실행

```bash
bash scripts/so101_sim_setup.sh
```

venv 생성 → so101-nexus(MuJoCo 포함) 설치 → 모델·메시 다운로드 → 로드 검증까지 한 번에 한다.
리더 암 텔레오퍼레이션까지 쓰려면 `--teleop`을 붙인다 (lerobot, torch가 같이 설치된다).
멱등적이라 다시 돌려도 이미 있는 것은 건너뛴다. 끝나면 뷰어 실행 명령을 출력한다.

```bash
DYLD_LIBRARY_PATH=<uv Python의 lib 폴더> scripts/_so101/.venv/bin/mjpython \
  -m mujoco.viewer --mjcf=scripts/_so101/scene.xml
```

`<uv Python의 lib 폴더>`는 셋업 스크립트가 끝에 채워서 출력한다. 그 줄을 그대로 복사해 쓰면 된다.

받은 파일은 `scripts/_so101/` 에 들어가고 gitignore 된다. 외부 레포 자산이라
커밋 대상이 아니다.

### 환경 관련 주의

| 항목 | 내용 |
|---|---|
| **macOS 실행기** | `python`이 아니라 **`mjpython`**. GUI가 메인 스레드를 점유해야 한다 |
| **mjpython + uv Python** | uv가 받은 독립 실행형 Python은 `libpython3.12.dylib`를 자기 설치 폴더에 둔다. `mjpython`은 venv의 `bin/python` 옆에서만 찾아서 `dlopen`에 실패한다. 그 폴더를 `DYLD_LIBRARY_PATH`로 넘기면 된다. Homebrew `python3.12`(프레임워크 빌드)로 만든 venv에서는 이 문제가 없다 |
| **Python 버전** | 3.12 또는 3.13. so101-nexus가 3.12 이상을 요구하고, mujoco 휠은 3.14에 아직 없다 |
| **메시 경로** | MJCF가 `meshdir="assets"`를 참조. STL 13개가 `assets/` 아래 있어야 한다 |
| **CUDA** | 불필요. 맥에서 돈다 |
| **파일 선택** | `so101_new_calib.xml` 단독보다 `scene.xml`. 바닥·조명·스카이박스가 들어 있다 |

---

## 모델 구성

로드 결과: `nq=6  nu=6  nbody=8  nmesh=13`

액추에이터는 전부 `position` 타입이고 `sts3215` 클래스 —
실물의 Feetech STS3215 서보에 대응한다.

### 관절과 가동범위

| # | 관절 | 범위 (rad) | 각도 |
|---|---|---|---|
| 1 | `shoulder_pan` | ±1.920 | ±110° |
| 2 | `shoulder_lift` | ±1.745 | ±100° |
| 3 | `elbow_flex` | ±1.690 | ±96.8° |
| 4 | `wrist_flex` | ±1.658 | ±95° |
| 5 | `wrist_roll` | −2.744 ~ 2.841 | −157° ~ 163° |
| 6 | `gripper` | −0.175 ~ 1.745 | −10° ~ 100° |

### 바디 계층

```
base → shoulder(pan) → upper_arm(lift) → lower_arm(elbow)
     → wrist(flex) → gripper(roll) → moving_jaw(개폐)
```

**팔은 5-DOF다.** 관절 6개 중 6번이 그리퍼이므로 조작 자유도는 5.
2차 자료의 "6-DOF" 표기는 그리퍼를 포함해 센 것이다.
URDF도 revolute 6개 + fixed 1개(`gripper_frame_joint`)로 일치한다.

구조는 **베이스 요 1 + 평면 내 피치 3 + 툴 롤 1**이다.
`shoulder_pan`이 작업 평면을 고르고, 나머지 셋이 그 평면 안에서 위치와 접근 각도를
만들고, `wrist_roll`이 툴 축 회전을 준다. 합이 위치 3 + 피치 1 + 롤 1 = 5.

**빠진 것은 말단의 독립적인 요(yaw)다.** 그리퍼 위치를 고정한 채 접근 방위만
바꿀 수 없다. 접근 방위가 `shoulder_pan`에 묶여 있기 때문이다.

---

## 캘리브레이션 두 버전

`scene.xml`이 include할 로봇 파일을 바꿔 전환한다.

| 파일 | 관절 0점 |
|---|---|
| `so101_new_calib.xml` (기본) | 각 관절 **가동범위의 중앙** |
| `so101_old_calib.xml` | 수평으로 **완전히 편 자세** |

실물 캘리브레이션과 시뮬 0점이 어긋나면 sim-to-real이 깨진다.

---

## 뷰어 조작

- 좌드래그 회전 / 우드래그 이동 / 스크롤 줌
- 왼쪽 패널 **Control** 탭의 슬라이더로 6축을 직접 움직인다
- `Ctrl` + 좌드래그로 링크를 끌어 물리 반응을 본다

---

## so101-nexus 태스크 환경

[so101-nexus](https://github.com/johnsutor/so101-nexus) `0.5.4`를 PyPI 버전 고정으로 설치한다.
Apache-2.0, 개인 관리 프로젝트이고 Beta다. 6주 사이 릴리스가 10번 나왔다.

```python
import gymnasium as gym
import so101_nexus.mujoco   # 환경 id를 등록한다

env = gym.make("MuJoCoPickLift-v1", render_mode="rgb_array")
obs, info = env.reset(seed=0)
obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
```

### 맥에서 확인한 결과 (2026-09-11, 기본 GL)

| 환경 | obs 차원 | 렌더 | 스텝 |
|---|---:|---|---:|
| `MuJoCoLookAt-v1` | 23 | 480×640 | 0.1 ms |
| `MuJoCoMove-v1` | 22 | 480×640 | 0.1 ms |
| `MuJoCoPickAndPlace-v1` | 43 | 480×640 | 0.2 ms |
| `MuJoCoPickLift-v1` | 31 | 480×640 | 0.2 ms |
| `MuJoCoStackCube-v1` | 43 | 480×640 | 0.2 ms |
| `MuJoCoTouch-v1` | 31 | 480×640 | 0.2 ms |

스텝 시간은 무작위 액션 100회 평균이고 렌더링은 포함하지 않았다.
`MUJOCO_GL` 설정 없이 기본값으로 오프스크린 렌더링이 됐다.

### 액션 공간

6개 환경 모두 `Box(6,)`, **단위는 라디안**이다. 범위가 SO-ARM100 MJCF의 관절 가동범위와 같다.

```
shoulder_pan  ±1.91986    shoulder_lift ±1.74533    elbow_flex ±1.69
wrist_flex    ±1.65806    wrist_roll    ±2.74385    gripper    −0.17453 ~ 1.74533
```

공개 데이터셋(`johnsutor/MuJoCoPickLift-v1` 등)의 `action`은 이와 달리 LeRobot SO-101 규약의
±100 스케일로 저장돼 있다. 변환 코드는 패키지의 `lerobot_adapter/normalization.py`에 있다.

### 텔레오퍼레이션

`--teleop`으로 설치하면 실물 SO-100/101 리더 암으로 시뮬 팔로워를 조종하고
LeRobot v3 데이터셋으로 기록한다 (Gradio UI).

```bash
scripts/_so101/.venv/bin/so101-nexus teleop --leader-port /dev/tty.usbmodemXXXX
```

---

## 키보드 조종 — `scripts/so101_teleop.py`

`libero-lab/teleop.py`와 같은 구성이다. 태스크를 손으로 몰아볼 뿐 아무것도 기록하지 않고,
성공하면 `solved`를 출력한다.

```bash
python3 scripts/so101_teleop.py                              # MuJoCoTouch-v1, 가장 쉽다
python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # 큐브 들기
python3 scripts/so101_teleop.py --demo                       # 키 없이 정해진 동작을 뷰어로
python3 scripts/so101_teleop.py --selftest                   # 뷰어 없이 키별 이동·회전 측정
```

어떤 `python3`로 실행해도 `scripts/_so101/.venv`로 옮겨 다시 실행한다. 뷰어가 필요하면
macOS에서는 `mjpython`으로 옮기면서 위의 `DYLD_LIBRARY_PATH`를 자동으로 붙인다.

### 키

| 키 | 동작 |
|---|---|
| `w` `s` / `a` `d` / `r` `f` | 말단 x / y / z 이동 (월드 좌표) |
| `z` `x` / `t` `g` / `c` `v` | x / y / z 축 회전 |
| `space` | 그리퍼 열기/닫기 |
| `q` | 태스크 리셋 (시드가 1 오르고 배치가 바뀐다) |
| `ctrl-c` | 종료 |

**키는 뷰어 창이 아니라 터미널에서 읽는다.** MuJoCo 뷰어가 스페이스(일시정지), 백스페이스
(물리 상태 리셋), 숫자 0~5(표시 그룹), 글자 대부분(시각화 플래그)을 이미 쓰고 있어서, 뷰어에서
받으면 팔이 움직이는 동시에 화면 설정이 바뀐다. 뷰어에서 카메라를 돌린 뒤에는 터미널을 다시
클릭한다. 터미널 입력이라 macOS 손쉬운 사용 권한이 필요 없고, 키를 누르고 있으면 자동 반복으로
계속 움직인다.

### 제어 방식

`control_mode="pd_ee_delta_pose"`로 환경을 만든다. 액션은 `[-1, 1]` 범위의 7차원
`[dx dy dz, wx wy wz, 그리퍼]`이고, 스텝당 최대 0.02 m / 0.1 rad / 0.2 rad로 스케일된 뒤
패키지의 감쇠 최소제곱 IK가 관절 목표로 바꾼다. 매 스텝 현재 말단 자세에서 목표를 새로 잡는다.

### 측정 (`--selftest`, MuJoCoTouch-v1, 2026-09-11)

`r`로 0.5초 들어 올린 자세에서 각 키를 0.5초 누른 결과다. 이동 속도 0.15, 회전 속도 0.2.

| IK 방향 가중치 | 이동 6키 | 이동 속도 | 회전 |
|---|---|---|---|
| 0 | 전부 통과 | 135~182 mm/s | 전혀 돌지 않는다 |
| 0.01 (패키지 기본값) | 전부 통과 | 136~186 mm/s | 0.5초에 4° 이하 |
| **0.1 (teleop 기본값)** | 전부 통과 | 114~172 mm/s | x ±22°, y +31°/−8°, z ±18°(x축과 섞임). 회전 중 말단이 16~40 mm 밀린다 |

가중치 0.1에서는 이동할 때 다른 축으로 새는 양도 줄었다 (`w`의 z 이탈 17 mm → 2 mm).

리셋 자세는 말단이 바닥에서 6 cm 위(관절 0°, −90°, 90°, 37.8°, 0°, −10°)라서,
들어 올리지 않고 `f`를 누르면 거의 내려가지 않는다.

### 확인하지 못한 것

실제 터미널에서 사람이 키를 누르는 경로는 시험하지 못했다. 자동 반복 간격과
`--hold`(기본 0.15초)가 맞지 않으면 누르고 있어도 움직임이 끊길 수 있다.

---

## 이 씬에 없는 것

`scene.xml`은 931바이트짜리로 **바닥·조명·카메라각뿐이다. 물체도 태스크도 없다.**
조작 태스크가 필요하면 별도다.

| 경로 | 내용 |
|---|---|
| [`johnsutor/so101-nexus`](https://github.com/johnsutor/so101-nexus) | MuJoCo 태스크 6종 + 텔레오퍼레이션 레코더. **이 스크립트가 설치한다** (위 절) |
| [`LightwheelAI/leisaac`](https://github.com/LightwheelAI/leisaac) | Isaac Lab 태스크 4종(오렌지 담기, 큐브 들기, 장난감 치우기, 양팔 천 접기). LeRobot EnvHub 공식 시뮬 환경. Linux + RTX GPU 필요 |
| [`MuammerBay/isaac_so_arm101`](https://github.com/MuammerBay/isaac_so_arm101) | Isaac Lab 태스크. GPU 필요 |
| LeRobot **EnvHub** | `env.py`에 `make_env()`를 두고 Hub에 올리면 `lerobot-train`/`lerobot-eval`에 연결된다 |
