# Evaluator Agent for Self-Correction
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class CorrectionAction(Enum):
    """Possible correction actions"""
    NO_ACTION = "no_action"
    REFORMAT_QUERY = "reformat_query"
    RE_RETRIEVE = "re_retrieve"
    RERANK_RESULTS = "rerank_results"
    REGENERATE_ANSWER = "regenerate_answer"
    ESCALATE = "escalate"


@dataclass
class EvaluationScore:
    """Evaluation metrics for a response"""
    relevance_score: float  # 0-1: Is answer relevant to query?
    factual_consistency: float  # 0-1: Can results be verified?
    numerical_coherence: float  # 0-1: Are financial figures sound?
    entailment_score: float  # 0-1: Does evidence support answer?
    overall_confidence: float  # 0-1: Overall confidence
    correction_needed: bool
    recommended_action: CorrectionAction


class EvaluatorAgent:
    """Evaluator agent for continuous assessment and self-correction"""
    
    def __init__(
        self,
        relevance_threshold: float = 0.7,
        confidence_threshold: float = 0.75,
        correction_attempts: int = 3
    ):
        """
        Initialize evaluator agent
        
        Args:
            relevance_threshold: Minimum relevance score
            confidence_threshold: Minimum overall confidence
            correction_attempts: Maximum correction iterations
        """
        self.relevance_threshold = relevance_threshold
        self.confidence_threshold = confidence_threshold
        self.correction_attempts = correction_attempts
        self.evaluation_history = []
        
        logger.info(f"Initialized evaluator agent with thresholds: "
                   f"relevance={relevance_threshold}, confidence={confidence_threshold}")
    
    def evaluate_relevance(
        self,
        query: str,
        answer: str,
        context: List[str]
    ) -> float:
        """
        Evaluate relevance of answer to query
        
        Args:
            query: Original query
            answer: Generated answer
            context: Supporting context
            
        Returns:
            Relevance score (0-1)
        """
        # Cosine-similarity relevance using TF-IDF vectors
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as cos_sim
        try:
            vec = TfidfVectorizer(stop_words="english", min_df=1)
            context_joined = " ".join(context)
            tfidf = vec.fit_transform([query, answer, context_joined])
            # query ↔ answer similarity and query ↔ context similarity
            qa_sim   = float(cos_sim(tfidf[0:1], tfidf[1:2])[0][0])
            qc_sim   = float(cos_sim(tfidf[0:1], tfidf[2:3])[0][0])
            relevance = float(np.clip(0.4 * qa_sim + 0.6 * qc_sim, 0.0, 1.0))
        except Exception:
            # fallback
            query_words = set(query.lower().split())
            answer_words = set(answer.lower().split())
            intersection = len(query_words & answer_words)
            union = len(query_words | answer_words)
            relevance = max(0.5, min(1.0, intersection / union)) if union else 0.5

        logger.debug(f"Relevance score: {relevance:.3f}")
        return relevance
    
    def evaluate_factual_consistency(
        self,
        answer: str,
        context: List[str]
    ) -> float:
        """
        Evaluate factual consistency with context
        
        Args:
            answer: Generated answer
            context: Supporting documents
            
        Returns:
            Factual consistency score (0-1)
        """
        # Check if answer contains information from context
        context_text = " ".join(context).lower()
        answer_text = answer.lower()
        
        # Simple check: see if key phrases appear in context
        sentences = answer_text.split(".")
        matches = 0
        
        for sentence in sentences:
            if any(phrase in context_text for phrase in sentence.split()):
                matches += 1
        
        consistency = matches / max(len(sentences), 1) if sentences else 0.5
        consistency = min(0.95, max(0.5, consistency))
        
        logger.debug(f"Factual consistency score: {consistency:.3f}")
        return consistency
    
    def evaluate_numerical_coherence(
        self,
        answer: str
    ) -> float:
        """
        Evaluate numerical coherence (are financial figures sound?)
        
        Args:
            answer: Generated answer containing numbers
            
        Returns:
            Numerical coherence score (0-1)
        """
        # Extract numbers from answer
        import re
        numbers = re.findall(r'\d+\.?\d*', answer)
        
        if not numbers:
            # No numbers = neutral score
            return 0.8
        
        # Check if numbers seem reasonable (simplified)
        try:
            num_values = [float(n) for n in numbers]
            mean_val = np.mean(num_values)
            std_val = np.std(num_values)
            
            # Check for outliers
            outliers = sum(1 for v in num_values if abs(v - mean_val) > 3 * std_val)
            coherence = 1.0 - (outliers / len(num_values) * 0.5)
            coherence = min(0.95, max(0.7, coherence))
            
        except:
            coherence = 0.8
        
        logger.debug(f"Numerical coherence score: {coherence:.3f}")
        return coherence
    
    def evaluate_entailment(
        self,
        query: str,
        answer: str,
        context: List[str]
    ) -> float:
        """
        Evaluate logical entailment (does evidence support answer?)
        
        Args:
            query: Original query
            answer: Generated answer
            context: Supporting evidence
            
        Returns:
            Entailment score (0-1)
        """
        # Entailment: does the retrieved evidence semantically support the answer?
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as cos_sim
        try:
            vec = TfidfVectorizer(stop_words="english", min_df=1)
            context_joined = " ".join(context)
            tfidf = vec.fit_transform([answer, context_joined])
            ans_ctx_sim = float(cos_sim(tfidf[0:1], tfidf[1:2])[0][0])

            # Bonus: rich context (long docs) and substantive answer
            context_richness = min(len(context_joined) / 2000.0, 1.0)
            answer_depth     = min(len(answer) / 400.0, 1.0)
            entailment = float(np.clip(
                0.55 * ans_ctx_sim + 0.25 * context_richness + 0.20 * answer_depth,
                0.0, 1.0
            ))
        except Exception:
            context_coverage = sum(1 for doc in context if len(doc) > 100) / max(len(context), 1)
            answer_coverage  = min(len(answer) / 500, 1.0)
            entailment = min(0.95, max(0.5, context_coverage * 0.6 + answer_coverage * 0.4))

        logger.debug(f"Entailment score: {entailment:.3f}")
        return entailment
    
    def evaluate_response(
        self,
        query: str,
        answer: str,
        context: List[str]
    ) -> EvaluationScore:
        """
        Comprehensive evaluation of response
        
        Args:
            query: Original query
            answer: Generated answer
            context: Supporting context
            
        Returns:
            EvaluationScore with all metrics
        """
        # Calculate individual scores
        relevance = self.evaluate_relevance(query, answer, context)
        factual = self.evaluate_factual_consistency(answer, context)
        numerical = self.evaluate_numerical_coherence(answer)
        entailment = self.evaluate_entailment(query, answer, context)
        
        # Calculate overall confidence
        overall_confidence = (
            relevance * 0.3 +
            factual * 0.3 +
            numerical * 0.2 +
            entailment * 0.2
        )
        
        # Determine correction action
        correction_needed = overall_confidence < self.confidence_threshold
        
        if not correction_needed:
            action = CorrectionAction.NO_ACTION
        elif relevance < self.relevance_threshold:
            action = CorrectionAction.REFORMAT_QUERY
        elif factual < 0.6:
            action = CorrectionAction.RE_RETRIEVE
        elif numerical < 0.6:
            action = CorrectionAction.REGENERATE_ANSWER
        else:
            action = CorrectionAction.RERANK_RESULTS
        
        score = EvaluationScore(
            relevance_score=relevance,
            factual_consistency=factual,
            numerical_coherence=numerical,
            entailment_score=entailment,
            overall_confidence=overall_confidence,
            correction_needed=correction_needed,
            recommended_action=action
        )
        
        self.evaluation_history.append(score)
        
        logger.info(f"Evaluation completed. Overall confidence: {overall_confidence:.3f}, "
                   f"Action: {action.value}")
        
        return score
    
    def get_correction_prompt(
        self,
        original_query: str,
        evaluation: EvaluationScore
    ) -> str:
        """
        Generate correction prompt based on evaluation
        
        Args:
            original_query: Original query
            evaluation: Evaluation scores
            
        Returns:
            Correction prompt for pipeline
        """
        if evaluation.recommended_action == CorrectionAction.NO_ACTION:
            return ""
        
        prompts = {
            CorrectionAction.REFORMAT_QUERY: 
                f"Query relevance too low. Reformulate: '{original_query}' "
                f"to be more specific about financial metrics.",
            
            CorrectionAction.RE_RETRIEVE:
                f"Low factual consistency detected. Re-retrieve documents "
                f"for: '{original_query}' with expanded keywords.",
            
            CorrectionAction.RERANK_RESULTS:
                f"Re-rank retrieved results for better relevance to: '{original_query}'.",
            
            CorrectionAction.REGENERATE_ANSWER:
                f"Numerical incoherence detected. Regenerate answer for: '{original_query}' "
                f"with more careful number validation.",
            
            CorrectionAction.ESCALATE:
                f"High uncertainty on: '{original_query}'. Escalate to human review."
        }
        
        return prompts.get(evaluation.recommended_action, "")
    
    def get_statistics(self) -> Dict:
        """Get evaluation statistics"""
        if not self.evaluation_history:
            return {}
        
        scores = self.evaluation_history
        return {
            "total_evaluations": len(scores),
            "avg_relevance": np.mean([s.relevance_score for s in scores]),
            "avg_factual_consistency": np.mean([s.factual_consistency for s in scores]),
            "avg_numerical_coherence": np.mean([s.numerical_coherence for s in scores]),
            "avg_entailment": np.mean([s.entailment_score for s in scores]),
            "avg_overall_confidence": np.mean([s.overall_confidence for s in scores]),
            "correction_rate": sum(1 for s in scores if s.correction_needed) / len(scores)
        }
