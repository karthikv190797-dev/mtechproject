# API Reference Documentation

Complete reference for all REST API endpoints in the Financial Intelligence System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required (optional to implement).

## Content Type

All requests and responses use `application/json`.

---

## Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | System health check |
| POST | `/query` | Process single query |
| GET | `/query/{query_id}` | Retrieve previous query result |
| POST | `/batch` | Process multiple queries |
| GET | `/statistics` | System statistics |
| GET | `/models` | Available models info |

---

## Detailed Endpoint Documentation

### 1. Health Check

Check system status and component readiness.

**Endpoint**: `GET /health`

**Parameters**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "components": {
    "retriever": "ready",
    "reasoning": "ready",
    "evaluator": "ready",
    "orchestrator": "ready",
    "models": {
      "student": "loaded",
      "teacher": "not_loaded"
    }
  },
  "uptime_seconds": 3600,
  "timestamp": "2026-06-17T10:30:00Z"
}
```

**Status Codes**:
- `200` - All systems operational
- `503` - Service unavailable or degraded

**Example**:
```bash
curl -X GET http://localhost:8000/health
```

---

### 2. Process Single Query

Execute a single financial query with optional parameters.

**Endpoint**: `POST /query`

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "What is Apple's revenue growth rate in 2023?",
  "use_teacher_model": false,
  "temperature": 0.7,
  "top_k": 15,
  "max_iterations": 3,
  "return_supporting_docs": true
}
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✓ | - | Financial question (1-1000 chars) |
| `use_teacher_model` | boolean | | false | Use teacher (GLM-130B) vs student (Mistral-7B) |
| `temperature` | float | | 0.7 | Output randomness (0.0-1.0) |
| `top_k` | integer | | 15 | Documents to retrieve (5-50) |
| `max_iterations` | integer | | 3 | Max correction iterations (1-5) |
| `return_supporting_docs` | boolean | | true | Include retrieved documents in response |

**Response** (200 OK):
```json
{
  "query_id": "q_550e8400e29b41d4a716446655440000",
  "query": "What is Apple's revenue growth rate in 2023?",
  "answer": "Apple's revenue in fiscal year 2023 was $394.3 billion, representing a 2% increase from fiscal 2022's $394.3 billion. However, net income declined to $96.995 billion from $99.803 billion, indicating margin compression despite stable revenues.",
  "confidence": 0.92,
  "evaluation_scores": {
    "relevance": 0.95,
    "factuality": 0.90,
    "numerical_coherence": 0.90,
    "entailment": 0.88,
    "combined": 0.92
  },
  "supporting_documents": [
    {
      "document_id": "apple_10k_2023",
      "title": "Apple Inc. Form 10-K Filing 2023",
      "source": "SEC EDGAR",
      "relevance_score": 0.97,
      "excerpt": "Apple reported total net sales of $394.3 billion for fiscal year 2023, compared to $394.3 billion in fiscal 2022.",
      "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K",
      "metadata": {
        "filing_date": "2023-11-30",
        "fiscal_period": "2023"
      }
    },
    {
      "document_id": "apple_earnings_transcript_q4_2023",
      "title": "Apple Q4 2023 Earnings Call Transcript",
      "source": "Earnings Call",
      "relevance_score": 0.94,
      "excerpt": "We had a strong fourth quarter with total net sales of $119.6 billion...",
      "url": "...",
      "metadata": {
        "date": "2023-10-31",
        "quarter": "Q4 2023"
      }
    }
  ],
  "evaluation_history": [
    {
      "iteration": 1,
      "agent": "reasoning",
      "confidence": 0.75,
      "scores": {
        "relevance": 0.92,
        "factuality": 0.80,
        "numerical_coherence": 0.85,
        "entailment": 0.75
      },
      "action": "Initial student model inference",
      "reason": null
    },
    {
      "iteration": 2,
      "agent": "correction",
      "confidence": 0.92,
      "scores": {
        "relevance": 0.95,
        "factuality": 0.90,
        "numerical_coherence": 0.90,
        "entailment": 0.88
      },
      "action": "Teacher model refinement",
      "reason": "Low factuality score (0.80) - teacher model provided fact checking"
    }
  ],
  "processing_stats": {
    "total_time_ms": 2345,
    "retrieval_time_ms": 234,
    "reasoning_time_ms": 1500,
    "evaluation_time_ms": 300,
    "correction_iterations": 1,
    "documents_retrieved": 15,
    "tokens_generated": 156
  },
  "created_at": "2026-06-17T10:30:00Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `query_id` | string | Unique query identifier for tracking |
| `query` | string | Original query text |
| `answer` | string | Generated answer |
| `confidence` | float (0-1) | Overall confidence score |
| `evaluation_scores` | object | Multi-dimensional scores |
| `supporting_documents` | array | Retrieved relevant documents |
| `evaluation_history` | array | Correction iteration history |
| `processing_stats` | object | Performance metrics |
| `created_at` | ISO 8601 | Timestamp of query processing |

**Error Responses**:

- **400 Bad Request** - Invalid parameters
```json
{
  "detail": "Query must be non-empty string",
  "error_code": "INVALID_QUERY"
}
```

- **422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

- **503 Service Unavailable** - Backend unavailable
```json
{
  "detail": "Service temporarily unavailable",
  "retry_after": 30
}
```

**Example - Using curl**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Apple revenue?",
    "temperature": 0.7,
    "top_k": 15
  }'
