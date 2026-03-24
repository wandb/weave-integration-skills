# Codebase Analysis Guide

How to scan an existing project and identify Weave integration points.

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
```

## Step 3: Identify Functions to Trace

Look for functions that should get `@weave.op()`:

### High priority — functions that call LLMs directly
```python
# Pattern: function body contains LLM API calls
def generate_response(prompt):          # → @weave.op()
    return client.chat.completions.create(...)

async def ask_claude(question):         # → @weave.op()
    return await anthropic_client.messages.create(...)
```

### Medium priority — pipeline/processing functions
```python
# Pattern: orchestration functions that combine multiple steps
def rag_pipeline(query):               # → @weave.op()
    context = retrieve(query)
    return generate(query, context)

def process_document(doc):             # → @weave.op()
    chunks = split(doc)
    embeddings = embed(chunks)
    return store(embeddings)
```

### Low priority — utility functions
```python
# Pattern: pure data transforms (usually skip unless full tracing desired)
def clean_text(text):                  # skip unless user wants full tracing
    return text.strip().lower()
```

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

## Step 7: Present Analysis Results

Format your findings as a structured summary:

```
## Codebase Analysis Results

**Entrypoint**: `app.py` (FastAPI app)
**LLM Providers**: OpenAI (auto-patched), Anthropic (auto-patched)
**Framework**: FastAPI

### Functions to trace (N found)
| File | Line | Function | Priority | Reason |
|------|------|----------|----------|--------|
| `api/chat.py` | 15 | `generate_response()` | High | Direct OpenAI call |
| `api/rag.py` | 32 | `rag_pipeline()` | High | Orchestration function |
| `api/rag.py` | 10 | `retrieve_context()` | Medium | Retrieval step |

### Model candidates (N found)
| File | Line | Class | Main method |
|------|------|-------|-------------|
| `models/chatbot.py` | 8 | `ChatBot` | `generate()` → `predict()` |

### Evaluation candidates (N found)
| File | Description |
|------|-------------|
| `tests/test_quality.py` | Has input-output pairs + scoring |

### Prompts to version (N found)
| File | Line | Current form |
|------|------|-------------|
| `models/chatbot.py` | 5 | `SYSTEM_PROMPT = "You are..."` |
```
