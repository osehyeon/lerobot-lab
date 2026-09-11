# SO-101 구매 정리 — 판매처, 카메라, 마운트

> 작성 2026-09-11. 가격과 재고는 이 날짜에 판매 페이지에서 본 값이고 자주 바뀐다.
> 판매 페이지를 직접 열지 못하고 검색 요약이나 판매처 문서로만 확인한 항목은 표에 표시했다.
> 하드웨어 지원 현황은 `docs/lerobot-hardware.md`, 시뮬레이션 카메라는 `docs/so101-sim.md`.

---

## 1. 한 세트에 들어가는 것

텔레오퍼레이션으로 시연을 모으려면 **리더 팔 + 팔로워 팔** 한 쌍이 필요하다.

### 공식 부품표

[TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) README의 "Parts For Two Arms". 3D 프린트 부품은 빠져 있다.

| 부품 | 수량 | 미국 단가 |
|---|---:|---:|
| STS3215 7.4V, 1/345 기어 (C001) | 7 | $13.89 |
| STS3215 7.4V, 1/191 기어 (C044) | 2 | $13.89 |
| STS3215 7.4V, 1/147 기어 (C046) | 3 | $13.89 |
| 모터 제어 보드 | 2 | $10.6 |
| USB-C 케이블 2개 | 1 | $7 |
| 전원 | 2 | $10 |
| 테이블 클램프 4개 | 1 | $9 |
| 드라이버 세트 | 1 | $6 |
| **합계** | | **$229.88** (€226.3 / ￥1,343.16 / ¥44,530) |

팔로워 한 대만이면 $121.94다. 서보 12개 중 C001 7개는 팔로워 6개와 리더 1개(어깨 들기 관절)이고,
C044와 C046은 리더의 나머지 관절에 들어간다.

### 팔로워 서보 전압

- **7.4V**: 공식 기본. 6V에서 정지 토크 16.5 kg·cm. README는 "7.4V로 충분했다"고 적는다
- **12V**: 정지 토크 30 kg·cm. 쓰려면 5V 전원 대신 **12V 5A 이상 전원**이 필요하다
- **리더는 항상 7.4V**다

판매처마다 팔로워를 12V로 구성한 경우가 있다 (PartaBot, ForgeMotion Labs). Waveshare는
7.4V 팔로워를 SO-ARM100, 12V 팔로워를 SO-ARM101로 구분해 부르는데, 공식 설계에서는
SO-100과 SO-101이 기구 개정판이고 전압은 둘 다 선택 사항이다.

### 3D 프린트 부품

공식 권장 설정: PLA+, 0.4 mm 노즐에 0.2 mm 층 두께(또는 0.6 mm 노즐에 0.4 mm), 채움 15%.

프린터가 없을 때 공식 저장소(`3DPRINT.md`)가 안내하는 출력 대행:

