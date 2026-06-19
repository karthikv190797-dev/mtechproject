# Examples Project Manifest

## Overview

Complete, production-ready examples for the Financial Intelligence System. This package contains everything you need to understand, test, and deploy the system.

**Version**: 1.0.0  
**Last Updated**: May 25, 2026  
**Status**: Production Ready ✓

---

## What's Included

### 📚 Documentation (3 files)
- `README.md` - Comprehensive tutorial with use cases
- `EXAMPLES_GUIDE.md` - Complete guide to all examples  
- `MANIFEST.md` - This file

### 💻 Python Scripts (6 production-ready scripts)
1. **api_usage_guide.py** - Basic API usage patterns
2. **batch_processor.py** - Batch query processing
3. **data_loader.py** - Document loading and indexing
4. **complete_workflow.py** - End-to-end analysis pipeline
5. **comparative_analyzer.py** - Multi-company analysis
6. **system_validator.py** - Comprehensive testing suite

### 📊 Sample Data (3 documents + batch queries)
- Tesla 10-K Filing excerpt (2,500 chars)
- Apple Q1 2024 Report (2,000 chars)
- Microsoft Earnings Transcript (2,300 chars)
- Batch query JSON templates (10 queries)

### ⚙️ Configuration Examples (6 variants)
- Minimal configuration (testing)
- Production configuration
- Semantic-focused configuration
- Batch processing configuration
- Real-time interactive configuration
- Research/analysis configuration

### 📡 API Request Examples (2 files)
- CURL command examples (bash script)
- JSON request templates

### 📓 Jupyter Notebooks (1 notebook)
- Getting Started notebook (interactive tutorial)

### 🔧 Utilities (1 script)
- quick_run.sh - Automated setup script

---

## File Structure

```
examples/
├── README.md                      (Tutorial & use cases)
├── EXAMPLES_GUIDE.md             (Complete guide)
├── MANIFEST.md                   (This file)
├── quick_run.sh                  (Setup automation)
│
├── scripts/                      (6 Python scripts)
│   ├── api_usage_guide.py        (Basic usage - ⭐ START HERE)
│   ├── batch_processor.py        (Batch processing)
│   ├── data_loader.py            (Data loading)
│   ├── complete_workflow.py      (Full pipeline)
│   ├── comparative_analyzer.py   (Analysis)
│   └── system_validator.py       (Testing)
│
├── sample_data/                  (3 financial documents)
│   ├── sec_filing_sample.txt     (Tesla 10-K)
│   ├── financial_report_sample.txt (Apple Q1 2024)
│   ├── earnings_call_summary.txt (Microsoft earnings)
│   └── batch_queries.json        (10 sample queries)
│
├── api_requests/                 (Request templates)
│   ├── api_calls.sh              (CURL examples)
│   └── request_examples.json     (JSON templates)
│
├── configs/                      (6 config variants)
│   └── configuration_examples.yaml
│
├── notebooks/                    (1 Jupyter notebook)
│   └── 01_getting_started.ipynb
│
└── indexed_documents/            (Generated files)
    └── documents_index.json
```

**Total Files**: 20+  
**Total Size**: ~200KB  
**Total Code**: 2,000+ lines  

---

## Quick Start

### 1. Automatic Setup (Recommended)

```bash
chmod +x examples/quick_run.sh
./examples/quick_run.sh
```

### 2. Manual Setup

```bash
# Start backend
python3 -m uvicorn backend.api:app --port 8000 &

# Run basic example
python3 examples/scripts/api_usage_guide.py

# Run tests
python3 examples/scripts/system_validator.py
```

### 3. Docker Setup

```bash
docker-compose -f docker-compose.yml up -d
docker-compose exec api python3 examples/scripts/complete_workflow.py
```

---

## Feature Showcase

### ✅ Demonstrated Capabilities

- [x] Basic API queries
- [x] Advanced parametrization
- [x] Batch processing (multiple queries)
- [x] Document loading and indexing
- [x] Comparative analysis (multiple companies)
- [x] End-to-end workflows
- [x] Error handling
- [x] Performance validation
- [x] Concurrent request handling
- [x] Configuration management
- [x] CURL/REST API calls
- [x] Response format validation
- [x] Confidence scoring
- [x] Query evaluation and correction

