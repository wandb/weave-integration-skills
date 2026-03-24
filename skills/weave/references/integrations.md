# Weave Integrations Reference

Provider-specific and framework-specific integration patterns for W&B Weave.

## OpenAI

### Basic (auto-patched — no extra code needed)

```python
import weave
from openai import OpenAI

weave.init('my-team/openai-project')
client = OpenAI()

# Automatically traced: inputs, outputs, tokens, cost, latency
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### With custom function tracing

```python
@weave.op()
def extract_entities(text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extract entities as JSON."},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
```

### Tool use

Weave automatically captures tool calls and results:

```python
@weave.op()
def chat_with_tools(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}],
        tools=[{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"]
                }
            }
        }],
    )
    return response.choices[0].message
```

### Streaming

Weave handles streaming transparently. Usage captured from final chunk:

```python
@weave.op()
def stream_response(prompt: str) -> str:
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    return full_response
```

## Anthropic

### Basic (auto-patched)

```python
import weave
import os
from anthropic import Anthropic

weave.init('my-team/anthropic-project')
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Automatically traced
message = client.messages.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a joke"}],
    model="claude-sonnet-4-20250514",
)
```

### Structured with weave.Model

```python
class ClaudeApp(weave.Model):
    model: str = "claude-sonnet-4-20250514"
    system_prompt: str = "You are a helpful assistant."
    max_tokens: int = 1024

    @weave.op()
    def predict(self, user_input: str) -> str:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": user_input}],
            system=self.system_prompt,
        )
        return message.content[0].text
```

### Tool use

Weave automatically tracks Anthropic tool calls:

```python
@weave.op()
def chat_with_tools(user_message: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}],
        tools=[{
            "name": "get_weather",
            "description": "Get weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        }],
    )
    return message
```

## LiteLLM

Multi-provider gateway. Auto-patched by Weave:

```python
import weave
import litellm

weave.init('my-team/litellm-project')

@weave.op()
def ask_any_model(model: str, question: str) -> str:
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content

# Route to different providers
ask_any_model("gpt-4o", "What is 2+2?")
ask_any_model("anthropic/claude-sonnet-4-20250514", "What is 2+2?")
ask_any_model("gemini/gemini-pro", "What is 2+2?")
```

## Agent Frameworks

### OpenAI Agents SDK

```python
import weave
import asyncio
from agents import Agent, Runner, function_tool, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

weave.init('my-team/openai-agents')
set_trace_processors([WeaveTracingProcessor()])

@function_tool
def get_weather(city: str) -> str:
    return f"Sunny, 22°C in {city}"

agent = Agent(
    name="Weather Assistant",
    instructions="You help users check the weather.",
    tools=[get_weather],
)

async def main():
    result = await Runner.run(agent, input="What's the weather in Seoul?")
    print(result.final_output)

asyncio.run(main())
```

### Smolagents

Just `weave.init()` — traces captured automatically:

```python
import weave
from smolagents import DuckDuckGoSearchTool, OpenAIServerModel, ToolCallingAgent

weave.init(project_name="smolagents")
model = OpenAIServerModel(model_id="gpt-4o")
agent = ToolCallingAgent(tools=[DuckDuckGoSearchTool()], model=model)
answer = agent.run("What is W&B Weave?")
```

### LangChain

Auto-patched after `weave.init()`:

```python
import weave
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

weave.init('my-team/langchain-project')
chat = ChatOpenAI(model="gpt-4o")
result = chat.invoke([HumanMessage(content="Hello!")])
```

### MCP (Model Context Protocol)

Weave auto-logs MCP agent traces:

```python
import weave
weave.init('my-team/mcp-project')
# MCP tool calls automatically captured in the trace tree
```

### LlamaIndex

Auto-patched after `weave.init()`:

```python
import weave
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

weave.init('my-team/llamaindex-project')

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is the meaning of life?")
```

### CrewAI

Auto-patched after `weave.init()`:

```python
import weave
from crewai import Agent, Task, Crew

weave.init('my-team/crewai-project')

researcher = Agent(
    role="Researcher",
    goal="Find the latest AI trends",
    backstory="You are an expert AI researcher.",
)
task = Task(
    description="Research the latest trends in AI agents.",
    expected_output="A summary of key trends.",
    agent=researcher,
)
crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

### DSPy

Auto-patched after `weave.init()`:

```python
import weave
import dspy

weave.init('my-team/dspy-project')

lm = dspy.LM("openai/gpt-4o")
dspy.configure(lm=lm)

classify = dspy.Predict("sentence -> sentiment")
result = classify(sentence="This movie is amazing!")
```

### Instructor

Auto-patched after `weave.init()`:

```python
import weave
import instructor
from openai import OpenAI
from pydantic import BaseModel

weave.init('my-team/instructor-project')

client = instructor.from_openai(OpenAI())

class UserInfo(BaseModel):
    name: str
    age: int

user = client.chat.completions.create(
    model="gpt-4o",
    response_model=UserInfo,
    messages=[{"role": "user", "content": "John is 30 years old"}],
)
```

### PydanticAI

Auto-patched after `weave.init()`:

```python
import weave
from pydantic_ai import Agent

weave.init('my-team/pydanticai-project')

agent = Agent("openai:gpt-4o", system_prompt="You are a helpful assistant.")
result = agent.run_sync("What is the capital of France?")
print(result.output)
```

### Google Agent Development Kit (ADK)

Auto-patched after `weave.init()`:

```python
import weave
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

weave.init('my-team/google-adk-project')

agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    instruction="You are a friendly greeting agent.",
)
```

### AutoGen

Auto-patched after `weave.init()`:

```python
import weave
from autogen import AssistantAgent, UserProxyAgent

weave.init('my-team/autogen-project')

assistant = AssistantAgent("assistant", llm_config={"model": "gpt-4o"})
user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)
user_proxy.initiate_chat(assistant, message="What is 2+2?")
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `WANDB_API_KEY` | W&B authentication (required) |
| `WANDB_BASE_URL` | Custom W&B server URL (dedicated/self-hosted) |
| `WEAVE_DISABLED` | Set `true` to disable tracing |
| `WEAVE_PRINT_CALL_LINK` | Set `false` to suppress trace URL output |
| `OPENAI_API_KEY` | OpenAI provider key |
| `ANTHROPIC_API_KEY` | Anthropic provider key |

## Supported Extras (pip install)

Install provider-specific extras for optimal integration:

```bash
pip install weave[openai]
pip install weave[anthropic]
pip install weave[litellm]
pip install weave[langchain]
pip install weave[llamaindex]
pip install weave[scorers]        # Built-in scorers with LiteLLM support
pip install weave[openai-agents]
pip install weave[smolagents]
pip install weave[crewai]
pip install weave[dspy]
pip install weave[instructor]
pip install weave[mcp]
```

Full list of extras: `anthropic`, `autogen`, `bedrock`, `cerebras`, `cohere`, `crewai`, `dspy`, `google-genai`, `groq`, `huggingface`, `instructor`, `langchain`, `litellm`, `llamaindex`, `mcp`, `mistral`, `modal`, `openai`, `openai-agents`, `smolagents`, `vertexai`
