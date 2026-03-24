# W&B Skills

English | [한국어](README_ko.md)

AI coding agent skills for [W&B](https://wandb.ai) — covering both [Models](https://docs.wandb.ai/models) (ML experiment tracking, artifact versioning, model registry) and [Weave](https://docs.wandb.ai/weave) (LLM tracing, evaluation, scoring, production monitoring).

This repository contains three skills:

| Skill | Product | Purpose |
|-------|---------|---------|
| **[models](skills/models/)** | W&B Models | ML experiment tracking, artifact versioning, model registry, sweeps |
| **[weave](skills/weave/)** | W&B Weave | Generate new Weave code for LLM tracing, evaluation, scoring |
| **[weave-integration](skills/weave-integration/)** | W&B Weave | Integrate Weave into existing applications (analyze → plan → apply) |

## Models Skill

### What This Skill Covers

| Feature | Description |
|---------|-------------|
| **Experiments** | `wandb.init()`, `wandb.log()`, `wandb.config`, `run.summary` |
| **Artifacts** | Dataset/model versioning, metadata, aliases, TTL |
| **Registry** | Model lifecycle with `link_artifact`, alias strategy |
| **Sweeps** | Bayesian/random/grid hyperparameter search |
| **Tables** | Rich data visualization with images, audio, multi-modal |
| **Leaderboard** | Auto-aggregating evaluation results via Tables + Reports |
| **Reports** | Programmatic report creation with `wandb-workspaces` |
| **Public API** | Query runs, artifacts, and metrics programmatically |
| **Integrations** | PyTorch, Lightning, HuggingFace, Keras, FastAI, XGBoost, LightGBM |
| **Troubleshooting** | Common errors and solutions |

### Skill Structure

```
skills/models/
├── SKILL.md                         # Core instructions + quick reference
└── reference/
    ├── experiments.md               # Experiment tracking details
    ├── artifacts.md                 # Artifact management
    ├── registry.md                  # Model Registry operations
    ├── sweeps.md                    # Sweep configuration and execution
    ├── api-patterns.md              # Public API, Tables, Reports
    ├── leaderboard.md               # Leaderboard pattern (Tables + Reports)
    ├── integrations.md              # Framework-specific callbacks
    ├── table-examples.md            # Diverse table examples
    └── troubleshooting.md           # Common errors and solutions
```

## Weave Skill (Code Generation)

### What This Skill Covers

| Feature | Description |
|---------|-------------|
| **Tracing** | `@weave.op()`, `weave.Model`, nested traces, async, sampling rate, kind/color, attributes, threads |
| **Evaluation** | `weave.Evaluation`, model comparison, evaluation pipelines |
| **Scorers** | Custom function/class scorers, LLM-as-judge, built-in scorers (hallucination, moderation, RAGAS, JSON/XML/Pydantic validation) |
| **Datasets** | `weave.Dataset`, versioning with `weave.publish()` / `weave.ref()` |
| **Prompts** | `weave.StringPrompt`, `weave.MessagesPrompt`, parameterized templates, versioning |
| **Monitors & Guardrails** | Production monitoring (LLM-as-judge), guardrails (`call.apply_scorer()`), content moderation, PII detection |
| **Feedback & Annotations** | Reactions, notes, custom feedback, human annotation scorers (`AnnotationSpec`) |
| **Costs** | Custom cost tracking, project-level cost aggregation |
| **Integrations** | OpenAI, Anthropic, LiteLLM, LangChain, LlamaIndex, CrewAI, DSPy, Instructor, PydanticAI, Google ADK, AutoGen, Smolagents, OpenAI Agents SDK, MCP |
| **Troubleshooting** | Common errors and solutions |

### Skill Structure

```
skills/weave/
├── SKILL.md                         # Core instructions + quick reference
└── references/
    ├── tracing.md                   # @weave.op, weave.Model, trace patterns, advanced config
    ├── evaluation.md                # weave.Evaluation, model comparison
    ├── scorers.md                   # Custom + built-in scorers (incl. RAGAS)
    ├── datasets.md                  # weave.Dataset, versioning
    ├── prompts.md                   # StringPrompt, MessagesPrompt, parameterization
    ├── monitors-guardrails.md       # Production monitoring, safety guardrails
    ├── feedback.md                  # Feedback collection, human annotations
    ├── costs.md                     # LLM cost tracking and aggregation
    ├── integrations.md              # Provider & agent framework integrations
    └── troubleshooting.md           # Common errors and solutions
```

## Weave Integration Skill (Existing App Onboarding)

Helps integrate Weave into **existing** applications through a guided 4-phase workflow:

1. **Analyze** — scan the codebase to identify LLM calls, model classes, evaluation logic, prompts
2. **Plan** — present an integration plan showing what to change and where
3. **Apply** — on user approval, automatically modify the code
4. **Validate** — verify all changes with a checklist

### What This Skill Covers

| Feature | Description |
|---------|-------------|
| **Codebase Analysis** | Detect LLM providers, pipeline functions, model classes, eval logic, prompts |
| **Tracing Integration** | Add `weave.init()` and `@weave.op()` to existing functions |
| **Model Conversion** | Convert existing classes to `weave.Model` |
| **Evaluation Integration** | Wire existing tests/benchmarks into `weave.Evaluation` |
| **Prompt Versioning** | Extract hardcoded prompts into `weave.StringPrompt` / `weave.MessagesPrompt` |
| **Framework-Specific** | Recipes for FastAPI, Streamlit, Flask, LangChain, CrewAI, DSPy, OpenAI Agents SDK |

### Skill Structure

```
skills/weave-integration/
├── SKILL.md                         # Core instructions + 4-phase workflow
└── references/
    ├── codebase-analysis.md         # Detection patterns, file classification
    ├── tracing-integration.md       # @weave.op() before/after patterns
    ├── model-conversion.md          # Class → weave.Model conversion
    ├── evaluation-integration.md    # Tests → weave.Evaluation conversion
    ├── prompt-versioning.md         # Prompt extraction patterns
    ├── framework-specific.md        # Per-framework integration recipes
    └── integration-checklist.md     # Pre/post integration validation
```

## Prerequisites

- Python 3.8+
- `pip install wandb` (for Models skill)
- `pip install weave` (for Weave skills)
- `wandb login` or set `WANDB_API_KEY` environment variable

## Installation

Clone the repository:

```bash
git clone https://github.com/hw-wandb/wandb-skills.git
```

Then copy the skills to your agent's skill directory:

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

### Project-level (any agent)

```bash
cp -r wandb-skills/skills/ .claude/skills/
# or
cp -r wandb-skills/skills/ .cursor/skills/
```

## Usage

The skills are automatically detected by AI coding agents. Ask your agent to:

### Models Skill
- "Add wandb tracking to my training script"
- "Set up a hyperparameter sweep"
- "Log predictions as a wandb table"
- "Register my model to wandb registry"
- "Create a leaderboard report for evaluation results"

### Weave Skill (new code)
- "Add Weave tracing to my LLM app"
- "Evaluate my chatbot with custom scorers"
- "Create a hallucination scorer for my RAG pipeline"
- "Version my prompts and evaluation dataset"
- "Set up production monitoring for my LLM"

### Weave Integration Skill (existing apps)
- "Add Weave to my existing app"
- "Integrate Weave into my current project"
- "Instrument my FastAPI app with Weave"

## W&B MCP Server

For features not covered by these skills (e.g., Automations, Launch), you can install the W&B MCP server to query the official documentation directly from your agent.

See [W&B MCP Server Docs](https://docs.wandb.ai/platform/mcp-server) for setup instructions.

## W&B Documentation

### Models
- [W&B Models](https://docs.wandb.ai/models) — Product overview
- [Experiments](https://docs.wandb.ai/models/track) — Experiment tracking
- [Artifacts](https://docs.wandb.ai/models/artifacts) — Data versioning
- [Registry](https://docs.wandb.ai/models/registry) — Model management
- [Sweeps](https://docs.wandb.ai/models/sweeps) — Hyperparameter optimization
- [Tables](https://docs.wandb.ai/models/tables) — Data visualization
- [Reports](https://docs.wandb.ai/models/reports) — Collaborative reports
- [SDK Cheat Sheet](https://docs.wandb.ai/models/ref/sdk-coding-cheat-sheet) — Quick reference

### Weave
- [W&B Weave](https://docs.wandb.ai/weave) — Product overview
- [Tracing](https://docs.wandb.ai/weave/guides/tracking/tracing) — LLM app tracing
- [Evaluation](https://docs.wandb.ai/weave/guides/evaluation/overview) — Evaluation pipelines
- [Scorers](https://docs.wandb.ai/weave/guides/evaluation/scorers) — Custom & built-in scorers
- [Datasets](https://docs.wandb.ai/weave/guides/core-types/datasets) — Dataset management
- [Prompts](https://docs.wandb.ai/weave/guides/core-types/prompts) — Prompt versioning
- [Monitors](https://docs.wandb.ai/weave/guides/evaluation/monitors) — Production monitoring
- [Guardrails](https://docs.wandb.ai/weave/guides/evaluation/guardrails) — Safety guardrails
- [Feedback](https://docs.wandb.ai/weave/guides/tracking/feedback) — Feedback & annotations
- [Costs](https://docs.wandb.ai/weave/guides/tracking/costs) — Cost tracking
- [Integrations](https://docs.wandb.ai/weave/guides/integrations) — Provider & framework integrations

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
