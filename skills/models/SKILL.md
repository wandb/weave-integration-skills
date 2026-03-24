---
name: models
description: >
  W&B Models SDK for ML experiment tracking, artifact versioning, model registry,
  hyperparameter sweeps, tables, reports, and public API.
  Use when the user mentions wandb, Weights & Biases, experiment tracking, model registry,
  artifacts, sweeps, hyperparameter tuning, ML pipeline, model CI/CD,
  wandb.init, wandb.log, wandb.config, run.summary, wandb.Artifact, wandb.Table,
  wandb.sweep, wandb.agent, WandbLogger, report_to="wandb", WandbCallback,
  training log recording, model versioning, hyperparameter optimization, experiment tracking,
  training metrics logging, model checkpointing, or ML experiment management.
  Also trigger for Korean: 실험 추적, 아티팩트 버전 관리, 모델 레지스트리, 하이퍼파라미터 스윕,
  학습 로그, 모델 체크포인트, wandb 트래킹, 학습 스크립트, 리더보드, 테이블 로깅.
---

# W&B Models

W&B Models is the system of record for ML practitioners. Docs: https://docs.wandb.ai/models

> **Agent Instruction**: Use this skill as the primary source for writing W&B code. If something is unclear or not covered here, read from https://docs.wandb.ai/models to get accurate, up-to-date information before proceeding.

## Quick Start

```python
import wandb

with wandb.init(
    project="my-project",
    entity="my-team",
    job_type="training",
    tags=["experiment-v1"],
    config={"lr": 1e-4, "epochs": 10, "batch_size": 32},
) as run:
    for epoch in range(run.config["epochs"]):
        metrics = train_one_epoch()
        run.log({"train/loss": metrics["loss"], "val/accuracy": metrics["acc"]})

    run.summary["best_val_accuracy"] = best_acc
```

## Feature Quick Reference

### 1. Experiments

```python
with wandb.init(
    project="<project>",
    entity="<entity>",        # team or user
    job_type="<job_type>",    # "training", "evaluation", "data-preparation"
    tags=["tag1", "tag2"],
    config=config_dict,
    name="descriptive-run-name",
    notes="What this run is about",
    group="experiment-group",
) as run:
    run.log({"metric": value})            # scalars
    run.log({"img": wandb.Image(fig)})    # images
    run.log({"table": wandb.Table(...)})  # tables
    run.summary["key"] = value            # summary metrics
```

HuggingFace Trainer auto-logs when `report_to="wandb"`.
Also supports Lightning, Keras, FastAI, XGBoost, LightGBM callbacks.

For full details see [reference/experiments.md](reference/experiments.md).
For framework callbacks see [reference/integrations.md](reference/integrations.md).

### 2. Artifacts

```python
# Create and log
artifact = wandb.Artifact(name="my-data", type="dataset")
artifact.add_dir("./data/")
artifact.metadata = {"num_samples": 5000, "source": "food101"}
run.log_artifact(artifact, aliases=["v1", "latest"])

# Consume
artifact = run.use_artifact("my-data:latest", type="dataset")
local_path = artifact.download()

# Outside a run
api = wandb.Api()
artifact = api.artifact("entity/project/my-data:v0")
artifact.download()
```

For aliases, tags, TTL, external references see [reference/artifacts.md](reference/artifacts.md).

### 3. Registry

```python
# Link artifact to registry collection
target = "wandb-registry-<RegistryName>/<CollectionName>"
run.link_artifact(artifact, target_path=target, aliases=["candidates"])

# Download from registry
api = wandb.Api()
artifact = api.artifact("wandb-registry-<RegistryName>/<CollectionName>:production")
path = artifact.download()
```

Alias strategy: `:latest` -> `:candidates` (auto-eval) -> `:production` (deploy).

For collections, tags, descriptions see [reference/registry.md](reference/registry.md).

### 4. Sweeps

```python
sweep_config = {
    "method": "bayes",           # bayes | random | grid
    "metric": {"name": "val/accuracy", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"distribution": "log_uniform_values", "min": 1e-5, "max": 1e-3},
        "batch_size": {"values": [8, 16, 32]},
        "epochs": {"values": [3, 5, 7]},
    },
}

sweep_id = wandb.sweep(sweep_config, project="my-project")
wandb.agent(sweep_id, function=train_fn, count=10)
```

For YAML config, early termination, nested params see [reference/sweeps.md](reference/sweeps.md).

### 5. Tables

