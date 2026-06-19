# Deployment and Operations Guide

Complete guide for deploying and operating the Financial Intelligence System in various environments.

---

## Table of Contents

1. [Local Development Deployment](#local-development-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Backup and Recovery](#backup-and-recovery)
7. [Performance Tuning](#performance-tuning)

---

## Local Development Deployment

### Quick Setup (5 minutes)

#### 1. Clone Repository

```bash
git clone <repository_url>
cd Mtech_project/financial_intelligence_system
```

#### 2. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 4. Configure Environment

Create `.env` in `financial_intelligence_system/`:

```env
# Required for Snowflake
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_user
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database

# Optional
LOG_LEVEL=INFO
DEBUG_MODE=false
```

#### 5. Run System

**Terminal 1 - Backend**:
```bash
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend**:
```bash
streamlit run frontend/app.py
```

**Terminal 3 - Monitor (Optional)**:
```bash
python examples/scripts/system_validator.py
```

**Access**:
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000

---

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 80GB disk space
- 32GB RAM recommended

### Quick Start (10 minutes)

#### 1. Prepare Environment

```bash
cd financial_intelligence_system

# Create .env file
cat > .env << EOF
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
EOF
```

#### 2. Build Images

```bash
# Build all images
docker-compose build

# View images
docker images | grep finiq
```

#### 3. Start Services

```bash
# Start in background
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 4. Health Check

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:8501
```

#### 5. Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Compose Structure

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT}
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Dockerfile for Backend

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile for Frontend

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## Production Deployment

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                     │
│                    (Health Checks Every 10s)                │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼──┐     ┌───▼──┐    ┌──▼────┐
    │ API  │     │ API  │    │ API   │
    │ Srv1 │     │ Srv2 │    │ Srv3  │
    └───┬──┘     └───┬──┘    └──┬────┘
        │            │          │
        └────────────┼──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼──────┐ ┌──▼────┐  ┌────▼───┐
    │Redis     │ │Config │  │Logging │
    │Cache     │ │Store  │  │(ELK)   │
    └──────────┘ └───────┘  └────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼──┐     ┌───▼──┐    ┌──▼────┐
    │ Storage    │ Models   │ Data   │
    │(S3/NFS)    │ Cache    │ Source │
    └────────────┘ └────────┘ └───────┘
```

### Hardware Requirements

| Component | Requirement |
|-----------|-------------|
| CPU | 16+ cores recommended |
| RAM | 128GB (64GB minimum) |
| GPU | 4x A100 or 2x H100 recommended |
| Storage | 500GB+ SSD for models/cache |
| Network | 1Gbps minimum |

### Kubernetes Deployment

#### Installation

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Create Namespace

```bash
kubectl create namespace finiq
kubectl config set-context --current --namespace=finiq
```

#### Deploy with Helm

```yaml
# values.yaml
replicaCount: 3

image:
  repository: youregistry/finiq-backend
  tag: "1.0.0"
  pullPolicy: IfNotPresent

backend:
  port: 8000
  replicas: 3
  resources:
    limits:
      memory: "32Gi"
      cpu: "8"
    requests:
      memory: "16Gi"
      cpu: "4"

frontend:
  port: 8501
  replicas: 1
  resources:
    limits:
      memory: "4Gi"
      cpu: "2"
    requests:
      memory: "2Gi"
      cpu: "1"

redis:
  enabled: true
  replicas: 1

ingress:
  enabled: true
  hostname: finiq.example.com
  tls: true

env:
  LOG_LEVEL: "INFO"
  SNOWFLAKE_ACCOUNT: "${SNOWFLAKE_ACCOUNT}"
```

Install:
```bash
helm install finiq ./chart -f values.yaml -n finiq
```

#### Monitoring with Prometheus

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'finiq-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

Deploy:
```bash
kubectl apply -f prometheus.yaml
```

---

## Cloud Deployment

### AWS Deployment

#### Using ECS

```bash
# Authenticate ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t finiq-backend:latest .
docker tag finiq-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/finiq-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/finiq-backend:latest

# Create ECS task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster finiq-cluster \
  --service-name finiq-backend \
  --task-definition finiq-backend:1 \
  --desired-count 3 \
  --launch-type EC2
```

#### Using SageMaker

For model hosting and inference:

```python
import sagemaker
from sagemaker.estimator import Estimator

sess = sagemaker.Session()
role = sagemaker.get_execution_role()

estimator = Estimator(
    image_uri='finiq-inference:latest',
    role=role,
    instance_count=1,
    instance_type='ml.p3.8xlarge',
    framework_version='1.0'
)

estimator.deploy(
    initial_instance_count=3,
    instance_type='ml.p3.2xlarge',
    endpoint_name='finiq-endpoint'
)
```

### Google Cloud Deployment

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/finiq-backend

# Deploy to Cloud Run
gcloud run deploy finiq-backend \
  --image gcr.io/PROJECT_ID/finiq-backend \
  --memory=32Gi \
  --cpu=8 \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars SNOWFLAKE_ACCOUNT=$SNOWFLAKE_ACCOUNT
```

#### Using Vertex AI

```python
from google.cloud import aiplatform

aiplatform.init(project='PROJECT_ID', location='us-central1')

model = aiplatform.Model.upload(
    display_name='finiq-model',
    artifact_uri='gs://bucket/model',
    serving_container_image_uri='gcr.io/PROJECT_ID/finiq-backend'
)

model.deploy(
    machine_type='n1-standard-16',
    accelerator_type='NVIDIA_TESLA_V100',
    accelerator_count=2
)
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name finiq-rg --location eastus

# Build container
az acr build \
  --registry finiqregistry \
  --image finiq-backend:latest .

# Deploy
az container create \
  --resource-group finiq-rg \
  --name finiq-backend \
  --image finiqregistry.azurecr.io/finiq-backend:latest \
  --cpu 8 \
  --memory 32 \
  --ports 8000 \
  --environment-variables SNOWFLAKE_ACCOUNT=$SNOWFLAKE_ACCOUNT
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl -s http://localhost:8000/health | jq

# Frontend health  
curl -s http://localhost:8501/_stcore/health

# Full system check
python examples/scripts/system_validator.py
```

### Logs

```bash
# View logs
docker-compose logs backend | tail -100

# Log aggregation (ELK Stack)
# Logs flow: Application → Filebeat → Elasticsearch → Kibana
```

### Metrics Collection

```python
# Prometheus metrics available at:
# http://localhost:8000/metrics

# Key metrics:
# - finiq_query_latency_seconds
# - finiq_retrieval_documents_count
# - finiq_answer_confidence
# - finiq_error_total
# - finiq_correction_iterations
```

### Alerting Rules

```yaml
groups:
  - name: finiq-alerts
    interval: 30s
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, finiq_query_latency_seconds) > 5
        for: 5m
        annotations:
          summary: "High query latency detected"

      - alert: LowConfidence
        expr: avg(finiq_answer_confidence) < 0.70
        for: 10m
        annotations:
          summary: "Low confidence scores"

      - alert: HighErrorRate
        expr: rate(finiq_error_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
```

---

## Backup and Recovery

### Data Backup

```bash
# Backup models and indices
tar -czf finiq-backup-$(date +%Y%m%d).tar.gz \
  models/ \
  data/indices/ \
  config/

# Upload to S3
aws s3 cp finiq-backup-*.tar.gz s3://finiq-backups/

# Schedule daily backups
0 2 * * * /path/to/backup.sh  # Run at 2 AM daily
```

### Database Backup (Snowflake)

```sql
-- Create backup table
CREATE TABLE documents_backup AS
SELECT * FROM documents;

-- Export to S3
COPY (SELECT * FROM documents)
TO @s3_stage
FILE_FORMAT = (TYPE = PARQUET)
;
```

### Recovery Procedure

```bash
# Restore from backup
aws s3 cp s3://finiq-backups/finiq-backup-20260601.tar.gz .
tar -xzf finiq-backup-20260601.tar.gz

# Stop services
docker-compose down

# Restore files
cp -r models/ /path/to/production/

# Start services
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

---

## Performance Tuning

### Model Optimization

```python
# 8-bit quantization
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B",
    load_in_8bit=True,
    device_map="auto"
)

# Result: 50% memory reduction, ~5% speed reduction
```

### Caching Strategy

```python
# Enable Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            
            # Compute and cache
            result = func(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(ttl=3600)
def retrieve_documents(query):
    return hybrid_retriever.retrieve(query)
```

### Batch Processing Optimization

```python
# Process in batches for better GPU utilization
def batch_process(queries: List[str], batch_size=10):
    results = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i+batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
    return results
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using load_test
pip install locust

# Create locustfile.py
from locust import HttpUser, task

class FinIQUser(HttpUser):
    @task
    def query(self):
        self.client.post("/query", json={
            "query": "What is Apple revenue?"
        })

# Run load test
locust -f locustfile.py -u 100 -r 10
```

---

## Troubleshooting

### Common Issues

#### High Memory Usage

```bash
# Check process memory
docker stats finiq-backend

# Solution: Enable 8-bit quantization
# Or reduce batch size in config
```

#### Slow Queries

```bash
# Enable query profiling
LOG_LEVEL=DEBUG python -c "..."

# Check retrieval time
curl -s http://localhost:8000/statistics | jq '.component_stats.retrieval'

# Solution: Reduce top_k or enable caching
```

#### Model Load Failures

```bash
# Check disk space
df -h

# Check GPU memory
nvidia-smi

# Solution: Clean cache, use smaller models
rm -rf ~/.cache/huggingface/
```

---

**Document Version**: 1.0  
**Last Updated**: June 2026
