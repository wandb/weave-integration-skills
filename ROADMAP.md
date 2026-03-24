# Roadmap

Future improvements and known issues for the Weave Integration skill.

## Planned

### `weave.Model` Guidance

Need a dedicated reference file (`references/model-conversion.md`) with clear criteria:

- **When to convert**: class holds LLM config + has inference method → `weave.Model`
- **When NOT to convert**: pure utility, data container, thin wrapper → keep `@weave.op()`
- **Function-based code**: can still become `weave.Model` if it represents a meaningful app/agent boundary
- Reference: Kei's `structure_update_kei` branch has a good `model-conversion.md` to use as starting point

### `@weave.op()` Display Customization (`kind`, `color`)

The `@weave.op()` decorator may support display customization for the trace UI, but this is not confirmed working.

- `kind: llm` and `color: green` were attempted in `structure_update_kei` but didn't work as expected
- Need to fetch latest docs (`/weave/guides/tracking/ops`) to verify current API
- Once confirmed, add to `weave-instrumentation-template.md` trace map format and `transformation-patterns.md`

### Gotchas Table

Common AI mistakes to catch during integration:

| Gotcha | Wrong | Right |
|--------|-------|-------|
| `weave.init` arguments | `weave.init(project="x")` | `weave.init("x")` |
| Bare `python` with unknown env | `python script.py` | Use detected runner (`uv run`, etc.) |
| Pydantic reserved name | `model: str` attribute | `model_name: str` |
| `weave.init()` placement | Module level in FastAPI | Inside `lifespan` context manager |

Add to SKILL.md once validated.

### wandb/skills Repo Alignment

Restructure for eventual PR contribution to the official `wandb/skills` repo:

- `npx skills add` installation support
- SPDX license headers

## Known Issues

- `kind: llm`, `color: green` in `@weave.op()` — needs API verification against latest docs
- Trace tree in `weave_instrumentation.md` is text-based; consider better formats
