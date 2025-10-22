# Safe Auto-Updater

A production-ready system that inventories Docker/Kubernetes assets, detects and evaluates changes with SemVer and diff gates, safely auto-updates Helm releases, and optionally updates Docker apps via Watchtower with health checks and rollback guidance.

## Features

- **Asset Inventory**: Automatically discover and catalog Docker containers, Kubernetes deployments, and Helm releases
- **Smart Update Detection**: Detect available updates with semantic versioning evaluation
- **Safety Gates**: Analyze configuration diffs and assess risk before applying updates
- **Health Checks**: Verify application health before and after updates
- **Automatic Rollback**: Roll back failed updates automatically
- **Multiple Deployment Options**: Docker Compose, Kubernetes, or Helm
- **Watchtower Integration**: Seamlessly update Docker containers
- **Helm Management**: Safely upgrade and rollback Helm releases

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
cd MannosREPOs___Safe-Auto-Updater

# Run installation script
./scripts/install.sh
```

### Configuration

Edit `configs/config.yaml` to configure your update policies:

```yaml
detection:
  semver:
    auto_update_patch: true   # Auto-update patch versions
    auto_update_minor: false  # Require approval for minor versions
    auto_update_major: false  # Require approval for major versions
```

### Usage

```bash
# Scan and inventory assets
safe-auto-updater inventory --type all

# Detect available updates
safe-auto-updater detect --dry-run

# Execute updates (with health checks)
safe-auto-updater update

# Check system status
safe-auto-updater status
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Usage Guide](docs/USAGE.md)
- [API Reference](docs/API.md)

## Architecture

The system consists of three main modules:

1. **Inventory Module**: Scans and catalogs Docker/Kubernetes assets
2. **Detection Module**: Identifies updates and evaluates safety using SemVer and diff analysis
3. **Execution Module**: Applies updates with health checks and rollback capability

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## Deployment

### Docker Compose

```bash
cd configs/docker
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f configs/kubernetes/deployment.yaml
```

### Helm

```bash
helm install safe-auto-updater ./configs/helm
```

## Development

### Running Tests

```bash
./scripts/test.sh
```

### Project Structure

```
├── src/safe_auto_updater/    # Main application code
│   ├── inventory/            # Asset scanning and inventory
│   ├── detection/            # Update detection and evaluation
│   ├── execution/            # Update execution and rollback
│   └── utils/                # Common utilities
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── configs/                  # Configuration files
│   ├── docker/               # Docker Compose configs
│   ├── kubernetes/           # Kubernetes manifests
│   └── helm/                 # Helm chart
├── docs/                     # Documentation
└── scripts/                  # Helper scripts
```

## Safety Features

- **SemVer-Based Policies**: Configure which version updates are automatically applied
- **Configuration Diff Analysis**: Analyze changes before applying updates
- **Pre/Post Health Checks**: Verify application health at every step
- **Automatic Rollback**: Failed updates are rolled back automatically
- **Dry Run Mode**: Preview changes without applying them
- **Risk Assessment**: Evaluate update risk level before proceeding

## Requirements

- Python 3.9+
- Docker (optional, for Docker asset management)
- kubectl (optional, for Kubernetes management)
- helm (optional, for Helm release management)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
