# Safe Auto-Updater

A production-ready Safe Auto-Updater system that inventories Docker/Kubernetes assets, detects and evaluates changes with SemVer and diff gates, safely auto-updates Helm releases, and optionally updates Docker apps via Watchtower with health checks and rollback guidance.

## Features

- **Asset Inventory**: Automatic discovery of Docker containers and Kubernetes resources (Deployments, StatefulSets, DaemonSets)
- **Semantic Versioning**: Intelligent version parsing and comparison using SemVer
- **Diff Gates**: Configurable policies for update approval (auto, review, manual)
- **Safe Updates**: Multi-layer health checks and automatic rollback on failure
- **Helm Integration**: Safe Helm release updates with validation
- **Watchtower Support**: Optional integration for standalone Docker containers
- **Audit Logging**: Complete audit trail of all update operations
- **Prometheus Metrics**: Built-in metrics export for monitoring

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker access (for Docker scanning)
- Kubernetes cluster access (for K8s scanning)
- kubectl configured (optional)

### Install from source

```bash
git clone <repository-url>
cd mGF-safeAUTO-updater

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### 1. Generate Configuration

```bash
python -m src.main generate-config --output config/policy.yaml
```

### 2. Scan Assets

```bash
# Scan Docker containers
python -m src.main scan --docker --no-kubernetes

# Scan Kubernetes resources
python -m src.main scan --no-docker --kubernetes --namespace default

# Scan both
python -m src.main scan
```

### 3. List Tracked Assets

```bash
python -m src.main list-assets
```

### 4. Compare Versions

```bash
python -m src.main compare 1.0.0 1.0.1
```

### 5. Evaluate Update Decision

```bash
python -m src.main evaluate 1.0.0 2.0.0
```

## Configuration

The system is configured via YAML files. See [config/default_policy.yaml](config/default_policy.yaml) for a complete example.

### Key Configuration Options

```yaml
auto_update:
  update_policy:
    enabled: true
    max_concurrent: 3
    update_window: "02:00-06:00"
    dry_run: false

  semver_gates:
    patch: auto        # Auto-approve patch updates
    minor: review      # Review minor updates
    major: manual      # Manual approval for major
    prerelease: manual # Manual for pre-releases

  rollback:
    auto_rollback: true
    failure_threshold: 0.1
    monitoring_duration: 300
```

### SemVer Gate Policies

- `auto`: Automatically approve and apply updates
- `review`: Flag for review but don't auto-apply
- `manual`: Require explicit manual approval
- `skip`: Never update (ignore)

## Usage

### CLI Commands

```bash
# Scan and inventory assets
python -m src.main scan [OPTIONS]

# List all tracked assets
python -m src.main list-assets

# Compare two versions
python -m src.main compare <current> <new>

# Evaluate update decision
python -m src.main evaluate <current> <new>

# Display statistics
python -m src.main stats

# Validate configuration
python -m src.main validate-config --config-file config/policy.yaml

# Generate default config
python -m src.main generate-config --output my-policy.yaml
```

### Docker Deployment

```bash
# Build image
docker build -t safe-auto-updater:latest .

# Run scanner
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/config:/app/config \
  safe-auto-updater:latest scan
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: safe-auto-updater
spec:
  replicas: 1
  template:
    spec:
      serviceAccountName: safe-updater-sa
      containers:
      - name: updater
        image: safe-auto-updater:latest
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: safe-updater-config
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_semver_analyzer.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
pylint src/

# Code formatting
black src/
isort src/
```

### Security Scanning

```bash
# Check for vulnerabilities
bandit -r src/

# Check dependencies
safety check
```

## Architecture

See [docs/STARTER.md](docs/STARTER.md) for detailed architecture documentation.

### Core Components

- **Inventory Service**: Discovers and tracks Docker/K8s assets
- **Change Detection**: Monitors registries and evaluates updates
- **Update Orchestration**: Manages safe update execution
- **Rollback System**: Handles automatic rollback on failures

## Security

This is a **defensive security tool** designed to safely manage updates. It includes:

- Secure credential management via Kubernetes secrets
- Minimal RBAC permissions
- Complete audit logging
- Image signature verification support
- Network security with TLS

## License

See [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! Please ensure all tests pass and code meets quality standards.

## Support

For issues and questions, please see [docs/STARTER.md](docs/STARTER.md).