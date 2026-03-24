"""W&B Q&A Chatbot — candidate for weave.Model conversion.

The ChatBot class wraps the RAG pipeline from chat.py and adds
conversation history tracking.

Expected changes:
- Inherit from weave.Model
- Rename 'model' → 'model_name' (Pydantic conflict)
- Remove __init__, use class-level type annotations
- Rename 'chat' → 'predict'
- Add @weave.op() to predict
"""

from chat import rag_pipeline


class ChatBot:
    """W&B Q&A chatbot powered by RAG pipeline."""

    def __init__(self, model="gpt-4o-mini", temperature=0.7):
        self.model = model
        self.temperature = temperature
        self.system_prompt = "You are a helpful Weights & Biases support assistant."
        self.history = []

    def chat(self, message):
        """Answer a W&B question using the RAG pipeline."""
        answer = rag_pipeline(message)
        self.history.append({"question": message, "answer": answer})
        return answer
