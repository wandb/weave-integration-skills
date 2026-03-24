# Weave Evaluation Reference

Evaluations help you systematically test your LLM application against a set of examples after making changes. Weave tracks evaluation results, enabling comparison across iterations.

## Core Concept

An evaluation combines three things:
1. **Dataset** — examples to test against (`weave.Dataset` or list of dicts)
2. **Model/Function** — what you're evaluating (`weave.Model` or `@weave.op()` function)
3. **Scorers** — functions that grade model outputs (see `references/scorers.md`)

## Setting Up an Evaluation

### Step 1: Define your model

Either a `weave.Model` subclass or a plain `@weave.op()` function:

```python
import weave
from openai import OpenAI

class MyModel(weave.Model):
    model_name: str = "gpt-4o"
    prompt_template: str = "Answer concisely: {question}"

    @weave.op()
    async def predict(self, question: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": self.prompt_template.format(question=question)}],
        )
        return response.choices[0].message.content
```

Or a simple function:

```python
@weave.op()
def my_model(question: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content
```

### Step 2: Prepare your dataset

```python
dataset = [
    {"question": "What is the capital of France?", "expected": "Paris"},
    {"question": "What is 2+2?", "expected": "4"},
    {"question": "Who wrote Romeo and Juliet?", "expected": "Shakespeare"},
]

# Or use weave.Dataset for versioning
dataset = weave.Dataset(
    name="qa-eval-set",
    rows=[
        {"question": "What is the capital of France?", "expected": "Paris"},
        {"question": "What is 2+2?", "expected": "4"},
    ]
)
```

### Step 3: Define scorers

```python
@weave.op()
def exact_match(expected: str, output: str) -> dict:
    return {"match": expected.strip().lower() == output.strip().lower()}
```

### Step 4: Run the evaluation

```python
import asyncio

weave.init('my-team/my-project')

evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[exact_match],
)

# With a weave.Model
model = MyModel()
asyncio.run(evaluation.evaluate(model))

# Or with a plain function
asyncio.run(evaluation.evaluate(my_model))
```

## Naming Evaluations

### Name the Evaluation object (the blueprint):
```python
evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[exact_match],
    evaluation_name="QA Accuracy Test"
)
```

### Name a specific run:
```python
evaluation.evaluate(model, __weave={"display_name": "GPT-4o v2 Run"})
```

## Comparing Model Versions

Run the same evaluation against multiple model configurations:

```python
import asyncio
import weave
from openai import OpenAI

weave.init('my-team/my-project')

class QAModel(weave.Model):
    model_name: str
    temperature: float = 0.0

    @weave.op()
    async def predict(self, question: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content

dataset = [
    {"question": "What is the capital of France?", "expected": "Paris"},
    {"question": "What is 2+2?", "expected": "4"},
]

@weave.op()
def exact_match(expected: str, output: str) -> dict:
    return {"match": expected.strip().lower() in output.strip().lower()}

evaluation = weave.Evaluation(dataset=dataset, scorers=[exact_match])

# Compare different models
models = [
    QAModel(model_name="gpt-4o"),
    QAModel(model_name="gpt-4o-mini"),
    QAModel(model_name="gpt-4o", temperature=0.7),
]

for model in models:
    asyncio.run(evaluation.evaluate(model))
# View and compare results in the Weave UI
```

## Complete End-to-End Example

```python
import json
import asyncio
import weave
from openai import OpenAI

# 1. Define Model
class FruitExtractor(weave.Model):
    model_name: str = "gpt-4o"
    prompt_template: str = 'Extract ("fruit", "color", "flavor") as JSON from: {sentence}'

    @weave.op()
    async def predict(self, sentence: str) -> dict:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": self.prompt_template.format(sentence=sentence)}
            ],
        )
        result = response.choices[0].message.content
        return json.loads(result) if result else {}

# 2. Create Dataset
dataset = weave.Dataset(
    name="fruit-extraction",
    rows=[
        {
            "sentence": "Neoskizzles are purple and taste like candy.",
            "expected": {"fruit": "neoskizzles", "color": "purple", "flavor": "candy"},
        },
        {
            "sentence": "Pounits are bright green and savory.",
            "expected": {"fruit": "pounits", "color": "bright green", "flavor": "savory"},
        },
    ],
)

# 3. Define Scorer
@weave.op()
def fruit_name_scorer(expected: dict, output: dict) -> dict:
    return {"correct": expected.get("fruit", "").lower() == output.get("fruit", "").lower()}

# 4. Run Evaluation
weave.init('my-team/fruit-eval')
weave.publish(dataset)  # Version the dataset

model = FruitExtractor()
evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[fruit_name_scorer],
    evaluation_name="Fruit Extraction Eval"
)

asyncio.run(evaluation.evaluate(model))
```

## Key Points

- `evaluation.evaluate()` is async — use `asyncio.run()` in scripts or `await` in async contexts
- The `predict` method in `weave.Model` (or the evaluated function) receives one dataset row at a time
- Scorer functions receive `output` (from predict) plus any dataset columns by name
- Evaluation results are viewable in the Weave UI with aggregated scores and per-row detail
- Each call to `.evaluate()` creates a new evaluation run; the `Evaluation` object is the reusable blueprint
