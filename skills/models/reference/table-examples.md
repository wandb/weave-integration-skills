# Table Examples

## Image Classification Results

```python
class_set = wandb.Classes([{"name": c, "id": i} for i, c in enumerate(class_names)])

table = wandb.Table(columns=["image", "prediction", "confidence", "label", "correct"])

for img, pred, conf, label in zip(images, predictions, confidences, labels):
    table.add_data(
        wandb.Image(img, caption=f"Pred: {pred}", classes=class_set),
        pred,
        round(conf, 4),
        label,
        pred == label,
    )

run.log({"classification_results": table})
```

Filter by `correct` column in the W&B UI to quickly find misclassifications.

## Object Detection Results

Uses `wandb.Image(boxes=...)` with `scores` for interactive confidence threshold filtering in the W&B UI.

```python
class_labels = {0: "person", 1: "car", 2: "dog", 3: "cat"}

table = wandb.Table(columns=["image", "num_objects", "classes_detected"])

for img, detections in zip(images, all_detections):
    box_data = []
    for det in detections:
        box_data.append({
            "position": {
                "minX": det["xmin"],
                "minY": det["ymin"],
                "maxX": det["xmax"],
                "maxY": det["ymax"],
            },
            "domain": "pixel",
            "class_id": det["class_id"],
            "box_caption": f"{class_labels[det['class_id']]} {det['score']:.2f}",
            "scores": {
                "confidence": det["score"],
                "iou": det.get("iou", 0.0),
            },
        })

    annotated = wandb.Image(
        img,
        boxes={
            "predictions": {"box_data": box_data, "class_labels": class_labels},
        },
    )

    detected_classes = set(class_labels[d["class_id"]] for d in detections)
    table.add_data(annotated, len(detections), ", ".join(sorted(detected_classes)))

run.log({"detections": table})
```

To compare predictions against ground truth, add a second key to `boxes`:

```python
wandb.Image(
    img,
    boxes={
        "predictions": {"box_data": pred_box_data, "class_labels": class_labels},
        "ground_truth": {"box_data": gt_box_data, "class_labels": class_labels},
    },
)
```

## Semantic Segmentation Results

Uses `wandb.Image(masks=...)` to overlay segmentation masks. Toggle mask visibility and adjust opacity in the W&B UI.

```python
class_labels = {0: "background", 1: "person", 2: "car", 3: "road", 4: "building"}

table = wandb.Table(columns=["image", "num_classes", "dominant_class"])

for img, pred_mask, gt_mask in zip(images, pred_masks, gt_masks):
    masked_img = wandb.Image(
        img,
        masks={
            "predictions": {
                "mask_data": pred_mask,  # 2D numpy array of integer class labels
                "class_labels": class_labels,
            },
            "ground_truth": {
                "mask_data": gt_mask,
                "class_labels": class_labels,
            },
        },
    )

    unique_classes = set(pred_mask.flatten()) - {0}
    dominant = class_labels[max(unique_classes, key=lambda c: (pred_mask == c).sum())]
    table.add_data(masked_img, len(unique_classes), dominant)

run.log({"segmentation_results": table})
```

For instance segmentation, encode each instance as a unique integer in `mask_data`:

```python
instance_mask = np.zeros_like(pred_mask)
for i, inst in enumerate(instances, start=1):
    instance_mask[inst["mask"]] = i

wandb.Image(
    img,
    masks={
        "instances": {
            "mask_data": instance_mask,
            "class_labels": {i: f"{inst['class']}_{i}" for i, inst in enumerate(instances, start=1)},
        },
    },
)
```

## Text Generation Comparison

```python
table = wandb.Table(columns=["prompt", "model_a", "model_b", "reference", "len_a", "len_b"])

for prompt, out_a, out_b, ref in zip(prompts, outputs_a, outputs_b, references):
    table.add_data(prompt, out_a, out_b, ref, len(out_a.split()), len(out_b.split()))

run.log({"generation_comparison": table})
```

## Audio Transcription Results

