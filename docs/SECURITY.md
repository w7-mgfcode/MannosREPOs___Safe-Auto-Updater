# Security Guidelines
## Safe Auto-Updater

**Version:** 1.0  
**Last Updated:** October 20, 2025  
**Security Contact:** security@example.com

---

## Table of Contents
1. [Security Overview](#1-security-overview)
2. [Threat Model](#2-threat-model)
3. [Authentication & Authorization](#3-authentication--authorization)
4. [Secret Management](#4-secret-management)
5. [Network Security](#5-network-security)
6. [Supply Chain Security](#6-supply-chain-security)
7. [Container Security](#7-container-security)
8. [Audit & Compliance](#8-audit--compliance)
9. [Security Best Practices](#9-security-best-practices)
10. [Incident Response](#10-incident-response)

---

## 1. Security Overview

### 1.1 Security Posture

Safe Auto-Updater is a **defensive security tool** designed to:
- ✅ Reduce attack surface through timely updates
- ✅ Minimize exposure to known vulnerabilities
- ✅ Prevent unauthorized changes through policy enforcement
- ✅ Maintain complete audit trails
- ✅ Enable rapid rollback on security incidents

### 1.2 Security Principles

| Principle | Implementation |
|-----------|----------------|
| **Least Privilege** | Minimal RBAC permissions, read-only where possible |
| **Defense in Depth** | Multiple layers: policy gates, health checks, rollback |
| **Fail Secure** | Block updates on policy violations or health failures |
| **Audit Everything** | Complete logging of all decisions and actions |
| **Zero Trust** | Verify all inputs, validate all configurations |

### 1.3 Compliance Alignment

- **SOC 2 Type II**: Audit logging, access controls
- **PCI-DSS**: Change management, vulnerability management
- **ISO 27001**: Security policies, risk management
- **NIST Cybersecurity Framework**: Identify, Protect, Detect, Respond, Recover

---

## 2. Threat Model

### 2.1 Threat Actors

| Actor | Motivation | Capabilities | Mitigations |
|-------|------------|--------------|-------------|
| **External Attacker** | Data theft, service disruption | Network access, exploits | Network segmentation, TLS, input validation |
| **Malicious Insider** | Sabotage, data exfiltration | Internal access, credentials | RBAC, audit logging, least privilege |
| **Supply Chain Attack** | Backdoor injection | Compromised dependencies | Signature verification, SBOM, scanning |
| **Misconfiguration** | Unintentional exposure | Admin access | Config validation, dry-run mode |

### 2.2 Attack Vectors

#### High Risk
- **Compromised Container Registry**: Malicious images
  - **Mitigation**: Image signing, vulnerability scanning, allowlist registries
  
- **Kubernetes API Abuse**: Unauthorized cluster access
  - **Mitigation**: RBAC, ServiceAccount constraints, audit logging

- **Credential Theft**: Stolen registry/cluster credentials
  - **Mitigation**: Secrets encryption, rotation, least privilege

#### Medium Risk
- **Policy Bypass**: Circumventing update gates
  - **Mitigation**: Policy validation, immutable configs, audit logs
  
- **Dependency Vulnerabilities**: Vulnerable Python packages
  - **Mitigation**: Automated scanning (safety, bandit), pinned versions

- **Container Escape**: Breaking out of containerized environment
  - **Mitigation**: Non-root user, read-only filesystem, seccomp

#### Low Risk
- **Denial of Service**: Resource exhaustion
  - **Mitigation**: Resource limits, rate limiting, timeouts

### 2.3 Data Flow Security

```
┌─────────────────────────────────────────────────────────────┐
│                    External Boundaries                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Container Registry] ─────TLS────> [Safe Updater]          │
│         (HTTPS)                         │                    │
│                                         │                    │
│  [Kubernetes API] ─────mTLS────────────┤                    │
│    (Auth Token)                         │                    │
│                                         │                    │
│  [Docker Daemon] ──Unix Socket──────────┤                    │
│   (Socket ACL)                          │                    │
│                                         ▼                    │
│                              ┌──────────────────┐           │
│                              │  State Storage   │           │
│                              │  (Encrypted)     │           │
│                              └──────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Authentication & Authorization

### 3.1 Kubernetes RBAC

#### Minimal Permissions

```yaml
# Read-Only Scanning Permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: safe-updater-readonly
rules:
  # Discover resources
  - apiGroups: ["", "apps", "batch"]
    resources:
      - pods
      - deployments
      - statefulsets
      - daemonsets
      - jobs
      - cronjobs
    verbs: ["get", "list", "watch"]
  
  # Read CRDs for compatibility checking
  - apiGroups: ["apiextensions.k8s.io"]
    resources:
      - customresourcedefinitions
    verbs: ["get", "list"]
  
  # No write permissions (updates via Helm/external tools)
```

#### Update Permissions (if implementing updates)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: safe-updater-updates
rules:
  # Update workloads
  - apiGroups: ["apps"]
    resources:
      - deployments
      - statefulsets
      - daemonsets
    verbs: ["get", "list", "watch", "update", "patch"]
  
  # Rollback capability
  - apiGroups: ["apps"]
    resources:
      - deployments/rollback
    verbs: ["create"]
  
  # Required for health checks
  - apiGroups: [""]
    resources:
      - pods
      - pods/log
    verbs: ["get", "list", "watch"]
```

### 3.2 Docker Access Control

#### Socket Permissions

```bash
# Create dedicated group
sudo groupadd docker-readonly
sudo usermod -aG docker-readonly safe-updater

# Set socket ACL (Linux)
sudo setfacl -m g:docker-readonly:r /var/run/docker.sock
```

#### TCP with TLS

```yaml
# Docker daemon.json
{
  "hosts": ["tcp://0.0.0.0:2376"],
  "tls": true,
  "tlsverify": true,
  "tlscacert": "/etc/docker/ca.pem",
  "tlscert": "/etc/docker/server-cert.pem",
  "tlskey": "/etc/docker/server-key.pem"
}
```

Client configuration:

```bash
export DOCKER_HOST=tcp://docker-host:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/client-certs
```

### 3.3 Service Account Security

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: safe-updater
  namespace: safe-updater
automountServiceAccountToken: true  # Explicitly set

---
# Token with expiration (1.22+)
apiVersion: v1
kind: Secret
metadata:
  name: safe-updater-token
  annotations:
    kubernetes.io/service-account.name: safe-updater
type: kubernetes.io/service-account-token
```

---

## 4. Secret Management

### 4.1 Secrets Hierarchy

```
┌────────────────────────────────────────────┐
│           Priority (High to Low)           │
├────────────────────────────────────────────┤
│ 1. External Secrets (Vault, AWS Secrets)  │
│ 2. Kubernetes Secrets (encrypted at rest) │
│ 3. Environment Variables (from Secrets)   │
│ 4. Config Files (mounted Secrets)         │
│ 5. NEVER: Hardcoded credentials           │
└────────────────────────────────────────────┘
```

### 4.2 Kubernetes Secrets

#### Encryption at Rest

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

Enable in API server:

```bash
--encryption-provider-config=/etc/kubernetes/encryption-config.yaml
```

#### Registry Credentials

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: safe-updater
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

Usage in pod:

```yaml
spec:
  imagePullSecrets:
  - name: registry-credentials
  
  containers:
  - name: safe-updater
    env:
    - name: REGISTRY_USERNAME
      valueFrom:
        secretKeyRef:
          name: registry-credentials
          key: username
```

### 4.3 HashiCorp Vault Integration (Future)

```python
# Example Vault integration
import hvac

client = hvac.Client(url='https://vault.example.com')
client.token = os.environ.get('VAULT_TOKEN')

# Read secret
secret = client.secrets.kv.v2.read_secret_version(
    path='safe-updater/registry-creds'
)
username = secret['data']['data']['username']
password = secret['data']['data']['password']
```

### 4.4 Secret Rotation

```bash
# Rotate Kubernetes ServiceAccount token
kubectl -n safe-updater delete secret safe-updater-token
# Token auto-regenerates

# Rotate registry credentials
kubectl -n safe-updater create secret docker-registry registry-credentials \
  --docker-server=registry.example.com \
  --docker-username=new-user \
  --docker-password=new-password \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new credentials
kubectl -n safe-updater rollout restart deployment/safe-updater
```

---

## 5. Network Security

### 5.1 Network Policies

#### Egress Control

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: safe-updater-egress
  namespace: safe-updater
spec:
  podSelector:
    matchLabels:
      app: safe-updater
  policyTypes:
  - Egress
  
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  
  # Allow Kubernetes API
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 6443
  
  # Allow HTTPS to registries
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443
  
  # Block all other egress
```

#### Ingress Control (Metrics)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: safe-updater-ingress
  namespace: safe-updater
spec:
  podSelector:
    matchLabels:
      app: safe-updater
  policyTypes:
  - Ingress
  
  ingress:
  # Allow Prometheus scraping
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 9090
```

### 5.2 TLS Configuration

#### Registry Communication

```python
import requests

# Verify TLS certificates
response = requests.get(
    'https://registry.example.com/v2/',
    verify=True,  # Always verify
    timeout=10
)

# Custom CA bundle
response = requests.get(
    'https://registry.example.com/v2/',
    verify='/etc/ssl/certs/ca-bundle.crt'
)
```

#### Kubernetes API

```python
from kubernetes import client, config

# Load config with TLS verification
config.load_kube_config()

# In-cluster config (automatic TLS)
config.load_incluster_config()
```

### 5.3 Service Mesh Integration

#### Istio Example

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: safe-updater
  namespace: safe-updater
spec:
  mtls:
    mode: STRICT  # Require mTLS

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: safe-updater
  namespace: safe-updater
spec:
  selector:
    matchLabels:
      app: safe-updater
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/monitoring/sa/prometheus"]
    to:
    - operation:
        ports: ["9090"]
```

---

## 6. Supply Chain Security

### 6.1 Dependency Scanning

#### Python Dependencies

```bash
# Check for known vulnerabilities
safety check -r requirements.txt

# Audit with pip-audit
pip-audit

# Generate SBOM
pip-licenses --format=json > sbom.json
```

#### Automated Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Safety check
        run: |
          pip install safety
          safety check -r requirements.txt
      
      - name: Bandit security lint
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: bandit-report.json
```

### 6.2 Image Signing & Verification

#### Sign Images with Cosign

```bash
# Install cosign
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Generate key pair
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key safe-auto-updater:latest

# Verify signature
cosign verify --key cosign.pub safe-auto-updater:latest
```

#### Policy Enforcement

```yaml
# Kubernetes admission controller (Kyverno example)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: enforce
  rules:
  - name: verify-signature
    match:
      resources:
        kinds:
        - Pod
    verifyImages:
    - image: "ghcr.io/mannosrepos/*"
      key: |-
        -----BEGIN PUBLIC KEY-----
        <cosign-public-key>
        -----END PUBLIC KEY-----
```

### 6.3 Vulnerability Scanning

#### Trivy Scan

```bash
# Scan Docker image
trivy image safe-auto-updater:latest

# Scan filesystem
trivy fs .

# Generate SARIF output
trivy image --format sarif -o trivy-report.sarif safe-auto-updater:latest

# Fail on HIGH/CRITICAL
trivy image --severity HIGH,CRITICAL --exit-code 1 safe-auto-updater:latest
```

#### Automated Scanning Pipeline

```yaml
# CI/CD integration
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Build image
        run: docker build -t safe-auto-updater:${{ github.sha }} .
      
      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: safe-auto-updater:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### 6.4 SBOM Generation

```bash
# Generate SBOM with Syft
syft safe-auto-updater:latest -o spdx-json > sbom.spdx.json

# Generate SBOM with pip
pip-licenses --format=json --with-urls > python-sbom.json
```

---

## 7. Container Security

### 7.1 Secure Container Build

```dockerfile
# Use official base image with known provenance
FROM python:3.11-slim@sha256:abc123...  # Pin by digest

# Create non-root user
RUN groupadd -r updater && useradd -r -g updater updater

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=updater:updater src/ /app/src/

# Switch to non-root user
USER updater

WORKDIR /app

# Read-only root filesystem
# (writable volumes mounted separately)
```

### 7.2 Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: safe-updater
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: safe-updater
    image: safe-auto-updater:latest
    
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
    
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: data
      mountPath: /app/data
  
  volumes:
  - name: tmp
    emptyDir: {}
  - name: data
    emptyDir: {}
```

### 7.3 Resource Limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
    ephemeral-storage: 1Gi
```

---

## 8. Audit & Compliance

### 8.1 Audit Logging

#### Application-Level Logging

```python
import structlog

logger = structlog.get_logger()

# Log all update decisions
logger.info(
    "update_decision",
    asset_id="my-app",
    current_version="1.0.0",
    new_version="1.1.0",
    decision="approved",
    change_type="minor",
    policy="auto_update.semver_gates.minor=review",
    operator="system",
    timestamp=datetime.utcnow().isoformat()
)
```

#### Kubernetes Audit Policy

```yaml
# /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log Safe Updater ServiceAccount actions
  - level: RequestResponse
    users:
      - "system:serviceaccount:safe-updater:safe-updater"
    omitStages:
      - RequestReceived
  
  # Log all updates to Deployments
  - level: RequestResponse
    resources:
      - group: "apps"
        resources: ["deployments"]
    verbs: ["update", "patch"]
```

### 8.2 Compliance Reports

#### Generate Audit Report

```python
# tools/generate_audit_report.py
import json
from datetime import datetime, timedelta

def generate_audit_report(days=30):
    """Generate compliance audit report"""
    
    report = {
        "period": {
            "start": (datetime.utcnow() - timedelta(days=days)).isoformat(),
            "end": datetime.utcnow().isoformat()
        },
        "summary": {
            "total_updates_attempted": 150,
            "successful_updates": 145,
            "failed_updates": 3,
            "rollbacks": 2,
            "policy_blocks": 20
        },
        "compliance": {
            "soc2": {
                "change_management": "PASS",
                "audit_logging": "PASS",
                "access_control": "PASS"
            },
            "pci_dss": {
                "vulnerability_management": "PASS",
                "change_tracking": "PASS"
            }
        },
        "findings": [
            {
                "severity": "LOW",
                "description": "3 failed updates required manual intervention"
            }
        ]
    }
    
    return report
```

### 8.3 Data Retention

```yaml
# Log retention policy
audit_logs:
  retention_days: 90
  archive_after_days: 30
  archive_location: s3://audit-logs/safe-updater/

metrics:
  retention_days: 30
  aggregation: 5m

state_backups:
  retention_count: 10
  backup_interval: 1h
```

---

## 9. Security Best Practices

### 9.1 Deployment Checklist

- [ ] Use non-root container user
- [ ] Enable read-only root filesystem
- [ ] Drop all capabilities
- [ ] Apply Pod Security Standards (Restricted)
- [ ] Configure Network Policies
- [ ] Use Secrets for credentials (no hardcoding)
- [ ] Enable encryption at rest for Secrets
- [ ] Implement RBAC least privilege
- [ ] Enable audit logging
- [ ] Configure resource limits
- [ ] Scan images for vulnerabilities
- [ ] Verify image signatures
- [ ] Use TLS for all external communication
- [ ] Rotate credentials regularly
- [ ] Monitor security metrics

### 9.2 Operational Security

```bash
# Regular security tasks

# 1. Update dependencies weekly
pip list --outdated
pip install --upgrade -r requirements.txt

# 2. Scan for vulnerabilities
safety check
trivy image safe-auto-updater:latest

# 3. Review audit logs
kubectl logs -n safe-updater deployment/safe-updater | grep -i security

# 4. Rotate ServiceAccount token
kubectl -n safe-updater delete secret safe-updater-token

# 5. Review RBAC permissions
kubectl get clusterrolebinding safe-updater -o yaml
```

### 9.3 Secure Defaults

```yaml
# Secure default configuration
auto_update:
  update_policy:
    dry_run: true  # Start with dry-run
    max_concurrent: 1  # Conservative
  
  semver_gates:
    patch: review  # Even patches need review initially
    minor: manual
    major: manual
    prerelease: skip
  
  rollback:
    auto_rollback: true
    failure_threshold: 0.05  # Strict
  
  health_checks:
    - type: kubernetes
      timeout: 10
      retries: 5
```

---

## 10. Incident Response

### 10.1 Incident Categories

| Category | Severity | Response Time | Examples |
|----------|----------|---------------|----------|
| **Security Breach** | Critical | Immediate | Compromised credentials, unauthorized access |
| **Vulnerability** | High | < 24 hours | CVE in dependency, container escape |
| **Policy Violation** | Medium | < 48 hours | Unauthorized update, RBAC bypass |
| **Misconfiguration** | Low | < 1 week | Wrong policy, excessive permissions |

### 10.2 Response Procedures

#### Compromised Credentials

```bash
# 1. Revoke credentials
kubectl -n safe-updater delete secret registry-credentials

# 2. Rotate ServiceAccount token
kubectl -n safe-updater delete secret safe-updater-token

# 3. Review audit logs
kubectl logs -n safe-updater deployment/safe-updater --since=24h | grep -i auth

# 4. Issue new credentials
kubectl -n safe-updater create secret docker-registry registry-credentials \
  --docker-server=registry.example.com \
  --docker-username=new-user \
  --docker-password=new-password

# 5. Restart pods
kubectl -n safe-updater rollout restart deployment/safe-updater
```

#### Malicious Update Detected

```bash
# 1. Immediate rollback
safe-updater rollback <asset-name>

# 2. Block further updates
kubectl -n safe-updater set env deployment/safe-updater DRY_RUN=true

# 3. Investigate
kubectl logs -n safe-updater deployment/safe-updater --since=1h > incident-logs.txt

# 4. Review decision trail
safe-updater stats --format json > decision-trail.json

# 5. Update policy to prevent recurrence
# Edit policy.yaml to block suspicious sources
```

### 10.3 Contact Information

```yaml
security_contacts:
  primary: security@example.com
  backup: devops-lead@example.com
  
  emergency_hotline: "+1-555-SECURITY"
  
  escalation_path:
    - Level 1: On-call SRE
    - Level 2: Security Team Lead
    - Level 3: CISO
```

---

## 11. Security Hardening Checklist

### 11.1 Pre-Production

- [ ] Security audit completed
- [ ] Penetration testing performed
- [ ] Vulnerability scan passed
- [ ] RBAC reviewed and minimized
- [ ] Secrets encrypted at rest
- [ ] Network policies configured
- [ ] Audit logging enabled
- [ ] Compliance requirements met

### 11.2 Production

- [ ] Image signatures verified
- [ ] TLS enabled everywhere
- [ ] Non-root user enforced
- [ ] Resource limits configured
- [ ] Monitoring dashboards created
- [ ] Incident response plan documented
- [ ] Backup and recovery tested
- [ ] Security training completed

---

**Security Notice**: This document outlines security guidelines for Safe Auto-Updater. For security vulnerabilities, please report to security@example.com. Do not open public issues for security concerns.

**Last Security Review**: 2025-10-20  
**Next Scheduled Review**: 2026-01-20

---

**Related Documents**:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment configuration
- [API.md](API.md) - API security considerations
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Security in development
