# Weave Feedback & Annotations Reference

Weave provides an integrated feedback system for collecting reactions, notes, and structured data on traced calls. Feedback supports fine-tuning workflows, issue identification, and evaluation dataset construction.

## Adding Feedback to a Call

### Get the call reference

To add feedback, you need the call's UUID. Two ways to get it:

```python
import weave

weave.init('my-team/my-project')

# Method 1: During call execution
@weave.op()
def my_function(input_value: str) -> str:
    current_call = weave.require_current_call()
    call_id = current_call.id
    return f"Processed {input_value}"

# Method 2: After call execution using .call()
@weave.op()
def my_function(input_value: str) -> str:
    return f"Processed {input_value}"

result, call = my_function.call("example input")
call_id = call.id
```

### Add reactions, notes, and custom feedback

```python
import weave

client = weave.init('my-team/my-project')
call = client.get_call("<call_uuid>")

# Emoji reaction
call.feedback.add_reaction("👍")

# Text note (max 1024 characters)
call.feedback.add_note("This response was accurate and well-structured.")

# Custom key/value pairs (must be JSON-serializable, < 1 KB)
call.feedback.add("correctness", {"value": 5})
call.feedback.add("relevance", {"value": 4, "note": "mostly relevant"})
```

## Querying Feedback

```python
import weave

client = weave.init('my-team/my-project')

# All feedback in the project
all_feedback = client.get_feedback()

# Specific feedback by ID
one = client.get_feedback("<feedback_uuid>")[0]

# Filter by reaction type (with pagination)
thumbs_up = client.get_feedback(reaction="👍", limit=10)

# Inspect feedback details
for f in client.get_feedback():
    print(f.id, f.feedback_type, f.created_at, f.payload)
```

## Deleting Feedback

```python
call.feedback.purge("<feedback_uuid>")
```

## Human Annotations

Human annotations enable structured evaluation of LLM outputs. Create annotation scorers to define the annotation schema, then annotate calls in the UI or via SDK.

### Create via SDK

```python
import weave
from weave.flow.annotation_spec import AnnotationSpec

client = weave.init('my-team/my-project')

# Numeric scorer
temperature_scorer = AnnotationSpec(
    name="Temperature",
    description="The perceived temperature of the LLM call",
    field_schema={
        "type": "number",
        "minimum": -1,
        "maximum": 1,
    },
)
weave.publish(temperature_scorer, "temperature-scorer")

# Enum scorer (categorical)
tone_scorer = AnnotationSpec(
    name="Tone",
    description="The tone of the LLM response",
    field_schema={
        "type": "string",
        "enum": ["Aggressive", "Neutral", "Polite", "N/A"],
    },
)
weave.publish(tone_scorer, "tone-scorer")

# Boolean scorer
accuracy_scorer = AnnotationSpec(
    name="Accurate",
    description="Whether the response is factually accurate",
    field_schema={"type": "boolean"},
)
weave.publish(accuracy_scorer, "accuracy-scorer")
```

### Update a scorer (creates new version)

```python
updated = AnnotationSpec(
    name="Temperature",
    description="The perceived temperature of the LLM call",
    field_schema={
        "type": "integer",  # changed from number to integer
        "minimum": -1,
        "maximum": 1,
    },
)
weave.publish(updated, "temperature-scorer")
```

### Apply annotation via SDK

```python
import weave

client = weave.init('my-team/my-project')
call = client.get_call("<call_id>")
annotation_spec = weave.ref("<annotation_spec_ref_uri>")

call.feedback.add(
    feedback_type="wandb.annotation." + annotation_spec.name,
    payload={"value": 1},
    annotation_ref=annotation_spec.uri(),
)
```

### Create via UI

1. Navigate to **Scorers** in the sidebar
2. Click **+ Create scorer**
3. Set **Scorer type** to **Human annotation**
4. Configure **Name**, **Description**, and **Type** (boolean, integer, string enum, etc.)
5. Click **Create scorer**

Then annotate calls from the **Traces** tab by opening a call and using the **Feedback** sidebar.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Feedback not appearing | Refresh the call table; ensure `weave.init()` was called |
| Note exceeds limit | Maximum 1024 characters per note |
| Custom feedback too large | Feedback payload must be < 1 KB when JSON-serialized |
| Annotation scorer not in UI | Ensure `weave.publish(spec, "name")` was called with correct name |