```python
table = wandb.Table(columns=["audio", "transcription", "reference", "wer"])

for audio_path, transcript, reference, wer_score in results:
    table.add_data(wandb.Audio(audio_path), transcript, reference, round(wer_score, 4))

run.log({"transcriptions": table})
```

## Error Analysis

```python
table = wandb.Table(columns=["image", "prediction", "label", "confidence", "error_type"])

for img, pred, label, conf in zip(images, preds, labels, confs):
    if pred != label:
        error_type = categorize_error(pred, label)
        table.add_data(
            wandb.Image(img, caption=f"P:{pred} / GT:{label}"),
            pred, label, round(conf, 4), error_type,
        )

run.log({"error_analysis": table})
```

Group by `error_type` column in the W&B UI to identify systematic failure patterns.

## Multi-Modal Table

```python
table = wandb.Table(columns=["image", "audio", "text_description", "category"])

for img_path, audio_path, text, category in samples:
    table.add_data(wandb.Image(img_path), wandb.Audio(audio_path), text, category)

run.log({"multi_modal_samples": table})
```

## Confusion Matrix

Using `wandb.plot.confusion_matrix()` for an interactive confusion matrix in the W&B UI:

```python
run.log({"confusion_matrix": wandb.plot.confusion_matrix(
    y_true=y_true, preds=y_pred, class_names=class_names,
)})
```

Or use matplotlib for a static image:

```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_true, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=class_names)
fig, ax = plt.subplots(figsize=(12, 10))
disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
plt.tight_layout()

run.log({"confusion_matrix_img": wandb.Image(fig)})
plt.close()
```

## Per-Class Metrics

```python
from sklearn.metrics import classification_report

report = classification_report(y_true, y_pred, output_dict=True)
table = wandb.Table(columns=["class", "precision", "recall", "f1-score", "support"])

for cls, metrics in report.items():
    if cls in ("accuracy", "macro avg", "weighted avg"):
        continue
    table.add_data(cls, metrics["precision"], metrics["recall"], metrics["f1-score"], int(metrics["support"]))

run.log({"per_class_metrics": table})
```

## From Pandas DataFrame

```python
import pandas as pd

df = pd.DataFrame({"feature_1": [1, 2, 3], "feature_2": [0.1, 0.2, 0.3], "label": ["A", "B", "A"]})
table = wandb.Table(dataframe=df)
run.log({"data": table})
```

## INCREMENTAL Table (streaming)

```python
table = wandb.Table(columns=["step", "input", "prediction", "label"], log_mode="INCREMENTAL")

for step in range(num_batches):
    inputs, labels = get_batch(step)
    predictions = model.predict(inputs)

    for inp, pred, label in zip(inputs, predictions, labels):
        table.add_data(step, inp, pred, label)

    run.log({"training_table": table}, step=step)
```

## MUTABLE Table (update columns)

```python
table = wandb.Table(columns=["input", "label", "prediction"], log_mode="MUTABLE")

for inp, label, pred in zip(inputs, labels, predictions):
    table.add_data(inp, label, pred)
run.log({"eval_table": table})

# Later: add confidence column
confidences = model.predict_proba(inputs).max(axis=1)
table.add_column("confidence", confidences)
run.log({"eval_table": table})
```

## Video Table

```python
table = wandb.Table(columns=["video", "label", "prediction", "correct"])

for video_path, label, pred in zip(video_paths, labels, predictions):
    table.add_data(wandb.Video(video_path, fps=4, format="mp4"), label, pred, pred == label)

run.log({"video_predictions": table})
```

## Tips

1. **Row limits**: Keep under 10k rows for best UI performance
2. **Sampling**: For large datasets, log representative samples
3. **Captions**: Add captions to `wandb.Image()` for quick context
4. **Prefixes**: Use `eval/` or `train/` prefixes for organized dashboards
5. **Rich media**: Mix `wandb.Image`, `wandb.Audio`, `wandb.Video`, `wandb.Html` in columns
6. **Interactive overlays**: Use `boxes` for bounding boxes and `masks` for segmentation — filter by score/class in the UI
7. **Comparison**: Add both `predictions` and `ground_truth` keys in `boxes`/`masks` to toggle between them
