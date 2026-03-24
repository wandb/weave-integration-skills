# Artifacts

## Create and Log

```python
import wandb

artifact = wandb.Artifact(
    name="my-dataset",
    type="dataset",                 # "dataset", "model", or custom
    description="Training dataset",
)

# Add content
artifact.add_file("data/train.csv")
artifact.add_file("data/labels.json", name="labels.json")
artifact.add_dir("data/images/")
artifact.add_reference("s3://bucket/path/to/data.csv")  # external reference

# Set metadata
artifact.metadata = {
    "num_classes": 10,
    "train_size": 4000,
    "source": "food101",
    "preprocessing": "resize-224",
}

with wandb.init(project="my-project", job_type="data-prep") as run:
    run.log_artifact(artifact, aliases=["v1", "latest"])
```

## Log with Aliases and Tags

```python
run.log_artifact(artifact, aliases=["baseline", "latest"])
run.log_artifact(artifact, tags=["production-ready", "reviewed"])
```

## Consume Artifacts

```python
# Within a run (creates lineage)
with wandb.init(project="my-project", job_type="training") as run:
    artifact = run.use_artifact("my-dataset:latest", type="dataset")
    data_dir = artifact.download()

    # Download specific file/subfolder
    artifact.download(path_prefix="train/")

    # Get single file entry
    entry = artifact.get_entry("config.json")
```

## Download Without a Run

```python
api = wandb.Api()
artifact = api.artifact("entity/project/my-dataset:v0")
path = artifact.download()
```

## Model Artifacts

```python
with wandb.init(project="my-project", job_type="training") as run:
    # ... training ...

    model_artifact = wandb.Artifact(
        name="food-classifier-vit",
        type="model",
        description="ViT fine-tuned on Food-101",
    )
    model_artifact.add_dir("./model_output/")
    model_artifact.metadata = {
        "model_architecture": "vit-base-patch16-224",
        "num_labels": 10,
        "best_val_accuracy": 0.95,
        "epochs": 5,
        "learning_rate": 3e-5,
    }
    run.log_artifact(model_artifact)
```

## Manage Aliases

```python
# Add alias when logging
run.log_artifact(artifact, aliases=["best", "latest"])

# Add alias to existing artifact
api = wandb.Api()
artifact = api.artifact("entity/project/my-model:v3")
artifact.aliases.append("production")
artifact.save()

# Remove alias
artifact.aliases.remove("staging")
artifact.save()

# Replace all aliases
artifact.aliases = ["latest", "v1"]
artifact.save()
```

## Manage Tags

```python
# Add tags when logging
run.log_artifact(artifact, tags=["reviewed", "v1"])

# Add tags to existing artifact
api = wandb.Api()
artifact = api.artifact("entity/project/my-model:v3")
artifact.tags = ["production-ready"]
artifact.save()
```

## Update Metadata and Description

```python
# Within a run
artifact = run.use_artifact("my-model:latest")
artifact.description = "Updated description"
artifact.save()

# Without a run
api = wandb.Api()
artifact = api.artifact("entity/project/my-model:v2")
artifact.description = "Production model v2"
artifact.metadata["deployed_at"] = "2024-01-15"
artifact.metadata["serving_endpoint"] = "https://api.example.com/predict"
artifact.save()
```

## TTL Policy

```python
from datetime import timedelta

# Set TTL on creation
artifact = wandb.Artifact(name="temp-data", type="dataset")
artifact.add_file("temp.csv")
artifact.ttl = timedelta(days=30)

# Update TTL on existing artifact
api = wandb.Api()
artifact = api.artifact("entity/project/temp-data:v0")
artifact.ttl = timedelta(days=365)
artifact.save()
```

## Delete Artifacts

```python
api = wandb.Api()

# Delete specific version
artifact = api.artifact("entity/project/my-model:v0")
artifact.delete(delete_aliases=True)

# Delete entire collection
collection = api.artifact_collection(
    type_name="model",
    name="entity/project/my-model",
)
collection.delete()

# Delete from run
run = api.run("entity/project/run_id")
for av in run.logged_artifacts():
    if av.name.endswith(":v0"):
        av.delete(delete_aliases=True)
```

## External References

```python
artifact = wandb.Artifact("external-data", type="dataset")
artifact.add_reference("s3://my-bucket/datasets/train/")
artifact.add_reference("gs://my-bucket/data.parquet")

with wandb.init() as run:
    run.log_artifact(artifact)
```
