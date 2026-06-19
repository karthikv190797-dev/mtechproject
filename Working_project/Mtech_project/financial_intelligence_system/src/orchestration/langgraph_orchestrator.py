# LangGraph-based Multi-Agent Orchestration
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent states in the workflow"""
    IDLE = "idle"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CORRECTION_NEEDED = "correction_needed"


@dataclass
class WorkflowState:
    """State object passed through workflow"""
    query: str
    documents: List[str] = field(default_factory=list)
    query_embedding: Any = None
    retrieved_docs: List[Dict] = field(default_factory=list)
    answer: str = ""
    confidence: float = 0.0
    evaluation_scores: Dict = field(default_factory=dict)
    correction_actions: List[str] = field(default_factory=list)
    final_answer: str = ""
    iteration: int = 0
    max_iterations: int = 3


class MultiAgentOrchestrator:
    """Orchestrates multi-agent RAG pipeline using LangGraph principles"""
    
    def __init__(
        self,
        retriever,
        reasoning_pipeline,
        evaluator,
        embedding_model=None
    ):
        """
        Initialize orchestrator
        
        Args:
            retriever: Hybrid retrieval system
            reasoning_pipeline: Teacher-student distillation
            evaluator: Evaluator agent
            embedding_model: Model for creating query embedding
        """
        self.retriever = retriever
        self.reasoning_pipeline = reasoning_pipeline
        self.evaluator = evaluator
        self.embedding_model = embedding_model
        self.workflow_history = []
        
        logger.info("Initialized multi-agent orchestrator")
    
    def _retriever_agent(self, state: WorkflowState) -> WorkflowState:
        """Retriever agent node"""
        logger.info(f"[Retriever] Processing query: {state.query}")
        
        # Generate query embedding
        if self.embedding_model:
            state.query_embedding = self.embedding_model.encode(state.query)
        else:
            import numpy as np
            # Dimension must match FAISS index; default matches main.py's sample_embeddings (384)
            faiss_dim = self.retriever.faiss_retriever.index.d
            state.query_embedding = np.random.randn(faiss_dim)
        
        # Retrieve documents
        retrieved = self.retriever.retrieve(state.query, state.query_embedding)
        state.retrieved_docs = [
            {
                "content": r.content,
                "score": r.score,
                "source": r.source
            }
            for r in retrieved
        ]
        
        logger.info(f"[Retriever] Retrieved {len(state.retrieved_docs)} documents")
        return state
    
    def _reader_agent(self, state: WorkflowState) -> WorkflowState:
        """Reader agent node - extracts and prepares context"""
        logger.info("[Reader] Preparing evidence")
        
        # Extract top documents for context
        context = [doc["content"] for doc in state.retrieved_docs[:3]]
        state.documents = context
        
        logger.info(f"[Reader] Prepared {len(context)} documents as context")
        return state
    
    def _reasoning_agent(self, state: WorkflowState) -> WorkflowState:
        """Reasoning agent node"""
        logger.info("[Reasoning] Performing inference")
        
        # Use student model by default
        result = self.reasoning_pipeline.infer(
            state.query,
            state.documents,
            use_teacher=False
        )
        
        state.answer = result.answer
        state.confidence = result.confidence
        
        logger.info(f"[Reasoning] Generated answer with confidence: {state.confidence:.3f}")
        return state
    
    def _evaluator_agent(self, state: WorkflowState) -> WorkflowState:
        """Evaluator agent node"""
        logger.info("[Evaluator] Assessing response quality")
        
        evaluation = self.evaluator.evaluate_response(
            state.query,
            state.answer,
            state.documents
        )
        
        state.evaluation_scores = {
            "relevance": evaluation.relevance_score,
            "factual_consistency": evaluation.factual_consistency,
            "numerical_coherence": evaluation.numerical_coherence,
            "entailment": evaluation.entailment_score,
            "overall_confidence": evaluation.overall_confidence
        }
        
        if evaluation.correction_needed:
            correction_prompt = self.evaluator.get_correction_prompt(
                state.query,
                evaluation
            )
            state.correction_actions.append(correction_prompt)
        
        logger.info(f"[Evaluator] Evaluation complete. Confidence: "
                   f"{evaluation.overall_confidence:.3f}, "
                   f"Correction needed: {evaluation.correction_needed}")
        
        return state
    
    def _verifier_agent(self, state: WorkflowState) -> WorkflowState:
        """Verifier agent node - cross-model verification"""
        logger.info("[Verifier] Performing cross-model verification")
        
        # In production: run multiple LLMs and consensus voting
        # For now: validate against retrieved context
        
        context_text = " ".join(state.documents).lower()
        answer_text = state.answer.lower()
        
        # Check coverage
        answer_sentences = answer_text.split(".")
        covered = sum(1 for sent in answer_sentences if len(sent) > 0 and any(
            word in context_text for word in sent.split()[:5]
        ))
        
        verification_score = covered / max(len(answer_sentences), 1)
        state.evaluation_scores["verification_score"] = verification_score
        
        logger.info(f"[Verifier] Verification score: {verification_score:.3f}")
        return state
    
    def _correction_agent(self, state: WorkflowState) -> WorkflowState:
        """Correction agent node - may retry with different strategies"""
        logger.info("[Correction] Attempting to improve response")
        
        if not state.correction_actions or state.iteration >= state.max_iterations:
            logger.info("[Correction] No more corrections needed or max iterations reached")
            state.final_answer = state.answer
            return state
        
        action = state.correction_actions[-1]
        logger.info(f"[Correction] Applying action: {action}")
        
        # Increment iteration counter
        state.iteration += 1
        
        # In production: re-run retrieval, reasoning, or evaluation
        # For now: use teacher model for better accuracy
        result = self.reasoning_pipeline.infer(
            state.query,
            state.documents,
            use_teacher=True
        )
        
        state.answer = result.answer
        state.confidence = result.confidence
        
        logger.info(f"[Correction] Retry completed with confidence: {state.confidence:.3f}")
        return state
    
    def route_after_evaluation(self, state: WorkflowState) -> str:
        """Routing logic after evaluation"""
        if not state.evaluation_scores.get("overall_confidence", 0) > self.evaluator.confidence_threshold:
            if state.iteration < state.max_iterations:
                return "correction"
        return "verification"
    
    def route_after_verification(self, state: WorkflowState) -> str:
        """Routing logic after verification"""
        if state.evaluation_scores.get("verification_score", 0) < 0.6:
            if state.iteration < state.max_iterations:
                return "correction"
        return "end"
    
    def execute_workflow(self, query: str) -> Dict:
        """
        Execute complete multi-agent workflow
        
        Args:
            query: User query
            
        Returns:
            Final result with answer and metadata
        """
        logger.info(f"Starting workflow for query: {query}")
        
        # Initialize state
        state = WorkflowState(query=query)
        
        # Execute agent nodes in sequence
        logger.info("Step 1: Retrival Agent")
        state = self._retriever_agent(state)
        
        logger.info("Step 2: Reader Agent")
        state = self._reader_agent(state)
        
        logger.info("Step 3: Reasoning Agent")
        state = self._reasoning_agent(state)
        
        logger.info("Step 4: Evaluator Agent")
        state = self._evaluator_agent(state)

        # If evaluator reports low overall confidence, attempt a teacher-model retry
        try:
            overall_conf = state.evaluation_scores.get("overall_confidence", 0)
            threshold = getattr(self.evaluator, "confidence_threshold", 0.75)
            if overall_conf < threshold:
                logger.info(f"Overall confidence {overall_conf:.3f} < threshold {threshold:.3f}. Running teacher-model fallback...")
                # Use teacher model to attempt a higher-quality answer
                teacher_result = self.reasoning_pipeline.infer(
                    state.query,
                    state.documents,
                    use_teacher=True
                )
                state.answer = teacher_result.answer
                state.confidence = teacher_result.confidence

                # Re-run evaluation after teacher attempt
                state = self._evaluator_agent(state)
                logger.info(f"Post-teacher evaluation overall confidence: {state.evaluation_scores.get('overall_confidence', 0):.3f}")
        except Exception as e:
            logger.warning(f"Teacher-model fallback failed: {e}")
        
        # Correction loop
        while state.correction_actions and state.iteration < state.max_iterations:
            logger.info(f"Step {4 + state.iteration}: Correction Iteration {state.iteration}")
            state = self._correction_agent(state)
            
            # Re-evaluate after correction
            logger.info(f"Step {5 + state.iteration}: Re-evaluation")
            state = self._evaluator_agent(state)
        
        logger.info("Step Final: Verification Agent")
        state = self._verifier_agent(state)
        
        state.final_answer = state.answer
        
        # Store workflow execution
        self.workflow_history.append({
            "query": query,
            "iterations": state.iteration,
            "confidence": state.confidence,
            "scores": state.evaluation_scores
        })
        
        logger.info(f"Workflow completed with final confidence: {state.confidence:.3f}")
        
        return {
            "query": query,
            "answer": state.final_answer,
            "confidence": state.confidence,
            "evaluation_scores": state.evaluation_scores,
            "iterations": state.iteration,
            "supporting_docs": state.retrieved_docs[:3]
        }
    
    def get_workflow_statistics(self) -> Dict:
        """Get workflow execution statistics"""
        if not self.workflow_history:
            return {}
        
        iterations = [w["iterations"] for w in self.workflow_history]
        confidences = [w["confidence"] for w in self.workflow_history]
        
        return {
            "total_queries": len(self.workflow_history),
            "avg_iterations": sum(iterations) / len(iterations),
            "max_iterations": max(iterations),
            "avg_confidence": sum(confidences) / len(confidences),
            "evaluator_stats": self.evaluator.get_statistics()
        }
