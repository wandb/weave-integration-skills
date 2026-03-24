# Weave Scorers Reference

Scorers grade model outputs during evaluations. Weave supports function-based scorers, class-based scorers, and built-in scorers.

## Function-Based Scorers

The simplest approach. Decorate a function with `@weave.op()` that returns a dictionary.

The function receives:
- `output` — the return value of your model's `predict` method
- Any dataset column by name (e.g., `expected`, `context`, `question`)

```python
@weave.op()
def exact_match(expected: str, output: str) -> dict:
    return {"match": expected.strip().lower() == output.strip().lower()}

@weave.op()
def contains_keyword(output: str, expected: str) -> dict:
    return {"contains": expected.lower() in output.lower()}

@weave.op()
def length_check(output: str) -> dict:
    return {"appropriate_length": 10 < len(output) < 500}
```

## Class-Based Scorers (`weave.Scorer`)

For complex scoring logic with state, multiple methods, or configurable parameters.

Requirements:
1. Inherit from `weave.Scorer`
2. Define a `score` method decorated with `@weave.op()`
3. Return a dictionary from `score`

```python
import weave
from weave import Scorer
from openai import OpenAI

class LLMJudgeScorer(Scorer):
    model_id: str = "gpt-4o"
    system_prompt: str = "You are an expert evaluator. Rate the answer quality from 1-5."

    @weave.op()
    def score(self, output: str, expected: str) -> dict:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": (
                    f"Expected answer: {expected}\n"
                    f"Actual answer: {output}\n"
                    "Rate from 1-5 and explain."
                )},
            ],
        )
        judgment = response.choices[0].message.content
        # Parse the score (simplified)
        score_val = int(judgment[0]) if judgment and judgment[0].isdigit() else 0
        return {"quality_score": score_val, "reasoning": judgment}
```

### Multi-Step Scorer

Class-based scorers can have helper methods:

```python
class DetailedScorer(Scorer):
    model_id: str = "gpt-4o"

    @weave.op()
    def preprocess(self, text: str) -> str:
        return text.strip().lower()

    @weave.op()
    def call_llm(self, prompt: str) -> str:
        client = OpenAI()
        res = client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content

    @weave.op()
    def score(self, output: str, expected: str) -> dict:
        processed = self.preprocess(output)
        judgment = self.call_llm(
            f"Compare:\nExpected: {expected}\nGot: {processed}\nIs it correct? yes/no"
        )
        return {"correct": "yes" in judgment.lower()}
```

## Column Mapping (`column_map`)

When your dataset column names don't match what a scorer expects, use `column_map`:

```python
from weave.scorers import HallucinationFreeScorer

# Dataset has "input" column, but scorer expects "context"
scorer = HallucinationFreeScorer(
    model_id="openai/gpt-4o",
    column_map={"context": "input", "output": "other_col"}
)
```

The `column_map` maps **scorer parameter names** → **dataset column names**.

## Built-in Scorers

Weave provides ready-to-use scorers via `weave.scorers`. As of Feb 2025, LLM-based scorers use `model_id` with LiteLLM format (no need to pass a client).

### HallucinationFreeScorer

Checks if the output contains hallucinations relative to context:

```python
import asyncio
import weave
from weave.scorers import HallucinationFreeScorer

weave.init('my-team/hallucination-eval')

hallucination_scorer = HallucinationFreeScorer(
    model_id="openai/gpt-4o",  # LiteLLM format: "provider/model"
    column_map={"context": "input"}  # Map if dataset uses different column name
)

dataset = [
    {"input": "John likes various types of cheese."},
    {"input": "Pepe likes various types of cheese."},
]

@weave.op()
def model(input: str) -> str:
    return "The person's favorite cheese is cheddar."

evaluation = weave.Evaluation(dataset=dataset, scorers=[hallucination_scorer])
asyncio.run(evaluation.evaluate(model))
# Returns: {'HallucinationFreeScorer': {'has_hallucination': {'true_count': 2, 'true_fraction': 1.0}}}
```

### SummarizationScorer

Evaluates summary quality against original text:

```python
from weave.scorers import SummarizationScorer

summarization_scorer = SummarizationScorer(
    model_id="openai/gpt-4o"  # or "anthropic/claude-3-5-sonnet-20240620"
)
```

Evaluates in two ways: entity density and quality assessment via LLM.

### EmbeddingSimilarityScorer

Cosine similarity between embeddings of output and reference:

```python
from weave.scorers import EmbeddingSimilarityScorer

similarity_scorer = EmbeddingSimilarityScorer(
    model_id="openai/text-embedding-3-small",
    threshold=0.4  # Minimum cosine similarity (default: 0.5)
)
```

