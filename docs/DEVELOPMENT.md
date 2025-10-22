# Development Guide
## Safe Auto-Updater

**Version:** 1.0  
**Last Updated:** October 20, 2025

---

## Table of Contents
1. [Getting Started](#1-getting-started)
2. [Development Environment](#2-development-environment)
3. [Project Structure](#3-project-structure)
4. [Coding Standards](#4-coding-standards)
5. [Testing](#5-testing)
6. [Git Workflow](#6-git-workflow)
7. [Contributing](#7-contributing)
8. [Release Process](#8-release-process)

---

## 1. Getting Started

### 1.1 Prerequisites

```bash
# Required
- Python 3.11+
- Git
- Docker Desktop (for testing)
- kubectl (for Kubernetes testing)

# Recommended
- VS Code or PyCharm
- kind or minikube (local Kubernetes)
- helm 3.x
```

### 1.2 Quick Start

```bash
# Clone repository
git clone https://github.com/MannosREPOs/Safe-Auto-Updater.git
cd Safe-Auto-Updater

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Try CLI
safe-updater --help
```

---

## 2. Development Environment

### 2.1 IDE Setup

#### VS Code

Install extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.pylint",
    "ms-azuretools.vscode-docker",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "redhat.vscode-yaml"
  ]
}
```

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project
2. Configure interpreter: Settings → Project → Python Interpreter → Add Interpreter → Virtualenv
3. Enable pytest: Settings → Tools → Python Integrated Tools → Testing → pytest
4. Configure Black: Settings → Tools → External Tools → Add Black
5. Enable mypy: Settings → Tools → External Tools → Add mypy

### 2.2 Environment Variables

Create `.env` file:

```bash
# .env (DO NOT COMMIT)
SAFE_UPDATER_LOG_LEVEL=DEBUG
SAFE_UPDATER_CONFIG=config/dev-policy.yaml

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# Kubernetes
KUBECONFIG=~/.kube/config

# Registry (for testing)
REGISTRY_USERNAME=testuser
REGISTRY_PASSWORD=testpass
```

Add to `.gitignore`:
```
.env
.env.local
*.env
```

### 2.3 Local Kubernetes Cluster

#### Using kind

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster --name safe-updater-dev

# Verify
kubectl cluster-info --context kind-safe-updater-dev

# Delete when done
kind delete cluster --name safe-updater-dev
```

#### Using minikube

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start cluster
minikube start --driver=docker --kubernetes-version=v1.28.0

# Verify
kubectl get nodes

# Stop when done
minikube stop
```

---

## 3. Project Structure

### 3.1 Directory Layout

```
safe-auto-updater/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # CLI entry point
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── policy_loader.py      # YAML config loader
│   │   └── schema.py             # Pydantic schemas
│   ├── detection/                # Version detection & comparison
│   │   ├── __init__.py
│   │   ├── semver_analyzer.py    # SemVer parsing & comparison
│   │   └── diff_gate.py          # Update policy evaluation
│   ├── inventory/                # Asset discovery
│   │   ├── __init__.py
│   │   ├── state_manager.py      # State persistence
│   │   ├── docker_scanner.py     # Docker container discovery
│   │   └── k8s_scanner.py        # Kubernetes resource discovery
│   ├── health/                   # Health check system
│   │   └── __init__.py
│   ├── rollback/                 # Rollback management
│   │   └── __init__.py
│   └── updater/                  # Update execution
│       └── __init__.py
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   │   ├── test_semver_analyzer.py
│   │   ├── test_diff_gate.py
│   │   └── test_config.py
│   ├── integration/              # Integration tests
│   │   ├── test_docker_scanner.py
│   │   └── test_k8s_scanner.py
│   └── e2e/                      # End-to-end tests
│       └── test_update_flow.py
├── config/                       # Configuration files
│   ├── default_policy.yaml
│   └── examples/
│       └── production_policy.yaml
├── docs/                         # Documentation
│   ├── PRD.md
│   ├── TechStack.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   ├── DEVELOPMENT.md
│   └── STARTER.md
├── .github/                      # GitHub workflows
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       └── release.yml
├── Dockerfile                    # Container build
├── docker-compose.yml            # Local testing
├── requirements.txt              # Production dependencies
├── setup.py                      # Package setup
├── pytest.ini                    # Pytest configuration
├── mypy.ini                      # MyPy configuration
├── .pylintrc                     # Pylint configuration
├── .gitignore
├── LICENSE
└── README.md
```

### 3.2 Module Organization

#### config/
- `schema.py`: Pydantic models for configuration
- `policy_loader.py`: YAML loading and validation

#### detection/
- `semver_analyzer.py`: Version parsing, comparison, upgrade detection
- `diff_gate.py`: Policy-based update approval logic

#### inventory/
- `state_manager.py`: Asset state persistence and queries
- `docker_scanner.py`: Docker container discovery via API
- `k8s_scanner.py`: Kubernetes resource discovery via client

---

## 4. Coding Standards

### 4.1 Python Style Guide

Follow **PEP 8** with these specifics:

```python
# Line length
max_line_length = 100

# Indentation
indent_size = 4  # spaces, not tabs

# Naming conventions
class MyClass:              # PascalCase
    CONSTANT_VALUE = 10     # UPPER_CASE
    
    def my_method(self):    # snake_case
        local_variable = 5   # snake_case
        return local_variable

# Type hints (required)
def process_version(version: str) -> Optional[semver.Version]:
    """Process version string."""
    pass

# Docstrings (Google style)
def compare_versions(current: str, new: str) -> Tuple[int, str]:
    """
    Compare two version strings.
    
    Args:
        current: Current version string.
        new: New version string.
    
    Returns:
        Tuple of (comparison_result, change_type).
        
    Raises:
        ValueError: If versions are invalid.
    """
    pass
```

### 4.2 Type Hints

**Always use type hints**:

```python
from typing import Optional, List, Dict, Tuple, Union

# Function signatures
def scan_containers(
    socket_path: str,
    include_stopped: bool = False
) -> List[Dict[str, str]]:
    """Scan Docker containers."""
    pass

# Class attributes
class Asset:
    name: str
    version: str
    metadata: Dict[str, Any]
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.metadata = {}

# Return types
def get_asset(asset_id: str) -> Optional[Asset]:
    """Retrieve asset by ID."""
    pass
```

### 4.3 Error Handling

```python
# Specific exceptions
class SafeUpdaterError(Exception):
    """Base exception for Safe Updater."""
    pass

class ConfigurationError(SafeUpdaterError):
    """Configuration validation error."""
    pass

class ScanError(SafeUpdaterError):
    """Asset scanning error."""
    pass

# Usage
try:
    config = load_config(config_path)
except FileNotFoundError:
    logger.error("Config file not found", path=config_path)
    raise ConfigurationError(f"Config not found: {config_path}")
except yaml.YAMLError as e:
    logger.error("Invalid YAML", error=str(e))
    raise ConfigurationError(f"Invalid YAML: {e}")
```

### 4.4 Logging

```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "scanning_started",
    scanner="docker",
    socket_path="/var/run/docker.sock"
)

logger.error(
    "scan_failed",
    scanner="kubernetes",
    namespace="default",
    error=str(e)
)

# Context binding
log = logger.bind(asset_id="my-app", namespace="production")
log.info("update_started", current="1.0.0", new="1.1.0")
log.info("update_completed", duration_seconds=45.2)
```

---

## 5. Testing

### 5.1 Test Structure

```python
# tests/unit/test_semver_analyzer.py
import pytest
from src.detection.semver_analyzer import SemVerAnalyzer, VersionChangeType

class TestSemVerAnalyzer:
    """Test suite for SemVerAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture providing analyzer instance."""
        return SemVerAnalyzer()
    
    def test_parse_standard_version(self, analyzer):
        """Test parsing standard semantic version."""
        version = analyzer.parse_version("1.2.3")
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
    
    def test_compare_patch_update(self, analyzer):
        """Test comparison of patch update."""
        comparison, change_type = analyzer.compare_versions("1.0.0", "1.0.1")
        assert comparison == 1  # Upgrade
        assert change_type == VersionChangeType.PATCH
    
    @pytest.mark.parametrize("current,new,expected_type", [
        ("1.0.0", "1.0.1", VersionChangeType.PATCH),
        ("1.0.0", "1.1.0", VersionChangeType.MINOR),
        ("1.0.0", "2.0.0", VersionChangeType.MAJOR),
    ])
    def test_change_types(self, analyzer, current, new, expected_type):
        """Test different change types."""
        _, change_type = analyzer.compare_versions(current, new)
        assert change_type == expected_type
```

### 5.2 Mocking

```python
# tests/integration/test_docker_scanner.py
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_docker_client():
    """Mock Docker client."""
    client = Mock()
    client.containers.list.return_value = [
        Mock(
            id="abc123",
            name="test-container",
            image=Mock(tags=["nginx:1.21"]),
            labels={"app": "web"}
        )
    ]
    return client

def test_scan_containers(mock_docker_client):
    """Test container scanning with mocked Docker."""
    with patch('docker.from_env', return_value=mock_docker_client):
        scanner = DockerScanner()
        containers = scanner.scan_containers()
        
        assert len(containers) == 1
        assert containers[0]['name'] == "test-container"
```

### 5.3 Test Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Coverage report
Coverage: 85%

src/config/schema.py          95%
src/detection/semver_analyzer.py  92%
src/detection/diff_gate.py        88%
src/inventory/state_manager.py    80%
src/inventory/docker_scanner.py   75%
```

### 5.4 Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_semver_analyzer.py

# Specific test
pytest tests/unit/test_semver_analyzer.py::TestSemVerAnalyzer::test_parse_standard_version

# With markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests

# Verbose
pytest -v

# Stop on first failure
pytest -x

# Parallel execution
pytest -n auto
```

---

## 6. Git Workflow

### 6.1 Branch Strategy

```
main (production)
  ↑
  └── develop (integration)
        ↑
        ├── feature/add-watchtower-integration
        ├── feature/helm-update-executor
        ├── bugfix/fix-version-parsing
        └── hotfix/security-patch
```

### 6.2 Branch Naming

```bash
# Feature branches
feature/short-description
feature/issue-123-add-feature

# Bug fixes
bugfix/short-description
bugfix/issue-456-fix-bug

# Hotfixes
hotfix/critical-security-patch

# Releases
release/v1.0.0
```

### 6.3 Commit Messages

Follow **Conventional Commits**:

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style (formatting, etc.)
refactor: Code refactoring
test:     Adding tests
chore:    Maintenance

# Examples
feat(scanner): add Kubernetes CRD discovery

Add support for discovering Custom Resource Definitions
to enable compatibility checking.

Closes #123

---

fix(semver): handle Docker-style version tags

Previously failed on tags like "1.21". Now coerces
to "1.21.0" for proper comparison.

Fixes #456
```

### 6.4 Pull Request Process

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
git add .
git commit -m "feat(component): add feature"

# 3. Push to GitHub
git push origin feature/my-feature

# 4. Create Pull Request
# - Fill out template
# - Request reviews
# - Ensure CI passes

# 5. Address review comments
git add .
git commit -m "fix: address review comments"
git push origin feature/my-feature

# 6. Merge (squash and merge)
# - PR approved
# - CI green
# - Squash commits
```

---

## 7. Contributing

### 7.1 First Contribution

1. **Find an issue**: Look for `good-first-issue` label
2. **Comment**: Express interest and ask questions
3. **Fork**: Fork the repository
4. **Branch**: Create feature branch
5. **Code**: Write code with tests
6. **Test**: Ensure all tests pass
7. **Submit**: Create pull request
8. **Iterate**: Address review feedback

### 7.2 Code Review Checklist

**Before submitting PR**:

- [ ] Code follows style guide
- [ ] All tests pass locally
- [ ] Added tests for new code
- [ ] Updated documentation
- [ ] Type hints added
- [ ] No linting errors
- [ ] Commit messages follow convention
- [ ] PR description filled out

**For reviewers**:

- [ ] Code is clear and maintainable
- [ ] Tests adequately cover changes
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Documentation is accurate
- [ ] Breaking changes are justified

### 7.3 Issue Templates

#### Bug Report

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With config '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.6]
- Safe Updater version: [e.g., 0.1.0]

**Additional context**
Logs, screenshots, etc.
```

#### Feature Request

```markdown
**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Clear description of desired behavior.

**Describe alternatives you've considered**
Other approaches considered.

**Additional context**
Any other information.
```

---

## 8. Release Process

### 8.1 Versioning

Follow **Semantic Versioning 2.0**:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Examples:
0.1.0         - Initial development
1.0.0         - First stable release
1.1.0         - New features (backward compatible)
1.1.1         - Bug fixes
2.0.0         - Breaking changes
2.0.0-beta.1  - Pre-release
```

### 8.2 Release Checklist

**Pre-release**:

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in setup.py
- [ ] Security scan passed
- [ ] Performance benchmarks met

**Release**:

- [ ] Create release branch
- [ ] Tag release
- [ ] Build Docker image
- [ ] Push to registry
- [ ] Create GitHub release
- [ ] Update docs site
- [ ] Announce release

**Post-release**:

- [ ] Monitor for issues
- [ ] Address critical bugs
- [ ] Plan next release

### 8.3 Release Script

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh v1.0.0"
    exit 1
fi

# Run tests
pytest || exit 1

# Update version
sed -i "s/version=\".*\"/version=\"${VERSION#v}\"/" setup.py

# Build Docker image
docker build -t safe-auto-updater:$VERSION .
docker tag safe-auto-updater:$VERSION safe-auto-updater:latest

# Tag release
git tag -a $VERSION -m "Release $VERSION"
git push origin $VERSION

echo "Release $VERSION complete!"
```

---

## 9. Troubleshooting Development Issues

### 9.1 Common Issues

#### Import Errors

```bash
# Problem: ModuleNotFoundError: No module named 'src'

# Solution: Install in editable mode
pip install -e .
```

#### Test Failures

```bash
# Problem: Tests fail with Docker connection error

# Solution: Ensure Docker is running
sudo systemctl start docker
docker ps
```

#### Type Checking Errors

```bash
# Problem: mypy reports missing type stubs

# Solution: Install type stubs
pip install types-pyyaml types-requests
```

### 9.2 Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use environment variable
export SAFE_UPDATER_LOG_LEVEL=DEBUG
safe-updater scan
```

---

## 10. Resources

### 10.1 Documentation

- [Python 3.11](https://docs.python.org/3.11/)
- [Docker SDK](https://docker-py.readthedocs.io/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [Pydantic](https://docs.pydantic.dev/)
- [Pytest](https://docs.pytest.org/)

### 10.2 Community

- GitHub Discussions: [link]
- Slack Channel: [link]
- Weekly Office Hours: Fridays 10 AM PT

---

**Happy Coding!** 🚀

For questions, reach out on GitHub Discussions or Slack.

**Last Updated**: 2025-10-20
