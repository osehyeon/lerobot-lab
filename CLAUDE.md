# lerobot-lab

VLA(Vision-Language-Action) 모델 학습용 개인 실습 랩. 프로덕션 코드베이스가 아니라
**이해와 실험**이 목적이다. (2026-09 시작, 현재 스캐폴딩 단계)

## 목표

1. VLA의 핵심 메커니즘 이해 — 연속 동작을 토큰으로 다루는 방식, VLM 백본, 모방학습 파이프라인
2. LeRobot 기반으로 실제 정책 추론/파인튜닝까지

## 스택 결정 (2026-09-10)

- **주 프레임워크: `huggingface/lerobot`.** VLA 생태계에서 통합 라이브러리(timm/transformers 역할)에
  가장 가까움. 정책·데이터셋 포맷(LeRobotDataset)·실물 로봇 드라이버·평가가 한 코드베이스에 있다.
  1급 지원 정책: Pi0 / Pi0-FAST / Pi0.5, SmolVLA, GR00T N1.7, XVLA, EO-1 등 + ACT, Diffusion Policy, VQ-BeT.
- **`openvla/openvla`는 레퍼런스로만.** LeRobot 지원 목록에 없고, 자체 학습/추론 스택을 통째로 가진
  구세대 구조. 액션 토크나이저(`prismatic/vla/action_tokenizer.py`)와 RLDS 데이터 파이프라인
  (`prismatic/vla/datasets/rlds/`)이 교과서적이라 **읽기용**으로 가치가 있다.
  실전 베이스라인 지위는 π0 계열에 넘어갔다.
- 서빙에 vLLM 같은 엔진은 쓰지 않는다. VLA 추론은 batch=1 / 출력 7토큰 / 레이턴시 바운드라
  continuous batching·PagedAttention이 줄 이득이 없다. 순수 PyTorch + HTTP/websocket 서버 패턴이 표준.

## 환경 — 중요

**이 Mac(darwin/arm64)에서는 모델을 실행하지 않는다.** CUDA 전용 의존성(flash-attn 등)이라
로컬 설치를 시도하지 말 것. 로컬은 **코드 읽기·문서·스크립트 작성 전용**.

실제 학습/추론은 **학교 연구실 GPU 서버**에서 한다. 서버 세팅 시:
- Python 3.10, PyTorch cu121 계열, conda 환경 신규 생성
- flash-attn 빌드가 가장 잘 깨지는 지점 — 여기서 막히면 먼저 이걸 의심

## 작업 규칙

- 모델 가중치(수십 GB)와 데이터셋은 **커밋하지 않는다.** `from_pretrained`가 HF 캐시로 받게 둔다.
- 외부 레포(lerobot, openvla)는 읽기용 클론이면 서브모듈/커밋 대상이 아니다.
- 임시 스크립트·중간 산출물은 프로젝트가 아니라 스크래치패드에 둔다.
- 커밋 메시지는 **한 줄, 영어, 본문 없음, trailer 없음.** 명령형·문장형 대소문자,
  타입 접두사 없이 의도를 적는다 (`libero-lab` 규약과 동일).
- 사용자와의 대화는 **한국어**로. 기술 용어는 영어 그대로 써도 된다.
- 설명할 때는 "이 코드가 무엇을 하는가"보다 **"왜 이렇게 설계했는가"**를 우선한다. 학습이 목적이다.
