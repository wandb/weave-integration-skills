# Weave Monitors & Guardrails Reference

Monitors and guardrails use scorers to assess production traffic. Monitors **passively observe** trends; guardrails **actively intervene** before outputs reach users.

## Monitors

Monitors use LLM judges to passively score production traffic and surface trends. They require **no code changes** — configure them in the W&B UI.

### Setting Up a Monitor (UI)

1. Open your Weave project in the W&B UI
2. Select **Monitors** from the sidebar, then click **+ New Monitor**
3. Configure the monitor:
   - **Name**: identifier for the monitor
   - **Operations**: select which `@weave.op`s to monitor (must have logged at least one trace first)
   - **Sampling rate**: percentage of calls to score (0–100%)
   - **Scorer name**: identifier for the scorer
   - **Judge model**: LLM model to use for scoring
   - **System prompt**: defines the judge's role
   - **Scoring prompt**: evaluation task (reference op variables with `{output}`, `{ground_truth}`, etc.)
   - **Response format**: `json_object` or `text`

### Monitor Example: Truthfulness

```python
import weave
import random
import openai

weave.init("my-team/my-project")
client = openai.OpenAI()

@weave.op()
def generate_statement(ground_truth: str) -> str:
    if random.random() < 0.5:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f"Generate an incorrect statement based on: {ground_truth}"}
            ]
        )
        return response.choices[0].message.content
    return ground_truth

generate_statement("The Earth revolves around the Sun.")
```

After running, create a monitor in the UI with scoring prompt:

```
Evaluate whether the output statement is accurate based on the input statement.
Input: {ground_truth}
Output: {output}
Respond as JSON: {"is_true": boolean, "reasoning": string}
```

## Guardrails

Guardrails actively intervene in your app's control flow using inline scorers. They run in real time and can block or modify responses. Guardrails **require code changes** but also function as monitors automatically.

### Using `call.apply_scorer()` Pattern

The core pattern: call the op, get the call object, apply a scorer, then decide whether to return the result.

```python
import weave
import openai
import asyncio

weave.init("my-team/my-project")
client = openai.OpenAI()

@weave.op()
def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content
```

### Built-in Moderation Guardrail

Use `OpenAIModerationScorer` to check for harmful content:

```python
from weave.scorers import OpenAIModerationScorer

moderation_scorer = OpenAIModerationScorer()

async def generate_safe_response(prompt: str) -> str:
    result, call = generate_response.call(prompt)
    score = await call.apply_scorer(moderation_scorer)

    if not score.result.get("passed", True):
        categories = score.result.get("categories", {})
        flagged = list(categories.keys()) if categories else []
        print(f"Content blocked. Flagged: {flagged}")
        return "I'm sorry, I can't provide that response due to content policy."

    return result

asyncio.run(generate_safe_response("What's the capital of France?"))
```

### Custom PII Detection Guardrail

```python
import re
from weave import Scorer

class PIIDetectionScorer(Scorer):
    @weave.op()
    def score(self, output: str) -> dict:
        detected = []
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output):
            detected.append("email")
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', output):
            detected.append("phone")
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', output):
            detected.append("ssn")
        return {"passed": len(detected) == 0, "detected_types": detected}

pii_scorer = PIIDetectionScorer()

async def generate_safe_response(prompt: str) -> str:
    result, call = generate_response.call(prompt)
    score = await call.apply_scorer(pii_scorer)

    if not score.result.get("passed", True):
        detected = score.result.get("detected_types", [])
        return f"Response blocked: contains sensitive information ({', '.join(detected)})."

    return result
```

### AWS Bedrock Guardrail

Requires `boto3` and a guardrail configured in AWS Bedrock console:

```python
from weave.scorers.bedrock_guardrails import BedrockGuardrailScorer

guardrail_scorer = BedrockGuardrailScorer(
    guardrail_id="your-guardrail-id",
    guardrail_version="DRAFT",
    source="INPUT",
    bedrock_runtime_kwargs={"region_name": "us-east-1"},
)

async def generate_safe_text(prompt: str) -> str:
    result, call = generate_text.call(prompt)
    score = await call.apply_scorer(guardrail_scorer)

    if not score.result.passed:
        if score.result.metadata.get("modified_output"):
            return score.result.metadata["modified_output"]
        return "Content blocked due to policy restrictions."

    return result
```

## Monitors vs. Guardrails

| Aspect | Monitors | Guardrails |
|--------|----------|------------|
| **Intervention** | Passive (observe only) | Active (block/modify responses) |
| **Code changes** | None (UI-only setup) | Required (`call.apply_scorer()`) |
| **Latency impact** | None (async scoring) | Adds latency (inline scoring) |
| **Use case** | Trend analysis, quality tracking | Content safety, PII filtering |
| **Sampling** | Configurable (0–100%) | Every call (100%) |

## Performance Tips

- Keep guardrail logic simple and fast
- Initialize scorers outside main functions to avoid repeated setup
- Cache common results when possible
- Avoid heavy external API calls in critical paths
