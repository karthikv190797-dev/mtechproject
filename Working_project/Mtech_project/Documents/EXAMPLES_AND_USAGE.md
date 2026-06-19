# Code Examples and Usage Guide

Practical examples demonstrating how to use the Financial Intelligence System.

---

## Table of Contents

1. [Python API Usage](#python-api-usage)
2. [REST API Examples](#rest-api-examples)
3. [Advanced Workflows](#advanced-workflows)
4. [Integration Examples](#integration-examples)
5. [Custom Extensions](#custom-extensions)

---

## Python API Usage

### Basic Query

```python
import requests
from typing import Dict, Any

# Initialize client
base_url = "http://localhost:8000"

def query_financial_question(question: str) -> Dict[str, Any]:
    """
    Submit a financial question and get answered
    
    Args:
        question: Financial question to ask
        
    Returns:
        Response with answer, confidence, and supporting docs
    """
    response = requests.post(
        f"{base_url}/query",
        json={
            "query": question,
            "temperature": 0.7,
            "top_k": 15,
            "max_iterations": 3
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()

# Example usage
result = query_financial_question("What is Apple's revenue in 2023?")

print(f"Question: {result['query']}")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Processing Time: {result['processing_stats']['total_time_ms']}ms")

# Get supporting documents
for doc in result['supporting_documents'][:3]:
    print(f"\n- {doc['title']}")
    print(f"  Relevance: {doc['relevance_score']:.2%}")
    print(f"  Source: {doc['source']}")
```

### Batch Processing

```python
def batch_query(questions: list) -> Dict[str, Any]:
    """
    Process multiple questions in a batch
    
    Args:
        questions: List of financial questions
        
    Returns:
        Batch results with all query responses
    """
    response = requests.post(
        f"{base_url}/batch",
        json={
            "queries": questions,
            "temperature": 0.7,
            "top_k": 15
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()

# Example: Competitive analysis
questions = [
    "What is Apple's revenue in 2023?",
    "What is Microsoft's revenue in 2023?",
    "What is Google's revenue in 2023?",
    "Compare profitability of Apple, Microsoft, and Google"
]

batch_result = batch_query(questions)

print(f"Batch ID: {batch_result['batch_id']}")
print(f"Processed: {batch_result['processed_queries']} queries")
print(f"Total Time: {batch_result['batch_stats']['total_time_ms']}ms")

# Results
for result in batch_result['results']:
    print(f"\nQ: {result['query']}")
    print(f"A: {result['answer'][:200]}...")
    print(f"Confidence: {result['confidence']:.1%}")
```

### Using Python Client Class

```python
class FinIQClient:
    """Client for Financial Intelligence System"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def query(
        self, 
        question: str,
        use_teacher: bool = False,
        temperature: float = 0.7,
        top_k: int = 15
    ) -> Dict:
        """Execute single query"""
        response = self.session.post(
            f"{self.base_url}/query",
            json={
                "query": question,
                "use_teacher_model": use_teacher,
                "temperature": temperature,
                "top_k": top_k
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def batch(self, questions: list, **kwargs) -> Dict:
        """Execute batch query"""
        response = self.session.post(
            f"{self.base_url}/batch",
            json={"queries": questions, **kwargs},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    
    def get_result(self, query_id: str) -> Dict:
        """Get previous query result"""
        response = self.session.get(
            f"{self.base_url}/query/{query_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def statistics(self) -> Dict:
        """Get system statistics"""
        response = self.session.get(
            f"{self.base_url}/statistics",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def health(self) -> Dict:
        """Check system health"""
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

# Usage
client = FinIQClient()

# Single query
result = client.query("What is Apple's dividend policy?")
print(result['answer'])

# Batch processing
results = client.batch([
    "Apple earnings growth",
    "Microsoft market share",
    "Google advertising revenue"
])

# Check system
stats = client.statistics()
print(f"Total queries: {stats['query_statistics']['total_queries']}")
```

---

## REST API Examples

### Using cURL

```bash
# Simple query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Apple revenue in 2023?",
    "temperature": 0.7
  }' | jq '.answer'

# Extract specific fields
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Apple revenue"}' \
| jq '{answer: .answer, confidence: .confidence, time: .processing_stats.total_time_ms}'

# Save full response
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Apple revenue"}' \
  > response.json

# Batch processing
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "Apple revenue",
      "Microsoft earnings",1
      "Google market cap"
    ]
  }' | jq '.results[] | {query: .query, confidence: .confidence}'
```

### Using Python Requests

```python
import requests
import json

base_url = "http://localhost:8000"

# Query with custom parameters
response = requests.post(
    f"{base_url}/query",
    json={
        "query": "What factors influence stock prices?",
        "temperature": 0.5,  # More deterministic
        "top_k": 20,
        "max_iterations": 3,
        "use_teacher_model": True  # Use teacher for better reasoning
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Answer: {data['answer']}")
    print(f"Confidence: {data['confidence']:.1%}")
    
    # Evaluate quality
    scores = data['evaluation_scores']
    print(f"\nEvaluation Scores:")
    print(f"  Relevance: {scores['relevance']:.2%}")
    print(f"  Factuality: {scores['factuality']:.2%}")
    print(f"  Numerical: {scores['numerical_coherence']:.2%}")
    print(f"  Entailment: {scores['entailment']:.2%}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Using JavaScript/Fetch

```javascript
// Query endpoint
async function queryFinancial(question) {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: question,
            temperature: 0.7,
            top_k: 15
        })
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
}

// Usage
async function main() {
    try {
        const result = await queryFinancial("What is Apple's revenue?");
        
        console.log(`Question: ${result.query}`);
        console.log(`Answer: ${result.answer}`);
        console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
        console.log(`Time: ${result.processing_stats.total_time_ms}ms`);
        
        // Display supporting documents
        console.log('\nSupporting Documents:');
        result.supporting_documents.forEach((doc, idx) => {
            console.log(`${idx + 1}. ${doc.title} (${(doc.relevance_score * 100).toFixed(0)}%)`);
        });
        
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
```

---

## Advanced Workflows

### Financial Analysis Pipeline

```python
class FinancialAnalyzer:
    """Analyze company financials using the system"""
    
    def __init__(self, client):
        self.client = client
    
    def analyze_company(self, company_name: str) -> Dict:
        """
        Comprehensive financial analysis of a company
        """
        # Define analysis queries
        queries = [
            f"What is {company_name}'s total revenue for the last 3 years?",
            f"What is {company_name}'s net income and profit margin?",
            f"What is {company_name}'s debt-to-equity ratio?",
            f"What are {company_name}'s main revenue sources?",
            f"What are the risks and challenges facing {company_name}?",
            f"What is {company_name}'s capital expenditure and investment strategy?"
        ]
        
        # Process batch
        batch_result = self.client.batch(queries)
        
        # Structure results
        analysis = {
            "company": company_name,
            "timestamp": batch_result['created_at'],
            "metrics": {},
            "risks": [],
            "strategy": ""
        }
        
        for result in batch_result['results']:
            if "revenue" in result['query'].lower():
                analysis['metrics']['revenue'] = result['answer']
            elif "profit" in result['query'].lower():
                analysis['metrics']['profitability'] = result['answer']
            elif "debt" in result['query'].lower():
                analysis['metrics']['leverage'] = result['answer']
            elif "risk" in result['query'].lower():
                analysis['risks'].append(result['answer'])
            elif "strategy" in result['query'].lower():
                analysis['strategy'] = result['answer']
        
        return analysis

# Usage
client = FinIQClient()
analyzer = FinancialAnalyzer(client)

apple_analysis = analyzer.analyze_company("Apple")
print(json.dumps(apple_analysis, indent=2))
```

### Comparative Analysis

```python
def compare_companies(companies: list) -> Dict:
    """
    Compare financial metrics across multiple companies
    """
    client = FinIQClient()
    
    # Build comparison queries
    queries = []
    for company in companies:
        queries.append(f"What is {company}'s market capitalisation?")
        queries.append(f"What is {company}'s P/E ratio?")
        queries.append(f"What is {company}'s revenue growth rate?")
    
    # Process batch
    batch_result = client.batch(queries)
    
    # Organize by company
    comparison = {company: {} for company in companies}
    
    for i, result in enumerate(batch_result['results']):
        company_idx = i // 3
        metric_idx = i % 3
        
        company = companies[company_idx]
        
        if metric_idx == 0:
            comparison[company]['market_cap'] = result['answer']
        elif metric_idx == 1:
            comparison[company]['pe_ratio'] = result['answer']
        elif metric_idx == 2:
            comparison[company]['revenue_growth'] = result['answer']
    
    return comparison

# Usage
comparison = compare_companies(['Apple', 'Microsoft', 'Google'])
print(json.dumps(comparison, indent=2))
```

### Temporal Analysis

```python
def analyze_temporal_trends(company: str, years: list) -> Dict:
    """
    Analyze financial trends over multiple years
    """
    client = FinIQClient()
    
    # Build queries for different years
    queries = [
        f"What was {company}'s revenue in {year}?"
        for year in years
    ]
    
    batch_result = client.batch(queries)
    
    # Extract and structure data
    trends = {
        "company": company,
        "years": {}
    }
    
    for year, result in zip(years, batch_result['results']):
        trends['years'][year] = {
            "answer": result['answer'],
            "confidence": result['confidence'],
            "data_sources": len(result['supporting_documents'])
        }
    
    return trends

# Usage
trends = analyze_temporal_trends('Apple', [2020, 2021, 2022, 2023])
print(json.dumps(trends, indent=2))
```

---

## Integration Examples

### Slack Integration

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackFinIQBot:
    def __init__(self, slack_token: str, finiq_url: str = "http://localhost:8000"):
        self.slack_client = WebClient(token=slack_token)
        self.finiq_client = FinIQClient(finiq_url)
    
    def handle_message(self, event):
        """Handle financial questions from Slack"""
        channel = event['channel']
        text = event['text']
        user = event['user']
        
        # For messages starting with @finiq
        if text.startswith('@finiq '):
            question = text.replace('@finiq', '').strip()
            
            # Show it's being processed
            self.slack_client.reactions_add(
                channel=channel,
                timestamp=event['ts'],
                emoji='hourglass_flowing_sand'
            )
            
            # Query system
            result = self.finiq_client.query(question)
            
            # Format response
            message = f"""
:chart_with_upwards_trend: *Financial Analysis*

*Question:* {question}

*Answer:* {result['answer'][:500]}...

*Confidence:* {result['confidence']:.1%}

*Supporting Documents:* {len(result['supporting_documents'])} sources found
            """
            
            # Send to Slack
            self.slack_client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=event.get('thread_ts', event['ts'])
            )
            
            # Remove hourglass emoji
            self.slack_client.reactions_remove(
                channel=channel,
                timestamp=event['ts'],
                emoji='hourglass_flowing_sand'
            )

# Usage: Run in your Slack bot event handler
```

### Dashboard Integration

```python
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Financial Intelligence Dashboard")

col1, col2 = st.columns(2)

# Query Interface
with col1:
    st.header("Financial Query")
    question = st.text_input("Ask a financial question:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    with col_b:
        top_k = st.slider("Documents", 5, 50, 15)
    
    if st.button("Analyze"):
        client = FinIQClient()
        result = client.query(question, temperature=temperature, top_k=top_k)
        
        # Display results
        st.success("✓ Analysis Complete")
        
        st.subheader("Answer")
        st.write(result['answer'])
        
        st.subheader("Confidence Metrics")
        scores_df = pd.DataFrame({
            'Metric': ['Relevance', 'Factuality', 'Numerical', 'Entailment'],
            'Score': [
                result['evaluation_scores']['relevance'],
                result['evaluation_scores']['factuality'],
                result['evaluation_scores']['numerical_coherence'],
                result['evaluation_scores']['entailment']
            ]
        })
        st.bar_chart(scores_df.set_index('Metric'))

# System Statistics
with col2:
    st.header("System Statistics")
    
    client = FinIQClient()
    stats = client.statistics()
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.metric(
            "Total Queries",
            stats['query_statistics']['total_queries']
        )
        st.metric(
            "Avg Confidence",
            f"{stats['query_statistics']['avg_confidence']:.1%}"
        )
    
    with col_y:
        st.metric(
            "Avg Response Time",
            f"{stats['performance_stats']['avg_total_time_ms']:.0f}ms"
        )
        st.metric(
            "Correction Rate",
            f"{stats['component_stats']['evaluation']['correction_rate']:.1%}"
        )
    
    # Confidence distribution chart
    conf_data = stats['query_statistics']['confidence_distribution']
    fig = px.pie(
        values=[conf_data['high']['count'], conf_data['medium']['count'], conf_data['low']['count']],
        names=['High', 'Medium', 'Low'],
        title='Confidence Distribution'
    )
    st.plotly_chart(fig)
```

### Email Report Generator

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime, timedelta

def generate_executive_report(companies: list, email_to: str):
    """Generate daily financial report and email"""
    
    client = FinIQClient()
    
    # Analyze each company
    analyses = {}
    for company in companies:
        queries = [
            f"What is {company}'s stock performance this week?",
            f"What are recent news and developments for {company}?",
            f"What is the analyst sentiment for {company}?"
        ]
        
        batch_result = client.batch(queries)
        analyses[company] = batch_result['results']
    
    # Generate HTML email
    html = """
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h1>Financial Intelligence Report</h1>
        <p>Generated on {}</p>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    for company, results in analyses.items():
        html += f"<h2>{company}</h2>"
        for result in results[:3]:
            html += f"<h3>{result['query']}</h3>"
            html += f"<p>{result['answer'][:300]}...</p>"
            html += f"<p><em>Confidence: {result['confidence']:.1%}</em></p>"
    
    html += """
      </body>
    </html>
    """
    
    # Send email
    msg = MIMEMultipart()
    msg['Subject'] = f"Financial Intelligence Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = "finiq@company.com"
    msg['To'] = email_to
    
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')
        server.send_message(msg)
    
    print(f"Report sent to {email_to}")

# Schedule with APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: generate_executive_report(
        ['Apple', 'Microsoft', 'Google'],
        'executive@company.com'
    ),
    'cron',
    hour=8,  # 8 AM daily
    minute=0
)
scheduler.start()
```

---

## Custom Extensions

### Custom Retriever

```python
from src.retrieval.hybrid_retriever import HybridRetriever

class CustomRetriever(HybridRetriever):
    """Extended retriever with domain-specific ranking"""
    
    def retrieve(self, query: str, top_k: int = 20, sector: str = None):
        # Get base results
        results = super().retrieve(query, top_k)
        
        # Apply sector filter if specified
        if sector:
            results = [
                r for r in results 
                if r.document.metadata.get('sector') == sector
            ]
        
        # Apply domain-specific ranking
        for result in results:
            # Boost relevance for recent documents
            days_old = (datetime.now() - result.document.timestamp).days
            time_factor = 1.0 / (1 + days_old / 365)
            result.relevance *= (0.9 + 0.1 * time_factor)
        
        # Re-rank by adjusted relevance
        results.sort(key=lambda x: x.relevance, reverse=True)
        
        return results[:top_k]
```

### Custom Evaluator

```python
from src.evaluation.evaluator import EvaluatorAgent

class ExtendedEvaluator(EvaluatorAgent):
    """Extended evaluator with domain-specific metrics"""
    
    def evaluate_financial_accuracy(self, answer: str, context: str) -> float:
        """Check financial data accuracy"""
        # Extract numbers from answer and context
        import re
        
        answer_numbers = re.findall(r'\d+\.?\d*', answer)
        context_numbers = re.findall(r'\d+\.?\d*', context)
        
        # Check consistency
        matches = sum(1 for n in answer_numbers if n in context_numbers)
        if not answer_numbers:
            return 1.0
        
        return matches / len(answer_numbers)
    
    def evaluate(self, query: str, answer: str, context: str):
        base_score = super().evaluate(query, answer, context)
        
        # Add financial accuracy
        financial_accuracy = self.evaluate_financial_accuracy(answer, context)
        
        # Incorporate into overall score
        updated_combined = (
            base_score.combined * 0.9 +
            financial_accuracy * 0.1
        )
        
        base_score.combined = updated_combined
        return base_score
```

---

**Document Version**: 1.0  
**Last Updated**: June 2026
