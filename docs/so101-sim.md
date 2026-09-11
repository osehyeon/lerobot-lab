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
성공하면 `solved!`를 출력한다. 시작할 때 터미널에 키 표를 찍는다.

```bash
python3 scripts/so101_teleop.py                              # MuJoCoTouch-v1, 가장 쉽다
python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # 큐브 들기
python3 scripts/so101_teleop.py --view overhead              # 정책이 보는 위쪽 카메라
python3 scripts/so101_teleop.py --demo                       # 키 없이 정해진 동작
python3 scripts/so101_teleop.py --selftest                   # 창 없이 키별 이동·회전 측정
python3 scripts/so101_teleop.py --snapshot view.png          # 창 한 장을 저장하고 끝낸다
python3 scripts/so101_teleop.py --mujoco-viewer              # 마우스로 카메라를 돌리는 MuJoCo 뷰어
```

어떤 `python3`로 실행해도 `scripts/_so101/.venv`로 옮겨 다시 실행한다.

### 창

기본은 **OpenCV 창 하나**다. 왼쪽은 받침대 바로 뒤에서 35° 내려다본 화면, 오른쪽은 손목
카메라(`wrist_cam`) 화면이다. 위쪽에 태스크 지시문, 말단 좌표(cm)와 그리퍼 상태, 지금 눌린 키,
성공 여부를 적는다. **키도 이 창에서 받는다.** 창이 뜨면 한 번 클릭해 포커스를 준다.

| 키 | 동작 |
|---|---|
| `w` `s` / `a` `d` / `r` `f` | 말단 x / y / z 이동 (월드 좌표). 화면에서는 멀어짐·다가옴 / 좌우 / 위아래 |
| `z` `x` / `t` `g` / `c` `v` | x / y / z 축 회전 |
| `space` | 그리퍼 열기/닫기 |
| `q` | 태스크 리셋 (시드가 1 오르고 배치가 바뀐다) |
| `esc` / 창 닫기 | 종료 |

**기본 화면을 비스듬한 시점으로 둔 이유.** 환경의 위쪽 카메라는 정확히 수직으로 내려다본다
(elevation −90°). 이 화면에서는 `r`로 8.6 cm 올라가도 화면상 이동이 1.3 cm뿐이고, `w` `s`도 팔이
화면 세로로 조금 늘었다 줄 뿐이라, 받침대를 중심으로 팔 전체가 도는 `a` `d`만 움직이는 것처럼
보인다. `--view overhead`는 정책 입력과 같은 화면이 필요할 때 쓴다. 환경의 `side` 렌더 설정은
환경을 만든 뒤 바꾸면 렌더에 반영되지 않았다.

### MuJoCo 뷰어를 기본으로 쓰지 않는 이유

MuJoCo 뷰어는 **알파벳 26개를 전부** 시각화 단축키로 쓴다 (`mujoco.mjVISSTRING`, `mujoco.mjRNDSTRING`).
조종 키에 걸린 기능은 이렇다.

| 키 | 뷰어 단축키 | 종류 |
|---|---|---|
| `w` `s` `r` `g` | Wireframe, Shadow, Reflection, Fog | 렌더링 플래그 (`scn.flags`) |
| `a` `d` `f` `z` `x` `t` `c` `v` `q` | Auto Connect, Static Body, Contact Force, Light, Texture, Transparent, Contact Point, Tendon, Camera | 표시 옵션 (`opt.flags`) |

뷰어 창에서 키를 받으면 팔이 움직이는 동시에 화면이 바뀐다. passive 뷰어 핸들은 `opt`는
공개하지만 렌더링 플래그가 든 내부 장면은 공개하지 않아서, 바뀐 설정을 되돌릴 수도 없다.
처음 버전은 키를 터미널에서 읽었는데, 뷰어 창이 뜨면서 포커스를 가져가 키가 뷰어로 들어갔다.

`libero-lab`이 된 이유는 robosuite가 MuJoCo 뷰어를 쓰지 않기 때문이다. robosuite 1.4.1은
`has_renderer=True`면 `OpenCVRenderer`로 화면 밖 렌더를 `cv2.imshow`에 띄우고
(`environments/base.py:290`, `utils/opencv_renderer.py:33`), 키는 pynput 전역 리스너로 받는다
(`devices/keyboard.py:33`). 그래서 손쉬운 사용 권한이 필요했다.

`--mujoco-viewer`는 터미널 입력 방식을 남겨둔 것이다. 카메라를 마우스로 돌릴 수 있고, 키는 터미널에서
읽고 `ctrl-c`로 끝낸다. 뷰어 창에는 키를 치지 않는다. macOS에서는 `mjpython`으로 옮기면서
`DYLD_LIBRARY_PATH`를 붙인다. OpenCV 창은 반대로 메인 스레드에서 돌아야 해서 일반 `python`으로 실행한다.

