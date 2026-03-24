---
name: weave-integration
description: >
  Integrate W&B Weave into an existing application — analyze the codebase, identify
  LLM calls, pipeline functions, model classes, and evaluation logic, then present
  an integration plan and apply changes on user approval.
  Use this skill when the user wants to add Weave to their existing app, integrate
  Weave into their codebase, instrument their current code with Weave, retrofit
  tracing into their project, or connect their existing LLM application to Weave.
  Trigger keywords: "add Weave to my app", "integrate Weave", "instrument my code
  with Weave", "retrofit Weave tracing", "apply Weave to my project",
  "connect Weave to my app", "set up Weave in my existing project",
  "Weave 적용", "기존 앱에 Weave 추가", "내 앱에 Weave 적용해줘",
  "내 코드에 Weave 연동", "Weave 통합", "기존 프로젝트에 Weave 설정",
  "내 LLM 앱에 Weave 연결", "Weave로 내 코드 계측",
  "현재 코드에 트레이싱 추가", "기존 코드에 Weave 붙여줘",
  "Weave onboarding", "Weave 온보딩", "Weave 셋업",
  "내 앱에 옵저버빌리티 추가", "add observability to my app".
  This skill is specifically for modifying existing code to add Weave.
  Do NOT trigger for requests to write new Weave code from scratch — that is
  handled by the 'weave' skill.
---

# W&B Weave Integration Skill

Analyze an existing codebase and integrate W&B Weave tracing, evaluation, and observability — with a guided plan before any code changes.

## Workflow: 4 Phases

Follow these phases strictly. **Never modify user code without presenting a plan first.**

### Phase 0: Project Setup

Before analyzing the codebase, ask the user for the Weave project name:

> `weave.init()` requires a project name in `'team/project'` format.
> - **team**: Your W&B team name or username (e.g., `my-team`)
> - **project**: A name for this Weave project (e.g., `my-llm-app`)
>
> Example: `weave.init('my-team/my-llm-app')`
>
> What project name would you like to use?

Use the provided project name in all generated `weave.init()` calls throughout the integration.

### Phase 1: Codebase Analysis

Read `references/codebase-analysis.md`, then scan the user's project to identify:

1. **Entrypoint** — where the app starts (`main.py`, `app.py`, `if __name__ == "__main__"`, etc.)
2. **LLM API calls** — OpenAI, Anthropic, LiteLLM, etc. (candidates for auto-patching)
3. **Custom functions** — functions that call LLMs or process data (candidates for `@weave.op()`)
4. **Model classes** — classes with LLM config + prediction methods (candidates for `weave.Model`)
5. **Evaluation logic** — existing tests, scoring, benchmarks (candidates for `weave.Evaluation`)
6. **Hardcoded prompts** — system messages, template strings (candidates for prompt versioning)
7. **Framework usage** — LangChain, CrewAI, FastAPI, Streamlit, etc. (determines integration recipe)

### Phase 2: Integration Plan

Present findings to the user as a clear plan:

```
## Weave Integration Plan

### 1. Setup
- Install: `pip install weave` (+ extras if needed)
- Add `weave.init('<project name from Phase 0>')` to [entrypoint file]

### 2. Tracing (N functions found)
- [file:line] `function_name` — add `@weave.op()`
- [file:line] `function_name` — add `@weave.op()`

### 3. Model Conversion (N classes found)
- [file:line] `ClassName` — convert to `weave.Model`

### 4. Evaluation (if applicable)
- [file] existing test logic → `weave.Evaluation`

### 5. Prompt Versioning (if applicable)
- [file:line] hardcoded prompt → `weave.StringPrompt`
```

**Wait for user approval before proceeding.**

### Phase 3: Apply Changes

On approval, read the relevant reference files and apply changes in this order:

1. **Setup** — add `import weave` and `weave.init()` to entrypoint
2. **Tracing** — add `@weave.op()` decorators + type hints (read `references/tracing-integration.md`)
3. **Model conversion** — convert classes to `weave.Model` (read `references/model-conversion.md`)
4. **Evaluation** — wire existing tests to `weave.Evaluation` (read `references/evaluation-integration.md`)
5. **Prompt versioning** — extract prompts (read `references/prompt-versioning.md`)

### Phase 4: Validation

Read `references/integration-checklist.md` and verify all changes, then guide the user to:
1. Run the app and confirm it works
2. Check the Weave UI at `https://wandb.ai/<team>/<project>/weave`

## Reference Files

| File | When to read | Covers |
|------|-------------|--------|
| `references/codebase-analysis.md` | Phase 1 — scanning the project | Detection patterns, file classification, output format |
| `references/tracing-integration.md` | Phase 3 — adding tracing | `weave.init()` placement, `@weave.op()` before/after patterns, decorator order, type hints |
| `references/model-conversion.md` | Phase 3 — converting classes | `weave.Model` conversion steps, before/after patterns, edge cases |
| `references/evaluation-integration.md` | Phase 3 — wiring evaluation | Existing tests → `weave.Evaluation`, scorer conversion, dataset extraction |
| `references/prompt-versioning.md` | Phase 3 — extracting prompts | Hardcoded prompts → `weave.StringPrompt` / `weave.MessagesPrompt` |
| `references/framework-specific.md` | Phase 1 & 3 — framework detection | FastAPI, Streamlit, Flask, LangChain, CrewAI, DSPy, OpenAI Agents SDK integration recipes |
| `references/integration-checklist.md` | Phase 4 — validation | Pre/post integration checks, common issues |

## Universal Rules

1. **Never modify code without presenting a plan first** — always complete Phase 2 before Phase 3
2. **Preserve existing functionality** — integration must not change app behavior
3. **Minimal changes** — only add what's needed for Weave integration
4. **Add type hints** only to functions being decorated with `@weave.op()`
5. **Use `import weave`** — never `from weave import *`
6. **Respond in the user's language** — Korean or English
7. **Always mention `WANDB_API_KEY`** setup

## Quick Reference: Integration Patterns

```python
# 1. Setup (entrypoint file)
import weave
weave.init('team/project')  # Use the project name from Phase 0

# 2. Trace a function — add decorator + type hints
@weave.op()
def existing_function(query: str) -> str:
    ...  # existing code unchanged

# 3. Convert class to weave.Model
class MyApp(weave.Model):
    model_name: str
    temperature: float = 0.7

    @weave.op()
    def predict(self, input: str) -> str:
        ...  # existing logic

# 4. Framework apps — just add weave.init()
# LangChain, CrewAI, LlamaIndex, DSPy: auto-patched
# OpenAI Agents SDK: also add set_trace_processors([WeaveTracingProcessor()])
```
