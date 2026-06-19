# Architecture and Design Documentation

## System Architecture Overview

### High-Level System Design

The Self-Correcting Financial Intelligence System is built on a modular, agent-based architecture that combines multiple advanced AI/ML techniques:

```
┌────────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                            │
├────────────────────────────────────────────────────────────────┤
│  Streamlit WebUI (Interactive)  │  REST API (Programmatic)     │
└────────┬──────────────────────────────────────┬─────────────────┘
         │                                       │
         └──────────────────┬────────────────────┘
                            │
         ┌──────────────────▼─────────────────────┐
         │    Multi-Agent Orchestrator (LangGraph) │
         ├──────────────────────────────────────┤
         │ • Workflow Management                 │
         │ • Agent Coordination                  │
         │ • State Management                    │
         │ • Dynamic Routing                     │
         └──────────────────┬────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼───────┐  ┌───────▼────────┐  ┌──────▼─────┐
    │ Reasoning │  │  Evaluation    │  │ Retrieval  │
    │ Pipeline  │  │  Agent         │  │ System     │
    │           │  │                │  │            │
    │ Teacher/  │  │ Multi-criteria │  │ Dense +    │
    │ Student   │  │ Scoring        │  │ Sparse     │
    │ Models    │  │ (4 dimensions) │  │ Indices    │
    └───┬───────┘  └───────┬────────┘  └──────┬─────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
            ┌───────────────▼────────────────┐
            │  Data Layer & Models           │
            ├────────────────────────────────┤
            │ • Embedding Store              │
            │ • Document Index               │
            │ • Model Weights (Disk)         │
            │ • Configuration                │
            └────────────────────────────────┘
                            │
            ┌───────────────▼────────────────┐
            │  Data Sources                  │
            ├────────────────────────────────┤
            │ • SEC EDGAR                    │
            │ • Snowflake DW                 │
            │ • Local Files                  │
            └────────────────────────────────┘
```

---

## Core Architectural Components

### 1. Data Ingestion Layer

**Responsibility**: Fetch, normalize, and prepare documents from multiple sources

**Components**:
- `DataIngestionPipeline`: Main orchestrator
- `SECFilingSource`: SEC EDGAR integration
- `SnowflakeSource`: Snowflake data warehouse integration
- `LocalFileSource`: File-based ingestion
- `Document`: Internal document representation

**Data Flow**:
```
Raw Data (PDF, Text, SQL) 
    ↓
[Fetch & Validate]
    ↓
[Extract & Parse] 
    ↓
[Normalize Format]
    ↓
[Split into Chunks]
    ↓
[Extract Metadata]
    ↓
Document Objects {
    id, content, metadata, source, timestamp
}
```

**Key Classes**:
```python
class Document:
    id: str                          # Unique document ID
    content: str                     # Main document text
    metadata: Dict[str, Any]         # Document metadata
    source: str                      # Data source
    chunk_index: int                 # Position in chunked set
    timestamp: datetime              # Ingestion time

class DataSource(ABC):
    """Base class for data sources"""
    @abstractmethod
    def fetch(...) -> List[Document]: pass
    
    @abstractmethod
    def connect() -> bool: pass
```

---

### 2. Retrieval System

**Responsibility**: Find most relevant documents for a query

**Architecture**: Hybrid retrieval combining:
- **Dense Retrieval**: Vector similarity using FAISS
- **Sparse Retrieval**: Keyword matching using BM25
- **Fusion**: Weighted combination of both signals

**Workflow**:
```
Query Input
    ↓
[Tokenize & Embed]  ──────────────────┐
    ↓                                   │
[Dense Search - FAISS]                │
    ↓                                   │
[Top-K Dense Results] (scores: 0-1)  │
    ├─────────────────────────────────┤
    │                                   │
    │         [Normalize Scores]       │
    │                                   │
[Sparse Search - BM25]                │
    ↓                                   │
[Top-K Sparse Results] (scores: 0-1) │
    │                                   │
    └──────────────┬────────────────┬──┘
                   │                │
            [Weighted Fusion]    [Combine]
                   │                │
            score = α*dense + β*sparse
                   │
            [Re-rank Results]
                   │
            [Final Top-K Documents]
```

