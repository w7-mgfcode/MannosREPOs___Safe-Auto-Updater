# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MannosREPOs Safe Auto-Updater** is a production-ready system designed to:
- Inventory Docker/Kubernetes assets
- Detect and evaluate changes with SemVer and diff gates
- Safely auto-update Helm releases
- Optionally update Docker apps via Watchtower with health checks and rollback guidance

This is a **defensive security tool** focused on safe, controlled automation of container and Kubernetes updates.

## Architecture

### Core Components (To Be Implemented)

1. **Asset Inventory Service**
   - Discovers Docker containers and Kubernetes resources
   - Maintains state of current deployments
   - Tracks versions and configurations

2. **Change Detection Engine**
   - Monitors container registries for new image versions
   - Evaluates changes using Semantic Versioning rules
   - Applies diff gates to determine update safety

3. **Update Orchestration Layer**
   - Manages Helm release updates with safety checks
   - Integrates with Watchtower for Docker updates
   - Implements health checks and validation

4. **Rollback System**
   - Monitors update health post-deployment
   - Provides automated rollback on failure detection
   - Maintains rollback history and audit logs

### Technology Stack Considerations

- **Languages**: Python (recommended for orchestration), Go (optional for performance-critical components)
- **Container Orchestration**: Kubernetes, Helm
- **Docker Management**: Watchtower integration
- **Configuration**: YAML-based declarative configuration
- **Monitoring**: Prometheus metrics, health check endpoints

## Development Commands

### Running the Application

```bash
# Scan assets
python -m src.main scan [--docker] [--kubernetes] [--namespace NAMESPACE]

# List tracked assets
python -m src.main list-assets

# Compare versions
python -m src.main compare <current_version> <new_version>

# Evaluate update decision
python -m src.main evaluate <current_version> <new_version>

# View statistics
python -m src.main stats

# Generate configuration
python -m src.main generate-config --output config/policy.yaml

# Validate configuration
python -m src.main validate-config --config-file config/policy.yaml
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
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

# Security scanning
bandit -r src/
safety check
```

### Docker Operations

```bash
# Build Docker image
docker build -t safe-auto-updater:latest .

# Run in Docker (with Docker socket access)
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/config:/app/config \
  safe-auto-updater:latest scan
```

## Project Structure

```
src/
├── config/           - Configuration schema and loading
│   ├── schema.py     - Pydantic models for configuration
│   └── policy_loader.py - Configuration file loader
├── inventory/        - Asset discovery and state management
│   ├── state_manager.py - Asset state persistence
│   ├── docker_scanner.py - Docker container scanning
│   └── k8s_scanner.py    - Kubernetes resource scanning
├── detection/        - Change detection and version analysis
│   ├── semver_analyzer.py - Semantic version parsing/comparison
│   └── diff_gate.py       - Update evaluation logic
├── updater/          - Update orchestration (future)
├── health/           - Health check implementations (future)
├── rollback/         - Rollback management (future)
└── main.py           - CLI entry point
```

### Configuration Management

Configuration is loaded from YAML files in this order:
1. `SAFE_UPDATER_CONFIG` environment variable
2. `./config/policy.yaml`
3. `./policy.yaml`
4. `/etc/safe-updater/policy.yaml`
5. `~/.safe-updater/policy.yaml`

See [config/default_policy.yaml](config/default_policy.yaml) for examples.

## Security Considerations

**CRITICAL**: This is a defensive security tool. Never implement:
- Unauthorized credential harvesting
- Malicious update injection
- Backdoor mechanisms
- Uncontrolled remote code execution

Always implement:
- Secure credential management (K8s secrets, vaults)
- Update validation and verification
- Audit logging of all actions
- Principle of least privilege for K8s RBAC

## Key Design Principles

1. **Safety First**: Always prefer no-op over risky operations
2. **Idempotency**: All update operations should be safely repeatable
3. **Observability**: Comprehensive logging and metrics at every step
4. **Fail-Safe**: Default to manual approval if automation confidence is low
5. **Auditability**: Complete trail of what was updated, when, and why
