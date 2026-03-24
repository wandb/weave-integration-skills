# Leaderboard

A pattern for building a leaderboard where evaluation results are automatically aggregated using Tables + Reports.

## Core Structure

```
Eval Run 1 ─┐
Eval Run 2 ──┤── Each run logs metrics with the same keys in summary
Eval Run 3 ──┤   + logs eval/leaderboard Table (1 row)
  ...       ─┘
              │
              ▼
         W&B Report
         ├── Runset (job_type="evaluation" filter)
         ├── Table panel (summary metric comparison)
         └── Chart panel (sorting/comparison)
```

Two approaches are available, and combining them is most effective:

1. **Summary metric-based**: Log metrics with the same keys in `run.summary` for each eval run -> Report's Runs Table auto-compares
2. **Leaderboard Table-based**: Log a single-row leaderboard table in each eval run -> View per-run Table

## Method 1: Summary Metric-Based Leaderboard (Recommended)

The simplest and most powerful approach. When all evaluation runs use the same summary keys, the Report's Runs Table panel automatically serves as a leaderboard.

### Evaluation Script

```python
import wandb

with wandb.init(
    project="my-project",
    job_type="evaluation",
    tags=["evaluation", "leaderboard"],
    name=f"eval-{model_name}",
    config={
        "model_artifact": model_artifact_path,
        "dataset_artifact": dataset_artifact_path,
        "eval_split": "test",
    },
) as run:
    # Load model and evaluate
    model_artifact = run.use_artifact(model_artifact_path, type="model")
    model_dir = model_artifact.download()
    dataset_artifact = run.use_artifact(dataset_artifact_path, type="dataset")
    data_dir = dataset_artifact.download()

    results = evaluate(model_dir, data_dir)

    # Log evaluation metrics
    run.log({
        "eval/accuracy": results["accuracy"],
        "eval/macro_f1": results["macro_f1"],
        "eval/weighted_f1": results["weighted_f1"],
    })

    # Log with same keys in summary (enables comparison in Report's Runs Table)
    run.summary["eval_accuracy"] = results["accuracy"]
    run.summary["eval_macro_f1"] = results["macro_f1"]
    run.summary["eval_weighted_f1"] = results["weighted_f1"]
    run.summary["eval_samples"] = results["num_samples"]
    run.summary["model_artifact"] = model_artifact_path
```

### Leaderboard Report Creation

```python
import wandb_workspaces.reports.v2 as wr

api = wandb.Api()
entity = api.default_entity

report = wr.Report(
    project="my-project",
    entity=entity,
    title="Model Evaluation Leaderboard",
    description="Auto-aggregating evaluation results leaderboard",
)

report.blocks = [
    wr.H1("Model Evaluation Leaderboard"),
    wr.P("All evaluation runs are automatically displayed on this leaderboard. "
         "When a new evaluation is run, refresh the Report to see updated results."),

    wr.H2("Performance Comparison"),
    wr.PanelGrid(
        panels=[
            wr.BarPlot(
                metrics=["eval_accuracy"],
                title="Accuracy by Model",
                group_by="model_artifact",
            ),
            wr.BarPlot(
                metrics=["eval_macro_f1"],
                title="Macro F1 by Model",
                group_by="model_artifact",
            ),
        ],
        runsets=[
            wr.Runset(
                project="my-project",
                entity=entity,
                filters={"jobType": "evaluation"},
                order=["-summary_metrics.eval_accuracy"],
            ),
        ],
    ),

    wr.H2("Training Curves of Evaluated Models"),
    wr.PanelGrid(
        panels=[
            wr.LinePlot(x="_step", y=["train/loss"], title="Training Loss"),
            wr.LinePlot(x="_step", y=["eval/accuracy"], title="Eval Accuracy"),
        ],
        runsets=[
            wr.Runset(
                project="my-project",
                entity=entity,
                filters={"jobType": {"$in": ["training", "sweep-training"]}},
            ),
        ],
    ),
]

report.save()
print(f"Leaderboard Report: {report.url}")
```

The Report only needs to be created once. When new evaluation runs are added, the Report automatically reflects the latest data when opened.

## Method 2: Leaderboard Table Logging

Explicitly log a leaderboard table in each evaluation run.

```python
from datetime import datetime

leaderboard = wandb.Table(
    columns=["model_artifact", "accuracy", "macro_f1", "weighted_f1", "eval_samples", "timestamp"]
)
leaderboard.add_data(
    model_artifact_path,
    round(results["accuracy"], 4),
    round(results["macro_f1"], 4),
    round(results["weighted_f1"], 4),
    results["num_samples"],
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)
run.log({"eval/leaderboard": leaderboard})
```

Each run's `eval/leaderboard` table can be viewed on the corresponding run page in the W&B UI.

## Method 3: INCREMENTAL Table for Cumulative Leaderboard

Sequentially evaluate multiple models in a single long-running run and accumulate results:

