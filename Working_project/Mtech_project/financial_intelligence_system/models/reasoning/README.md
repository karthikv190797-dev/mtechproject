# Teacher and Student Models for Reasoning

This folder contains configurations and weights for the Teacher-Student distillation pipeline.

## 📁 Structure

```
reasoning/
├── README.md                    # This file
├── teacher_model/
│   ├── config.yaml             # Teacher model configuration
│   ├── weights.pt              # PyTorch weights (placeholder)
│   └── training_metadata.json
└── student_model/
    ├── config.yaml             # Student model configuration
    ├── weights.pt              # PyTorch weights (placeholder)
    └── training_metadata.json
```

## 🎓 Teacher-Student Distillation

The system uses knowledge distillation to transfer knowledge from a larger teacher model to a smaller student model.

### Teacher Model
- **Purpose**: High-accuracy reasoning and knowledge source
- **Characteristics**: Larger, more powerful, slower inference
- **Backends**: 
  - Local: Ollama (open-source LLMs)
  - Remote: OpenAI, HuggingFace, etc.
  - Custom: Fine-tuned models

### Student Model
- **Purpose**: Fast, efficient reasoning for production
- **Characteristics**: Smaller, optimized for inference speed
- **Training**: Fine-tuned on teacher model outputs

## 📋 Configuration Format

### teacher_model/config.yaml
```yaml
model:
  type: "teacher"
  framework: "pytorch"  # or "transformers", "ollama", etc.
  name: "teacher-base"
  
backend:
  type: "ollama"        # local, ollama, openai, huggingface
  endpoint: "http://localhost:11434"
  model: "mistral:latest"
  
inference:
  temperature: 0.3       # Lower for reasoning (more deterministic)
  max_tokens: 1024
  top_p: 0.95

training:
  learning_rate: 2e-5
  batch_size: 32
  epochs: 3
  warm_up_steps: 500
```

### student_model/config.yaml
```yaml
model:
  type: "student"
  framework: "pytorch"
  architecture: "distilbert"  # or any transformer variant
  
model_size:
  hidden_size: 256
  num_layers: 6
  num_attention_heads: 8

inference:
  temperature: 0.5
  max_tokens: 512
  
training:
  learning_rate: 1e-4
  batch_size: 64
  epochs: 10
  distillation_temperature: 4.0
  alpha: 0.5              # Weight for distillation loss vs task loss
```

## 🚀 Usage

### Load Models
```python
from models.model_loader import ModelLoader

loader = ModelLoader()
teacher = loader.get_reasoning_model("teacher_model")
student = loader.get_reasoning_model("student_model")
```

### Use in Pipeline
```python
from src.reasoning.distillation import DistillationPipeline

pipeline = DistillationPipeline(teacher_model, student_model)
reasoning = pipeline.infer(
    query="What are the risks in Apple's 10-K?",
    context="Apple Inc. 10-K filing...",
    use_teacher=False  # Use student for faster inference
)
```

## 📊 Configuration Examples

### For Financial Reasoning
```yaml
teacher:
  backend: "ollama"
  model: "mistral:latest"  # Good at reasoning
  temperature: 0.2

student:
  architecture: "distilbert-base"
  hidden_size: 768
  num_layers: 6
```

### For High-Accuracy Responses
```yaml
teacher:
  backend: "openai"
  model: "gpt-4"
  temperature: 0.1

student:
  architecture: "bert-base"
  hidden_size: 768
  num_layers: 12
```

### For Speed-Optimized Inference
```yaml
student:
  architecture: "distilbert-small"
  hidden_size: 256
  num_layers: 4
```

## 🔄 Training a Student Model

```python
from src.reasoning.distillation import DistillationPipeline

# Initialize with teacher and untrained student
pipeline = DistillationPipeline(teacher, student_model_config)

# Train student on teacher outputs
training_data = [
    {"query": "...", "context": "..."},
    # ...
]

pipeline.train_student(
    training_data=training_data,
    epochs=10,
    learning_rate=1e-4,
    distillation_temperature=4.0,
    alpha=0.5  # Balance between distillation and task loss
)

# Save trained student
pipeline.save_student("models/reasoning/student_model/weights.pt")
```

## ⚙️ Backend Configuration

### Local Ollama
```yaml
backend:
  type: "ollama"
  endpoint: "http://localhost:11434"
  model: "mistral:latest"  # or any ollama model
  # Start ollama: ollama serve
  # Pull model: ollama pull mistral
```

### OpenAI
```yaml
backend:
  type: "openai"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.1
```

### HuggingFace
```yaml
backend:
  type: "huggingface"
  model: "meta-llama/Llama-2-7b"
  token: "${HUGGINGFACE_TOKEN}"
```

## 📚 References

- Knowledge Distillation: https://arxiv.org/abs/1503.02531
- DistilBERT: https://arxiv.org/abs/1910.01108
- Ollama: https://ollama.ai
