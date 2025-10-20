# Safe Auto-Updater

[![CI Pipeline](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/actions/workflows/ci.yml/badge.svg)](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeRabbit](https://img.shields.io/badge/AI%20Review-CodeRabbit-blue)](https://coderabbit.ai)

A production-ready Safe Auto-Updater system that inventories Docker/Kubernetes assets, detects and evaluates changes with SemVer and diff gates, safely auto-updates Helm releases, and optionally updates Docker apps via Watchtower with health checks and rollback guidance.

**⚡ Features AI-powered code reviews with CodeRabbit and comprehensive CI/CD automation!**

## Features

- **Asset Inventory**: Automatic discovery of Docker containers and Kubernetes resources (Deployments, StatefulSets, DaemonSets)
- **Semantic Versioning**: Intelligent version parsing and comparison using SemVer
- **Diff Gates**: Configurable policies for update approval (auto, review, manual)
- **Safe Updates**: Multi-layer health checks and automatic rollback on failure
- **Helm Integration**: Safe Helm release updates with validation
- **Watchtower Support**: Optional integration for standalone Docker containers
- **REST API Server**: FastAPI-based REST API for programmatic access
- **Prometheus Metrics**: Built-in metrics export for monitoring (20+ metrics)
- **Audit Logging**: Complete audit trail of all update operations
- **Interactive Documentation**: Swagger UI and ReDoc for API exploration

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker access (for Docker scanning)
- Kubernetes cluster access (for K8s scanning)
- kubectl configured (optional)

### Install from source

```bash
git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
cd MannosREPOs___Safe-Auto-Updater

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

### 6. Start REST API Server

```bash
# Start with defaults (port 8000)
python -m src.main serve

# Production with multiple workers
python -m src.main serve --workers 4

# Access interactive documentation
# Open http://localhost:8000/api/docs in your browser
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

We welcome contributions! This project uses an automated workflow with AI-powered code reviews.

### Quick Start for Contributors

1. **Fork and clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** following our [coding standards](#development)
4. **Run tests**: `pytest`
5. **Commit**: Use [Conventional Commits](https://www.conventionalcommits.org/) format
6. **Push and create a PR**: Our CI and CodeRabbit will review automatically

### Development Workflow

See **[docs/WORKFLOW.md](docs/WORKFLOW.md)** for complete details on:
- Git branching strategy
- CodeRabbit AI integration
- GitHub Actions CI/CD pipeline
- Pull request process
- Code review guidelines
- Release process

### Code Standards

- **Style**: Black formatting, isort imports, PEP 8
- **Quality**: Pylint score ≥ 8.0, MyPy type checking
- **Testing**: pytest with ≥80% coverage
- **Security**: Bandit, Safety checks must pass
- **Documentation**: Docstrings on all public methods

### Automated Checks

Every PR automatically runs:
- ✅ Code formatting (Black, isort)
- ✅ Linting (Pylint, MyPy)
- ✅ Security scanning (Bandit, Safety, Trivy)
- ✅ Tests (Python 3.11 & 3.12)
- ✅ Docker build & vulnerability scan
- 🤖 **AI code review** with CodeRabbit

See our **CI status**: [![CI](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/actions/workflows/ci.yml/badge.svg)](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/actions)

### Issue & PR Templates

We provide templates for:
- 🐛 [Bug Reports](.github/ISSUE_TEMPLATE/bug_report.yml)
- ✨ [Feature Requests](.github/ISSUE_TEMPLATE/feature_request.yml)
- 🔒 [Security Vulnerabilities](.github/ISSUE_TEMPLATE/security_vulnerability.yml)
- 📋 [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)

## CI/CD Pipeline

This project uses **GitHub Actions** for comprehensive CI/CD:

### Pipeline Stages

1. **Code Quality** (parallel)
   - Black formatting check
   - isort import sorting
   - Pylint linting
   - MyPy type checking

2. **Security Scanning** (parallel)
   - Bandit (Python security)
   - Safety (dependency vulnerabilities)
   - Trivy (container scanning)

3. **Testing** (matrix: Python 3.11, 3.12)
   - Unit tests with pytest
   - Coverage reporting (Codecov)
   - Integration tests

4. **Docker Build**
   - Multi-stage build
   - Vulnerability scanning
   - Push to GHCR (on main)

**Total Duration**: ~5 minutes ⚡

### CodeRabbit AI Integration

This project uses [CodeRabbit](https://coderabbit.ai) for AI-powered code reviews:

- 🤖 **Automatic reviews** on every PR
- 🔍 **Security-focused** analysis for defensive code
- 💡 **Committable suggestions** for quick fixes
- 📊 **Incremental reviews** on each push
- 💬 **Chat functionality** for explanations

**Configuration**: See [.coderabbit.yaml](.coderabbit.yaml)

## Project Status

- ✅ **MVP Complete**: Asset inventory, SemVer analysis, diff gates
- 🚧 **In Progress**: Helm updater, health checks, rollback system
- 📅 **Planned**: Watchtower integration, Prometheus metrics, audit logging

See [docs/PRD.md](docs/PRD.md) for the complete roadmap.

## Documentation

- **[README.md](README.md)** - This file (quick start)
- **[docs/STARTER.md](docs/STARTER.md)** - Architecture & specifications
- **[docs/WORKFLOW.md](docs/WORKFLOW.md)** - Development workflow & CI/CD
- **[docs/PRD.md](docs/PRD.md)** - Product requirements (comprehensive)
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance

## Support

### Getting Help

- 📖 **Documentation**: Start with [docs/STARTER.md](docs/STARTER.md)
- 🐛 **Bug Reports**: Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml)
- 💡 **Feature Requests**: Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml)
- 🔒 **Security Issues**: Report privately via [security advisory](../../security/advisories/new)
- 💬 **Questions**: Open a [GitHub Discussion](../../discussions)

### Community

- **GitHub**: [w7-mgfcode/MannosREPOs___Safe-Auto-Updater](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater)
- **Issues**: [Issue Tracker](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/issues)
- **Pull Requests**: [Open PRs](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/pulls)

---

**Built with ❤️ by MannosREPOs**
**Powered by 🤖 [CodeRabbit AI](https://coderabbit.ai) & ⚡ [GitHub Actions](https://github.com/features/actions)**