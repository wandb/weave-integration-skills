---
name: weave
description: >
  W&B Weave — generate code, integrate into existing projects, or answer questions.
  Trigger on: weave, weave.init, weave.op, @weave.op, weave.Model, weave.Evaluation,
  weave.Scorer, weave.Dataset, weave.publish, weave.ref, weave.StringPrompt,
  weave.MessagesPrompt, AnnotationSpec, apply_scorer, add_cost, query_costs,
  LLM tracing, evaluation, scorers, datasets, prompts, monitors, guardrails,
  feedback, annotations, cost tracking, PII detection, content moderation,
  LLM observability, "add Weave to my app", "integrate Weave", "track my LLM calls",
  "evaluate my chatbot". Covers all Weave features and integrations
  (OpenAI, Anthropic, LangChain, CrewAI, DSPy, LlamaIndex, etc.).
---

# W&B Weave Copilot

One skill for everything W&B Weave: generating new code, integrating into existing projects, and answering concept/usage questions.

## Step 1: Determine Mode

Classify every user request into exactly one mode:

| Mode | When | Action |
|------|------|--------|
| **Code** | User wants to *write new* Weave code from scratch (tracing, evaluation, scorers, datasets, prompts, monitors, feedback, costs, etc.) | Go to [Code Mode](#code-mode) |
| **Integration** | User wants to *add Weave to existing code* — instrument, retrofit, onboard, or add new Weave features to a project that already uses Weave | Go to [Integration Mode](#integration-mode) |
| **Guide** | User asks a *concept or usage question* about Weave ("what is...", "how does...", "when should I...") without requesting code changes | Go to [Guide Mode](#guide-mode) |

**Ambiguous requests**: If unclear, ask the user: "Are you looking to (A) write new Weave code, (B) add Weave to your existing project, or (C) learn about a Weave concept?"

---

## Step 2: Fetch Official Documentation

Before generating any Weave code or answering technical questions, **always fetch the latest documentation** from the W&B official docs.

### How to Fetch Docs

1. **Find the right URL** — use the Documentation URL Mapping table below
2. **Fetch the page** — `WebFetch("https://docs.wandb.ai/<path>")`
3. **If the topic isn't in the table** — fetch the index at `https://docs.wandb.ai/llms.txt` and search for the relevant URL

### Documentation URL Mapping

All paths are relative to `https://docs.wandb.ai`.

| User is asking about | Documentation URL |
|---------------------|-------------------|
| Getting started, quickstart | `/weave/quickstart` |
| Tracing fundamentals (ops, calls) | `/weave/guides/tracking/tracing` |
| `@weave.op()` settings, color, postprocess | `/weave/guides/tracking/ops` |
| Create/instrument calls | `/weave/guides/tracking/create-call` |
| Get call object at runtime | `/weave/guides/tracking/get-call-object` |
| Call schema reference | `/weave/guides/tracking/call-schema-reference` |
| Query/filter calls | `/weave/guides/tracking/querying-calls` |
| Custom attributes, metadata | `/weave/guides/tools/attributes` |
| Thread/session tracking | `/weave/guides/tracking/threads` |
| Media types (images, audio, video) | `/weave/guides/core-types/media` |
| Trace tree visualization | `/weave/guides/tracking/trace-tree` |
| Generator function tracing | `/weave/guides/tracking/trace-generator-func` |
| Disable/control tracing | `/weave/guides/tracking/trace-disable` |
| Display name customization | `/weave/guides/tracking/set-call-display` |
| `weave.Model` class | `/weave/guides/core-types/models` |
| Object serialization, refs | `/weave/guides/tracking/objects` |
| `weave.Evaluation` pipeline | `/weave/guides/core-types/evaluations` |
| Custom scorers (function/class) | `/weave/guides/evaluation/scorers` |
| Built-in scorers | `/weave/guides/evaluation/builtin_scorers` |
| Local scorers (small LMs) | `/weave/guides/evaluation/weave_local_scorers` |
| Dynamic leaderboards | `/weave/guides/evaluation/dynamic_leaderboards` |
| Evaluation logger | `/weave/guides/evaluation/evaluation_logger` |
| Guardrails (inline scoring) | `/weave/guides/evaluation/guardrails` |
| Monitors (production scoring) | `/weave/guides/evaluation/monitors` |
| `weave.Dataset` | `/weave/guides/core-types/datasets` |
| Prompts (StringPrompt, MessagesPrompt) | `/weave/guides/core-types/prompts` |
| Prompt versioning | `/weave/guides/core-types/prompts-version` |
| Prompt playground | `/weave/guides/tools/playground` |
| Evaluation playground | `/weave/guides/tools/evaluation_playground` |
| Feedback (reactions, notes) | `/weave/guides/tracking/feedback` |
| Annotations, human review | `/weave/guides/tracking/annotation-review` |
| Annotation queues | `/weave/guides/tracking/annotation-queues` |
| Cost tracking | `/weave/guides/tracking/costs` |
| Leaderboards | `/weave/guides/core-types/leaderboards` |
| PII redaction | `/weave/guides/tracking/redact-pii` |
| Column mapping | `/weave/guides/tools/column-mapping` |
| Comparison tools | `/weave/guides/tools/comparison` |
| Saved views | `/weave/guides/tools/saved-views` |
| Environment variables | `/weave/guides/core-types/env-vars` |
| Auto-patching overview | `/weave/guides/integrations/autopatching` |
| OpenAI integration | `/weave/guides/integrations/openai` |
| Anthropic integration | `/weave/guides/integrations/anthropic` |
| LiteLLM integration | `/weave/guides/integrations/litellm` |
| Google GenAI integration | `/weave/guides/integrations/google` |
| Google ADK integration | `/weave/guides/integrations/google_adk` |
| Mistral integration | `/weave/guides/integrations/mistral` |
| Cohere integration | `/weave/guides/integrations/cohere` |
| Groq integration | `/weave/guides/integrations/groq` |
| Cerebras integration | `/weave/guides/integrations/cerebras` |
| Together AI integration | `/weave/guides/integrations/together_ai` |
| AWS Bedrock integration | `/weave/guides/integrations/bedrock` |
| Azure OpenAI integration | `/weave/guides/integrations/azure` |
| LangChain integration | `/weave/guides/integrations/langchain` |
| LlamaIndex integration | `/weave/guides/integrations/llamaindex` |
| CrewAI integration | `/weave/guides/integrations/crewai` |
| DSPy integration | `/weave/guides/integrations/dspy` |
| OpenAI Agents SDK | `/weave/guides/integrations/openai_agents` |
| Instructor integration | `/weave/guides/integrations/instructor` |
| PydanticAI integration | `/weave/guides/integrations/pydantic_ai` |
| AutoGen integration | `/weave/guides/integrations/autogen` |
| Smolagents integration | `/weave/guides/integrations/smolagents` |
| Claude Agent SDK / MCP | `/weave/guides/integrations/claude_agent` |
| MCP integration | `/weave/guides/integrations/mcp` |
| Agno integration | `/weave/guides/integrations/agno` |
| Local models (Ollama, etc.) | `/weave/guides/integrations/local_models` |
| OpenTelemetry | `/weave/guides/tracking/otel` |
| FAQs, troubleshooting | `/weave/details/faqs` |
| Limits, known issues | `/weave/details/limits` |
| Tutorials — evaluation | `/weave/tutorial-eval` |
| Tutorials — RAG | `/weave/tutorial-rag` |
| Tutorials — tracing | `/weave/tutorial-tracing_2` |
| Tutorials — models | `/weave/tutorial-weave_models` |

### Documentation Rules

- **Always fetch before generating code** — do not rely on memorized API patterns
- **If official docs and a reference file conflict** → official docs take priority (latest API)
- **Never guess APIs** — if the docs don't document it, tell the user it may not exist
- **Cache within conversation** — no need to re-fetch the same topic in the same conversation

---

## Code Mode

Generate new W&B Weave code from scratch.

### Code Generation Checklist

Every piece of Weave code you generate must:

1. Include `import weave` and `weave.init('team/project')` with a comment to replace with actual team/project
2. Add type hints on all function parameters and return types
3. Be complete and runnable — not fragments
4. Include brief inline comments explaining what Weave tracks at each point
5. Mention `WANDB_API_KEY` setup in comments or explanations
6. Use the latest API patterns from official docs (fetch first!)
7. Respond in whichever language the user is using (Korean/English)

### Code Workflow

1. **Identify the feature** — what Weave capability does the user need?
2. **Fetch docs** — WebFetch the appropriate URL from the Documentation URL Mapping table
3. **Generate code** — follow the checklist above
4. **Explain** — briefly explain what the code does and how to verify in the Weave UI

### Feature Workflows

| Feature | Key steps |
|---------|-----------|
| Tracing | `weave.init()` → `@weave.op()` on functions → type hints |
| Model versioning | `class X(weave.Model)` → typed attributes → `predict()` with `@weave.op()` |
| Evaluation | `weave.Dataset` → scorer functions with `@weave.op()` → `weave.Evaluation` → `asyncio.run()` |
| Custom scorer | Function: `@weave.op()` returning `dict`. Class: `weave.Scorer` with `score()` method |
| Built-in scorers | Import from `weave.scorers` → pass `model_id` parameter |
| Dataset | `weave.Dataset(name=..., rows=[...])` → `weave.publish()` |
| Prompt versioning | `weave.StringPrompt` / `weave.MessagesPrompt` → `weave.publish()` → `.format()` |
| Monitors | Create scorer → configure in Weave UI for async production scoring |
| Guardrails | `result, call = fn.call(...)` → `await call.apply_scorer(scorer)` → check result |
| Feedback | `call.feedback.add_reaction()` / `.add_note()` / `.add()` |
| Annotations | `weave.AnnotationSpec` → `weave.publish()` → attach to calls |
| Costs | `client.add_cost(llm_id=..., ...)` → `client.query_costs()` |

---

## Integration Mode

Add Weave to an existing codebase — or add new Weave features to a project that already uses Weave.

### Integration Workflow: 5 Phases

Follow these phases strictly. **Never modify user code without presenting a plan first.**

#### Phase 0: Project Setup

Ask the user for the Weave project name:

> `weave.init()` requires a project name in `'team/project'` format.
> What project name would you like to use? (e.g., `my-team/my-llm-app`)

#### Phase 1: Codebase Analysis

Read `references/codebase-analysis.md`, then scan the user's project to identify integration points.

**Important**: Check if the project already uses Weave (`import weave`, `weave.init()`, `@weave.op()`, `weave.Model`).
- If Weave is already present → **Evolve scenario**: identify what's missing and propose additions only
- If no Weave found → **Fresh integration**: full analysis

#### Phase 2: Integration Plan

Present findings as a structured plan. **Wait for user approval before proceeding.**

#### Phase 3: Apply Changes

On approval, read the relevant reference files and apply changes:

| Step | Reference file |
|------|---------------|
| Setup (`weave.init()` placement) | `references/framework-specific.md` |
| Tracing (`@weave.op()`) | `references/tracing-integration.md` |
| Model conversion (`weave.Model`) | `references/model-conversion.md` |
| Evaluation (`weave.Evaluation`) | `references/evaluation-integration.md` |
| Prompt versioning | `references/prompt-versioning.md` |

**Also fetch official docs** (WebFetch) for the specific features being integrated — reference files contain transformation patterns (before/after), while official docs have the latest API details.

#### Phase 4: Validation

Read `references/integration-checklist.md` and verify all changes.

### Reference Files

| File | When to read |
|------|-------------|
| `references/codebase-analysis.md` | Phase 1 — scanning the project |
| `references/tracing-integration.md` | Phase 3 — adding `@weave.op()` decorators |
| `references/model-conversion.md` | Phase 3 — converting classes to `weave.Model` |
| `references/evaluation-integration.md` | Phase 3 — wiring `weave.Evaluation` |
| `references/prompt-versioning.md` | Phase 3 — extracting hardcoded prompts |
| `references/framework-specific.md` | Phase 1 & 3 — framework detection + `weave.init()` placement |
| `references/integration-checklist.md` | Phase 4 — validation |

### Integration Rules

1. **Never modify code without presenting a plan first**
2. **Preserve existing functionality** — Weave only observes, it must not change app behavior
3. **Minimal changes** — only add what's needed
4. **Add type hints** only to functions being decorated with `@weave.op()`
5. **Use `import weave`** — never `from weave import *`
6. **Always mention `WANDB_API_KEY`** setup

---

## Guide Mode

Answer Weave concept/usage questions.

### Guide Workflow

1. **Fetch docs** — WebFetch the appropriate URL from the Documentation URL Mapping table
2. **Explain clearly** — use the fetched docs to give an accurate answer
3. **Include code snippets** if it helps illustrate the concept
4. **Suggest next step** — if the user's question leads naturally to Code or Integration mode, offer to switch

---

## Universal Rules

These apply to all modes:

1. **Official docs first** — always WebFetch from docs.wandb.ai before generating code or answering technical questions
2. **Language matching** — respond in the user's language (Korean or English)
3. **Latest APIs only** — use patterns from official docs, not memorized patterns that may be outdated
4. **No API guessing** — if a feature isn't in the docs, say so rather than fabricating an API
5. **Reference file role** — integration reference files contain before/after transformation patterns. If they conflict with official docs on specific API details, official docs win.
