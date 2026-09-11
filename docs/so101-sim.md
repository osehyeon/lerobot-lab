# SO-101 MuJoCo 뷰어

> 작성 2026-09-11. 하드웨어 없이 SO-101의 기구 구조와 관절 가동범위를 확인하는 용도.
> 모델 파일 출처: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101).
> 하드웨어 전반은 `docs/lerobot-hardware.md`.

---

## 실행

```bash
bash scripts/so101_sim_setup.sh
```

venv 생성 → MuJoCo 설치 → 모델·메시 다운로드 → 로드 검증까지 한 번에 한다.
멱등적이라 다시 돌려도 이미 있는 것은 건너뛴다. 끝나면 뷰어 실행 명령을 출력한다.

```bash
scripts/_so101/.venv/bin/mjpython -m mujoco.viewer --mjcf=scripts/_so101/scene.xml
```

받은 파일은 `scripts/_so101/` 에 들어가고 gitignore 된다. 외부 레포 자산이라
커밋 대상이 아니다.

### 환경 관련 주의

| 항목 | 내용 |
|---|---|
| **macOS 실행기** | `python`이 아니라 **`mjpython`**. GUI가 메인 스레드를 점유해야 한다 |
| **Python 버전** | mujoco 휠이 있는 3.10~3.13. Homebrew python3.14 에는 없다 |
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

## 이 씬에 없는 것

`scene.xml`은 931바이트짜리로 **바닥·조명·카메라각뿐이다. 물체도 태스크도 없다.**
조작 태스크가 필요하면 별도다.

| 경로 | 내용 |
|---|---|
| [`johnsutor/so101-nexus`](https://github.com/johnsutor/so101-nexus) | MuJoCo 태스크 6종(PickLift, PickAndPlace, StackCube, Touch, LookAt, Move) + 텔레오퍼레이션 레코더. Beta |
| [`MuammerBay/isaac_so_arm101`](https://github.com/MuammerBay/isaac_so_arm101) | Isaac Lab 태스크. GPU 필요 |
| LeRobot **EnvHub** | `env.py`에 `make_env()`를 두고 Hub에 올리면 `lerobot-train`/`lerobot-eval`에 연결된다 |
