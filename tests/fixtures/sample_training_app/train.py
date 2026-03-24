"""Image classifier training script — sample app for testing models skill.

This app intentionally does NOT use W&B.
Test with: "내 학습 스크립트에 wandb 트래킹 추가해줘" or "Add wandb tracking to my training script"

Expected integration results:
- wandb.init() added with project, config, tags
- wandb.log() added for train/val metrics
- run.summary set for best metrics
- Model saved as wandb.Artifact
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from model import SimpleCNN
from data import get_train_loader, get_val_loader


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    avg_loss = total_loss / len(loader)
    accuracy = correct / total
    return avg_loss, accuracy


def validate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    avg_loss = total_loss / len(loader)
    accuracy = correct / total
    return avg_loss, accuracy


def main():
    # Hyperparameters
    config = {
        "learning_rate": 1e-3,
        "epochs": 10,
        "batch_size": 64,
        "optimizer": "adam",
        "num_classes": 10,
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Data
    train_loader = get_train_loader(batch_size=config["batch_size"])
    val_loader = get_val_loader(batch_size=config["batch_size"])

    # Model
    model = SimpleCNN(num_classes=config["num_classes"]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])

    best_val_acc = 0.0

    for epoch in range(config["epochs"]):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        print(
            f"Epoch {epoch+1}/{config['epochs']} — "
            f"train_loss: {train_loss:.4f}, train_acc: {train_acc:.4f}, "
            f"val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_model.pth")
            print(f"  → New best model saved (val_acc: {val_acc:.4f})")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.4f}")


if __name__ == "__main__":
    main()
