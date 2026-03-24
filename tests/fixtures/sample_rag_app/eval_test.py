"""Evaluation script for the W&B Q&A chatbot.

Candidate for weave.Evaluation conversion:
- test_cases → weave.Dataset
- score logic → @weave.op() scorer function
- loop → weave.Evaluation.evaluate()
"""

from models import ChatBot


def run_eval():
    """Evaluate the chatbot's answer quality on W&B questions."""
    bot = ChatBot()

    test_cases = [
        {"question": "How do I trace my LLM app with Weave?", "expected": "weave.init"},
        {"question": "How do I track experiments in W&B?", "expected": "wandb.init"},
        {"question": "How do I version my datasets?", "expected": "artifact"},
    ]

    correct = 0
    total = len(test_cases)

    for case in test_cases:
        output = bot.chat(case["question"])
        if case["expected"].lower() in output.lower():
            correct += 1
            print(f"  PASS: {case['question']}")
        else:
            print(f"  FAIL: {case['question']}")

    print(f"\nAccuracy: {correct}/{total} = {correct/total:.0%}")


if __name__ == "__main__":
    run_eval()
