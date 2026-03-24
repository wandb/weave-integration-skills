# Manual Testing Guide

AI 에이전트(Claude Code, Cursor)에서 W&B 스킬을 직접 테스트하는 가이드입니다.

## 1. 설치

```bash
# 스킬 복사 (Claude Code)
cp -r skills/models/ ~/.claude/skills/models/
cp -r skills/weave/ ~/.claude/skills/weave/
cp -r skills/weave-integration/ ~/.claude/skills/weave-integration/

# 스킬 복사 (Cursor)
cp -r skills/models/ ~/.cursor/skills/models/
cp -r skills/weave/ ~/.cursor/skills/weave/
cp -r skills/weave-integration/ ~/.cursor/skills/weave-integration/
```

## 2. Models 스킬 테스트

### 트리거 테스트

다음 쿼리를 에이전트에게 입력하고, W&B Models 코드가 생성되는지 확인합니다:

| 쿼리 | 기대 결과 |
|------|-----------|
| "Add wandb tracking to my PyTorch training script" | `wandb.init()`, `wandb.log()` 코드 생성 |
| "Set up a hyperparameter sweep with bayesian optimization" | sweep config + `wandb.agent()` 코드 생성 |
| "Log my model predictions as a wandb table with images" | `wandb.Table` 코드 생성 |
| "Register my trained model to wandb registry with production alias" | `run.link_artifact()` 코드 생성 |
| "Version my dataset as a wandb artifact with metadata" | `wandb.Artifact` 코드 생성 |

### 확인 포인트

- [ ] 생성된 코드에 `import wandb`와 `wandb.init()` 포함
- [ ] context manager 패턴 사용 (`with wandb.init() as run:`)
- [ ] 완전한 실행 가능한 코드 (프래그먼트 아닌)
- [ ] `WANDB_API_KEY` 또는 `wandb login` 언급
- [ ] 한국어 쿼리에 한국어 응답

### 네거티브 테스트

다음 쿼리에는 Models 스킬이 **트리거되지 않아야** 합니다:

- "How do I deploy a Flask app on AWS?"
- "Write a unit test for my Python function"
- "Help me set up MLflow experiment tracking"

### 샘플 앱으로 Models 스킬 테스트

샘플 학습 앱을 작업 디렉토리에 복사합니다:

```bash
cp -r tests/fixtures/sample_training_app/ /tmp/test-wandb-models/
cd /tmp/test-wandb-models/
```

에이전트에게 다음을 요청합니다:

```
내 학습 스크립트에 wandb 트래킹 추가해줘
```

또는:

```
Add wandb tracking to my training script
```

#### 기대되는 변경 사항

##### train.py
- [ ] `import wandb` 추가
- [ ] `wandb.init(project=..., config=config, tags=..., job_type="training")` 추가
- [ ] 에폭 루프 안에 `wandb.log({"train/loss": ..., "train/accuracy": ..., "val/loss": ..., "val/accuracy": ...})` 추가
- [ ] `run.summary["best_val_accuracy"]` 설정
- [ ] best model을 `wandb.Artifact`로 저장

##### sweep_config.py
- [ ] `wandb.sweep(sweep_config, project=...)` 추가
- [ ] `wandb.agent(sweep_id, function=train)` 추가

##### evaluate.py
- [ ] `wandb.init(job_type="evaluation")` 추가
- [ ] 예측 결과를 `wandb.Table`로 로깅
- [ ] `run.summary`에 전체 정확도 설정

## 3. Weave 스킬 테스트 (코드 생성)

### 트리거 테스트

다음 쿼리를 에이전트에게 입력하고, Weave 코드가 생성되는지 확인합니다:

| 쿼리 | 기대 결과 |
|------|-----------|
| "Add Weave tracing to my LLM application" | `weave.init()`, `@weave.op()` 코드 생성 |
| "Set up an evaluation pipeline for my chatbot with custom scorers" | `weave.Evaluation`, scorer 코드 생성 |
| "LLM 출력 품질을 hallucination scorer로 평가하고 싶어" | `HallucinationFreeScorer` 사용 코드 생성 |
| "Create a versioned evaluation dataset from my JSON data" | `weave.Dataset`, `weave.publish()` 코드 생성 |
| "Track my LangChain agent calls with observability" | `weave.init()` + LangChain 연동 코드 생성 |

