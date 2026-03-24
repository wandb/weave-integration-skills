# Weave Tracing Reference

Tracing is the foundation of Weave. It captures the inputs, outputs, latency, and code version of every function call in your LLM application.

## Project Initialization

Every Weave-instrumented app starts with `weave.init()`:

```python
import weave

# Format: 'team-name/project-name' or just 'project-name' (uses default team)
weave.init('my-team/my-project')
```

- Call once at application start
- Project is auto-created if it doesn't exist
- Requires `WANDB_API_KEY` environment variable
- For teams: `weave.init('team/project')`. Omitting team uses default entity

## The `@weave.op()` Decorator

Decorating a function captures its inputs, outputs, execution time, and code version. Nested decorated functions form a trace tree.

```python
@weave.op()
def my_function(input_text: str) -> str:
    return result
```

Key behaviors:
- Parentheses optional: `@weave.op` and `@weave.op()` both work
- Works with sync and async functions
- Type hints improve trace readability
- Only decorated functions appear in the trace tree

## Auto-Patching (LLM Provider Integrations)

After `weave.init()`, supported LLM libraries are automatically patched — no extra decorators needed:

| Provider | Library | What's auto-tracked |
|----------|---------|-------------------|
| OpenAI | `openai` | chat.completions, embeddings, images |
| Anthropic | `anthropic` | messages.create, tool use |
| Google AI | `google-generativeai` | generate_content |
| Cohere | `cohere` | chat, generate |
| Mistral | `mistralai` | chat.complete |
| LiteLLM | `litellm` | completion, acompletion |
| Groq | `groq` | chat.completions |
| Bedrock | `boto3` (bedrock-runtime) | invoke_model |

## The `weave.Model` Class

For structured apps with configurable parameters. Captures parameters and auto-versions when they change.

Requirements:
- Inherit from `weave.Model`
- Type annotations on all class attributes
- Implement `predict` (or `invoke`) method with `@weave.op()`

```python
class MyApp(weave.Model):
    model_name: str
    system_prompt: str
    temperature: float = 0.7

    @weave.op()
    def predict(self, user_input: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content
```

Use `weave.Model` when you have parameters to version and compare. Use plain `@weave.op()` for quick scripts.

### Publishing and Retrieving Models

```python
weave.init('my-team/my-project')
model = MyApp(model_name="gpt-4o", system_prompt="You are helpful.")
ref = weave.publish(model)

# Later, retrieve the exact version
retrieved = weave.ref("weave:///team/project/object/MyApp:<digest>").get()
result = retrieved.predict("Hello!")
```

## Advanced Op Configuration

### Custom Display Name

```python
@weave.op(name="custom_name")
def my_internal_function():
    ...
```

### Sampling Rate

Control how frequently an op's calls are traced. Only applies to root calls — nested ops inherit the parent's sampling decision:

```python
@weave.op(tracing_sample_rate=0.1)  # Trace ~10% of calls
def high_frequency_op(x: int) -> int:
    return x + 1

@weave.op(tracing_sample_rate=1.0)  # Always trace (default)
def always_traced_op(x: int) -> int:
    return x + 1
```

### Kind and Color

Visually categorize ops in the Weave UI trace tree:

```python
@weave.op(kind="llm", color="blue")
def llm_call():
    @weave.op(kind="tool", color="red")
    def tool_call():
        return "tool result"
    return f"llm result with {tool_call()}"
```

Available `kind` values: `search`, `tool`, `llm`, `agent`
Available `color` values: `purple`, `blue`, `green`, `yellow`, `orange`, `red`

### Input/Output Postprocessing (Data Redaction)

Hide sensitive data from traces without modifying the original function:

```python
from typing import Any

def redact_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in inputs.items() if k != "api_key"}

def redact_output(output: dict) -> dict:
    return {**output, "secret": "REDACTED"}

@weave.op(
    postprocess_inputs=redact_inputs,
    postprocess_output=redact_output,
)
def call_api(query: str, api_key: str) -> dict:
    return {"result": "data", "secret": api_key}
```

## Custom Attributes

Attach metadata to traced calls for filtering and segmentation:

```python
import weave

weave.init('my-team/my-project')

@weave.op()
def my_function(input: str) -> str:
    return f"Processed: {input}"

# Tag calls with environment, user, or any custom metadata
with weave.attributes({"env": "production", "user_id": "user-123"}):
    my_function("hello")
```

## Threads (Multi-Turn Conversations)

Group related calls under a shared `thread_id` for multi-turn conversation tracking:

```python
import weave
import openai

weave.init("my-team/my-project")
client = openai.OpenAI()

conversation_history = []
thread_id = "session-abc-123"

@weave.op()
def chat_turn(user_message: str) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation_history,
    )
    assistant_msg = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_msg})
    return assistant_msg

# Each turn is grouped under the same thread
with weave.attributes({"weave": {"thread_id": thread_id}}):
    chat_turn("Hello!")
    chat_turn("What did I just say?")
```

## Media Logging

Weave can log images, audio, video, and other media in traces. Use type annotations to indicate media content:

```python
from typing import Annotated
from weave.flow.chat_util import Content
import weave
import base64

weave.init('my-team/my-project')

@weave.op()
def process_image(image_path: str) -> Annotated[str, Content]:
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"
```

## Code Patterns

### Pattern A: Quick Start

Simplest possible tracing for getting started:

```python
import weave
from openai import OpenAI

weave.init('my-team/my-project')  # Replace with your team/project
client = OpenAI()

@weave.op()
def ask(question: str) -> str:
    """Weave tracks: inputs, outputs, latency, OpenAI token usage & cost"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

result = ask("What is the capital of France?")
print(result)
```

### Pattern B: Structured Application (weave.Model)

For real applications with configurable parameters:

```python
import weave
from openai import OpenAI

class QABot(weave.Model):
    model_name: str = "gpt-4o"
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7

    @weave.op()
    def predict(self, question: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content

weave.init('my-team/my-project')
bot = QABot()
result = bot.predict("Explain quantum computing simply.")
```

### Pattern C: Multi-Step Pipeline (nested traces)

Each decorated function becomes a span in the trace tree:

```python
import weave
from openai import OpenAI

weave.init('my-team/my-project')
client = OpenAI()

@weave.op()
def retrieve_context(query: str) -> list[str]:
    # Your retrieval logic here
    return ["relevant doc 1", "relevant doc 2"]

@weave.op()
def generate_answer(query: str, context: list[str]) -> str:
    context_str = "\n".join(context)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Answer based on:\n{context_str}"},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content

@weave.op()
def rag_pipeline(query: str) -> str:
    """Parent span groups retrieve + generate as children"""
    context = retrieve_context(query)
    return generate_answer(query, context)

result = rag_pipeline("What is W&B Weave?")
```

### Pattern D: Async Application

For async apps (FastAPI, aiohttp, etc.):

```python
import weave
import asyncio
from openai import AsyncOpenAI

weave.init('my-team/my-project')
client = AsyncOpenAI()

@weave.op()
async def async_ask(question: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

asyncio.run(async_ask("Hello!"))
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No traces appearing | Check `WANDB_API_KEY` is set and `weave.init()` called before traced functions |
| Missing LLM details | Ensure LLM library imported and called after `weave.init()` |
| Nested ops not forming tree | Parent function must also have `@weave.op()` |
| `weave.Model` attributes missing | All attributes need type annotations |
| Streaming not tracked | Weave handles it automatically; trace completes when stream finishes |
