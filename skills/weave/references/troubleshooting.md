# Troubleshooting

## Authentication & Initialization

### "wandb.errors.AuthenticationError" or "Invalid API key"
**Cause:** `WANDB_API_KEY` not set or invalid.
```bash
export WANDB_API_KEY="your-key"  # get from https://wandb.ai/authorize
```
Or in Python:
```python
import os
os.environ["WANDB_API_KEY"] = "your-key"
```

### "weave.init() not called" — traces not appearing
**Cause:** `weave.init()` must be called before any `@weave.op()` decorated function is invoked.
```python
import weave

weave.init('team/project')  # must come first

@weave.op()
def my_func(x: str) -> str:
    return x.upper()

# now calls are traced
my_func("hello")
```

### Traces going to wrong project
**Cause:** Wrong project string format or `weave.init()` called multiple times.
```python
# Correct format
weave.init('my-team/my-project')

# Common mistake: extra slash or typo
# Wrong: weave.init('my-team//my-project')
# Wrong: weave.init('/my-project')
```

## Tracing

### `@weave.op()` not capturing inputs/outputs
**Cause:** Missing type hints. Weave uses type hints for serialization.
```python
# Wrong — no type hints
@weave.op()
def process(data):
    return result

# Correct — with type hints
@weave.op()
def process(data: str) -> str:
    return result
```

### Nested function calls not showing as child traces
**Cause:** Inner functions not decorated with `@weave.op()`.
```python
@weave.op()
def pipeline(query: str) -> str:
    context = retrieve(query)    # this won't appear in trace tree
    return generate(context)     # this won't either

# Fix: decorate all functions you want in the trace tree
@weave.op()
def retrieve(query: str) -> list[str]:
    ...

@weave.op()
def generate(context: str) -> str:
    ...

@weave.op()
def pipeline(query: str) -> str:
    context = retrieve(query)    # now appears as child span
    return generate(context)     # now appears as child span
```

### Async functions not being traced
**Cause:** Async functions work with `@weave.op()` but must be awaited properly.
```python
@weave.op()
async def async_generate(prompt: str) -> str:
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content

# Must use asyncio to run
import asyncio
result = asyncio.run(async_generate("hello"))
```

### Large objects causing slow traces
**Cause:** Weave serializes all inputs/outputs. Large objects (images, embeddings) slow things down.
```python
# Instead of passing large raw data, pass references or paths
@weave.op()
def process(file_path: str) -> dict:  # pass path, not file content
    data = load_file(file_path)
    return {"result": summarize(data)}
```

## Evaluation

### "TypeError: object dict can't be used in 'await' expression"
**Cause:** Evaluation must be run with `asyncio.run()`.
```python
evaluation = weave.Evaluation(dataset=dataset, scorers=[my_scorer])

# Wrong
results = evaluation.evaluate(model)

# Correct
import asyncio
results = asyncio.run(evaluation.evaluate(model))
```

