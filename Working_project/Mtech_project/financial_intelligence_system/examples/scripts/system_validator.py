"""
System Integration Tests and Validation
Comprehensive testing suite for the Financial Intelligence System
"""

import requests
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SystemValidator:
    """
    Validate system components and functionality.
    """
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.test_results = {
            "timestamp": None,
            "tests": [],
            "summary": {}
        }
        self.passed = 0
        self.failed = 0
    
    def test_health_check(self) -> Tuple[bool, str]:
        """Test 1: API Health Check"""
        test_name = "Health Check"
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                status = health.get('status') == 'operational'
                return (True, f"✓ Status: {health.get('status')}"), status
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_simple_query(self) -> Tuple[bool, str]:
        """Test 2: Basic Query Processing"""
        test_name = "Basic Query"
        try:
            query = "What was Tesla's revenue in 2023?"
            response = requests.post(
                f"{self.api_base}/query",
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                has_answer = bool(result.get('answer'))
                has_confidence = 'confidence_score' in result
                
                if has_answer and has_confidence:
                    return (True, f"✓ Query processed (confidence: {result['confidence_score']:.1%})"), True
                else:
                    return (False, "✗ Missing required fields"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_advanced_query(self) -> Tuple[bool, str]:
        """Test 3: Query with Parameters"""
        test_name = "Advanced Query"
        try:
            response = requests.post(
                f"{self.api_base}/query",
                json={
                    "query": "Analyze profit margin trends",
                    "parameters": {
                        "retrieval_method": "hybrid",
                        "max_corrections": 2,
                        "evaluation_threshold": 0.7
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                has_scores = 'evaluation_scores' in result
                if has_scores:
                    return (True, "✓ Advanced parameters processed"), True
                else:
                    return (False, "✗ Missing evaluation scores"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_batch_processing(self) -> Tuple[bool, str]:
        """Test 4: Batch Query Processing"""
        test_name = "Batch Processing"
        try:
            queries = [
                "What was Tesla's revenue?",
                "What is Apple's profit margin?",
                "Describe Microsoft's AI strategy"
            ]
            
            response = requests.post(
                f"{self.api_base}/batch",
                json={
                    "queries": queries,
                    "batch_id": "test_batch_001"
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('batch_id') and result.get('total_queries'):
                    return (True, f"✓ Batch: {result['total_queries']} queries"), True
                else:
                    return (False, "✗ Invalid batch response"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_statistics(self) -> Tuple[bool, str]:
        """Test 5: System Statistics"""
        test_name = "Statistics"
        try:
            response = requests.get(f"{self.api_base}/statistics", timeout=5)
            
            if response.status_code == 200:
                stats = response.json()
                has_metrics = (
                    'total_queries' in stats and
                    'avg_response_time_ms' in stats
                )
                if has_metrics:
                    avg_time = stats.get('avg_response_time_ms', 0)
                    total = stats.get('total_queries', 0)
                    return (True, f"✓ Queries: {total}, Avg Time: {avg_time:.0f}ms"), True
                else:
                    return (False, "✗ Missing statistics"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_error_handling(self) -> Tuple[bool, str]:
        """Test 6: Error Handling"""
        test_name = "Error Handling"
        try:
            # Test invalid query format
            response = requests.post(
                f"{self.api_base}/query",
                json={"invalid_field": "test"},
                timeout=5
            )
            
            # Should return 422 (validation error) or similar
            if response.status_code >= 400:
                return (True, "✓ Error handling works"), True
            else:
                return (False, "✗ Should return error for invalid request"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_response_time(self) -> Tuple[bool, str]:
        """Test 7: Response Time Performance"""
        test_name = "Response Time"
        try:
            start = time.time()
            
            response = requests.post(
                f"{self.api_base}/query",
                json={"query": "What was Apple's revenue?"},
                timeout=30
            )
            
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            if response.status_code == 200:
                performance = "Excellent" if elapsed < 2000 else \
                             "Good" if elapsed < 5000 else \
                             "Acceptable" if elapsed < 10000 else "Slow"
                return (True, f"✓ Response time: {elapsed:.0f}ms ({performance})"), True
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_confidence_score_range(self) -> Tuple[bool, str]:
        """Test 8: Confidence Score Validity"""
        test_name = "Confidence Score"
        try:
            response = requests.post(
                f"{self.api_base}/query",
                json={"query": "Test query"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                confidence = result.get('confidence_score')
                
                if confidence is not None and 0 <= confidence <= 1:
                    return (True, f"✓ Confidence score valid: {confidence:.2f}"), True
                else:
                    return (False, f"✗ Invalid confidence: {confidence}"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_concurrent_requests(self) -> Tuple[bool, str]:
        """Test 9: Concurrent Request Handling"""
        test_name = "Concurrent Requests"
        try:
            import threading
            
            results = []
            errors = []
            
            def make_request():
                try:
                    response = requests.post(
                        f"{self.api_base}/query",
                        json={"query": "Test query"},
                        timeout=10
                    )
                    results.append(response.status_code == 200)
                except Exception as e:
                    errors.append(str(e))
            
            # Create 3 concurrent threads
            threads = [threading.Thread(target=make_request) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            success_count = sum(results)
            if success_count >= 2:  # At least 2 out of 3 succeeded
                return (True, f"✓ Handled {success_count}/3 concurrent requests"), True
            else:
                return (False, f"✗ Only {success_count}/3 concurrent requests succeeded"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def test_data_format_consistency(self) -> Tuple[bool, str]:
        """Test 10: Response Format Consistency"""
        test_name = "Data Format"
        try:
            response = requests.post(
                f"{self.api_base}/query",
                json={"query": "Example query"}
            )
            
            if response.status_code == 200:
                result = response.json()
                required_fields = ['answer', 'confidence_score', 'query', 'evaluation_scores']
                missing_fields = [f for f in required_fields if f not in result]
                
                if not missing_fields:
                    return (True, "✓ Response format consistent"), True
                else:
                    return (False, f"✗ Missing fields: {missing_fields}"), False
            else:
                return (False, f"✗ Status: {response.status_code}"), False
        except Exception as e:
            return (False, f"✗ Error: {str(e)}"), False
    
    def run_all_tests(self) -> Dict:
        """
        Run all validation tests.
        """
        import inspect
        
        print("\n" + "="*70)
        print("SYSTEM VALIDATION TEST SUITE")
        print("="*70)
        
        test_methods = [
            method for method in dir(self)
            if method.startswith('test_') and callable(getattr(self, method))
        ]
        
        self.test_results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        for test_method in sorted(test_methods):
            test_name = test_method.replace('test_', '').replace('_', ' ').title()
            method = getattr(self, test_method)
            
            print(f"\n[{len(self.test_results['tests'])+1}] {test_name}...", end=" ", flush=True)
            
            try:
                (success, message), status = method()
                
                if status:
                    print(message)
                    self.passed += 1
                else:
                    print(message)
                    self.failed += 1
                
                self.test_results["tests"].append({
                    "name": test_name,
                    "result": "PASSED" if status else "FAILED",
                    "message": message
                })
            except Exception as e:
                print(f"✗ Exception: {str(e)}")
                self.failed += 1
                self.test_results["tests"].append({
                    "name": test_name,
                    "result": "ERROR",
                    "message": str(e)
                })
        
        # Summary
        self.test_results["summary"] = {
            "total_tests": len(self.test_results["tests"]),
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": f"{(self.passed / len(self.test_results['tests']) * 100):.1f}%"
        }
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.test_results['summary']['total_tests']}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {self.test_results['summary']['pass_rate']}")
        print("="*70)
        
        return self.test_results
    
    def save_results(self, output_file="validation_results.json"):
        """
        Save test results to file.
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n✓ Results saved to {output_file}")
        return output_file


def main():
    """
    Run system validation.
    """
    validator = SystemValidator()
    results = validator.run_all_tests()
    validator.save_results("examples/validation_results.json")
    
    # Return exit code based on test results
    if validator.failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
