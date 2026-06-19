#!/bin/bash
#
# API Request Examples using CURL
# Demonstrates various API endpoints and parameters
#

API_BASE="http://localhost:8000"

echo "=================================================="
echo "FINANCIAL INTELLIGENCE SYSTEM - API EXAMPLES"
echo "=================================================="

# ==========================================================================
# 1. HEALTH CHECK
# ==========================================================================
echo ""
echo "1. Health Check"
echo "--------------------------------------------------"
curl -X GET "$API_BASE/health" \
  -H "Content-Type: application/json" \
  -v

echo ""
echo ""

# ==========================================================================
# 2. SIMPLE QUERY
# ==========================================================================
echo "2. Simple Query"
echo "--------------------------------------------------"
curl -X POST "$API_BASE/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was Teslas total revenue in 2023?"
  }' \
  -v

echo ""
echo ""

# ==========================================================================
# 3. QUERY WITH PARAMETERS
# ==========================================================================
echo "3. Query with Advanced Parameters"
echo "--------------------------------------------------"
curl -X POST "$API_BASE/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain why Tesla'\''s gross margin declined from 27.1% to 15.5%",
    "parameters": {
      "retrieval_method": "hybrid",
      "retrieval_top_k": 5,
      "reasoning_model": "distilled",
      "evaluation_threshold": 0.8,
      "max_corrections": 3,
      "return_supporting_docs": true,
      "explain_reasoning": true
    }
  }' \
  -v

echo ""
echo ""

# ==========================================================================
# 4. BATCH PROCESSING
# ==========================================================================
echo "4. Batch Query Processing"
echo "--------------------------------------------------"
curl -X POST "$API_BASE/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What was Apple'\''s Q1 2024 revenue?",
      "What is Microsoft'\''s strategy on AI investment?",
      "Compare gross margins across all three companies"
    ],
    "batch_id": "example_batch_001",
    "max_parallel_processing": 3
  }' \
  -v

echo ""
echo ""

# ==========================================================================
# 5. STATISTICS
# ==========================================================================
echo "5. Get System Statistics"
echo "--------------------------------------------------"
curl -X GET "$API_BASE/statistics" \
  -H "Content-Type: application/json" \
  -v

echo ""
echo ""

# ==========================================================================
# 6. RETRIEVE SPECIFIC QUERY RESULT
# ==========================================================================
echo "6. Retrieve Specific Query Result"
echo "--------------------------------------------------"
# Note: Replace 'example_query_id' with actual query ID from a previous response
curl -X GET "$API_BASE/query/example_query_id" \
  -H "Content-Type: application/json" \
  -v

echo ""
echo ""

# ==========================================================================
# 7. QUERY WITH CUSTOM DOCUMENTS
# ==========================================================================
echo "7. Query with Custom Context Documents"
echo "--------------------------------------------------"
curl -X POST "$API_BASE/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the revenue growth rate",
    "documents": [
      "SEC FILING - 10-K ANNUAL REPORT",
      "QUARTERLY FINANCIAL REPORT"
    ],
    "parameters": {
      "max_corrections": 2,
      "evaluation_threshold": 0.75
    }
  }' \
  -v

echo ""
echo ""

echo "=================================================="
echo "API Examples Completed"
echo "=================================================="
echo ""
echo "Tips:"
echo "- Replace query IDs with actual IDs from responses"
echo "- Adjust parameters based on your requirements"
echo "- Check API logs for detailed tracing"
echo "- Use 'jq' for pretty-printing JSON responses"
echo ""
echo "Example with jq:"
echo "  curl -s -X GET $API_BASE/health | jq ."
echo ""
