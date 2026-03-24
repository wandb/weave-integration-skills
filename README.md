# Weave Copilot Skill

AI coding agent skill for [W&B Weave](https://docs.wandb.ai/weave) — LLM tracing, evaluation, scoring, and production monitoring.

## What It Does

One skill that handles three modes:

| Mode | When | Examples |
|------|------|----------|
| **Code** | Write new Weave code from scratch | "Add Weave tracing to my LLM app", "Evaluate my chatbot with custom scorers" |
| **Integration** | Add Weave to an existing codebase | "Add Weave to my existing app", "Instrument my FastAPI app with Weave" |
| **Guide** | Answer Weave concept/usage questions | "What is weave.op?", "How do evaluations work?" |

## Integration Mode: How It Works

The Integration mode follows a strict 5-phase workflow to safely add Weave to existing codebases:

```
Phase 0: Project Setup
  └─ Ask for Weave project name (team/project format)

Phase 1: Codebase Analysis                    → codebase-analysis.md, framework-specific.md
  └─ Scan for LLM calls, model classes, eval logic, prompts
  └─ Detect frameworks (FastAPI, LangChain, CrewAI, etc.)
  └─ Check if Weave is already partially integrated

Phase 2: Integration Plan
  └─ Present structured plan of all proposed changes
  └─ ⏸ Wait for user approval before touching any code

Phase 3: Apply Changes                        → tracing-integration.md
  └─ Add weave.init() at the app entrypoint     → framework-specific.md
  └─ Decorate functions with @weave.op()         → tracing-integration.md
  └─ Convert model classes to weave.Model        → model-conversion.md
  └─ Wire evaluation logic into weave.Evaluation → evaluation-integration.md
  └─ Extract hardcoded prompts                   → prompt-versioning.md

Phase 4: Validation                            → integration-checklist.md
  └─ Run integration checklist (setup, tracing, models, eval)
  └─ Verify no regressions — Weave only observes, never changes app behavior
```

Key principle: **no code is modified without presenting a plan first**.

## Features

| Feature | Description |
|---------|-------------|
| **Tracing** | `@weave.op()`, `weave.Model`, nested traces, async support |
| **Evaluation** | `weave.Evaluation`, custom & built-in scorers, model comparison |
| **Datasets & Prompts** | `weave.Dataset`, `weave.StringPrompt`, `weave.MessagesPrompt`, versioning |
| **Monitors & Guardrails** | Production monitoring, content moderation, PII detection |
| **Feedback & Annotations** | Reactions, notes, human review with `AnnotationSpec` |
| **Cost Tracking** | Custom cost tracking, project-level aggregation |
| **Integrations** | OpenAI, Anthropic, LangChain, CrewAI, DSPy, LlamaIndex, and more |

## Skill Structure

```
skills/weave-copilot/
├── SKILL.md                         # Core instructions, 3-mode routing, doc URL mapping
├── evals/
│   └── evals.json                   # 46 test cases for skill trigger evaluation
└── references/
    ├── codebase-analysis.md         # Detection patterns for existing codebases
    ├── tracing-integration.md       # @weave.op() before/after patterns
    ├── model-conversion.md          # Class → weave.Model conversion
    ├── evaluation-integration.md    # Tests → weave.Evaluation conversion
    ├── prompt-versioning.md         # Prompt extraction patterns
    ├── framework-specific.md        # Per-framework integration recipes
    └── integration-checklist.md     # Pre/post integration validation
```

## Prerequisites

- Python 3.8+
- `pip install weave`
- `wandb login` or set `WANDB_API_KEY` environment variable

## Installation

### Claude Code

```bash
cp -r skills/weave-copilot/ ~/.claude/skills/weave-copilot/
```

### Cursor

```bash
cp -r skills/weave-copilot/ ~/.cursor/skills/weave-copilot/
```

### Project-level (any agent)

```bash
cp -r skills/ .claude/skills/
# or
cp -r skills/ .cursor/skills/
```

## Documentation

- [W&B Weave](https://docs.wandb.ai/weave) — Product overview
- [Tracing](https://docs.wandb.ai/weave/guides/tracking/tracing) — LLM app tracing
- [Evaluation](https://docs.wandb.ai/weave/guides/core-types/evaluations) — Evaluation pipelines
- [Scorers](https://docs.wandb.ai/weave/guides/evaluation/scorers) — Custom & built-in scorers
- [Integrations](https://docs.wandb.ai/weave/guides/integrations/autopatching) — Provider & framework integrations

## License

MIT