**Key Parameters**:
| Parameter | Purpose | Default |
|-----------|---------|---------|
| `alpha` | Dense retrieval weight | 0.6 |
| `beta` | Sparse retrieval weight | 0.4 |
| `top_k` | Documents to retrieve | 20 |
| `threshold` | Minimum relevance score | 0.3 |

**Implementation**:
```python
class HybridRetriever:
    def __init__(
        self, 
        documents: List[Document],
        alpha: float = 0.6,
        beta: float = 0.4
    ):
        self.faiss_index = build_dense_index(documents)
        self.bm25_index = build_sparse_index(documents)
        self.alpha = alpha
        self.beta = beta
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 20
    ) -> List[RetrievedDocument]:
        # Dense search
        dense_results = self.faiss_index.search(query, k=top_k)
        
        # Sparse search
        sparse_results = self.bm25_index.search(query, k=top_k)
        
        # Fusion
        combined = self._fuse_results(
            dense_results, 
            sparse_results,
            self.alpha, 
            self.beta
        )
        
        return combined[:top_k]
```

---

### 3. Reasoning Pipeline (Knowledge Distillation)

**Responsibility**: Generate answers from retrieved documents

**Model Architecture**:
- **Teacher Model**: GLM-130B (deep reasoning, slow)
- **Student Model**: Mistral-7B (fast inference, deployment-ready)
- **Knowledge Distillation**: Transfer knowledge from teacher to student

**Workflow**:
```
Retrieved Documents + Query
         │
         ├─ INFERENCE PATH (Student Model - Normal Use)
         │           │
         │      [Tokenize]
         │           │
         │  [Student Model Forward Pass]
         │           │
         │  [Logits → Probabilities]
         │           │
         │  [Temperature-scaled Sampling]
         │           │
         │      [Generated Answer]
         │
         ├─ TRAINING PATH (Teacher Model - Correction)
         │           │
         │  [Teacher: Deep Reasoning]
         │           │
         │  [Knowledge Distillation Loss]
         │  └─ KL_divergence(student_probs, teacher_probs)
         │           │
         │  [Update Student Weights]
         │
    Final Answer (refined by teacher if needed)
```

**Key Classes**:
```python
class DistillationPipeline:
    def __init__(
        self,
        teacher_model: str = "GLM-130B",
        student_model: str = "Mistral-7B"
    ):
        self.teacher = load_model(teacher_model, load_in_8bit=True)
        self.student = load_model(student_model)
    
    def infer(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """Generate answer using student model"""
        return self.student.generate(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def refine_with_teacher(
        self,
        prompt: str,
        student_answer: str
    ) -> str:
        """Use teacher model for deep reasoning"""
        refined = self.teacher.generate(
            prompt,
            context=student_answer
        )
        return refined
    
    def distill(
        self,
        training_data: List[TrainingExample]
    ) -> None:
        """Train student model using teacher knowledge"""
        for epoch in range(num_epochs):
            for batch in training_data:
                student_output = self.student(batch.input)
                teacher_output = self.teacher(batch.input)
                
                loss = kl_divergence(
                    student_output.logits,
                    teacher_output.logits
                )
                loss.backward()
                optimizer.step()
```

---

### 4. Evaluation System

**Responsibility**: Multi-dimensional quality assessment of answers

**Evaluation Dimensions**:

| Dimension | Definition | Calculation |
|-----------|-----------|-------------|
| **Relevance** | How well answer addresses query | Semantic similarity between query-answer |
| **Factuality** | Alignment with retrieved documents | Named entity matching, fact verification |
| **Numerical Coherence** | Consistency of numbers/metrics | Range check, mathematical consistency |
| **Entailment** | Logical relationship | NLI classifier on answer vs. context |

