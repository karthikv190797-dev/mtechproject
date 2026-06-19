# Examples Directory Guide

## Overview

This directory contains comprehensive examples, tutorials, and demonstrations of the Financial Intelligence System. All examples are production-ready and can be used as starting points for your own implementations.

---

## Directory Structure

```
examples/
├── README.md                          # Main tutorial guide (START HERE)
├── notebooks/
│   └── 01_getting_started.ipynb       # Jupyter notebook tutorial
├── scripts/
│   ├── api_usage_guide.py             # Basic API usage examples
│   ├── batch_processor.py             # Batch query processing
│   ├── data_loader.py                 # Document loading & indexing
│   ├── complete_workflow.py           # End-to-end analysis workflow
│   ├── comparative_analyzer.py        # Multi-company analysis
│   └── system_validator.py            # System testing & validation
├── sample_data/
│   ├── sec_filing_sample.txt          # Tesla 10-K filing excerpt
│   ├── financial_report_sample.txt    # Apple Q1 2024 report
│   ├── earnings_call_summary.txt      # Microsoft earnings transcript
│   └── batch_queries.json             # Sample batch queries
├── api_requests/
│   ├── api_calls.sh                   # CURL command examples
│   └── request_examples.json          # JSON request templates
├── configs/
│   └── configuration_examples.yaml    # Configuration variants
└── indexed_documents/
    └── documents_index.json           # Generated document index
```

---

## Quick Start Guide

### 1. **Installation** (2 minutes)

```bash
cd financial_intelligence_system
pip install -r requirements.txt
```

### 2. **Start Services** (3 minutes)

```bash
# Terminal 1: Backend
python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (optional)
streamlit run frontend/app.py --server.port 8501
```

### 3. **Validate Setup** (1 minute)

```bash
curl http://localhost:8000/health
```

---

## Example Index

### Entry Level: Getting Started

| Script | Difficulty | Time | Description |
|--------|-----------|------|-------------|
| [API Usage Guide](scripts/api_usage_guide.py) | ⭐ Easy | 5 min | Basic queries and responses |
| [Health Check](#health-check-verification) | ⭐ Easy | 1 min | Verify system is running |
| [Simple Queries](#examples/api_requests) | ⭐ Easy | 2 min | Sample CURL requests |

**Try this first:**
```bash
python3 examples/scripts/api_usage_guide.py
```

### Intermediate: Core Functionality

| Script | Difficulty | Time | Description |
|--------|-----------|------|-------------|
| [Batch Processor](scripts/batch_processor.py) | ⭐⭐ Medium | 10 min | Process multiple queries |
| [Data Loader](scripts/data_loader.py) | ⭐⭐ Medium | 8 min | Load and index documents |
| [Comparative Analyzer](scripts/comparative_analyzer.py) | ⭐⭐ Medium | 12 min | Compare multiple companies |

**Try this next:**
```bash
python3 examples/scripts/batch_processor.py
python3 examples/scripts/data_loader.py
```

### Advanced: Production Workflows

| Script | Difficulty | Time | Description |
|--------|-----------|------|-------------|
| [Complete Workflow](scripts/complete_workflow.py) | ⭐⭐⭐ Hard | 15 min | End-to-end analysis pipeline |
| [System Validator](scripts/system_validator.py) | ⭐⭐⭐ Hard | 10 min | Comprehensive testing suite |

**Production ready:**
```bash
python3 examples/scripts/complete_workflow.py
python3 examples/scripts/system_validator.py
```

---

## Usage Examples

### Example 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "components": {
    "database": "connected",
    "retrieval": "ready",
    "reasoning": "active"
  }
}
```

### Example 2: Basic Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was Tesla'\''s revenue in 2023?"}'
```

### Example 3: Batch Processing

```bash
# Process 10 queries in parallel
python3 examples/scripts/batch_processor.py
```

### Example 4: Comparative Analysis

```bash
# Analyze and compare multiple companies
python3 examples/scripts/comparative_analyzer.py
```

### Example 5: Complete Workflow

```bash
# Full end-to-end analysis with all stages
python3 examples/scripts/complete_workflow.py
```

### Example 6: System Validation

```bash
# Run comprehensive test suite
python3 examples/scripts/system_validator.py
```

---

## Sample Data

### Available Documents

Three sample financial documents are included in `sample_data/`:

1. **Tesla 10-K Filing** (2,500+ chars)
   - Revenue: $81.46B (2023)
   - Key metrics and risk factors
   - See: `sample_data/sec_filing_sample.txt`

2. **Apple Q1 2024 Report** (2,000+ chars)
   - Revenue: $119.6B
   - Geographic breakdown
   - See: `sample_data/financial_report_sample.txt`

3. **Microsoft Earnings Call** (2,300+ chars)
   - Revenue: $72.8B (Q2 2024)
   - AI strategy and investments
   - See: `sample_data/earnings_call_summary.txt`

### Batch Query Set

10 pre-formatted queries for batch analysis:
- See: `sample_data/batch_queries.json`

---

## Configuration Examples

### Available Configurations

Located in `configs/configuration_examples.yaml`:

1. **Minimal** - For testing and development
2. **Production** - High-performance production setup
3. **Semantic** - Optimized for semantic search
4. **Batch** - Optimized for batch processing  
5. **Real-time** - Optimized for interactive queries
6. **Research** - High-quality analysis mode

