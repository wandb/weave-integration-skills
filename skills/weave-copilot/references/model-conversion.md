# Model Conversion Reference

How to convert existing classes to `weave.Model` for automatic parameter versioning and evaluation compatibility.

## When to Convert

Convert a class to `weave.Model` when it:
- Holds LLM configuration (model name, temperature, system prompt)
- Has a method that calls an LLM
- Will be used with `weave.Evaluation` for comparison

**Do not convert** pure data containers, utility classes, or classes without LLM interaction.

## Conversion Steps

### Step 1: Add `weave.Model` as base class

```python
# BEFORE
class ChatBot:
    ...

# AFTER
class ChatBot(weave.Model):
    ...
```

If the class already inherits from another class, add `weave.Model` as an additional base:

```python
# BEFORE
class ChatBot(BaseLLM):
    ...

# AFTER
class ChatBot(weave.Model, BaseLLM):
    ...
```

### Step 2: Convert `__init__` to Pydantic-style attributes

`weave.Model` uses Pydantic under the hood. Declare attributes with type annotations at the class level instead of in `__init__`.

```python
# BEFORE
class ChatBot:
    def __init__(self, model="gpt-4o", temperature=0.7, system_prompt="You are helpful."):
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.client = OpenAI()

# AFTER
class ChatBot(weave.Model):
    model_name: str = "gpt-4o"          # Renamed: 'model' conflicts with Pydantic
    temperature: float = 0.7
    system_prompt: str = "You are helpful."

    # Non-serializable objects: create in methods or use model_post_init
    def model_post_init(self, __context):
        self._client = OpenAI()
```

**Important naming note**: Avoid attribute name `model` — it conflicts with Pydantic's reserved name. Use `model_name`, `llm_model`, or similar.

### Step 3: Rename the main method to `predict`

```python
# BEFORE
class ChatBot(weave.Model):
    model_name: str = "gpt-4o"

    def generate(self, prompt):          # Any name
        ...

# AFTER
class ChatBot(weave.Model):
    model_name: str = "gpt-4o"

    @weave.op()
    def predict(self, prompt: str) -> str:   # Must be 'predict' (or 'invoke')
        ...
```

### Step 4: Add `@weave.op()` to the predict method

```python
@weave.op()
def predict(self, user_input: str) -> str:
    ...
```

## Complete Before/After Examples

### Example 1: Simple LLM wrapper

```python
# BEFORE
from openai import OpenAI

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

# Usage
bot = QABot(model="gpt-4o-mini")
result = bot.answer("What is Python?")
```

```python
# AFTER
import weave
from openai import OpenAI

class QABot(weave.Model):
    model_name: str = "gpt-4o"         # 'model' → 'model_name'
    temperature: float = 0.7

    @weave.op()
    def predict(self, question: str) -> str:   # 'answer' → 'predict'
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content

# Usage — instantiation changes to keyword args (Pydantic style)
bot = QABot(model_name="gpt-4o-mini")
result = bot.predict("What is Python?")
```

### Example 2: Class with system prompt and multiple methods

```python
# BEFORE
class Summarizer:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.system_prompt = "You are a text summarizer."
        self.client = OpenAI()

    def summarize(self, text):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Summarize:\n{text}"},
            ],
        )
        return response.choices[0].message.content

    def bullet_points(self, text):
        summary = self.summarize(text)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"Convert to bullet points:\n{summary}"},
            ],
        )
        return response.choices[0].message.content
```

```python
# AFTER
import weave
from openai import OpenAI

class Summarizer(weave.Model):
    model_name: str = "gpt-4o"
    system_prompt: str = "You are a text summarizer."

    @weave.op()
    def predict(self, text: str) -> str:   # Main method → predict
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Summarize:\n{text}"},
            ],
        )
        return response.choices[0].message.content

    @weave.op()
    def bullet_points(self, text: str) -> str:  # Additional methods: keep name, add @weave.op()
        summary = self.predict(text)    # Call predict instead of summarize
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": f"Convert to bullet points:\n{summary}"},
            ],
        )
        return response.choices[0].message.content
```

### Example 3: Dataclass-based model

```python
# BEFORE
from dataclasses import dataclass

@dataclass
class TranslationModel:
    source_lang: str
    target_lang: str
    model: str = "gpt-4o"

    def translate(self, text):
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"Translate from {self.source_lang} to {self.target_lang}."},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
```

```python
# AFTER — remove @dataclass, weave.Model handles it
import weave
from openai import OpenAI

class TranslationModel(weave.Model):       # Remove @dataclass
    source_lang: str
    target_lang: str
    model_name: str = "gpt-4o"             # 'model' → 'model_name'

    @weave.op()
    def predict(self, text: str) -> str:   # 'translate' → 'predict'
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"Translate from {self.source_lang} to {self.target_lang}."},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content
```

## Edge Cases

### Non-serializable attributes

Objects like API clients, database connections cannot be Pydantic fields. Use `model_post_init`:

```python
class MyApp(weave.Model):
    model_name: str = "gpt-4o"

    def model_post_init(self, __context):
        self._client = OpenAI()  # Prefix with _ to exclude from serialization

    @weave.op()
    def predict(self, input: str) -> str:
        return self._client.chat.completions.create(...)
```

### Backward-compatible alias (only if necessary)

If the old method name (`generate`, `answer`, etc.) is called from many places and updating all call sites is impractical, you can add a temporary alias. **Prefer updating call sites directly** — aliases add indirection and should be removed once all callers are migrated.

```python
class MyApp(weave.Model):
    @weave.op()
    def predict(self, input: str) -> str:
        ...

    # Temporary alias — remove once all callers use predict()
    def generate(self, input: str) -> str:
        return self.predict(input)
```

### Updating callers

After renaming the main method to `predict`, update all call sites:

```python
# BEFORE
result = bot.answer("question")
result = bot.generate("prompt")

# AFTER
result = bot.predict("question")
result = bot.predict("prompt")
```
