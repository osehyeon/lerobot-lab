# VLA 양자화 논문 계보

> 작성 2026-09-10. 웹 검색으로 확인. 날짜는 arXiv ID 기준.
> 실험 셋업을 원문에서 직접 확인한 것은 **QuantVLA와 BitVLA 둘뿐**이고,
> 나머지는 제목·초록 수준이다. 인용 전 원문 확인 필요.
> 모델 계보는 `docs/vla-lineage.md`, 벤치마크는 `docs/vla-benchmarks.md`.

---

## 0. 이 분야를 관통하는 문제

**액션 헤드는 LM 백본보다 양자화에 훨씬 민감하다.**

이유가 구조적이다. 액션 헤드는 **연속 제어 신호**를 내고 물리 액추에이터와
**closed-loop**로 물려 있다. 언어 벤치마크에서라면 감지도 안 될 미세한 섭동이
**접촉력과 물리 동역학을 거치며 증폭된다.** 토큰 하나 잘못 고르는 것과
그리퍼가 몇 밀리미터 어긋나는 것은 결과가 다르다.

LLM 양자화 기법을 그대로 가져오면 안 되는 이유고, 2026년 논문들이
전부 이 지점을 공략한다. 계보 전체가 **"어디를 얼마나 아껴야 하는가"** 를
정교화해 온 과정이다.

---

## 1. 0기 — 양자화가 부산물이던 시기 (2024)

### OpenVLA (2024-06, [2406.09246](https://arxiv.org/abs/2406.09246))
양자화 논문이 아니다. 다만 **7B 모델을 소비자 GPU에서 돌리려고**
bfloat16 / int8 / int4 추론을 부록에서 비교했다.
"양자화하면 메모리가 준다"는 수준이고, VLA 고유의 문제의식은 없다.

계보상 의미는 **대상과 기준선을 제공했다**는 것이다. 이후 몇 년간
거의 모든 VLA 양자화 논문이 OpenVLA를 베이스로 삼는다.

---

## 2. 1기 — 모방학습 QAT (2024-12 ~ 2025)

VLA보다 넓은 **로봇 모방학습**의 양자화로 시작한다.

### Quantization-Aware Imitation-Learning (2024-12, [2412.01034](https://arxiv.org/abs/2412.01034))
*"Resource-Efficient Robotic Control."* 학습 단계에서 양자화를 고려하는
**QAT를 모방학습에 도입**. 사후 양자화(PTQ)가 아니라 학습부터 손을 대는 접근.

### Saliency-Aware Quantized Imitation Learning (2025-05, [2505.15304](https://arxiv.org/abs/2505.15304))
**어디가 중요한지(saliency)를 재서 차등 적용**한다는 발상의 등장.
"모든 가중치를 똑같이 줄이지 않는다"는 이 아이디어가 이후 계보의 뼈대가 된다.

### FAST (2025-01, [2501.09747](https://arxiv.org/abs/2501.09747))
서베이가 양자화 절에 넣지만 성격이 다르다. **모델 가중치가 아니라
액션 공간을 양자화**한다 (DCT + BPE, `docs/policies.md` 참조).
같은 "양자화"라는 단어를 쓰지만 층위가 다르다는 점에서 오히려 대조군으로 유용하다.

---

## 3. 2기 — 극단 압축과 결합 (2025 중후반)

### BitVLA (2025-06, [2506.07530](https://arxiv.org/html/2506.07530v2))
**1비트(삼진 {−1,0,1}) VLA.** 계보에서 가장 공격적인 지점.

- 백본: BitNet b1.58 2B4T + SigLIP-L, 총 약 3.0B
- LLM은 삼진 가중치 + INT8 활성값, 비전 인코더는 **Quantize-then-Distill** 후 1.58비트
- **커넥터와 액션 헤드는 BF16 전정밀도로 남긴다** — 0절의 민감도 문제를
  회피가 아니라 설계로 인정한 것
- 결과: 메모리 **1.4GB** (OpenVLA-OFT BF16 15.4GB 대비 11배 감소),
  레이턴시 73ms(4.4배), LIBERO 평균 96.0% (OpenVLA-OFT 97.1%)
- 관찰: **OpenVLA는 4비트에서 OpenVLA-OFT보다 크게 무너진다**

