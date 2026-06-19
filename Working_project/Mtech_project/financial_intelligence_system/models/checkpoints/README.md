# Training Checkpoints and Artifacts

This directory stores training checkpoints, logs, and fine-tuned models.

## 📁 Subdirectories

### training_logs/
Training metrics, loss curves, and validation results:
- `training_log_0001.json` — Run 1 metrics
- `training_log_0002.json` — Run 2 metrics
- `tensorboard_logs/` — TensorBoard event files

### best_models/
Best performing model weights from training runs:
- `student_model_best.pt` — Best student model
- `teacher_model_best.pt` — Best teacher model

### fine_tuned_embeddings/
Fine-tuned embedding models:
- `financial_all_minilm_v1/` — Domain-fine-tuned embeddings
- `financial_mpnet_v1/` — Alternative fine-tuned model

## 📊 Checkpoint Format

### PyTorch Checkpoints
```python
checkpoint = {
    "epoch": 5,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "loss": 0.45,
    "metrics": {
        "accuracy": 0.92,
        "f1_score": 0.91,
        "precision": 0.93,
        "recall": 0.89
    },
    "config": model_config,
    "timestamp": "2024-06-18T10:30:00"
}

torch.save(checkpoint, "checkpoints/best_models/model_epoch_5.pt")
```

### Loading Checkpoints
```python
import torch

checkpoint = torch.load("checkpoints/best_models/model_epoch_5.pt")
model.load_state_dict(checkpoint["model_state_dict"])
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
epoch = checkpoint["epoch"]
```

## 🚀 Usage

### Save During Training
```python
if val_loss < best_loss:
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": train_loss,
            "metrics": metrics
        },
        f"models/checkpoints/best_models/model_best.pt"
    )
```

### Track Training Progress
```python
import json

training_log = {
    "epoch": 1,
    "train_loss": 0.45,
    "val_loss": 0.48,
    "accuracy": 0.92,
    "learning_rate": 1e-4,
    "timestamp": datetime.now().isoformat()
}

with open("models/checkpoints/training_logs/run_log.jsonl", "a") as f:
    f.write(json.dumps(training_log) + "\n")
```

## 📈 Common Checkpoint Patterns

### Pattern: Save Every N Epochs
```python
if (epoch + 1) % 5 == 0:  # Every 5 epochs
    torch.save(checkpoint, f"checkpoints/student_model_epoch_{epoch}.pt")
```

### Pattern: Save Best Model
```python
if val_metric > best_metric:
    best_metric = val_metric
    torch.save(checkpoint, "checkpoints/best_models/best_model.pt")
```

### Pattern: Distributed Training
```python
if is_main_process:
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.module.state_dict(),  # unwrap DDP
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": loss
        },
        checkpoint_path
    )
```

## 🗑️ Cleanup

```bash
# Remove old checkpoints (keep last 5)
ls -t models/checkpoints/best_models/model_*.pt | tail -n+6 | xargs rm

# Clear training logs
rm models/checkpoints/training_logs/*.jsonl
```

## 📚 Best Practices

1. **Save Frequently**: Save after each validation cycle
2. **Keep Last 5**: Only keep 5 most recent checkpoints
3. **Log Metadata**: Always save config, metrics, and timestamp
4. **Version Models**: Use epoch/version numbers
5. **Validate Before Saving**: Only save improving checkpoints
