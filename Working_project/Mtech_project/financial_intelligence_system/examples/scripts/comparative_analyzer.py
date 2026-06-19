"""
Comparative Financial Analysis
Advanced example showing how to perform competitive analysis across multiple companies
"""

import requests
import json
from datetime import datetime
from pathlib import Path


class ComparativeAnalyzer:
    """
    Perform comparative financial analysis across companies.
    """
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.companies = ["Tesla", "Apple", "Microsoft"]
        self.metrics = ["revenue", "profit_margin", "growth_rate", "risk_factors"]
        self.results = {}
    
    def query_metric(self, company: str, metric: str) -> dict:
        """
        Query a specific metric for a company.
        """
        query_map = {
            "revenue": f"What was {company}'s total revenue or quarterly revenue?",
            "profit_margin": f"What is {company}'s gross profit margin or net profit margin?",
            "growth_rate": f"What is {company}'s revenue growth rate?",
            "risk_factors": f"What are the main risk factors for {company}?",
            "cash_flow": f"What is {company}'s operating cash flow?",
            "expansion": f"What expansion plans does {company} mention?"
        }
        
        query = query_map.get(metric, f"Tell me about {company}'s {metric}")
        
        try:
            response = requests.post(
                f"{self.api_base}/query",
                json={
                    "query": query,
                    "parameters": {
                        "max_corrections": 3,
                        "evaluation_threshold": 0.75
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "metric": metric,
                    "company": company,
                    "query": query,
                    "answer": result.get("answer", "N/A"),
                    "confidence": result.get("confidence_score", 0),
                    "evaluation_scores": result.get("evaluation_scores", {})
                }
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_company(self, company: str) -> dict:
        """
        Analyze a single company across multiple metrics.
        """
        print(f"\n{'='*70}")
        print(f"ANALYZING: {company}")
        print('='*70)
        
        company_results = {
            "company": company,
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for metric in self.metrics:
            print(f"  Querying {metric}...", end=" ", flush=True)
            
            result = self.query_metric(company, metric)
            
            if "error" in result:
                print(f"✗ Error: {result['error']}")
            else:
                company_results["metrics"][metric] = result
                confidence = result.get("confidence", 0)
                print(f"✓ (Confidence: {confidence:.1%})")
        
        self.results[company] = company_results
        return company_results
    
    def perform_comparative_analysis(self) -> dict:
        """
        Perform full comparative analysis across all companies.
        """
        print("\n" + "="*70)
        print("COMPARATIVE FINANCIAL ANALYSIS")
        print("="*70)
        
        # Analyze each company
        for company in self.companies:
            self.analyze_company(company)
        
        # Perform cross-company comparisons
        print(f"\n{'='*70}")
        print("CROSS-COMPANY COMPARISONS")
        print('='*70)
        
        comparison_queries = [
            "Compare revenue growth rates across Tesla, Apple, and Microsoft",
            "Which company has the highest profit margin?",
            "What are the common risks across all three companies?",
            "Which company is investing most in artificial intelligence?"
        ]
        
        comparisons = []
        for query in comparison_queries:
            print(f"\nQuery: {query}")
            
            try:
                response = requests.post(
                    f"{self.api_base}/query",
                    json={"query": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ Answer: {result.get('answer', 'N/A')[:150]}...")
                    
                    comparisons.append({
                        "query": query,
                        "answer": result.get("answer"),
                        "confidence": result.get("confidence_score")
                    })
            except Exception as e:
                print(f"✗ Error: {e}")
        
        return {
            "individual_analysis": self.results,
            "comparative_analysis": comparisons
        }
    
    def generate_comparison_report(self) -> str:
        """
        Generate a formatted comparison report.
        """
        report = "\n" + "="*70 + "\n"
        report += "COMPARATIVE FINANCIAL ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"
        
        # Individual company summaries
        report += "COMPANY SUMMARIES:\n"
        report += "-"*70 + "\n\n"
        
        for company, data in self.results.items():
            report += f"\n{company.upper()}\n"
            report += f"Analysis Time: {data['timestamp']}\n"
            report += f"Total Metrics Analyzed: {len(data['metrics'])}\n"
            
            # Show metrics
            for metric_name, metric_data in data['metrics'].items():
                if "error" not in metric_data:
                    confidence = metric_data.get("confidence", 0)
                    answer = metric_data.get("answer", "N/A")
                    # Truncate long answers
                    if len(answer) > 100:
                        answer = answer[:100] + "..."
                    report += f"\n  {metric_name}:\n"
                    report += f"    Answer: {answer}\n"
                    report += f"    Confidence: {confidence:.1%}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report
    
    def save_analysis(self, output_file: str = "comparative_analysis.json"):
        """
        Save analysis results to file.
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Analysis saved to {output_file}")
        return output_file


def example_revenue_comparison():
    """
    Example: Compare revenue metrics across companies.
    """
    print("\n" + "="*70)
    print("REVENUE COMPARISON EXAMPLE")
    print("="*70)
    
    analyzer = ComparativeAnalyzer()
    
    # Specific revenue queries
    revenue_queries = {
        "Tesla": "What was Tesla's total revenue in 2023?",
        "Apple": "What was Apple's Q1 2024 net revenue?",
        "Microsoft": "What was Microsoft's Q2 2024 revenue?"
    }
    
    revenues = {}
    for company, query in revenue_queries.items():
        print(f"\nQuerying {company}...")
        
        try:
            response = requests.post(
                f"{analyzer.api_base}/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                revenues[company] = {
                    "answer": result.get("answer", "N/A"),
                    "confidence": result.get("confidence_score", 0)
                }
                print(f"✓ Revenue: {result.get('answer', 'N/A')[:80]}...")
            else:
                print(f"✗ Error: {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return revenues


def example_margin_analysis():
    """
    Example: Analyze profit margins.
    """
    print("\n" + "="*70)
    print("PROFIT MARGIN ANALYSIS EXAMPLE")
    print("="*70)
    
    analyzer = ComparativeAnalyzer()
    
    # Margin queries
    margin_queries = {
        "Tesla": "What is Tesla's gross profit margin?",
        "Apple": "What is Apple's gross margin in Q1 2024?",
        "Microsoft": "What is Microsoft's operating margin?"
    }
    
    margins = {}
    for company, query in margin_queries.items():
        print(f"\nQuerying {company}...")
        
        try:
            response = requests.post(
                f"{analyzer.api_base}/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                margins[company] = {
                    "answer": result.get("answer", "N/A"),
                    "confidence": result.get("confidence_score", 0)
                }
                print(f"✓ Margin: {result.get('answer', 'N/A')[:80]}...")
            else:
                print(f"✗ Error: {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return margins


def main():
    """
    Run complete comparative analysis.
    """
    # Initialize analyzer
    analyzer = ComparativeAnalyzer()
    
    # Run full analysis
    print("\nStarting comparative analysis...")
    analysis_results = analyzer.perform_comparative_analysis()
    
    # Generate report
    report = analyzer.generate_comparison_report()
    print(report)
    
    # Save results
    analyzer.save_analysis("examples/analysis_results/comparative_analysis.json")
    
    # Save report
    report_file = Path("examples/analysis_results/comparative_report.txt")
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"✓ Report saved to {report_file}")


if __name__ == "__main__":
    main()