**Scoring Process**:
```
Query, Answer, Context (retrieved docs)
         │
    ┌────┴────┐
    │          │
[Relevance] [Factuality] [Numerical] [Entailment]
Analysis    Analysis      Coherence   Analysis
    │          │            │           │
  0.92       0.88          0.85        0.90
    │          │            │           │
    └────┬─────┴────┬───────┴──────┬────┘
         │          │               │
    [Apply Weights] (shared: 0-1)
    ├─ 0.35 * relevance
    ├─ 0.35 * factuality
    ├─ 0.20 * numerical
    └─ 0.10 * entailment
         │
    Combined Score: 0.89
         │
    ├─ >= 0.75? → High Confidence ✓
    └─ < 0.75?  → Trigger Correction
```

**Correction Trigger Logic**:
```python
if score < min_confidence_threshold:
    # Low confidence - initiate correction
    teacher_refined = reasoning_pipeline.refine_with_teacher(...)
    revised_score = evaluator.evaluate(teacher_refined, ...)
    
    if revised_score > previous_score:
        # Improvement - use refined answer
        answer = teacher_refined
    
    if iterations < max_iterations:
        # Continue correction loop
        iterate()
```

---

### 5. Multi-Agent Orchestrator

**Responsibility**: Coordinate agents in controlled workflow using LangGraph

**Agent Definitions**:

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Retriever** | Fetch documents | Query | Top-k docs |
| **Reader** | Prepare context | Docs qty | Formatted context |
| **Reasoning** | Generate answer | Context | Answer text |
| **Evaluator** | Score quality | Query+answer+context | Scores & confidence |
| **Verifier** | Cross-check | Answer vs context | Verification status |
| **Correction** | Refine answer | Low-score answer | Improved answer |

**State Management**:
```python
class QueryState:
    query: str                          # Original query
    documents: List[Document]           # Retrieved docs
    context: str                        # Formatted context
    answer: str                         # Generated answer
    confidence: float                   # Confidence score
    evaluation_scores: EvaluationScore  # 4D scores
    iteration: int                      # Correction iteration
    history: List[StateSnapshot]        # Decision history
    final_result: QueryResult           # Final response
```

**Workflow Graph**:
```
START
  │
  ├─ [Retriever: fetch top-k docs]
  │           │
  │           ▼
  ├─ [Reader: prepare context]
  │           │
  │           ▼
  ├─ [Reasoning: generate answer]
  │           │
  │           ▼
  ├─ [Evaluator: score answer]
  │           │
  │           ▼
  └─ DECISION: confidence >= threshold?
              │                    │
             YES                   NO
              │                    │
              ▼                    ▼
         [Verifier]        [Correction Agent]
              │                    │
              │              [Re-evaluate]
              │                    │
              │          DECISION: iterations < max?
              │                    │
              │                 YES│
              │                    ▼
              │              [Loop back]
              │                    │
              │              iterations++
              │                    │
              │                   MAX reached
              │                    │
              ▼                    ▼
         ────────────────────────────
                       │
                       ▼
                  CONSTRUCT RESPONSE
                  (answer + scores + docs)
                       │
                       ▼
                      END
```

**Implementation**:
```python
class MultiAgentOrchestrator:
    def __init__(self, config):
        self.graph = StateGraph(QueryState)
        self.setup_workflow()
    
    def setup_workflow(self):
        # Add nodes (agents)
        self.graph.add_node("retriever", self.retriever_node)
        self.graph.add_node("reader", self.reader_node)
        self.graph.add_node("reasoning", self.reasoning_node)
        self.graph.add_node("evaluator", self.evaluator_node)
        self.graph.add_node("verifier", self.verifier_node)
        self.graph.add_node("correction", self.correction_node)
        
        # Add edges
        self.graph.add_edge("START", "retriever")
        self.graph.add_edge("retriever", "reader")
        self.graph.add_edge("reader", "reasoning")
        self.graph.add_edge("reasoning", "evaluator")
        
        # Conditional edge based on confidence
        self.graph.add_conditional_edges(
            "evaluator",
            self.check_confidence,
            {
                "verify": "verifier",
                "correct": "correction"
            }
        )
        
        self.graph.add_edge("verifier", "END")
        self.graph.add_edge("correction", "evaluator")
        
        self.workflow = self.graph.compile()
    
    def execute_workflow(self, query: str) -> QueryResult:
        initial_state = QueryState(
            query=query,
            iteration=0
        )
        
        final_state = self.workflow.invoke(initial_state)
        
        return self.construct_response(final_state)
```

