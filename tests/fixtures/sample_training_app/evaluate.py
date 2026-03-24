"""Model evaluation script — candidate for wandb Table logging and leaderboard.

This script evaluates a trained model and prints results.
Test with: "평가 결과를 wandb 테이블로 로깅해줘" or "Log evaluation results as a wandb table"

Expected integration results:
- wandb.init() with job_type="evaluation"
- Results logged as wandb.Table
- Predictions with images logged for visual inspection
- run.summary set for leaderboard comparison
"""

import torch
from model import SimpleCNN
from data import get_val_loader

CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]


def evaluate_model(model_path="best_model.pth", num_classes=10):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = SimpleCNN(num_classes=num_classes).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    val_loader = get_val_loader(batch_size=64)

    correct = 0
    total = 0
    class_correct = [0] * num_classes
    class_total = [0] * num_classes
    predictions = []

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)

            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            for i in range(labels.size(0)):
                label = labels[i].item()
                class_correct[label] += (predicted[i] == label).item()
                class_total[label] += 1

            # Collect first batch predictions for inspection
            if len(predictions) < 100:
                for i in range(min(labels.size(0), 100 - len(predictions))):
                    predictions.append({
                        "true_label": CLASSES[labels[i].item()],
                        "predicted_label": CLASSES[predicted[i].item()],
                        "correct": predicted[i].item() == labels[i].item(),
                    })

    overall_accuracy = correct / total
    print(f"Overall Accuracy: {overall_accuracy:.4f}")
    print(f"\nPer-class Accuracy:")
    for i in range(num_classes):
        acc = class_correct[i] / class_total[i] if class_total[i] > 0 else 0
        print(f"  {CLASSES[i]:>12s}: {acc:.4f} ({class_correct[i]}/{class_total[i]})")

    return overall_accuracy, predictions


if __name__ == "__main__":
    evaluate_model()
