# Transformation Patterns

For API details, always fetch official docs first. This file covers conversion patterns that are NOT in the docs.

## Tracing Rules (quick reference)

1. `@weave.op()` goes **above** other decorators (`@retry`, `@cache`, etc.)
2. Add type hints to parameters and return type on decorated functions
3. Add `import weave` to every file that uses `@weave.op()`
4. `@weave.op()` is for **your** functions — LLM provider calls are auto-traced after `weave.init()`

---

## Model Conversion: Class → `weave.Model`

Convert when the class holds LLM configuration and has a method that calls an LLM. Don't convert pure data containers or utility classes.

### Conversion rules

1. Add `weave.Model` as base class (remove `@dataclass` if present)
2. Convert `__init__` params → Pydantic-style class attributes with type annotations
3. Rename `model` attribute → `model_name` (Pydantic reserved name)
4. Rename main method → `predict` (or `invoke`), add `@weave.op()`
5. Non-serializable objects (API clients) → create inside methods or use `model_post_init` with `_` prefix

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
