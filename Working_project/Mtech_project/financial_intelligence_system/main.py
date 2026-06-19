# Main Entry Point for Financial Intelligence System
# Disable SSL verification for HuggingFace hub (corporate proxy / self-signed cert)
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ.setdefault("CURL_CA_BUNDLE", "")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "")

# Patch httpx (used by huggingface_hub) to skip SSL verification
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

import logging
import yaml
from pathlib import Path
from typing import Dict

import sys
sys.path.insert(0, str(Path(__file__).parent))

# Load .env so Snowflake credentials are available before any imports
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)
except ImportError:
    pass

from src.ingestion import DataIngestionPipeline, SECFilingSource, SnowflakeSource
from src.retrieval.hybrid_retriever import HybridRetriever
from src.reasoning.distillation import DistillationPipeline
from src.evaluation.evaluator import EvaluatorAgent
from src.orchestration.langgraph_orchestrator import MultiAgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemInitializer:
    """Initialize and manage the complete financial intelligence system"""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        """Initialize system with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.components = {}
        logger.info("System initializer created")
    
    def _load_config(self) -> Dict:
        """Load YAML configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def setup_data_ingestion(self) -> DataIngestionPipeline:
        """Initialize data ingestion pipeline"""
        logger.info("Setting up data ingestion pipeline...")
        
        pipeline = DataIngestionPipeline()
        
        # Register SEC filings source
        sec_config = self.config['data_ingestion']['sources'].get('sec_filings', {})
        if sec_config.get('enabled'):
            sec_source = SECFilingSource(
                cache_dir=sec_config.get('cache_dir', './data/sec_filings')
            )
            pipeline.register_source('sec_filings', sec_source)
            logger.info("Registered SEC filings source")
        
        # Register Snowflake source
        snowflake_config = self.config['data_ingestion']['sources'].get('snowflake', {})
        if snowflake_config.get('enabled'):
            sf_conn_config = snowflake_config.get('connection', {})
            sf_source = SnowflakeSource(sf_conn_config)
            pipeline.register_source('snowflake', sf_source)
            logger.info("Registered Snowflake source")
        
        self.components['data_ingestion'] = pipeline
        logger.info("Data ingestion pipeline setup complete")
        return pipeline
    
    def setup_retrieval(self, documents: list, embeddings) -> HybridRetriever:
        """Initialize hybrid retrieval system"""
        logger.info("Setting up hybrid retrieval system...")
        
        retrieval_config = self.config['retrieval']
        hybrid_config = retrieval_config['hybrid_retriever']
        
        retriever = HybridRetriever(
            documents=documents,
            embeddings=embeddings,
            k=hybrid_config.get('top_k', 5),
            alpha=hybrid_config.get('alpha', 0.5),
            beta=hybrid_config.get('beta', 0.5)
        )
        
        self.components['retrieval'] = retriever
        logger.info("Hybrid retrieval system setup complete")
        return retriever
    
    def setup_reasoning(self) -> DistillationPipeline:
        """Initialize teacher-student reasoning pipeline"""
        logger.info("Setting up reasoning pipeline...")
        
        reasoning_config = self.config['reasoning']
        teacher_model = reasoning_config['teacher_model'].get('model_name', 'glm-130b')
        student_model = reasoning_config['student_model'].get('model_name', 'mistral-7b')
        temperature = reasoning_config['distillation'].get('temperature', 4.0)
        
        pipeline = DistillationPipeline(
            teacher_model_name=teacher_model,
            student_model_name=student_model,
            distillation_temperature=temperature
        )
        
        self.components['reasoning'] = pipeline
        logger.info("Reasoning pipeline setup complete")
        return pipeline
    
    def setup_evaluation(self) -> EvaluatorAgent:
        """Initialize evaluator agent"""
        logger.info("Setting up evaluator agent...")
        
        eval_config = self.config['evaluation']['evaluator']
        
        evaluator = EvaluatorAgent(
            relevance_threshold=eval_config.get('relevance_threshold', 0.7),
            confidence_threshold=eval_config.get('confidence_threshold', 0.75),
            correction_attempts=eval_config.get('max_correction_attempts', 3)
        )
        
        self.components['evaluation'] = evaluator
        logger.info("Evaluator agent setup complete")
        return evaluator
    
    def setup_orchestration(
        self,
        retriever,
        reasoning_pipeline,
        evaluator
    ) -> MultiAgentOrchestrator:
        """Initialize multi-agent orchestrator"""
        logger.info("Setting up multi-agent orchestrator...")
        
        orchestrator = MultiAgentOrchestrator(
            retriever=retriever,
            reasoning_pipeline=reasoning_pipeline,
            evaluator=evaluator
        )
        
        self.components['orchestration'] = orchestrator
        logger.info("Multi-agent orchestrator setup complete")
        return orchestrator
    
    def initialize_all(self, sample_docs=None, sample_embeddings=None):
        """Initialize all system components"""
        logger.info("=" * 80)
        logger.info("INITIALIZING SELF-CORRECTING FINANCIAL INTELLIGENCE SYSTEM")
        logger.info("=" * 80)

        # Initialize data ingestion
        ingestion = self.setup_data_ingestion()

        # ── Load documents from Snowflake ────────────────────────────────
        if sample_docs is None:
            logger.info("Fetching documents from Snowflake…")
            sf_source = SnowflakeSource()           # credentials from .env
            sf_docs = sf_source.fetch_documents()   # auto-discovers all tables

            if sf_docs:
                sample_docs = [d.content for d in sf_docs]
                logger.info(f"Loaded {len(sample_docs)} documents from Snowflake")
            else:
                logger.warning("Snowflake returned no documents — using fallback sample data")
                sample_docs = [
                    "Apple Inc. 10-K filing 2023. Revenue increased 2% YoY to $383B.",
                    "Microsoft Corporation financial report. Azure cloud revenue grew 28% YoY.",
                    "Tesla annual report showing record production of 1.8M vehicles in 2023.",
                    "Google Alphabet financial documentation: advertising revenue $237B.",
                    "Amazon shareholder letter discussing AWS revenue $91B, up 13% YoY.",
                ]

        if sample_embeddings is None:
            import os as _os
            _os.environ.setdefault("HF_HUB_DISABLE_SSL_VERIFICATION", "1")
            _os.environ.setdefault("CURL_CA_BUNDLE", "")
            _os.environ.setdefault("REQUESTS_CA_BUNDLE", "")
            from sentence_transformers import SentenceTransformer
            logger.info("Encoding documents with SentenceTransformer (all-MiniLM-L6-v2)...")
            _embed_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            import numpy as np
            sample_embeddings = _embed_model.encode(sample_docs, show_progress_bar=False).astype("float32")
            logger.info(f"Encoded {len(sample_docs)} documents, shape {sample_embeddings.shape}")
        else:
            _embed_model = None

        # Initialize retrieval
        retriever = self.setup_retrieval(sample_docs, sample_embeddings)
        
        # Initialize reasoning
        reasoning_pipeline = self.setup_reasoning()
        
        # Initialize evaluation
        evaluator = self.setup_evaluation()
        
        # Initialize orchestration (pass embed model for real query encoding)
        orchestrator = self.setup_orchestration(
            retriever,
            reasoning_pipeline,
            evaluator
        )
        if _embed_model is not None:
            orchestrator.embedding_model = _embed_model
        
        logger.info("=" * 80)
        logger.info("SYSTEM INITIALIZATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Active Components: {list(self.components.keys())}")
        
        return orchestrator
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "components_initialized": list(self.components.keys()),
            "config_file": self.config_path,
            "system_name": self.config['system']['name'],
            "version": self.config['system']['version']
        }


def main():
    """Run system initialization and demo"""
    try:
        # Initialize system
        initializer = SystemInitializer()
        orchestrator = initializer.initialize_all()
        
        # Print system status
        status = initializer.get_system_status()
        logger.info(f"System Status: {status}")
        
        # Test query
        logger.info("\n" + "=" * 80)
        logger.info("RUNNING DEMO QUERY")
        logger.info("=" * 80)
        
        test_query = "What is the revenue growth for Apple in 2023?"
        logger.info(f"Query: {test_query}")
        
        result = orchestrator.execute_workflow(test_query)
        
        logger.info(f"Answer: {result['answer']}")
        logger.info(f"Confidence: {result['confidence']:.3f}")
        logger.info(f"Iterations: {result['iterations']}")
        logger.info(f"Scores: {result['evaluation_scores']}")
        
        logger.info("=" * 80)
        logger.info("DEMO COMPLETE")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