| 서비스 | 지역 | 비고 |
|---|---|---|
| [Craftcloud3d](https://craftcloud3d.com) | 유럽, 미국 | 부품 14종을 올린다. 공용 부품 9종은 수량 2 |
| [PCBWay](https://www.pcbway.com) | 중국 | 세계 배송, 중국 밖은 수입세 별도. 두 팔 합계 약 $95였다고 적혀 있다 |

### 카메라

**대부분의 키트에 카메라가 들어 있지 않다.** 4절 참고.

---

## 2. 공식 판매처

SO-ARM100 README의 "Kits" 목록이다.

| 판매처 | 지역 | 확인한 구성과 가격 |
|---|---|---|
| **[RoboSEasy](https://smartstore.naver.com/roboseasy)** | **한국** (네이버 스마트스토어) | RoboSEasy 문서 기준 "리더+팔로워 세트 약 50만 원", "카메라 홀더 포함 55만 원 수준", "해외 직구는 관세·배송 포함 약 50만 원". **구성품은 미확인** (스마트스토어 접근 불가, 상세 문서 404) |
| [Seeed Studio](https://www.seeedstudio.com/SO-101-Low-Cost-AI-Arm-Kit-Pro-p-6427.html) | 국제, 중국(타오바오), 일본(아키즈키), 알리익스프레스 | 서보 모터 키트 $249.90 — 모터, 어댑터 보드, 케이블. **"3D 부품과 카메라는 포함되지 않는다"** 고 명시. 3D 부품 $29.90 별도 |
| | | [조립 완성품 Assembled Kit Pro](https://www.seeedstudio.com/SO-ARM-101-Assembled-Kit-Pro-p-6691.html) $299, 재고 있음. 설명에 서보 6개와 컨트롤러 1개만 나와 **팔 1대로 보인다** (구성품 목록 없음, 미확인) |
| | | [Unassembled Bundle](https://www.seeedstudio.com/SO-ARM101-Pro-Unassembled-Bundle.html) — 모터 키트, 3D 부품, 카메라, 서보를 골라 담는 방식 |
| WowRobo | 국제, 중국(타오바오) | [OpenELAB 리셀러](https://openelab.io/products/wowrobo-robotics-so-arm101-diy) 기준: 부품만 €389.95 (품절), 미조립 + 카메라 1대 €479.95 (품절), **조립·캘리브레이션 완료 + 2MP 카메라 1대 €549.95** (판매 중). 조립 구성에는 서보 어댑터, 전원, 클램프, 케이블 포함. 공식 쇼핑몰은 이번에 접속되지 않았다 |
| [PartaBot](https://partabot.com/products/so-arm101) | 미국 | **전 구성 품절.** 팔로워 12V 모터 6개, 리더 7.4V 모터 6개(1/345 1개, 1/191 2개, 1/147 3개), 12V·5V 전원, 보드 2개, USB-C 2개, 클램프 4개, 3D 부품. 공식 구성품 목록에 카메라 없음. 가격 표기가 $329 / $119로 섞여 있다 |
| [ForgeMotion Labs](https://forgemotionlabs.com/products) | 미국, 아마존 미국 | Complete Teleoperation Kit **$339.99** (리더+팔로워, 전원 2개, 전자부품). 리더 키트 $164.99, 팔로워 키트 $184.99(12V, 그리퍼·**카메라 마운트 포함**). 전자부품 키트 리더 $134.99 / 팔로워 $154.99. 프레임 키트 리더 $33.99 / 팔로워 $34.99(카메라 마운트 포함). 카메라 단품 없음 |
| [RobotEd](https://roboted.ch/en/shop/so-101-robot-arm-kit) | 스위스·리히텐슈타인 | Full Kit CHF 319.95, 전자부품만 CHF 279.95, 3D 부품만 CHF 59.95. 액세서리로 **손목 카메라 마운트 CHF 12.95~19.95**, **Overhead Camera Tower CHF 49.95** |
| [Autodiscovery](https://autodiscovery.eu/en/products/so-101-kit) | EU (함부르크) | 부품 또는 조립, 팔 구성(팔로워만 / 리더만 / 한 쌍) 선택. 한 쌍: 3D 부품, 서보 12개(C001 7, C044 2, C046 3), 보드 2, USB-C 2, 전원 케이블 2, 클램프 2. 가격은 로그인해야 보인다. 백오더 2주 |
| [Robonine](https://robonine.com/) | 국제 | SO-ARM101 Kit **$349** — 리더+팔로워(서보 12개), **USB 카메라**, 전원·케이블·클램프, 연습용 물체와 ArUco 큐브, 설명서. 전 세계 표준 배송 무료, 관세·부가세는 수령 시 별도 |
| NeoBot | 중국(타오바오) | 미확인 |

참고로 [Phospho](https://robots.phospho.ai)는 리더 없이 SO-100 팔로워만 판다.

---

## 3. 비공식·호환 판매처

| 판매처 | 내용 |
|---|---|
| [Hiwonder](https://www.hiwonder.com/products/lerobot-so-101) | **자체 30 kg 고토크 서보를 쓰는 변형.** Standard·Advanced 구성에 그리퍼 카메라와 외부 카메라가 둘 다 들어 있고, DIY 구성은 카메라 없이 마운트만 (검색 요약 기준). 가격 미확인. [아마존](https://www.amazon.com/HIWONDER-Compatible-SO-ARM101-Imitation-Development/dp/B0H4LD4CS9), RobotShop, OZ Robotics에서도 판다 |
| Waveshare | 수지(레진) 3D 부품 키트, 카메라 키트, Jetson 키트 (검색 요약 기준, 상품 페이지 403). [아마존](https://us.amazon.com/SO-ARM101-Photosensitive-Parts-3DP-KIt/dp/B0G6SKB1LG)에도 있다 |
| Feetech 공식 알리익스프레스 | STS3215 서보 단품. 7.4V/12V, 기어비별로 판다 |
| 리셀러 | OpenELAB(WowRobo 유럽), RCDrone, MG Super Labs·ThinkRobotics(인도), eBay |

---

## 4. 카메라와 마운트

### 공식 선택 마운트

SO-ARM100 저장소 `Optional/`. STL은 무료다.

| 위치 | 마운트 | 권장 카메라 |
|---|---|---|
| Overhead | `Overhead_Cam_Mount_32x32_UVC_Module` | 32×32 mm USB 카메라 모듈 |
| | `Overhead_Cam_Mount_Webcam` | 웹캠 (README에 권장 모델 링크) |
| 손목 | `Wrist_Cam_Mount_32x32_UVC_Module` (일체형, 손목 부품 교체) | 32×32 mm USB 모듈, 720p/30fps 이상 |
| | `Wrist_Cam_Plug_Mount_32x32_UVC_Module` | 같음 |
| | `SO101_Wrist_Cam_Hex-Nut_Mount_32x32_UVC_Module` | 같음 (SO-101 전용) |
| | `Wrist_Cam_Mount_Vinmooog_Webcam` | Vinmooog 웹캠 |
| | `Wrist_Cam_Mount_RealSense_D405` / `D435` | Intel RealSense |

**Overhead 마운트의 위치는 수치가 아니라 부품 형상으로 정해진다.** 로봇이 올라가는 받침판과
카메라 기둥이 한 몸으로 맞물려서, 팔을 받침판에 올리면 카메라 위치가 저절로 고정된다.
README의 설계 목표는 "표준화된 카메라 위치와 팔 간격으로 사용자들 사이에 데이터를 일관되게 하는 것"이다.
README가 명시한 카메라 설정은 30 fps, 640×480(작업 공간이 넓으면 1280×720)이다.

기둥 부품 가운데 가장 긴 것이 웹캠용 242.5 mm, 32×32 모듈용 230.9 mm라서
**출력 판이 약 245 mm 이상인 프린터**가 필요하다.

### 판매되는 마운트와 카메라

| 판매처 | 품목 | 가격 |
|---|---|---|
| [JuxiTech](https://www.juxitech.com/products/so-arm101-wrist-camera-mount) | 손목·옆·위 시점 마운트 키트 (3D 프린트) + 카메라. 60 fps 고정초점 또는 30 fps 자동초점. 재고 있음 | ¥137~267 (CNY) |
| RobotEd | 손목 카메라 마운트 / **Overhead Camera Tower** | CHF 12.95~19.95 / CHF 49.95 |
| ForgeMotion Labs | 팔로워 프레임에 카메라 마운트 포함 | 프레임 $34.99 |
| Seeed | X10 USB 카메라 1080p / RGB USB 카메라 100° 720P / ET-S231 | $12 / $30 / $52~64 |
| [WowRobo](https://openelab.io/products/wowrobo-robotics-2mp-usb-camera) | 2MP USB 카메라 모듈, 30 fps, 3 m 케이블. 마운트 없음 | €39.85 |

무료 STL은 공식 저장소 외에도
[Printables](https://www.printables.com/model/1531820-modular-camera-mount-for-so-101-arm),
[MakerWorld](https://makerworld.com/en/models/2445589-camera-module-mount-for-so-101-robot-arm),
[Thingiverse](https://www.thingiverse.com/thing:7143999)에 있다.

### 참고 셋업

| 셋업 | 고정 카메라 | 손목 카메라 |
|---|---|---|
| VLA-REPLICA | Intel RealSense D455 (~$425), 수평 기준 −50~−60° | Vinmooog 웹캠 ($15) + 3D 프린트 마운트 |
| 시뮬레이션 (MuJoCo Menagerie 모델) | 모델에 없음. so101-nexus가 수직 위 0.785 m에 가상 카메라를 둔다 | `wrist_cam`: 센서 5.76×3.24 mm, 초점거리 3.6 mm, 1920×1080 |

---

## 5. 카메라까지 포함한 구성 비교

| 구성 | 포함 카메라 | 가격 | 상태 | 따로 필요한 것 |
|---|---|---|---|---|
| **Robonine SO-ARM101 Kit** | USB 카메라 1대 | $349, 배송 무료 (관세 별도) | 판매 중 | 카메라 1대, 마운트 |
| WowRobo 조립 키트 (OpenELAB) | 2MP 1대 | €549.95 | 판매 중 | 카메라 1대 (€39.85), 마운트 |
| RoboSEasy | 카메라 홀더 (카메라 포함 여부 미확인) | 약 55만 원 | 미확인 | 미확인 |
| Hiwonder Standard / Advanced | 2대 | 미확인 | 미확인 | 없음. 서보가 공식 설계와 다르다 |
| Seeed 조합 | 선택 | $249.90 + $29.90 + 카메라 ($12~) | 판매 중 | 조립, 마운트 출력 |
| ForgeMotion Complete Kit | 없음 (팔로워에 카메라 마운트) | $339.99 | 판매 중 | 카메라 2대 |
| 공식 부품표로 직접 조달 | 없음 | $229.88 + 3D 출력 (PCBWay 약 $95) | — | 카메라 2대, 마운트, 조립 |

---

## 6. 확인하지 못한 것

- RoboSEasy의 구성품과 옵션 (스마트스토어 접근 불가, 판매처 문서의 상세 페이지 404)
- Seeed Assembled Kit Pro가 팔 1대인지 한 쌍인지
- Hiwonder, Waveshare, Autodiscovery 가격
- WowRobo 공식 쇼핑몰의 가격 (OpenELAB 리셀러 가격으로 적었다)
- NeoBot과 타오바오 판매처
- 한국까지의 배송비와 관세

---

## 출처

- [TheRobotStudio/SO-ARM100 README — Kits, Sourcing Parts, Optional Hardware](https://github.com/TheRobotStudio/SO-ARM100)
- [SO-ARM100 3DPRINT.md — 출력 대행](https://github.com/TheRobotStudio/SO-ARM100/blob/main/3DPRINT.md)
- [RoboSEasy Docs — SO ARM 시작하기](https://roboseasy.github.io/docs/physical-ai/lerobot/so-arm/), [하드웨어 선택 가이드](https://roboseasy.github.io/docs/physical-ai/lerobot/get-start/hardware/)
- 각 판매처 링크는 표 안에 있다
