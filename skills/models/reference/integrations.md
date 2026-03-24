# Framework Integrations

## Integration Methods by Framework

| Framework | Method | Key API |
|---|---|---|
| PyTorch | Manual `wandb.log()` + `wandb.watch()` | `wandb.watch(model)` |
| PyTorch Lightning | WandbLogger | `WandbLogger(project=...)` |
| HuggingFace Transformers | `report_to="wandb"` | `TrainingArguments(report_to="wandb")` |
| Keras / TensorFlow | WandbCallback | `WandbCallback(save_model=True)` |
| FastAI | WandbCallback | `WandbCallback(log_preds=True)` |
| XGBoost | WandbCallback | `WandbCallback(log_model=True)` |
| LightGBM | WandbCallback | `WandbCallback(log_summary=True)` |

## PyTorch Lightning

```python
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning import Trainer

wandb_logger = WandbLogger(
    project="my-project",
    name="experiment-name",
    log_model=True,        # auto-log model checkpoints as artifacts
    save_dir="./wandb_logs",
    tags=["lightning", "resnet"],
)

trainer = Trainer(
    max_epochs=10,
    logger=wandb_logger,
    log_every_n_steps=10,
)

trainer.fit(model, train_loader, val_loader)
# wandb.finish() is automatic with WandbLogger
```

In LightningModule, use `self.log()` — auto-synced to W&B:
```python
class MyModel(pl.LightningModule):
    def training_step(self, batch, batch_idx):
        loss = self.compute_loss(batch)
        self.log("train/loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        loss, acc = self.compute_metrics(batch)
        self.log("val/loss", loss)
        self.log("val/accuracy", acc)
```

## HuggingFace Transformers

```python
import os
import wandb
from transformers import TrainingArguments, Trainer

os.environ["WANDB_PROJECT"] = "my-hf-project"

wandb.init(
    project="my-hf-project",
    name="fine-tuning-bert",
    config={"model": "bert-base", "task": "classification"},
)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    report_to="wandb",
    run_name="bert-finetune",
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
wandb.finish()
```

## Keras / TensorFlow

```python
import wandb
from wandb.integration.keras import WandbMetricsLogger, WandbModelCheckpoint

wandb.init(project="keras-project", config={"epochs": 10, "lr": 0.001})

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

model.fit(
    x_train, y_train,
    epochs=wandb.config.epochs,
    validation_data=(x_val, y_val),
    callbacks=[
        WandbMetricsLogger(),
        WandbModelCheckpoint("models/"),
    ],
)

wandb.finish()
```

## FastAI

```python
from fastai.vision.all import *
from fastai.callback.wandb import WandbCallback
import wandb

wandb.init(project="fastai-project")

learn = vision_learner(dls, resnet34, metrics=accuracy)
learn.fit_one_cycle(5, cbs=WandbCallback(log_preds=True, log_model=True))

wandb.finish()
```

## XGBoost

```python
import xgboost as xgb
from wandb.integration.xgboost import WandbCallback
import wandb

wandb.init(project="xgboost-project", config=params)

wandb_callback = WandbCallback(log_model=True, log_feature_importance=True)

model = xgb.train(
    params,
    dtrain,
    num_boost_round=100,
    evals=[(dval, "validation")],
    callbacks=[wandb_callback],
)

wandb.finish()
```

## LightGBM

```python
import lightgbm as lgb
from wandb.integration.lightgbm import WandbCallback
import wandb

wandb.init(project="lightgbm-project", config=params)

model = lgb.train(
    params,
    train_set,
    valid_sets=[valid_set],
    callbacks=[
        WandbCallback(log_summary=True, save_model_checkpoint=True),
    ],
)

wandb.finish()
```

## TRL (Transformer Reinforcement Learning)
```python
from trl import SFTTrainer
from transformers import TrainingArguments
import os

os.environ["WANDB_PROJECT"] = "trl-fine-tune"

training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",
    run_name="sft-llama3",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    logging_steps=10,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    peft_config=lora_config,  # optional LoRA
)

trainer.train()
```

TRL's SFTTrainer, DPOTrainer, and PPOTrainer are all based on HuggingFace Trainer, so `report_to="wandb"` enables auto-logging.

## Unsloth
```python
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
import os

os.environ["WANDB_PROJECT"] = "unsloth-fine-tune"

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16)

training_args = TrainingArguments(
    output_dir="./outputs",
    report_to="wandb",
    run_name="unsloth-llama3-lora",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    logging_steps=5,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
```

Unsloth uses HuggingFace Trainer internally, so `report_to="wandb"` works as-is.

## Callback Options

| Framework | Key Options |
|---|---|
| Lightning WandbLogger | `log_model`, `save_dir`, `name`, `version`, `tags` |
| Keras WandbCallback | `save_model`, `monitor`, `log_weights`, `log_gradients` |
| HuggingFace | `report_to`, `run_name`, `logging_steps` |
| FastAI | `log_preds`, `log_model`, `log_dataset` |
| XGBoost | `log_model`, `log_feature_importance` |
| LightGBM | `log_summary`, `save_model_checkpoint` |

## Codebase Analysis for Integration

When adding W&B to existing code, follow this checklist:

1. **Detect framework**: Search for import statements
2. **Find training loop**: `def train`, `def fit`, `for epoch in`
3. **Identify config**: argparse, dataclass, YAML, hardcoded values
4. **Locate metric logging**: `print(loss)`, `logging.info()`, TensorBoard
5. **Check model saving**: `torch.save()`, `model.save()`, `save_model()`

```bash
# Quick framework detection
grep -r "import torch\b" --include="*.py"
grep -r "import tensorflow\|import keras" --include="*.py"
grep -r "from transformers import" --include="*.py"
grep -r "import pytorch_lightning\|import lightning" --include="*.py"
grep -r "from fastai" --include="*.py"
grep -r "import xgboost\|import lightgbm" --include="*.py"
```

Replace existing logging:

| Current | wandb Replacement |
|---|---|
| `print(f"loss: {loss}")` | `wandb.log({"loss": loss})` |
| `logging.info(...)` | `wandb.log(...)` |
| `SummaryWriter` (TensorBoard) | `WandbLogger` or `wandb.log()` |
| `tqdm(desc=...)` | Keep tqdm + add `wandb.log()` |
