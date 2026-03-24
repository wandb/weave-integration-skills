"""Hyperparameter sweep configuration — candidate for wandb.sweep integration.

This file defines a sweep config as a plain dict.
Test with: "하이퍼파라미터 스윕 설정해줘" or "Set up a hyperparameter sweep"

Expected integration results:
- wandb.sweep() called with this config
- wandb.agent() launched with a train function
- sweep_config integrated with wandb
"""

sweep_config = {
    "method": "bayes",
    "metric": {"name": "val_accuracy", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"min": 1e-5, "max": 1e-2},
        "batch_size": {"values": [32, 64, 128]},
        "optimizer": {"values": ["adam", "sgd", "adamw"]},
        "epochs": {"value": 10},
    },
}

if __name__ == "__main__":
    import json
    print(json.dumps(sweep_config, indent=2))