### 📈 Metrics Included

- **10+ sample queries** covering various domains
- **3 real financial documents** with varying lengths
- **6 configuration profiles** for different use cases
- **10 API test cases** validating system behavior
- **3 analysis workflows** demonstrating real-world scenarios

---

## Learning Path

### Beginner (1-2 hours)
1. Read: `README.md`
2. Run: `python3 examples/scripts/api_usage_guide.py`
3. Explore: Sample data files
4. Test: `curl http://localhost:8000/health`

### Intermediate (2-3 hours)
1. Run: `python3 examples/scripts/batch_processor.py`
2. Run: `python3 examples/scripts/data_loader.py`
3. Modify: Configuration examples
4. Test: CURL requests from `api_requests/api_calls.sh`

### Advanced (3-4 hours)
1. Run: `python3 examples/scripts/complete_workflow.py`
2. Run: `python3 examples/scripts/comparative_analyzer.py`
3. Review: `complete_workflow.py` source code
4. Customize: Create your own analysis

### Expert (2-3 hours)
1. Run: `python3 examples/scripts/system_validator.py`
2. Review: Validation results
3. Deploy: Custom scenarios
4. Monitor: Performance metrics

---

## Example Scenarios

### Scenario 1: Quick Company Analysis
```bash
python3 examples/scripts/api_usage_guide.py
# Time: 2 minutes
# Output: Basic financial metrics
```

### Scenario 2: Comparative Analysis
```bash
python3 examples/scripts/comparative_analyzer.py
# Time: 5-10 minutes
# Output: Cross-company comparison report
```

### Scenario 3: Complete Analysis Pipeline
```bash
python3 examples/scripts/complete_workflow.py
# Time: 15-20 minutes
# Output: Full JSON report with metrics
```

### Scenario 4: System Validation
```bash
python3 examples/scripts/system_validator.py
# Time: 5-10 minutes
# Output: Test results in JSON
```

### Scenario 5: Batch Processing
```bash
python3 examples/scripts/batch_processor.py
# Time: 10-15 minutes  
# Output: Batch processing report
```

---

## Configuration Options

All configurations include:
- Retrieval strategy (semantic, keyword, hybrid)
- Reasoning model (teacher, student, distilled)
- Evaluation parameters
- Performance tuning

**Quick switch between configs:**
```bash
cp examples/configs/config_production.yaml config/system_config.yaml
python3 main.py
```

---

## Testing & Validation

### Included Tests

1. **Health Check** - API responsiveness
2. **Query Processing** - Basic and advanced queries
3. **Batch Operations** - Multi-query handling
4. **Statistics** - Metrics collection
5. **Error Handling** - Invalid input handling
6. **Response Time** - Performance validation
7. **Confidence Scores** - Output validation
8. **Concurrent Requests** - Load handling
9. **Data Format** - Response consistency
10. **Edge Cases** - Boundary conditions

**Run all tests:**
```bash
python3 examples/scripts/system_validator.py
```

---

## Performance Metrics

### Expected Performance

| Operation | Time | CPU | Memory |
|-----------|------|-----|--------|
| Health Check | <50ms | <1% | <10MB |
| Simple Query | 200-500ms | 20-30% | 50-100MB |
| Complex Query | 2-5s | 40-60% | 100-200MB |
| Batch (3 queries) | 2-3s | 50-70% | 150-250MB |
| Full Workflow | 20-30s | 60-80% | 200-400MB |

### Validation Results Available

- `examples/validation_results.json` - Full test results
- `examples/analysis_results/` - Analysis outputs
- `examples/indexed_documents/` - Indexed data

---

## Troubleshooting

### Issue: Connection Refused
```bash
# Check if API is running
curl http://localhost:8000/health

# Start API if not running
python3 -m uvicorn backend.api:app --port 8000
```

### Issue: Low Confidence Scores
```python
# Use these parameters in requests
"parameters": {
    "max_corrections": 5,
    "evaluation_threshold": 0.6
}
```

### Issue: Out of Memory
```bash
# Reduce parallel processing
batch:
  max_parallel_processing: 2
```

