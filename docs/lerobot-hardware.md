# LeRobot 실물 로봇 지원 현황

> 작성 2026-09-10. 출처: LeRobot 공식 문서와 `src/lerobot/robots`,
> `src/lerobot/teleoperators` 디렉터리 구조.
> 정책·모델 쪽은 `docs/policies.md`.

LeRobot이 다른 학습 라이브러리와 갈라지는 지점이 이 층이다.
**텔레오퍼레이션 → 데이터 기록 → 학습 → 롤아웃**의 전 사이클이
하나의 CLI 안에 들어 있다.

---

## 1. 공식 지원 로봇

`src/lerobot/robots/` 기준.

| 로봇 | 드라이버 | 성격 |
|---|---|---|
| **SO-101 / SO-100** | `so_follower` | 플래그십. 저가 3D 프린트 6DOF 팔 |
| SO 양팔 | `bi_so_follower` | SO 팔 2대 구성 |
| **Koch v1.1** | `koch_follower` | 커뮤니티에서 오래 쓰인 저가 팔 |
| **LeKiwi** | `lekiwi` | 모바일 베이스 + 팔. 이동 조작 |
| **Hope Jr** | `hope_jr` | HuggingFace 휴머노이드 |
| **Reachy 2** | `reachy2` | Pollen Robotics 서비스 로봇 |
| **Unitree G1** | `unitree_g1` | 휴머노이드 |
| Earth Rover Mini | `earthrover_mini_plus` | 모바일 로버 |
| OMX | `omx_follower` | ROBOTIS OpenMANIPULATOR 계열 |
| OpenArm | `openarm_follower`, `bi_openarm_follower` | 오픈 하드웨어 팔, 단·양팔 |
| reBot B601-DM | `rebot_b601_follower`, `bi_rebot_b601_follower` | 단·양팔 |

**양팔(bi_) 변형이 별도 드라이버로 존재**하는 게 특징이다.
단순히 팔 2개가 아니라 동기화·캘리브레이션이 따로 필요하기 때문이다.

---

## 2. 공식 지원 텔레오퍼레이터

`src/lerobot/teleoperators/` 기준. 두 부류로 갈린다.

### 리더 암 (같은 형태의 팔로 조종)
`so_leader`, `bi_so_leader`, `koch_leader`, `omx_leader`,
`openarm_leader`, `bi_openarm_leader`, `openarm_mini`, `bi_openarm_mini`,
`rebot_102_leader`, `bi_rebot_102_leader`, `unitree_g1`, `reachy2_teleoperator`

### 리더 암이 아닌 입력
| 드라이버 | 설명 |
|---|---|
| `keyboard` | 키보드 |
| `gamepad` | 게임패드 |
| `phone` | 스마트폰 (문서: `phone_teleop`) |
| `homunculus` | 착용형 조종 장치 |

문서에는 `isaac_teleop`(NVIDIA Isaac 연동)도 별도 항목으로 있다.

> **리더-팔로워 방식이 표준인 이유** — 사람이 리더 암을 손으로 움직이면
> 팔로워가 그대로 따라 하고, 그 관절값이 그대로 **액션 라벨**이 된다.
> 조이스틱으로 조종하면 사람의 의도와 관절 궤적 사이에 변환이 끼지만,
> 리더 암은 **관절 공간에서 직접 대응**되므로 모방학습 데이터로서 품질이 높다.

---

## 3. SO-101 상세 — 플래그십

문서가 조립부터 캘리브레이션까지 전 과정을 다루는 유일한 로봇이다.

### 하드웨어
- 부품표(BOM)와 3D 프린트 파일: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)
- SDK: `pip install -e ".[feetech]"` (Feetech 서보)
- **팔로워:** STS3215 모터 6개, 전부 **1/345 기어비**

### 리더 암은 축마다 기어비가 다르다

| 축 | 모터 | 기어비 |
|---|---|---|
| Base / Shoulder Pan | 1 | 1/191 |
| Shoulder Lift | 2 | 1/345 |
| Elbow Flex | 3 | 1/191 |
| Wrist Flex | 4 | 1/147 |
| Wrist Roll | 5 | 1/147 |
| Gripper | 6 | 1/147 |

**설계 의도가 명확하다.** 리더 암은 두 가지를 동시에 만족해야 한다 —
**자기 무게를 버티면서**(어깨 쪽은 높은 감속비), **사람이 큰 힘 없이 움직일 수 있어야**
한다(손목 쪽은 낮은 감속비). 팔로워처럼 전부 1/345로 하면 사람이 못 움직인다.
같은 형상의 팔인데 모터 구성이 다른 이유다.