### 확인 포인트

- [ ] 생성된 코드에 `import weave`와 `weave.init('team/project')` 포함
- [ ] 함수에 타입 힌트 포함
- [ ] 완전한 실행 가능한 코드 (프래그먼트 아닌)
- [ ] `WANDB_API_KEY` 언급
- [ ] 한국어 쿼리에 한국어 응답

### 네거티브 테스트

다음 쿼리에는 Weave 스킬이 **트리거되지 않아야** 합니다:

- "How do I deploy a Flask app on AWS?"
- "Help me set up LangSmith tracing for my LLM app"
- "wandb.init으로 학습 실험 추적하고 싶어"

## 4. Weave Integration 스킬 테스트 (기존 앱 통합)

### 준비

샘플 앱을 작업 디렉토리에 복사합니다:

```bash
cp -r tests/fixtures/sample_app/ /tmp/test-weave-integration/
cd /tmp/test-weave-integration/
```

### 트리거 테스트

에이전트에게 다음을 요청합니다:

```
내 앱에 Weave 적용해줘
```

또는:

```
Add Weave to my existing app
```

### 4단계 워크플로우 확인

#### Phase 1: 분석
- [ ] 에이전트가 프로젝트 파일을 스캔함
- [ ] `main.py`를 엔트리포인트로 식별
- [ ] `chat.py`의 RAG 파이프라인 함수들(`classify_intent`, `retrieve_context`, `generate_answer`, `rag_pipeline`)을 `@weave.op()` 후보로 식별
- [ ] `models.py`의 `ChatBot` 클래스를 `weave.Model` 후보로 식별 (`chat` → `predict` 변환)
- [ ] `ChatBot.chat`이 `rag_pipeline`을 호출하는 관계를 파악
- [ ] `eval_test.py`의 평가 루프를 `weave.Evaluation` 후보로 식별
- [ ] `chat.py`의 `SYSTEM_PROMPT`를 프롬프트 버전 관리 후보로 식별

#### Phase 2: 계획
- [ ] 에이전트가 통합 계획을 구조화된 형태로 제시
- [ ] 수정할 파일, 라인 번호, 변경 내용이 명시됨
- [ ] 사용자 승인을 요청함 (**코드 수정 전에**)

#### Phase 3: 적용 (승인 후)
- [ ] `main.py`: `import weave` + `weave.init()` 추가
- [ ] `chat.py`: `import weave` + 모든 함수에 `@weave.op()` + 타입 힌트 추가
- [ ] `models.py`: `ChatBot` → `weave.Model` 변환 (model→model_name, chat→predict, `__init__` 제거)
- [ ] `eval_test.py`: `weave.Dataset` + `weave.Evaluation` 전환

#### Phase 4: 검증
- [ ] 에이전트가 체크리스트를 기반으로 변경 사항 검증
- [ ] `WANDB_API_KEY` 설정 안내
- [ ] Weave UI 확인 안내 (`https://wandb.ai/<team>/<project>/weave`)

### 추가 통합 테스트 쿼리

| 쿼리 | 기대 동작 |
|------|-----------|
| "Instrument my FastAPI app with Weave" | lifespan에 `weave.init()`, 핸들러에 `@weave.op()` |
| "내 LangChain 앱에 Weave를 추가해줘" | `weave.init()` + auto-patch 안내 |
| "Convert my model class to use weave.Model" | `weave.Model` 변환 가이드 + 적용 |

## 5. 트리거 분리 테스트

세 스킬이 올바르게 분리되어 트리거되는지 확인합니다:

### Models 스킬만 트리거되어야 하는 쿼리

| 쿼리 | 이유 |
|------|------|
| "Add wandb experiment tracking to my training script" | ML 학습 추적 (Weave 아님) |
| "Set up a hyperparameter sweep" | W&B Sweeps (Weave 아님) |
| "Register my model to wandb registry" | Model Registry (Weave 아님) |

