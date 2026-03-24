# Weave Prompts Reference

Weave provides versioned prompt management for LLM applications. Prompts are tracked objects — every change creates a new version, enabling safe experimentation and rollback.

## StringPrompt

For single-string prompts (system messages, user queries, standalone text inputs):

```python
import weave
from openai import OpenAI

weave.init('my-team/my-project')
client = OpenAI()

system_prompt = weave.StringPrompt("You speak like a pirate")
weave.publish(system_prompt, name="pirate_prompt")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt.format()},
        {"role": "user", "content": "Explain general relativity in one paragraph."},
    ],
)
```

## MessagesPrompt

For multi-turn conversations and chat-based prompts:

```python
import weave
from openai import OpenAI

weave.init('my-team/my-project')
client = OpenAI()

prompt = weave.MessagesPrompt([
    {
        "role": "system",
        "content": "You are a helpful coding assistant."
    },
    {
        "role": "user",
        "content": "How do I sort a list in Python?"
    }
])
weave.publish(prompt, name="coding_prompt")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=prompt.format(),
)
```

## Parameterized Prompts

Both `StringPrompt` and `MessagesPrompt` support `{variable}` placeholders. The `format()` method accepts keyword arguments to fill them:

### StringPrompt with parameters

```python
import weave
from openai import OpenAI

weave.init('my-team/my-project')
client = OpenAI()

prompt = weave.StringPrompt("Solve the equation {equation}")
weave.publish(prompt, name="calculator_prompt")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": prompt.format(equation="1 + 1 = ?")},
    ],
)
```

### MessagesPrompt with parameters

```python
prompt = weave.MessagesPrompt([
    {
        "role": "system",
        "content": "You are an expert on {topic}."
    },
    {
        "role": "user",
        "content": "{question}"
    }
])
weave.publish(prompt, name="expert_prompt")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=prompt.format(topic="machine learning", question="What is backpropagation?"),
)
```

## Versioning and Retrieval

Publishing a prompt with the same name but different content automatically creates a new version:

```python
import weave

weave.init('my-team/my-project')

# Version 1
prompt_v1 = weave.StringPrompt("Be concise.")
weave.publish(prompt_v1, name="style_prompt")

# Version 2 (auto-increments)
prompt_v2 = weave.StringPrompt("Be concise and use bullet points.")
weave.publish(prompt_v2, name="style_prompt")

# Retrieve latest version
latest = weave.ref("style_prompt").get()

# Retrieve specific version
v1 = weave.ref("style_prompt:v0").get()
```

## Custom Prompt Subclass

For complex prompt logic, subclass `weave.Prompt` and override `format`:

```python
import weave

class RAGPrompt(weave.Prompt):
    context_template: str = "Context:\n{context}\n\nQuestion: {question}"

    def format(self, **kwargs) -> str:
        context_str = "\n".join(kwargs.get("context", []))
        return self.context_template.format(
            context=context_str,
            question=kwargs.get("question", ""),
        )

weave.init('my-team/my-project')
prompt = RAGPrompt()
weave.publish(prompt, name="rag_prompt")

formatted = prompt.format(
    context=["Paris is the capital of France.", "France is in Europe."],
    question="What is the capital of France?",
)
```

## Using Prompts with weave.Model

Combine prompts with `weave.Model` for full versioning of both prompt and model parameters:

```python
import weave
from openai import OpenAI

class ChatBot(weave.Model):
    model_name: str = "gpt-4o"
    system_prompt: weave.StringPrompt

    @weave.op()
    def predict(self, user_input: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt.format()},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content

weave.init('my-team/my-project')

bot = ChatBot(system_prompt=weave.StringPrompt("You are a helpful assistant."))
result = bot.predict("Hello!")
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Prompt not appearing in UI | Ensure `weave.publish(prompt, name="...")` is called with a name |
| Variables not replaced | Check placeholder names match `format()` keyword arguments exactly |
| Version not incrementing | Content must differ from previous version; identical content reuses existing version |
