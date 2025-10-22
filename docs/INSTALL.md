# Installation Guide

This guide provides instructions for installing and setting up the Safe Auto-Updater system.

## Prerequisites

### Required
- Python 3.8 or higher
- pip (Python package manager)

### Optional (depending on your use case)
- Docker (for Docker container updates)
- kubectl (for Kubernetes integration)
- Helm 3 (for Helm release updates)
- Access to a Kubernetes cluster (for Kubernetes features)

## Installation Methods

### Method 1: Python Virtual Environment (Recommended for Development)

1. Clone the repository:
```bash
git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
cd MannosREPOs___Safe-Auto-Updater
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Verify the installation:
```bash
python src/main.py --help
```

### Method 2: Docker Deployment

1. Build the Docker image:
```bash
docker build -f deployment/docker/Dockerfile -t safe-auto-updater:latest .
```

2. Run using Docker Compose:
```bash
docker-compose -f configs/docker/docker-compose.yml up -d
```

3. Check the logs:
```bash
docker logs safe-auto-updater
```

### Method 3: Kubernetes Deployment

1. Apply the Kubernetes manifests:
```bash
kubectl apply -f configs/kubernetes/deployment.yaml
```

2. Check the deployment status:
```bash
kubectl get pods -n safe-auto-updater
```

3. View logs:
```bash
kubectl logs -n safe-auto-updater deployment/safe-auto-updater
```

### Method 4: Helm Chart

1. Create the namespace:
```bash
kubectl create namespace safe-auto-updater
```

2. Install the Helm chart:
```bash
helm install safe-auto-updater configs/helm/ \
  --namespace safe-auto-updater \
  --values configs/helm/values.yaml
```

3. Check the release:
```bash
helm list -n safe-auto-updater
```

## Configuration

1. Copy the example configuration:
```bash
cp configs/config.yaml configs/config.local.yaml
```

2. Edit the configuration file:
```bash
nano configs/config.local.yaml
```

3. Update the following settings based on your environment:
   - `enable_docker`: Set to `true` if monitoring Docker containers
   - `enable_kubernetes`: Set to `true` if monitoring Kubernetes resources
   - `kubernetes.namespace`: Specify the namespace to monitor
   - `semver` settings: Configure allowed update types
   - `health_check` settings: Adjust timeouts and intervals

## Verification

Test the installation:

```bash
# For Python installation
python src/main.py -c configs/config.local.yaml --dry-run

# For Docker installation
docker exec safe-auto-updater python src/main.py --help

# For Kubernetes installation
kubectl exec -n safe-auto-updater deployment/safe-auto-updater -- python src/main.py --help
```

## Troubleshooting

### Python Module Not Found
If you see module import errors, ensure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Docker Socket Permission Denied
Ensure the user has permission to access the Docker socket:
```bash
sudo usermod -aG docker $USER
```

### Kubernetes Connection Issues
Verify your kubeconfig is properly set up:
```bash
kubectl cluster-info
```

## Next Steps

- Read the [Usage Guide](USAGE.md) to learn how to use the system
- Review the [API Documentation](API.md) for integration details
- Check the [Configuration Reference](CONFIG.md) for all available options
