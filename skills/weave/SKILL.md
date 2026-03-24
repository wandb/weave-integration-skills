---
name: weave
description: >
  Generate W&B Weave code for LLM application development — tracing, evaluation, scoring, dataset
  management, prompt versioning, production monitoring, guardrails, feedback, and cost tracking.
  Use this skill whenever the user mentions weave, weave.op, @weave.op, weave.init,
  weave.Model, weave.Evaluation, weave.Scorer, weave.Dataset, weave.publish, weave.ref,
  weave.StringPrompt, weave.MessagesPrompt, weave.Prompt, weave.attributes,
  HallucinationFreeScorer, SummarizationScorer, EmbeddingSimilarityScorer,
  OpenAIModerationScorer, ValidJSONScorer, PydanticScorer,
  ContextEntityRecallScorer, ContextRelevancyScorer, AnnotationSpec,
  call.apply_scorer, call.feedback, add_cost, query_costs, or asks about
  LLM observability, tracing, evaluation pipelines, custom scorers, LLM-as-judge,
  dataset versioning, prompt versioning, production monitoring, guardrails,
  content moderation, PII detection, feedback collection, annotations,
  cost tracking, or sampling rate with W&B Weave. Also trigger when the user wants to:
  add tracing/logging to an LLM app, evaluate LLM outputs, create scoring functions,
  build evaluation datasets, version prompts, set up monitors or guardrails,
  collect feedback on LLM outputs, track LLM costs,
  integrate with LLM providers (OpenAI, Anthropic, LiteLLM, Google GenAI, Mistral, Cohere, etc.),
  or use agent framework integrations (LangChain, LlamaIndex, Smolagents, OpenAI Agents SDK,
  CrewAI, DSPy, Instructor, PydanticAI, Google ADK, AutoGen, MCP).
  Casual mentions should also trigger: "track my LLM calls", "evaluate my chatbot",
  "score my model outputs", "version my prompts", "monitor my LLM in production",
  "block harmful content", "add feedback to calls", "track LLM costs",
  "LLM 호출 추적", "LLM 평가", "프롬프트 버전 관리", "RAG 파이프라인 트레이싱",
  "챗봇 품질 평가", "hallucination 체크", "프로덕션 모니터링", "가드레일 설정",
  "피드백 수집", "비용 추적". Covers the full Weave workflow from instrumentation to production.
---

# W&B Weave Skill

Generate production-ready W&B Weave code for the full LLM development lifecycle: tracing, evaluation, scoring, and dataset management.

## How to use this skill

This skill is organized into focused reference files. Read the relevant reference(s) based on the user's request before generating code.

### Reference Files

| File | When to read | Covers |
|------|-------------|--------|
| `references/tracing.md` | User wants to add observability, track LLM calls, use `@weave.op()`, create `weave.Model` | Project init, `@weave.op()` decorator, `weave.Model` class, nested traces, async patterns, sampling rate, kind/color, postprocess, attributes, threads, media logging |
| `references/evaluation.md` | User wants to evaluate their LLM app, run evaluations, compare model versions | `weave.Evaluation` class, evaluation pipeline setup, running evaluations, comparing results |
| `references/scorers.md` | User wants to create scoring functions, use built-in scorers, or build LLM-as-judge evaluators | Custom scorers, `weave.Scorer` class, built-in scorers (hallucination, summarization, similarity, moderation, JSON/XML/Pydantic validation, RAGAS), `column_map` |
| `references/datasets.md` | User wants to create, publish, version, or retrieve evaluation datasets | `weave.Dataset`, `weave.publish()`, `weave.ref()`, dataset versioning, data formats |
| `references/prompts.md` | User wants to version prompts, use prompt templates, or manage prompt lifecycle | `weave.StringPrompt`, `weave.MessagesPrompt`, parameterized prompts, custom prompt subclasses |
| `references/monitors-guardrails.md` | User wants to monitor production LLM traffic or add safety guardrails | Monitors (UI-based passive scoring), guardrails (`call.apply_scorer()`), `OpenAIModerationScorer`, `BedrockGuardrailScorer`, PII detection |
| `references/feedback.md` | User wants to collect feedback on LLM outputs or set up human annotations | `call.feedback.add_reaction()`, `call.feedback.add_note()`, custom feedback, `AnnotationSpec`, human annotation scorers |
| `references/costs.md` | User wants to track or manage LLM costs | `client.add_cost()`, `client.query_costs()`, `client.purge_costs()`, project-level cost aggregation |
| `references/integrations.md` | User wants provider-specific integration code (OpenAI, Anthropic, LiteLLM, agent frameworks) | Auto-patching, provider patterns, agent framework tracing (LangChain, LlamaIndex, CrewAI, DSPy, Instructor, PydanticAI, Google ADK, AutoGen, MCP), environment variables |
| `references/troubleshooting.md` | User hits an error, traces not appearing, scorer not working, or any debugging question | Authentication, tracing issues, evaluation errors, model/dataset problems, integration fixes |