### 셋업 순서
```
lerobot-find-port      # USB 포트 식별 (케이블 뽑았다 꽂으며 확인)
lerobot-setup-motors   # 모터별 id·baudrate를 EEPROM에 기록. 1회만
[3D 프린트 부품 조립]
lerobot-calibrate      # 리더·팔로워 각각
```

**모터 id 설정은 한 개씩 연결해가며** 진행한다. 새 모터는 전부 id가 1이라
데이지체인으로 묶기 전에 개별로 구분해줘야 한다. EEPROM에 쓰므로 한 번만 하면 된다.

### 캘리브레이션이 중요한 이유
문서가 직접 밝힌다 — **"한 로봇에서 학습한 신경망이 다른 로봇에서도 동작하게
하려고"** 한다. 리더와 팔로워가 같은 물리적 자세에서 같은 관절값을 갖게 맞추는
작업이고, 이게 어긋나면 데이터셋 자체가 로봇 개체에 종속된다.
LeRobotDataset을 Hub로 공유하는 구조가 성립하려면 필수적인 단계다.

---

## 4. 서드파티 플러그인 생태계

### 플러그인 자동 탐색
LeRobot은 **`lerobot_robot_` 또는 `lerobot_teleoperator_` 접두사가 붙은
설치된 패키지를 자동으로 임포트**한다.

```bash
pip install lerobot_robot_<name> lerobot_teleoperator_<name>
lerobot-record --robot.type=<name> --teleop.type=<name> ...
```

레포를 포크하거나 코드를 고칠 필요가 없다. **하드웨어 지원을 코어에서
분리한 설계**이고, 덕분에 아래처럼 넓어졌다.

### 산업용·협동로봇
UFACTORY xArm, Lebai 6축, Franka(+RobotEra XHand, VR 텔레오퍼레이션),
**Universal Robots UR5e** (단팔·양팔, Robotiq 그리퍼, RTDE 제어, 모바일 자동 수집 변형)

### 연구·학습용 팔
Trossen Robotics의 **WidowX / ALOHA 계열**, AgileX Piper (두 개의 독립 플러그인)

### 저가·취미용
FashionStar StarAI Cello / Viola (6+1 DOF)

### 서비스·모바일
ugo Pro 양팔 서비스 로봇, LeKiwi + PincOpen 그리퍼 변형

### 텔레오퍼레이터
| 부류 | 예 |
|---|---|
| VR·모션 | WebXR(폰/헤드셋), Meta Quest, PICO 4, 3Dconnexion SpaceMouse |
| 리더 암 | GELLO 7DOF, I2RT YAM(양방향 힘 피드백), **ROBOTIS OMY-L100**, PiperMate |
| 햅틱 | Haply Inverse3, Force Dimension omega.7 |
| 원격 | LiveKit(WebRTC) |

### 풀 키트 (로봇 + 텔레오퍼레이터)
ARX5, Nextis AIRA 7DOF, I2RT YAM, The Robot Learning Company DK1,
HEXFELLOW, Hiwonder NexArm

### ROS 2 브리지
`leros2` (토픽·액션 브리지), `lerobot_robot_ros2_zenoh` (Zenoh pub/sub)

> 문서가 ⚠️ 표시로 **포크/확장**과 **드롭인 플러그인**을 구분한다.
> 포크 계열(LeFranX, UR5e-LeRobot 등)은 수정되지 않은 LeRobot 설치본과
> 그대로 동작하지 않는다.

---

## 5. 하드웨어 없이 쓸 수 있는 것

- **`lerobot-robot-dummy`** — 로봇을 시뮬레이션해 **하드웨어 없이 기록 파이프라인을
  돌리는** 서드파티 플러그인. 디버깅용
- Hub의 기존 LeRobotDataset으로 학습
- 시뮬 환경(LIBERO, Meta-World)에서 평가
- **LeLab** — CLI 없이 캘리브레이션·기록·학습을 하는 브라우저 GUI

---

## 6. 국내 관련

**ROBOTIS**(서울) 하드웨어가 양쪽에 다 있다 —
로봇 쪽 `omx_follower` / `omx_leader`(OpenMANIPULATOR 계열)는 **공식 지원**이고,
텔레오퍼레이터 OMY-L100은 서드파티 플러그인(`lerobot_teleoperator_omy`)이다.
국내 조달이 가능한 선택지다.
