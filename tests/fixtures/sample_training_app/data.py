"""Data loading utilities for CIFAR-10."""

from torchvision import datasets, transforms
from torch.utils.data import DataLoader


def get_transforms():
    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(32, padding=4),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])
    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])
    return train_transform, val_transform


def get_train_loader(batch_size=64):
    train_transform, _ = get_transforms()
    train_dataset = datasets.CIFAR10(
        root="./data", train=True, download=True, transform=train_transform
    )
    return DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)


def get_val_loader(batch_size=64):
    _, val_transform = get_transforms()
    val_dataset = datasets.CIFAR10(
        root="./data", train=False, download=True, transform=val_transform
    )
    return DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
