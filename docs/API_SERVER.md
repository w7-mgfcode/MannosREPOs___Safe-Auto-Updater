# REST API Server Guide

**Version:** 0.1.0  
**Last Updated:** October 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Reference](#api-reference)
4. [Authentication & Security](#authentication--security)
5. [Prometheus Metrics](#prometheus-metrics)
6. [Client Examples](#client-examples)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Safe Auto-Updater REST API provides programmatic access to all system functionality including:

- **Asset Management**: List, query, and manage tracked containers and Kubernetes resources
- **Update Operations**: Evaluate updates, trigger scans, apply updates
- **Health Monitoring**: Check system health and component status
- **Metrics Export**: Prometheus-compatible metrics endpoint
- **Configuration**: View and manage system configuration

### Key Features

✅ **RESTful Design**: Standard HTTP methods and status codes  
✅ **OpenAPI/Swagger**: Auto-generated interactive documentation  
✅ **Prometheus Integration**: Built-in metrics export  
✅ **Type Safety**: Pydantic models for request/response validation  
✅ **CORS Support**: Configurable cross-origin resource sharing  
✅ **Performance Tracking**: Automatic response time headers  

---

## Getting Started

### Installation

Install the required dependencies:

```bash
pip install 'fastapi>=0.109.0' 'uvicorn[standard]>=0.27.0'
```

### Starting the Server

#### Option 1: CLI Command

```bash
# Start with defaults (host=0.0.0.0, port=8000)
safe-updater serve

# Custom host and port
safe-updater serve --host 127.0.0.1 --port 9000

# Development mode with auto-reload
safe-updater serve --reload

# Production with multiple workers
safe-updater serve --workers 4
```

#### Option 2: Python Module

```python
from api.server import start_server

start_server(
    host="0.0.0.0",
    port=8000,
    workers=4,
    reload=False
)
```

#### Option 3: Direct Uvicorn

```bash
uvicorn api.server:create_app --host 0.0.0.0 --port 8000 --workers 4
```

### Configuration

Add API server configuration to your `policy.yaml`:

```yaml
api_server:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  cors_origins:
    - "https://dashboard.example.com"
    - "http://localhost:3000"
  api_key: null  # Optional API key authentication
  rate_limit_enabled: false
  rate_limit_requests: 100
  rate_limit_window: 60
```

### Accessing the API

Once started, the API is available at:

- **Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI Spec**: `http://localhost:8000/api/openapi.json`

---

## API Reference

### Base Endpoints

#### GET /

Get service information.

**Response:**
```json
{
  "service": "Safe Auto-Updater API",
  "version": "0.1.0",
  "status": "running",
  "docs": "/api/docs",
  "health": "/api/v1/health",
  "metrics": "/api/v1/metrics"
}
```

---

### Health & Status

#### GET /api/v1/health

Get system health status with component checks.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600.5,
  "checks": [
    {
      "check_type": "docker",
      "status": "healthy",
      "message": "Docker daemon accessible",
      "duration_ms": 15.2,
      "timestamp": "2025-10-20T12:00:00Z"
    },
    {
      "check_type": "kubernetes",
      "status": "healthy",
      "message": "Kubernetes API accessible",
      "duration_ms": 45.8,
      "timestamp": "2025-10-20T12:00:00Z"
    }
  ],
  "components": {
    "api": "healthy",
    "config": "healthy",
    "docker": "healthy",
    "kubernetes": "healthy"
  }
}
```

#### GET /api/v1/version

Get version information.

**Response:**
```json
{
  "version": "0.1.0",
  "api_version": "v1",
  "python_version": "3.11.0",
  "hostname": "safe-updater-001"
}
```

#### GET /api/v1/config

Get current configuration.

**Response:**
```json
{
  "auto_update_enabled": true,
  "max_concurrent_updates": 3,
  "semver_gates": {
    "patch": "auto",
    "minor": "review",
    "major": "manual",
    "prerelease": "manual"
  },
  "rollback_enabled": true,
  "monitoring_enabled": true,
  "docker_enabled": true,
  "kubernetes_enabled": true
}
```

---

### Asset Management

#### GET /api/v1/assets/

List all tracked assets with optional filtering and pagination.

**Query Parameters:**
- `asset_type` (optional): Filter by type (`docker`, `kubernetes`, `helm`)
- `namespace` (optional): Filter by namespace
- `status` (optional): Filter by status (`active`, `updating`, `failed`, etc.)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```bash
GET /api/v1/assets/?namespace=production&status=active&page=1&page_size=20
```

**Response:**
```json
{
  "assets": [
    {
      "id": "docker-nginx-prod-001",
      "name": "nginx-prod",
      "asset_type": "docker",
      "namespace": "production",
      "current_version": "1.21.0",
      "latest_version": "1.21.3",
      "status": "active",
      "labels": {
        "app": "nginx",
        "env": "production"
      },
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-20T12:00:00Z",
      "metadata": {
        "image": "nginx:1.21.0",
        "container_id": "abc123def456"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/v1/assets/stats

Get asset statistics.

**Response:**
```json
{
  "total_assets": 150,
  "by_type": {
    "docker_container": 50,
    "k8s_deployment": 75,
    "helm_release": 25
  },
  "by_status": {
    "active": 140,
    "updating": 5,
    "failed": 3,
    "rolled_back": 2
  },
  "by_namespace": {
    "production": 100,
    "staging": 30,
    "development": 20
  }
}
```

#### GET /api/v1/assets/{asset_id}

Get details of a specific asset.

**Response:**
```json
{
  "id": "k8s-api-prod-001",
  "name": "api-deployment",
  "asset_type": "kubernetes",
  "namespace": "production",
  "current_version": "2.5.1",
  "latest_version": "2.6.0",
  "status": "active",
  "labels": {
    "app": "api",
    "tier": "backend"
  },
  "created_at": "2025-09-15T08:00:00Z",
  "updated_at": "2025-10-20T12:00:00Z",
  "metadata": {
    "replicas": 3,
    "resource_type": "Deployment"
  }
}
```

---

### Update Operations

#### POST /api/v1/updates/evaluate

Evaluate whether an update should be applied based on semver gates.

**Request Body:**
```json
{
  "asset_id": "docker-nginx-prod-001",
  "current_version": "1.21.0",
  "new_version": "1.21.3",
  "asset_type": "docker"
}
```

**Response:**
```json
{
  "current_version": "1.21.0",
  "new_version": "1.21.3",
  "change_type": "patch",
  "decision": "approve",
  "safe": true,
  "reason": "Patch update approved by semver gate policy",
  "metadata": {
    "gate_policy": "auto",
    "requires_approval": false
  }
}
```

**Change Types:**
- `patch`: 1.0.0 → 1.0.1
- `minor`: 1.0.0 → 1.1.0
- `major`: 1.0.0 → 2.0.0
- `prerelease`: 1.0.0 → 1.0.1-rc.1
- `build`: 1.0.0+build.1 → 1.0.0+build.2

**Decisions:**
- `approve`: Auto-approved, safe to apply
- `review_required`: Requires review before applying
- `manual_approval`: Requires explicit manual approval
- `reject`: Update rejected by policy

#### POST /api/v1/updates/scan

Trigger asset discovery and scanning.

**Request Body:**
```json
{
  "docker": true,
  "kubernetes": true,
  "namespace": "production",
  "force_refresh": false
}
```

**Response:**
```json
{
  "status": "success",
  "assets_discovered": 150,
  "docker_assets": 50,
  "kubernetes_assets": 100,
  "duration_seconds": 12.5,
  "timestamp": "2025-10-20T12:00:00Z"
}
```

#### POST /api/v1/updates/apply

Apply an update to an asset.

**Request Body:**
```json
{
  "asset_id": "docker-nginx-prod-001",
  "target_version": "1.21.3",
  "force": false,
  "dry_run": false
}
```

**Response:**
```json
{
  "asset_id": "docker-nginx-prod-001",
  "status": "pending",
  "previous_version": "1.21.0",
  "new_version": "1.21.3",
  "started_at": "2025-10-20T12:00:00Z",
  "completed_at": null,
  "message": "Update queued for execution",
  "rollback_available": true
}
```

#### GET /api/v1/updates/history

Get update history.

**Query Parameters:**
- `asset_id` (optional): Filter by asset
- `limit` (optional): Maximum records (default: 50)

**Response:**
```json
[
  {
    "id": "update-001",
    "asset_id": "docker-nginx-prod-001",
    "asset_name": "nginx-prod",
    "previous_version": "1.21.0",
    "new_version": "1.21.3",
    "change_type": "patch",
    "status": "completed",
    "started_at": "2025-10-20T12:00:00Z",
    "completed_at": "2025-10-20T12:05:00Z",
    "duration_seconds": 300,
    "rolled_back": false
  }
]
```

---

### Metrics

#### GET /api/v1/metrics

Get Prometheus metrics in text format.

**Response Headers:**
```
Content-Type: text/plain; version=0.0.4; charset=utf-8
```

**Response Body:**
```prometheus
# HELP safe_updater_assets_total Total number of tracked assets
# TYPE safe_updater_assets_total gauge
safe_updater_assets_total{namespace="production",type="docker_container"} 50
safe_updater_assets_total{namespace="production",type="k8s_deployment"} 75

# HELP safe_updater_scans_total Total number of asset scans
# TYPE safe_updater_scans_total counter
safe_updater_scans_total{status="success",type="docker"} 120
safe_updater_scans_total{status="success",type="kubernetes"} 118

# HELP safe_updater_updates_evaluated_total Total updates evaluated
# TYPE safe_updater_updates_evaluated_total counter
safe_updater_updates_evaluated_total{change_type="patch",decision="approve"} 85
safe_updater_updates_evaluated_total{change_type="minor",decision="review_required"} 12
safe_updater_updates_evaluated_total{change_type="major",decision="manual_approval"} 3
```

---

## Authentication & Security

### API Key Authentication (Optional)

Enable API key authentication in configuration:

```yaml
api_server:
  api_key: "your-secure-api-key-here"
```

Include API key in requests:

```bash
curl -H "X-API-Key: your-secure-api-key-here" \
     http://localhost:8000/api/v1/assets/
```

### CORS Configuration

Configure allowed origins:

```yaml
api_server:
  cors_origins:
    - "https://dashboard.example.com"
    - "https://monitoring.example.com"
```

### Rate Limiting

Enable rate limiting to prevent abuse:

```yaml
api_server:
  rate_limit_enabled: true
  rate_limit_requests: 100  # Max requests
  rate_limit_window: 60     # Per 60 seconds
```

### TLS/HTTPS

For production, run behind a reverse proxy with TLS:

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Prometheus Metrics

### Available Metrics

#### Asset Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `safe_updater_assets_total` | Gauge | Total assets by type and namespace |
| `safe_updater_assets_by_status` | Gauge | Assets grouped by status and type |

#### Scan Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `safe_updater_scans_total` | Counter | Total scans by type and status |
| `safe_updater_scan_duration_seconds` | Histogram | Scan duration |
| `safe_updater_scan_assets_discovered_total` | Counter | Assets discovered per scan |

#### Update Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `safe_updater_updates_evaluated_total` | Counter | Updates evaluated by change type |
| `safe_updater_updates_applied_total` | Counter | Updates applied by status |
| `safe_updater_update_duration_seconds` | Histogram | Update operation duration |
| `safe_updater_version_changes_total` | Counter | Version changes by type |

#### Health Check Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `safe_updater_health_checks_total` | Counter | Health checks performed |
| `safe_updater_health_check_duration_seconds` | Summary | Health check duration |
| `safe_updater_health_check_failures_total` | Counter | Health check failures |

#### API Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `safe_updater_api_requests_total` | Counter | API requests by endpoint and status |
| `safe_updater_api_request_duration_seconds` | Histogram | API request duration |

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'safe-updater'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

Example queries:

```promql
# Asset count by type
sum(safe_updater_assets_total) by (type)

# Update success rate
rate(safe_updater_updates_applied_total{status="success"}[5m])
/ 
rate(safe_updater_updates_applied_total[5m])

# API request rate
rate(safe_updater_api_requests_total[5m])

# P95 API latency
histogram_quantile(0.95, 
  rate(safe_updater_api_request_duration_seconds_bucket[5m])
)
```

---

## Client Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# List assets
response = requests.get(f"{BASE_URL}/api/v1/assets/")
assets = response.json()
print(f"Total assets: {assets['total']}")

# Evaluate update
evaluation = requests.post(
    f"{BASE_URL}/api/v1/updates/evaluate",
    json={
        "current_version": "1.0.0",
        "new_version": "1.0.1"
    }
)
result = evaluation.json()
print(f"Decision: {result['decision']}, Safe: {result['safe']}")

# Trigger scan
scan = requests.post(
    f"{BASE_URL}/api/v1/updates/scan",
    json={
        "docker": True,
        "kubernetes": True,
        "namespace": "production"
    }
)
scan_result = scan.json()
print(f"Discovered {scan_result['assets_discovered']} assets")
```

### cURL

```bash
# Get health status
curl http://localhost:8000/api/v1/health

# List assets with filtering
curl "http://localhost:8000/api/v1/assets/?namespace=production&status=active"

# Evaluate update
curl -X POST http://localhost:8000/api/v1/updates/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.0.0",
    "new_version": "1.1.0"
  }'

# Trigger scan
curl -X POST http://localhost:8000/api/v1/updates/scan \
  -H "Content-Type: application/json" \
  -d '{
    "docker": true,
    "kubernetes": true,
    "namespace": "production"
  }'

# Get Prometheus metrics
curl http://localhost:8000/api/v1/metrics
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000';

// List assets
async function listAssets() {
  const response = await fetch(`${BASE_URL}/api/v1/assets/`);
  const data = await response.json();
  return data;
}

// Evaluate update
async function evaluateUpdate(current: string, newVersion: string) {
  const response = await fetch(`${BASE_URL}/api/v1/updates/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      current_version: current,
      new_version: newVersion
    })
  });
  return await response.json();
}

// Get metrics
async function getMetrics() {
  const response = await fetch(`${BASE_URL}/api/v1/metrics`);
  return await response.text();
}
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.server:create_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
docker build -t safe-updater-api .
docker run -p 8000:8000 safe-updater-api
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: safe-updater-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: safe-updater-api
  template:
    metadata:
      labels:
        app: safe-updater-api
    spec:
      containers:
      - name: api
        image: safe-updater:latest
        ports:
        - containerPort: 8000
        env:
        - name: SAFE_UPDATER_VERSION
          value: "0.1.0"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: safe-updater-api
spec:
  selector:
    app: safe-updater-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Troubleshooting

### Server Won't Start

**Error:** `ImportError: No module named 'fastapi'`

**Solution:**
```bash
pip install 'fastapi>=0.109.0' 'uvicorn[standard]>=0.27.0'
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
safe-updater serve --port 9000

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Slow Response Times

Check worker count and increase if needed:
```bash
safe-updater serve --workers 8
```

Monitor metrics:
```bash
curl http://localhost:8000/api/v1/metrics | grep api_request_duration
```

### CORS Issues

Update configuration to allow your frontend origin:
```yaml
api_server:
  cors_origins:
    - "https://your-frontend.com"
```

---

## See Also

- [API Reference (API.md)](API.md)
- [Deployment Guide (DEPLOYMENT.md)](DEPLOYMENT.md)
- [Architecture Documentation (ARCHITECTURE.md)](ARCHITECTURE.md)