```

**Example - Using Python**:
```python
import requests
import json

url = "http://localhost:8000/query"
payload = {
    "query": "What is Apple's revenue growth?",
    "use_teacher_model": False,
    "temperature": 0.7,
    "top_k": 15,
    "max_iterations": 3
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Processing time: {result['processing_stats']['total_time_ms']}ms")
```

**Example - Using JavaScript**:
```javascript
const query = "What is Apple's revenue?";

fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: query,
        temperature: 0.7,
        top_k: 15
    })
})
.then(response => response.json())
.then(data => {
    console.log('Answer:', data.answer);
    console.log('Confidence:', (data.confidence * 100).toFixed(1) + '%');
    console.log('Time:', data.processing_stats.total_time_ms + 'ms');
});
```

---

### 3. Retrieve Query Result

Get a previously processed query result by ID.

**Endpoint**: `GET /query/{query_id}`

**Parameters**:
- `query_id` (path) - Query ID from previous response

**Response** (200 OK):
Same as query endpoint response (cached result)

**Error Responses**:
- **404 Not Found** - Query not found
```json
{
  "detail": "Query not found",
  "query_id": "q_invalid_id"
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/query/q_550e8400e29b41d4a716446655440000
```

---

### 4. Batch Processing

Process multiple queries in a single batch.

**Endpoint**: `POST /batch`

**Request Body**:
```json
{
  "queries": [
    "What is Apple's revenue?",
    "What is Microsoft's earnings per share?",
    "Compare Google and Facebook revenue"
  ],
  "use_teacher_model": false,
  "temperature": 0.7,
  "top_k": 15,
  "max_iterations": 3
}
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `queries` | array | ✓ | - | Array of query strings (1-100 queries) |
| Other params | - | | - | Same as single query endpoint |

**Response** (200 OK):
```json
{
  "batch_id": "batch_660f9511f30b51e5b716446655440000",
  "total_queries": 3,
  "processed_queries": 3,
  "failed_queries": 0,
  "results": [
    {
      "query_id": "q_1",
      "query": "What is Apple's revenue?",
      "answer": "Apple's revenue in 2023 was $394.3 billion...",
      "confidence": 0.92,
      "evaluation_scores": {
        "relevance": 0.95,
        "factuality": 0.90,
        "numerical_coherence": 0.90,
        "entailment": 0.88
      },
      "processing_time_ms": 2345
    },
    {
      "query_id": "q_2",
      "query": "What is Microsoft's earnings per share?",
      "answer": "Microsoft's EPS for fiscal 2023 was...",
      "confidence": 0.88,
      "evaluation_scores": {
        "relevance": 0.93,
        "factuality": 0.88,
        "numerical_coherence": 0.89,
        "entailment": 0.83
      },
      "processing_time_ms": 2156
    },
    {
      "query_id": "q_3",
      "query": "Compare Google and Facebook revenue",
      "answer": "Comparing fiscal year revenues: Google generated $307.4 billion...",
      "confidence": 0.85,
      "evaluation_scores": {
        "relevance": 0.90,
        "factuality": 0.85,
        "numerical_coherence": 0.87,
        "entailment": 0.80
      },
      "processing_time_ms": 2234
    }
  ],
  "batch_stats": {
    "total_time_ms": 7500,
    "avg_time_per_query_ms": 2500,
    "total_tokens_generated": 450,
    "total_documents_retrieved": 45,
    "avg_confidence": 0.88,
    "total_iterations": 5
  },
  "created_at": "2026-06-17T10:35:00Z"
}
```

**Error Responses**:
- **400 Bad Request** - Invalid batch format
```json
{
  "detail": "Batch must contain 1-100 queries",
  "provided_queries": 200
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What is Apple revenue?",
      "What is Microsoft earnings?"
    ],
    "temperature": 0.7
  }'
```

---

### 5. System Statistics

Get overall system performance and usage statistics.

**Endpoint**: `GET /statistics`

**Parameters**: None

**Response** (200 OK):
```json
{
  "uptime_minutes": 120,
  "timestamp": "2026-06-17T10:45:00Z",
  "query_statistics": {
    "total_queries": 45,
    "total_batches": 3,
    "total_individual_queries": 45,
    "avg_confidence": 0.89,
    "confidence_distribution": {
      "high": {
        "range": "0.8-1.0",
        "count": 38,
        "percentage": 84.4
      },
      "medium": {
        "range": "0.6-0.8",
        "count": 6,
        "percentage": 13.3
      },
      "low": {
        "range": "0.0-0.6",
        "count": 1,
        "percentage": 2.2
      }
    }
  },
  "performance_stats": {
    "avg_total_time_ms": 2234,
    "min_time_ms": 1234,
    "max_time_ms": 5678,
    "p50_time_ms": 2100,
    "p95_time_ms": 3500,
    "p99_time_ms": 4200
  },
  "component_stats": {
    "retrieval": {
      "avg_documents_retrieved": 18,
      "avg_retrieval_time_ms": 234,
      "total_retrievals": 45,
      "cache_hit_rate": 0.22
    },
    "reasoning": {
      "avg_inference_time_ms": 1500,
      "avg_tokens_generated": 156,
      "student_model_usage": 45,
      "teacher_model_usage": 5
    },
    "evaluation": {
      "avg_evaluation_time_ms": 300,
      "avg_relevance_score": 0.93,
      "avg_factuality_score": 0.88,
      "avg_numerical_coherence": 0.87,
      "avg_entailment_score": 0.85,
      "correction_rate": 0.13
    }
  },
  "model_stats": {
    "teacher_model": {
      "model_name": "THUDM/glm-130b-chat",
      "status": "not_loaded",
      "memory_usage_mb": 0
    },
    "student_model": {
      "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
      "status": "loaded",
      "memory_usage_mb": 14500
    }
  },
  "system_health": {
    "memory_usage_percent": 68,
    "gpu_memory_usage_percent": 85,
    "disk_space_available_gb": 150,
    "error_rate": 0.02,
    "last_error": "Low confidence in query #42",
    "last_error_time": "2026-06-17T10:40:00Z"
  }
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/statistics
```

---

### 6. Available Models

Get information about available models.

**Endpoint**: `GET /models`

**Response** (200 OK):
```json
{
  "models": {
    "student": {
      "name": "Mistral-7B-Instruct-v0.2",
      "provider": "mistralai",
      "size_parameters": 7000000000,
      "quantization": "fp16",
      "loaded": true,
      "memory_required_gb": 14,
      "inference_speed_tokens_per_second": 10,
      "capabilities": [
        "text_generation",
        "instruction_following",
        "financial_qa"
      ]
    },
    "teacher": {
      "name": "GLM-130B-Chat",
      "provider": "THUDM",
      "size_parameters": 130000000000,
      "quantization": "int8",
      "loaded": false,
      "memory_required_gb": 64,
      "inference_speed_tokens_per_second": 2,
      "capabilities": [
        "text_generation",
        "deep_reasoning",
        "knowledge_distillation"
      ]
    },
    "embeddings": {
      "name": "all-MiniLM-L6-v2",
      "provider": "sentence-transformers",
      "embedding_dimension": 384,
      "model_size_mb": 22,
      "loaded": true,
      "inference_speed_embeddings_per_second": 500
    }
  },
  "retrieval_indices": {
    "dense": {
      "type": "FAISS",
      "documents_indexed": 10000,
      "index_size_mb": 2048,
      "search_latency_ms": 50
    },
    "sparse": {
      "type": "BM25",
      "documents_indexed": 10000,
      "index_size_mb": 512,
      "search_latency_ms": 100
    }
  }
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this format:

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-06-17T10:30:00Z",
  "request_id": "req_550e8400e29b41d4a716446655440000"
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_QUERY` | 400 | Query parameter invalid |
| `INVALID_PARAMETER` | 400 | Invalid request parameter |
| `VALIDATION_ERROR` | 422 | Request body validation failed |
| `RESOURCE_NOT_FOUND` | 404 | Query result not found |
| `SERVICE_UNAVAILABLE` | 503 | Backend unable to process |
| `TIMEOUT` | 504 | Request exceeded timeout |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Rate Limiting

Default limits (optional implementation):

- `/query`: 10 requests per minute per IP
- `/batch`: 2 requests per minute per IP
- `/statistics`: 60 requests per minute per IP

**Rate Limit Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1686057000
```

**429 Too Many Requests**:
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## Pagination (Future Feature)

Planned for large batch results:

```json
{
  "results": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_results": 150,
    "total_pages": 3,
    "has_next": true,
    "next_url": "/batch?page=2"
  }
}
```

---

## Webhooks (Future Feature)

Planned for long-running batch operations:

```bash
# Register webhook
curl -X POST http://localhost:8000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-api.com/finiq-callback",
    "events": ["batch_completed", "batch_failed"]
  }'

# Start batch with webhook notification
curl -X POST http://localhost:8000/batch \
  -d '{
    "queries": [...],
    "webhook_url": "https://your-api.com/finiq-callback"
  }'
```

---

## SDK/Client Libraries

### Python Client

```python
from requests import Session

class FinIQClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = Session()
    
    def query(self, question: str, **kwargs):
        response = self.session.post(
            f"{self.base_url}/query",
            json={"query": question, **kwargs}
        )
        response.raise_for_status()
        return response.json()
    
    def batch(self, queries: list, **kwargs):
        response = self.session.post(
            f"{self.base_url}/batch",
            json={"queries": queries, **kwargs}
        )
        response.raise_for_status()
        return response.json()
    
    def get_result(self, query_id: str):
        response = self.session.get(
            f"{self.base_url}/query/{query_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def stats(self):
        response = self.session.get(
            f"{self.base_url}/statistics"
        )
        response.raise_for_status()
        return response.json()

# Usage
client = FinIQClient()
result = client.query("What is Apple's revenue?")
print(result['answer'])
```

---

## OpenAPI/Swagger

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

**Document Version**: 1.0  
**Last Updated**: June 2026
