# Tracing Integration Reference

How to add `@weave.op()` to existing code with minimal changes.

For `weave.init()` placement by framework, see `framework-specific.md`.

## Adding `@weave.op()` to Functions

### Rule 1: Add decorator above existing decorators

```python
# BEFORE
@retry(max_retries=3)
def call_llm(prompt):
    return client.chat.completions.create(...)

# AFTER
@weave.op()           # weave.op goes on top
@retry(max_retries=3)
def call_llm(prompt: str) -> str:  # Add type hints
    return client.chat.completions.create(...)
```

### Rule 2: Add type hints to parameters and return type

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

### Rule 3: Handle async functions

```python
# BEFORE
async def ask_claude(question):
    message = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text

# AFTER — @weave.op() works with async too, no changes needed
@weave.op()
async def ask_claude(question: str) -> str:
    message = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text
```

### Rule 4: Class methods

```python
# BEFORE
class RAGPipeline:
    def retrieve(self, query):
        return self.vector_store.search(query)

    def generate(self, query, context):
        return client.chat.completions.create(...)

    def run(self, query):
        context = self.retrieve(query)
        return self.generate(query, context)

# AFTER — decorate methods that should appear in the trace tree
class RAGPipeline:
    @weave.op()
    def retrieve(self, query: str) -> list[str]:
        return self.vector_store.search(query)

    @weave.op()
    def generate(self, query: str, context: list[str]) -> str:
        return client.chat.completions.create(...)

    @weave.op()
    def run(self, query: str) -> str:
        context = self.retrieve(query)
        return self.generate(query, context)
```

### Rule 5: Add `import weave` to each modified file

```python
# Every file that uses @weave.op() needs the import
import weave  # Add at top of file with other imports
```

## Auto-Patching Reminder

After `weave.init()`, LLM provider calls are **automatically traced** — no decorators needed on provider calls themselves. `@weave.op()` is for **your custom functions** to create a trace tree around the auto-patched calls.

Auto-patched providers: OpenAI, Anthropic, LiteLLM, Google GenAI, Cohere, Mistral, Groq, Cerebras, Together, Bedrock

## What NOT to Decorate

- Pure utility functions (string formatting, data conversion) — unless the user wants full tracing
- Functions that don't relate to the LLM pipeline
- Functions called thousands of times per second (use `tracing_sample_rate` if needed)
- Third-party library functions (use auto-patching instead)

## Common Integration Patterns

### Pattern: RAG Pipeline

```python
# BEFORE
def answer_question(query):
    docs = search_docs(query)
    context = format_context(docs)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content
```

```python
# AFTER — trace the pipeline and its steps
@weave.op()
def search_docs(query: str) -> list[dict]:
    # existing retrieval logic
    ...

@weave.op()
def answer_question(query: str) -> str:
    docs = search_docs(query)         # child span
    context = format_context(docs)    # not traced (utility)
    response = client.chat.completions.create(  # auto-patched child span
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content
```

### Pattern: Multi-Agent System

```python
# BEFORE
def run_agents(task):
    plan = planner.plan(task)
    for step in plan:
        result = executor.execute(step)
    return summarizer.summarize(results)
```

```python
# AFTER
@weave.op()
def run_agents(task: str) -> str:
    plan = planner.plan(task)         # trace if planner methods are decorated
    for step in plan:
        result = executor.execute(step)
    return summarizer.summarize(results)
```
