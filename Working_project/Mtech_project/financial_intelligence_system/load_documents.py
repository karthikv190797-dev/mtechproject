#!/usr/bin/env python3
"""
Quick script to load documents from the local data/ directory and verify they're indexed correctly.
Usage: python load_documents.py
"""

import os
import sys

# Add the project root to path so we can import src modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.ingestion import LocalFileSource, SnowflakeSource, DocumentManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Load and index documents from the data/ directory"""
    
    print("\n" + "="*70)
    print("📚 Financial Intelligence System - Document Loader")
    print("="*70 + "\n")
    
    # Initialize local file source
    data_dir = os.path.join(project_root, "data")
    print(f"📂 Scanning documents in: {data_dir}\n")
    
    local_source = LocalFileSource(base_dir=data_dir)
    local_docs = local_source.fetch_documents()
    
    print(f"✅ Loaded {len(local_docs)} documents from local filesystem\n")
    
    if local_docs:
        print("📋 Document Summary:")
        print("-" * 70)
        for i, doc in enumerate(local_docs, 1):
            print(f"\n{i}. {doc.title}")
            print(f"   ID: {doc.id}")
            print(f"   Source: {doc.source}")
            print(f"   Company: {doc.company or 'N/A'}")
            print(f"   Year: {doc.financial_year or 'N/A'}")
            print(f"   Content Length: {len(doc.content)} characters")
            if doc.metadata:
                print(f"   Metadata: {doc.metadata}")
    
    # Try loading from Snowflake (if credentials available)
    print("\n" + "-"*70)
    print("\n🔄 Attempting to load from Snowflake...\n")
    
    try:
        sf_source = SnowflakeSource()
        sf_docs = sf_source.fetch_documents()
        if sf_docs:
            print(f"✅ Loaded {len(sf_docs)} documents from Snowflake")
            total_docs = len(local_docs) + len(sf_docs)
        else:
            print("ℹ️  No documents found in Snowflake (credentials may not be configured)")
            total_docs = len(local_docs)
    except Exception as e:
        print(f"⚠️  Could not connect to Snowflake: {e}")
        print("   This is okay if Snowflake credentials are not configured.")
        print("   The system will use local documents instead.\n")
        total_docs = len(local_docs)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total documents ready for indexing: {total_docs}")
    print(f"Data source: Local filesystem (data/)")
    if total_docs > 0:
        print("✅ Knowledge base is ready! You can now run queries.")
    else:
        print("⚠️  No documents found. Add .txt or .json files to data/ directory.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
