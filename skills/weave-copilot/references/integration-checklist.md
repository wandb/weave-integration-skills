# Integration Checklist

Pre-flight and post-integration validation checks.

## Pre-Integration Checklist

Before making any code changes:

- [ ] **Commit existing code** — ensure all current changes are committed so integration changes can be reviewed or reverted
- [ ] **Install Weave** — `pip install weave` (add extras as needed: `pip install weave[openai,anthropic]`)
- [ ] **Set API key** — `export WANDB_API_KEY=<your-key>` (get from https://wandb.ai/authorize)
- [ ] **Choose project name** — format: `team-name/project-name`

## Post-Integration Checklist

After applying all changes, verify:

### Setup
- [ ] `import weave` is present in all modified files
- [ ] `weave.init('team/project')` is called once at the app entrypoint
- [ ] `weave.init()` is called **before** any LLM calls or `@weave.op()` function invocations

### Tracing
- [ ] All LLM-calling functions have `@weave.op()` decorator
- [ ] `@weave.op()` is placed **above** other decorators (e.g., `@retry`, `@cache`)
- [ ] Type hints are present on parameters and return types of decorated functions
- [ ] Async functions work correctly with `@weave.op()` (no behavioral change)

### Model Conversion (if applicable)
- [ ] `weave.Model` subclass has type annotations on all attributes
- [ ] Attribute named `model` has been renamed (e.g., `model_name`) to avoid Pydantic conflict
- [ ] Main method is named `predict` (or `invoke`) with `@weave.op()`
- [ ] Non-serializable objects (API clients, DB connections) are in `model_post_init`, not as class attributes
- [ ] All call sites updated to use new method name (`predict` instead of `generate`, etc.)

### Evaluation (if applicable)
- [ ] Test data extracted into `weave.Dataset`
- [ ] Scoring functions decorated with `@weave.op()` and return `dict`
- [ ] `weave.Evaluation` correctly references dataset and scorers
- [ ] Scorer parameter names match dataset column names (or `column_map` is used)

### Prompt Versioning (if applicable)
- [ ] Extracted prompts use `weave.StringPrompt` or `weave.MessagesPrompt`
- [ ] Prompts are published with `weave.publish(prompt, name="...")`
- [ ] Format calls pass correct variable names

### Evolve Scenario (adding features to existing Weave project)
- [ ] No duplicate `weave.init()` calls introduced
- [ ] New `@weave.op()` decorators are consistent with existing tracing style
- [ ] New `weave.Model` classes don't conflict with existing ones
- [ ] Existing traces and evaluations are not broken by new changes
- [ ] If adding evaluation to an existing `weave.Model`, the `predict` method signature matches dataset columns

### No Regressions
- [ ] Application runs without errors
- [ ] Existing tests still pass
- [ ] No circular imports introduced
- [ ] No behavioral changes — Weave only observes, doesn't modify app logic

## Verification Steps

1. **Run the app** and trigger a few LLM calls
2. **Check the Weave UI** at `https://wandb.ai/<team>/<project>/weave`
3. **Verify traces appear** with correct inputs, outputs, and latency
4. **Check the trace tree** — nested `@weave.op()` calls should form parent-child relationships
5. **Verify auto-patching** — LLM provider calls (OpenAI, Anthropic, etc.) should appear as child spans

## Common Post-Integration Issues

| Issue | Solution |
|-------|----------|
| No traces appearing | Check `WANDB_API_KEY` is set. Check `weave.init()` is called before traced functions. |
| `ModuleNotFoundError: weave` | Run `pip install weave` (with extras if needed) |
| `ValidationError` on `weave.Model` | Add type annotations to all class attributes |
| `model` attribute error | Rename `model` → `model_name` (Pydantic reserved name) |
| Missing child spans | Parent function also needs `@weave.op()` |
| Import errors / circular imports | Move `import weave` to top of file; ensure no circular dependencies |
| `TypeError: predict() missing argument` | Dataset column names must match `predict` parameter names |
| Async errors | Ensure `@weave.op()` is above `async def`, use `asyncio.run()` for evaluation |
| Duplicate `weave.init()` (Evolve) | Remove the new one — keep the existing `weave.init()` call |
| Traces in wrong project (Evolve) | Verify the existing `weave.init()` uses the correct project name |