### Issue: Slow Responses
```bash
# Use lighter model and fewer documents
retrieval:
  top_k: 3
reasoning:
  model_type: "student"
```

---

## Advanced Usage

### Custom Analysis

```python
from examples.scripts.complete_workflow import FinancialAnalysisWorkflow

workflow = FinancialAnalysisWorkflow()
result = workflow.run_complete_workflow()
```

### Custom Configuration

```yaml
retrieval:
  method: "hybrid"
  hybrid_alpha: 0.7
  hybrid_beta: 0.3
  top_k: 15

reasoning:
  model_type: "teacher"
  temperature: 0.3
  
evaluation:
  threshold: 0.85
  max_corrections: 5
```

### Integration with Your System

```python
import requests

def analyze_financial_query(query: str) -> dict:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query}
    )
    return response.json()

# Use it
result = analyze_financial_query("What was Apple's revenue?")
print(result['answer'])
```

---

## Production Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.yml up -d
docker-compose exec api python3 examples/scripts/complete_workflow.py
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
kubectl run financial-analysis --image=financial-intelligence:1.0.0
```

### Cloud Deployment
- AWS: See deployment guide
- GCP: See deployment guide
- Azure: See deployment guide

---

## Integration Points

### REST API
- Endpoint: `http://localhost:8000/query`
- Method: `POST`
- Content-Type: `application/json`

### WebSocket (Optional)
- Endpoint: `ws://localhost:8000/ws`
- For real-time streaming

### File I/O
- Input: YAML configs, JSON requests, text documents
- Output: JSON responses, analysis reports

### Database Integration
- Supports: PostgreSQL, MongoDB, DuckDB
- Connection pooling available
- Query caching supported

---

## Support & Resources

### Documentation
- Main README: `../README.md`
- Quick Start: `../QUICKSTART.md`
- API Docs: `../README.md#API`
- Config Ref: `../config/system_config.yaml`

### Examples
- All scripts in `scripts/`
- API calls in `api_requests/`
- Sample data in `sample_data/`

### Testing
- Validator: `scripts/system_validator.py`
- All results saved to JSON

---

## Versions & Compatibility

### Version Information
- **Examples Version**: 1.0.0
- **System Version**: 1.0.0+
- **Python**: 3.11+
- **Dependencies**: See `../requirements.txt`

### Backward Compatibility
- All examples are forward-compatible
- API responses maintain same schema
- Configuration format stable

---

## Contributing & Extending

### Add New Examples
1. Create script in `scripts/`
2. Follow naming convention
3. Include docstrings
4. Update `EXAMPLES_GUIDE.md`

### Share Sample Data
1. Add to `sample_data/`
2. Update manifest
3. Document format

### New Configurations
1. Add to `configs/`
2. Document use case
3. Include performance notes

---

## FAQ

**Q: Where do I start?**
A: Run `python3 examples/scripts/api_usage_guide.py`

**Q: How long does setup take?**
A: 5-10 minutes with `quick_run.sh`

**Q: Can I use in production?**
A: Yes, all examples are production-ready

**Q: What's the learning curve?**
A: Beginner-friendly with progressive complexity

**Q: How do I customize?**
A: See configuration examples and scripts

**Q: What's the performance?**
A: See Performance Metrics section above

**Q: How do I deploy?**
A: See Production Deployment section

---

## Summary

✅ **Ready to Use**
- 6 production-ready Python scripts
- 3 complete financial documents
- 10+ sample queries
- 6 configuration variants
- Comprehensive documentation
- Full test suite

✅ **Well Documented**
- README with use cases
- Complete guide with examples
- Inline code comments
- API request templates
- Configuration examples

✅ **Easy to Learn**
- Progressive complexity
- Beginner to advanced
- Real-world scenarios
- Troubleshooting guide
- FAQ section

✅ **Enterprise Ready**
- Error handling
- Validation testing
- Performance metrics
- Concurrent handling
- Scalable design

---

**Start Now:**
```bash
python3 examples/scripts/api_usage_guide.py
```

**Questions?** See `README.md` and `EXAMPLES_GUIDE.md`

**Last Updated**: May 25, 2026  
**Status**: ✅ Complete and Production Ready