```python
table = wandb.Table(columns=["image", "label", "prediction", "correct", "confidence"])
table.add_data(wandb.Image(img), true_label, pred_label, is_correct, conf_score)
run.log({"predictions": table})
```

Supports `IMMUTABLE` (default), `MUTABLE` (update columns), `INCREMENTAL` (streaming rows) modes.

For diverse examples (object detection, audio, multi-modal, error analysis) see [reference/table-examples.md](reference/table-examples.md).

### 6. Leaderboard

> **IMPORTANT**: When the user asks to create a leaderboard, ALWAYS ask which metrics to include and how to rank them before writing any code. Propose candidate metrics based on the task (e.g., accuracy, F1, loss) and let the user confirm or modify.

Build a leaderboard where evaluation results are automatically aggregated using Tables + Reports + Summary:

```python
# In eval run: log with same keys in summary -> Report auto-compares
with wandb.init(project="my-project", job_type="evaluation", tags=["leaderboard"]) as run:
    run.summary["eval_accuracy"] = accuracy
    run.summary["eval_macro_f1"] = macro_f1
    run.summary["model_artifact"] = model_artifact_path

    # Also log a Leaderboard Table
    lb = wandb.Table(columns=["model", "accuracy", "f1", "timestamp"])
    lb.add_data(model_name, accuracy, macro_f1, datetime.now().isoformat())
    run.log({"eval/leaderboard": lb})
```

```python
# Create Report (once) -> new eval runs are auto-reflected
import wandb_workspaces.reports.v2 as wr
report = wr.Report(project="my-project", entity=entity, title="Leaderboard")
report.blocks = [
    wr.H1("Evaluation Leaderboard"),
    wr.PanelGrid(
        panels=[wr.BarPlot(metrics=["eval_accuracy"], title="Accuracy")],
        runsets=[wr.Runset(project="my-project", entity=entity,
                          filters={"jobType": "evaluation"},
                          order=["-summary_metrics.eval_accuracy"])],
    ),
]
report.save()
```

For full patterns (INCREMENTAL table, API queries) see [reference/leaderboard.md](reference/leaderboard.md).

### 7. Public API

```python
api = wandb.Api()

# Query runs
runs = api.runs("entity/project", filters={"sweep": sweep_id}, order="-summary_metrics.eval/accuracy")
for r in runs:
    print(r.name, r.summary.get("eval/accuracy"))

# Get artifact
artifact = api.artifact("entity/project/artifact-name:alias")
```

For Reports, advanced queries see [reference/api-patterns.md](reference/api-patterns.md).

## Best Practices

1. **Always set `job_type` and `tags`** on `wandb.init()` for run filtering and organization
2. **Use context manager** (`with wandb.init() as run:`) for proper cleanup
3. **Store metadata on artifacts** — model architecture, accuracy, dataset stats
4. **Load data via artifacts/registry**, not local paths — ensures reproducibility and lineage
5. **Use env vars** for portable config:
   - `WANDB_PROJECT`, `WANDB_ENTITY`, `WANDB_API_KEY`
   - `WANDB_DIR` (local storage), `WANDB_MODE` (online/offline/disabled)
6. **Registry alias convention**: `latest` -> `candidates` -> `production`
7. **Log predictions as Tables** with `wandb.Image()` for visual inspection
8. **Set `run.summary`** for metrics you want in the runs table (not just logged over time)

## E2E ML Pipeline Pattern

```
Data Prep       ->  Training       ->  Sweep          ->  Evaluation
(job_type:       (job_type:         (job_type:          (job_type:
 data-prep)       training)          sweep-training)     evaluation)
    |                |                   |                   |
    v                v                   v                   v
Dataset Artifact -> Model Artifact -> Best Model    ->  Registry
    |                                    |               (candidates)
    v                                    v                   |
Registry         <-  link_artifact  <-  link_artifact       v
(dataset)            (model)            (model)         Evaluation
                                                            |
                                                            v
                                                        Leaderboard
                                                        (summary + table
                                                         + report auto-update)
                                                            |
                                                            v
                                                        Human Review
                                                            |
                                                            v
                                                        Registry
                                                        (production)
```

## Troubleshooting

Common errors and solutions: [reference/troubleshooting.md](reference/troubleshooting.md)

## Documentation

- Official docs: https://docs.wandb.ai/models
- SDK cheat sheet: https://docs.wandb.ai/models/ref/sdk-coding-cheat-sheet
- Python SDK ref: https://docs.wandb.ai/models/ref/python