### Scorer receiving wrong arguments
**Cause:** Scorer parameter names must match. Weave passes `output` (model's return value) and dataset column names.
```python
# If dataset rows have {"question": "...", "expected": "..."}
# and model.predict() returns a string

# Wrong — 'answer' doesn't match any dataset column
@weave.op()
def my_scorer(output: str, answer: str) -> dict:
    return {"correct": output == answer}

# Correct — 'expected' matches the dataset column name
@weave.op()
def my_scorer(output: str, expected: str) -> dict:
    return {"correct": output == expected}
```

### Class-based scorer not working — `column_map` needed
**Cause:** When scorer parameter names differ from dataset column names, use `column_map`.
```python
class RelevanceScorer(weave.Scorer):
    @weave.op()
    def score(self, output: str, context: str) -> dict:
        # 'context' is the scorer's parameter name
        return {"relevant": context in output}

# Dataset has 'retrieved_docs' not 'context'
scorer = RelevanceScorer(column_map={"context": "retrieved_docs"})
```

### Built-in scorer "model_id" error
**Cause:** Built-in scorers (v0.51.35+) use `model_id` with LiteLLM format, not `client`.
```python
from weave.scorers import HallucinationFreeScorer

# Wrong (old API)
# scorer = HallucinationFreeScorer(client=openai_client)

# Correct (current API)
scorer = HallucinationFreeScorer(
    model_id="openai/gpt-4o",  # LiteLLM format
    column_map={"context": "context"}
)
```

### Evaluation results not appearing in W&B UI
**Cause:** `weave.init()` not called, or evaluation ran without internet.
```python
import weave

weave.init('team/project')  # must be called before evaluation

evaluation = weave.Evaluation(dataset=dataset, scorers=[scorer])
results = asyncio.run(evaluation.evaluate(model))
# Results are now visible at https://wandb.ai/<team>/<project>/weave
```

## Model

### "weave.Model predict method not found"
**Cause:** `weave.Model` subclass must implement `predict()` method decorated with `@weave.op()`.
```python
class MyModel(weave.Model):
    system_prompt: str
    temperature: float = 0.7

    # Wrong — missing @weave.op() or wrong method name
    def run(self, input: str) -> str: ...

    # Correct
    @weave.op()
    def predict(self, input: str) -> str:
        ...
```

### Model attributes not being versioned
**Cause:** Attributes must be declared as class-level typed fields (Pydantic-style).
```python
class MyModel(weave.Model):
    # Correct — declared as typed fields, will be versioned
    system_prompt: str
    temperature: float = 0.7
    model_name: str = "gpt-4o"

    @weave.op()
    def predict(self, input: str) -> str:
        ...

# Wrong — setting attributes in __init__ bypasses versioning
class BadModel(weave.Model):
    def __init__(self):
        self.prompt = "something"  # not versioned
```

## Dataset

### "weave.publish() not saving dataset"
**Cause:** Must call `weave.init()` first, and dataset needs a name.
```python
weave.init('team/project')

dataset = weave.Dataset(
    name='my-dataset',  # name is required
    rows=[{"input": "hello", "expected": "world"}]
)
weave.publish(dataset)
```

### Dataset rows format error
**Cause:** Rows must be a list of dicts with consistent keys.
```python
# Wrong — inconsistent keys
rows = [
    {"question": "hi", "answer": "hello"},
    {"q": "bye", "a": "goodbye"},  # different keys!
]

# Correct — all rows have same keys
rows = [
    {"question": "hi", "answer": "hello"},
    {"question": "bye", "answer": "goodbye"},
]
dataset = weave.Dataset(name='qa-data', rows=rows)
```

## Integrations

### OpenAI calls not being auto-traced
**Cause:** `weave.init()` must be called **before** creating the OpenAI client.
```python
import weave
from openai import OpenAI

weave.init('team/project')  # before client creation
client = OpenAI()

# Now all client.chat.completions.create() calls are auto-traced
```

### LiteLLM calls not being traced
**Cause:** Same rule — `weave.init()` before `litellm.completion()`.
```python
import weave
import litellm

weave.init('team/project')

# Auto-traced
response = litellm.completion(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "hello"}]
)
```

### Anthropic client not auto-patching
**Cause:** `weave.init()` must precede `anthropic.Anthropic()` creation.
```python
import weave
import anthropic

weave.init('team/project')  # before client creation
client = anthropic.Anthropic()

# Auto-traced
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "hello"}]
)
```

## Environment

### Disable Weave temporarily
```python
# Set before weave.init()
import os
os.environ["WANDB_MODE"] = "disabled"
```

### Weave slowing down application
```python
# Log fewer traces by not decorating high-frequency utility functions
# Only decorate functions you actually want to observe

# For batch processing, consider sampling
import random
@weave.op()
def traced_process(input: str) -> str:
    ...

def process_batch(items):
    for item in items:
        if random.random() < 0.1:  # trace 10% of calls
            traced_process(item)
        else:
            untraced_process(item)
```
