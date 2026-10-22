# Integration Checklist

Post-integration validation checks. Run this after Phase 4 (Apply Changes).

## Agent Lens (when selected)

- [ ] The integration is listed in the public Agent Lens chooser, or its compatibility was separately verified.
- [ ] The package and initialization match that integration's current guide.
- [ ] Related turns reuse one conversation/session/group ID.
- [ ] A real run produces a grouped conversation with model and tool spans in Agent Lens.
- [ ] Any screenshots come from that integration and state the tested version.
- [ ] Runtime links encode identifiers and do not contain UTMs.
- [ ] Existing Calls and evaluation behavior remains covered where the application uses it.

The following setup and decorator checks apply to Weave Calls and evaluations.

## Setup

- [ ] `import weave` is present in all modified files
- [ ] `weave.init()` is called once at the app entrypoint
- [ ] `weave.init()` is called **before** any LLM calls or `@weave.op()` function invocations
- [ ] No duplicate `weave.init()` calls (especially in Evolve scenarios)

## Tracing

- [ ] All checked functions in `weave_instrumentation.md` have `@weave.op()` decorator
- [ ] `@weave.op()` is placed **above** other decorators (e.g., `@retry`, `@cache`)
- [ ] Type hints are present on parameters and return types of decorated functions
- [ ] Async functions work correctly with `@weave.op()` (no behavioral change)

## Model Conversion (if applicable)

- [ ] `weave.Model` subclass has type annotations on all attributes
- [ ] Attribute named `model` has been renamed (e.g., `model_name`) to avoid Pydantic conflict
- [ ] Main method is named `predict` (or `invoke`) with `@weave.op()`
- [ ] Non-serializable objects (API clients, DB connections) are in `model_post_init` or created inside methods
- [ ] All call sites updated to use new method name

## Evaluation (if applicable)

- [ ] Test data extracted into `weave.Dataset`
- [ ] Scoring functions decorated with `@weave.op()` and return `dict`
- [ ] `weave.Evaluation` correctly references dataset and scorers
- [ ] Scorer parameter names match dataset column names (or `column_map` is used)

## No Regressions

- [ ] Application runs without errors
- [ ] Existing tests still pass
- [ ] No circular imports introduced
- [ ] No behavioral changes — Weave only observes, doesn't modify app logic

## Common Issues

| Issue | Solution |
|-------|----------|
| No traces appearing | Check `WANDB_API_KEY` is set. Check `weave.init()` is called before traced functions. |
| `ModuleNotFoundError: weave` | Install weave with the project's package manager |
| `ValidationError` on `weave.Model` | Add type annotations to all class attributes |
| `model` attribute error | Rename `model` → `model_name` (Pydantic reserved name) |
| Missing child spans | Parent function also needs `@weave.op()` |
| Import errors / circular imports | Move `import weave` to top of file; ensure no circular dependencies |
| `TypeError: predict() missing argument` | Dataset column names must match `predict` parameter names |
| Async errors | Ensure `@weave.op()` is above `async def`, use `asyncio.run()` for evaluation |
| Duplicate `weave.init()` (Evolve) | Remove the new one — keep the existing `weave.init()` call |
| Traces in wrong project (Evolve) | Verify the existing `weave.init()` uses the correct project name |
