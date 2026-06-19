# FastAPI Backend for Financial Intelligence System
# Disable SSL verification for HuggingFace hub (corporate proxy / self-signed cert)
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ.setdefault("CURL_CA_BUNDLE", "")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "")

try:
    import httpx
    _OrigClient = httpx.Client
    _OrigAsync  = httpx.AsyncClient

    class _NoVerifyClient(_OrigClient):
        def __init__(self, *a, **kw):
            kw["verify"] = False
            super().__init__(*a, **kw)

    class _NoVerifyAsync(_OrigAsync):
        def __init__(self, *a, **kw):
            kw["verify"] = False
            super().__init__(*a, **kw)

    httpx.Client      = _NoVerifyClient
    httpx.AsyncClient = _NoVerifyAsync
except Exception:
    pass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging
import uuid
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Self-Correcting Financial Intelligence System",
    description="Multi-agent RAG pipeline for financial analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    """Financial query request"""
    query: str = Field(..., description="Financial question or query")
    use_teacher_model: bool = Field(False, description="Use teacher model for better accuracy")
    temperature: float = Field(0.7, ge=0.0, le=1.0)


class DocumentResult(BaseModel):
    """Retrieved document"""
    content: str
    source: str
    score: float
    metadata: Dict = {}


class EvaluationScores(BaseModel):
    """Evaluation metrics"""
    relevance: float
    factual_consistency: float
    numerical_coherence: float
    entailment: float
    overall_confidence: float
    verification_score: Optional[float] = None


class QueryResponse(BaseModel):
    """Query response"""
    query_id: str
    query: str
    answer: str
    confidence: float
    evaluation_scores: EvaluationScores
    supporting_documents: List[DocumentResult]
    iterations: int
    processing_time_ms: float
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    components: Dict[str, str]


# Global state (in production: use proper state management)
pipeline = None
processing_log = {}


def initialize_pipeline():
    """Initialize the RAG pipeline, loading documents from local files (data/ directory)."""
    global pipeline
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv(
            dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"),
            override=False,
        )

        from src.ingestion import LocalFileSource, SnowflakeSource
        from src.retrieval.hybrid_retriever import HybridRetriever
        from src.reasoning.distillation import DistillationPipeline
        from src.evaluation.evaluator import EvaluatorAgent
        from src.orchestration.langgraph_orchestrator import MultiAgentOrchestrator

        logger.info("Initializing RAG pipeline — loading documents from local files…")

        # ── Step 1: Try to load documents from local data/ directory (PRIMARY SOURCE) ─────
        doc_texts = []
        try:
            local_source = LocalFileSource(base_dir="data")
            local_docs = local_source.fetch_documents()
            if local_docs:
                doc_texts = [d.content for d in local_docs]
                logger.info(f"✅ Loaded {len(doc_texts)} documents from local data/ directory")
        except Exception as le:
            logger.warning(f"Could not load from local files: {le}")

        # ── Step 2: If no local docs, try Snowflake (SECONDARY SOURCE) ────────────────────
        if not doc_texts:
            logger.info("No local documents found — attempting Snowflake fallback…")
            try:
                sf_source = SnowflakeSource()
                sf_docs = sf_source.fetch_documents()
                if sf_docs:
                    doc_texts = [d.content for d in sf_docs]
                    logger.info(f"Loaded {len(doc_texts)} documents from Snowflake")
            except Exception as se:
                logger.warning(f"Snowflake unavailable: {se}")

        # ── Step 3: If still no docs, use fallback sample data (TERTIARY SOURCE) ─────────
        if not doc_texts:
            logger.warning("No documents from local or Snowflake — using fallback sample data")
            doc_texts = [
                "Apple Inc. 10-K filing 2023. Revenue increased 2% YoY to $383B.",
                "Microsoft Corporation financial report. Azure cloud revenue grew 28% YoY.",
                "Tesla annual report showing record production of 1.8M vehicles in 2023.",
                "Alphabet (Google) financial documentation: advertising revenue $237B.",
                "Amazon shareholder letter: AWS revenue $91B, up 13% YoY.",
                "Apple gross margin improved to 44.1% driven by services segment growth.",
                "Microsoft net income rose 20% to $72B; cloud now 54% of total revenue.",
                "Tesla operating margin compressed to 8.2% amid price cuts in 2023.",
                "Google Search revenue $175B; YouTube ads $31.5B for fiscal 2023.",
                "Amazon operating income $36.8B; AWS operating income $24.6B in 2023.",
            ]

        # Try sentence-transformer embeddings (prefer cached model). If unavailable,
        # fall back to a TF-IDF embedder and a simple dense retriever so the API remains usable offline.
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformer model (all-MiniLM-L6-v2) from cache...")
            embed_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            embeddings = embed_model.encode(doc_texts, show_progress_bar=False).astype("float32")
            logger.info(f"Encoded {len(doc_texts)} documents → shape {embeddings.shape}")

            retriever = HybridRetriever(
                documents=doc_texts,
                embeddings=embeddings,
                k=5,
                alpha=0.5,
                beta=0.5,
            )
        except Exception as se:
            logger.warning(f"SentenceTransformer unavailable or offline: {se}. Falling back to TF-IDF embedder.")

            # Lightweight TF-IDF embedder to produce stable embeddings offline
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np

            class TFIDFEmbedder:
                def __init__(self, docs: list):
                    self.vectorizer = TfidfVectorizer(max_features=2048)
                    self.doc_matrix = self.vectorizer.fit_transform(docs)

                def encode(self, texts, show_progress_bar=False):
                    # Accept single string or list
                    if isinstance(texts, str):
                        arr = self.vectorizer.transform([texts]).toarray()
                        return arr[0]
                    else:
                        return self.vectorizer.transform(list(texts)).toarray()

            # Create TF-IDF embedder and embeddings
            embed_model = TFIDFEmbedder(doc_texts)
            embeddings = embed_model.doc_matrix.toarray().astype("float32")
            logger.info(f"Created TF-IDF embeddings (offline) → shape {embeddings.shape}")

            # Try to use provided HybridRetriever; if FAISS missing, fallback to a simple retriever
            try:
                retriever = HybridRetriever(
                    documents=doc_texts,
                    embeddings=embeddings,
                    k=5,
                    alpha=0.5,
                    beta=0.5,
                )
            except Exception as hre:
                logger.warning(f"HybridRetriever/FAISS unavailable: {hre}. Using simple numpy retriever.")

                # Minimal dense retriever using cosine similarity + BM25
                from src.retrieval.hybrid_retriever import BM25Retriever

                class SimpleDenseRetriever:
                    def __init__(self, documents, embeddings, k=5, alpha=0.5, beta=0.5):
                        self.documents = documents
                        self.k = k
                        self.alpha = alpha
                        self.beta = beta
                        self.bm25 = BM25Retriever(documents, k)
                        self.embeddings = embeddings

                    def _cosine_sim(self, a, b):
                        # a: (d,), b: (n_docs, d)
                        import numpy as _np
                        if a.ndim == 1:
                            a = a.reshape(1, -1)
                        an = _np.linalg.norm(a, axis=1, keepdims=True)
                        bn = _np.linalg.norm(b, axis=1, keepdims=True)
                        denom = (an * bn.T)
                        sims = _np.dot(a, b.T) / (denom + 1e-12)
                        return sims.flatten()

                    def retrieve(self, query, query_embedding):
                        import numpy as _np
                        # BM25 scores
                        bm25_results = dict(self.bm25.retrieve(query))

                        # Dense cosine similarities
                        sims = self._cosine_sim(_np.array(query_embedding), self.embeddings)
                        faiss_results = {i: float(s) for i, s in enumerate(sims)}

                        # Combine
                        combined = {}
                        all_idx = set(bm25_results.keys()) | set(faiss_results.keys())
                        for idx in all_idx:
                            b = bm25_results.get(idx, 0.0)
                            f = faiss_results.get(idx, 0.0)
                            combined[idx] = self.alpha * f + self.beta * b

                        sorted_idx = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:self.k]
                        results = []
                        for idx, score in sorted_idx:
                            results.append({"content": self.documents[idx], "score": float(score), "source": f"document_{idx}"})
                        # Normalize to expected RetrievalResult structure used downstream
                        from types import SimpleNamespace
                        ret = []
                        for r in results:
                            ret.append(SimpleNamespace(content=r["content"], score=r["score"], source=r["source"]))
                        return ret

                retriever = SimpleDenseRetriever(doc_texts, embeddings, k=5, alpha=0.5, beta=0.5)
        reasoning = DistillationPipeline()
        evaluator = EvaluatorAgent()

        pipeline = MultiAgentOrchestrator(retriever, reasoning, evaluator,
                                          embedding_model=embed_model)
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    try:
        initialize_pipeline()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        components={
            "retrieval": "operational",
            "reasoning": "operational",
            "evaluation": "operational",
            "orchestration": "operational"
        }
    )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process financial query through RAG pipeline
    
    Args:
        request: QueryRequest with query and parameters
        
    Returns:
        QueryResponse with answer and metadata
    """
    import time
    
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        query_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Processing query {query_id}: {request.query}")
        
        # Execute workflow
        result = pipeline.execute_workflow(request.query)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Build response
        response = QueryResponse(
            query_id=query_id,
            query=request.query,
            answer=result["answer"],
            confidence=result["confidence"],
            evaluation_scores=EvaluationScores(
                **result["evaluation_scores"]
            ),
            supporting_documents=[
                DocumentResult(
                    content=doc["content"],
                    source=doc["source"],
                    score=doc["score"],
                    metadata=doc
                )
                for doc in result["supporting_docs"]
            ],
            iterations=result["iterations"],
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Log query
        processing_log[query_id] = {
            "query": request.query,
            "response": response.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Query {query_id} processed successfully "
                   f"(confidence: {result['confidence']:.3f}, time: {processing_time:.0f}ms)")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/{query_id}")
async def get_query_result(query_id: str):
    """Retrieve previous query result"""
    if query_id not in processing_log:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return processing_log[query_id]


@app.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    return {
        "total_queries": len(processing_log),
        "workflow_stats": pipeline.get_workflow_statistics(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/batch")
async def batch_query(queries: List[QueryRequest]):
    """Process multiple queries in batch"""
    results = []
    
    for query_req in queries:
        try:
            result = await process_query(query_req, BackgroundTasks())
            results.append(result)
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            results.append({"error": str(e)})
    
    return {"results": results, "total": len(results)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
