# LeRobot 지원 정책(Policy) 정리

> 작성 2026-09-10. 출처: LeRobot 공식 문서(huggingface.co/docs/lerobot) 및 README.
> 숫자는 공식 문서 기준이며 "indicative"라고 명시된 값들이다. 정확한 재현 수치가 아니라
> **하드웨어 고르기용 어림값**으로 쓸 것.

## 0. 전체 지원 목록 (2026-09 기준)

| 분류 | 정책 |
|---|---|
| Imitation Learning | `act`, `diffusion`, `vqbet`, `multi_task_dit` |
| VLA | `pi0`, `pi0_fast`, `pi05`, `smolvla`, `groot`, `xvla`, `eo1`, `molmoact2`, `wall_x` (WALL-OSS), `evo1` |
| RL | `sac` (HIL-SERL), `tdmpc` (QC-FQL 예정) |
| World Model | VLA-JEPA, LingBot-VA, FastWAM |
| Reward Model | SARM, TOPreward, Robometer |

아래에서는 **널리 쓰이고 문서화가 잘 된 것들**만 다룬다. World/Reward 모델 계열은
비교적 최근 추가분이라 여기서는 목록만 남긴다.

---

## 1. ACT — 시작점

**Action Chunking with Transformers.** Zhao et al., [arXiv:2304.13705](https://arxiv.org/abs/2304.13705)
("Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware", ALOHA 논문).
LeRobot 공식 문서가 **첫 정책으로 명시적으로 추천**한다.

- **크기: ~80M.** VLM 없음. 태스크 데모만으로 스크래치 학습.
- **구조:** ResNet-18 비전 백본(카메라 여러 대) → Transformer 인코더(이미지 특징 +
  관절 위치 + 학습된 latent `z`) → Transformer 디코더가 **미래 k스텝 액션 청크**를 출력.
- `z`는 CVAE의 style 변수. 학습 때 데모의 다양성(사람마다 다른 수행 방식)을 흡수하고,
  **추론 시엔 0으로 고정**한다. 즉 "평균적인 시연자"처럼 행동하게 만든다.
- **데이터 효율:** 데모 50개로도 높은 성공률이 나온다고 문서가 밝힌다.

**왜 액션 청킹인가** — 한 스텝씩 예측하면 오차가 누적되고(compounding error),
사람 시연 특유의 멈칫거림(pause)이 정책을 정지 상태로 빨아들인다. 앞으로 k스텝을
한 번에 뱉으면 유효 의사결정 주기가 1/k로 줄어 이 두 문제가 동시에 완화된다.
**이후 거의 모든 정책(Diffusion, π0, SmolVLA, GR00T)이 이 청킹 구조를 계승한다.**

```bash
lerobot-train --policy.type=act --dataset.repo_id=${HF_USER}/your_dataset \
  --policy.device=cuda --output_dir=outputs/train/act_x --job_name=act_x
```

---

## 2. Diffusion Policy

- **액션 청크를 확산 모델로 생성.** 노이즈에서 시작해 반복 디노이징으로 액션 시퀀스를 뽑는다.
- **강점: 멀티모달 분포.** "왼쪽으로 돌아가도 되고 오른쪽으로 돌아가도 되는" 상황에서
  회귀 모델은 두 답의 평균(= 벽에 정면충돌)을 내지만, 확산은 하나를 골라낸다.
  모방학습에서 이게 결정적인 경우가 많다.
- **약점: 샘플링 비용.** 디노이징 스텝만큼 forward를 돌아야 해서 추론이 무겁다.
- ACT보다 학습이 오래 걸린다 (같은 조건에서 30~60분 vs 2~4시간).

## 3. VQ-BeT

- **Vector-Quantized Behavior Transformer.** 액션을 **학습된 코드북**으로 양자화해
  이산 토큰으로 다루고, Transformer가 그 토큰을 예측한다.
- 이산 토큰의 멀티모달 표현력 + 확산보다 싼 추론이라는 절충점.
- 액션 표현 축에서 "고정 binning(OpenVLA)"과 "연속 확산(π0)" 사이에 있다.

---

## 4. SmolVLA — 가장 현실적인 첫 VLA

HuggingFace 자체 개발. [논문 2506.01844](https://huggingface.co/papers/2506.01844).

- **크기: 450M** (`lerobot/smolvla_base`). VLA치고 매우 작다.
- 입력: 카메라 여러 대 + 로봇 센서모터 상태 + 자연어 지시 → **action expert**가
  액션 청크를 생성.
- **A100 한 장에서 20k 스텝 ≈ 4시간.** VRAM ~10–16GB라 RTX 4080급에서도 돈다.
- 메모리가 빡빡하면 `freeze_vision_encoder=True`가 1차 처방.
- 파인튜닝 데이터 권고가 구체적이다: **에피소드 50개**, 그리고 태스크 변형(예: 큐브 위치)
  **하나당 10개씩**. 문서가 "25개로 해봤는데 성능이 안 나왔다"고 못박아 뒀다.
  → 데이터 수집 계획 세울 때 이 숫자를 기준선으로 쓸 것.

```bash
lerobot-train --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=${HF_USER}/mydataset \
  --batch_size=64 --steps=20000 --policy.device=cuda
```

---

## 5. π0 계열 (Physical Intelligence)

LeRobot 구현은 [OpenPI](https://github.com/Physical-Intelligence/openpi)에서 이식. Apache 2.0.
설치는 `pip install -e ".[pi]"`.

### π0 (`pi0`)
- **3B VLM 백본 + flow matching 액션 헤드.** flow matching은 확산의 변종으로,
  사전학습 VLM에 **연속 액션 출력**을 붙이는 방법이다.
- 8종 로봇 플랫폼(UR5e, Franka, Bimanual Trossen, Mobile 계열 등) **cross-embodiment 학습.**
- 최대 **50Hz** 제어 출력.
- 체크포인트: `lerobot/pi0_base`, `lerobot/pi0_libero`.

### π0-FAST (`pi0_fast`)
- **같은 문제를 토큰으로 푼다.** flow matching 대신 **자기회귀 next-token 예측.**
- 백본: PaliGemma 계열 — SigLIP 비전 타워 + Gemma 2B.
- **FAST(Frequency-space Action Sequence Tokenization)**: 액션 청크 `(H, D)`를
  ① 정규화(quantile 권장) → ② 차원별 **DCT** → ③ 양자화로 고주파 계수 제거 →
  ④ 저주파 우선 flatten → ⑤ **BPE**로 압축. 기존 토큰화 대비 약 **10배 압축.**
- **왜 DCT인가** — 단순 per-dimension binning은 정밀·고주파 동작에서 무너진다.
  액션 시퀀스는 시간축 신호이므로 주파수 영역이 훨씬 조밀하게 압축된다.
  JPEG/MP3와 완전히 같은 발상이고, 그래서 **아무 VLM이나 VLA로 바꿀 수 있다.**
- 학습이 π0보다 **약 5배 빠르다.** 추론은 자기회귀 디코딩 + KV 캐시.
- 체크포인트: `lerobot/pi0fast-base`, `lerobot/pi0fast-libero`,
  토크나이저 `lerobot/fast-action-tokenizer` (실 로봇 시퀀스 100만+ 로 학습).
  `lerobot-train-tokenizer`로 자기 데이터에 맞춰 재학습도 가능.

### π0.5 (`pi05`)
- 목표는 **open-world generalization** — 학습 때 못 본 환경/물체로의 일반화.
- 핵심은 **이종 데이터 co-training**: 웹 멀티모달 데이터(캡셔닝/VQA/검출) +
  사람의 구두 코칭 + 서브태스크 명령 + cross-embodiment + 다환경 + 모바일 조작 ~400시간.
- 상태를 **256 bin으로 이산화해 프롬프트에 써 넣는다**(LIBERO 설정 기준).
  액션은 내부적으로 32차원으로 패딩하고 손실은 앞 7차원만 사용.
- **정규화가 quantile 기본** — 데이터셋 `meta/stats.json`에 `q01`/`q99`가 없으면
  첫 배치에서 터진다. `lerobot-edit-dataset --operation.type recompute_stats`로 해결.
- LIBERO 성적(LeRobot 구현 / OpenPI 레퍼런스): 평균 **97.5% / 96.85%**.
- 체크포인트: `lerobot/pi05_base`, `lerobot/pi05_libero_base`.
- PaliGemma 토크나이저(`google/paligemma-3b-pt-224`)가 gated라 **HF 라이선스 동의 + 로그인 필요.**

> **`--policy.path` vs `--policy.pretrained_path` 함정**
> `path`는 가중치+`config.json`을 같이 로드하고, `pretrained_path`는 **가중치만** 로드한다.
> 후자는 `n_action_steps` 같은 설정이 기본값으로 리셋되므로 명시적으로 다시 넘겨야 한다.

---

## 6. GR00T N1.7 (`groot`, NVIDIA)

- 휴머노이드 지향 cross-embodiment 파운데이션 모델. 베이스: `nvidia/GR00T-N1.7-3B`.
- 백본 **Cosmos-Reason2 / Qwen3-VL**, 액션은 **flow matching action transformer**로
  비전·언어·proprioception 조건부 청크 생성.
- 학습 데이터: 실 로봇 + **Isaac GR00T Blueprint 합성 데이터** + 인터넷 스케일 영상.
- **주의 — 파괴적 변경:** N1.5 지원이 제거됐다. N1.5 체크포인트를 쓰려면
  `pip install 'lerobot==0.5.1'`로 핀 고정해야 한다.
- LIBERO 평균 96.5%. 라이선스는 Apache가 아니라 **NVIDIA Open Model License.**
- SO-101 같은 새 로봇에는 `--policy.embodiment_tag=new_embodiment`.

---

## 7. 참고: OpenVLA (LeRobot 미지원)

LeRobot 지원 목록에 **없다.** 자체 학습/추론 스택을 통째로 가진 구세대 구조라
섞어 쓰지 않고 **읽기용 레퍼런스**로만 둔다. 볼 가치가 있는 두 곳:

- `prismatic/vla/action_tokenizer.py` — 연속 액션 → 이산 토큰 매핑의 교과서적 최소 구현.
  **π0-FAST의 DCT+BPE와 대조해서 읽으면** "단순 binning이 왜 부족한가"가 선명해진다.
- `prismatic/vla/datasets/rlds/` — RLDS 파이프라인. LeRobotDataset과 대조용.

---

## 8. 축으로 정리: 액션을 어떻게 표현하는가

이 분야의 실질적 갈림길이다.

| 표현 | 대표 | 추론 비용 | 멀티모달 분포 | 비고 |
|---|---|---|---|---|
| 연속값 회귀 (CVAE) | ACT | 매우 낮음 | 약함 | latent `z`로 부분 보완 |
| 학습된 코드북 양자화 | VQ-BeT | 낮음 | 보통 | 이산 + 표현력 절충 |
| 고정 binning 토큰 | OpenVLA | 중간 | 보통 | 정밀 동작에서 한계 |
| 주파수영역 토큰 (DCT+BPE) | π0-FAST | 중간(자기회귀, KV캐시) | 강함 | 10배 압축, 학습 5배 빠름 |
| Flow matching / 확산 | Diffusion Policy, π0, π0.5, GR00T | 높음(반복 디노이징) | 강함 | 현재 대형 VLA의 주류 |

**관찰:** 대형 VLA는 flow matching으로 수렴하는 추세지만, π0-FAST는
"토큰이면 기존 LM 인프라(자기회귀, KV캐시)를 그대로 쓴다"는 반대 방향의 장점을 보여준다.
둘은 경쟁이라기보다 **학습 속도 ↔ 추론 지연**의 트레이드오프다.

---

## 9. 하드웨어 — 연구실 서버 계획용

### VRAM (배치 8, AdamW 기준, 공식 문서 어림값)

| 그룹 | 정책 | Peak VRAM | 최소 GPU |
|---|---|---:|---|
| Light BC | `act`, `vqbet`, `tdmpc` | ~2–6GB | RTX 3060, L4, A10G |
| Diffusion | `diffusion`, `multi_task_dit` | ~8–14GB | RTX 4070+ |
| Small VLA | `smolvla` | ~10–16GB | RTX 4080+ |
| Large VLA | `pi0`, `pi0_fast`, `pi05`, `xvla`, `wall_x` | ~24–40GB | A100 40GB+ (24GB는 BS 1도 빠듯) |
| Multimodal | `groot`, `eo1` | ~24–40GB | A100 40GB+ |

메모리는 배치 크기에 대략 선형. AdamW 옵티마이저 상태가 forward+backward 대비 30~100% 추가.

### 학습 시간 (50 에피소드 ≈ 45k 프레임, 5 epoch, 640×480)

| 환경 | 정책 | 배치 | 소요 |
|---|---|---|---:|
| RTX 4090 / 3090 | `act` | 8 | ~30–60분 |
| RTX 4090 / 3090 | `diffusion` | 8 | ~2–4시간 |
| A100 40GB | `smolvla` | 16 | ~1–2시간 |
| A100 40GB | `pi0` / `pi05` | 4 | ~4–8시간 |
| 4×H100 | `smolvla` | 32 | ~1–2시간 |
| **Apple Silicon (MPS)** | `act` | 4 | **~6–14시간** |

> **수렴 기준이 스텝이 아니라 epoch이다.** 로보틱스 모방학습은 보통
> **데이터셋 5~10 epoch**이면 수렴한다. 수십만 스텝을 돌리는 게 아니다.
> 학습을 짧게 잡으면 LR 스케줄도 같이 줄여야 한다 (`--policy.scheduler_decay_steps≈--steps`).
> 안 그러면 LR이 피크에 머문 채 끝난다.

> **병목 진단 지표: `dataloading_s` vs `update_s`.** 전자가 후자에 근접하면
> GPU를 더 붙여도 소용없다. `--num_workers`, 이미지 해상도, 디스크 속도를 먼저 볼 것.
> (`docs/lerobot.md`에 적은 "비디오 디코딩이 병목"이 여기서 구체적 지표로 확인된다.)

---

## 10. 이 프로젝트의 진입 경로

1. **`act` + 시뮬(LIBERO 등)** — 파이프라인 한 바퀴 완주. 여기서 데이터로더·평가·체크포인트
   흐름을 몸에 익힌다. 빠르고 싸서 디버깅 루프가 짧다.
2. **`smolvla` 파인튜닝** — 첫 VLA. 450M이라 연구실 GPU 사양 부담이 적고,
   `smolvla_base`에서 시작하니 VLM 백본이 붙는 지점을 실물로 볼 수 있다.
3. **`pi05` 또는 `pi0_fast`** — 여기서부터 A100급이 필요하다.
   두 개를 **같은 데이터로 돌려 비교**하면 flow matching ↔ 자기회귀 토큰의
   트레이드오프를 직접 측정할 수 있다. 이 랩의 목표에 가장 잘 맞는 실험.

로컬 Mac은 코드 읽기·문서 전용 (`CLAUDE.md`). 위 표의 MPS 행은 참고용일 뿐 여기서 돌리지 않는다.
