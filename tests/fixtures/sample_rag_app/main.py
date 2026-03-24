"""W&B Q&A Chatbot — sample app for testing weave-integration skill.

This app intentionally does NOT use Weave.
Test with: "내 앱에 Weave 적용해줘" or "Add Weave to my app"

Expected integration results:
- weave.init() added here
- @weave.op() added to chat.py functions (classify_intent, retrieve_context, generate_answer, rag_pipeline)
- ChatBot converted to weave.Model (model→model_name, chat→predict)
- eval_test.py converted to weave.Evaluation
"""

from models import ChatBot


def main():
    bot = ChatBot(model="gpt-4o-mini", temperature=0.5)

    questions = [
        "How do I trace my LLM app with Weave?",
        "How do I log metrics during training?",
        "How do I version my datasets with W&B?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer = bot.chat(q)
        print(f"A: {answer}")

    print(f"\n--- Chat history: {len(bot.history)} messages ---")


if __name__ == "__main__":
    main()