```python
with wandb.init(
    project="my-project",
    job_type="leaderboard",
    name="model-leaderboard",
) as run:
    leaderboard = wandb.Table(
        columns=["model", "accuracy", "f1", "params", "timestamp"],
        log_mode="INCREMENTAL",
    )

    for model_path in model_candidates:
        results = evaluate_model(model_path)
        leaderboard.add_data(
            model_path,
            results["accuracy"],
            results["f1"],
            results["num_params"],
            datetime.now().isoformat(),
        )
        run.log({"leaderboard": leaderboard})
```

## Combined Pattern (Recommended)

Use Summary metrics + Leaderboard Table + Report together:

```python
import wandb
from datetime import datetime

def run_evaluation(model_artifact_path, dataset_artifact_path, project="my-project"):
    """Run evaluation + auto-update leaderboard"""
    with wandb.init(
        project=project,
        job_type="evaluation",
        tags=["evaluation", "leaderboard"],
        config={
            "model_artifact": model_artifact_path,
            "dataset_artifact": dataset_artifact_path,
        },
    ) as run:
        # Load artifacts
        model_art = run.use_artifact(model_artifact_path, type="model")
        model_dir = model_art.download()
        data_art = run.use_artifact(dataset_artifact_path, type="dataset")
        data_dir = data_art.download()

        # Run evaluation
        results = evaluate(model_dir, data_dir)

        # 1) Log scalar metrics
        run.log({
            "eval/accuracy": results["accuracy"],
            "eval/macro_f1": results["macro_f1"],
        })

        # 2) Summary metrics (for Report Runs Table comparison)
        run.summary["eval_accuracy"] = results["accuracy"]
        run.summary["eval_macro_f1"] = results["macro_f1"]
        run.summary["eval_weighted_f1"] = results["weighted_f1"]
        run.summary["eval_samples"] = results["num_samples"]
        run.summary["model_artifact"] = model_artifact_path

        # 3) Leaderboard Table (for individual run inspection)
        lb = wandb.Table(
            columns=["model_artifact", "accuracy", "macro_f1", "weighted_f1", "samples", "timestamp"]
        )
        lb.add_data(
            model_artifact_path,
            round(results["accuracy"], 4),
            round(results["macro_f1"], 4),
            round(results["weighted_f1"], 4),
            results["num_samples"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        run.log({"eval/leaderboard": lb})

        # 4) Detailed results (Predictions Table, Confusion Matrix, etc.)
        log_detailed_results(run, results)

    return results


def create_leaderboard_report(project="my-project", entity=None):
    """Create leaderboard Report (run once only)"""
    import wandb_workspaces.reports.v2 as wr

    if entity is None:
        entity = wandb.Api().default_entity

    report = wr.Report(
        project=project,
        entity=entity,
        title="Evaluation Leaderboard",
        description="Auto-aggregating model evaluation results",
    )

    eval_runset = wr.Runset(
        project=project,
        entity=entity,
        filters={"jobType": "evaluation"},
        order=["-summary_metrics.eval_accuracy"],
    )

    report.blocks = [
        wr.H1("Evaluation Leaderboard"),
        wr.P("New evaluation runs are automatically reflected on this leaderboard."),

        wr.H2("Model Ranking"),
        wr.PanelGrid(
            panels=[
                wr.BarPlot(metrics=["eval_accuracy"], title="Accuracy"),
                wr.BarPlot(metrics=["eval_macro_f1"], title="Macro F1"),
            ],
            runsets=[eval_runset],
        ),
    ]

    report.save()
    print(f"Leaderboard Report: {report.url}")
    return report
```

## Querying Leaderboard via Public API

Retrieve leaderboard data programmatically without a Report:

```python
import wandb
import pandas as pd

api = wandb.Api()

runs = api.runs(
    "entity/project",
    filters={"jobType": "evaluation", "state": "finished"},
    order="-summary_metrics.eval_accuracy",
)

leaderboard_data = []
for run in runs:
    leaderboard_data.append({
        "run_name": run.name,
        "model": run.summary.get("model_artifact", "N/A"),
        "accuracy": run.summary.get("eval_accuracy"),
        "macro_f1": run.summary.get("eval_macro_f1"),
        "weighted_f1": run.summary.get("eval_weighted_f1"),
        "samples": run.summary.get("eval_samples"),
        "date": run.created_at,
    })

df = pd.DataFrame(leaderboard_data)
print(df.to_string(index=False))
```

## Key Principles

1. **Use the same summary keys across all evaluation runs** — Report automatically creates a comparison table
2. **Unify `job_type="evaluation"`** — Report's Runset filter selects only evaluation runs
3. **Record `model_artifact` in summary** — Track which model produced the results
4. **Create the Report only once** — New runs are automatically reflected afterward
5. **Maintain artifact lineage** — Load models/data via `run.use_artifact()` for provenance tracking