---

## Data Models and Schemas

### Document Schema

```python
@dataclass
class Document:
    """Internal document representation"""
    id: str                               # Unique ID
    content: str                          # Full text
    title: Optional[str]                  # Document title
    source: str                           # Data source (SEC, Snowflake, etc.)
    chunk_index: int                      # Position in chunked document
    metadata: Dict[str, Any]              # Custom metadata
    embedding: Optional[np.ndarray]       # Dense embedding vector (386D)
    indexed_at: datetime                  # When ingested
    
@dataclass
class RetrievedDocument:
    """Document with relevance score"""
    document: Document
    relevance: float                      # 0-1 relevance score
    dense_score: float                    # FAISS similarity
    sparse_score: float                   # BM25 score
    rank: int                             # Position in results

@dataclass
class EvaluationScore:
    """Multi-dimensional evaluation"""
    relevance: float                      # 0-1
    factuality: float                     # 0-1
    numerical_coherence: float            # 0-1
    entailment: float                     # 0-1
    combined: float                       # Weighted combination
    
@dataclass
class QueryResult:
    """Final query response"""
    query_id: str
    query: str
    answer: str
    confidence: float
    evaluation_scores: EvaluationScore
    supporting_documents: List[RetrievedDocument]
    evaluation_history: List[EvaluationRecord]
    processing_stats: ProcessingStats
```

---

## Design Patterns Used

### 1. **Pipeline Pattern**
- **Used in**: Data Ingestion, Distillation
- **Purpose**: Sequential processing with transformation at each step
- **Benefits**: Modularity, reusability, testability

### 2. **Agent Pattern**
- **Used in**: Multi-Agent Orchestration
- **Purpose**: Independent agents with specific roles coordinated by orchestrator
- **Benefits**: Separation of concerns, scalability

### 3. **Strategy Pattern**
- **Used in**: Data Sources, Evaluation Metrics
- **Purpose**: Interchangeable implementations for different sources/metrics
- **Benefits**: Extensibility, flexibility

### 4. **State Machine Pattern**
- **Used in**: Query Workflow (LangGraph)
- **Purpose**: Manage state transitions in agent workflow
- **Benefits**: Clear control flow, history tracking

### 5. **Decorator Pattern**
- **Used in**: Logging, Caching middleware
- **Purpose**: Add functionality without modifying core classes
- **Benefits**: Separation of concerns, DRY principle

### 6. **Factory Pattern**
- **Used in**: Model loading, Source creation
- **Purpose**: Centralized object creation
- **Benefits**: Configuration-driven behavior, easier testing

---

## Resource Allocation and Performance

### Memory Requirements

| Component | Memory | Notes |
|-----------|--------|-------|
| Teacher Model (GLM-130B) | 60-80 GB | 8-bit quantization |
| Student Model (Mistral-7B) | 14-16 GB | Full precision |
| FAISS Index | ~2 GB | For 10K documents |
| BM25 Index | ~500 MB | Tokenized documents |
| Embeddings Cache | ~2 GB | 10K documents × 384D |
| Python Runtime | 2-4 GB | Dependencies + overhead |
| **Total** | **80-108 GB** | With both models active |

### Compute Requirements

| Operation | Time (10K docs) | Speed-up |
|-----------|-----------------|----------|
| Embedding Generation | 5-10 min | Can be parallelized |
| Index Build (FAISS) | 2-3 min | One-time cost |
| Index Build (BM25) | 1-2 min | One-time cost |
| Dense Retrieval | 50-100 ms | O(log N) with HNSW |
| Sparse Retrieval | 100-200 ms | O(M) with inverted index |
| Student Inference | 500-1000 ms | O(sequence_length) |
| Teacher Inference | 2000-5000 ms | O(sequence_length) |
| Evaluation | 200-500 ms | Multi-metric computation |

