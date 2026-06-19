# Self-Correcting Financial Intelligence System - Full Documentation

**M.Tech Dissertation | BITS WILP | 2026**

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Installation and Setup](#installation-and-setup)
5. [Configuration Guide](#configuration-guide)
6. [API Reference](#api-reference)
7. [Frontend Usage](#frontend-usage)
8. [Development Guide](#development-guide)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is FinIQ?

FinIQ (Financial Intelligence System with Self-Correction) is an advanced RAG (Retrieval-Augmented Generation) system designed to provide accurate, contextualized answers to financial questions by combining:

- **Intelligent Retrieval**: Hybrid search combining dense vector similarity (FAISS) and sparse keyword matching (BM25)
- **Multi-Agent Orchestration**: Coordinated agents for retrieval, reasoning, evaluation, and correction
- **Knowledge Distillation**: Teacher-student model architecture for efficient inference with deep reasoning
- **Automated Quality Assessment**: Multi-dimensional evaluation (relevance, factuality, coherence, entailment)
- **Self-Correction Loop**: Iterative refinement when confidence is low

### Key Features

✅ **Multi-Source Data Integration**
- SEC EDGAR filings
- Snowflake data warehouse
- Local file ingestion

✅ **Hybrid Retrieval System**
- FAISS-based dense vector search
- BM25-based sparse keyword matching
- Weighted score combination

✅ **Advanced Reasoning Pipeline**
- Teacher model: GLM-130B (deep reasoning)
- Student model: Mistral-7B (fast inference)
- Knowledge distillation mechanism

✅ **Multi-Criteria Evaluation**
- Relevance assessment
- Factual consistency checking
- Numerical coherence validation
- Entailment score calculation

✅ **Interactive Interfaces**
- REST API (FastAPI)
- Web UI (Streamlit)
- Batch processing capability

✅ **Comprehensive Monitoring**
- Query history tracking
- System statistics
- Performance metrics
- Workflow visualization

### Use Cases

1. **Financial Analysis**: Answering questions about company financials, revenue, earnings
2. **Investment Research**: Analyzing SEC filings, earnings calls, financial reports
3. **Comparative Analysis**: Understanding financial metrics across multiple companies
4. **Risk Assessment**: Identifying financial risks and trends
5. **Due Diligence**: Extracting relevant information from large document collections

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────────┤
│  SEC EDGAR   │  Snowflake Data Warehouse  │  Local Files             │
└────────────┬────────────────────────┬──────────────────────┬─────────┘
             │                        │                      │
             └────────────┬───────────┴──────────┬───────────┘
                          │                      │
                    ┌─────▼──────────────────────▼──────────┐
                    │   DATA INGESTION PIPELINE              │
                    │  - Document normalization              │
                    │  - Chunk processing                    │
                    │  - Metadata extraction                 │
                    └─────┬──────────────────────────────────┘
                          │
                    ┌─────▼────────────────────────────────┐
                    │  EMBEDDING GENERATION                 │
                    │  (all-MiniLM-L6-v2)                   │
                    └─────┬────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
    ┌───▼──────────────┐          ┌────────▼──────────────┐
    │   DENSE INDEX    │          │  SPARSE INDEX         │
    │    (FAISS)       │          │   (BM25)              │
    └───┬──────────────┘          └────────┬──────────────┘
        │                                   │
        └──────────────┬────────────────────┘
                       │
            ┌──────────▼──────────────┐
            │  HYBRID RETRIEVER       │
            │ (Weighted Combination)  │
            └──────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    ┌───▼──────────────┐      ┌──────▼──────────┐
    │  FastAPI Backend │      │  Streamlit UI   │
    │  - /query        │      │  - Interactive  │
    │  - /batch        │      │  - Batch mode   │
    │  - /statistics   │      │  - Analytics    │
    └───┬──────────────┘      └──────┬──────────┘
        │                            │
        └────────────┬───────────────┘
                     │
    ┌────────────────▼────────────────┐
    │  MULTI-AGENT ORCHESTRATOR       │
    │  ┌─────────────────────────────┐│
    │  │ 1. Retriever Agent          ││
    │  │ 2. Reader Agent             ││
    │  │ 3. Reasoning Agent          ││
    │  │ 4. Evaluator Agent          ││
    │  │ 5. Verifier Agent           ││
    │  │ 6. Correction Agent         ││
    │  └─────────────────────────────┘│
    └────────────────┬─────────────────┘
                     │
    ┌────────────────▼────────────────┐
    │  RESPONSE WITH CONFIDENCE       │
    │  - Answer text                  │
    │  - Confidence score             │
    │  - Supporting documents         │
    │  - Evaluation metrics           │
    └─────────────────────────────────┘
```

### Data Flow

1. **Initialization Phase**
   - Load configuration from `system_config.yaml`
   - Initialize data sources (SEC, Snowflake, local files)
   - Generate embeddings and build indices
   - Initialize models (teacher and student)

2. **Query Processing Phase**
   - User submits query via API or UI
   - Hybrid retrieval fetches top-k documents
   - Context preparation by reader agent
   - Reasoning agent generates initial answer
   - Evaluator assesses quality across 4 dimensions

3. **Correction Phase** (if confidence < threshold)
   - Correction agent refines answer using teacher model
   - Re-evaluation
   - Iteration until convergence or max iterations reached

4. **Response Phase**
   - Final answer with confidence metrics
   - Supporting documents with relevance scores
   - Processing statistics and metadata

---

## Core Components

### 1. **Data Ingestion Module** (`src/ingestion.py`)

Handles multi-source data collection and preparation.

#### Classes

| Class | Purpose |
|-------|---------|
| `DataIngestionPipeline` | Main orchestrator for data ingestion |
| `SECFilingSource` | Fetches SEC EDGAR filings |
| `SnowflakeSource` | Connects to Snowflake data warehouse |
| `Document` | Internal representation of ingested documents |

#### Key Methods

```python
# Register and execute data sources
pipeline.register_source('sec', sec_source)
documents = pipeline.ingest(source_name='sec', query='Apple earnings')

# Normalize documents
pipeline.normalize_documents(documents)
```

### 2. **Hybrid Retrieval System** (`src/retrieval/hybrid_retriever.py`)

Combines dense vector search and sparse keyword matching.

#### Architecture

- **Dense Retrieval**: FAISS index on sentence embeddings
- **Sparse Retrieval**: BM25 index on tokenized documents
- **Fusion**: Weighted combination of both scores

#### Key Methods

```python
# Initialize retriever
retriever = HybridRetriever(
    documents=docs,
    alpha=0.6,  # Weight for dense
    beta=0.4    # Weight for sparse
)

# Retrieve documents
results = retriever.retrieve("What is Apple's revenue?", top_k=10)
```

### 3. **Reasoning Pipeline** (`src/reasoning/distillation.py`)

Implements teacher-student knowledge distillation for efficient inference.

#### Models

| Model | Purpose | Size |
|-------|---------|------|
| Teacher (GLM-130B) | Deep reasoning, comprehensive answers | 130B parameters |
| Student (Mistral-7B) | Fast inference, deployment-ready | 7B parameters |

#### Features

- Temperature-controlled generation
- Soft target probability distribution
- Loss calculation for training
- Inference mode switching

### 4. **Evaluator Agent** (`src/evaluation/evaluator.py`)

Multi-dimensional quality assessment of generated answers.

#### Evaluation Dimensions

| Dimension | Measures |
|-----------|----------|
| **Relevance** | How well answer addresses the query (0-1) |
| **Factuality** | Alignment with retrieved documents (0-1) |
| **Numerical Coherence** | Consistency of numbers and metrics (0-1) |
| **Entailment** | Logical relationship with context (0-1) |

#### Key Methods

```python
evaluator = EvaluatorAgent()
score = evaluator.evaluate(
    query="Apple revenue?",
    answer="Apple revenue was $394.3B",
    context=[...retrieved docs...],
    previous_score=0.7
)
```

### 5. **Multi-Agent Orchestrator** (`src/orchestration/langgraph_orchestrator.py`)

Coordinates agents in a controlled workflow using LangGraph.

#### Agent Workflow

```
Query Input
    ↓
[1] Retriever Agent → Top-k documents
    ↓
[2] Reader Agent → Context preparation
    ↓
[3] Reasoning Agent → Initial answer (Student model)
    ↓
[4] Evaluator Agent → Quality scoring
    ↓
    ├─ Confidence >= threshold? 
    │   ├─ YES → [5] Verifier Agent
    │   └─ NO → [6] Correction Agent (Loop back to [4])
    │
[5] Verifier Agent → Cross-check answer
    ↓
Final Response (answer + confidence + evidence)
```

#### Key Features

- **Dynamic Routing**: Conditional agent transitions based on confidence
- **Correction Loop**: Iterative refinement (up to max_iterations)
- **State Management**: Tracks query state through workflow
- **History Tracking**: Records agent decisions and rationales

### 6. **FastAPI Backend** (`backend/api.py`)

REST API for system access and integration.

#### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System health check |
| POST | `/query` | Process single query |
| GET | `/query/{query_id}` | Retrieve previous result |
| POST | `/batch` | Process multiple queries |
| GET | `/statistics` | System statistics |

#### Request/Response Models

**Query Request**
```python
{
    "query": "What is Apple's revenue?",
    "use_teacher_model": false,
    "temperature": 0.7,
    "top_k": 10,
    "max_iterations": 3
}
```

**Query Response**
```python
{
    "query_id": "q_12345",
    "query": "What is Apple's revenue?",
    "answer": "Apple's revenue in 2023 was $394.3 billion...",
    "confidence": 0.92,
    "evaluation_scores": {
        "relevance": 0.95,
        "factuality": 0.90,
        "numerical_coherence": 0.90,
        "entailment": 0.88
    },
    "supporting_documents": [
        {
            "title": "Apple 10-K Filing 2023",
            "relevance": 0.97,
            "excerpt": "..."
        },
        ...
    ],
    "evaluation_history": [
        {"iteration": 1, "confidence": 0.75, "correction": "Refined numbers"},
        ...
    ],
    "processing_time_ms": 2345
}
```

### 7. **Streamlit Frontend** (`frontend/app.py`)

Interactive web interface for easy system access.

#### Interface Modes

1. **Interactive Query Mode**
   - Single query input
   - Real-time answer generation
   - Confidence visualization
   - Supporting documents browser

2. **Batch Processing Mode**
   - Multiple queries input (JSON)
   - Batch progress tracking
   - Results export

3. **System Statistics Mode**
   - Query history
   - Performance metrics
   - Model effectiveness charts

#### Features

- Query input with parameter controls
- Answer display with formatted text
- Confidence gauge visualization
- Evaluation metrics display
- Supporting documents explorer
- Processing time display
- Real-time backend status

---

## Installation and Setup

### System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.9 or higher
- **RAM**: 16GB minimum (32GB recommended for teacher model)
- **GPU**: Optional but recommended (CUDA 11.8+)
- **Storage**: 50GB+ for models and data

### Installation Steps

#### Step 1: Clone Repository

```bash
git clone <repository_url>
cd Mtech_project/financial_intelligence_system
```

#### Step 2: Create Virtual Environment

```bash
# Using venv
python -m venv .venv

# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Set Environment Variables

Create `.env` file in `financial_intelligence_system/` directory:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database

# HuggingFace Configuration
HUGGINGFACE_API_KEY=your_hf_api_key

# System Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
```

#### Step 5: Configure System

Edit `config/system_config.yaml` for your environment (see Configuration Guide below).

#### Step 6: Run System

**Option 1: Local Execution**

```bash
# Terminal 1: Start Backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Frontend
streamlit run frontend/app.py

# Terminal 3 (Optional): Run Demo
python main.py
```

**Option 2: Docker Execution**

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Configuration Guide

### System Configuration File (`config/system_config.yaml`)

```yaml
# ============================================
# SYSTEM CONFIGURATION
# ============================================

# Data Ingestion Configuration
data_ingestion:
  sources:
    sec_filings:
      enabled: true
      cache_dir: ./data/sec_filings
      batch_size: 10
    
    snowflake:
      enabled: true
      connection:
        account: ${SNOWFLAKE_ACCOUNT}
        user: ${SNOWFLAKE_USER}
        password: ${SNOWFLAKE_PASSWORD}
        warehouse: ${SNOWFLAKE_WAREHOUSE}
        database: ${SNOWFLAKE_DATABASE}
      query: "SELECT * FROM DOCUMENTS LIMIT 10000"

# Embedding Configuration
embeddings:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  embedding_dim: 384
  batch_size: 32

# Retrieval Configuration
retrieval:
  hybrid_retriever:
    alpha: 0.6  # Weight for dense retrieval (FAISS)
    beta: 0.4   # Weight for sparse retrieval (BM25)
    top_k: 20   # Number of documents to retrieve
    use_reranker: true

# Reasoning Configuration
reasoning:
  teacher_model:
    model_name: "THUDM/glm-130b-chat"
    device: "cuda"  # or "cpu"
    load_in_8bit: true
    temperature: 0.7
    max_tokens: 512
    enabled: false  # Set true to use teacher model
  
  student_model:
    model_name: "mistralai/Mistral-7B-Instruct-v0.2"
    device: "cuda"
    temperature: 0.7
    max_tokens: 512
    enabled: true

# Evaluation Configuration
evaluation:
  min_confidence: 0.75  # Threshold for triggering correction
  max_iterations: 3     # Maximum correction iterations
  
  scoring_weights:
    relevance: 0.35
    factuality: 0.35
    numerical_coherence: 0.20
    entailment: 0.10

# Orchestration Configuration
orchestration:
  workflow_type: "langgraph"  # Orchestration type
  timeout_ms: 30000           # Query timeout
  enable_history: true        # Track workflow history
  enable_logging: true        # Enable detailed logging

# Backend Configuration
backend:
  host: "0.0.0.0"
  port: 8000
  reload: true
  workers: 4
  log_level: "INFO"

# Frontend Configuration
frontend:
  host: "0.0.0.0"
  port: 8501
  theme: "light"
  max_query_length: 1000
  session_timeout_minutes: 60

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "./logs/system.log"
  max_file_size_mb: 100
  backup_count: 5
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SNOWFLAKE_ACCOUNT` | - | Snowflake account identifier |
| `SNOWFLAKE_USER` | - | Snowflake username |
| `SNOWFLAKE_PASSWORD` | - | Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | Snowflake warehouse name |
| `SNOWFLAKE_DATABASE` | - | Snowflake database name |
| `HUGGINGFACE_API_KEY` | - | HuggingFace API key |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG_MODE` | `false` | Enable debug mode |

---

## API Reference

### Health Check

**Request**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response (200)**
```json
{
  "status": "healthy",
  "components": {
    "retriever": "ready",
    "reasoning": "ready",
    "evaluator": "ready",
    "orchestrator": "ready"
  },
  "timestamp": "2026-06-17T10:30:00Z"
}
```

### Query Processing

**Request**
```http
POST /query HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "query": "What is Apple's revenue growth in 2023?",
  "use_teacher_model": false,
  "temperature": 0.7,
  "top_k": 15,
  "max_iterations": 3
}
```

**Response (200)**
```json
{
  "query_id": "q_abc123def456",
  "query": "What is Apple's revenue growth in 2023?",
  "answer": "Apple's revenue in 2023 was $394.3 billion, representing a 2% increase from 2022 when revenue was $394.3 billion...",
  "confidence": 0.92,
  "evaluation_scores": {
    "relevance": 0.95,
    "factuality": 0.90,
    "numerical_coherence": 0.90,
    "entailment": 0.88
  },
  "supporting_documents": [
    {
      "id": "apple_10k_2023",
      "title": "Apple Inc. Form 10-K 2023",
      "relevance": 0.97,
      "source": "SEC EDGAR",
      "excerpt": "Apple reported total net sales of $394.3 billion for fiscal 2023...",
      "document_url": "https://www.sec.gov/..."
    },
    {
      "id": "apple_earnings_call_2023",
      "title": "Apple Earnings Call Transcript Q4 2023",
      "relevance": 0.94,
      "source": "Earnings Call",
      "excerpt": "We had an excellent quarter with revenues up to $394.3 billion...",
      "document_url": "..."
    }
  ],
  "evaluation_history": [
    {
      "iteration": 1,
      "confidence": 0.75,
      "scores": {
        "relevance": 0.92,
        "factuality": 0.80,
        "numerical_coherence": 0.85,
        "entailment": 0.75
      },
      "correction_reason": "Low factuality score - teacher model refining",
      "agent": "correction"
    },
    {
      "iteration": 2,
      "confidence": 0.92,
      "scores": {
        "relevance": 0.95,
        "factuality": 0.90,
        "numerical_coherence": 0.90,
        "entailment": 0.88
      },
      "correction_reason": "Improved factuality",
      "agent": "verifier"
    }
  ],
  "processing_stats": {
    "total_time_ms": 2345,
    "retrieval_time_ms": 234,
    "reasoning_time_ms": 1500,
    "evaluation_time_ms": 300,
    "iterations": 2
  }
}
```

**Error Response (400)**
```json
{
  "detail": "Query must be non-empty string"
}
```

### Query History

**Request**
```http
GET /query/q_abc123def456 HTTP/1.1
Host: localhost:8000
```

**Response (200)**
```json
{
  "query_id": "q_abc123def456",
  "created_at": "2026-06-17T10:30:00Z",
  "query": "What is Apple's revenue growth in 2023?",
  "answer": "...",
  "confidence": 0.92,
  "...": "..."
}
```

### Batch Processing

**Request**
```http
POST /batch HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "queries": [
    "What is Apple's revenue?",
    "What is Microsoft's earnings per share?",
    "Compare Google and Facebook financial metrics"
  ],
  "use_teacher_model": false,
  "temperature": 0.7
}
```

**Response (200)**
```json
{
  "batch_id": "batch_xyz789",
  "total_queries": 3,
  "results": [
    {
      "query_id": "q_1",
      "query": "What is Apple's revenue?",
      "answer": "...",
      "confidence": 0.92
    },
    {
      "query_id": "q_2",
      "query": "What is Microsoft's earnings per share?",
      "answer": "...",
      "confidence": 0.88
    },
    {
      "query_id": "q_3",
      "query": "Compare Google and Facebook financial metrics",
      "answer": "...",
      "confidence": 0.85
    }
  ],
  "processing_stats": {
    "total_time_ms": 7500,
    "avg_time_per_query_ms": 2500,
    "total_iterations": 5
  }
}
```

### System Statistics

**Request**
```http
GET /statistics HTTP/1.1
Host: localhost:8000
```

**Response (200)**
```json
{
  "uptime_minutes": 120,
  "total_queries_processed": 45,
  "avg_confidence": 0.89,
  "confidence_distribution": {
    "high": 38,
    "medium": 6,
    "low": 1
  },
  "avg_processing_time_ms": 2234,
  "retrieval_stats": {
    "avg_documents_retrieved": 18,
    "avg_retrieval_time_ms": 234
  },
  "evaluation_stats": {
    "avg_relevance": 0.93,
    "avg_factuality": 0.88,
    "avg_numerical_coherence": 0.87,
    "avg_entailment": 0.85,
    "correction_rate": 0.13
  },
  "model_stats": {
    "teacher_model_used": false,
    "student_model_inference_count": 45,
    "avg_tokens_generated": 156
  }
}
```

---

## Frontend Usage

### Starting the Frontend

```bash
streamlit run frontend/app.py
```

Access at: `http://localhost:8501`

### Interface Components

#### 1. Mode Selection

Choose from three modes in the sidebar:
- **Interactive Query**: Single query processing
- **Batch Processing**: Multiple queries
- **System Statistics**: Performance analytics

#### 2. Interactive Query Mode

**Usage Steps:**

1. **Enter Query**: Type financial question in the text input
2. **Configure Parameters**:
   - Model: Select student or teacher model
   - Temperature: 0.0-1.0 (creativity vs. consistency)
   - Top-K Documents: 5-50
   - Max Iterations: 1-5

3. **Click "Analyze"**: Start processing

4. **View Results**:
   - Main answer displayed in text area
   - Confidence gauge (0-100%)
   - Evaluation metrics (4 dimensions)
   - Supporting documents with relevance scores
   - Processing time and statistics

#### 3. Batch Processing Mode

**Usage Steps:**

1. **Input Format**: Paste queries as JSON array:
```json
[
  {
    "query": "What is Apple's revenue?"
  },
  {
    "query": "What is Microsoft's stock price?"
  }
]
```

2. **Configure Settings**: Same as interactive mode

3. **Click "Process Batch"**: Process all queries

4. **Download Results**: Export results as JSON/CSV

#### 4. System Statistics Mode

Displays:
- Total queries processed
- Average confidence score
- Processing time statistics
- Model performance metrics
- Correction rate
- Document retrieval efficiency

---

## Development Guide

### Project Structure

```
financial_intelligence_system/
├── backend/
│   ├── api.py                 # FastAPI application
│   └── __init__.py
├── frontend/
│   ├── app.py                 # Streamlit application
│   └── __init__.py
├── src/
│   ├── ingestion.py           # Data ingestion
│   ├── orchestration/
│   │   ├── langgraph_orchestrator.py
│   │   └── __init__.py
│   ├── reasoning/
│   │   ├── distillation.py
│   │   └── __init__.py
│   ├── retrieval/
│   │   ├── hybrid_retriever.py
│   │   └── __init__.py
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   └── __init__.py
│   └── __init__.py
├── config/
│   └── system_config.yaml     # System configuration
├── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_evaluation.py
│   └── __init__.py
├── examples/
│   ├── api_requests/          # API call examples
│   ├── configs/               # Configuration examples
│   ├── scripts/               # Usage scripts
│   └── notebooks/             # Jupyter notebooks
├── main.py                    # System entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image for backend
├── Dockerfile.frontend        # Container image for frontend
├── docker-compose.yml         # Multi-container setup
└── README.md
```

### Adding New Data Sources

To add a new data source, extend `DataSource` base class:

```python
# In src/ingestion.py

class CustomDataSource(DataSource):
    """Custom data source implementation"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        # Initialize your source
    
    def fetch(self, **kwargs) -> List[Document]:
        """Fetch documents from source"""
        # Implement fetching logic
        documents = []
        # ... fetch documents ...
        return documents
    
    def connect(self) -> bool:
        """Test connection to source"""
        try:
            # Test connection logic
            return True
        except:
            return False
```

Register in `main.py`:

```python
from src.ingestion import CustomDataSource

pipeline = DataIngestionPipeline()
custom_source = CustomDataSource(config={...})
pipeline.register_source('custom', custom_source)
```

### Adding Custom Evaluation Criteria

Extend `EvaluatorAgent` to add new evaluation dimensions:

```python
# In src/evaluation/evaluator.py

class CustomEvaluator(EvaluatorAgent):
    def evaluate_custom_dimension(
        self, 
        query: str, 
        answer: str, 
        context: str
    ) -> float:
        """Custom evaluation dimension (0-1)"""
        # Implement custom logic
        # Use LLM or heuristics
        return score

    def evaluate(self, query: str, answer: str, 
                context: str) -> EvaluationScore:
        base_score = super().evaluate(query, answer, context)
        custom_score = self.evaluate_custom_dimension(
            query, answer, context
        )
        # Integrate custom score
        return updated_score
```

### Modifying the Agent Workflow

Edit orchestration logic in `src/orchestration/langgraph_orchestrator.py`:

```python
class CustomOrchestrator(MultiAgentOrchestrator):
    def setup_workflow(self):
        """Define custom agent workflow"""
        self.graph = StateGraph(QueryState)
        
        # Add nodes
        self.graph.add_node("my_agent", my_agent_function)
        
        # Add edges
        self.graph.add_edge("start", "my_agent")
        self.graph.add_edge("my_agent", "end")
        
        self.workflow = self.graph.compile()
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_retrieval.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

### Test Files

| File | Purpose |
|------|---------|
| `test_ingestion.py` | Data ingestion pipeline tests |
| `test_retrieval.py` | Hybrid retrieval system tests |
| `test_reasoning.py` | Reasoning pipeline tests |
| `test_evaluation.py` | Evaluator agent tests |
| `test_orchestration.py` | Multi-agent orchestration tests |

### Example Test

```python
# tests/test_retrieval.py

import pytest
from src.retrieval.hybrid_retriever import HybridRetriever
from src.ingestion import Document

@pytest.fixture
def sample_documents():
    return [
        Document(
            id="doc1",
            content="Apple revenue was $394.3 billion",
            metadata={"source": "SEC"}
        ),
        Document(
            id="doc2",
            content="Microsoft revenue reached $198.3 billion",
            metadata={"source": "SEC"}
        ),
    ]

def test_hybrid_retriever(sample_documents):
    retriever = HybridRetriever(
        documents=sample_documents,
        alpha=0.6,
        beta=0.4
    )
    
    results = retriever.retrieve("Apple revenue", top_k=5)
    assert len(results) > 0
    assert results[0].id == "doc1"
    assert results[0].relevance > 0.8
```

---

## Deployment

### Docker Deployment

**Build and Run**

```bash
# Navigate to project
cd financial_intelligence_system

# Build images
docker-compose build

# Run services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Environment Setup**

Create `.env` file:

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
```

### Manual Deployment

**Prerequisites**

- Python 3.9+
- CUDA 11.8+ (optional, for GPU)
- Snowflake credentials (if using Snowflake)

**Installation**

```bash
# Clone and setup
git clone <repo_url>
cd financial_intelligence_system
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp config/system_config.yaml.example config/system_config.yaml
# Edit config with your settings
```

**Start Services**

```bash
# Terminal 1: Backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py

# Terminal 3 (Optional): Monitoring
python examples/scripts/system_validator.py
```

### Production Considerations

1. **Model Loading**: Use quantization (8-bit) to reduce memory usage
2. **GPU Memory**: Allocate appropriate VRAM for teacher/student models
3. **Caching**: Enable embedding cache to speed up re-used queries
4. **Logging**: Configure centralized logging for monitoring
5. **Rate Limiting**: Implement API rate limiting
6. **Security**: Use API keys for authentication
7. **Monitoring**: Track system metrics and alert on failures

---

## Troubleshooting

### Common Issues

#### 1. SSL/Certificate Errors

**Problem**: SSL verification failures when fetching from HuggingFace

**Solution**:
```python
# Already handled in main.py, but if needed:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
```

#### 2. GPU Memory Errors

**Problem**: CUDA out of memory when loading models

**Solutions**:
- Reduce model size (use smaller student model)
- Enable 8-bit quantization:
  ```yaml
  # In config/system_config.yaml
  reasoning:
    teacher_model:
      load_in_8bit: true
  ```
- Use CPU with smaller batch sizes
- Reduce `top_k` in retrieval (fewer documents to process)

#### 3. Snowflake Connection Issues

**Problem**: Cannot connect to Snowflake

**Solutions**:
- Verify credentials in `.env`
- Check network connectivity
- Ensure Snowflake warehouse is running
- Test with sample data (disable Snowflake source temporarily)

```yaml
# In config/system_config.yaml
data_ingestion:
  sources:
    snowflake:
      enabled: false  # Disable problematic source
```

#### 4. Slow Queries

**Problem**: Queries taking >30 seconds

**Solutions**:
- Reduce `top_k` (fewer documents to process)
- Reduce `max_tokens` in reasoning config
- Disable teacher model (use student only)
- Enable caching in retrieval:
  ```yaml
  retrieval:
    hybrid_retriever:
      enable_cache: true
  ```

#### 5. Low Confidence Scores

**Problem**: Answers have low confidence

**Solutions**:
- Increase `top_k` for better document coverage
- Check data quality and relevance
- Adjust evaluation weights:
  ```yaml
  evaluation:
    scoring_weights:
      relevance: 0.4  # Increase weight on document relevance
  ```
- Enable teacher model for better reasoning

#### 6. API Connection Issues

**Problem**: Frontend cannot connect to backend

**Solutions**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check backend URL in frontend config
- Allow CORS: Already configured in `backend/api.py`
- Check firewall settings

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in config
logging:
  level: DEBUG

# Run with debug output
python main.py --debug
```

### Getting Help

1. **Check Logs**: Review `logs/system.log` for error details
2. **Run Diagnostics**: `python examples/scripts/system_validator.py`
3. **Test Components**: Run individual tests: `pytest tests/ -v`
4. **Review Examples**: Check `examples/` directory for working code

---

## Appendices

### A. Glossary

| Term | Definition |
|------|-----------|
| **FAISS** | Facebook AI Similarity Search - dense vector search library |
| **BM25** | Okapi BM25 - probabilistic ranking function for text search |
| **RAG** | Retrieval-Augmented Generation - generating answers from retrieved documents |
| **LangGraph** | Framework for building agent workflows with state management |
| **Knowledge Distillation** | Technique to transfer knowledge from large to small models |
| **Temperature** | Parameter controlling randomness in model output (0=deterministic, 1=random) |
| **Entailment** | Logical relationship where one statement follows from another |

### B. Resource URLs

- [LangChain Documentation](https://python.langchain.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Snowflake Documentation](https://docs.snowflake.com/)

### C. Bibliography / References

1. OpenAI. "GPT-4 Technical Report" (2023)
2. Khandelwal, U. et al. "Generalization through the Lens of Leave-One-Out Error" (2021)
3. Gao, L. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)
4. Hinton, G., Vinyals, O., & Dean, J. "Distilling the Knowledge in a Neural Network" (2015)

---

**Document Version**: 1.0  
**Last Updated**: June 2026  
**Author**: M.Tech Dissertation Team  
**Status**: Active
