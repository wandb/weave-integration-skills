# Sweeps

## Configuration

### Python Dict

```python
sweep_config = {
    "method": "bayes",  # "bayes" | "random" | "grid"
    "metric": {
        "name": "val/accuracy",
        "goal": "maximize",  # "maximize" | "minimize"
    },
    "parameters": {
        "learning_rate": {
            "distribution": "log_uniform_values",
            "min": 1e-5,
            "max": 1e-3,
        },
        "batch_size": {"values": [8, 16, 32]},
        "epochs": {"values": [3, 5, 7]},
        "warmup_ratio": {"values": [0.0, 0.05, 0.1, 0.2]},
        "weight_decay": {"values": [0.0, 0.01, 0.05]},
        "dropout": {
            "distribution": "uniform",
            "min": 0.1,
            "max": 0.5,
        },
    },
}
```

### YAML File

```yaml
method: bayes
metric:
  name: val/accuracy
  goal: maximize
parameters:
  learning_rate:
    distribution: log_uniform_values
    min: !!float 1e-5
    max: !!float 1e-3
  batch_size:
    values: [8, 16, 32]
  epochs:
    values: [3, 5, 7]
  warmup_ratio:
    values: [0.0, 0.05, 0.1, 0.2]
  weight_decay:
    values: [0.0, 0.01, 0.05]
```

## Parameter Distributions

| Distribution | Use Case | Keys |
|---|---|---|
| `values` | Discrete choices | `values: [a, b, c]` |
| `value` | Fixed value | `value: 42` |
| `uniform` | Continuous uniform | `min`, `max` |
| `log_uniform_values` | Log-scale (learning rates) | `min`, `max` |
| `q_log_uniform_values` | Quantized log-uniform | `min`, `max`, `q` |
| `normal` | Normal distribution | `mean`, `std` |
| `int_uniform` | Integer uniform | `min`, `max` |

## Early Termination

```yaml
early_terminate:
  type: hyperband
  min_iter: 3
  # or
  max_iter: 27
  s: 2
  eta: 3
```

## Nested Parameters

```python
sweep_config = {
    "method": "grid",
    "parameters": {
        "optimizer": {"values": ["adam", "sgd"]},
        "optimizer_config": {
            "parameters": {
                "momentum": {"distribution": "uniform", "min": 0.0, "max": 0.9},
                "weight_decay": {"values": [0.0001, 0.001]},
            }
        },
    },
}
```

## Create and Run Sweep

```python
import wandb

# From Python dict
sweep_id = wandb.sweep(sweep_config, project="my-project", entity="my-team")

# From YAML file
sweep_id = wandb.sweep(sweep="configs/sweep_config.yaml", project="my-project")

# Run agent
wandb.agent(sweep_id, function=train_fn, count=20)
```

## Training Function for Sweeps

```python
def train_fn():
    with wandb.init() as run:
        config = wandb.config

        model = build_model(config)
        optimizer = build_optimizer(config)

        for epoch in range(config.epochs):
            train_loss = train_epoch(model, optimizer)
            val_acc = evaluate(model)

            wandb.log({
                "train/loss": train_loss,
                "val/accuracy": val_acc,
                "epoch": epoch,
            })
```

## Analyze Sweep Results

```python
api = wandb.Api()

# Get best run from sweep
runs = api.runs(
    f"{entity}/{project}",
    filters={"sweep": sweep_id},
    order="-summary_metrics.val/accuracy",
)

best_run = runs[0]
print(f"Best run: {best_run.name}")
print(f"Accuracy: {best_run.summary.get('val/accuracy')}")
print(f"Config: {best_run.config}")

# Get best model artifact
for artifact in best_run.logged_artifacts():
    if artifact.type == "model":
        best_model = artifact
        break
```

## Manage Sweeps

```bash
# Pause sweep
wandb sweep --pause <entity>/<project>/<sweep_id>

# Resume sweep
wandb sweep --resume <entity>/<project>/<sweep_id>

# Cancel sweep
wandb sweep --cancel <entity>/<project>/<sweep_id>
```

## CLI Sweep

```bash
# Create sweep from YAML
wandb sweep configs/sweep_config.yaml --project my-project

# Start agent
wandb agent <entity>/<project>/<sweep_id>

# Start agent with count
wandb agent --count 10 <entity>/<project>/<sweep_id>
```
