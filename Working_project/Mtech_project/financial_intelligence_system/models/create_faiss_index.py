"""
FAISS Index Creation Script
──────────────────────────────────────────────────────────
Creates and saves FAISS indices for document retrieval.

Usage:
    python create_faiss_index.py
    python create_faiss_index.py --documents data/documents.json --output models/embeddings/all-MiniLM-L6-v2/index.faiss
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_faiss_index(
    documents: List[str],
    embedding_model_name: str = "all-MiniLM-L6-v2",
    output_dir: str = "models/embeddings/all-MiniLM-L6-v2"
) -> Optional[str]:
    """
    Create and save FAISS index from documents
    
    Args:
        documents: List of document texts
        embedding_model_name: Name of embedding model
        output_dir: Directory to save FAISS index
    
    Returns:
        Path to saved index or None on error
    """
    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        logger.error(f"Missing required packages: {e}")
        logger.info("Install with: pip install faiss-cpu sentence-transformers")
        return None
    
    logger.info(f"Creating FAISS index from {len(documents)} documents...")
    logger.info(f"Embedding model: {embedding_model_name}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load embedding model
    logger.info("Loading embedding model...")
    try:
        embedder = SentenceTransformer(embedding_model_name)
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return None
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    try:
        embeddings = embedder.encode(documents, show_progress_bar=True).astype("float32")
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return None
    
    # Create FAISS index
    logger.info("Creating FAISS index...")
    try:
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        logger.info(f"FAISS index created with {index.ntotal} vectors")
    except Exception as e:
        logger.error(f"Failed to create FAISS index: {e}")
        return None
    
    # Save index
    index_path = os.path.join(output_dir, "index.faiss")
    try:
        faiss.write_index(index, index_path)
        logger.info(f"✅ FAISS index saved to: {index_path}")
    except Exception as e:
        logger.error(f"Failed to save FAISS index: {e}")
        return None
    
    # Save metadata
    metadata = {
        "total_documents": len(documents),
        "embedding_model": embedding_model_name,
        "vector_dimension": int(dimension),
        "index_type": "IndexFlatL2",
        "documents": documents,
        "created_at": str(Path(index_path).stat().st_mtime)
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✅ Metadata saved to: {metadata_path}")
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")
    
    return index_path


def load_documents_from_data_dir(data_dir: str = "data") -> List[str]:
    """
    Load documents from data/ directory structure
    
    Args:
        data_dir: Data directory path
    
    Returns:
        List of document texts
    """
    documents = []
    
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory not found: {data_dir}")
        return documents
    
    logger.info(f"Loading documents from: {data_dir}")
    
    # Scan .txt files
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(('.txt', '.md')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(content)
                        logger.debug(f"Loaded: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
    
    # Scan .json batch files
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if 'content' in item:
                                    documents.append(item['content'])
                        elif isinstance(data, dict) and 'content' in data:
                            documents.append(data['content'])
                        logger.debug(f"Loaded {len(documents)} documents from: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")
    
    logger.info(f"✅ Loaded {len(documents)} total documents")
    return documents


def main():
    parser = argparse.ArgumentParser(
        description="Create FAISS index for document retrieval"
    )
    parser.add_argument(
        "--documents",
        type=str,
        default="data",
        help="Path to documents (directory or JSON file)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Embedding model name"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/embeddings/all-MiniLM-L6-v2",
        help="Output directory for FAISS index"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔧 FAISS Index Creation Tool")
    print("="*70 + "\n")
    
    # Load documents
    if os.path.isdir(args.documents):
        documents = load_documents_from_data_dir(args.documents)
    else:
        logger.error(f"Invalid documents path: {args.documents}")
        return
    
    if not documents:
        logger.error("No documents loaded!")
        return
    
    # Create index
    index_path = create_faiss_index(
        documents,
        embedding_model_name=args.model,
        output_dir=args.output
    )
    
    if index_path:
        print("\n" + "="*70)
        print("✅ SUCCESS")
        print("="*70)
        print(f"FAISS index created: {index_path}")
        print(f"Documents indexed: {len(documents)}")
        print(f"Embedding model: {args.model}")
        print("="*70 + "\n")
    else:
        print("\n❌ Failed to create FAISS index\n")


if __name__ == "__main__":
    main()
