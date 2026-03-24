# Troubleshooting

## Authentication

### "wandb: ERROR Run initialization failed"
**Cause:** Not authenticated or network issue.
```bash
wandb login  # Enter API key from https://wandb.ai/authorize
```
Or use offline mode:
```python
wandb.init(project="project-name", mode="offline")
```

### "Permission denied" when logging to project
**Cause:** Wrong entity or project permissions.
```python
wandb.init(project="my-project", entity="correct-team")
```

## Run Initialization

### Config not showing in dashboard
**Cause:** Config passed after init or not as dict.
```python
# Correct
wandb.init(project="...", config={"lr": 0.001, "epochs": 10})

# Wrong — argparse namespace must be converted
wandb.init(project="...", config=vars(args))  # use vars()
```

### Duplicate runs created
**Cause:** `wandb.init()` called multiple times, or both `wandb.init()` and WandbLogger used.
```python
# Lightning — use ONLY WandbLogger (handles init internally)
wandb_logger = WandbLogger(project="my-project")
trainer = Trainer(logger=wandb_logger)
# Do NOT also call wandb.init()
```

### Run not finishing properly
**Cause:** Script exits without cleanup.
```python
# Use context manager (preferred)
with wandb.init() as run:
    train()

# Or try/finally
try:
    run = wandb.init()
    train()
finally:
    wandb.finish()
```

## Logging

### Duplicate metrics logged
**Cause:** `wandb.log()` called multiple times per step without explicit step.
```python
# Use explicit step
wandb.log({"loss": loss}, step=global_step)

# Or log everything in a single call
wandb.log({"train/loss": train_loss, "val/loss": val_loss})
```

### Metrics not appearing in dashboard
**Cause (framework):** Using wrong logging method.
```python
# Lightning — use self.log(), not wandb.log()
self.log("train/loss", loss)

# Keras — automatic with WandbCallback

# HuggingFace — automatic with report_to="wandb"
```

### "wandb: WARNING Step must only increase"
**Cause:** Logging with a step that is less than or equal to a previous step.
```python
# Ensure step is monotonically increasing
wandb.log({"loss": loss}, step=global_step)
global_step += 1
```

## Artifacts

### "Artifact not found"
**Cause:** Wrong name format or artifact doesn't exist.
```python
# Correct formats
run.use_artifact("artifact-name:latest")            # within project
run.use_artifact("entity/project/artifact-name:v0")  # cross-project
api.artifact("wandb-registry-MyReg/collection:v0")   # from registry
```

### Artifact download hangs
**Cause:** Large artifact or network issues.
```python
# Download specific file only
artifact.download(path_prefix="model.pt")

# Check artifact size first
print(f"Size: {artifact.size / 1e6:.1f} MB")
```

### "Cannot link artifact — collection type mismatch"
**Cause:** Artifact type doesn't match collection type in registry.
```python
# Ensure artifact type matches what the collection expects
artifact = wandb.Artifact("my-model", type="model")  # type must match
run.link_artifact(artifact, "wandb-registry-MyModels/my-collection")
```

## Sweeps

### Sweep agent hangs
**Cause:** Training function doesn't call `wandb.finish()`.
```python
def train_fn():
    with wandb.init() as run:  # context manager auto-finishes
        config = wandb.config
        # training code
```

### Sweep config not applied
**Cause:** Config not read from `wandb.config`.
```python
def train_fn():
    wandb.init()
    lr = wandb.config.learning_rate    # read from sweep config
    batch_size = wandb.config.batch_size
    # NOT from argparse or hardcoded values
```

### "Error: sweep config key not recognized"
**Cause:** Using wrong distribution name or parameter format.
```python
# Valid distributions
"distribution": "log_uniform_values"  # not "log_uniform"
"distribution": "q_log_uniform_values"
"distribution": "uniform"
"distribution": "normal"
"distribution": "int_uniform"
```

## Registry

### "Registry not found"
**Cause:** Wrong registry path format.
```python
# Correct format
"wandb-registry-<RegistryName>/<CollectionName>"

# Common mistake: missing "wandb-registry-" prefix
# Wrong: "MyModels/food-classifier"
# Correct: "wandb-registry-MyModels/food-classifier"
```

### "Permission denied" when linking to registry
**Cause:** User doesn't have write access to the registry.
- Check registry visibility settings in W&B UI
- Ensure the user is part of the organization

## Reports

### "ModuleNotFoundError: wandb_workspaces"
```bash
pip install wandb-workspaces
```

### Report not saving
**Cause:** Missing required fields.
```python
report = wr.Report(
    project="my-project",  # required
    entity="my-team",      # required for team projects
    title="My Report",
)
report.save()  # don't forget to call save()
```

## Environment

### wandb slowing down training
```python
# Reduce logging frequency
wandb.log({"loss": loss}, step=step)  # log every N steps, not every batch

# Or disable console capture
os.environ["WANDB_CONSOLE"] = "off"

# Or disable system metrics
os.environ["WANDB_DISABLE_SERVICE"] = "true"
```

### Offline mode
```python
# No internet during training
os.environ["WANDB_MODE"] = "offline"
wandb.init(project="my-project")

# Sync later when online
# wandb sync ./wandb/offline-run-*
```

### Disable wandb temporarily
```python
os.environ["WANDB_MODE"] = "disabled"
# All wandb calls become no-ops
```
