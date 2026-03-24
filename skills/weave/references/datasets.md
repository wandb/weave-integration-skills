# Weave Datasets Reference

`weave.Dataset` provides versioned, trackable datasets for evaluations. Every time you publish a dataset, Weave creates a new version automatically.

## Creating a Dataset

```python
import weave

dataset = weave.Dataset(
    name="my-eval-dataset",
    rows=[
        {"question": "What is ML?", "expected": "Machine Learning"},
        {"question": "What is NLP?", "expected": "Natural Language Processing"},
        {"question": "What is RAG?", "expected": "Retrieval-Augmented Generation"},
    ]
)
```

Rows are list of dictionaries. Each dictionary is one example. Keys become column names.

## Publishing and Versioning

```python
weave.init('my-team/my-project')

# Publish creates or updates a versioned dataset
ref = weave.publish(dataset)
print(ref.uri())  # weave:///team/project/object/my-eval-dataset:<digest>
```

Every `weave.publish()` call creates a new version if the data has changed. Versions are content-addressed (based on a digest of the data).

## Retrieving a Dataset

```python
# By name (latest version)
dataset = weave.ref('my-eval-dataset').get()

# By full URI (specific version)
dataset = weave.ref('weave:///team/project/object/my-eval-dataset:<digest>').get()

# Access rows
for row in dataset.rows:
    print(row['question'], row['expected'])

# Access specific row
example = dataset.rows[0]
print(example['question'])
```

## Using Datasets in Evaluations

Datasets plug directly into `weave.Evaluation`:

```python
import asyncio
import weave

weave.init('my-team/my-project')

# Create and publish
dataset = weave.Dataset(
    name="qa-golden-set",
    rows=[
        {"question": "Capital of France?", "expected": "Paris"},
        {"question": "Capital of Japan?", "expected": "Tokyo"},
    ]
)
weave.publish(dataset)

# Use in evaluation
@weave.op()
def my_model(question: str) -> str:
    return "Some answer"

@weave.op()
def match(expected: str, output: str) -> dict:
    return {"correct": expected.lower() in output.lower()}

evaluation = weave.Evaluation(dataset=dataset, scorers=[match])
asyncio.run(evaluation.evaluate(my_model))
```

You can also pass a plain list of dicts instead of `weave.Dataset`, but using `weave.Dataset` gives you versioning and reproducibility.

## Building Datasets from Various Sources

### From CSV/JSON files

```python
import json
import weave

# From JSON
with open("eval_data.json") as f:
    rows = json.load(f)
dataset = weave.Dataset(name="from-json", rows=rows)

# From CSV
import csv
with open("eval_data.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
dataset = weave.Dataset(name="from-csv", rows=rows)

weave.init('my-team/my-project')
weave.publish(dataset)
```

### From Pandas DataFrame

```python
import pandas as pd
import weave

df = pd.read_csv("data.csv")
rows = df.to_dict(orient="records")
dataset = weave.Dataset(name="from-pandas", rows=rows)
```

### From HuggingFace Datasets

```python
from datasets import load_dataset
import weave

hf_dataset = load_dataset("squad", split="validation[:100]")
rows = [
    {
        "question": item["question"],
        "context": item["context"],
        "expected": item["answers"]["text"][0],
    }
    for item in hf_dataset
]
dataset = weave.Dataset(name="squad-subset", rows=rows)

weave.init('my-team/my-project')
weave.publish(dataset)
```

## Dataset Design Best Practices

1. **Include clear input/output pairs** — at minimum, have an input field and an expected output field
2. **Use descriptive column names** — `question`, `expected`, `context` are clearer than `input`, `label`
3. **Match column names to scorer parameters** — or use `column_map` in scorers
4. **Start small** — 20-50 high-quality examples beat 1000 noisy ones
5. **Cover edge cases** — include adversarial, ambiguous, and boundary examples
6. **Version incrementally** — publish new versions as you add examples, enabling regression tracking
7. **Keep datasets focused** — one dataset per evaluation task (e.g., separate QA accuracy from style evaluation)

## Publishing Other Objects

`weave.publish()` works for any Weave object, not just datasets:

```python
# Publish a model
model = MyModel(model_name="gpt-4o", system_prompt="Be helpful.")
ref = weave.publish(model)

# Publish a custom object
class SystemPrompt(weave.Object):
    prompt: str

sp = SystemPrompt(prompt="You are a Korean language tutor.")
weave.publish(sp)

# Retrieve later
retrieved = weave.ref('SystemPrompt').get()
```
