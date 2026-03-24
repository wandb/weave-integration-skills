# Weave Instrumentation Plan

> This file is a collaboration artifact. The AI fills it in based on codebase analysis,
> pre-checking recommended trace targets. Review the checkboxes and uncheck anything
> you don't want traced. Then approve for implementation.

## Environment

- **Python runner**: <!-- e.g., uv, poetry, pip, conda -->
- **Install command**: <!-- e.g., uv add weave, pip install weave -->
- **WANDB_API_KEY**: <!-- set / not set -->
- **WEAVE_PROJECT**: <!-- team/project -->
- **WANDB_BASE_URL**: <!-- only for Dedicated Cloud or Self-Managed W&B -->

## Current Structure

### Entry Point

- **File**: <!-- e.g., app.py -->
- **Pattern**: <!-- e.g., FastAPI lifespan, if __name__ == "__main__" -->
- **`weave.init()` placement**: <!-- e.g., inside lifespan context manager -->

### LLM Providers Detected

- <!-- e.g., OpenAI (auto-patched), Anthropic (auto-patched) -->

### Frameworks Detected

- <!-- e.g., FastAPI, LangChain -->

## Trace Map

All traceable functions are listed below. The AI pre-checks recommended targets.
**Review and uncheck anything you do NOT want traced.**

### Functions

<!-- Format:
- [x] `file.py` — `function_name()` — reason
- [ ] `file.py` — `utility_func()` — reason (unchecked = not recommended but available)
-->

```text
Example trace tree (shows nesting):

- [x] main_pipeline()
  - [x] retrieve_context()
    - [x] OpenAI Embeddings API  (auto-patched)
  - [x] generate_response()
    - [x] OpenAI Chat API  (auto-patched)
  - [ ] format_output()  — pure formatting, optional
```

### Classes

<!-- Format:
- [x] `file.py` — `ClassName` — reason for weave.Model conversion
- [ ] `file.py` — `ClassName` — not recommended (utility/data container)
-->

## Optional: `weave.Model` Candidates

<!-- List classes worth converting to weave.Model for versioning.
     Leave empty if none are suitable. See reference/model-conversion criteria. -->

| File | Class | Main Method | Why |
|------|-------|-------------|-----|
| <!-- e.g., models/bot.py --> | <!-- ChatBot --> | <!-- generate() → predict() --> | <!-- Holds LLM config, good for eval comparison --> |

## Optional: Prompts to Version

<!-- Hardcoded prompts that could become weave.StringPrompt / weave.MessagesPrompt.
     Skip if prompts are already inside a weave.Model (already versioned). -->

| File | Line | Current Form | Suggested Name |
|------|------|-------------|----------------|

## Optional: Evaluation Candidates

<!-- Existing test/eval code that could become weave.Evaluation. -->

| File | Description |
|------|-------------|

## Optional: PII / Sensitive Data

<!-- List any fields or data that should NOT be traced.
     The user should fill this in. -->

- <!-- e.g., user email, credit card numbers -->

## Approval

- [ ] I have reviewed the trace map and checkboxes above
- [ ] Approved for implementation
