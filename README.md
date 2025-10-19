# Safe Auto-Updater

[![CI](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/workflows/CI/badge.svg)](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A production-ready Safe Auto-Updater system that inventories Docker/Kubernetes assets, detects and evaluates changes with SemVer and diff gates, safely auto-updates Helm releases, and optionally updates Docker apps via Watchtower with health checks and rollback guidance.

## Features

- **Inventory Management**: Automatically discover and track Docker containers and Kubernetes resources
- **Smart Detection**: Detect available updates for images and Helm releases
- **Safe Evaluation**: Use Semantic Versioning rules and diff gates to evaluate changes
- **Automated Updates**: Safely execute updates with health checks and automatic rollback
- **Helm Integration**: Native support for Helm release management
- **Watchtower Support**: Optional integration with Watchtower for Docker updates
- **Health Monitoring**: Built-in health checks for containers and services
- **Rollback Capability**: Automatic and manual rollback support

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Docker (optional, for Docker monitoring)
- kubectl (optional, for Kubernetes monitoring)
- Helm 3 (optional, for Helm management)

### Installation

```bash
# Clone the repository
git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
cd MannosREPOs___Safe-Auto-Updater

# Run the setup script
./scripts/setup.sh

# Activate the virtual environment
source venv/bin/activate
```

### Basic Usage

```bash
# Run with default configuration
python src/main.py

# Run with custom configuration
python src/main.py -c configs/config.yaml

# Dry run (no actual updates)
python src/main.py --dry-run

# Set log level
python src/main.py --log-level DEBUG
```

### Docker Deployment

```bash
# Build the image
docker build -f deployment/docker/Dockerfile -t safe-auto-updater:latest .

# Run with Docker Compose
docker-compose -f configs/docker/docker-compose.yml up -d
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f configs/kubernetes/deployment.yaml

# Check status
kubectl get pods -n safe-auto-updater
```

## Configuration

Edit `configs/config.yaml` to customize behavior:

```yaml
# Enable/disable components
enable_docker: true
enable_kubernetes: true

# Semantic Version rules
semver:
  allow_major_updates: false
  allow_minor_updates: true
  allow_patch_updates: true

# Update policies
update:
  auto_update: true
  auto_rollback: true
  wait_for_health: true
```

See the [Configuration Documentation](docs/CONFIG.md) for all options.

## Documentation

- [Installation Guide](docs/INSTALL.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - How to use the system
- [API Documentation](docs/API.md) - API reference and examples

## Project Structure

```
.
├── src/                    # Source code
│   ├── inventory/          # Asset inventory modules
│   ├── detection/          # Change detection modules
│   ├── evaluation/         # Change evaluation modules
│   ├── updater/            # Update execution modules
│   └── utils/              # Utility modules
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── configs/               # Configuration files
│   ├── docker/           # Docker configurations
│   ├── kubernetes/       # Kubernetes manifests
│   └── helm/             # Helm chart
├── scripts/              # Utility scripts
├── deployment/           # Deployment files
├── docs/                 # Documentation
└── README.md            # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Lint code
flake8 src/

# Format code
black src/

# Type checking
pylint src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please use the [GitHub Issues](https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater/issues) page.

## Authors

- Safe Auto-Updater Team

## Acknowledgments

- Docker team for Docker API
- Kubernetes team for Kubernetes API
- Helm team for Helm
- Watchtower project for inspiration
