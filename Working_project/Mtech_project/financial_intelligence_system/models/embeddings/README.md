# Embeddings and Vector Indices

This folder stores pre-computed embeddings and FAISS vector indices for fast semantic retrieval.

## 📁 Structure

```
embeddings/
├── README.md                            # This file
├── all-MiniLM-L6-v2/                   # Embedding model directory
│   ├── index.faiss                     # FAISS vector index
│   ├── metadata.json                   # Document metadata and embeddings
│   └── config.yaml                     # Index configuration
└── [other-embedding-models]/
    ├── index.faiss
    └── metadata.json
```

## 🔍 Embedding Models

### all-MiniLM-L6-v2 (Default)
- **Source**: sentence-transformers
- **Dimensions**: 384
- **Size**: ~90 MB
- **Inference**: Very fast (~100 docs/sec)
- **Use Case**: General semantic similarity for financial documents

**Other Available Models**:
- `all-mpnet-base-v2` (384 dims, higher quality)
- `all-roberta-large-v1` (1024 dims, highest quality)
- `all-distilroberta-v1` (768 dims, fast + accurate)
- `paraphrase-MiniLM-L6-v2` (384 dims, good for paraphrasing)

## 📊 FAISS Index Format

### index.faiss
Binary FAISS index file containing:
- Vector embeddings for all documents
- Index type: `IndexFlatL2` (exact nearest neighbor search)
- Metric: L2 (Euclidean) distance

**File Structure**:
```
[Index Header] [Vector Data] [Index Metadata]
```

### metadata.json
JSON file containing:
```json
{
  "total_documents": 100,
  "embedding_model": "all-MiniLM-L6-v2",
  "vector_dimension": 384,
  "index_type": "IndexFlatL2",
  "documents": [
    "Document 1 full text...",
    "Document 2 full text...",
    ...
  ],
  "created_at": "2024-06-18T10:30:00"
}
```

## 🚀 Creating an Embedding Index

### Step 1: Prepare Documents
Place documents in `data/` directory:
```bash
data/
├── sec_filings/
│   ├── apple_10k_2023.txt
│   └── microsoft_10k_2023.txt
├── earnings_calls/
└── financial_reports/
```

### Step 2: Generate FAISS Index
```bash
cd financial_intelligence_system/
python models/create_faiss_index.py \
  --documents data \
  --model all-MiniLM-L6-v2 \
  --output models/embeddings/all-MiniLM-L6-v2
```

This will create:
- `models/embeddings/all-MiniLM-L6-v2/index.faiss`
- `models/embeddings/all-MiniLM-L6-v2/metadata.json`

### Step 3: Use the Index
```python
from models.model_loader import ModelLoader

loader = ModelLoader()
faiss_index = loader.get_faiss_index("all-MiniLM-L6-v2")
metadata = loader.get_faiss_metadata("all-MiniLM-L6-v2")

# Search
query_embedding = embedder.encode("What is Apple revenue?")
distances, indices = faiss_index.search(
    query_embedding.reshape(1, -1), 
    k=5
)

# Get documents
for idx in indices[0]:
    doc = metadata["documents"][idx]
    print(doc)
```

## 📈 Fine-tuning Embeddings

### For Domain-Specific Tasks
```python
from sentence_transformers import SentenceTransformer, losses
from torch.utils.data import DataLoader

# Start with pretrained model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Fine-tune on financial domain data
train_examples = [
    InputExample(texts=["Apple revenue query", "Apple 10-K filing excerpt"], label=0.9),
    InputExample(texts=["Tesla revenue query", "Apple 10-K filing"], label=0.1),
    # ... more examples
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100
)

# Save fine-tuned model
model.save("models/embeddings/financial-distilroberta-v1")
```

## 🔧 Index Management

### Check Index Status
```bash
python -c "
from models.model_loader import ModelLoader
loader = ModelLoader()
loader.print_summary()
print('Index ready:', loader.is_faiss_index_ready())
"
```

### Rebuild Index
```bash
# Delete old index
rm models/embeddings/all-MiniLM-L6-v2/index.faiss
rm models/embeddings/all-MiniLM-L6-v2/metadata.json

# Create new index
python models/create_faiss_index.py
```

### Update Index with New Documents
```python
import faiss
import json
from sentence_transformers import SentenceTransformer

# Load existing index
index = faiss.read_index("models/embeddings/all-MiniLM-L6-v2/index.faiss")
with open("models/embeddings/all-MiniLM-L6-v2/metadata.json") as f:
    metadata = json.load(f)

# Load embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Add new documents
new_docs = [...]
new_embeddings = embedder.encode(new_docs).astype("float32")
index.add(new_embeddings)

# Update metadata
metadata["total_documents"] += len(new_docs)
metadata["documents"].extend(new_docs)

# Save
faiss.write_index(index, "models/embeddings/all-MiniLM-L6-v2/index.faiss")
with open("models/embeddings/all-MiniLM-L6-v2/metadata.json", "w") as f:
    json.dump(metadata, f)
```

## 📊 Performance Metrics

| Model | Dims | Size | Speed | Accuracy | Use Case |
|-------|------|------|-------|----------|----------|
| all-MiniLM-L6-v2 (default) | 384 | 90M | Very Fast | Good | Financial docs |
| all-distilroberta-v1 | 768 | 271M | Fast | Very Good | High-precision search |
| all-mpnet-base-v2 | 384 | 438M | Moderate | Very High | Complex queries |
| all-roberta-large-v1 | 1024 | 498M | Slow | Excellent | Maximum accuracy |

## 📚 Tips

1. **Choosing Embedding Model**:
   - Start with `all-MiniLM-L6-v2` (default, fast)
   - Move to `all-distilroberta-v1` if accuracy needed
   - Use `all-roberta-large-v1` for maximum accuracy (slower)

2. **Index Size Management**:
   - Keep FAISS index in memory for fast retrieval
   - For >1M documents, consider GPU indices or approximate methods

3. **Document Chunking**:
   - Large documents should be split into sections
   - Each section gets its own embedding
   - Improves retrieval relevance

4. **Batch Indexing**:
   ```bash
   python models/create_faiss_index.py --documents data --model all-MiniLM-L6-v2
   ```

## 🔗 References

- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [HuggingFace Embeddings](https://huggingface.co/models?other=sentence-similarity)
