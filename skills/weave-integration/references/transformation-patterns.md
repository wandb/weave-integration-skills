# Transformation Patterns

Before/after patterns for adding Weave to existing code. For API details, always fetch official docs first.

## Tracing: Adding `@weave.op()`

### Rules

1. **Decorator order**: `@weave.op()` goes **above** other decorators (`@retry`, `@cache`, etc.)
2. **Type hints**: Add to parameters and return type on decorated functions
3. **Import**: Add `import weave` to every file that uses `@weave.op()`
4. **Async**: `@weave.op()` works with `async def` — no changes needed
5. **Auto-patching**: After `weave.init()`, LLM provider calls are auto-traced. `@weave.op()` is for **your** functions.

### What NOT to decorate

- Pure utility functions (string formatting, data conversion)
- Functions called thousands of times per second (use `tracing_sample_rate`)
- Third-party library functions (use auto-patching)

### Basic pattern

```python
# BEFORE
def generate_response(prompt, temperature=0.7):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# AFTER
@weave.op()
def generate_response(prompt: str, temperature: float = 0.7) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

### Class methods

```python
# BEFORE
class RAGPipeline:
    def retrieve(self, query):
        return self.vector_store.search(query)

    def run(self, query):
        context = self.retrieve(query)
        return self.generate(query, context)

# AFTER
class RAGPipeline:
    @weave.op()
    def retrieve(self, query: str) -> list[str]:
        return self.vector_store.search(query)

    @weave.op()
    def run(self, query: str) -> str:
        context = self.retrieve(query)
        return self.generate(query, context)
```

---

## Model Conversion: Class → `weave.Model`

### When to convert

Convert when the class holds LLM configuration (model name, temperature, system prompt) and has a method that calls an LLM. **Don't convert** pure data containers or utility classes.

### Conversion rules

1. Add `weave.Model` as base class (remove `@dataclass` if present)
2. Convert `__init__` params → Pydantic-style class attributes with type annotations
3. Rename `model` attribute → `model_name` (Pydantic reserved name)
4. Rename main method → `predict` (or `invoke`), add `@weave.op()`
5. Non-serializable objects (API clients) → `model_post_init` or create in methods

### Example

```python
# BEFORE
class QABot:
    def __init__(self, model="gpt-4o", temperature=0.7):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI()

    def answer(self, question):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content

# AFTER
class QABot(weave.Model):
    model_name: str = "gpt-4o"
    temperature: float = 0.7

    @weave.op()
    def predict(self, question: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content

# Update all call sites: bot.answer(...) → bot.predict(...)
```

### Non-serializable attributes

```python
class MyApp(weave.Model):
    model_name: str = "gpt-4o"

    def model_post_init(self, __context):
        self._client = OpenAI()  # Prefix with _ to exclude from serialization
```

---

## Evaluation: Existing Tests → `weave.Evaluation`

### When to convert

Convert when existing code has test cases with expected outputs, computes scores/metrics on LLM outputs, or runs comparison loops.

### Pattern

```
Existing test data       →  weave.Dataset
Existing scoring logic   →  Scorer function with @weave.op()
Existing eval loop       →  weave.Evaluation.evaluate()
```

### Example

```python
# BEFORE
def run_eval():
    cases = [{"question": "What is 2+2?", "answer": "4"}, ...]
    correct = 0
    for case in cases:
        output = model(case["question"])
        if case["answer"].lower() in output.lower():
            correct += 1
    print(f"Accuracy: {correct/len(cases):.2%}")

# AFTER
import asyncio
import weave

weave.init('team/project')

dataset = weave.Dataset(name="qa-benchmark", rows=cases)

@weave.op()
def accuracy_scorer(output: str, answer: str) -> dict:
    return {"correct": answer.lower() in output.lower()}

evaluation = weave.Evaluation(dataset=dataset, scorers=[accuracy_scorer])
asyncio.run(evaluation.evaluate(model))
```

### Key points

- `evaluation.evaluate()` is async — use `asyncio.run()` in scripts
- Scorer receives `output` (from model) + dataset columns by name
- Use `column_map` if scorer param names don't match dataset columns:
  ```python
  weave.Evaluation(dataset=dataset, scorers=[MyScorer(column_map={"reference": "expected"})])
  ```

---

## Prompt Extraction: Hardcoded Strings → Versioned Prompts

### When to extract

Extract when system messages or templates are hardcoded as string literals, shared across files, or need A/B testing.

**Exception**: If the prompt is inside a `weave.Model`, it's already versioned as a model attribute — no need for separate `weave.StringPrompt`.

### String constant → `weave.StringPrompt`

```python
# BEFORE
SYSTEM_PROMPT = "You are a helpful assistant."

# AFTER
system_prompt = weave.StringPrompt("You are a helpful assistant.")
weave.publish(system_prompt, name="qa-system-prompt")
# Usage: system_prompt.format()
```

### Template → Parameterized `weave.StringPrompt`

```python
# BEFORE
prompt = f"Summarize in {language}:\n\n{text}"

# AFTER
summary_prompt = weave.StringPrompt("Summarize in {language}:\n\n{text}")
weave.publish(summary_prompt, name="summary-prompt")
# Usage: summary_prompt.format(language=language, text=text)
```

### Message list → `weave.MessagesPrompt`

```python
# BEFORE
messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": user_message},
]

# AFTER
chat_prompt = weave.MessagesPrompt(messages=[
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "{user_message}"},
])
weave.publish(chat_prompt, name="coding-assistant-prompt")
# Usage: chat_prompt.format(user_message=user_message)
```
