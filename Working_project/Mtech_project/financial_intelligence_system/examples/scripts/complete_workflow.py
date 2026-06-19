"""
Complete End-to-End Analysis Example
Demonstrates a full workflow from document loading to analysis to reporting
"""

import json
import time
from pathlib import Path
from datetime import datetime
import requests


class FinancialAnalysisWorkflow:
    """
    Complete workflow for financial intelligence analysis.
    """
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "workflow_id": self.workflow_id,
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }
    
    def stage_1_health_check(self):
        """
        Stage 1: Verify system health and readiness.
        """
        print("\n" + "="*70)
        print("STAGE 1: SYSTEM HEALTH CHECK")
        print("="*70)
        
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✓ API Status: {health.get('status', 'OK')}")
                print(f"  Components: {json.dumps(health.get('components', {}), indent=2)}")
                self.results["stages"]["health_check"] = {
                    "status": "passed",
                    "health": health
                }
                return True
            else:
                print(f"✗ API Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def stage_2_load_documents(self):
        """
        Stage 2: Load and prepare financial documents.
        """
        print("\n" + "="*70)
        print("STAGE 2: DOCUMENT LOADING AND PREPARATION")
        print("="*70)
        
        # Create sample documents
        sample_data = {
            "tesla_doc": "Tesla, Inc. reported total revenue of $81.46 billion in 2023, up 34.5% from $60.57 billion in 2022. Gross profit margin declined to 15.5% from 27.1% due to increased competition and lower pricing.",
            "apple_doc": "Apple delivered net revenue of $119.6 billion in Q1 2024, up 11.2% year-over-year. Gross margin expanded to 46.2% from 44.3% in the prior year. Services revenue grew 13.9%.",
            "microsoft_doc": "Microsoft's Q2 2024 revenue reached $72.8 billion, up 16% year-over-year. Azure grew 29% while AI services adoption accelerated. Operating margin improved to 38.8%."
        }
        
        docs_loaded = len(sample_data)
        print(f"✓ Loaded {docs_loaded} financial documents")
        for doc_id, content in sample_data.items():
            print(f"  - {doc_id}: {len(content)} characters")
        
        self.results["stages"]["document_loading"] = {
            "status": "passed",
            "documents_loaded": docs_loaded,
            "total_characters": sum(len(d) for d in sample_data.values())
        }
        
        return sample_data
    
    def stage_3_formulate_queries(self):
        """
        Stage 3: Formulate comprehensive analysis queries.
        """
        print("\n" + "="*70)
        print("STAGE 3: QUERY FORMULATION")
        print("="*70)
        
        queries = [
            {
                "query_id": "comp_revenue",
                "query": "Compare the revenue figures for Tesla, Apple, and Microsoft",
                "category": "comparative_analysis"
            },
            {
                "query_id": "tesla_margin",
                "query": "Explain the factors behind Tesla's margin compression",
                "category": "root_cause_analysis"
            },
            {
                "query_id": "growth_drivers",
                "query": "What are the key growth drivers for each company?",
                "category": "trend_analysis"
            },
            {
                "query_id": "profitability",
                "query": "How do the profitability metrics compare across companies?",
                "category": "financial_metrics"
            },
            {
                "query_id": "future_outlook",
                "query": "What are the growth prospects for these technology companies?",
                "category": "forward_looking"
            }
        ]
        
        print(f"✓ Formulated {len(queries)} analysis queries")
        for q in queries:
            print(f"  - {q['query_id']}: {q['query'][:50]}...")
        
        self.results["stages"]["query_formulation"] = {
            "status": "passed",
            "queries_count": len(queries)
        }
        
        return queries
    
    def stage_4_execute_queries(self, queries):
        """
        Stage 4: Execute queries against the API.
        """
        print("\n" + "="*70)
        print("STAGE 4: QUERY EXECUTION")
        print("="*70)
        
        query_results = []
        successful = 0
        failed = 0
        
        for idx, query_obj in enumerate(queries, 1):
            query = query_obj["query"]
            query_id = query_obj["query_id"]
            
            try:
                print(f"\n[{idx}/{len(queries)}] Query: {query_id}")
                print(f"  Question: {query}")
                
                response = requests.post(
                    f"{self.api_base}/query",
                    json={
                        "query": query,
                        "parameters": {
                            "max_corrections": 3,
                            "evaluation_threshold": 0.7,
                            "return_supporting_docs": True
                        }
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result["query_id"] = query_id
                    result["category"] = query_obj.get("category")
                    query_results.append(result)
                    
                    confidence = result.get("confidence_score", 0)
                    print(f"  ✓ Confidence: {confidence:.1%}")
                    print(f"  ✓ Answer: {result.get('answer', 'N/A')[:100]}...")
                    successful += 1
                else:
                    print(f"  ✗ Failed: {response.status_code}")
                    failed += 1
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                failed += 1
        
        print(f"\n✓ Query Execution Complete: {successful} successful, {failed} failed")
        
        self.results["stages"]["query_execution"] = {
            "status": "passed",
            "successful_queries": successful,
            "failed_queries": failed,
            "total_queries": len(queries)
        }
        
        return query_results
    
    def stage_5_evaluate_results(self, query_results):
        """
        Stage 5: Evaluate and analyze results.
        """
        print("\n" + "="*70)
        print("STAGE 5: RESULT EVALUATION")
        print("="*70)
        
        if not query_results:
            print("✗ No results to evaluate")
            return {}
        
        # Calculate metrics
        total_results = len(query_results)
        avg_confidence = sum(r.get("confidence_score", 0) for r in query_results) / total_results
        high_confidence = sum(1 for r in query_results if r.get("confidence_score", 0) >= 0.8)
        avg_corrections = sum(r.get("corrections_applied", 0) for r in query_results) / total_results
        
        evaluation = {
            "total_results": total_results,
            "average_confidence": avg_confidence,
            "high_confidence_count": high_confidence,
            "high_confidence_pct": (high_confidence / total_results * 100),
            "average_corrections": avg_corrections
        }
        
        print(f"Total Results: {evaluation['total_results']}")
        print(f"Average Confidence: {evaluation['average_confidence']:.1%}")
        print(f"High Confidence (≥80%): {evaluation['high_confidence_count']}/{total_results} ({evaluation['high_confidence_pct']:.1f}%)")
        print(f"Average Corrections Applied: {evaluation['average_corrections']:.2f}")
        
        self.results["stages"]["result_evaluation"] = {
            "status": "passed",
            "evaluation_metrics": evaluation
        }
        
        return evaluation
    
    def stage_6_generate_report(self, query_results, evaluation):
        """
        Stage 6: Generate comprehensive analysis report.
        """
        print("\n" + "="*70)
        print("STAGE 6: REPORT GENERATION")
        print("="*70)
        
        report = {
            "title": "Financial Intelligence Analysis Report",
            "workflow_id": self.workflow_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_queries": len(query_results),
                "evaluation_metrics": evaluation,
                "categories": {}
            },
            "detailed_results": []
        }
        
        # Categorize results
        categories = {}
        for result in query_results:
            category = result.get("category", "uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        report["summary"]["categories"] = {
            cat: len(results) for cat, results in categories.items()
        }
        
        # Add detailed results
        for result in query_results:
            report["detailed_results"].append({
                "query_id": result.get("query_id"),
                "category": result.get("category"),
                "query": result.get("query", "N/A"),
                "answer": result.get("answer", "N/A")[:200],
                "confidence": result.get("confidence_score"),
                "evaluation_scores": result.get("evaluation_scores", {}),
                "corrections_applied": result.get("corrections_applied", 0)
            })
        
        print(f"✓ Report generated with {len(report['detailed_results'])} results")
        print(f"  Categories: {list(report['summary']['categories'].keys())}")
        
        self.results["stages"]["report_generation"] = {
            "status": "passed",
            "report_sections": len(report['detailed_results'])
        }
        
        return report
    
    def stage_7_save_outputs(self, report):
        """
        Stage 7: Save analysis outputs and artifacts.
        """
        print("\n" + "="*70)
        print("STAGE 7: OUTPUT STORAGE")
        print("="*70)
        
        output_dir = Path("./analysis_outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Save report
        report_file = output_dir / f"report_{self.workflow_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✓ Report saved: {report_file}")
        
        # Save workflow metadata
        metadata_file = output_dir / f"metadata_{self.workflow_id}.json"
        self.results["end_time"] = datetime.now().isoformat()
        with open(metadata_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Metadata saved: {metadata_file}")
        
        self.results["stages"]["output_storage"] = {
            "status": "passed",
            "report_file": str(report_file),
            "metadata_file": str(metadata_file)
        }
        
        return report_file, metadata_file
    
    def run_complete_workflow(self):
        """
        Execute the complete analysis workflow.
        """
        print("\n" + "="*80)
        print(" " * 15 + "FINANCIAL INTELLIGENCE ANALYSIS WORKFLOW")
        print("="*80)
        print(f"Workflow ID: {self.workflow_id}")
        print(f"Start Time: {self.results['start_time']}")
        
        # Stage 1: Health Check
        if not self.stage_1_health_check():
            print("Workflow aborted: System health check failed")
            return None
        
        # Stage 2: Load Documents
        documents = self.stage_2_load_documents()
        
        # Stage 3: Formulate Queries
        queries = self.stage_3_formulate_queries()
        
        # Stage 4: Execute Queries
        query_results = self.stage_4_execute_queries(queries)
        
        # Stage 5: Evaluate Results
        evaluation = self.stage_5_evaluate_results(query_results)
        
        # Stage 6: Generate Report
        report = self.stage_6_generate_report(query_results, evaluation)
        
        # Stage 7: Save Outputs
        report_file, metadata_file = self.stage_7_save_outputs(report)
        
        # Summary
        print("\n" + "="*80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Report: {report_file}")
        print(f"Metadata: {metadata_file}")
        print("="*80)
        
        return {
            "workflow_id": self.workflow_id,
            "report": report,
            "report_file": report_file,
            "metadata_file": metadata_file
        }


def main():
    """
    Execute the complete end-to-end workflow.
    """
    workflow = FinancialAnalysisWorkflow()
    result = workflow.run_complete_workflow()
    
    if result:
        print("\n✓ Analysis workflow completed successfully!")
        return result
    else:
        print("\n✗ Analysis workflow failed!")
        return None


if __name__ == "__main__":
    main()