**Usage:**
```bash
cp examples/configs/config_production.yaml config/system_config.yaml
python3 main.py
```

---

## API Request Templates

### Available Request Templates

In `api_requests/request_examples.json`:

- Simple query
- Advanced query with parameters
- Batch processing
- Comparison queries
- Risk analysis queries

**Usage:**
```bash
# Make request using template
curl -X POST http://localhost:8000/query \
  -d @examples/api_requests/simple_query.json
```

---

## Jupyter Notebook

### Getting Started Notebook

Located at: `notebooks/01_getting_started.ipynb`

**Features:**
- Step-by-step tutorial
- Interactive examples
- Data visualization
- Performance analysis

**Usage:**
```bash
jupyter notebook examples/notebooks/01_getting_started.ipynb
```

---

## Performance Benchmarks

### Expected Response Times

| Query Type | Model | Avg Time | CPU Usage |
|-----------|-------|----------|-----------|
| Simple (keyword) | Student | 200-500ms | Low |
| Standard (hybrid) | Student | 500-1000ms | Medium |
| Complex (semantic) | Student | 1000-2000ms | Medium |
| Advanced (reasoning) | Teacher | 2000-5000ms | High |
| Batch (3 queries) | Student | 2000-3000ms | High |

---

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if API is running
   curl http://localhost:8000/health
   # If not, start it
   python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
   ```

2. **Low Confidence Scores**
   ```python
   # Increase corrections and lower threshold
   "parameters": {
       "max_corrections": 5,
       "evaluation_threshold": 0.6
   }
   ```

3. **Port Already in Use**
   ```bash
   # Use different port
   python3 -m uvicorn backend.api:app --port 8001
   ```

4. **Out of Memory**
   ```bash
   # Reduce batch size
   batch:
     max_parallel_processing: 2
   ```

---

## Running Tests

### System Validation

```bash
# Comprehensive test suite
python3 examples/scripts/system_validator.py

# View results
cat examples/validation_results.json
```

### Load Testing

```bash
# Test with many concurrent queries
python3 -c "
import concurrent.futures
import requests

def query(i):
    return requests.post(
        'http://localhost:8000/query',
        json={'query': f'Test query {i}'}
    )

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(query, range(100)))
    print(f'Completed: {sum(1 for r in results if r.status_code == 200)}/100')
"
```

---

## Learning Path

### Recommended Learning Sequence

1. **Day 1: Basics**
   - Read: `README.md`
   - Run: `api_usage_guide.py`
   - Explore: Sample data files
   - Time: 1-2 hours

2. **Day 2: Core Features**
   - Run: `batch_processor.py`
   - Run: `data_loader.py`
   - Modify: `api_requests/simple_query.json`
   - Time: 2-3 hours

3. **Day 3: Advanced**
   - Run: `comparative_analyzer.py`
   - Run: `complete_workflow.py`
   - Notebook: `01_getting_started.ipynb`
   - Time: 3-4 hours

4. **Day 4: Production**
   - Run: `system_validator.py`
   - Review: Configuration examples
   - Deploy: Custom scenarios
   - Time: 2-3 hours

---

## Contributing Examples

To add new examples:

1. **Script Examples**
   - Add to `scripts/` directory
   - Follow naming convention
   - Include docstrings and comments

2. **Sample Data**
   - Add to `sample_data/`
   - Document format and structure

3. **API Requests**
   - Add to `api_requests/`
   - Include usage instructions

4. **Documentation**
   - Update this README
   - Include in learning path

---

## Support & Resources

### Documentation
- Main README: `../../README.md`
- Quick Start: `../../QUICKSTART.md`
- Config Reference: `../../config/system_config.yaml`

### Examples
- API Calls: `api_requests/api_calls.sh`
- Request Templates: `api_requests/request_examples.json`
- Batch Queries: `sample_data/batch_queries.json`

### Testing
- Validation Suite: `scripts/system_validator.py`
- Comparative Analysis: `scripts/comparative_analyzer.py`

---

## Statistics & Metrics

### Sample Data Coverage

- **Total Documents**: 3
- **Total Characters**: 6,800+
- **Companies Covered**: Tesla, Apple, Microsoft
- **Metrics Tracked**: Revenue, Margin, Growth, Risks
- **Sample Queries**: 10+

### Performance Characteristics

- **Min Response Time**: ~200ms
- **Avg Response Time**: ~1000ms
- **Max Response Time**: ~5000ms
- **Concurrent Capacity**: 8+ simultaneous queries

---

## FAQ

**Q: How do I get started?**
A: Start with `api_usage_guide.py` and follow the learning path above.

**Q: Can I use these examples in production?**
A: Yes, all examples are production-ready. Validate with `system_validator.py`.

**Q: Which configuration should I use?**
A: Start with "Production" config. Tune based on your needs.

**Q: How do I optimize performance?**
A: See Performance Optimization section in `README.md`.

**Q: Where are API documentation?**
A: See `../../README.md` and `api_requests/api_calls.sh`.

---

## Version Information

- **Examples Version**: 1.0.0
- **Last Updated**: May 25, 2026
- **Compatible Versions**: Financial Intelligence System 1.0.0+
- **Python**: 3.11+

---

**Happy analyzing! 📊📈**
