# Prompt Versioning Reference

How to extract hardcoded prompts from existing code into versioned Weave prompt objects.

## When to Extract

Extract prompts when:
- System messages or templates are hardcoded as string literals
- The same prompt is used across multiple files
- The user wants to track prompt changes over time
- The user wants to A/B test different prompts

## Pattern 1: String Constant → `weave.StringPrompt`

```python
# BEFORE
SYSTEM_PROMPT = "You are a helpful assistant that answers questions concisely."

def ask(question):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
```

```python
# AFTER
import weave

system_prompt = weave.StringPrompt("You are a helpful assistant that answers questions concisely.")
weave.publish(system_prompt, name="qa-system-prompt")

@weave.op()
def ask(question: str) -> str:
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt.format()},
            {"role": "user", "content": question},
        ],
    )
```

## Pattern 2: Template String → Parameterized `weave.StringPrompt`

```python
# BEFORE
def generate_summary(text, language="English"):
    prompt = f"Summarize the following text in {language}:\n\n{text}"
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
```

```python
# AFTER
import weave

summary_prompt = weave.StringPrompt(
    "Summarize the following text in {language}:\n\n{text}"
)
weave.publish(summary_prompt, name="summary-prompt")

@weave.op()
def generate_summary(text: str, language: str = "English") -> str:
    prompt = summary_prompt.format(language=language, text=text)
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
```

## Pattern 3: Messages List → `weave.MessagesPrompt`

```python
# BEFORE
def chat(user_message):
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": user_message},
    ]
    return client.chat.completions.create(model="gpt-4o", messages=messages)
```

```python
# AFTER
import weave

chat_prompt = weave.MessagesPrompt(
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "{user_message}"},
    ]
)
weave.publish(chat_prompt, name="coding-assistant-prompt")

@weave.op()
def chat(user_message: str) -> str:
    messages = chat_prompt.format(user_message=user_message)
    return client.chat.completions.create(model="gpt-4o", messages=messages)
```

## Pattern 4: Prompts in `weave.Model`

```python
# BEFORE
class ChatBot:
    def __init__(self):
        self.system_prompt = "You are a helpful assistant."

# AFTER — system_prompt becomes a versioned Model attribute
class ChatBot(weave.Model):
    system_prompt: str = "You are a helpful assistant."

    @weave.op()
    def predict(self, user_input: str) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content
```

When the class is a `weave.Model`, the system prompt is automatically versioned as a model attribute — no need for a separate `weave.StringPrompt`.

## Pattern 5: Retrieving Published Prompts

```python
# Load a specific version of a prompt
prompt = weave.ref("qa-system-prompt:latest").get()
formatted = prompt.format(variable="value")

# Load a specific version
prompt_v2 = weave.ref("qa-system-prompt:v2").get()
```

## When to Use Each Approach

| Scenario | Approach |
|----------|----------|
| Prompt is inside a `weave.Model` class | Keep as model attribute (auto-versioned) |
| Standalone prompt used across files | `weave.StringPrompt` + `weave.publish()` |
| Message array with system/user roles | `weave.MessagesPrompt` + `weave.publish()` |
| Simple one-off script | Leave as string (not worth the overhead) |