### Optimization Strategies

1. **Embedding Cache**: Avoid re-computing embeddings for repeated queries
2. **Batch Processing**: Process multiple queries together
3. **Model Quantization**: Use 8-bit for large models
4. **Index Optimization**: Use HNSW for faster dense search
5. **Async Operations**: Non-blocking I/O for API calls
6. **Result Caching**: Cache frequent query results

---

## Security and Validation

### Input Validation

```python
# Query validation
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    temperature: float = Field(..., ge=0.0, le=1.0)
    top_k: int = Field(default=20, ge=5, le=50)
    max_iterations: int = Field(default=3, ge=1, le=5)

# Validation happens automatically in FastAPI
```

### Authentication (Optional)

```python
# JWT token validation
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    # Verify JWT token
    # Return user info or raise exception
    pass
```

### Rate Limiting

```python
# Protect API endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("10/minute")
async def query_endpoint(...):
    pass
```

---

## Extensibility Points

### Adding New Data Sources

1. Inherit from `DataSource` base class
2. Implement `fetch()` and `connect()` methods
3. Register in pipeline via `register_source()`

### Adding New Evaluation Metrics

1. Extend `EvaluatorAgent` class
2. Implement custom metric calculation
3. Update `evaluation_scores` weight distribution

### Adding New Reasoning Models

1. Modify model loading in `DistillationPipeline`
2. Update prompt templates in `reasoning_node()`
3. Configure in `system_config.yaml`

### Adding New Retrieval Methods

1. Implement retriever inheriting from `BaseRetriever`
2. Support same interface (`retrieve()` method)
3. Integrate in hybrid retriever fusion logic

---

## Error Handling and Resilience

### Graceful Degradation

```python
# Fallback chain
try:
    data = fetch_from_snowflake()  # Primary source
except SnowflakeError:
    logger.warning("Snowflake unavailable, using SEC EDGAR")
    data = fetch_from_sec()
except SECError:
    logger.warning("All sources unavailable, using sample data")
    data = load_sample_data()
```

### Retry Mechanisms

```python
@retry(max_attempts=3, backoff=2)
def fetch_with_retry(source, query):
    return source.fetch(query)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args):
        if self.state == "OPEN":
            raise CircuitBreakerOpen()
        try:
            result = func(*args)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "OPEN"
            raise
```

---

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Test edge cases and error conditions

### Integration Tests
- Test component interactions
- Use sample data
- Verify end-to-end workflows

### Performance Tests
- Measure latency and throughput
- Profile memory usage
- Benchmark model inference times

### Acceptance Tests
- Verify business requirements
- Test with realistic data
- Validate output quality

---

## Monitoring and Observability

### Key Metrics

```python
# Prometheus metrics
query_latency = Histogram('query_latency_ms')
retrieval_time = Histogram('retrieval_time_ms')
answer_confidence = Histogram('answer_confidence')
model_inference_time = Histogram('model_inference_ms')
evaluation_scores = Gauge('evaluation_score')
error_rate = Counter('error_count_total')
correction_rate = Gauge('correction_rate')
```

### Logging Strategy

```python
logger.info(f"Query {query_id} started")
logger.debug(f"Retrieved {len(docs)} documents")
logger.warning(f"Low confidence score: {score}")
logger.error(f"Model inference failed: {error}")
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "components": {
            "retriever": check_retriever(),
            "reasoning": check_models(),
            "evaluator": check_evaluator(),
            "database": check_snowflake()
        }
    }
```

---

## Deployment Architecture

### Single Machine Deployment
```
Machine (80GB RAM, 4 GPUs)
├── Backend Service (port 8000)
├── Frontend Service (port 8501)
└── Data/Models (disk)
```

### Distributed Deployment (Future)
```
Load Balancer
├── API Server 1 (FastAPI)
├── API Server N (FastAPI)
├── Shared Cache (Redis)
├── Shared Storage (S3/NFS)
└── Message Queue (RabbitMQ)
```

---

**Document Version**: 1.0  
**Last Updated**: June 2026
