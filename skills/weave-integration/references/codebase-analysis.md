# Codebase Analysis Guide

How to scan an existing project and identify Weave integration points.

## Check for Existing Weave Usage

Before scanning, check if Weave is already in use:

```
import weave
weave.init(
@weave.op
weave.Model
weave.Evaluation
weave.Dataset
weave.publish
```

**If Weave is already present (Evolve scenario)**:
- Do NOT add another `weave.init()` — verify the existing one is correct
- Do NOT re-convert classes that already extend `weave.Model`
- Focus on what's MISSING: untraced functions, unconverted classes, etc.
- Report what's already integrated and what can be added

**If no Weave found (Fresh integration)**: proceed with full analysis.

## Scan the Project

Scan for all functions, classes, and API calls. List everything — do not pre-filter.

For each target, decide the default checkbox state in `weave_instrumentation.md`:

### Recommend checked `[x]`
- Functions that call LLM APIs directly (e.g., `client.chat.completions.create(...)`)
- Pipeline/orchestration functions that combine multiple steps (e.g., retrieve → generate → format)
- Class methods that are the main inference entry point (e.g., `predict()`, `run()`, `invoke()`)
- Tool functions used by agents

### Recommend unchecked `[ ]` (but still listed)
- Pure utility functions (string formatting, data conversion, validation)
- Functions called at very high frequency (consider `tracing_sample_rate` if traced)
- Simple getters/setters with no LLM interaction

## Create `weave_instrumentation.md`

Use `references/weave-instrumentation-template.md` to create `weave_instrumentation.md` in the project root.

Fill in all sections from the analysis. The trace map uses a tree format with checkboxes:

```text
- [x] `api/rag.py` — `rag_pipeline()` — orchestration function
  - [x] `api/rag.py` — `retrieve_context()` — retrieval step
    - [x] OpenAI Embeddings API (auto-patched)
  - [x] `api/chat.py` — `generate_response()` — direct OpenAI call
    - [x] OpenAI Chat API (auto-patched)
  - [ ] `api/utils.py` — `format_output()` — pure formatting
- [x] `models/chatbot.py` — `ChatBot` — weave.Model candidate
```

The user reviews checkboxes and approves before any code changes.