### Decision Flow

1. If the user asks a **quickstart / getting started** question → read `references/tracing.md`
2. If the request involves **multiple topics** (e.g., "set up tracing and evaluation") → read all relevant references
3. If unsure which reference applies → read `references/tracing.md` first (it's the foundation), then read others as needed

## Universal Code Requirements

Every piece of Weave code you generate must follow these rules:

1. **Always include** `import weave` and `weave.init('team/project')` with a comment to replace with actual team/project
2. **Always add type hints** on function parameters and return types
3. **Generate complete, runnable code** — not fragments
4. **Include brief inline comments** explaining what Weave tracks at each point
5. **Mention `WANDB_API_KEY`** setup in comments or explanations
6. **Use the latest API patterns**: `@weave.op` (parentheses optional), `model_id` for built-in scorers (not `client` parameter)
7. **Korean and English**: Respond in whichever language the user is using

## Quick Reference: Core API Surface

```python
# Initialization
weave.init('team/project')

# Tracing
@weave.op()
def my_func(input: str) -> str: ...

# Advanced op config
@weave.op(tracing_sample_rate=0.1, kind="llm", color="blue")
def sampled_llm(input: str) -> str: ...

# Model versioning
class MyModel(weave.Model):
    param: str
    @weave.op()
    def predict(self, input: str) -> str: ...

# Prompts
prompt = weave.StringPrompt("You are a {role}.")
weave.publish(prompt, name="my-prompt")
formatted = prompt.format(role="helpful assistant")

# Dataset
dataset = weave.Dataset(name='my-dataset', rows=[...])
weave.publish(dataset)
retrieved = weave.ref('my-dataset').get()

# Evaluation
evaluation = weave.Evaluation(dataset=dataset, scorers=[my_scorer])
import asyncio
asyncio.run(evaluation.evaluate(model))

# Custom Scorer (function-based)
@weave.op()
def my_scorer(output: str, expected: str) -> dict:
    return {"match": output == expected}

# Custom Scorer (class-based)
class MyScorer(weave.Scorer):
    @weave.op()
    def score(self, output: str, expected: str) -> dict:
        return {"match": output == expected}

# Built-in Scorers
from weave.scorers import (
    HallucinationFreeScorer, SummarizationScorer, EmbeddingSimilarityScorer,
    OpenAIModerationScorer, ValidJSONScorer, ValidXMLScorer, PydanticScorer,
    ContextEntityRecallScorer, ContextRelevancyScorer,
)

# Guardrails (inline scoring)
result, call = my_func.call("input")
score = await call.apply_scorer(my_scorer_instance)

# Feedback
call.feedback.add_reaction("👍")
call.feedback.add_note("Great response")
call.feedback.add("correctness", {"value": 5})

# Costs
client = weave.init('team/project')
client.add_cost(llm_id="my-model", prompt_token_cost=0.01, completion_token_cost=0.02)

# Attributes
with weave.attributes({"env": "production"}):
    my_func("input")
```

This quick reference is for at-a-glance lookup. For complete patterns and examples, always read the appropriate reference file.

## Troubleshooting

Common errors and solutions: [references/troubleshooting.md](references/troubleshooting.md)
