# W&B Skills

[English](README.md) | 한국어

[W&B](https://wandb.ai)를 위한 AI 코딩 에이전트 스킬 — [Models](https://docs.wandb.ai/models) (ML 실험 추적, 아티팩트 버전 관리, 모델 레지스트리)와 [Weave](https://docs.wandb.ai/weave) (LLM 트레이싱, 평가, 스코링, 프로덕션 모니터링)를 모두 지원합니다.

이 저장소에는 세 가지 스킬이 포함되어 있습니다:

| 스킬 | 제품 | 목적 |
|------|------|------|
| **[models](skills/models/)** | W&B Models | ML 실험 추적, 아티팩트 버전 관리, 모델 레지스트리, 스윕 |
| **[weave](skills/weave/)** | W&B Weave | LLM 트레이싱, 평가, 스코링을 위한 새 코드 생성 |
| **[weave-integration](skills/weave-integration/)** | W&B Weave | 기존 애플리케이션에 Weave 통합 (분석 → 계획 → 적용) |

## Models 스킬

### 이 스킬이 다루는 기능

| 기능 | 설명 |
|------|------|
| **Experiments** | `wandb.init()`, `wandb.log()`, `wandb.config`, `run.summary` |
| **Artifacts** | 데이터셋/모델 버전 관리, 메타데이터, alias, TTL |
| **Registry** | `link_artifact`를 통한 모델 라이프사이클 관리 |
| **Sweeps** | Bayesian/random/grid 하이퍼파라미터 탐색 |
| **Tables** | 이미지, 오디오, 멀티모달 등 리치 데이터 시각화 |
| **Leaderboard** | Tables + Reports를 활용한 평가 결과 자동 집계 |
| **Reports** | `wandb-workspaces`를 통한 프로그래매틱 리포트 생성 |
| **Public API** | Run, artifact, 메트릭 프로그래매틱 조회 |
| **Integrations** | PyTorch, Lightning, HuggingFace, Keras, FastAI, XGBoost, LightGBM |
| **Troubleshooting** | 흔한 에러와 해결법 |

### 스킬 구조

```
skills/models/
├── SKILL.md                         # 핵심 지침 + 빠른 참조
└── reference/
    ├── experiments.md               # 실험 추적 상세
    ├── artifacts.md                 # 아티팩트 관리
    ├── registry.md                  # 모델 레지스트리
    ├── sweeps.md                    # 스윕 설정 및 실행
    ├── api-patterns.md              # Public API, Tables, Reports
    ├── leaderboard.md               # 리더보드 패턴 (Tables + Reports)
    ├── integrations.md              # 프레임워크별 콜백
    ├── table-examples.md            # 다양한 테이블 예제
    └── troubleshooting.md           # 흔한 에러와 해결법
```

## Weave 스킬 (코드 생성)

### 이 스킬이 다루는 기능

| 기능 | 설명 |
|------|------|
| **Tracing** | `@weave.op()`, `weave.Model`, 중첩 트레이스, async, 샘플링 레이트, kind/color, 속성, 스레드 |
| **Evaluation** | `weave.Evaluation`, 모델 비교, 평가 파이프라인 |
| **Scorers** | 커스텀 함수/클래스 스코러, LLM-as-judge, 내장 스코러 (환각, 모더레이션, RAGAS, JSON/XML/Pydantic 검증) |
| **Datasets** | `weave.Dataset`, `weave.publish()` / `weave.ref()` 버전 관리 |
| **Prompts** | `weave.StringPrompt`, `weave.MessagesPrompt`, 파라미터화된 템플릿, 버전 관리 |
| **Monitors & Guardrails** | 프로덕션 모니터링 (LLM-as-judge), 가드레일 (`call.apply_scorer()`), 콘텐츠 모더레이션, PII 탐지 |
| **Feedback & Annotations** | 리액션, 노트, 커스텀 피드백, 휴먼 어노테이션 스코러 (`AnnotationSpec`) |
| **Costs** | 커스텀 비용 추적, 프로젝트 레벨 비용 집계 |
| **Integrations** | OpenAI, Anthropic, LiteLLM, LangChain, LlamaIndex, CrewAI, DSPy, Instructor, PydanticAI, Google ADK, AutoGen, Smolagents, OpenAI Agents SDK, MCP |
| **Troubleshooting** | 주요 오류 및 해결 방법 |

### 스킬 구조

```
skills/weave/
├── SKILL.md                         # 핵심 지침 + 빠른 참조
└── references/
    ├── tracing.md                   # @weave.op, weave.Model, 트레이스 패턴, 고급 설정
    ├── evaluation.md                # weave.Evaluation, 모델 비교
    ├── scorers.md                   # 커스텀 + 내장 스코러 (RAGAS 포함)
    ├── datasets.md                  # weave.Dataset, 버전 관리
    ├── prompts.md                   # StringPrompt, MessagesPrompt, 파라미터화
    ├── monitors-guardrails.md       # 프로덕션 모니터링, 안전 가드레일
    ├── feedback.md                  # 피드백 수집, 휴먼 어노테이션
    ├── costs.md                     # LLM 비용 추적 및 집계
    ├── integrations.md              # 프로바이더 & 에이전트 프레임워크 연동
    └── troubleshooting.md           # 주요 오류 및 해결 방법
```

## Weave Integration 스킬 (기존 앱 온보딩)

기존 애플리케이션에 Weave를 가이드 방식의 4단계 워크플로우로 통합합니다:

1. **분석** — 코드베이스를 스캔하여 LLM 호출, 모델 클래스, 평가 로직, 프롬프트 식별
2. **계획** — 어디에 무엇을 변경할지 통합 계획 제시
3. **적용** — 사용자 승인 후 자동으로 코드 수정
4. **검증** — 체크리스트로 모든 변경 사항 확인

### 이 스킬이 다루는 기능

| 기능 | 설명 |
|------|------|
| **코드베이스 분석** | LLM 프로바이더, 파이프라인 함수, 모델 클래스, 평가 로직, 프롬프트 감지 |
| **트레이싱 통합** | 기존 함수에 `weave.init()` 및 `@weave.op()` 추가 |
| **모델 변환** | 기존 클래스를 `weave.Model`로 변환 |
| **평가 통합** | 기존 테스트/벤치마크를 `weave.Evaluation`으로 연결 |
| **프롬프트 버전 관리** | 하드코딩된 프롬프트를 `weave.StringPrompt` / `weave.MessagesPrompt`로 추출 |
| **프레임워크별 가이드** | FastAPI, Streamlit, Flask, LangChain, CrewAI, DSPy, OpenAI Agents SDK 적용 방법 |

### 스킬 구조

```
skills/weave-integration/
├── SKILL.md                         # 핵심 지침 + 4단계 워크플로우
└── references/
    ├── codebase-analysis.md         # 탐지 패턴, 파일 분류
    ├── tracing-integration.md       # @weave.op() before/after 패턴
    ├── model-conversion.md          # 클래스 → weave.Model 변환
    ├── evaluation-integration.md    # 테스트 → weave.Evaluation 변환
    ├── prompt-versioning.md         # 프롬프트 추출 패턴
    ├── framework-specific.md        # 프레임워크별 적용 레시피
    └── integration-checklist.md     # 적용 전/후 검증 체크리스트
```

## 사전 요구 사항

- Python 3.8+
- `pip install wandb` (Models 스킬)
- `pip install weave` (Weave 스킬)
- `wandb login` 또는 `WANDB_API_KEY` 환경 변수 설정

## 설치

저장소를 클론합니다:

```bash
git clone https://github.com/hw-wandb/wandb-skills.git
```

그 다음 에이전트의 스킬 디렉토리로 복사합니다:

### Claude Code

```bash
cp -r wandb-skills/skills/models/ ~/.claude/skills/models/
cp -r wandb-skills/skills/weave/ ~/.claude/skills/weave/
cp -r wandb-skills/skills/weave-integration/ ~/.claude/skills/weave-integration/
```

### Cursor

```bash
cp -r wandb-skills/skills/models/ ~/.cursor/skills/models/
cp -r wandb-skills/skills/weave/ ~/.cursor/skills/weave/
cp -r wandb-skills/skills/weave-integration/ ~/.cursor/skills/weave-integration/
```

### 프로젝트 레벨 (모든 에이전트)

```bash
cp -r wandb-skills/skills/ .claude/skills/
# or
cp -r wandb-skills/skills/ .cursor/skills/
```

## 사용 방법

AI 코딩 에이전트가 자동으로 스킬을 감지합니다. 에이전트에게 다음과 같이 요청하세요:

### Models 스킬
- "내 학습 스크립트에 wandb 트래킹 추가해줘"
- "하이퍼파라미터 스윕 설정해줘"
- "예측 결과를 wandb 테이블로 로깅해줘"
- "모델을 wandb 레지스트리에 등록해줘"
- "평가할 때 결과를 한눈에 볼 수 있는 리더보드 만들어줘"

### Weave 스킬 (새 코드 생성)
- "내 LLM 앱에 Weave 트레이싱을 추가해줘"
- "커스텀 스코러로 내 챗봇을 평가해줘"
- "RAG 파이프라인을 위한 환각 스코러를 만들어줘"
- "프롬프트와 평가 데이터셋을 버전 관리해줘"
- "내 LLM에 프로덕션 모니터링을 설정해줘"

### Weave Integration 스킬 (기존 앱)
- "내 앱에 Weave 적용해줘"
- "기존 프로젝트에 Weave 연동하고 싶어"
- "내 FastAPI 앱에 Weave 옵저버빌리티를 적용해줘"

## W&B MCP 서버

이 스킬에서 다루지 않는 기능(예: Automations, Launch)은 W&B MCP 서버를 설치하여 에이전트에서 공식 문서를 직접 조회할 수 있습니다.

설정 방법은 [W&B MCP Server Docs](https://docs.wandb.ai/platform/mcp-server)를 참고하세요.

## W&B 문서

### Models
- [W&B Models](https://docs.wandb.ai/models) — 제품 개요
- [Experiments](https://docs.wandb.ai/models/track) — 실험 추적
- [Artifacts](https://docs.wandb.ai/models/artifacts) — 데이터 버전 관리
- [Registry](https://docs.wandb.ai/models/registry) — 모델 관리
- [Sweeps](https://docs.wandb.ai/models/sweeps) — 하이퍼파라미터 최적화
- [Tables](https://docs.wandb.ai/models/tables) — 데이터 시각화
- [Reports](https://docs.wandb.ai/models/reports) — 협업 리포트
- [SDK Cheat Sheet](https://docs.wandb.ai/models/ref/sdk-coding-cheat-sheet) — 빠른 참조

### Weave
- [W&B Weave](https://docs.wandb.ai/weave) — 제품 개요
- [Tracing](https://docs.wandb.ai/weave/guides/tracking/tracing) — LLM 앱 트레이싱
- [Evaluation](https://docs.wandb.ai/weave/guides/evaluation/overview) — 평가 파이프라인
- [Scorers](https://docs.wandb.ai/weave/guides/evaluation/scorers) — 커스텀 & 내장 스코러
- [Datasets](https://docs.wandb.ai/weave/guides/core-types/datasets) — 데이터셋 관리
- [Prompts](https://docs.wandb.ai/weave/guides/core-types/prompts) — 프롬프트 버전 관리
- [Monitors](https://docs.wandb.ai/weave/guides/evaluation/monitors) — 프로덕션 모니터링
- [Guardrails](https://docs.wandb.ai/weave/guides/evaluation/guardrails) — 안전 가드레일
- [Feedback](https://docs.wandb.ai/weave/guides/tracking/feedback) — 피드백 & 어노테이션
- [Costs](https://docs.wandb.ai/weave/guides/tracking/costs) — 비용 추적
- [Integrations](https://docs.wandb.ai/weave/guides/integrations) — 프로바이더 & 프레임워크 연동

## 기여하기

기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

MIT