### Weave 스킬만 트리거되어야 하는 쿼리

| 쿼리 | 이유 |
|------|------|
| "Create a new Weave evaluation from scratch" | 새 코드 생성 (기존 앱 아님) |
| "weave.op으로 새 함수를 만들어줘" | 새 코드 생성 |
| "Write a HallucinationFreeScorer for my app" | 특정 API 사용법 (통합 아님) |

### Weave Integration 스킬만 트리거되어야 하는 쿼리

| 쿼리 | 이유 |
|------|------|
| "Add Weave to my existing app" | 기존 앱 통합 |
| "내 앱에 Weave 적용해줘" | 기존 앱 통합 |
| "Instrument my FastAPI app with Weave" | 기존 프레임워크에 적용 |

## 6. E2E 검증 (실제 실행)

스킬이 생성/적용한 코드가 실제로 동작하는지 확인합니다.

### 6-1. Models E2E 검증

#### 사전 준비

```bash
export WANDB_API_KEY="..."
pip install wandb torch torchvision
```

#### 실행

Models 스킬이 적용된 `/tmp/test-wandb-models/` 디렉토리에서:

```bash
cd /tmp/test-wandb-models/
python train.py
```

#### 체크리스트

- [ ] `python train.py` 실행 시 에러 없이 완료
- [ ] W&B 대시보드에 run이 나타남 (`https://wandb.ai/<team>/<project>`)
- [ ] train/loss, train/accuracy, val/loss, val/accuracy 메트릭이 차트로 표시
- [ ] config에 learning_rate, epochs, batch_size 등 하이퍼파라미터가 기록됨
- [ ] run.summary에 best_val_accuracy가 설정됨
- [ ] Artifacts 탭에 best_model.pth가 기록됨

#### Evaluation 검증 (선택)

```bash
python evaluate.py
```

- [ ] W&B에 job_type="evaluation"인 별도 run 생성
- [ ] 예측 결과가 wandb.Table로 표시 (true_label, predicted_label, correct 컬럼)
- [ ] 클래스별 정확도가 summary에 기록됨

#### Sweep 검증 (선택)

```bash
python sweep_config.py  # sweep 생성 후 agent 실행
```

- [ ] W&B Sweeps 탭에 sweep이 나타남
- [ ] Bayesian 방식으로 하이퍼파라미터 탐색 진행
- [ ] 각 sweep run의 val_accuracy가 기록되고 비교 가능

### 6-2. Weave E2E 검증

#### 사전 준비

```bash
export OPENAI_API_KEY="sk-..."
export WANDB_API_KEY="..."
pip install weave openai
```

#### 실행

Phase 3 적용이 완료된 `/tmp/test-weave-integration/` 디렉토리에서:

```bash
cd /tmp/test-weave-integration/
python main.py
```

#### 트레이스 트리 구조

Weave UI (`https://wandb.ai/<team>/<project>/weave/traces`)에서 다음 계층 구조가 보여야 합니다:

```
ChatBot.predict
└── rag_pipeline
    ├── classify_intent
    │   └── openai.chat.completions.create
    ├── retrieve_context
    └── generate_answer
        └── openai.chat.completions.create
```

#### 체크리스트

- [ ] `python main.py` 실행 시 에러 없이 완료
- [ ] Weave UI에 트레이스가 나타남
- [ ] `ChatBot.predict` 트레이스 하위에 `rag_pipeline`이 자식으로 표시
- [ ] `rag_pipeline` 하위에 3개의 자식 스팬 (classify → retrieve → answer)
- [ ] 각 OpenAI 호출에 토큰 사용량과 비용 표시
- [ ] `weave.Model` 하위에 모델 버전이 기록됨

#### Evaluation 검증 (선택)

```bash
python eval_test.py
```

- [ ] Weave UI의 Evaluations 탭에 평가 결과가 나타남
- [ ] 각 테스트 케이스별 scorer 결과가 표시됨
- [ ] 전체 정확도 요약이 표시됨

## 7. 자동 테스트 실행

```bash
# 프로젝트 루트에서 (fixtures 디렉토리 제외)
python -m pytest tests/ --ignore=tests/fixtures -v
```