평가에 **멀티모달 VQA**(MMMU, SeedBench, SeedBench2+, MMStar, AI2D)를 포함시킨
것이 특징이다. 양자화가 VLM 백본의 지각·언어 능력을 얼마나 깎았는지를
따로 재는 진단이다.

### SQAP-VLA (2025-09, [2509.09090](https://arxiv.org/abs/2509.09090))
*"Synergistic Quantization-Aware Pruning."* **양자화와 프루닝을 따로가 아니라
함께** 설계. 압축 기법 결합의 시작.

---

## 4. 3기 — VLA 고유 문제의 정면 공략 (2026)

2026년에 논문이 쏟아진다. 공통점은 **"LLM 양자화와 무엇이 다른가"** 를
명시적 기여로 내세운다는 것이다.

### QVLA (2026-02, [2602.03782](https://arxiv.org/abs/2602.03782))
*"Not All Channels Are Equal in VLA's Quantization."*
**채널 단위 이질성.** 1기의 saliency 발상을 채널 축으로 구체화했다.

### QuantVLA (2026-02, [2602.20309](https://arxiv.org/pdf/2602.20309))
*"Scale-Calibrated PTQ."* **DiT 계열 액션 헤드**를 정면 대상으로 삼은
training-free PTQ.

- 대상 모델: **OpenPI π0.5, GR00T N1.5** (둘 다 DiT 액션 헤드).
  DiT 계열 밖에도 적용되는지 보려고 OpenVLA도 추가 검증
- 기법: attention-temperature matching, output-head balancing으로
  양자화 후 스케일 복원
- 캘리브레이션: 라벨 없는 소규모 캘리브레이션 버퍼 **128배치**, 99.9 퍼센타일 활성값 클리핑,
  per-channel smoothing 계수 0.15
- 비교: **DuQuant**(주 비교군), SmoothQuant(W8A8/W4A8)
- 비트폭: **W4A8** 주력, W4A4·W8A16 추가
- 평가: LIBERO 4 suite, SimplerEnv, Pick-and-Can
- 별도로 **디노이징 스텝 수에 따른 견고성**을 보고한다 — 반복 디노이징에서
  양자화 오차가 누적되는 문제를 인식했다는 신호

### DA-PTQ (2026-04, [2604.11572](https://arxiv.org/html/2604.11572v1))
*"Drift-Aware PTQ."* 확산 기반 VLA인 **CogACT**에 W4A8 적용.
'drift'를 명시적으로 다룬다는 점에서 QuantVLA의 스텝 누적 문제와 같은 계열.

### ActQuant (2026-05, [2605.24011](https://arxiv.org/html/2605.24011))
*"Sub-4-bit Action-Guided Quantization."*
**액션이 양자화를 유도한다.** 가중치 크기나 활성값 통계가 아니라
**액션 공간에서의 민감도**를 직접 재서 채널별 비트를 할당한다.
0절의 문제의식이 방법론으로 완성된 형태.

### Ω-QVLA / HoloQ-VLA (2026-05, [2605.28803](https://arxiv.org/abs/2605.28803))
*"Uniform W4A4."* 가장 공격적인 균일 비트폭. **composite rotation +
per-step scaling.** rotation은 LLM 양자화(QuaRot 계열)의 이상치 처리 기법인데,
**per-step**이 붙은 게 VLA 고유다 — 디노이징 스텝마다 스케일을 달리 준다.

> 같은 arXiv ID가 두 제목(HoloQ-VLA / Ω-QVLA)으로 검색된다. 버전 간 개명으로 보이나
> 확인이 필요하다.

### Mix-QVLA (2026-06, [2606.19565](https://arxiv.org/html/2606.19565))
*"Task-Evidence-Aware Mixed-Precision."* 균일 비트폭을 포기하고
**태스크 증거 기반 혼합 정밀도.** 계보의 현재 최전선.

---

## 5. 이웃 갈래 — 양자화 아닌 압축

같은 "효율화" 문제를 다른 축으로 푼다. 양자화 논문의 비교군이나 결합 대상이 된다.

