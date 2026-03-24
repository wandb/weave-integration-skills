# Framework-Specific Integration Reference

Integration recipes for common frameworks and app architectures.

## Web Frameworks

### FastAPI

```python
# BEFORE
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await generate(request.message)
    return {"response": response}
```

```python
# AFTER
import weave
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    weave.init('team/project')  # Init during app startup
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
@weave.op()                         # Trace the endpoint
async def chat(request: ChatRequest) -> dict:
    response = await generate(request.message)
    return {"response": response}
```

**Notes**:
- Place `weave.init()` in the `lifespan` context manager (not at module level)
- Decorate endpoint handlers with `@weave.op()` — put it below `@app.post/get/put`
- Internal functions called by endpoints can also be decorated

### Streamlit

```python
# BEFORE
import streamlit as st

st.title("AI Chat")
user_input = st.text_input("Message:")
if user_input:
    response = generate(user_input)
    st.write(response)
```

```python
# AFTER
import weave
import streamlit as st

weave.init('team/project')  # Add at very top, before any Streamlit calls

st.title("AI Chat")
user_input = st.text_input("Message:")
if user_input:
    response = generate(user_input)
    st.write(response)
```

**Notes**:
- Place `weave.init()` at the top of the script, before `st.title()` etc.
- Streamlit reruns the entire script on each interaction — `weave.init()` handles repeated calls gracefully
- Decorate your generation functions with `@weave.op()`

### Flask

```python
# BEFORE
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    response = generate(data["message"])
    return jsonify({"response": response})
```

```python
# AFTER
import weave
from flask import Flask, request, jsonify

app = Flask(__name__)
weave.init('team/project')  # Add after app creation

@app.route("/chat", methods=["POST"])
@weave.op()                 # Below @app.route
def chat() -> dict:
    data = request.json
    response = generate(data["message"])
    return jsonify({"response": response})
```

### Django

```python
# In settings.py or wsgi.py/asgi.py
import weave
weave.init('team/project')
```

```python
# In views.py
import weave

@weave.op()
def chat_view(request) -> dict:
    ...
```

## AI Agent Frameworks

All major agent frameworks are **auto-patched** — just add `weave.init()` at the top.

### LangChain

```python
# BEFORE
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o")
chain = prompt | llm
result = chain.invoke({"question": "Hello"})
```

```python
# AFTER — just add 2 lines
import weave                                    # Add
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

weave.init('team/project')                      # Add

llm = ChatOpenAI(model="gpt-4o")
chain = prompt | llm
result = chain.invoke({"question": "Hello"})    # Auto-traced
```

### LlamaIndex

```python
# BEFORE
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is...?")
```

```python
# AFTER — just add 2 lines
import weave
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

weave.init('team/project')

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is...?")    # Auto-traced
```

### CrewAI

```python
# BEFORE
from crewai import Agent, Task, Crew

agent = Agent(role="Researcher", goal="...", backstory="...")
task = Task(description="...", agent=agent, expected_output="...")
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

```python
# AFTER — just add 2 lines
import weave
from crewai import Agent, Task, Crew

weave.init('team/project')

agent = Agent(role="Researcher", goal="...", backstory="...")
task = Task(description="...", agent=agent, expected_output="...")
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()    # Auto-traced
```

### DSPy

```python
# BEFORE
import dspy
lm = dspy.LM("openai/gpt-4o")
dspy.configure(lm=lm)
```

```python
# AFTER — just add 2 lines
import weave
import dspy

weave.init('team/project')

lm = dspy.LM("openai/gpt-4o")
dspy.configure(lm=lm)
```

### OpenAI Agents SDK

This framework requires an **extra step** beyond `weave.init()`:

```python
# BEFORE
from agents import Agent, Runner

agent = Agent(name="My Agent", instructions="You are helpful.")
result = await Runner.run(agent, input="Hello")
```

```python
# AFTER — requires WeaveTracingProcessor
import weave
from agents import Agent, Runner, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

weave.init('team/project')
set_trace_processors([WeaveTracingProcessor()])   # Extra step required

agent = Agent(name="My Agent", instructions="You are helpful.")
result = await Runner.run(agent, input="Hello")
```

### PydanticAI / Instructor / AutoGen / Smolagents / Google ADK

All follow the same pattern — just add `weave.init()`:

```python
import weave
weave.init('team/project')
# ... existing framework code works as-is, auto-traced
```

## CLI Applications

```python
# BEFORE
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    args = parser.parse_args()
    result = generate(args.query)
    print(result)

if __name__ == "__main__":
    main()
```

```python
# AFTER
import weave
import argparse

def main():
    weave.init('team/project')       # First line in main
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    args = parser.parse_args()
    result = generate(args.query)
    print(result)

if __name__ == "__main__":
    main()
```

## Jupyter Notebooks

```python
# Cell 1 — add at the top of the notebook
import weave
weave.init('team/project')

# Remaining cells work as-is — LLM calls are auto-traced
```

## Installation Extras

Install the appropriate extras for your framework:

```bash
pip install weave                    # Base
pip install weave[openai]            # OpenAI
pip install weave[anthropic]         # Anthropic
pip install weave[litellm]           # LiteLLM
pip install weave[langchain]         # LangChain
pip install weave[llamaindex]        # LlamaIndex
pip install weave[crewai]            # CrewAI
pip install weave[dspy]              # DSPy
pip install weave[openai-agents]     # OpenAI Agents SDK
pip install weave[instructor]        # Instructor
pip install weave[smolagents]        # Smolagents
pip install weave[mcp]               # MCP
```
