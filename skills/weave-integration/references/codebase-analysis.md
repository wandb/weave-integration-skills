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

### Step 1: Discover all source files

Glob for all Python files in the project (e.g., `**/*.py`). Do not limit scanning to the entrypoint or main module — every file may contain traceable targets.

### Step 2: Extract all functions and classes from every file

For each `.py` file found, list every:
- Top-level function (`def`)
- Class and its public methods
- Nested/inner functions if they perform meaningful work

Do not skip files that look like "helpers" or "utils" — list their contents too.

### Step 3: Identify API calls and framework integrations

Search across all files for:
- LLM API calls (`client.chat.completions.create`, `anthropic`, `litellm`, etc.)
- Agent/tool definitions (`@tool`, `function_tool`, tool registrations)
- Framework integrations (LangChain chains, LlamaIndex query engines, CrewAI agents, etc.)
- External API calls (REST, gRPC, database queries)
- Callback/hook functions (event handlers, middleware, pre/post-processing)

### Step 3.5: Identify auto-patched scope and thin wrappers

When a framework is auto-patched by `weave.init()` (e.g., OpenAI Agents SDK, LangChain, LlamaIndex), determine what is **already traced automatically** and mark wrapper functions accordingly.

1. **List auto-patched calls**: Identify which calls the integration traces automatically (e.g., `Runner.run()`, `client.chat.completions.create()`).
2. **Identify thin wrappers**: Functions whose only LLM-related work is calling an auto-patched API. These do NOT need `@weave.op()` because the inner call is already traced. Example: a method that just calls `Runner.run(agent, input)` and returns the result.
3. **Check input serializability**: `@weave.op()` serializes all input arguments. Functions that receive non-serializable or complex SDK objects (e.g., `RunResult`, `RunResultStreaming`, framework-internal types) as parameters will cause runtime errors during Weave's input redaction. Mark these as **not safe for `@weave.op()`**.

**Decision rule for wrapper functions:**
- If a function **only** delegates to an auto-patched call → `[ ]` (already traced)
- If a function adds meaningful logic around an auto-patched call (aggregation, retry, branching) AND all its inputs are serializable → `[x]`
- If a function takes non-serializable SDK objects as input → `[ ]` with note: "non-serializable input"

### Step 4: Common blind spots checklist

Before finalizing the scan, explicitly check for these commonly missed targets:

| Category | What to look for |
|----------|-----------------|
| Agent definitions | Classes or functions that define agent behavior, system prompts, tool lists |
| Tool/function definitions | Functions registered as tools for agents (often in separate files) |
| Callbacks & hooks | Event handlers, on_complete/on_error handlers, middleware functions |
| Data loaders & parsers | Functions that fetch/parse external data before LLM calls |
| Post-processing | Functions that transform LLM output (parsing, validation, formatting) |
| Sub-modules & packages | Files in subdirectories (`agents/`, `tools/`, `prompts/`, `chains/`, etc.) |
| Config/factory functions | Functions that construct agents, chains, or clients dynamically |

If any category has no matches, that is fine — but confirm it was checked, not skipped.

### Step 5: Assign checkbox defaults

For each target, decide the default checkbox state in `weave_instrumentation.md`:

#### Recommend checked `[x]`
- Functions that call LLM APIs directly (e.g., `client.chat.completions.create(...)`)
- Pipeline/orchestration functions that combine multiple steps (e.g., retrieve → generate → format)
- Class methods that are the main inference entry point (e.g., `predict()`, `run()`, `invoke()`)
- Tool functions used by agents
- Agent definition/factory functions
- Callback or hook functions that process LLM inputs/outputs
- Data loading functions that feed into LLM calls

#### Recommend unchecked `[ ]` (but still listed)
- Pure utility functions (string formatting, data conversion, validation)
- Functions called at very high frequency (consider `tracing_sample_rate` if traced)
- Simple getters/setters with no LLM interaction
- Config/constant definitions
- Thin wrappers around auto-patched calls (already traced by framework integration)
- Functions with non-serializable input parameters (SDK objects like `RunResult`, stream handles, client connections) — `@weave.op()` will fail at runtime during input serialization

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
