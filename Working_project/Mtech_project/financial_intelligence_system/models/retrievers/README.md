# Retriever Models Configuration

This folder contains configurations and model files for different retriever types.

## 📁 Structure

- `bm25_config.yaml` — BM25 sparse retriever configuration
- `hybrid_retriever_config.yaml` — Hybrid (BM25 + FAISS) retriever configuration

## 🎯 Available Retrievers

### 1. BM25 Retriever
Keyword-based sparse retrieval using BM25 algorithm.

**Pros**: Fast, memory-efficient, good for keyword queries
**Cons**: Doesn't capture semantic meaning

### 2. FAISS Retriever
Dense vector-based semantic retrieval using Facebook AI Similarity Search.

**Pros**: Captures semantic similarity, finds semantically similar docs
**Cons**: Requires pre-computed embeddings, higher memory usage

### 3. Hybrid Retriever
Combines BM25 and FAISS with configurable weights.

**Pros**: Best of both worlds - semantic + keyword matching
**Cons**: Requires FAISS index setup

## 📚 Configuration Parameters

### BM25 Parameters
- `k1` (default 1.5): Controls term frequency saturation
- `b` (default 0.75): Controls document length normalization

### Hybrid Parameters
- `alpha` (default 0.7): Weight for FAISS semantic scores
- `beta` (default 0.3): Weight for BM25 keyword scores
- `top_k` (default 5): Number of results to return

## 🔧 Usage

```python
from src.retrieval.hybrid_retriever import HybridRetriever

# Initialize with hybrid retriever
retriever = HybridRetriever(
    documents=doc_texts,
    embeddings=embeddings,
    k=5,
    alpha=0.7,  # Favor semantic similarity
    beta=0.3    # But include keyword matching
)

# Search
results = retriever.search("What is Apple revenue?")
```

## 📊 Tuning Guide

### For Semantic Queries
```yaml
alpha: 0.8   # Increase semantic weighting
beta: 0.2    # Decrease keyword weighting
```

### For Keyword Queries
```yaml
alpha: 0.5   # Balance both
beta: 0.5
```

### For Large Document Sets
```yaml
top_k: 10    # Return more candidates
k_dense: 20  # Search deeper in FAISS
```
