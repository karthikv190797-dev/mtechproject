# Financial Intelligence System - Comprehensive Tutorials & Examples

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Advanced Use Cases](#advanced-use-cases)
4. [Configuration Guide](#configuration-guide)
5. [Performance Optimization](#performance-optimization)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip or conda
- Docker (optional, for containerized deployment)

### Installation

```bash
# Navigate to project directory
cd financial_intelligence_system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start the System

```bash
# Terminal 1: Start the Backend API
python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start the Frontend
streamlit run frontend/app.py --server.port 8501

# Terminal 3: (Optional) Monitor system
python3 -m examples.scripts.api_usage_guide
```

### Verify Setup

```bash
# Check API health
curl http://localhost:8000/health

# Check frontend
open http://localhost:8501
```

---

## Basic Usage Examples

### Example 1: Simple Financial Query

```python
import requests

API_BASE = "http://localhost:8000"

# Query 1: Tesla Revenue Analysis
query = "What was Tesla's total revenue in 2023?"

response = requests.post(
    f"{API_BASE}/query",
    json={"query": query}
)

result = response.json()
print(f"Query: {query}")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence_score']:.1%}")
```

**Expected Output:**
```
Query: What was Tesla's total revenue in 2023?
Answer: Tesla's total revenue in 2023 was $81.46 billion, representing 
a 34.5% increase from $60.57 billion in 2022.
Confidence: 92.0%
```

### Example 2: Competitive Analysis

```python
# Compare multiple companies
queries = [
    "What was Apple's Q1 2024 net revenue?",
    "What was Microsoft's Q2 2024 revenue?",
    "What was Tesla's 2023 total revenue?"
]

for query in queries:
    response = requests.post(f"{API_BASE}/query", json={"query": query})
    result = response.json()
    print(f"Q: {query}")
    print(f"A: {result['answer'][:100]}...")
    print(f"Confidence: {result['confidence_score']:.1%}\n")
```

### Example 3: Profitability Analysis

```python
# Analyze profit margins
query = "Compare the gross profit margins of the three technology companies"

response = requests.post(
    f"{API_BASE}/query",
    json={
        "query": query,
        "parameters": {
            "retrieval_method": "hybrid",
            "evaluation_threshold": 0.8,
            "max_corrections": 3
        }
    }
)

result = response.json()
analysis = result['answer']
supporting_docs = result.get('supporting_documents', [])

print(f"Analysis: {analysis}")
print(f"Supporting Documents: {supporting_docs}")
print(f"Evaluation Scores: {result['evaluation_scores']}")
```

---

## Advanced Use Cases

### Use Case 1: Batch Financial Analysis

```python
from examples.scripts.batch_processor import BatchProcessor

# Initialize processor
processor = BatchProcessor()

# Define comprehensive queries
queries = [
    {
        "query_id": "q001",
        "query": "What was Tesla's revenue growth rate?",
        "priority": "high"
    },
    {
        "query_id": "q002",
        "query": "What are Microsoft's AI investment plans?",
        "priority": "high"
    },
    {
        "query_id": "q003",
        "query": "Compare operating margins across companies",
        "priority": "medium"
    }
]

# Process all queries
results = processor.process_queries(queries)

# Generate report
report = processor.generate_report()

# Save results
processor.save_results("analysis_results.json")
```

### Use Case 2: Document Extraction & Indexing

```python
from examples.scripts.data_loader import FinancialDocumentLoader

# Initialize loader
loader = FinancialDocumentLoader()

# Load documents
loader.load_directory("examples/sample_data", doc_type="filing")

# Create chunks for better retrieval
for doc in loader.documents:
    chunks = loader.create_chunks(doc["id"], chunk_size=500)
    print(f"Created {len(chunks)} chunks for {doc['filename']}")

# Save indexed documents
loader.save_indexed_documents("indexed_documents.json")

# Print summary
loader.print_summary()
```

### Use Case 3: Real-time Dashboard Integration

```python
import streamlit as st
import requests
import plotly.express as px

st.title("Financial Intelligence Dashboard")

# Load sample documents
st.sidebar.title("Configuration")
company = st.sidebar.selectbox("Select Company", ["Tesla", "Apple", "Microsoft"])
metric = st.sidebar.selectbox("Metric", ["Revenue", "Margin", "Growth", "Risk"])

# Query based on selections
query = f"What {metric.lower()} metrics does {company} report?"

# Get API response
response = requests.post(
    "http://localhost:8000/query",
    json={"query": query}
)

if response.status_code == 200:
    result = response.json()
    
    # Display results
    st.write(f"**Query:** {query}")
    st.write(f"**Answer:** {result['answer']}")
    st.metric("Confidence", f"{result['confidence_score']:.1%}")
    
    # Show evaluation scores
    scores = result['evaluation_scores']
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Relevance", f"{scores.get('relevance', 0):.2f}")
    col2.metric("Consistency", f"{scores.get('factual_consistency', 0):.2f}")
    col3.metric("Coherence", f"{scores.get('numerical_coherence', 0):.2f}")
    col4.metric("Entailment", f"{scores.get('entailment', 0):.2f}")
else:
    st.error("Error querying system")
```

### Use Case 4: Automated Report Generation

```python
import json
from datetime import datetime

def generate_financial_report(queries, output_file="report.json"):
    """
    Generate comprehensive financial analysis report.
    """
    
    API_BASE = "http://localhost:8000"
    report = {
        "timestamp": datetime.now().isoformat(),
        "queries": [],
        "summary": {}
    }
    
    total_confidence = 0
    
    for idx, query in enumerate(queries, 1):
        print(f"Processing query {idx}/{len(queries)}: {query[:50]}...")
        
        response = requests.post(
            f"{API_BASE}/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            report["queries"].append({
                "query": query,
                "answer": result['answer'],
                "confidence": result['confidence_score'],
                "evaluation_scores": result['evaluation_scores']
            })
            total_confidence += result['confidence_score']
    
    # Calculate summary
    report["summary"] = {
        "total_queries": len(report["queries"]),
        "average_confidence": total_confidence / len(report["queries"]),
        "report_generated": datetime.now().isoformat()
    }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to {output_file}")
    return report

# Generate report
queries = [
    "What was Tesla's revenue in 2023?",
    "How does Tesla's margin compare to Apple?",
    "What are the growth prospects mentioned?"
]

report = generate_financial_report(queries)
```

---

## Configuration Guide

### Configuration Files Location

```
financial_intelligence_system/
├── config/
│   └── system_config.yaml          # Main configuration
└── examples/
    └── configs/
        ├── config_minimal.yaml     # Minimal setup
        ├── config_production.yaml  # Production settings
        ├── config_semantic.yaml    # Semantic search focus
        └── ...                      # Other variants
```

### Key Configuration Options

#### Retrieval Configuration

```yaml
retrieval:
  method: "hybrid"              # Options: semantic, keyword, hybrid
  hybrid_alpha: 0.6             # Weight for semantic search
  hybrid_beta: 0.4              # Weight for keyword search
  top_k: 10                      # Number of documents to retrieve
  cache_enabled: true           # Enable result caching
  cache_ttl: 3600               # Cache time-to-live in seconds
```

#### Reasoning Configuration

```yaml
reasoning:
  model_type: "distilled"       # Options: teacher, student, distilled
  max_tokens: 1024              # Maximum response length
  temperature: 0.7              # Response determinism (0-1)
  enable_streaming: true        # Stream responses
```

#### Evaluation Configuration

```yaml
evaluation:
  enabled: true                 # Enable evaluation pipeline
  threshold: 0.8                # Confidence threshold (0-1)
  max_corrections: 3            # Maximum correction iterations
  scoring_weights:
    relevance: 0.25
    factual_consistency: 0.25
    numerical_coherence: 0.25
    entailment: 0.25
```

### Switching Configurations

```bash
# Use minimal configuration (testing)
cp examples/configs/config_minimal.yaml config/system_config.yaml
python3 main.py

# Use production configuration (high performance)
cp examples/configs/config_production.yaml config/system_config.yaml
python3 main.py

# Use custom configuration
python3 main.py --config custom_config.yaml
```

---

## Performance Optimization

### Optimization 1: Caching Strategy

```python
# Enable intelligent caching
cache_config = {
    "enabled": True,
    "ttl": 3600,  # 1 hour
    "max_size": 10000,  # items
    "eviction_policy": "LRU"  # Least Recently Used
}

# Queries that match cached results are served instantly
```

### Optimization 2: Batch Processing

```python
# Process multiple queries efficiently
batch_config = {
    "max_parallel_processing": 4,
    "timeout_per_query": 30,
    "retry_on_failure": True,
    "queue_size": 100
}

# Optimal for large-scale analysis
```

### Optimization 3: Model Selection

```python
# Light model for speed (Streamlit, real-time)
reasoning_config_fast = {
    "model_type": "student",
    "max_tokens": 256,
    "temperature": 0.5
}

# Heavy model for quality (Research, batch)
reasoning_config_quality = {
    "model_type": "teacher",
    "max_tokens": 2048,
    "temperature": 0.3
}
```

### Optimization 4: Retrieval Tuning

```python
# Semantic search for understanding (slower, more accurate)
retrieval_semantic = {
    "method": "semantic",
    "top_k": 10,
    "threshold": 0.5
}

# Keyword search for speed (faster, less comprehensive)
retrieval_keyword = {
    "method": "keyword",
    "top_k": 5,
    "threshold": 0.3
}

# Hybrid for balance
retrieval_hybrid = {
    "method": "hybrid",
    "hybrid_alpha": 0.5,
    "hybrid_beta": 0.5,
    "top_k": 7
}
```

---

## Troubleshooting

### Issue 1: API Not Responding

```bash
# Check if API is running
curl http://localhost:8000/health

# If failed, check logs
tail -f backend/logs/api.log

# Restart API
pkill -f "uvicorn backend.api"
python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Issue 2: Low Confidence Scores

**Cause:** Insufficient context or mismatched query scope

**Solution:**
```python
# Increase max_corrections and lower threshold
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "...",
        "parameters": {
            "max_corrections": 5,  # Increase from 3
            "evaluation_threshold": 0.6  # Decrease from 0.8
        }
    }
)
```

### Issue 3: Slow Response Times

**Cause:** Large document set or resource constraints

**Solution:**
```python
# Use smaller model
reasoning = {
    "model_type": "student",  # Instead of "teacher"
    "max_tokens": 256  # Reduce from 1024
}

# Reduce retrieval size
retrieval = {
    "top_k": 3  # Reduce from 10
}
```

### Issue 4: Out of Memory Error

**Cause:** Too many parallel processes or large batch

**Solution:**
```bash
# Reduce parallel processing
config:
  batch:
    max_parallel_processing: 2  # Reduce from 4

# Process queries sequentially
processor = BatchProcessor(max_parallel=1)
```

### Issue 5: Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python3 -m uvicorn backend.api:app --port 8001
```

---

## Additional Resources

- **API Documentation:** See `README.md` in project root
- **Configuration Reference:** See `config/system_config.yaml`
- **Docker Deployment:** See `docker-compose.yml`
- **Example Notebooks:** See `examples/notebooks/`
- **Sample Data:** See `examples/sample_data/`

---

## Getting Help

1. Check `QUICKSTART.md` for basic setup
2. Review example scripts in `examples/scripts/`
3. Check API logs for error details
4. Review configuration examples in `examples/configs/`
5. Run tests: `python3 -m pytest tests/`

---

**Last Updated:** May 25, 2026
**Version:** 1.0.0
