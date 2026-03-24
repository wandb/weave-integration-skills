# Weave Costs Reference

Weave automatically tracks costs for supported LLM providers. You can also add custom costs for unsupported models and query project-level cost data.

## Adding Custom Costs

Use `client.add_cost()` for models not automatically priced:

```python
import weave
from datetime import datetime

client = weave.init("my-team/my-project")

# Basic cost definition (cost per token, not per million)
client.add_cost(
    llm_id="your_model_name",
    prompt_token_cost=0.01,
    completion_token_cost=0.02,
)

# Cost with effective date (for price changes)
client.add_cost(
    llm_id="your_model_name",
    prompt_token_cost=10,
    completion_token_cost=20,
    effective_date=datetime(2025, 4, 22),
)
```

If your LLM prices are specified per million tokens, convert to per-token cost before passing.

## Querying Costs

```python
import weave

client = weave.init("my-team/my-project")

# Query by model name
costs = client.query_costs(llm_ids=["your_model_name"])

# Query by cost ID
cost = client.query_costs(costs[0].id)
```

## Purging Costs

```python
import weave

client = weave.init("my-team/my-project")

costs = client.query_costs(llm_ids=["your_model_name"])
client.purge_costs([cost.id for cost in costs])
```

## Calculating Project-Level Costs

Aggregate costs across all calls in a project:

```python
import weave

weave.init("cost-analysis")

@weave.op()
def get_costs_for_project(project_name: str) -> dict:
    total_cost = 0
    requests = 0

    client = weave.init(project_name)
    calls = list(
        client.get_calls(filter={"trace_roots_only": True}, include_costs=True)
    )

    for call in calls:
        if (
            call.summary.get("weave") is not None
            and call.summary["weave"].get("costs") is not None
        ):
            for k, cost in call.summary["weave"]["costs"].items():
                requests += cost["requests"]
                total_cost += cost["prompt_tokens_total_cost"]
                total_cost += cost["completion_tokens_total_cost"]

    return {
        "total_cost": total_cost,
        "requests": requests,
        "calls": len(calls),
    }

result = get_costs_for_project("my-team/my-project")
print(f"Total cost: ${result['total_cost']:.4f} over {result['requests']} requests")
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No cost data in traces | Ensure the provider is supported or add custom costs via `add_cost()` |
| Cost shows zero | Verify `prompt_token_cost` and `completion_token_cost` are per-token (not per million) |
| `include_costs=True` not working | Must be passed to `client.get_calls()`, not available on individual call objects |
