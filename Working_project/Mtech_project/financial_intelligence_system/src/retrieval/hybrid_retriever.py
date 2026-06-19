# Hybrid Retrieval System combining FAISS and BM25
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from retrieval pipeline"""
    score: float
    content: str
    source: str
    metadata: Dict


class BM25Retriever:
    """BM25-based sparse retrieval for keyword matching"""
    
    def __init__(self, documents: List[str], k: int = 5):
        """
        Initialize BM25 retriever
        
        Args:
            documents: List of documents to index
            k: Number of results to return
        """
        self.documents = documents
        self.k = k
        # Tokenize documents
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        self.avg_doc_length = np.mean([len(doc.split()) for doc in documents])
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return text.lower().split()
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate IDF for a term"""
        doc_freq = sum(1 for doc in self.tokenized_docs if term in doc)
        if doc_freq == 0:
            return 0
        return np.log((len(self.tokenized_docs) - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
    
    def _bm25_score(self, doc_idx: int, query_terms: List[str]) -> float:
        """Calculate BM25 score for a document"""
        score = 0.0
        doc_length = len(self.tokenized_docs[doc_idx])
        k1, b = 1.5, 0.75  # BM25 parameters
        
        for term in query_terms:
            idf = self._calculate_idf(term)
            term_freq = self.tokenized_docs[doc_idx].count(term)
            
            score += idf * (term_freq * (k1 + 1)) / (
                term_freq + k1 * (1 - b + b * (doc_length / self.avg_doc_length))
            )
        
        return score
    
    def retrieve(self, query: str) -> List[Tuple[int, float]]:
        """Retrieve top-k documents for query"""
        query_terms = self._tokenize(query)
        
        scores = []
        for doc_idx in range(len(self.documents)):
            score = self._bm25_score(doc_idx, query_terms)
            scores.append((doc_idx, score))
        
        # Sort by score and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:self.k]


class FAISSRetriever:
    """FAISS-based dense retrieval for semantic search"""
    
    def __init__(self, embeddings: np.ndarray, k: int = 5):
        """
        Initialize FAISS retriever
        
        Args:
            embeddings: Document embeddings (n_docs, embedding_dim)
            k: Number of results to return
        """
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            raise
        
        self.embeddings = embeddings.astype('float32')
        self.k = k
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(self.embeddings)
        
    def retrieve(self, query_embedding: np.ndarray) -> List[Tuple[int, float]]:
        """Retrieve top-k documents for query embedding"""
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, self.k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # Convert L2 distance to similarity score (0-1)
            similarity = 1.0 / (1.0 + distance)
            results.append((int(idx), float(similarity)))
        
        return results


class HybridRetriever:
    """Combines FAISS and BM25 retrieval"""
    
    def __init__(
        self,
        documents: List[str],
        embeddings: np.ndarray,
        k: int = 5,
        alpha: float = 0.5,
        beta: float = 0.5
    ):
        """
        Initialize hybrid retriever
        
        Args:
            documents: List of documents
            embeddings: Document embeddings
            k: Number of results
            alpha: Weight for FAISS scores
            beta: Weight for BM25 scores
        """
        self.documents = documents
        self.k = k
        self.alpha = alpha
        self.beta = beta
        
        self.bm25_retriever = BM25Retriever(documents, k)
        self.faiss_retriever = FAISSRetriever(embeddings, k)
        
    def retrieve(
        self,
        query: str,
        query_embedding: np.ndarray
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using hybrid approach
        
        Args:
            query: Query text
            query_embedding: Query embedding vector
            
        Returns:
            List of RetrievalResult objects
        """
        # Get results from both retrievers
        bm25_results = dict(self.bm25_retriever.retrieve(query))
        faiss_results = dict(self.faiss_retriever.retrieve(query_embedding))
        
        # Combine scores
        combined_scores = {}
        all_indices = set(bm25_results.keys()) | set(faiss_results.keys())
        
        for idx in all_indices:
            bm25_score = bm25_results.get(idx, 0.0)
            faiss_score = faiss_results.get(idx, 0.0)
            
            # Normalize and combine
            combined_score = self.alpha * faiss_score + self.beta * bm25_score
            combined_scores[idx] = combined_score
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.k]
        
        # Create RetrievalResult objects
        results = []
        for idx, score in sorted_results:
            result = RetrievalResult(
                score=score,
                content=self.documents[idx],
                source=f"document_{idx}",
                metadata={"index": idx, "query": query}
            )
            results.append(result)
        
        logger.info(f"Retrieved {len(results)} documents for query: {query}")
        return results