### 렌더링과 제어 주기

맥에서 렌더 한 장에 약 18 ms가 든다. 해상도를 640×480에서 320×240으로 줄여도 거의 같았다.
비용이 픽셀 수가 아니라 렌더 호출 자체에서 나온다는 뜻이다. 그래서 물리는 50 Hz(`control_dt` 0.02 s)로
벽시계를 따라 돌리고, 화면은 `--fps`(기본 20)로 따로 그린다. 렌더하는 사이 밀린 스텝은 한 번에
5개까지 몰아서 민다. `--no-wrist`로 손목 화면을 빼면 렌더 비용이 절반이 된다.

### 제어 방식

`control_mode="pd_ee_delta_pose"`로 환경을 만든다. 액션은 `[-1, 1]` 범위의 7차원
`[dx dy dz, wx wy wz, 그리퍼]`이고, 스텝당 최대 0.02 m / 0.1 rad / 0.2 rad로 스케일된 뒤
패키지의 감쇠 최소제곱 IK가 관절 목표로 바꾼다. 매 스텝 현재 말단 자세에서 목표를 새로 잡는다.

### IK 방향 가중치 — 회전할 때만 올린다

IK가 말단 방향 오차에 주는 가중치(`config.robot.ee_orientation_weight`)를 스텝마다 바꾼다.
이동만 할 때는 **패키지 기본값 0.01**, 회전 키를 누르는 동안만 **`--rotation-weight`(기본 0.1)**다.
IK가 매 스텝 이 값을 config에서 읽기 때문에 바꾸면 바로 반영된다.

한 값으로 둘 다 만족시킬 수 없었다.

- **0.01에서는 회전 키가 거의 먹지 않는다.** 0.5초에 4° 이하
- **0.1로 이동하면 리셋 자세에서 `f`가 거꾸로 간다.** 리셋 자세는 팔이 접혀 `shoulder_lift` −90°,
  `elbow_flex` 90°로 둘 다 한계(−100°, ±96.8°) 근처다. 방향을 유지하려다 `shoulder_lift`가 곧 −100°에
  걸리고 `wrist_flex`만 계속 꺾이면서 말단이 1.2초에 6.1 cm → 22.0 cm로 올라갔다.
  가중치 0에서는 `shoulder_lift`가 −90° → −28°로 풀리며 제대로 내려가 바닥에 닿는다

어깨·팔꿈치 3관절로 위치를 풀고 손목 2관절은 키로 직접 돌리는 방식도 시제품으로 시험했지만,
리셋 자세에서 `w` `s` `f`가 틀린 방향으로 가서 버렸다. 관절 3개만으로는 한계에 걸린 관절을
다른 관절이 대신 받아주지 못한다.

### 측정 (2026-09-11, MuJoCoTouch-v1, 이동 속도 0.15, 회전 속도 0.2)

**리셋 직후 자세에서 실제 키보드처럼 1초 누름** (첫 입력, 0.5초 공백, 이후 50 ms 자동 반복).
사람이 처음 조종하는 조건이다.

| 키 | Δx | Δy | Δz (mm) | |
|---|---:|---:|---:|---|
| `w` | 96.2 | 0.1 | 27.7 | 통과 |
| `s` | −52.4 | 0.0 | 1.7 | 통과 |
| `a` | −14.8 | 128.3 | 24.2 | 통과 |
| `d` | −15.3 | −127.8 | 23.7 | 통과 |
| `r` | −0.1 | 0.0 | 118.9 | 통과 |
| `f` | 11.6 | 0.0 | −22.6 | 통과. 그 아래는 바닥 |

**회전** (들어 올린 뒤 0.5초 계속 누름, 회전 중 가중치 0.1): `z` `x`는 x축 ±30°(z축 ∓7°와 섞임),
`t`는 y축 +31°, `g`는 y축 −4°, `c` `v`는 z축 ±12°(x축 ∓10°와 섞임). 회전하는 동안 말단이 12~40 mm 밀린다.
`g`는 거의 돌지 않고 말단만 40 mm 끌고 간다. 리셋 직후 자세에서 1초 누르면 이 이동이 148 mm까지 커진다.

위 두 표는 `--selftest` 출력이다. 이동 키를 리셋 직후 조건과, `r`로 들어 올린 뒤 0.5초 계속 누르는
조건에서 각각 판정하고(12개 모두 통과), 회전은 판정 없이 값만 보여준다.

### 확인한 것과 못 한 것

- `--demo`로 OpenCV 창과 MuJoCo 뷰어 두 경로 모두 창을 띄워 정해진 키 입력이 적용되는 것을 확인했다
- 사람이 실제로 키를 누르는 경로는 시험하지 못했다. 자동 반복 간격과 `--hold`(기본 0.15초)가
  맞지 않으면 누르고 있어도 움직임이 끊길 수 있다

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
