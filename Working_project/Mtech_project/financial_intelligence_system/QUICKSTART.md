# QUICK START GUIDE
## Self-Correcting Financial Intelligence System

### 🎯 5-Minute Quick Start

#### Option 1: Run with Docker Compose (Recommended)

```bash
# Navigate to project
cd financial_intelligence_system

# Set environment variables
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Access:
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Monitoring**: http://localhost:9090

---

#### Option 2: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend
streamlit run frontend/app.py

# Terminal 3 (Optional): Run demo
python main.py
```

---

### 🧪 Test the System

#### Via Frontend UI
1. Go to http://localhost:8501
2. Select "Interactive Query"
3. Enter: "What is Apple's revenue growth?"
4. Click "Analyze"

#### Via API
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Apple revenue in 2023?",
    "use_teacher_model": false,
    "temperature": 0.7
  }'
```

#### Via Python
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "Apple revenue growth",
        "use_teacher_model": False,
        "temperature": 0.7
    }
)

print(response.json())
```

---

### 🔧 Configuration

Edit `config/system_config.yaml` to customize:

```yaml
# Change model
reasoning:
  student_model:
    model_name: "your-model-7b"

# Adjust retrieval weights
retrieval:
  hybrid_retriever:
    alpha: 0.6  # More semantic
    beta: 0.4   # Less keyword

# Change confidence threshold
evaluation:
  evaluator:
    confidence_threshold: 0.80
```

---

### 📊 Example Queries

```
"What is the debt-to-equity ratio for Microsoft?"
"Analyze Apple's risk factors from 10-K filing"
"Compare revenue growth between Tesla and competitors"
"What are Google's main revenue sources?"
"Evaluate Amazon AWS growth trends"
```

---

### 🚀 Deployment to Production

```bash
# Build production image
docker build -t financial-intelligence:prod -f Dockerfile .

# Push to registry
docker tag financial-intelligence:prod myregistry/financial-intelligence:prod
docker push myregistry/financial-intelligence:prod

# Deploy with scaling
docker-compose -f docker-compose.prod.yml up -d
```

---

### 🆘 Troubleshooting

**Issue**: Backend not responding
- Check: `docker ps | grep api`
- View logs: `docker-compose logs api`

**Issue**: Out of memory
- Reduce `top_k` in config.yaml
- Disable teacher model initially

**Issue**: Slow queries
- Enable Redis caching
- Use student model (faster)

---

### 📈 Monitoring

**View Metrics**:
```bash
# Prometheus Query
curl "http://localhost:9090/api/v1/query?query=query_latency"

# Check health
curl http://localhost:8000/health
```

**View Logs**:
```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

---

### 📚 Next Steps

1. **Explore the Code**: Check `src/` modules
2. **Customize Models**: Edit in `config/system_config.yaml`
3. **Add Data Sources**: Update `src/ingestion.py`
4. **Deploy**: Use `docker-compose.prod.yml`
5. **Monitor**: Access Grafana at localhost:3000

---

### 💡 Key Concepts

**Hybrid Retrieval**: Combines semantic search (FAISS) + keyword search (BM25)

**Teacher-Student**: Large model teaches smaller model for faster inference

**Evaluator Loop**: Automatically improves answers until confident

**Multi-Agent**: Specialized agents collaborate to process queries

**Zero Data Leakage**: All processing on-premise, nothing to cloud

---

**Ready?** Go to http://localhost:8501 and start querying! 🚀
