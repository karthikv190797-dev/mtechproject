# Quick Reference and Index Guide

Fast lookup reference for common tasks and documentation locations.

---

## 📚 Documentation Index

### Core Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **DOCUMENTATION.md** | Complete system documentation with all details | All users |
| **ARCHITECTURE_AND_DESIGN.md** | Deep dive into system architecture and design patterns | Developers, Architects |
| **API_REFERENCE.md** | Complete REST API reference with examples | API users, Integrators |
| **DEPLOYMENT_AND_OPERATIONS.md** | Deployment guides and operational procedures | DevOps, Operations |
| **EXAMPLES_AND_USAGE.md** | Code examples and integration patterns | Developers, Users |
| **QUICK_REFERENCE.md** | This file - quick lookup guide | All users |

---

## 🚀 Quick Start (5 Minutes)

### Local Development
```bash
# 1. Clone and setup
git clone <repo>
cd Mtech_project/financial_intelligence_system

# 2. Create environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your Snowflake credentials

# 5. Run
# Terminal 1:
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2:
streamlit run frontend/app.py
```

Access:
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Quick Start
```bash
# Setup
docker-compose build

# Run
docker-compose up -d

# Check
docker-compose ps
docker-compose logs -f
```

---

## 🔍 Common Tasks

### Ask Financial Questions (API)

**Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What is Apple's revenue?"}
)
print(response.json()['answer'])
```

**cURL**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Apple revenue?"}'
```

**JavaScript**:
```javascript
fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: "Apple revenue?"})
})
.then(r => r.json())
.then(d => console.log(d.answer));
```

### Process Multiple Queries

```python
response = requests.post(
    "http://localhost:8000/batch",
    json={"queries": [
        "Apple revenue",
        "Microsoft earnings",
        "Google market cap"
    ]}
)
results = response.json()['results']
```

### Check System Status

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/statistics | jq '.query_statistics'
```

### Access Web UI

1. Open http://localhost:8501
2. Select mode: **Interactive Query**, **Batch**, or **Statistics**
3. Enter question and click **Analyze**

---

## ⚙️ Configuration Quick Guide

### Key Configuration File: `config/system_config.yaml`

```yaml
# Adjust retrieval (fusion weights)
retrieval:
  hybrid_retriever:
    alpha: 0.6  # More semantic? Increase
    beta: 0.4   # More keyword? Increase

# Change confidence threshold
evaluation:
  min_confidence: 0.75  # Lower → more corrections, slower
  max_iterations: 3     # Higher → slower but more refined

# Model selection
reasoning:
  student_model:
    enabled: true
  teacher_model:
    enabled: false  # Set true for deep reasoning
```

### Environment Variables (`.env`)

```env
# Required
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Optional
LOG_LEVEL=INFO           # DEBUG for verbose logs
HUGGINGFACE_API_KEY=...  # For model downloads
```

---

## 📊 API Endpoints Cheat Sheet

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | System status |
| POST | `/query` | Single question |
| GET | `/query/{id}` | Retrieve previous |
| POST | `/batch` | Multiple questions |
| GET | `/statistics` | System stats |
| GET | `/models` | Available models |

### Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (check params) |
| 422 | Validation error (check types) |
| 500 | Server error (check logs) |
| 503 | Service unavailable |

---

## 🔧 Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| **Backend won't start** | Check port 8000 not in use: `lsof -i :8000` |
| **Frontend won't connect** | Ensure backend running: `curl http://localhost:8000/health` |
| **High GPU memory** | Enable 8-bit: `model: load_in_8bit: true` in config |
| **Slow queries** | Reduce `top_k` from 15 to 5, disable teacher model |
| **SSL errors** | Already handled, but set `HF_HUB_DISABLE_SSL_VERIFICATION=1` |
| **Low confidence** | Increase `top_k`, use teacher model, check data quality |
| **Models not loading** | Check disk space, VRAM, internet connection |

---

## 📈 Performance Optimization

