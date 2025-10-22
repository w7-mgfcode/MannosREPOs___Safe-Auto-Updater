# Usage Guide

## Installation

### Using pip

```bash
pip install safe-auto-updater
```

### From source

```bash
git clone https://github.com/w7-mgfcode/MannosREPOs___Safe-Auto-Updater.git
cd MannosREPOs___Safe-Auto-Updater
./scripts/install.sh
```

## Configuration

Create a configuration file `config.yaml`:

```yaml
inventory:
  docker:
    enabled: true
    scan_interval: 300
  kubernetes:
    enabled: true
    namespaces:
      - default
      - production

detection:
  semver:
    auto_update_patch: true
    auto_update_minor: false
    auto_update_major: false

execution:
  health_checks:
    enabled: true
    retry_count: 3
  rollback:
    enabled: true
    auto_rollback_on_failure: true
```

## Command Line Usage

### Inventory Scan

Scan and inventory Docker and Kubernetes assets:

```bash
# Scan all assets
safe-auto-updater inventory --type all

# Scan only Docker containers
safe-auto-updater inventory --type docker

# Scan only Kubernetes deployments
safe-auto-updater inventory --type kubernetes

# Scan only Helm releases
safe-auto-updater inventory --type helm
```

### Detect Updates

Detect available updates for monitored assets:

```bash
# Detect updates
safe-auto-updater detect

# Dry run mode (show what would be updated)
safe-auto-updater detect --dry-run
```

### Execute Updates

Execute updates with health checks and rollback capability:

```bash
# Update all assets
safe-auto-updater update

# Update specific asset
safe-auto-updater update --asset my-app

# Skip health checks (not recommended)
safe-auto-updater update --skip-health-check
```

### Check Status

Display system status:

```bash
safe-auto-updater status
```

## Docker Deployment

### Using Docker Compose

```bash
cd configs/docker
docker-compose up -d
```

### Using Docker directly

```bash
docker build -t safe-auto-updater .
docker run -v /var/run/docker.sock:/var/run/docker.sock \
           -v $(pwd)/configs:/app/configs \
           safe-auto-updater inventory --type all
```

## Kubernetes Deployment

### Apply manifests

```bash
kubectl apply -f configs/kubernetes/deployment.yaml
```

### Using Helm

```bash
helm install safe-auto-updater ./configs/helm \
  --values configs/helm/values.yaml
```

## Configuration Options

### Inventory Settings

- `scan_interval`: Time between scans (seconds)
- `namespaces`: Kubernetes namespaces to scan

### Detection Settings

- `auto_update_patch`: Automatically update patch versions
- `auto_update_minor`: Automatically update minor versions
- `auto_update_major`: Automatically update major versions
- `max_risk_level`: Maximum acceptable risk level

### Execution Settings

- `retry_count`: Number of health check retries
- `retry_delay`: Delay between retries (seconds)
- `timeout`: Health check timeout (seconds)
- `auto_rollback_on_failure`: Enable automatic rollback

## Best Practices

1. **Start with Dry Run**: Always test with `--dry-run` first
2. **Enable Health Checks**: Never skip health checks in production
3. **Conservative Updates**: Start with patch-only updates
4. **Monitor Logs**: Review logs after updates
5. **Test Rollback**: Verify rollback procedures work before deploying

## Troubleshooting

### Docker Socket Permission Denied

Ensure the user has access to Docker socket:

```bash
sudo usermod -aG docker $USER
```

### Kubernetes RBAC Errors

Verify service account has correct permissions:

```bash
kubectl auth can-i list deployments --as=system:serviceaccount:default:safe-auto-updater
```

### Health Check Failures

Increase retry count and delay:

```yaml
execution:
  health_checks:
    retry_count: 5
    retry_delay: 10
```
