# Evaluation Integration Reference

How to convert existing test/eval logic into `weave.Evaluation` for systematic, tracked evaluation.

## When to Convert

Convert existing evaluation code when it:
- Has test cases with expected outputs (input-output pairs)
- Computes scores or metrics on LLM outputs
- Runs in a loop comparing outputs against expected values
- Uses assertions to check LLM output quality

## Conversion Pattern Overview

```
Existing test data       →  weave.Dataset
Existing scoring logic   →  Scorer function with @weave.op()
Existing eval loop       →  weave.Evaluation.evaluate()
```

## Step 1: Extract Test Data → `weave.Dataset`

### From hardcoded test cases

```python
# BEFORE
test_cases = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Capital of France?", "expected": "Paris"},
]

for case in test_cases:
    output = model(case["input"])
    assert case["expected"].lower() in output.lower()
```

```python
# AFTER
import weave

dataset = weave.Dataset(
    name="qa-test-cases",
    rows=[
        {"question": "What is 2+2?", "expected": "4"},
        {"question": "Capital of France?", "expected": "Paris"},
    ]
)
weave.publish(dataset)  # Version the dataset
```

### From JSON/CSV file

```python
# BEFORE
import json
with open("test_data.json") as f:
    test_cases = json.load(f)

# AFTER
import json
import weave

with open("test_data.json") as f:
    rows = json.load(f)

dataset = weave.Dataset(name="eval-dataset", rows=rows)
weave.publish(dataset)
```

### From pandas DataFrame

```python
# BEFORE
import pandas as pd
df = pd.read_csv("eval_data.csv")

# AFTER
import pandas as pd
import weave

df = pd.read_csv("eval_data.csv")
dataset = weave.Dataset(
    name="eval-dataset",
    rows=df.to_dict(orient="records")
)
```

## Step 2: Convert Scoring Logic → Scorer

### From assertion-based checks

```python
# BEFORE
def test_qa_accuracy():
    correct = 0
    for case in test_cases:
        output = model(case["input"])
        if case["expected"].lower() in output.lower():
            correct += 1
    accuracy = correct / len(test_cases)
    assert accuracy > 0.8
```

```python
# AFTER — extract the comparison logic into a scorer
@weave.op()
def contains_expected(output: str, expected: str) -> dict:
    return {"contains_match": expected.lower() in output.lower()}
```

### From custom scoring functions

```python
# BEFORE
def score_response(output, expected):
    exact = output.strip() == expected.strip()
    contains = expected.lower() in output.lower()
    length_ok = len(output) < 500
    return {"exact": exact, "contains": contains, "length_ok": length_ok}
```

```python
# AFTER — add @weave.op() and ensure correct parameter names
@weave.op()
def score_response(output: str, expected: str) -> dict:
    exact = output.strip() == expected.strip()
    contains = expected.lower() in output.lower()
    length_ok = len(output) < 500
    return {"exact": exact, "contains": contains, "length_ok": length_ok}
```

### From class-based scorers

```python
# BEFORE
class RelevanceScorer:
    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def score(self, output, reference):
        similarity = compute_similarity(output, reference)
        return similarity > self.threshold
```

```python
# AFTER
class RelevanceScorer(weave.Scorer):
    threshold: float = 0.7

    @weave.op()
    def score(self, output: str, reference: str) -> dict:
        similarity = compute_similarity(output, reference)
        return {
            "similarity": similarity,
            "relevant": similarity > self.threshold
        }
```

**Scorer parameter mapping**: The `output` parameter receives the model's return value. Other parameter names must match dataset column names. Use `column_map` if names differ:

```python
evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[RelevanceScorer(column_map={"reference": "expected"})],
)
```

## Step 3: Convert Eval Loop → `weave.Evaluation`

### From manual loop

```python
# BEFORE
results = []
for case in test_cases:
    output = model.generate(case["input"])
    score = score_response(output, case["expected"])
    results.append(score)

avg_accuracy = sum(r["exact"] for r in results) / len(results)
print(f"Accuracy: {avg_accuracy}")
```

```python
# AFTER
import asyncio
import weave

weave.init('team/project')

dataset = weave.Dataset(name="eval-set", rows=test_cases)

evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[score_response],
)

# If model is a weave.Model:
asyncio.run(evaluation.evaluate(model))

# If model is a function:
@weave.op()
def model_fn(input: str) -> str:
    return model.generate(input)

asyncio.run(evaluation.evaluate(model_fn))
```

### From pytest tests

```python
# BEFORE
import pytest

@pytest.mark.parametrize("question,expected", [
    ("What is 2+2?", "4"),
    ("Capital of France?", "Paris"),
])
def test_qa(question, expected):
    output = model.answer(question)
    assert expected.lower() in output.lower()
```

```python
# AFTER — keep pytest tests AND add Weave evaluation
import asyncio
import weave

# Pytest tests can remain for CI
# Add a Weave evaluation for tracked comparison

weave.init('team/project')

dataset = weave.Dataset(
    name="qa-test-cases",
    rows=[
        {"question": "What is 2+2?", "expected": "4"},
        {"question": "Capital of France?", "expected": "Paris"},
    ]
)

@weave.op()
def contains_match(output: str, expected: str) -> dict:
    return {"match": expected.lower() in output.lower()}

evaluation = weave.Evaluation(dataset=dataset, scorers=[contains_match])
asyncio.run(evaluation.evaluate(model))
```

## Complete Before/After Example

```python
# BEFORE — eval_benchmark.py
from openai import OpenAI
import json

client = OpenAI()

def run_eval():
    with open("test_data.json") as f:
        cases = json.load(f)

    correct = 0
    total = len(cases)

    for case in cases:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": case["question"]}],
        )
        output = response.choices[0].message.content

        if case["answer"].lower() in output.lower():
            correct += 1

    print(f"Accuracy: {correct}/{total} = {correct/total:.2%}")

if __name__ == "__main__":
    run_eval()
```

```python
# AFTER — eval_benchmark.py
import json
import asyncio
import weave
from openai import OpenAI

class QAModel(weave.Model):
    model_name: str = "gpt-4o"

    @weave.op()
    def predict(self, question: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content

@weave.op()
def accuracy_scorer(output: str, answer: str) -> dict:
    return {"correct": answer.lower() in output.lower()}

def run_eval():
    weave.init('team/project')

    with open("test_data.json") as f:
        cases = json.load(f)

    dataset = weave.Dataset(name="qa-benchmark", rows=cases)

    evaluation = weave.Evaluation(
        dataset=dataset,
        scorers=[accuracy_scorer],
        evaluation_name="QA Benchmark"
    )

    model = QAModel()
    asyncio.run(evaluation.evaluate(model))

if __name__ == "__main__":
    run_eval()
```

## Key Points

- `evaluation.evaluate()` is async — use `asyncio.run()` in scripts
- The model's `predict` method receives dataset columns by name (one row at a time)
- Scorer functions receive `output` (from predict) plus dataset columns by name
- Existing pytest tests can coexist with Weave evaluations
- Results are viewable and comparable in the Weave UI