### For Speed (< 1 second queries)
```yaml
retrieval:
  hybrid_retriever:
    top_k: 5  # Fewer docs
reasoning:
  student_model:
    max_tokens: 256  # Shorter answers
evaluation:
  max_iterations: 1  # No correction
```

### For Quality (More accurate answers)
```yaml
retrieval:
  hybrid_retriever:
    top_k: 30  # More docs
reasoning:
  teacher_model:
    enabled: true  # Better reasoning
evaluation:
  max_iterations: 3  # More refinement
  min_confidence: 0.85
```

### For Memory Efficiency (Smaller hardware)
```yaml
reasoning:
  teacher_model:
    load_in_8bit: true  # Quantization
  student_model:
    enabled: true
embeddings:
  batch_size: 8  # Smaller batches
```

---

## 🔐 Security Checklist

- [ ] Set strong `.env` passwords
- [ ] Use environment variables (don't hardcode secrets)
- [ ] Enable HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication (optional)
- [ ] Enable logging and monitoring
- [ ] Regular backups of indices
- [ ] API key rotation policy

---

## 📋 Component Status Commands

```bash
# Backend status
curl -s http://localhost:8000/health | jq '.components'

# Frontend status
curl -s http://localhost:8501/_stcore/health

# System metrics
curl -s http://localhost:8000/statistics | \
  jq '.query_statistics, .performance_stats'

# Model status
curl -s http://localhost:8000/models | \
  jq '.models | keys'

# Docker containers
docker-compose ps

# Container logs
docker-compose logs backend --tail=50
```

---

## 🎯 Parameter Cheat Sheet

### Query Parameters

```python
# Standard query
{
    "query": "Financial question here",
    "temperature": 0.7,        # 0=factual, 1=creative
    "top_k": 15,              # Docs to retrieve (5-50)
    "max_iterations": 3,      # Correction loops (1-5)
    "use_teacher_model": false # Better but slower
}
```

### Expected Response Times

| Configuration | Time | GPU |
|---------------|------|-----|
| Student only, top_k=5 | 1-2s | V100 |
| Student only, top_k=20 | 2-3s | V100 |
| Teacher enabled | 5-10s | A100 |
| Batch (10 queries) | 25-30s | A100 |

---

## 📚 Documentation Locations

### For Users/Investors
→ See **DOCUMENTATION.md** sections:
- [Project Overview](#project-overview)
- [Use Cases](#use-cases)
- [Key Features](#key-features)

### For Developers
→ See **ARCHITECTURE_AND_DESIGN.md**:
- System architecture
- Component design
- Data models

### For API Users
→ See **API_REFERENCE.md**:
- All endpoints
- Request/response formats
- Error handling

### For DevOps/Operations
→ See **DEPLOYMENT_AND_OPERATIONS.md**:
- Docker setup
- Cloud deployment
- Monitoring
- Backup/recovery

### For Integration/Extension
→ See **EXAMPLES_AND_USAGE.md**:
- Code examples
- Integration patterns
- Custom extensions

---

## 🧪 Testing Quick Reference

```bash
# Run all tests
pytest

# Test specific component
pytest tests/test_retrieval.py -v

# With coverage
pytest --cov=src tests/

# Load testing
locust -f locustfile.py -u 100
```

---

## 📱 Using the Web Interface

### Interactive Query Mode
1. Navigate to http://localhost:8501
2. Type your question
3. Adjust sliders if needed
4. Click "Analyze"
5. View answer, confidence, and documents

### Batch Processing Mode
1. Select "Batch Processing"
2. Paste JSON array of questions
3. Click "Process Batch"
4. Download results as JSON/CSV

### Statistics View
1. Select "System Statistics"
2. View query history
3. Monitor performance metrics
4. Check model effectiveness

---

## 🔄 Backup and Restore

```bash
# Backup indices and models
tar -czf finiq-backup.tar.gz models/ data/indices/ config/

# Upload backup
aws s3 cp finiq-backup.tar.gz s3://bucket/backups/

# Restore backup
aws s3 cp s3://bucket/backups/finiq-backup.tar.gz .
tar -xzf finiq-backup.tar.gz
docker-compose up -d
```

---

## 🌐 API Integration Examples

### Using Python Client Class
```python
from your_module import FinIQClient

client = FinIQClient("http://localhost:8000")
result = client.query("Apple revenue?")
print(result['answer'])
```

### Using REST Direct
```bash
curl -X POST http://api.example.com/query \
  -d '{"query":"Apple revenue?"}' \
  -H "Content-Type: application/json" \
  | jq '.answer'
```

### Using Batch
```python
client = FinIQClient()
results = client.batch([
    "Apple revenue",
    "Microsoft earnings",
    "Google market cap"
])
```

---

## 📊 Key Metrics to Monitor

| Metric | Target | How to Check |
|--------|--------|-------------|
| Query Latency | < 3 seconds | `/statistics` → `avg_total_time_ms` |
| Confidence | > 0.80 | `/statistics` → `avg_confidence` |
| Error Rate | < 2% | `/statistics` → `error_rate` |
| Cache Hit Rate | > 20% | `/statistics` → `cache_hit_rate` |
| Correction Rate | < 20% | `/statistics` → `correction_rate` |

---

## 🎓 Learning Path

### Beginner (Day 1)
1. Read [Project Overview](#) in DOCUMENTATION.md
2. Run quick start
3. Test via web UI
4. Run example queries

### Intermediate (Days 2-3)
1. Read Architecture in ARCHITECTURE_AND_DESIGN.md
2. Study API Reference
3. Integrate with your code
4. Review configuration options

### Advanced (Week 1)
1. Study component details
2. Custom extensions
3. Performance tuning
4. Production deployment

---

## 🤝 Getting Help

### Documentation Search
- Full documentation: See **DOCUMENTATION.md**
- Architecture details: See **ARCHITECTURE_AND_DESIGN.md**
- API reference: See **API_REFERENCE.md**
- Deployment: See **DEPLOYMENT_AND_OPERATIONS.md**

### Common Questions

**Q: How do I ask questions?**
A: POST to `/query` with `{"query": "your question"}` (See API_REFERENCE.md)

**Q: How fast are responses?**
A: Typically 2-3 seconds for student model, 5-10 for teacher (See Performance Tuning)

**Q: Can I deploy to the cloud?**
A: Yes! See AWS/GCP/Azure sections in DEPLOYMENT_AND_OPERATIONS.md

**Q: How do I extend the system?**
A: See Custom Extensions in EXAMPLES_AND_USAGE.md

**Q: What are confidence scores?**
A: 0-1 scale based on 4 dimensions: Relevance, Factuality, Numerical, Entailment (See Evaluation System)

---

## 📞 Support Resources

### System Information
```bash
# Check versions
python --version
docker --version
docker-compose --version

# Check dependencies
pip list | grep -E 'langchain|fastapi|streamlit|torch'

# System resources
nvidia-smi                    # GPU info
free -h                      # RAM info
df -h                        # Disk info
```

---

## Template: Common API Requests

### Query Template
```json
{
  "query": "QUESTION_HERE",
  "temperature": 0.7,
  "top_k": 15,
  "max_iterations": 3,
  "use_teacher_model": false
}
```

### Batch Template
```json
{
  "queries": [
    "Question 1",
    "Question 2",
    "Question 3"
  ],
  "temperature": 0.7
}
```

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Backend `/health` returns 200
- ✅ Frontend loads at http://localhost:8501
- ✅ API docs available at http://localhost:8000/docs
- ✅ Sample query returns answer in < 5 seconds
- ✅ Confidence score visible and > 0.70
- ✅ Supporting documents appear
- ✅ No errors in logs

---

**Last Updated**: June 2026  
**Version**: 1.0  
**Status**: Complete