### 레이어 프루닝 / 동적 추론
| 논문 | 시기 | 내용 |
|---|---|---|
| DeeR-VLA ([2411.02359](https://arxiv.org/abs/2411.02359)) | 2024-11 | 멀티모달 LLM 동적 추론 |
| MoLe-VLA ([2503.20384](https://arxiv.org/abs/2503.20384)) | 2026 | 동적 레이어 스킵 |
| DySL-VLA ([2602.22896](https://arxiv.org/abs/2602.22896)) | 2026-02 | 동적·정적 레이어 스킵 결합 |

### 토큰 최적화
| 논문 | 시기 | 내용 |
|---|---|---|
| VLA-Cache ([2502.02175](https://arxiv.org/abs/2502.02175)) | 2025-02 | 적응적 토큰 캐싱 |
| HybridVLA ([2503.10631](https://arxiv.org/abs/2503.10631)) | 2025-03 | 확산 + 자기회귀 협업 |
| Think Twice, Act Once ([2505.21200](https://arxiv.org/abs/2505.21200)) | 2025-05 | 토큰 압축 + 액션 재사용 |
| SP-VLA ([2506.12723](https://arxiv.org/abs/2506.12723)) | 2025-06 | 모델 스케줄링 + 토큰 프루닝 |
| CogVLA ([2508.21046](https://arxiv.org/abs/2508.21046)) | 2025-08 | 인지 정렬 |
| SpecPrune-VLA ([2509.05614](https://arxiv.org/abs/2509.05614)) | 2026 | 액션 인식 self-speculative 프루닝 |

---

## 6. 축으로 보는 흐름

| 축 | 흐름 |
|---|---|
| **아끼는 기준** | 균일 → 가중치 크기 → saliency(2025) → 채널 이질성(QVLA) → **액션 공간 민감도(ActQuant)** |
| **비트폭** | INT8/INT4 추론(OpenVLA) → W4A8(주 전장) → **W4A4(Ω-QVLA)** / **1.58비트(BitVLA)** |
| **방법** | QAT(모방학습기) → PTQ training-free(QuantVLA) → 혼합 정밀도(Mix-QVLA) |
| **대상 부위** | LM 백본 → + 비전 인코더 → **액션 헤드(2026 전부)** |
| **대상 구조** | 자기회귀(OpenVLA) → **DiT/flow matching 액션 헤드(π0.5, GR00T, CogACT)** |
| **결합** | 양자화 단독 → **프루닝과 공동 설계(SQAP-VLA)** |

**관찰:** 2026년 논문 6편이 전부 액션 헤드 또는 디노이징 스텝을 건드린다.
자기회귀 LM 부분의 양자화는 사실상 정리된 문제로 취급되고,
**확산·flow matching 액션 생성기가 남은 전장**이다.

---

## 7. 평가 관행

원문에서 확인한 두 편 기준이다.

| | QuantVLA | BitVLA |
|---|---|---|
| 대상 모델 | π0.5, GR00T N1.5 (+OpenVLA) | 자체 3.0B (BitNet b1.58 + SigLIP-L) |
| 주 벤치마크 | LIBERO 4 suite | LIBERO 4 suite |
| 보조 | SimplerEnv, Pick-and-Can | 실물 조작(core 3 + OOD 3), 멀티모달 VQA 5종 |
| 비교군 | DuQuant, SmoothQuant | OpenVLA-OFT, π0, SmolVLA, NORA-Long, INT8/INT4 PTQ |
| 비트폭 | W4A8 / W4A4 / W8A16 | 1.58비트 W + INT8 A |
| 지표 | 성공률, 메모리(GB), 디노이징 스텝별 견고성 | 성공률, 메모리(1.4GB), 레이턴시(73ms) |

**LIBERO 4 suite 성공률**이 공통분모이고, 여기에 메모리·레이턴시가 붙는다.
BitVLA의 멀티모달 VQA는 백본 손상을 따로 재는 용도다.

---

## 8. 추적 자료

- [Efficient VLA Survey (2510.24795)](https://arxiv.org/abs/2510.24795) — 데이터·모델·학습 전 구간의 효율화를 다룬 첫 서베이
- [Efficient-VLAs-Survey 레포](https://github.com/yuzhaoshu/efficient-vla-survey) — 위 서베이의 논문 목록. 갱신됨
