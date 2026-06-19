"""
COMPREHENSIVE GUIDE: Using the Financial Intelligence System
Complete tutorial with step-by-step examples
"""

# =============================================================================
# 1. BASIC QUERY EXAMPLE
# =============================================================================

import requests
import json

API_BASE = "http://localhost:8000"

# Example 1: Simple Query
def basic_query_example():
    """
    Execute a basic query to the Financial Intelligence System.
    """
    query = "What was Tesla's revenue growth rate in 2023?"
    
    payload = {
        "query": query,
        "documents": [],  # Optional: provide specific documents
        "parameters": {
            "max_corrections": 3,
            "evaluation_threshold": 0.7
        }
    }
    
    response = requests.post(
        f"{API_BASE}/query",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Query: {query}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence_score']:.2%}")
        print(f"Evaluation Scores: {result['evaluation_scores']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None


# =============================================================================
# 2. BATCH PROCESSING EXAMPLE
# =============================================================================

def batch_processing_example():
    """
    Submit multiple queries for batch processing.
    """
    queries = [
        "What are Tesla's key risk factors?",
        "Compare Apple's gross margin with the prior year",
        "What is Microsoft's AI investment strategy?"
    ]
    
    batch_payload = {
        "queries": queries,
        "batch_id": "example_batch_001",
        "max_parallel_processing": 3
    }
    
    response = requests.post(
        f"{API_BASE}/batch",
        json=batch_payload
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"Batch ID: {results['batch_id']}")
        print(f"Total Queries: {results['total_queries']}")
        print(f"Completed: {results['completed_queries']}")
        return results
    else:
        print(f"Batch processing error: {response.status_code}")
        return None


# =============================================================================
# 3. RETRIEVE STATISTICS
# =============================================================================

def statistics_example():
    """
    Get system statistics and performance metrics.
    """
    response = requests.get(f"{API_BASE}/statistics")
    
    if response.status_code == 200:
        stats = response.json()
        print("System Statistics:")
        print(f"  Total Queries Processed: {stats.get('total_queries', 0)}")
        print(f"  Average Response Time: {stats.get('avg_response_time_ms', 0):.1f}ms")
        print(f"  Average Confidence Score: {stats.get('avg_confidence', 0):.2%}")
        print(f"  Documents in System: {stats.get('total_documents', 0)}")
        return stats
    else:
        print(f"Statistics error: {response.status_code}")
        return None


# =============================================================================
# 4. CHECK HEALTH
# =============================================================================

def health_check_example():
    """
    Verify system health and component status.
    """
    response = requests.get(f"{API_BASE}/health")
    
    if response.status_code == 200:
        health = response.json()
        print("System Health Status:")
        print(f"  Status: {health['status']}")
        print(f"  Version: {health.get('version', 'N/A')}")
        print(f"  Components: {health.get('components', {})}")
        return health
    else:
        print(f"Health check failed: {response.status_code}")
        return None


# =============================================================================
# 5. ADVANCED QUERY WITH PARAMETERS
# =============================================================================

def advanced_query_example():
    """
    Execute a query with advanced parameters for fine-grained control.
    """
    query = "Analyze the impact of AI investment on Microsoft's Azure growth"
    
    payload = {
        "query": query,
        "parameters": {
            "retrieval_method": "hybrid",  # Options: semantic, keyword, hybrid
            "retrieval_top_k": 5,  # Number of documents to retrieve
            "reasoning_model": "distilled",  # Options: teacher, student, distilled
            "evaluation_threshold": 0.8,  # Confidence threshold (0-1)
            "max_corrections": 3,  # Maximum correction iterations
            "return_supporting_docs": True,
            "explain_reasoning": True
        }
    }
    
    response = requests.post(
        f"{API_BASE}/query",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print("=== Advanced Query Result ===")
        print(f"Query: {query}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence Score: {result['confidence_score']:.2%}")
        print(f"Evaluation Details: {result['evaluation_scores']}")
        if 'supporting_documents' in result:
            print(f"Supporting Documents: {result['supporting_documents']}")
        if 'reasoning_steps' in result:
            print(f"Reasoning Steps: {result['reasoning_steps']}")
        return result
    else:
        print(f"Advanced query error: {response.status_code}")
        return None


# =============================================================================
# 6. RETRIEVE SPECIFIC QUERY RESULTS
# =============================================================================

def retrieve_query_result(query_id):
    """
    Retrieve results of a specific query by ID.
    """
    response = requests.get(f"{API_BASE}/query/{query_id}")
    
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Query result not found: {response.status_code}")
        return None


# =============================================================================
# 7. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FINANCIAL INTELLIGENCE SYSTEM - API USAGE EXAMPLES")
    print("=" * 70)
    
    # Check system health first
    print("\n1. Health Check:")
    print("-" * 70)
    health_check_example()
    
    # Basic query
    print("\n2. Basic Query Example:")
    print("-" * 70)
    basic_result = basic_query_example()
    
    # Advanced query
    print("\n3. Advanced Query with Parameters:")
    print("-" * 70)
    advanced_result = advanced_query_example()
    
    # Statistics
    print("\n4. System Statistics:")
    print("-" * 70)
    stats = statistics_example()
    
    # Batch processing
    print("\n5. Batch Processing:")
    print("-" * 70)
    batch_result = batch_processing_example()
    
    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)
