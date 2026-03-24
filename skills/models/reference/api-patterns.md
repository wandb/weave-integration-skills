# Public API, Tables, and Reports

## Public API

### Initialize

```python
import wandb

api = wandb.Api()

# With overrides
api = wandb.Api(overrides={"entity": "my-team", "project": "my-project"})

# Default entity
entity = api.default_entity
```

### Query Runs

```python
# Basic query
runs = api.runs("entity/project")

# With filters
runs = api.runs(
    "entity/project",
    filters={
        "sweep": "sweep_id",                          # runs from specific sweep
        "state": "finished",                           # "finished", "running", "crashed"
        "config.learning_rate": {"$lt": 0.01},         # config filter
        "summary_metrics.val/accuracy": {"$gt": 0.9},  # metric filter
        "tags": {"$in": ["production"]},               # tag filter
        "$and": [                                       # combine filters
            {"config.epochs": {"$gte": 5}},
            {"summary_metrics.val/loss": {"$lt": 0.3}},
        ],
    },
    order="-summary_metrics.val/accuracy",  # prefix - for descending
    per_page=50,
)

for run in runs:
    print(run.id, run.name, run.state)
    print(run.config)
    print(run.summary)
    print(run.tags)
```

### Access Run Details

```python
run = api.run("entity/project/run_id")

# Properties
run.id
run.name
run.state          # "finished", "running", "crashed", "failed"
run.config         # hyperparameters
run.summary        # final metrics
run.tags
run.url            # W&B UI URL
run.created_at
run.heartbeat_at

# History (logged metrics over time)
history = run.history()  # pandas DataFrame
scan = run.scan_history()  # generator for large histories

# Files
for f in run.files():
    print(f.name)
    f.download()

# Artifacts
for artifact in run.logged_artifacts():
    print(artifact.name, artifact.type)

for artifact in run.used_artifacts():
    print(artifact.name, artifact.type)
```

### Update Run

```python
run = api.run("entity/project/run_id")
run.tags.append("reviewed")
run.notes = "Best performing model"
run.update()
```

### Delete Runs

```python
run = api.run("entity/project/run_id")
run.delete()
```

### Get Artifact

```python
# By project path
artifact = api.artifact("entity/project/artifact-name:alias")

# From registry
artifact = api.artifact("wandb-registry-MyModels/food-classifier:production")

# Properties
artifact.name
artifact.type
artifact.version
artifact.aliases
artifact.metadata
artifact.description
artifact.created_at
artifact.size        # bytes

# Download
path = artifact.download()
```

## Tables

### Create and Log

```python
import wandb

table = wandb.Table(columns=["image", "true_label", "pred_label", "correct", "confidence"])

for img, true, pred, conf in zip(images, true_labels, predictions, confidences):
    table.add_data(
        wandb.Image(img),
        true,
        pred,
        true == pred,
        round(conf, 4),
    )

run.log({"predictions": table})
```

### Create from DataFrame

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
table = wandb.Table(dataframe=df)
run.log({"data": table})
```

### Per-Class Metrics Table

```python
from sklearn.metrics import classification_report

report = classification_report(y_true, y_pred, output_dict=True)
metrics_table = wandb.Table(columns=["class", "precision", "recall", "f1-score", "support"])

for cls, metrics in report.items():
    if cls in ("accuracy", "macro avg", "weighted avg"):
        continue
    metrics_table.add_data(cls, metrics["precision"], metrics["recall"], metrics["f1-score"], metrics["support"])

run.log({"eval/per_class_metrics": metrics_table})
```

### Leaderboard Table

```python
leaderboard = wandb.Table(columns=["model", "accuracy", "f1", "eval_samples", "timestamp"])

leaderboard.add_data(
    model_artifact_path,
    accuracy,
    macro_f1,
    num_samples,
    datetime.now().isoformat(),
)

run.log({"eval/leaderboard": leaderboard})
```

### Log Confusion Matrix

```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_true, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
fig, ax = plt.subplots(figsize=(12, 10))
disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
plt.tight_layout()

run.log({"eval/confusion_matrix": wandb.Image(fig)})
plt.close()
```

## Reports

### Programmatic Creation

```python
import wandb_workspaces.reports.v2 as wr

report = wr.Report(
    project="my-project",
    entity="my-team",
    title="Training Results",
    description="Summary of training experiments",
)

report.blocks = [
    wr.H1("Training Overview"),
    wr.P("This report summarizes our latest training runs."),

    wr.H2("Loss Curves"),
    wr.PanelGrid(
        panels=[
            wr.LinePlot(x="Step", y=["train/loss"], title="Training Loss"),
            wr.LinePlot(x="Step", y=["val/accuracy"], title="Validation Accuracy"),
        ],
        runsets=[
            wr.Runset(project="my-project", entity="my-team"),
        ],
    ),

    wr.H2("Sweep Results"),
    wr.PanelGrid(
        panels=[
            wr.LinePlot(x="Step", y=["val/accuracy"], title="Sweep Accuracy"),
        ],
        runsets=[
            wr.Runset(
                project="my-project",
                entity="my-team",
                filters={"sweep": "sweep_id"},
            ),
        ],
    ),
]

report.save()
print(f"Report URL: {report.url}")
```

### Report Building Blocks

| Block | Usage |
|---|---|
| `wr.H1(text)` | Heading level 1 |
| `wr.H2(text)` | Heading level 2 |
| `wr.H3(text)` | Heading level 3 |
| `wr.P(text)` | Paragraph |
| `wr.CodeBlock(code, language)` | Code block |
| `wr.MarkdownBlock(text)` | Markdown content |
| `wr.LinePlot(x, y, title)` | Line chart |
| `wr.ScatterPlot(x, y, title)` | Scatter chart |
| `wr.BarPlot(metrics, title)` | Bar chart |
| `wr.PanelGrid(panels, runsets)` | Panel layout |
| `wr.Runset(project, entity)` | Run selection |

### Install

```bash
pip install wandb-workspaces
```
