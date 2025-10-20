# API & CLI Reference
## Safe Auto-Updater Command-Line Interface

**Version:** 1.0  
**Last Updated:** October 20, 2025

---

## Table of Contents
1. [CLI Overview](#1-cli-overview)
2. [Global Options](#2-global-options)
3. [Commands Reference](#3-commands-reference)
4. [Configuration API](#4-configuration-api)
5. [Python API](#5-python-api)
6. [Exit Codes](#6-exit-codes)
7. [Environment Variables](#7-environment-variables)
8. [Examples](#8-examples)

---

## 1. CLI Overview

### 1.1 Installation

```bash
# From source
git clone https://github.com/MannosREPOs/Safe-Auto-Updater.git
cd Safe-Auto-Updater
pip install -e .

# Verify installation
safe-updater --version
```

### 1.2 Basic Usage

```bash
safe-updater [OPTIONS] COMMAND [ARGS]...
```

### 1.3 Getting Help

```bash
# General help
safe-updater --help

# Command-specific help
safe-updater scan --help
safe-updater compare --help
```

---

## 2. Global Options

### 2.1 Configuration File

```bash
--config, -c PATH
```

**Description**: Path to YAML configuration file  
**Default**: `config/default_policy.yaml`  
**Example**:
```bash
safe-updater --config /path/to/policy.yaml scan
```

### 2.2 Verbosity

```bash
--verbose, -v
```

**Description**: Enable verbose output  
**Default**: `False`  
**Example**:
```bash
safe-updater -v scan
```

### 2.3 Quiet Mode

```bash
--quiet, -q
```

**Description**: Suppress non-error output  
**Default**: `False`  
**Example**:
```bash
safe-updater -q scan
```

### 2.4 Help

```bash
--help
```

**Description**: Show help message and exit  
**Example**:
```bash
safe-updater --help
```

---

## 3. Commands Reference

### 3.1 scan

**Purpose**: Scan and inventory Docker and Kubernetes assets

#### Syntax
```bash
safe-updater scan [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--docker/--no-docker` | - | flag | `True` | Scan Docker containers |
| `--kubernetes/--no-kubernetes` | - | flag | `True` | Scan Kubernetes resources |
| `--namespace` | `-n` | text | `default` | Kubernetes namespace to scan |
| `--all-namespaces` | - | flag | `False` | Scan all namespaces |
| `--output` | `-o` | path | - | Save inventory to file |

#### Examples

```bash
# Scan both Docker and Kubernetes
safe-updater scan

# Scan only Docker
safe-updater scan --no-kubernetes

# Scan only Kubernetes in specific namespace
safe-updater scan --no-docker -n production

# Scan all namespaces
safe-updater scan --no-docker --all-namespaces

# Save inventory to file
safe-updater scan -o inventory.json
```

#### Output

```
[INFO] Starting asset inventory scan...
[YELLOW] Scanning Docker containers...
[GREEN] Found 15 Docker containers
[YELLOW] Scanning Kubernetes resources in namespace: default...
[GREEN] Found 23 Kubernetes resources

┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Type        ┃ Count ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ deployment  │ 12    │
│ statefulset │ 3     │
│ daemonset   │ 2     │
│ container   │ 15    │
└─────────────┴───────┘

[GREEN] Total assets discovered: 38
```

---

### 3.2 list-assets

**Purpose**: List all tracked assets from inventory

#### Syntax
```bash
safe-updater list-assets [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--type` | `-t` | text | - | Filter by asset type |
| `--namespace` | `-n` | text | - | Filter by namespace |
| `--format` | `-f` | choice | `table` | Output format: table, json, yaml |

#### Examples

```bash
# List all assets
safe-updater list-assets

# List only deployments
safe-updater list-assets -t deployment

# List assets in production namespace
safe-updater list-assets -n production

# Output as JSON
safe-updater list-assets -f json
```

#### Output (table format)

```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ Name          ┃ Type       ┃ Namespace  ┃ Version ┃ Status   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ nginx-app     │ deployment │ default    │ 1.21.0  │ healthy  │
│ postgres-db   │ statefulset│ database   │ 14.5    │ healthy  │
│ redis-cache   │ deployment │ cache      │ 7.0.5   │ healthy  │
└───────────────┴────────────┴────────────┴─────────┴──────────┘
```

---

### 3.3 compare

**Purpose**: Compare two version strings

#### Syntax
```bash
safe-updater compare <current_version> <new_version>
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `current_version` | Yes | Current version string |
| `new_version` | Yes | New version string |

#### Examples

```bash
# Compare versions
safe-updater compare 1.0.0 1.0.1

# Compare with different formats
safe-updater compare v1.2.3 1.2.4

# Compare Docker-style versions
safe-updater compare 1.21 1.22
```

#### Output

```
Comparing versions:
  Current: 1.0.0
  New:     1.0.1

✓ New version is an upgrade
  Change type: patch

Version Details:

Current: {'valid': True, 'major': 1, 'minor': 0, 'patch': 0}
New:     {'valid': True, 'major': 1, 'minor': 0, 'patch': 1}
```

---

### 3.4 evaluate

**Purpose**: Evaluate if an update should be approved based on policy

#### Syntax
```bash
safe-updater evaluate <current_version> <new_version> [OPTIONS]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `current_version` | Yes | Current version string |
| `new_version` | Yes | New version string |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--policy` | `-p` | path | - | Override default policy |
| `--asset-type` | `-t` | text | - | Asset type for policy lookup |
| `--namespace` | `-n` | text | - | Namespace for policy overrides |

#### Examples

```bash
# Evaluate patch update
safe-updater evaluate 1.0.0 1.0.1

# Evaluate major update
safe-updater evaluate 1.0.0 2.0.0

# With custom policy
safe-updater evaluate 1.0.0 1.1.0 --policy custom-policy.yaml

# For specific asset type
safe-updater evaluate 1.0.0 1.1.0 -t deployment -n production
```

#### Output

```
Update Evaluation:
  Current: 1.0.0
  New:     1.1.0
  Change:  minor
  Decision: ⚠ REVIEW REQUIRED
  Reason:   Minor updates require manual review per policy
  Safe:     False
```

---

### 3.5 stats

**Purpose**: Display statistics about tracked assets

#### Syntax
```bash
safe-updater stats [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--namespace` | `-n` | text | - | Filter by namespace |
| `--format` | `-f` | choice | `text` | Output format: text, json |

#### Examples

```bash
# Show all statistics
safe-updater stats

# Statistics for specific namespace
safe-updater stats -n production

# JSON output
safe-updater stats -f json
```

#### Output

```
Asset Statistics:
  Total assets: 45

By Type:
  deployment: 20
  statefulset: 8
  daemonset: 3
  container: 14

By Status:
  healthy: 42
  updating: 2
  failed: 1
```

---

### 3.6 generate-config

**Purpose**: Generate a default configuration file

#### Syntax
```bash
safe-updater generate-config [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | path | `config/policy.yaml` | Output file path |
| `--template` | `-t` | choice | `default` | Template: default, production, development |

#### Examples

```bash
# Generate default config
safe-updater generate-config

# Custom output path
safe-updater generate-config -o /etc/safe-updater/policy.yaml

# Production template
safe-updater generate-config -t production -o prod-policy.yaml
```

#### Output

```
✓ Configuration file generated: config/policy.yaml
```

---

### 3.7 validate-config

**Purpose**: Validate configuration file syntax and semantics

#### Syntax
```bash
safe-updater validate-config [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config-file` | `-c` | path | - | Configuration file to validate |
| `--strict` | - | flag | `False` | Enable strict validation |

#### Examples

```bash
# Validate specific file
safe-updater validate-config -c config/policy.yaml

# Strict validation
safe-updater validate-config -c policy.yaml --strict
```

#### Output (valid)

```
✓ Configuration is valid

Loaded configuration:
  Auto-update enabled: True
  Max concurrent updates: 3
  Patch updates: auto
  Minor updates: review
  Major updates: manual
```

#### Output (invalid)

```
✗ Configuration validation failed: 
  - auto_update.update_policy.max_concurrent: must be >= 1
  - auto_update.semver_gates.patch: 'autoapprove' is not a valid UpdateAction
```

---

### 3.8 update

**Purpose**: Trigger update for specific assets (future feature)

#### Syntax
```bash
safe-updater update <asset_name> [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--to-version` | - | text | - | Target version |
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |
| `--dry-run` | - | flag | `False` | Simulate update without applying |
| `--force` | - | flag | `False` | Skip policy gates |

#### Examples

```bash
# Update to specific version
safe-updater update my-app --to-version 1.2.3

# Dry run
safe-updater update my-app --to-version 1.2.3 --dry-run

# Force update (skip gates)
safe-updater update my-app --to-version 2.0.0 --force
```

---

### 3.8 serve

**Purpose**: Start the REST API server

#### Syntax
```bash
safe-updater serve [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--host` | - | text | `0.0.0.0` | Host to bind to |
| `--port` | - | integer | `8000` | Port to bind to |
| `--workers` | - | integer | `1` | Number of worker processes |
| `--reload` | - | flag | `False` | Enable auto-reload (development) |

#### Examples

```bash
# Start with defaults
safe-updater serve

# Custom host and port
safe-updater serve --host 127.0.0.1 --port 9000

# Development mode with auto-reload
safe-updater serve --reload

# Production with multiple workers
safe-updater serve --workers 4
```

#### Output

```
============================================================
Safe Auto-Updater API Server
============================================================
Host:     0.0.0.0:8000
Docs:     http://0.0.0.0:8000/api/docs
Health:   http://0.0.0.0:8000/api/v1/health
Metrics:  http://0.0.0.0:8000/api/v1/metrics
Workers:  4
Reload:   False
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### API Endpoints

Once started, the API provides:
- **Interactive Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/api/v1/metrics
- **Assets API**: http://localhost:8000/api/v1/assets/
- **Updates API**: http://localhost:8000/api/v1/updates/

See [API_SERVER.md](API_SERVER.md) for complete API documentation.

---

### 3.9 rollback

**Purpose**: Rollback a failed update (future feature)

#### Syntax
```bash
safe-updater rollback <asset_name> [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--to-version` | - | text | - | Rollback to specific version |
| `--namespace` | `-n` | text | `default` | Kubernetes namespace |

#### Examples

```bash
# Rollback to previous version
safe-updater rollback my-app

# Rollback to specific version
safe-updater rollback my-app --to-version 1.0.0 -n production
```

---

## 4. Configuration API

### 4.1 Configuration File Format

```yaml
# config/policy.yaml
auto_update:
  update_policy:
    enabled: true
    max_concurrent: 3
    update_window: "02:00-06:00"
    dry_run: false

  semver_gates:
    patch: auto        # auto, review, manual, skip
    minor: review
    major: manual
    prerelease: manual

  health_checks:
    - type: http
      http:
        endpoint: /health
        timeout: 30
        retries: 3
        expected_status: 200

  rollback:
    auto_rollback: true
    failure_threshold: 0.1
    monitoring_duration: 300
    max_rollback_attempts: 3

docker:
  socket_path: /var/run/docker.sock
  watchtower_enabled: false

kubernetes:
  kubeconfig_path: null
  namespace: default
  in_cluster: false

monitoring:
  prometheus_enabled: true
  prometheus_port: 9090
  log_level: INFO
```

### 4.2 Configuration Schema

#### UpdateAction Enum
- `auto`: Automatically approve and apply
- `review`: Flag for review but don't auto-apply
- `manual`: Require explicit manual approval
- `skip`: Never update (ignore)

#### HealthCheckType Enum
- `http`: HTTP/HTTPS endpoint check
- `tcp`: TCP port connectivity
- `exec`: Execute command in container
- `kubernetes`: Use K8s readiness/liveness probes

---

## 5. Python API

### 5.1 Programmatic Usage

```python
from src.config.policy_loader import load_config
from src.inventory.state_manager import StateManager
from src.inventory.docker_scanner import DockerScanner
from src.detection.semver_analyzer import SemVerAnalyzer
from src.detection.diff_gate import DiffGate

# Load configuration
config = load_config('config/policy.yaml')

# Initialize state manager
state_manager = StateManager()

# Scan Docker containers
docker_scanner = DockerScanner(
    socket_path=config.docker.socket_path,
    state_manager=state_manager
)
assets = docker_scanner.scan_containers()

# Analyze version changes
analyzer = SemVerAnalyzer()
comparison, change_type = analyzer.compare_versions('1.0.0', '1.1.0')

# Evaluate update decision
diff_gate = DiffGate(semver_gates=config.auto_update.semver_gates)
decision = diff_gate.evaluate_update('1.0.0', '1.1.0')
print(decision)  # {'decision': 'review_required', 'safe': False, ...}
```

### 5.2 Core Classes

#### SemVerAnalyzer

```python
class SemVerAnalyzer:
    def parse_version(self, version_string: str) -> Optional[semver.Version]:
        """Parse version string to semver.Version"""
        
    def compare_versions(self, current: str, new: str) -> Tuple[int, VersionChangeType]:
        """Compare two versions, return (comparison, change_type)"""
        
    def is_upgrade(self, current: str, new: str) -> bool:
        """Check if new version is an upgrade"""
        
    def is_breaking_change(self, current: str, new: str) -> bool:
        """Check if version change is breaking (major bump)"""
```

#### DiffGate

```python
class DiffGate:
    def __init__(self, semver_gates: SemVerGates):
        """Initialize with SemVer gate policies"""
        
    def evaluate_update(self, current: str, new: str) -> dict:
        """Evaluate update decision based on policy"""
        # Returns: {
        #   'decision': 'approve' | 'review_required' | 'manual_approval' | 'reject',
        #   'change_type': 'major' | 'minor' | 'patch' | ...,
        #   'safe': bool,
        #   'reason': str
        # }
```

#### StateManager

```python
class StateManager:
    def add_asset(self, asset: Asset) -> None:
        """Add asset to inventory"""
        
    def update_asset(self, asset_id: str, **updates) -> None:
        """Update asset attributes"""
        
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Retrieve asset by ID"""
        
    def list_assets(self, **filters) -> List[Asset]:
        """List assets with optional filters"""
        
    def get_statistics(self) -> dict:
        """Get inventory statistics"""
```

---

## 6. Exit Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | SUCCESS | Command completed successfully |
| 1 | GENERAL_ERROR | General error occurred |
| 2 | CONFIG_ERROR | Configuration validation failed |
| 3 | SCAN_ERROR | Asset scanning failed |
| 4 | UPDATE_ERROR | Update operation failed |
| 5 | ROLLBACK_ERROR | Rollback operation failed |
| 10 | POLICY_VIOLATION | Update blocked by policy |
| 20 | HEALTH_CHECK_FAILED | Health check failed |

### Usage in Scripts

```bash
#!/bin/bash

safe-updater scan
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Scan successful"
elif [ $exit_code -eq 3 ]; then
    echo "Scan failed"
    exit 1
fi
```

---

## 7. Environment Variables

### 7.1 Configuration Overrides

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SAFE_UPDATER_CONFIG` | Config file path | `config/default_policy.yaml` | `/etc/safe-updater/policy.yaml` |
| `SAFE_UPDATER_LOG_LEVEL` | Log level | `INFO` | `DEBUG` |
| `SAFE_UPDATER_DRY_RUN` | Enable dry-run mode | `false` | `true` |

### 7.2 Docker Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DOCKER_HOST` | Docker daemon host | `unix:///var/run/docker.sock` | `tcp://docker-host:2376` |
| `DOCKER_TLS_VERIFY` | Enable TLS verification | `0` | `1` |
| `DOCKER_CERT_PATH` | TLS certificate path | - | `/certs` |

### 7.3 Kubernetes Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `KUBECONFIG` | Kubeconfig file path | `~/.kube/config` | `/etc/kube/config` |
| `KUBERNETES_SERVICE_HOST` | K8s API server host (in-cluster) | - | `kubernetes.default.svc` |
| `KUBERNETES_SERVICE_PORT` | K8s API server port (in-cluster) | - | `443` |

### 7.4 Registry Credentials

| Variable | Description | Example |
|----------|-------------|---------|
| `REGISTRY_USERNAME` | Registry username | `myuser` |
| `REGISTRY_PASSWORD` | Registry password | `mypassword` |
| `REGISTRY_URL` | Registry URL | `https://registry.example.com` |

---

## 8. Examples

### 8.1 Daily Operations

#### Morning Health Check
```bash
#!/bin/bash
# Check system health

safe-updater stats
safe-updater list-assets --format table
```

#### Scan for Updates
```bash
#!/bin/bash
# Scan for new versions

safe-updater scan --all-namespaces
safe-updater list-assets | grep -v "up-to-date"
```

### 8.2 Integration Examples

#### Cron Job
```cron
# Scan every 30 minutes
*/30 * * * * /usr/local/bin/safe-updater scan >/dev/null 2>&1
```

#### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: safe-updater-scan
spec:
  schedule: "*/30 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: safe-updater
            image: safe-auto-updater:latest
            args: ["scan", "--kubernetes", "--all-namespaces"]
          restartPolicy: OnFailure
```

### 8.3 CI/CD Integration

#### GitHub Actions
```yaml
name: Safe Update Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Safe Updater
        run: pip install -e .
      
      - name: Scan for updates
        run: safe-updater scan --output updates.json
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: update-scan
          path: updates.json
```

### 8.4 Advanced Usage

#### Custom Policy per Environment
```bash
# Development: aggressive updates
safe-updater --config dev-policy.yaml scan

# Production: conservative updates
safe-updater --config prod-policy.yaml scan
```

#### Namespace-Specific Scans
```bash
# Scan only production namespaces
for ns in prod-app prod-db prod-cache; do
    safe-updater scan --no-docker -n $ns
done
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Permission Denied (Docker)
```
Error: Permission denied connecting to Docker socket
```

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Or run with sudo (not recommended)
sudo safe-updater scan --no-kubernetes
```

#### Kubernetes Connection Failed
```
Error: Failed to connect to Kubernetes cluster
```

**Solution**:
```bash
# Verify kubeconfig
kubectl cluster-info

# Set kubeconfig explicitly
export KUBECONFIG=/path/to/kubeconfig
safe-updater scan --no-docker
```

#### Invalid Configuration
```
✗ Configuration validation failed
```

**Solution**:
```bash
# Validate config first
safe-updater validate-config -c config/policy.yaml

# Generate new default config
safe-updater generate-config -o new-policy.yaml
```

---

## 10. API Changelog

### v1.0.0 (Current)
- Initial CLI release
- Basic scan, compare, evaluate commands
- Configuration validation

### v1.1.0 (Planned)
- `update` command implementation
- `rollback` command implementation
- Webhook notifications
- Watch mode for continuous scanning

---

**Document Maintenance**:
- Update on every minor version release
- Review API deprecations quarterly
- Maintain backward compatibility policy

**Next Review**: 2026-01-20
