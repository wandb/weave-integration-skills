"""RAG pipeline utilities for the W&B Q&A chatbot.

Candidates for @weave.op() tracing.
"""

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = "You are a helpful Weights & Biases support assistant. Answer questions about W&B products including Weave, Experiments, Artifacts, and Models."

# Simulated knowledge base about W&B
KNOWLEDGE_BASE = {
    "weave": [
        "W&B Weave is an observability toolkit for LLM and GenAI applications.",
        "Use weave.init('team/project') to start tracing your LLM app.",
        "Decorate functions with @weave.op() to trace inputs, outputs, and latency.",
        "weave.Model is a versioned, traceable model class based on Pydantic.",
        "weave.Evaluation lets you systematically test LLM outputs with custom scorers.",
    ],
    "experiments": [
        "W&B Experiments tracks ML training runs with wandb.init() and wandb.log().",
        "Use sweeps to automatically search hyperparameter spaces.",
        "Compare runs side-by-side in the W&B dashboard.",
        "Log metrics, images, tables, and custom charts during training.",
    ],
    "artifacts": [
        "W&B Artifacts version and track datasets, models, and other files.",
        "Use wandb.log_artifact() to save a new version of an artifact.",
        "Artifacts support lineage tracking — see which run produced which data.",
        "The Model Registry organizes production-ready models with aliases like 'latest' or 'production'.",
    ],
    "general": [
        "Weights & Biases (W&B) is an ML platform for experiment tracking, model management, and LLM observability.",
        "Sign up at wandb.ai and get your API key from wandb.ai/authorize.",
    ],
}


def classify_intent(question):
    """Classify the user's question into a W&B product category."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's question about Weights & Biases into one category. "
                    "Reply with ONLY one word: weave, experiments, artifacts, or general."
                ),
            },
            {"role": "user", "content": question},
        ],
        max_tokens=10,
    )
    return response.choices[0].message.content.strip().lower()


def retrieve_context(intent):
    """Retrieve relevant W&B documentation based on classified intent."""
    return KNOWLEDGE_BASE.get(intent, KNOWLEDGE_BASE["general"])


def generate_answer(question, context):
    """Generate an answer using the retrieved W&B documentation."""
    context_str = "\n- ".join(context)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\nUse the following context to answer:\n- {context_str}",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def rag_pipeline(question):
    """Full RAG pipeline: classify → retrieve → answer."""
    intent = classify_intent(question)
    context = retrieve_context(intent)
    answer = generate_answer(question, context)
    return answer
