# Codebase Analysis Guide

How to scan an existing project and identify Weave integration points.

## Step 0: Check for Existing Weave Usage

Before scanning for new integration points, check if Weave is already in use:

```
# Search for these patterns:
import weave
weave.init(
@weave.op
weave.Model
weave.Evaluation
weave.Dataset
weave.publish
```

**If Weave is already present (Evolve scenario)**:
- Do NOT add another `weave.init()` — verify the existing one is correct
- Do NOT re-convert classes that already extend `weave.Model`
- Focus on what's MISSING: untraced functions, unconverted classes, missing evaluations, etc.
- Report what's already integrated and what can be added

**If no Weave found (Fresh integration)**: proceed with full analysis below.

## Step 1: Find the Entrypoint

Search for the app's entry point — this is where `weave.init()` will be placed.

| Pattern | File indicators |
|---------|----------------|
| Script | `if __name__ == "__main__":` |
| FastAPI | `app = FastAPI()` or `uvicorn.run()` |
| Streamlit | `st.title()`, `st.write()` at top level |
| Flask | `app = Flask(__name__)` |
| Django | `manage.py`, `wsgi.py`, `asgi.py` |
| CLI tool | `@click.command()`, `argparse`, `typer.run()` |
| Notebook | First code cell |

### `weave.init()` Placement by Framework

| Framework | Where to place `weave.init()` |
|-----------|-------------------------------|
| Script | First line inside `main()` |
| FastAPI | Inside `lifespan` async context manager (not module level) |
| Streamlit | Top of script, before any `st.*` calls |
| Flask | After `app = Flask(__name__)` |
| Django | In `settings.py` or `wsgi.py`/`asgi.py` |
| CLI | First line inside the command function |
| Notebook | First code cell |
| Agent frameworks | Before any framework code — just `weave.init()` + auto-patching |

**Note**: OpenAI Agents SDK requires an extra step: `set_trace_processors([WeaveTracingProcessor()])` after `weave.init()`.

## Step 2: Detect LLM Provider Usage

Search for these import patterns to identify which LLM providers are used:

```
# Direct providers (auto-patched by Weave)
import openai / from openai import OpenAI, AsyncOpenAI
import anthropic / from anthropic import Anthropic, AsyncAnthropic
import litellm
import cohere
import mistralai
import groq
from google import generativeai / import google.generativeai
import boto3  # check for bedrock-runtime usage
from cerebras.cloud import sdk  # Cerebras
import together  # Together AI

# Agent frameworks (auto-patched by Weave)
from langchain import ... / from langchain_openai import ...
from llama_index import ... / from llama_index.core import ...
from crewai import ...
import dspy
import instructor
from pydantic_ai import ...
from autogen import ...
from smolagents import ...
from agents import ...  # OpenAI Agents SDK
from google.adk import ...  # Google ADK
from claude_agent_sdk import ...  # Claude Agent SDK
```

## Step 3: Identify ALL Functions to Trace

**Trace-first approach**: List every function that could be traced. Do not pre-filter or skip. The AI recommends defaults, the user decides what to exclude.

Scan for all functions and methods in the project, categorize them:

### LLM-calling functions (recommend: checked)
```python
def generate_response(prompt):          # → [x] @weave.op()
    return client.chat.completions.create(...)

async def ask_claude(question):         # → [x] @weave.op()
    return await anthropic_client.messages.create(...)
```

### Pipeline/orchestration functions (recommend: checked)
```python
def rag_pipeline(query):               # → [x] @weave.op()
    context = retrieve(query)
    return generate(query, context)

def process_document(doc):             # → [x] @weave.op()
    chunks = split(doc)
    embeddings = embed(chunks)
    return store(embeddings)
```

### Tool/helper functions (recommend: unchecked, but listed)
```python
def clean_text(text):                  # → [ ] @weave.op() — available if user wants
    return text.strip().lower()

def format_output(data):              # → [ ] @weave.op() — pure formatting
    return json.dumps(data, indent=2)
```

**Key**: List all of them in `weave_instrumentation.md` with checkboxes. AI pre-checks recommended ones, leaves others unchecked for the user to opt in.

## Step 4: Identify Model Classes

Look for classes that could become `weave.Model`:

```python
# Indicators of a Model candidate:
# 1. Has LLM configuration as attributes (model name, temperature, system prompt)
# 2. Has a method that calls an LLM (predict, generate, invoke, run, call, __call__)
# 3. Holds state that affects LLM behavior

class ChatBot:                         # → weave.Model candidate
    def __init__(self, model="gpt-4o", temperature=0.7):
        self.model = model
        self.temperature = temperature

    def generate(self, prompt):        # → rename to predict
        return client.chat.completions.create(...)
```

### Not a Model candidate
```python
# Pure utility class, data container, or class without LLM interaction
class TextSplitter:                    # skip
    def split(self, text): ...

class Config:                          # skip
    db_url: str
```

## Step 5: Detect Evaluation Logic

Search for existing test/eval/benchmark code:

| Pattern | What to look for |
|---------|-----------------|
| Test files | `test_*.py`, `*_test.py` with LLM assertions |
| Eval scripts | `eval*.py`, `benchmark*.py`, `score*.py` |
| Scoring functions | Functions that compare output vs expected |
| Test datasets | JSON/CSV files with input-output pairs |
| Loops with metrics | `for example in examples: ... accuracy += ...` |

## Step 6: Detect Hardcoded Prompts

Search for prompt strings that could be versioned:

```python
# System prompts
system_prompt = "You are a helpful assistant..."       # → weave.StringPrompt
SYSTEM_MSG = """You are an expert..."""                 # → weave.StringPrompt

# Message lists
messages = [
    {"role": "system", "content": "You are..."},       # → weave.MessagesPrompt
    {"role": "user", "content": f"Answer: {question}"},
]

# Template strings with variables
TEMPLATE = "Given {context}, answer {question}"        # → weave.StringPrompt with params
```

## Step 7: Create `weave_instrumentation.md`

Use `references/weave-instrumentation-template.md` to create `weave_instrumentation.md` in the project root.

Fill in all sections from the analysis. For the trace map:
- **`[x]`** = AI recommends tracing (LLM calls, pipelines, important methods)
- **`[ ]`** = available but not recommended by default (utilities, formatters)

Example trace tree:

```text
- [x] `api/rag.py` — `rag_pipeline()` — orchestration function
  - [x] `api/rag.py` — `retrieve_context()` — retrieval step
    - [x] OpenAI Embeddings API (auto-patched)
  - [x] `api/chat.py` — `generate_response()` — direct OpenAI call
    - [x] OpenAI Chat API (auto-patched)
  - [ ] `api/utils.py` — `format_output()` — pure formatting
- [x] `models/chatbot.py` — `ChatBot` — weave.Model candidate
```

The user reviews checkboxes and approves before any code changes.
