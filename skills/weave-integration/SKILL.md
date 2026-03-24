---
name: weave-integration
description: Comprehensive skill for adding W&B Weave to existing applications. Covers trace-first instrumentation, evaluation only after trace verification, documentation-first implementation, CLI-based Weave data access, and validation workflows. Activate this skill only when the user explicitly mentions the skill by name, such as `weave-integration`, `@skills weave-integration`, or another direct skill reference. Do not auto-trigger from generic Weave or W&B questions.
---
<!--
Package: weave-integration
Repository: wandb/weave-integration-skills-hackathon
Scope: W&B Weave integration for existing applications
-->

# W&B Weave Integration Skill

Use this skill to integrate W&B Weave into an existing codebase with minimal behavioral change.

## Activation

- Run this skill only when it is explicitly mentioned by name.
- Default invocation: `@skills weave-integration`

## Weave Documentation

Use the Weave docs before making implementation decisions.

### 1. Find the Right Page

Start with the root documentation index:

```bash
curl -s https://docs.wandb.ai/llms.txt
```

Important quirk: `llms.txt` covers all W&B docs, not only Weave. Filter for `/weave/`, `https://docs.wandb.ai/weave`, or titles containing `W&B Weave`.

If you prefer browsing first, start from:

```text
https://docs.wandb.ai/weave
```

### 2. Fetch Specific Pages as Markdown

Once you know the right page, fetch it as markdown. This is usually the clearest way to read the docs because it returns clean text, code examples, and configuration details.

Examples:

```bash
curl -s https://docs.wandb.ai/weave/quickstart.md
curl -s https://docs.wandb.ai/weave/guides/tracking/querying-calls.md
curl -s https://docs.wandb.ai/weave/reference/service-api.md
```

Use these pages intentionally:

- `quickstart.md` for current setup patterns
- `guides/tracking/querying-calls.md` for trace inspection and query patterns
- `reference/service-api.md` when the task involves programmatic or CLI-driven access to Weave data

### 3. Search Documentation

There is no documented W&B docs search API to rely on with `curl`.

Use this order:

1. Search `llms.txt` locally with `rg` or `grep`
2. Fetch the matched Weave page as `.md`
3. If that is not enough, use native web search with `site:docs.wandb.ai/weave`

For ambiguous topics, search both guide pages and API reference pages before concluding.

---

## Integration Workflow

Default to tracing **everything** (all functions, tools, API calls), then let the user opt out. Do not pre-filter or skip functions based on priority. The user decides what to exclude.

Follow these 6 phases strictly. **Never modify user code without presenting a plan first.** There are two explicit approval gates — do not skip them.

### Phase 0: Project Setup

Confirm the environment:

1. **Weave project name** — ask for `'team/project'` format
2. **Environment detection** — check for `pyproject.toml`, `uv.lock`, `poetry.lock`, `Pipfile`, `requirements.txt` to determine the correct install command
3. **API key** — confirm `WANDB_API_KEY` is set

If the environment is clear, suggest the correct Weave install command and ask whether it is okay to add Weave there.
If the environment is unclear, say exactly: `I could not determine the environment setup method.` Then instruct the user to install Weave first before continuing.

### Phase 1: Codebase Analysis

Read `references/codebase-analysis.md` and follow its steps to scan the project. List **all** traceable functions, classes, and API calls found.

### Phase 2: Plan File (Approval Gate 1)

Ask the user explicitly:

> **Do you want me to create `weave_instrumentation.md` before I edit any code?**

Do not treat a generic implementation request as approval.

**If approved**: Create `weave_instrumentation.md` from `references/weave-instrumentation-template.md`.
- Fill in environment, entry point, detected providers/frameworks
- List **all** traceable targets with checkboxes
- **AI pre-checks recommended targets** (`- [x]`), leaves others unchecked (`- [ ]`)
- Include trace tree showing nesting relationships
- Add optional sections (weave.Model candidates, prompts, evaluation, PII)

**If declined**: Present the same plan inline in chat.

### Phase 3: Review (Approval Gate 2)

Ask the user to review the plan (file or inline), then ask explicitly:

> **Do you approve this plan for implementation?**

Do not treat approval to create `weave_instrumentation.md` as approval to implement code changes. Wait for explicit approval.

### Phase 4: Apply Changes

On approval:

1. **Fetch official docs** using the [Weave Documentation](#weave-documentation) workflow for `weave.init()` placement, tracing, and any features being integrated
2. **Read `references/transformation-patterns.md`** for model conversion patterns (class → `weave.Model`)
3. Apply only the checked items from the plan

### Phase 5: Validation

Read `references/integration-checklist.md` and verify all changes.

Guide the user through a real test run:
1. Confirm environment variables are set
2. Ask the user to run the app
3. Confirm traces appear in Weave UI
4. Show the Weave URL  (`https://<WANDB_BASE_URL>/<team>/<project>/weave` or `https://weave.wandb.ai/<team>/<project>/weave`) and ask the user to explore the traces
5. Ask if `weave_instrumentation.md` should be kept or deleted

### Reference Files

| File | When to read |
|------|-------------|
| `references/codebase-analysis.md` | Phase 1 — scan guide, evolve vs fresh logic, checkbox criteria |
| `references/weave-instrumentation-template.md` | Phase 2 — template for the plan file |
| `references/transformation-patterns.md` | Phase 4 — model conversion patterns (class → `weave.Model`) |
| `references/integration-checklist.md` | Phase 5 — post-integration validation checklist |

---

## Rules

1. **Official docs first** — always fetch from docs.wandb.ai before generating code. Never guess APIs — if it's not in the docs, say so. If reference files conflict with docs, docs win.
2. **Two approval gates** — gate 1: create plan, gate 2: implement changes
3. **Trace first** — list all targets, AI recommends, user opts out
4. **Preserve existing functionality** — Weave only observes, it must not change app behavior
