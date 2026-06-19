"""
Model Loader Utility
─────────────────────────────────────────────────────────────
Handles loading, caching, and management of models from the models/ directory.
Supports embeddings, retriever indices, and reasoning models.
"""

import json
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelConfig:
    """Model configuration helper"""
    
    @staticmethod
    def load_registry(registry_path: str = "models/model_registry.json") -> Dict[str, Any]:
        """Load the model registry JSON"""
        if not os.path.exists(registry_path):
            logger.warning(f"Registry not found at {registry_path}")
            return {}
        
        try:
            with open(registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            return {}
    
    @staticmethod
    def get_model_info(registry: Dict, model_id: str, category: str = "embeddings") -> Optional[Dict]:
        """Get metadata for a specific model"""
        try:
            return registry.get(category, {}).get(model_id)
        except Exception:
            return None


class ModelLoader:
    """
    Central model loader for all model types.
    
    Usage:
        loader = ModelLoader()
        embedder = loader.get_embedding_model("all-MiniLM-L6-v2")
        faiss_index = loader.get_faiss_index("all-MiniLM-L6-v2")
        teacher = loader.get_reasoning_model("teacher_model")
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = os.path.abspath(models_dir)
        self.registry = ModelConfig.load_registry(
            os.path.join(self.models_dir, "model_registry.json")
        )
        logger.info(f"ModelLoader initialized with models_dir: {self.models_dir}")
    
    def get_embedding_model(self, model_id: str = "all-MiniLM-L6-v2"):
        """
        Load a sentence embeddings model
        
        Args:
            model_id: Model identifier (e.g., "all-MiniLM-L6-v2")
        
        Returns:
            SentenceTransformer model or None
        """
        logger.info(f"Loading embedding model: {model_id}")
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Try local cache first
            model_info = ModelConfig.get_model_info(self.registry, model_id, "embeddings")
            if model_info:
                local_path = model_info.get("local_path")
                if local_path and os.path.exists(local_path):
                    logger.info(f"Loading from local path: {local_path}")
                    return SentenceTransformer(local_path)
            
            # Fall back to downloading from HuggingFace
            logger.info(f"Downloading {model_id} from HuggingFace...")
            return SentenceTransformer(model_id)
        
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            return None
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            return None
    
    def get_faiss_index(self, model_id: str = "all-MiniLM-L6-v2"):
        """
        Load a FAISS index for document retrieval
        
        Args:
            model_id: Embedding model ID the index was created for
        
        Returns:
            FAISS index object or None
        """
        logger.info(f"Loading FAISS index for model: {model_id}")
        
        try:
            import faiss
            
            index_path = os.path.join(
                self.models_dir, 
                "embeddings", 
                model_id.replace("/", "_"),
                "index.faiss"
            )
            
            if not os.path.exists(index_path):
                logger.warning(f"FAISS index not found at {index_path}")
                logger.info("To create an index, run: python models/create_faiss_index.py")
                return None
            
            logger.info(f"Loading FAISS index from: {index_path}")
            return faiss.read_index(index_path)
        
        except ImportError:
            logger.error("faiss-cpu not installed. Install with: pip install faiss-cpu")
            return None
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return None
    
    def get_faiss_metadata(self, model_id: str = "all-MiniLM-L6-v2") -> Optional[Dict]:
        """
        Load FAISS index metadata (document IDs, sources, etc.)
        
        Args:
            model_id: Embedding model ID
        
        Returns:
            Metadata dictionary or None
        """
        logger.info(f"Loading FAISS metadata for model: {model_id}")
        
        try:
            metadata_path = os.path.join(
                self.models_dir,
                "embeddings",
                model_id.replace("/", "_"),
                "metadata.json"
            )
            
            if not os.path.exists(metadata_path):
                logger.warning(f"Metadata not found at {metadata_path}")
                return None
            
            with open(metadata_path, 'r') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Error loading FAISS metadata: {e}")
            return None
    
    def get_reasoning_model(self, model_type: str = "teacher_model"):
        """
        Load a reasoning model (teacher or student)
        
        Args:
            model_type: "teacher_model" or "student_model"
        
        Returns:
            Model object or placeholder dict
        """
        logger.info(f"Loading reasoning model: {model_type}")
        
        try:
            model_info = ModelConfig.get_model_info(self.registry, model_type, "reasoning")
            if not model_info:
                logger.warning(f"Model {model_type} not found in registry")
                return None
            
            weights_path = model_info.get("weights_file")
            if weights_path and os.path.exists(weights_path):
                logger.info(f"Loading weights from: {weights_path}")
                import torch
                return torch.load(weights_path)
            else:
                logger.info(f"Model {model_type} is a placeholder. Configure with your preferred backend.")
                return model_info
        
        except Exception as e:
            logger.error(f"Error loading reasoning model: {e}")
            return None
    
    def get_retriever_config(self, retriever_type: str = "hybrid") -> Optional[Dict]:
        """
        Get configuration for a retriever
        
        Args:
            retriever_type: "bm25", "faiss", or "hybrid"
        
        Returns:
            Configuration dictionary or None
        """
        logger.info(f"Loading retriever config: {retriever_type}")
        
        try:
            config_info = ModelConfig.get_model_info(self.registry, retriever_type, "retrievers")
            if not config_info:
                logger.warning(f"Retriever {retriever_type} not found in registry")
                return None
            
            return config_info
        
        except Exception as e:
            logger.error(f"Error loading retriever config: {e}")
            return None
    
    def list_available_models(self) -> Dict[str, list]:
        """
        List all available models by category
        
        Returns:
            Dictionary of model categories and their model IDs
        """
        available = {
            "embeddings": list(self.registry.get("embeddings", {}).keys()),
            "reasoning": list(self.registry.get("reasoning", {}).keys()),
            "retrievers": list(self.registry.get("retrievers", {}).keys()),
        }
        logger.info(f"Available models: {available}")
        return available
    
    def get_default_models(self) -> Dict[str, str]:
        """Get default models to use"""
        defaults = self.registry.get("defaults", {})
        logger.info(f"Default models: {defaults}")
        return defaults
    
    def is_faiss_index_ready(self, model_id: str = "all-MiniLM-L6-v2") -> bool:
        """Check if FAISS index has been created"""
        index_path = os.path.join(
            self.models_dir,
            "embeddings",
            model_id.replace("/", "_"),
            "index.faiss"
        )
        ready = os.path.exists(index_path)
        logger.info(f"FAISS index ready for {model_id}: {ready}")
        return ready
    
    def print_summary(self):
        """Print a summary of available models"""
        print("\n" + "="*70)
        print("📚 MODEL REGISTRY SUMMARY")
        print("="*70 + "\n")
        
        models = self.list_available_models()
        for category, model_list in models.items():
            print(f"📦 {category.upper()}: {len(model_list)} models")
            for model_id in model_list:
                status = "✅" if category != "reasoning" else "⚙️"
                print(f"   {status} {model_id}")
        
        print("\n" + "-"*70)
        defaults = self.get_default_models()
        print("🎯 DEFAULT MODELS:")
        for key, value in defaults.items():
            print(f"   • {key}: {value}")
        
        print("\n" + "-"*70)
        print("📊 INDEX STATUS:")
        print(f"   • FAISS Index Ready: {self.is_faiss_index_ready()}")
        
        print("\n" + "="*70 + "\n")


# ─────────────────────────────────────────────────────────────
# COMMAND-LINE INTERFACE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """Show available models and system status"""
    loader = ModelLoader()
    loader.print_summary()
    
    print("\n💡 NEXT STEPS:\n")
    print("1. Load embedding model:")
    print("   embedder = loader.get_embedding_model('all-MiniLM-L6-v2')\n")
    
    print("2. Create FAISS index from documents:")
    print("   python models/create_faiss_index.py\n")
    
    print("3. Load FAISS index:")
    print("   index = loader.get_faiss_index('all-MiniLM-L6-v2')\n")
    
    print("4. Load reasoning models:")
    print("   teacher = loader.get_reasoning_model('teacher_model')\n")
