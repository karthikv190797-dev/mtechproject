"""
Batch Processing Example
Demonstrates how to load, process, and manage batch queries
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path


class BatchProcessor:
    """
    Utility class for batch processing financial queries.
    """
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.batch_id = None
        self.results = []
        
    def load_queries(self, file_path):
        """
        Load queries from a JSON file.
        
        Expected format:
        [
            {"query_id": "q001", "query": "...", "priority": "high"},
            ...
        ]
        """
        with open(file_path, 'r') as f:
            queries = json.load(f)
        return queries
    
    def submit_batch(self, queries, batch_name="batch"):
        """
        Submit a batch of queries for processing.
        """
        payload = {
            "queries": [q.get("query") for q in queries],
            "batch_id": batch_name,
            "priority_queries": [
                q.get("query_id") for q in queries 
                if q.get("priority") == "high"
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/batch",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                self.batch_id = batch_name
                print(f"✓ Batch submitted: {batch_name}")
                return response.json()
            else:
                print(f"✗ Batch submission failed: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"✗ Error submitting batch: {e}")
            return None
    
    def process_queries(self, queries):
        """
        Process queries sequentially with error handling.
        """
        results = []
        for idx, query_obj in enumerate(queries, 1):
            query = query_obj.get("query")
            query_id = query_obj.get("query_id")
            
            print(f"\n[{idx}/{len(queries)}] Processing: {query_id}")
            
            try:
                payload = {
                    "query": query,
                    "parameters": {
                        "max_corrections": 3,
                        "evaluation_threshold": 0.7,
                        "return_supporting_docs": True
                    }
                }
                
                response = requests.post(
                    f"{self.api_base}/query",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result["query_id"] = query_id
                    result["timestamp"] = datetime.now().isoformat()
                    results.append(result)
                    confidence = result.get("confidence_score", 0)
                    print(f"  ✓ Processed (confidence: {confidence:.1%})")
                else:
                    print(f"  ✗ Failed with status {response.status_code}")
                    
            except requests.RequestException as e:
                print(f"  ✗ Request error: {e}")
            
            # Adding small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        self.results = results
        return results
    
    def save_results(self, output_file):
        """
        Save processing results to a JSON file.
        """
        output_data = {
            "batch_id": self.batch_id,
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(self.results),
            "results": self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n✓ Results saved to {output_file}")
        return output_file
    
    def generate_report(self):
        """
        Generate a summary report of batch processing results.
        """
        if not self.results:
            print("No results to report")
            return
        
        total = len(self.results)
        avg_confidence = sum(r.get("confidence_score", 0) for r in self.results) / total
        high_confidence = sum(1 for r in self.results if r.get("confidence_score", 0) >= 0.8)
        avg_corrections = sum(
            r.get("corrections_applied", 0) for r in self.results
        ) / total
        
        print("\n" + "=" * 70)
        print("BATCH PROCESSING REPORT")
        print("=" * 70)
        print(f"Batch ID: {self.batch_id}")
        print(f"Total Queries Processed: {total}")
        print(f"Average Confidence Score: {avg_confidence:.1%}")
        print(f"High Confidence Results (≥80%): {high_confidence}/{total}")
        print(f"Average Corrections Applied: {avg_corrections:.1f}")
        print("=" * 70)
        
        return {
            "total_queries": total,
            "avg_confidence": avg_confidence,
            "high_confidence_count": high_confidence,
            "avg_corrections": avg_corrections
        }


def example_batch_workflow():
    """
    Complete example workflow for batch processing.
    """
    
    processor = BatchProcessor()
    
    # Example queries
    queries = [
        {
            "query_id": "q001",
            "query": "What was Tesla's revenue growth rate in 2023?",
            "priority": "high"
        },
        {
            "query_id": "q002", 
            "query": "Why did Tesla's gross margin decline significantly?",
            "priority": "high"
        },
        {
            "query_id": "q003",
            "query": "What geographic regions showed highest growth for Apple?",
            "priority": "medium"
        },
        {
            "query_id": "q004",
            "query": "How is Microsoft investing in artificial intelligence?",
            "priority": "high"
        },
        {
            "query_id": "q005",
            "query": "Compare operating margins across the three companies",
            "priority": "medium"
        }
    ]
    
    print("=" * 70)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 70)
    print(f"Processing {len(queries)} queries...\n")
    
    # Process all queries
    results = processor.process_queries(queries)
    
    # Generate report
    report = processor.generate_report()
    
    # Save results
    output_file = Path(__file__).parent / "batch_results.json"
    processor.save_results(str(output_file))
    
    return processor, results, report


if __name__ == "__main__":
    processor, results, report = example_batch_workflow()
