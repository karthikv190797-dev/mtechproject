"""
Data Loading and Indexing Example
Demonstrates how to load financial documents and prepare them for retrieval
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict


class FinancialDocumentLoader:
    """
    Load and index financial documents for the system.
    """
    
    def __init__(self):
        self.documents = []
        self.metadata = {}
    
    def load_text_file(self, file_path: str, doc_type: str = "filing") -> Dict:
        """
        Load a text-based financial document.
        
        Args:
            file_path: Path to the document file
            doc_type: Type of document (filing, report, transcript, etc.)
        
        Returns:
            Document dictionary with metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_name = Path(file_path).name
        
        doc = {
            "id": f"doc_{len(self.documents):04d}",
            "filename": file_name,
            "type": doc_type,
            "content": content,
            "length_chars": len(content),
            "file_path": file_path
        }
        
        self.documents.append(doc)
        print(f"✓ Loaded: {file_name} ({len(content)} chars)")
        
        return doc
    
    def load_directory(self, directory: str, doc_type: str = "filing") -> List[Dict]:
        """
        Load all text files from a directory.
        """
        path = Path(directory)
        
        if not path.exists():
            print(f"✗ Directory not found: {directory}")
            return []
        
        files = list(path.glob("*.txt")) + list(path.glob("*.md"))
        print(f"Found {len(files)} files in {directory}")
        
        loaded_docs = []
        for file_path in files:
            doc = self.load_text_file(str(file_path), doc_type)
            loaded_docs.append(doc)
        
        return loaded_docs
    
    def create_chunks(self, doc_id: str, chunk_size: int = 500) -> List[Dict]:
        """
        Split a document into chunks for better retrieval.
        
        Args:
            doc_id: Document ID
            chunk_size: Number of characters per chunk
        
        Returns:
            List of document chunks
        """
        doc = next((d for d in self.documents if d["id"] == doc_id), None)
        
        if not doc:
            print(f"✗ Document not found: {doc_id}")
            return []
        
        content = doc["content"]
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split("\n\n")
        current_chunk = ""
        chunk_id = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_id": f"{doc_id}_chunk_{chunk_id:03d}",
                        "content": current_chunk.strip(),
                        "length": len(current_chunk),
                        "parent_doc_id": doc_id
                    })
                    chunk_id += 1
                current_chunk = para + "\n\n"
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "chunk_id": f"{doc_id}_chunk_{chunk_id:03d}",
                "content": current_chunk.strip(),
                "length": len(current_chunk),
                "parent_doc_id": doc_id
            })
        
        return chunks
    
    def extract_metadata(self) -> Dict:
        """
        Extract metadata about loaded documents.
        """
        metadata = {
            "total_documents": len(self.documents),
            "total_characters": sum(d.get("length_chars", 0) for d in self.documents),
            "documents_by_type": {},
            "document_list": []
        }
        
        for doc in self.documents:
            doc_type = doc.get("type", "unknown")
            if doc_type not in metadata["documents_by_type"]:
                metadata["documents_by_type"][doc_type] = 0
            metadata["documents_by_type"][doc_type] += 1
            
            metadata["document_list"].append({
                "id": doc["id"],
                "filename": doc["filename"],
                "type": doc_type,
                "size_chars": doc.get("length_chars", 0)
            })
        
        self.metadata = metadata
        return metadata
    
    def save_indexed_documents(self, output_file: str):
        """
        Save indexed documents to a JSON file.
        """
        output_data = {
            "metadata": self.extract_metadata(),
            "documents": self.documents
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✓ Indexed documents saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """
        Print a summary of loaded documents.
        """
        metadata = self.extract_metadata()
        
        print("\n" + "=" * 70)
        print("DOCUMENT LOADING SUMMARY")
        print("=" * 70)
        print(f"Total Documents: {metadata['total_documents']}")
        print(f"Total Characters: {metadata['total_characters']:,}")
        print("\nDocuments by Type:")
        for doc_type, count in metadata['documents_by_type'].items():
            print(f"  {doc_type}: {count}")
        print("\nLoaded Documents:")
        for doc in metadata['document_list']:
            print(f"  - {doc['filename']} ({doc['size_chars']:,} chars)")
        print("=" * 70)


def example_document_loading():
    """
    Complete example of loading and indexing documents.
    """
    
    loader = FinancialDocumentLoader()
    
    # Define sample data directory
    sample_data_dir = Path(__file__).parent.parent / "sample_data"
    
    print("=" * 70)
    print("FINANCIAL DOCUMENT LOADING EXAMPLE")
    print("=" * 70)
    print(f"Loading documents from: {sample_data_dir}\n")
    
    # Load individual documents
    if sample_data_dir.exists():
        loader.load_directory(str(sample_data_dir), doc_type="filing")
    else:
        print(f"Note: Sample data directory not found at {sample_data_dir}")
        print("Creating example documents...\n")
        
        # Create temporary example documents
        example_content = {
            "Tesla Report.txt": "Revenue 2023: $81.46B\nGross Margin: 15.5%",
            "Apple Report.txt": "Revenue Q1 2024: $119.6B\nGross Margin: 46.2%",
            "Microsoft Report.txt": "Q2 2024 Revenue: $72.8B\nOperating Margin: 38.8%"
        }
        
        for filename, content in example_content.items():
            doc = {
                "id": f"doc_{len(loader.documents):04d}",
                "filename": filename,
                "type": "report",
                "content": content,
                "length_chars": len(content),
                "file_path": filename
            }
            loader.documents.append(doc)
            print(f"✓ Created example: {filename}")
    
    # Print summary
    loader.print_summary()
    
    # Save indexed documents
    output_dir = Path(__file__).parent.parent / "indexed_documents"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "documents_index.json"
    loader.save_indexed_documents(str(output_file))
    
    return loader


if __name__ == "__main__":
    loader = example_document_loading()