### OpenAIModerationScorer

Checks for harmful or disallowed content using OpenAI's Moderation API:

```python
import asyncio
import weave
from weave.scorers import OpenAIModerationScorer

weave.init('my-team/moderation-eval')

moderation_scorer = OpenAIModerationScorer()

dataset = [
    {"input": "I love puppies and kittens!"},
    {"input": "I hate everyone and want to hurt them."},
]

@weave.op()
async def model(input: str) -> str:
    return input

evaluation = weave.Evaluation(dataset=dataset, scorers=[moderation_scorer])
asyncio.run(evaluation.evaluate(model))
# Returns: {'OpenAIModerationScorer': {'flagged': {'true_count': 1, 'true_fraction': 0.5}}}
```

### ValidJSONScorer

Checks whether model output is valid JSON:

```python
from weave.scorers import ValidJSONScorer

json_scorer = ValidJSONScorer()
```

### ValidXMLScorer

Checks whether model output is valid XML:

```python
from weave.scorers import ValidXMLScorer

xml_scorer = ValidXMLScorer()
```

### PydanticScorer

Validates model output against a Pydantic schema:

```python
from weave.scorers import PydanticScorer
from pydantic import BaseModel

class FinancialReport(BaseModel):
    revenue: int
    year: str

pydantic_scorer = PydanticScorer(model=FinancialReport)
```

### ContextEntityRecallScorer (RAGAS)

Extracts entities from output and context, then computes recall. Based on the RAGAS library:

```python
from weave.scorers import ContextEntityRecallScorer

entity_recall_scorer = ContextEntityRecallScorer(
    model_id="openai/gpt-4o"
)
```

Expects a `context` column in your dataset. Use `column_map` if the column name differs.

### ContextRelevancyScorer (RAGAS)

Rates the relevancy of provided context to the model output:

```python
from weave.scorers import ContextRelevancyScorer

relevancy_scorer = ContextRelevancyScorer(
    model_id="openai/gpt-4o",
    relevancy_prompt="""
Given the following question and context, rate the relevancy on a scale from 0 to 1.

Question: {question}
Context: {context}
Relevancy Score (0-1):
"""
)
```

### Complete RAG Evaluation Example

```python
import asyncio
from textwrap import dedent
import weave
from weave.scorers import ContextEntityRecallScorer, ContextRelevancyScorer

weave.init('my-team/rag-eval')

class RAGModel(weave.Model):
    @weave.op()
    async def predict(self, question: str) -> str:
        return "Paris is the capital of France."

entity_recall_scorer = ContextEntityRecallScorer(model_id="openai/gpt-4o")
relevancy_scorer = ContextRelevancyScorer(model_id="openai/gpt-4o")

dataset = [
    {"question": "What is the capital of France?", "context": "Paris is the capital city of France."},
    {"question": "Who wrote Romeo and Juliet?", "context": "William Shakespeare wrote many famous plays."},
]

evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[entity_recall_scorer, relevancy_scorer],
)
asyncio.run(evaluation.evaluate(RAGModel()))
```

## RAG-Specific Scorers

For evaluating RAG pipelines, combine multiple scorers:

```python
import weave
from weave.scorers import HallucinationFreeScorer, EmbeddingSimilarityScorer

# Faithfulness: is the answer grounded in context?
faithfulness = HallucinationFreeScorer(
    model_id="openai/gpt-4o",
    column_map={"context": "retrieved_docs"}
)

# Relevance: is the answer similar to the expected answer?
relevance = EmbeddingSimilarityScorer(
    model_id="openai/text-embedding-3-small",
    threshold=0.5
)

# Correctness: custom exact match
@weave.op()
def answer_correctness(output: str, expected_answer: str) -> dict:
    return {"correct": expected_answer.lower() in output.lower()}

evaluation = weave.Evaluation(
    dataset=rag_dataset,
    scorers=[faithfulness, relevance, answer_correctness],
    evaluation_name="RAG Pipeline Eval"
)
```

## Tips for Writing Good Scorers

1. **Return dictionaries** — keys become metric names in the UI
2. **Use descriptive key names** — `{"factually_correct": True}` is better than `{"score": 1}`
3. **Boolean values get aggregated** — Weave auto-computes `true_count` and `true_fraction`
4. **Numeric values get aggregated** — Weave computes `mean`
5. **Keep scorers focused** — one metric per scorer is easier to track
6. **Use `column_map`** when reusing scorers across datasets with different column names
7. **LLM-as-judge scorers** are powerful but add cost and latency — use sparingly for key metrics
