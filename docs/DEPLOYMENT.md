# Deployment Guide
## Safe Auto-Updater

**Version:** 1.0  
**Last Updated:** October 20, 2025

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Standalone Deployment](#2-standalone-deployment)
3. [Docker Deployment](#3-docker-deployment)
4. [Kubernetes Deployment](#4-kubernetes-deployment)
5. [Configuration](#5-configuration)
6. [Monitoring Setup](#6-monitoring-setup)
7. [High Availability](#7-high-availability)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### 1.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 1 core | 2 cores |
| Memory | 256MB | 512MB |
| Disk | 1GB | 5GB |
| Network | 10Mbps | 100Mbps |

### 1.2 Software Dependencies

```bash
# Operating System
- Linux (Ubuntu 20.04+, RHEL 8+, Alpine 3.14+)
- macOS 12+ (for development)

# Runtime
- Python 3.11+
- Docker 20.10+ (for Docker scanning)
- kubectl 1.24+ (for Kubernetes scanning)
- Helm 3.0+ (for Helm updates)

# Optional
- Prometheus (for metrics)
- Grafana (for visualization)
```

### 1.3 Access Requirements

```yaml
Docker Access:
  - Read access to Docker socket (/var/run/docker.sock)
  - Or TCP connection to Docker daemon

Kubernetes Access:
  - Valid kubeconfig with read permissions
  - Or in-cluster ServiceAccount with RBAC

Network Access:
  - Outbound HTTPS to container registries
  - Outbound access to Kubernetes API server
  - Inbound access for Prometheus metrics (port 9090)
```

---

## 2. Standalone Deployment

### 2.1 Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/MannosREPOs/Safe-Auto-Updater.git
cd Safe-Auto-Updater

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install package
pip install -e .

# 5. Verify installation
safe-updater --version
```

### 2.2 System Service (systemd)

Create service file `/etc/systemd/system/safe-updater.service`:

```ini
[Unit]
Description=Safe Auto-Updater Service
After=network.target docker.service

[Service]
Type=simple
User=safe-updater
Group=safe-updater
WorkingDirectory=/opt/safe-auto-updater
Environment="PATH=/opt/safe-auto-updater/venv/bin"
ExecStart=/opt/safe-auto-updater/venv/bin/python -m src.main scan
Restart=on-failure
RestartSec=30

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/safe-updater

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
# Create user
sudo useradd -r -s /bin/false safe-updater
sudo usermod -aG docker safe-updater

# Create directories
sudo mkdir -p /opt/safe-auto-updater
sudo mkdir -p /var/lib/safe-updater
sudo chown -R safe-updater:safe-updater /opt/safe-auto-updater /var/lib/safe-updater

# Copy application
sudo cp -r . /opt/safe-auto-updater/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable safe-updater
sudo systemctl start safe-updater

# Check status
sudo systemctl status safe-updater
```

### 2.3 Cron-Based Scanning

```cron
# /etc/cron.d/safe-updater

# Scan every 30 minutes
*/30 * * * * safe-updater /opt/safe-auto-updater/venv/bin/safe-updater scan 2>&1 | logger -t safe-updater

# Daily statistics at 9 AM
0 9 * * * safe-updater /opt/safe-auto-updater/venv/bin/safe-updater stats 2>&1 | logger -t safe-updater
```

---

## 3. Docker Deployment

### 3.1 Build Docker Image

#### Dockerfile

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -r -u 1000 -m updater

# Copy dependencies from builder
COPY --from=builder /root/.local /home/updater/.local

# Copy application
COPY --chown=updater:updater src/ /app/src/
COPY --chown=updater:updater config/ /app/config/

WORKDIR /app
USER updater

# Add local bin to PATH
ENV PATH=/home/updater/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src.main" || exit 1

# Default command
CMD ["python", "-m", "src.main", "scan"]
```

#### Build and Run

```bash
# Build image
docker build -t safe-auto-updater:latest .

# Run with Docker socket
docker run -d \
    --name safe-updater \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd)/config:/app/config \
    safe-auto-updater:latest

# Run with kubeconfig
docker run -d \
    --name safe-updater \
    -v ~/.kube/config:/home/updater/.kube/config:ro \
    -v $(pwd)/config:/app/config \
    safe-auto-updater:latest

# Check logs
docker logs -f safe-updater
```

### 3.2 Docker Compose

#### docker-compose.yml

```yaml
version: '3.8'

services:
  safe-updater:
    build: .
    container_name: safe-auto-updater
    restart: unless-stopped
    
    # Docker scanning
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./config:/app/config:ro
      - ./data:/app/data
    
    environment:
      - SAFE_UPDATER_LOG_LEVEL=INFO
      - DOCKER_HOST=unix:///var/run/docker.sock
    
    # Prometheus metrics
    ports:
      - "9090:9090"
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import src.main"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 256M
```

#### Run with Compose

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## 4. Kubernetes Deployment

### 4.1 RBAC Setup

#### serviceaccount.yaml

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: safe-updater
  namespace: safe-updater
```

#### clusterrole.yaml

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: safe-updater
rules:
  # Read pods, services, configmaps
  - apiGroups: [""]
    resources:
      - pods
      - services
      - configmaps
      - namespaces
    verbs: ["get", "list", "watch"]
  
  # Read deployments, statefulsets, daemonsets
  - apiGroups: ["apps"]
    resources:
      - deployments
      - statefulsets
      - daemonsets
      - replicasets
    verbs: ["get", "list", "watch"]
  
  # Read jobs and cronjobs
  - apiGroups: ["batch"]
    resources:
      - jobs
      - cronjobs
    verbs: ["get", "list", "watch"]
  
  # Read CRDs
  - apiGroups: ["apiextensions.k8s.io"]
    resources:
      - customresourcedefinitions
    verbs: ["get", "list", "watch"]
```

#### clusterrolebinding.yaml

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: safe-updater
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: safe-updater
subjects:
  - kind: ServiceAccount
    name: safe-updater
    namespace: safe-updater
```

### 4.2 ConfigMap

#### configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: safe-updater-config
  namespace: safe-updater
data:
  policy.yaml: |
    auto_update:
      update_policy:
        enabled: true
        max_concurrent: 3
        update_window: "02:00-06:00"
        dry_run: false
      
      semver_gates:
        patch: auto
        minor: review
        major: manual
        prerelease: manual
      
      health_checks:
        - type: kubernetes
      
      rollback:
        auto_rollback: true
        failure_threshold: 0.1
        monitoring_duration: 300
    
    kubernetes:
      in_cluster: true
      namespace: default
    
    monitoring:
      prometheus_enabled: true
      prometheus_port: 9090
      log_level: INFO
```

### 4.3 Deployment

#### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: safe-updater
  namespace: safe-updater
  labels:
    app: safe-updater
spec:
  replicas: 1
  selector:
    matchLabels:
      app: safe-updater
  template:
    metadata:
      labels:
        app: safe-updater
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: safe-updater
      
      containers:
      - name: safe-updater
        image: safe-auto-updater:latest
        imagePullPolicy: IfNotPresent
        
        args:
          - "scan"
          - "--kubernetes"
          - "--no-docker"
          - "--all-namespaces"
        
        env:
        - name: SAFE_UPDATER_CONFIG
          value: /config/policy.yaml
        - name: SAFE_UPDATER_LOG_LEVEL
          value: INFO
        
        volumeMounts:
        - name: config
          mountPath: /config
          readOnly: true
        - name: data
          mountPath: /app/data
        
        ports:
        - name: metrics
          containerPort: 9090
          protocol: TCP
        
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        
        livenessProbe:
          exec:
            command:
              - python
              - -c
              - "import src.main"
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /metrics
            port: 9090
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
      
      volumes:
      - name: config
        configMap:
          name: safe-updater-config
      - name: data
        emptyDir: {}
      
      securityContext:
        fsGroup: 1000
```

### 4.4 Service (for Prometheus)

#### service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: safe-updater
  namespace: safe-updater
  labels:
    app: safe-updater
spec:
  type: ClusterIP
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
    protocol: TCP
  selector:
    app: safe-updater
```

### 4.5 CronJob (Scheduled Scans)

#### cronjob.yaml

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: safe-updater-scan
  namespace: safe-updater
spec:
  schedule: "*/30 * * * *"  # Every 30 minutes
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: safe-updater
          restartPolicy: OnFailure
          
          containers:
          - name: safe-updater
            image: safe-auto-updater:latest
            imagePullPolicy: IfNotPresent
            
            args:
              - "scan"
              - "--kubernetes"
              - "--no-docker"
              - "--all-namespaces"
            
            env:
            - name: SAFE_UPDATER_CONFIG
              value: /config/policy.yaml
            
            volumeMounts:
            - name: config
              mountPath: /config
              readOnly: true
            
            resources:
              requests:
                cpu: 100m
                memory: 256Mi
              limits:
                cpu: 200m
                memory: 512Mi
          
          volumes:
          - name: config
            configMap:
              name: safe-updater-config
```

### 4.6 Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace safe-updater

# Apply RBAC
kubectl apply -f serviceaccount.yaml
kubectl apply -f clusterrole.yaml
kubectl apply -f clusterrolebinding.yaml

# Apply ConfigMap
kubectl apply -f configmap.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f cronjob.yaml

# Verify deployment
kubectl -n safe-updater get all
kubectl -n safe-updater logs deployment/safe-updater -f
```

---

## 5. Configuration

### 5.1 Environment-Specific Configs

#### Development

```yaml
# config/dev-policy.yaml
auto_update:
  update_policy:
    enabled: true
    max_concurrent: 10
    update_window: null  # Anytime
    dry_run: false
  
  semver_gates:
    patch: auto
    minor: auto  # Aggressive in dev
    major: review
    prerelease: auto

monitoring:
  log_level: DEBUG
```

#### Production

```yaml
# config/prod-policy.yaml
auto_update:
  update_policy:
    enabled: true
    max_concurrent: 3
    update_window: "02:00-06:00"  # Night window
    dry_run: false
  
  semver_gates:
    patch: auto
    minor: manual  # Conservative
    major: manual
    prerelease: skip  # Never in prod

  rollback:
    auto_rollback: true
    failure_threshold: 0.05  # Strict
    monitoring_duration: 600  # 10 min

monitoring:
  log_level: INFO
```

### 5.2 Registry Credentials

#### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: safe-updater
type: Opaque
stringData:
  REGISTRY_USERNAME: myuser
  REGISTRY_PASSWORD: mypassword
  REGISTRY_URL: https://registry.example.com
```

Mount in Deployment:

```yaml
env:
- name: REGISTRY_USERNAME
  valueFrom:
    secretKeyRef:
      name: registry-credentials
      key: REGISTRY_USERNAME
- name: REGISTRY_PASSWORD
  valueFrom:
    secretKeyRef:
      name: registry-credentials
      key: REGISTRY_PASSWORD
```

---

## 6. Monitoring Setup

### 6.1 Prometheus Integration

#### ServiceMonitor (Prometheus Operator)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: safe-updater
  namespace: safe-updater
  labels:
    app: safe-updater
spec:
  selector:
    matchLabels:
      app: safe-updater
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 6.2 Grafana Dashboard

Import dashboard JSON (example metrics):

```json
{
  "dashboard": {
    "title": "Safe Auto-Updater",
    "panels": [
      {
        "title": "Total Assets Tracked",
        "targets": [{
          "expr": "safe_updater_assets_tracked"
        }]
      },
      {
        "title": "Update Success Rate",
        "targets": [{
          "expr": "rate(safe_updater_updates_succeeded_total[5m]) / rate(safe_updater_updates_attempted_total[5m])"
        }]
      },
      {
        "title": "Rollback Events",
        "targets": [{
          "expr": "increase(safe_updater_rollbacks_total[1h])"
        }]
      }
    ]
  }
}
```

---

## 7. High Availability

### 7.1 Active-Passive Setup

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: safe-updater
spec:
  replicas: 2  # Multiple replicas
  strategy:
    type: Recreate  # Only one active at a time
  
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: safe-updater
            topologyKey: kubernetes.io/hostname
```

### 7.2 Leader Election (Future)

Using Kubernetes leader election:

```python
# Example leader election code (future feature)
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def acquire_leadership():
    # Leader election logic
    pass
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Pod CrashLoopBackOff

```bash
# Check logs
kubectl -n safe-updater logs deployment/safe-updater

# Check events
kubectl -n safe-updater get events --sort-by='.lastTimestamp'

# Describe pod
kubectl -n safe-updater describe pod <pod-name>
```

#### RBAC Permission Denied

```bash
# Verify ServiceAccount
kubectl -n safe-updater get sa safe-updater

# Check RoleBinding
kubectl get clusterrolebinding safe-updater -o yaml

# Test permissions
kubectl auth can-i list pods --as=system:serviceaccount:safe-updater:safe-updater
```

#### Metrics Not Scraped

```bash
# Test metrics endpoint
kubectl -n safe-updater port-forward deployment/safe-updater 9090:9090
curl http://localhost:9090/metrics

# Check ServiceMonitor
kubectl -n safe-updater get servicemonitor
```

### 8.2 Debugging

```bash
# Enable debug logging
kubectl -n safe-updater set env deployment/safe-updater SAFE_UPDATER_LOG_LEVEL=DEBUG

# Execute commands in pod
kubectl -n safe-updater exec -it deployment/safe-updater -- /bin/bash
safe-updater scan -v
```

---

**Next Steps**:
- Review [SECURITY.md](SECURITY.md) for hardening
- Setup monitoring dashboards
- Configure backup and disaster recovery
- Test rollback procedures

**Last Updated**: 2025-10-20
