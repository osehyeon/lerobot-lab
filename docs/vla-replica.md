# VLA-REPLICA

> 작성 2026-09-11. SO-101 실물 VLA 벤치마크와 그 시연 데이터셋.
> 데이터셋 스펙·지시문·에피소드 수는 HF의 `meta/` 파일을 직접 읽어 확인했다.
> 결과 표·셋업 수치는 논문 HTML과 셋업 문서 페이지에서 가져왔다.

---

## 1. 개요

| 항목 | 내용 |
|---|---|
| 논문 | *VLA-REPLICA: A Low-Cost, Reproducible Benchmark for Real-World Evaluation of Vision-Language-Action Models* |
| arXiv | [2605.20774](https://arxiv.org/abs/2605.20774), 2026-05-20 (v1), cs.RO |
| 게재 | **Data-Centric Robotics Workshop at RSS 2026** (본 학회 아님) |
| 저자 | Alex S. Huang*, Jiahui Zhang*, Shiqing Tang, Yu Xiang (*공동 1저자) |
| 소속 | UT Dallas, Intelligent Robotics and Vision Lab (IRVL) |
| 지원 | NSF, NVIDIA Academic Grant Program |
| 코드 | [IRVLUTD/VLAReplica](https://github.com/IRVLUTD/VLAReplica) — MIT, ★17 (2026-09) |
| 데이터 | [HenryZhang/VLAReplica_SFT_data](https://huggingface.co/datasets/HenryZhang/VLAReplica_SFT_data) — **CC-BY-4.0** |
| 프로젝트 | [irvlutd.github.io/VLAReplica](https://irvlutd.github.io/VLAReplica/) |

같은 연구실의 [SceneReplica (ICRA 2024)](https://arxiv.org/abs/2306.15620)는 YCB 물체로
**장면**을 재현하는 실물 파지 벤치마크였다. VLA-REPLICA는 복제 대상을
**로봇·카메라·조명·물체를 포함한 셋업 전체**로 넓혔다. 기성품 부품만으로 구성해
다른 연구실이 1시간 안에 같은 환경을 조립할 수 있게 한 것이 설계의 중심이다.

---

## 2. 데이터셋

**실물 환경에서 사람이 SO-101 리더 암으로 팔로워 암을 조종해 수집한 시연이다.**
저장소에 리더 암 캘리브레이션 파일과 `so101_teleoperate.py`가 들어 있다.
데이터 카드에는 라이선스와 언어만 적혀 있고 수집 절차 설명은 없다.

### 스펙 (`meta/info.json`)

| 항목 | 값 |
|---|---|
| 포맷 | LeRobotDataset **v3.0** |
| `robot_type` | `so_follower` |
| fps | 30 |
| 에피소드 | **501** |
| 프레임 | 266,240 (약 2.5시간) |
| 지시문 | **27종** |
| `action` | float32 [6] — 관절 위치 |
| `observation.state` | float32 [6] — 관절 위치 |
| `observation.images.top` | 480×640, 30fps, **AV1** |
| `observation.images.wrist` | 480×640, 30fps, **AV1** |

`action`과 `observation.state`의 6개 이름은
`shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper`로,
SO-ARM100 공식 MJCF의 관절 이름과 같다 (`docs/so101-sim.md`).

에피소드 길이는 185~1,197프레임, **중앙값 486프레임(약 16초)** 이다.

### 태스크별 에피소드

| # | 태스크 | 에피소드 | 지시문 변형 |
|---|---|---:|---|
| 1 | 빵을 접시에 | 50 | 빨강/파랑 접시 × 25 |
| 2 | 그릇을 코스터에 | 50 | 색 조합 5종 × 10 |
| 3 | 블록 쌓기 | 50 | 색 조합 5종 × 10 |
| 4 | 수건 반으로 접기 | 50 | 분홍/노랑 × 25 |
| 5 | 오븐 열기 | 50 | 1종 |
| 6 | 화이트보드 지우기 | 50 | 1종 |
| 7 | 후추 뿌리기 | 51 | 1번 20 / 2번 16 / 3번 15 |
| 8 | 그릇 들기 | 50 | 색 × 횟수 5종 × 10 |
| 9 | 버튼 누르기 | 50 | 1번/3번 × 25 |
| 10 | 블록 전부 필통에 | 50 | 1종 |

### 지시문 27종 (`meta/tasks.parquet`)

```
 0  Put the bread on the red plate.
 1  Put the bread on the blue plate.
 2  Put the yellow bowl on the purple coaster.
 3  Put the red bowl on the green coaster.
 4  Put the blue bowl on the orange coaster.
 5  Put the blue bowl on the green coaster.
 6  Put the red bowl on the purple coaster.
 7  Stack the red block on the blue block.
 8  Stack the blue block on the red block.
 9  Stack the blue block on the yellow block.
10  Stack the yellow block on the blue block.
11  Stack the red block on the yellow block.
12  Fold the pink towel in half.
13  Fold the yellow towel in half.
14  Open the oven.
15  Clean the whiteboard with the whiteboard eraser.
16  Pour one shake of pepper on the plate.
17  Pour two shakes of pepper on the plate.
18  Pour three shakes of pepper on the plate.
19  Lift the green bowl one time.
20  Lift the green bowl three times.
21  Lift the blue bowl one time.
22  Lift the blue bowl three times.
23  Lift the red bowl one time.
24  Press the button one time.
25  Press the button three times.
26  Collect all the blocks into the pencil box.
```

### 성격

- 연구실 한 곳의 라이트박스 안에서 수집했다. 조명·배경·카메라 배치가 고정이다
- 태스크당 50개, 변형당 10개 구성은 LeRobot 문서의 권장 수집 방식(위치당 10개, 최소 50개)과 같다
- 변형체(수건), 도구 사용(화이트보드), 입자(후추), 횟수 세기(후추·그릇·버튼) 태스크가 섞여 있다
- HF의 같은 계정에 `VLAReplicaTask*`, `VLAReplicaV2_Task*` 이름의 녹화 세션 데이터셋이 20개 더 있다.
  `V2_Task17` 같은 번호가 있어 확장판을 준비 중일 수 있다 (미확인)

---

## 3. 수집 환경

### 부품 (셋업 문서 Bill of Materials)

| 항목 | 가격 |
|---|---:|
| SO-101 팔로워 암 | ~$200 |
| Intel RealSense **D455** (top) | ~$425 |
| Vinmooog 웹캠 (wrist) | $15 |
| Glendan 라이트박스 32"×32" (PVC 프레임, 확산막, LED 패널, 배경) | $150 |
| 클램프·USB-C 케이블·마찰 테이프 | ~$25 |
| **하드웨어 소계** | **~$815** |
| 태스크 물체 16종 | $212.21 |
| **총계** | **~$1,050** |

3D 프린트 부품: 카메라 마운트 스냅훅 2개, 백플레이트 1개, wrist 카메라 마운트 1개.
AprilTag(36h11, 4cm)는 종이 출력.

태스크 물체: 버튼, 펜꽂이, 수건(분홍·노랑·파랑), 장난감 오븐, 코스터(초록·주황·보라·노랑),
그릇(빨강·파랑·노랑·초록), 화이트보드와 마커, 장난감 과일(사과·노란 배), 접시(빨강·파랑),
숟가락·포크, 장난감 빵(크루아상·작은 번·도넛), 휴지 상자(초록), 후추, 필통(파랑·노랑·분홍),
블록(6색), 화이트보드 지우개.

학습·평가 PC: i9-10900X, 64GB RAM, A5000 24GB.

### 배치 (셋업 문서 Hardware Assembly)

| 항목 | 값 |
|---|---|
| 라이트박스 | 32×32 inch |
| SO-101 베이스 중심 | −x 면에서 **16.5 inch**, 앞 모서리를 −z/−y PVC 교차점에 붙임 |
| top 카메라 | −x 면에서 **≈17 inch**, +z·+y 내면 파이프 교차점에 장착 |
| top 카메라 각도 | 수평 기준 **−50° ~ −60°** |
| top 카메라 설정 | **1.5배 줌**, 문서상 680×480 (데이터셋은 640×480) |
| LED 패널 3개 | +z 면 2개(−y/+y 면에서 각 ≈7.5 inch, 아래 방향), +y 면 1개(+z 면에서 ≈8 inch) |
| 색온도 | 최대 약 5600K |

### 캘리브레이션 (셋업 문서 System Calibration)

- **팔**: LeRobot 절차. 각 모터를 중앙에 두고 시작해 물리 한계까지 돌린다
- **top 카메라 1차**: AprilTag 기반. 목표 자세에 맞을 때까지 마운트를 조정한다
  - 위치 X = −0.06, Y = −0.39, Z = 1.25 m (각 ±0.01)
  - 회전 R = −18.5°, P = 3.0°, Y = 2.5° (각 ±1.0°)
- **2차**: 실시간 영상에 `referenceImages/top/top.jpg`, `wrist/wrist.jpg`를 겹쳐
  거의 같아질 때까지 물리적으로 조정한다
- **내부 파라미터**: 저장소에 체커보드 사진 30장과 `lens_calibration.py`가 있다

---

## 4. 태스크와 평가 프로토콜

### 성공 조건 (셋업 문서 Task Reference)

대부분 **"목표 달성 + SO-101이 홈 자세로 복귀"** 둘 다를 요구한다.

| # | 태스크 | 성공 조건 | ID / OOD 변형 |
|---|---|---|---|
| 1 | 빵→접시 | 빵이 맞는 색 접시 위 + 홈 복귀 | ID 빵 A·B, 빨강/파랑 접시, 방해물 0~2 / OOD 빵 C 또는 노랑 접시 |
| 2 | 그릇→코스터 | 맞는 그릇이 맞는 코스터에 닿거나 올라감 + 홈 복귀 | ID 빨강/파랑 그릇 / OOD 노랑·초록 그릇, 새 색 조합 |
| 3 | 블록 쌓기 | 맞는 위 블록이 맞는 아래 블록에 **2초 이상** 접촉 | ID 빨강·노랑·파랑 / OOD 초록, 같은 색끼리 |
| 4 | 수건 접기 | 가장자리를 들어 **50% 넘게** 접음 + 홈 복귀 | ID 분홍/노랑 / OOD 파랑 |
| 5 | 오븐 열기 | 문이 **2초 이상** 열림 + 홈 복귀 | ID만 |
| 6 | 화이트보드 | 지우개로 **2회 이상** 닦고 옆에 둠 | ID만 |
| 7 | 후추 | **정확한 횟수**를 맞는 접시에 + 후추를 접시 왼쪽에 둠 + 홈 복귀 | ID 1~3회 빨강 접시 / OOD 4~5회, 파랑 접시 |
| 8 | 그릇 들기 | 맞는 그릇을 **정확한 횟수** 들었다 내림 + 홈 복귀 | ID 1~3회 / OOD 노랑 그릇, 2·4회 |
| 9 | 버튼 | **정확한 횟수** 누름 + 홈 복귀 | ID 1~3회 / OOD 2·4·5회 |
| 10 | 블록→필통 | 모든 블록이 맞는 색 필통에 + 홈 복귀 | ID 2~4개, 파랑/노랑 / OOD 분홍 필통, 5개 |

### 평가 절차 (셋업 문서 Running Evaluations)

| 항목 | 값 |
|---|---|
| ID | 10태스크 × 변형 5개 = **50회** |
| OOD | 8태스크(오븐·화이트보드 제외) × 변형 5개 = **40회** |
| 시행당 제한 | **90초** |
| 채점 | 이진 (성공/실패) |
| 장면 리셋 | `arm_reset.json`의 자세로 팔 복귀, 참조 사진을 실시간 영상에 겹쳐 물체 배치 |
| 실행 | `benchmark.py` |

변형 하나에 참조 사진 하나가 대응한다 (`tasks/{ID,OOD}/referencePics/taskNN/pic1~5.jpg`,
총 100장). 지시문은 `tasks/{ID,OOD}/task_variants/taskNN.json`에 순서대로 들어 있다.

---

## 5. 실물 결과 (논문)

학습은 모든 방법 **40,000 스텝**. ACT·DiT는 스크래치, VLA는 사전학습 체크포인트에서 파인튜닝.
태스크당 5회 시행이라 표의 각 칸은 0.2 단위다.

### ID 성공률

| 태스크 | ACT | DiT-D | DiT-F | SmolVLA | X-VLA | π0 | π0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 빵→접시 | 0.4 | 0.4 | 0.4 | 0.6 | 0.4 | 0.8 | 0.8 |
| 그릇→코스터 | 0 | 0 | 0 | 0.2 | 0.2 | 0.6 | 0.8 |
| 블록 쌓기 | 0 | 0 | 0 | 0.2 | 0 | 0 | 0.4 |
| 블록→필통 | 0 | 0.2 | 0 | 0 | 0 | 0 | 0.4 |
| 수건 접기 | 0.4 | 0.2 | 0.2 | 0.6 | 0.6 | 0.8 | 1.0 |
| 오븐 열기 | 0.4 | 0.6 | 0.4 | 0.4 | 0 | 0.2 | 0.6 |
| 화이트보드 | 0.2 | 0.2 | 0.2 | 0.2 | 0 | 0.4 | 0.4 |
| 후추 | 0.2 | 0 | 0 | 0 | 0.2 | 0.2 | 0.4 |
| 그릇 들기 | 0.2 | 0 | 0 | 0.2 | 0 | 0.2 | 0.4 |
| 버튼 | 0 | 0 | 0 | 0.2 | 0 | 0.2 | 0.2 |
| **평균** | **0.18** | **0.16** | **0.12** | **0.26** | **0.14** | **0.34** | **0.54** |

### OOD 성공률

| 태스크 | ACT | DiT-D | DiT-F | SmolVLA | X-VLA | π0 | π0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 빵→접시 | 0.4 | 0 | 0.2 | 0.8 | 0.6 | 0.8 | 1.0 |
| 그릇→코스터 | 0.2 | 0.2 | 0 | 0.4 | 0 | 0.6 | 0.4 |
| 블록 쌓기 | 0 | 0 | 0 | 0.2 | 0 | 0.2 | 0 |
| 블록→필통 | 0 | 0 | 0 | 0.2 | 0 | 0 | 0.2 |
| 수건 접기 | 0 | 0.2 | 0 | 0.6 | 0 | 0.6 | 0.8 |
| 후추 | 0 | 0 | 0 | 0 | 0 | 0.2 | 0.4 |
| 그릇 들기 | 0 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 버튼 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **평균** | **0.075** | **0.05** | **0.025** | **0.30** | **0.075** | **0.30** | **0.35** |

### 논문의 주요 관찰

- 파인튜닝한 VLA가 스크래치 모방학습 정책보다 대체로 낫다. π0.5가 ID 평균 0.54
- 강체 파지에서 파지 자세가 부정확하면 물체가 미끄러진다. 블록 쌓기가 모든 방법에서 낮다
- **횟수 세기 태스크는 어떤 방법도 일반화하지 못한다.** 후추를 계속 흔들고 제자리에 두지 못하는 실패가 반복된다
- 사전학습 VLA는 색·모양 변화(OOD)에서 ID와 비슷한 성능을 유지한다. SmolVLA는 OOD(0.30)가 ID(0.26)보다 높다
- 독립적으로 만든 두 번째 셋업에서 비슷한 결과가 나왔다 (ID 0.49 vs 0.48, OOD 0.55 vs 0.50). 비전문가가 1시간 안에 조립했다

---

## 6. 저장소 구성

```
benchmark.py                  평가 실행
so101_teleoperate.py          텔레오퍼레이션 (데이터 수집)
train.sh                      정책별 학습 (act, smolvla, pi0, pi0_fast, pi05, dit, flow_matching_dit, xvla)
arm_reset.json                리셋 자세
calibration/
  robots/                     팔로워·리더·replay 캘리브레이션 JSON
  camera/detect_apriltag.py   AprilTag 자세 추정
  camera/overlay.py           참조 사진 오버레이
  camera/intrinsicParameters/ 체커보드 사진 30장 + lens_calibration.py
  camera/referenceImages/     top.jpg, wrist.jpg
tasks/
  ID/  task_variants/*.json + referencePics/task01~10/pic1~5.jpg
  OOD/ task_variants/*.json + referencePics/task01~10/pic1~5.jpg
vla_tasks.json, vla_tasks_gui_config.json
```

`train.sh`는 단일 GPU와 다중 GPU에서 서로 다른 검증된 하이퍼파라미터(chunk_size, batch_size,
steps)를 쓴다. π0 다중 GPU는 FSDP 설정(`fsdp_pi0.yaml`)이 필요하다.

---

## 7. 시뮬레이션 자산

**시뮬레이션 환경은 공개되지 않았다.** 논문과 저장소에 시뮬 씬, 물체 3D 모델,
물리 파라미터가 없다. 공개된 것과 없는 것은 다음과 같다.

| 필요한 것 | 공개 여부 |
|---|---|
| 로봇 모델 | ✅ SO-ARM100 공식 MJCF/URDF, MuJoCo Menagerie `robotstudio_so101` (VLA-REPLICA 제공 아님) |
| 작업 공간 치수 | ✅ 라이트박스 32"×32", 베이스 위치 |
| 조명 배치 | ✅ LED 3개 위치·방향·색온도 |
| top 카메라 자세 | △ 설치 위치·각도 수치 + AprilTag 목표 자세. 좌표계 정의는 문서에 없다 |
| top 카메라 내부 파라미터 | △ 체커보드 사진 30장과 스크립트로 계산 가능. 값 자체는 없다 |
| wrist 카메라 자세 | △ 마운트 부품과 참조 사진뿐 |
| 물체 목록 | ✅ 제품명과 가격 |
| **물체 3D 모델** | ❌ |
| **물체 초기 배치 좌표** | ❌ 참조 사진 100장으로만 있다 |
| **물리 파라미터** (질량, 마찰) | ❌ |
| 성공 조건 | ✅ 텍스트 정의 |
| 실물 궤적 | ✅ 데이터셋 501 에피소드 |
| 실물 결과 | ✅ 모델 7종 × ID/OOD |

---

## 8. 불일치·미확인

- top 카메라 해상도: 셋업 문서 680×480, 데이터셋 640×480
- 에피소드 수: 논문 500, 데이터셋 501
- AprilTag 목표 Z = 1.25 m는 라이트박스 한 변(0.81 m)보다 크다. 1.5배 줌 적용 전후 어느
  기준인지, 좌표계가 무엇인지 문서에 없다
- 교차 연구실 재현 수치(ID 0.49/0.48, OOD 0.55/0.50)는 5절 표의 어느 모델 평균과도
  일치하지 않는다. 어떤 모델·부분집합 기준인지 원문 확인이 필요하다
- 후추 태스크: 셋업 문서는 ID를 "빨강 접시"로 정의하지만 데이터셋 지시문은 "the plate"로 색을 명시하지 않는다
