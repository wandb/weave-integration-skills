# Weave Integration Skill

AI coding agent skill for integrating [W&B Weave](https://docs.wandb.ai/weave) into existing applications — trace-first instrumentation with minimal code changes.

## What It Does

Analyzes an existing codebase, creates a collaborative integration plan, and applies Weave tracing with user approval at every step.

- Scan for all functions, LLM calls, model classes, and frameworks
- Create `weave_instrumentation.md` with checkbox-based trace map
- AI pre-checks recommended targets, user opts out of what they don't need
- Two explicit approval gates before any code is modified

## How It Works

```
Phase 0: Project Setup
  └─ Confirm project name, environment, API key

Phase 1: Codebase Analysis                     → codebase-analysis.md
  └─ Scan for ALL functions, classes, API calls
  └─ Detect frameworks (FastAPI, LangChain, CrewAI, etc.)
  └─ Check if Weave is already partially integrated

Phase 2: Plan File ⏸ APPROVAL GATE 1          → weave-instrumentation-template.md
  └─ Ask: "Create weave_instrumentation.md?"
  └─ List ALL traceable targets with checkboxes
  └─ AI pre-checks [x] recommended, leaves [ ] others
  └─ User reviews and unchecks what they don't want

Phase 3: Review ⏸ APPROVAL GATE 2
  └─ Ask: "Approve this plan for implementation?"
  └─ Do NOT proceed without explicit approval

Phase 4: Apply Changes                         → official docs + transformation-patterns.md
  └─ Add weave.init() at the app entrypoint
  └─ Decorate checked functions with @weave.op()
  └─ Convert checked classes to weave.Model

Phase 5: Validation                            → integration-checklist.md
  └─ Run integration checklist (setup, tracing, models, eval)
  └─ Guide user through test run + Weave UI verification
  └─ Ask if weave_instrumentation.md should be kept or deleted
```

Key principles:
- **Trace first** — list everything, user opts out
- **Two approval gates** — plan creation and implementation are separate approvals
- **No code changes without explicit approval**

## Skill Structure

```
skills/weave-integration/
├── SKILL.md                                # Integration workflow, docs lookup, rules
├── evals/
│   └── evals.json                          # Test cases for skill trigger evaluation
└── references/
    ├── codebase-analysis.md                # Scan guide, evolve vs fresh logic, checkbox criteria
    ├── weave-instrumentation-template.md   # Template for weave_instrumentation.md plan file
    ├── transformation-patterns.md          # Model conversion patterns (class → weave.Model)
    └── integration-checklist.md            # Post-integration validation checklist
```

## Prerequisites

- Python 3.8+
- `pip install weave`
- `wandb login` or set `WANDB_API_KEY` environment variable

## Installation

```bash
# Clone the repo
git clone https://github.com/wandb/weave-integration-skills-hackathon.git
cd weave-integration-skills-hackathon

# Claude Code
cp -r skills/weave-integration/ ~/.claude/skills/weave-integration/

# Cursor
cp -r skills/weave-integration/ ~/.cursor/skills/weave-integration/

# Project-level (any agent)
cp -r skills/ .claude/skills/
```

## Example Prompts

- "Add Weave to my existing app"
- "Instrument my FastAPI app with Weave"
- "Integrate Weave into my LangChain project"
- "Add Weave to my OpenAI Agents SDK project"
- "Retrofit Weave tracing into my production chatbot"

## Documentation

- [W&B Weave](https://docs.wandb.ai/weave) — Product overview
- [Tracing](https://docs.wandb.ai/weave/guides/tracking/tracing) — LLM app tracing
- [Evaluation](https://docs.wandb.ai/weave/guides/core-types/evaluations) — Evaluation pipelines
- [Integrations](https://docs.wandb.ai/weave/guides/integrations/autopatching) — Provider & framework integrations

## License

MIT
