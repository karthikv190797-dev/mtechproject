# Models Directory

This folder stores model files, pretrained weights, embeddings indices, and model configurations for the Financial Intelligence System.

## 📁 Directory Structure

```
models/
├── README.md                    # This file
├── model_registry.json          # Registry of available models
├── model_loader.py              # Model loading utilities
├── embeddings/                  # Vector embeddings and FAISS indices
│   ├── all-MiniLM-L6-v2/
│   │   ├── index.faiss          # FAISS vector index
│   │   └── metadata.json        # Document metadata and embeddings
│   └── README.md
├── reasoning/                   # Teacher-Student distillation models
│   ├── teacher_model/
│   │   ├── config.yaml
│   │   └── weights.pt           # Model weights (PyTorch)
│   ├── student_model/
│   │   ├── config.yaml
│   │   └── weights.pt
│   └── README.md
├── retrievers/                  # Retriever model configs
│   ├── bm25_config.json
│   ├── hybrid_retriever_config.yaml
│   └── README.md
└── checkpoints/                 # Training checkpoints and finetuning artifacts
    ├── fine_tuned_embeddings/
    ├── training_logs/
    └── best_models/
```

## 📋 Model Types

### 1. **Embedding Models**
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Purpose**: Generate semantic embeddings for document retrieval
- **Dimension**: 384 dimensions
- **Use**: Hybrid retriever semantic component

### 2. **Reasoning Models** (Teacher-Student Distillation)
- **Teacher Model**: Larger, more accurate model (placeholder for external LLMs)
- **Student Model**: Lightweight, optimized for inference
- **Purpose**: Generate reasoning paths and explanations

### 3. **Retriever Models**
- **BM25 Retriever**: Keyword-based sparse retrieval
- **FAISS Retriever**: Dense vector-based semantic retrieval
- **Hybrid Retriever**: Combines both approaches

## 🔧 Configuration Files

### `model_registry.json`
Central registry of all available models with metadata:
```json
{
  "embeddings": {
    "all-MiniLM-L6-v2": {
      "model_name": "all-MiniLM-L6-v2",
      "provider": "sentence-transformers",
      "dimensions": 384,
      "local_path": "models/embeddings/all-MiniLM-L6-v2",
      "status": "ready"
    }
  },
  "reasoning": {
    "teacher": {
      "model_type": "teacher",
      "local_path": "models/reasoning/teacher_model",
      "status": "available"
    },
    "student": {
      "model_type": "student",
      "local_path": "models/reasoning/student_model",
      "status": "available"
    }
  }
}
```

### `model_loader.py`
Utility module for loading models:
```python
from models.model_loader import ModelLoader

loader = ModelLoader()
embedder = loader.get_embedding_model("all-MiniLM-L6-v2")
teacher = loader.get_reasoning_model("teacher")
faiss_index = loader.get_faiss_index("all-MiniLM-L6-v2")
```

## 💾 Storing Models

### Option 1: Download and Cache Locally
```bash
# Pre-download embedding model from HuggingFace
python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2')"

# Copy to models/embeddings/
cp -r ~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2 \
      models/embeddings/all-MiniLM-L6-v2
```

### Option 2: FAISS Index Creation
```bash
python models/create_faiss_index.py \
  --documents data/documents.json \
  --model all-MiniLM-L6-v2 \
  --output models/embeddings/all-MiniLM-L6-v2/index.faiss
```

### Option 3: Fine-tuned Models
Store custom fine-tuned checkpoints:
```
models/reasoning/teacher_model/
├── config.yaml           # Model configuration
├── weights.pt            # PyTorch weights
└── training_metadata.json # Training info
```

## 🚀 Usage Examples

### Load Embedding Model
```python
from models.model_loader import ModelLoader

loader = ModelLoader()
embedder = loader.get_embedding_model("all-MiniLM-L6-v2")
embeddings = embedder.encode(["Document text 1", "Document text 2"])
```

### Load FAISS Index
```python
faiss_index = loader.get_faiss_index("all-MiniLM-L6-v2")
distances, indices = faiss_index.search(query_embeddings, k=5)
```

### Load Reasoning Models
```python
teacher_model = loader.get_reasoning_model("teacher")
student_model = loader.get_reasoning_model("student")

# Use for distillation pipeline
reasoning = DistillationPipeline(teacher_model, student_model)
```

## 📊 Model Status and Formats

| Model Type | Format | Size | Status | Location |
|-----------|--------|------|--------|----------|
| Embeddings (all-MiniLM-L6-v2) | PyTorch | ~90 MB | Ready | `embeddings/` |
| Teacher Model | PyTorch/ONNX | TBD | Placeholder | `reasoning/teacher_model/` |
| Student Model | PyTorch/ONNX | TBD | Placeholder | `reasoning/student_model/` |
| FAISS Index | FAISS Binary | Dynamic | Generated | `embeddings/*/index.faiss` |

## 🔍 Model Discovery

The system automatically discovers models:
1. Check `model_registry.json` for registered models
2. Look for model files in subdirectories
3. Load from HuggingFace Hub if not found locally
4. Use fallback TF-IDF embeddings if downloading fails

## 🎯 Next Steps

1. **Download Embeddings**:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **Create FAISS Index**:
   ```bash
   python models/create_faiss_index.py
   ```

3. **Add Custom Models**:
   - Place fine-tuned weights in `reasoning/teacher_model/weights.pt`
   - Update `model_registry.json`
   - Update `model_loader.py` to load custom models

## 📚 References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [PyTorch Model Checkpoints](https://pytorch.org/docs/stable/generated/torch.save.html)
