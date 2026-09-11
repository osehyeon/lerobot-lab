# lerobot-lab

VLA(Vision-Language-Action) 모델을 공부하고 실험하는 개인 실습 랩.
주 프레임워크는 [LeRobot](https://github.com/huggingface/lerobot)이고, 로봇은 SO-101을 기준으로 한다.

이 저장소는 두 부분으로 되어 있다.

- **`docs/`** — LeRobot, 모방학습, VLA 계보, 벤치마크, 양자화, 하드웨어를 정리한 노트
- **`scripts/`** — 맥에서 도는 SO-101 MuJoCo 시뮬레이션 환경과 키보드 조종 스크립트

모델 학습과 추론은 CUDA GPU 서버에서 한다. 맥에서는 코드 읽기, 문서, 스크립트, MuJoCo 시뮬레이션만 한다.

## 빠른 시작

```bash
git clone git@github.com:osehyeon/lerobot-lab.git
cd lerobot-lab

bash scripts/so101_sim_setup.sh             # venv, MuJoCo, so101-nexus, SO-101 모델
python3 scripts/so101_teleop.py             # 키보드로 SO-101 조종
```

셋업 스크립트는 멱등적이다. 다시 돌려도 이미 있는 것은 건너뛰고, 끝에서 환경 6개를 리셋·스텝·렌더링해 확인한다.
받은 파일과 venv는 gitignore된 `scripts/_so101/`에 들어간다.

## 구성

| 경로 | |
|---|---|
| `scripts/so101_sim_setup.sh` | venv 생성, [so101-nexus](https://github.com/johnsutor/so101-nexus) `0.5.4` 설치, SO-101 MJCF·STL 다운로드, 검증 |
| `scripts/so101_teleop.py` | SO-101 태스크를 키보드로 조종. 기록하지 않는다 |
| `docs/` | 노트 12편. 아래 목록 |
| `CLAUDE.md` | 작업 규칙과 환경 메모 |

## 직접 조종하기

```bash
python3 scripts/so101_teleop.py                              # MuJoCoTouch-v1, 가장 쉽다
python3 scripts/so101_teleop.py --task MuJoCoPickLift-v1     # 큐브 들기
python3 scripts/so101_teleop.py --task MuJoCoStackCube-v1 --seed 3
```

어떤 `python3`로 실행해도 `scripts/_so101/.venv`로 옮겨 다시 실행한다. macOS에서는 뷰어 때문에 `mjpython`으로 옮긴다.

| 키 | |
|---|---|
| `w` `s` / `a` `d` / `r` `f` | 말단 x / y / z 이동 |
| `z` `x` / `t` `g` / `c` `v` | x / y / z 축 회전 |
| `space` | 그리퍼 열기/닫기 |
| `q` | 리셋 (배치가 바뀐다) |
| `ctrl-c` | 종료 |

- **키는 뷰어 창이 아니라 터미널에서 읽는다.** MuJoCo 뷰어가 스페이스, 백스페이스, 숫자, 글자 대부분을 이미 단축키로 쓰기 때문이다.
  뷰어에서 카메라를 돌린 뒤에는 터미널을 다시 클릭한다. macOS 손쉬운 사용 권한은 필요 없다
- 리셋 직후 말단이 바닥에서 6 cm 위라 `f`로는 거의 내려가지 않는다. `r`로 먼저 들어 올린다
- SO-101 팔은 5축이다. x·y 축 회전은 되지만 z 축 회전은 x 축과 섞이고, 회전하면 말단 위치도 몇 cm 밀린다

| 옵션 | |
|---|---|
| `--task` | `MuJoCoTouch-v1`(기본), `MuJoCoPickLift-v1`, `MuJoCoPickAndPlace-v1`, `MuJoCoStackCube-v1`, `MuJoCoLookAt-v1`, `MuJoCoMove-v1` |
| `--pos-sensitivity` / `--rot-sensitivity` | 이동·회전 속도, 기본 0.15 / 0.2 |
| `--hold` | 키 입력 한 번이 움직임을 유지하는 시간, 기본 0.15초. 누르고 있어도 끊기면 늘린다 |
| `--demo` | 키 없이 정해진 동작을 뷰어로 보여준다 |
| `--selftest` | 뷰어 없이 키별 이동·회전을 측정한다 |

측정값과 제어 방식은 [docs/so101-sim.md](docs/so101-sim.md)에 있다.

### 뷰어만 띄우기

셋업 스크립트가 마지막에 출력하는 명령을 그대로 쓴다.

```bash
DYLD_LIBRARY_PATH=<uv Python의 lib 폴더> scripts/_so101/.venv/bin/mjpython \
  -m mujoco.viewer --mjcf=scripts/_so101/scene.xml
```

uv가 받은 독립 실행형 Python은 `libpython`을 자기 설치 폴더에 두는데, `mjpython`은 venv 옆에서만 찾기 때문에
`DYLD_LIBRARY_PATH`가 필요하다. Homebrew `python3.12`로 만든 venv에서는 필요 없다.

## 문서

**개념**

| 문서 | |
|---|---|
| [lerobot.md](docs/lerobot.md) | LeRobot이란 무엇인가 |
| [imitation-learning.md](docs/imitation-learning.md) | 모방학습 — BC의 세 가지 근본 문제와 대응 |
| [mpc-act-rtc.md](docs/mpc-act-rtc.md) | MPC → ACT → RTC, 비전공자용 설명 |

**모델**

| 문서 | |
|---|---|
| [policies.md](docs/policies.md) | LeRobot 지원 정책, 액션 표현 방식, VRAM·학습 시간 |
| [vla-lineage.md](docs/vla-lineage.md) | VLA 논문 계보 (RT-2부터 2026년까지) |

**평가**

| 문서 | |
|---|---|
| [vla-benchmarks.md](docs/vla-benchmarks.md) | 평가 데이터셋·벤치마크 계보 |
| [vla-replica.md](docs/vla-replica.md) | VLA-REPLICA — SO-101 실물 벤치마크와 사람 시연 데이터셋 501개 |

**양자화**

| 문서 | |
|---|---|
| [vla-quantization.md](docs/vla-quantization.md) | VLA 양자화 논문 계보 |
| [training-free-trend.md](docs/training-free-trend.md) | "training-free" 키워드가 늘어난 이유 |
| [quantization-experiment-plan.md](docs/quantization-experiment-plan.md) | 실험 계획 — SmolVLA·π0.5, LIBERO·LIBERO-Plus |

**하드웨어와 시뮬레이션**

| 문서 | |
|---|---|
| [lerobot-hardware.md](docs/lerobot-hardware.md) | LeRobot이 지원하는 실물 로봇과 텔레오퍼레이터 |
| [so101-sim.md](docs/so101-sim.md) | SO-101 MuJoCo 모델, so101-nexus 태스크, 키보드 조종 |

## 논문

`paper/`는 gitignore되어 있다. 문서가 참조하는 LeRobot 논문 두 편은 arXiv에서 받는다.

```bash
mkdir -p paper
curl -L -o paper/2602.22818-lerobot-library.pdf       https://arxiv.org/pdf/2602.22818
curl -L -o paper/2510.12403-robot-learning-tutorial.pdf https://arxiv.org/pdf/2510.12403
```

## 외부 코드와 데이터

이 저장소에 포함되지 않고, 스크립트가 받아 온다.

| | 라이선스 |
|---|---|
| [so101-nexus](https://github.com/johnsutor/so101-nexus) | Apache-2.0. PyPI `0.5.4` 고정 |
| [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) `Simulation/SO101` | 원 저장소 라이선스를 따른다 |
| MuJoCo | Apache-2.0 |
