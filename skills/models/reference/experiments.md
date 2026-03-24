# Experiments

## wandb.init()

```python
import wandb

with wandb.init(
    project="my-project",          # required: W&B project name
    entity="my-team",              # team or user (default: WANDB_ENTITY or default entity)
    job_type="training",           # categorize runs: "training", "evaluation", "data-preparation"
    tags=["vit", "fine-tune"],     # filterable labels
    config={                       # hyperparameters and settings
        "learning_rate": 1e-4,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "vit-base-patch16-224",
    },
    name="baseline-training",      # display name (auto-generated if omitted)
    notes="First baseline run",    # markdown-supported description
    group="experiment-group",      # group related runs
    resume="allow",                # "allow" | "must" | "never" | "auto" | run_id
    settings=wandb.Settings(
        job_source="repo",         # for Launch jobs
    ),
) as run:
    # training code
    pass
```

## wandb.log()

```python
# Scalars
run.log({"train/loss": 0.5, "train/accuracy": 0.85})
run.log({"val/loss": 0.3, "val/accuracy": 0.92})

# Step control
run.log({"loss": 0.5}, step=100)
run.log({"loss": 0.3}, step=200, commit=True)

# Images
run.log({"examples": wandb.Image(pil_image, caption="sample")})
run.log({"confusion_matrix": wandb.Image(matplotlib_fig)})

# Multiple images
images = [wandb.Image(img, caption=f"pred: {pred}") for img, pred in zip(imgs, preds)]
run.log({"predictions": images})

# Tables
table = wandb.Table(columns=["input", "output", "label"])
table.add_data("hello", "positive", "positive")
run.log({"results": table})

# Histograms
run.log({"gradients": wandb.Histogram(grad_array)})

# Plotly / matplotlib
run.log({"chart": wandb.Plotly(plotly_fig)})
run.log({"plot": wandb.Image(plt)})  # matplotlib via Image
```

## wandb.define_metric()
```python
# Custom x-axis: val metrics plotted against epoch instead of global step
wandb.define_metric("epoch")
wandb.define_metric("val/*", step_metric="epoch")

for epoch in range(num_epochs):
    train_loss = train_one_epoch()
    wandb.log({"train/loss": train_loss})  # plotted vs default step

    val_metrics = evaluate()
    wandb.log({
        "epoch": epoch,
        "val/accuracy": val_metrics["accuracy"],
        "val/loss": val_metrics["loss"],
    })  # val/* plotted vs epoch
```

Call `define_metric()` right after `wandb.init()`, before the first `wandb.log()` call.

**Key patterns:**
- `wandb.define_metric("val/*", step_metric="epoch")` — plot val metrics against epoch
- `wandb.define_metric("train/*", summary="min")` — auto-record min value in summary
- `wandb.define_metric("eval/*", summary="max")` — auto-record max value in summary
- `wandb.define_metric("*", step_metric="global_step")` — unify x-axis to global_step for all metrics

## run.summary

```python
# Set summary metrics directly (appear in runs table)
run.summary["best_val_accuracy"] = 0.95
run.summary["best_epoch"] = 7
run.summary["eval_macro_f1"] = 0.91

# Update multiple
run.summary.update({"metric_a": 1.0, "metric_b": 2.0})
```

## run.config

```python
# Set config after init
run.config.learning_rate = 0.001
run.config.update({"dropout": 0.5, "hidden_size": 256})

# Access config
lr = run.config["learning_rate"]
# or
lr = wandb.config.learning_rate  # global access
```

## HuggingFace Trainer Integration

```python
import os
os.environ["WANDB_PROJECT"] = "my-hf-project"

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",              # enables W&B logging
    run_name="vit-fine-tune",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics,
)

trainer.train()
```

## PyTorch Integration

```python
import wandb
import torch

wandb.init(project="pytorch-project", config={"lr": 0.01, "epochs": 20})

model = MyModel()
wandb.watch(model, log="all", log_freq=100)  # log gradients and parameters

optimizer = torch.optim.Adam(model.parameters(), lr=wandb.config.lr)

for epoch in range(wandb.config.epochs):
    for batch in dataloader:
        loss = train_step(model, batch, optimizer)
        wandb.log({"train/loss": loss.item()})

    val_metrics = evaluate(model, val_loader)
    wandb.log({"val/accuracy": val_metrics["accuracy"], "epoch": epoch})

wandb.finish()
```

## Keras Integration

```python
import wandb
from wandb.integration.keras import WandbMetricsLogger, WandbModelCheckpoint

wandb.init(project="keras-project", config={"epochs": 10})

model.fit(
    x_train, y_train,
    epochs=wandb.config.epochs,
    callbacks=[
        WandbMetricsLogger(),
        WandbModelCheckpoint("models/"),
    ],
)

wandb.finish()
```

## Environment Variables

| Variable | Description |
|---|---|
| `WANDB_API_KEY` | API key for authentication |
| `WANDB_PROJECT` | Default project name |
| `WANDB_ENTITY` | Default entity (team or user) |
| `WANDB_DIR` | Local directory for run data |
| `WANDB_MODE` | `online` (default), `offline`, `disabled` |
| `WANDB_TAGS` | Comma-separated tags |
| `WANDB_NOTES` | Run notes |
| `WANDB_NAME` | Run display name |
| `WANDB_RUN_GROUP` | Run group |
| `WANDB_JOB_TYPE` | Job type |
| `WANDB_SILENT` | `true` to suppress output |
| `WANDB_CONSOLE` | `off` to disable console capture |
| `WANDB_LOG_MODEL` | `true` to auto-log model checkpoints |

## Finish and Cleanup

```python
# Context manager (preferred)
with wandb.init() as run:
    # automatically calls finish

# Manual
run = wandb.init()
# ... training ...
wandb.finish()  # or run.finish()
```

## Log Code for Reproducibility

```python
run.log_code()  # logs current directory
run.log_code("./src")  # logs specific directory
```
