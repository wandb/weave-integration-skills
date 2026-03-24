# Registry

Registry provides a centralized hub for organizing and sharing artifact versions across an organization.

## Registry Path Format

```
wandb-registry-<RegistryName>/<CollectionName>
```

Examples:
- `wandb-registry-MyModels/food101-classifier`
- `wandb-registry-MyDatasets/food101-subset`

## Link Artifact to Registry

```python
import wandb

artifact = wandb.Artifact(name="food-classifier", type="model")
artifact.add_dir("./model/")

target_path = "wandb-registry-MyModels/food101-classifier"

with wandb.init(project="my-project", job_type="registry") as run:
    run.link_artifact(
        artifact=artifact,
        target_path=target_path,
        aliases=["candidates", "latest"],
    )
```

## Link Existing Artifact

```python
with wandb.init(project="my-project") as run:
    existing = run.use_artifact("food-classifier-vit:v5", type="model")
    run.link_artifact(
        artifact=existing,
        target_path="wandb-registry-MyModels/food101-classifier",
        aliases=["candidates"],
    )
```

## Download from Registry

```python
# Within a run
with wandb.init() as run:
    artifact = run.use_artifact(
        "wandb-registry-MyModels/food101-classifier:production"
    )
    model_dir = artifact.download()

# Without a run (Public API)
api = wandb.Api()
artifact = api.artifact(
    "wandb-registry-MyModels/food101-classifier:production",
    type="model",
)
model_dir = artifact.download()
```

## Alias Strategy

| Alias | Purpose | Who Sets It |
|---|---|---|
| `latest` | Most recent version | Automatic |
| `candidates` | Ready for evaluation | CI/training pipeline |
| `production` | Serving in production | Human after review |
| `staging` | Pre-production testing | Optional |

Typical flow:
```
Training -> log_artifact -> link_artifact(aliases=["candidates"])
                                |
                                v
                        Automation triggers eval
                                |
                                v
                        Human reviews results
                                |
                                v
                        Assign "production" alias (manual or API)
                                |
                                v
                        Webhook -> Deploy
```

## Manage Aliases via API

```python
api = wandb.Api()
artifact = api.artifact("wandb-registry-MyModels/food101-classifier:v3")
artifact.aliases.append("production")
artifact.save()
```

## Create a Registry

```python
api = wandb.Api()
registry = api.create_registry(
    name="MyModels",
    visibility="OPEN_TO_ALL_ORG_MEMBERS",  # or "RESTRICTED"
)
```

## Delete a Registry

```python
api = wandb.Api()
registry = api.registry("MyModels")
registry.delete()
```

## Collection Management

### Add Description

```python
api = wandb.Api()
collection = api.artifact_collection(
    type_name="model",
    name="wandb-registry-MyModels/food101-classifier",
)
collection.description = "ViT-based food classifier for Food-101 dataset"
collection.save()
```

### Add Tags to Collection

```python
collection = wandb.Api().artifact_collection(
    type_name="model",
    name="wandb-registry-MyModels/food101-classifier",
)
collection.tags = ["production", "computer-vision", "food-classification"]
collection.save()
```

### Remove Tags

```python
collection.tags.remove("staging")
collection.save()
```

## Retrieve Specific Version

```python
api = wandb.Api()

# By version number
artifact = api.artifact("wandb-registry-MyModels/food101-classifier:v3")

# By alias
artifact = api.artifact("wandb-registry-MyModels/food101-classifier:production")

# Access metadata
print(artifact.metadata)
print(artifact.aliases)
print(artifact.version)
```
