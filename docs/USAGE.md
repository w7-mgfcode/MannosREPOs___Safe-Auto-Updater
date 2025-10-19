# Usage Guide

This guide explains how to use the Safe Auto-Updater system for managing Docker and Kubernetes updates.

## Basic Usage

### Command Line Interface

Run the auto-updater with default configuration:
```bash
python src/main.py
```

Run with a custom configuration file:
```bash
python src/main.py -c /path/to/config.yaml
```

Run in dry-run mode (no actual updates):
```bash
python src/main.py --dry-run
```

Set logging level:
```bash
python src/main.py --log-level DEBUG
```

### Docker Usage

Start the containerized version:
```bash
docker-compose -f configs/docker/docker-compose.yml up -d
```

View logs:
```bash
docker logs -f safe-auto-updater
```

Stop the service:
```bash
docker-compose -f configs/docker/docker-compose.yml down
```

### Kubernetes Usage

Deploy to Kubernetes:
```bash
kubectl apply -f configs/kubernetes/deployment.yaml
```

Check status:
```bash
kubectl get pods -n safe-auto-updater
kubectl logs -n safe-auto-updater deployment/safe-auto-updater -f
```

## Configuration

### Docker Monitoring

To enable Docker container monitoring:

1. Update `configs/config.yaml`:
```yaml
enable_docker: true
docker:
  socket: /var/run/docker.sock
```

2. Ensure the Docker socket is mounted (for containerized deployments)

### Kubernetes Monitoring

To enable Kubernetes resource monitoring:

1. Update `configs/config.yaml`:
```yaml
enable_kubernetes: true
kubernetes:
  namespace: default  # or specific namespace
  labels:
    auto-update: "enabled"  # Only monitor resources with this label
```

2. Apply appropriate RBAC permissions

### Semantic Versioning Rules

Configure which types of updates are allowed:

```yaml
semver:
  allow_major_updates: false  # 1.x.x -> 2.x.x
  allow_minor_updates: true   # 1.1.x -> 1.2.x
  allow_patch_updates: true   # 1.1.1 -> 1.1.2
```

### Health Checks

Configure health check behavior:

```yaml
health_check:
  timeout: 60      # Maximum wait time (seconds)
  interval: 5      # Check interval (seconds)
  retries: 3       # Number of retries
```

### Update Policies

Configure update execution policies:

```yaml
update:
  auto_update: true        # Automatically apply updates
  auto_rollback: true      # Rollback on failure
  wait_for_health: true    # Wait for health checks
  create_backup: true      # Create backup before update
```

## Watchtower Integration

### Setup Watchtower

1. Deploy Watchtower alongside Safe Auto-Updater:
```bash
docker-compose -f configs/docker/docker-compose.yml up -d watchtower
```

2. Configure in `config.yaml`:
```yaml
enable_watchtower: true
watchtower:
  endpoint: http://watchtower:8080
  schedule: "0 0 * * *"  # Daily at midnight
```

### Label Containers for Watchtower

Add labels to containers you want Watchtower to monitor:
```yaml
labels:
  - "com.centurylinklabs.watchtower.enable=true"
```

## Helm Release Updates

### Enable Helm Updates

```yaml
enable_kubernetes: true
kubernetes:
  namespace: default
```

### Update a Helm Release

The system will automatically detect and update Helm releases based on your configuration.

Manual rollback if needed:
```bash
./scripts/rollback.sh helm my-release default
```

## Health Checks

### Manual Health Check

Run a manual health check on a container:
```bash
./scripts/health_check.sh safe-auto-updater
```

### Container Health Check

For containers, the system checks:
- Container running status
- Docker health check status (if defined)
- Application-specific health endpoints

### Kubernetes Health Check

For Kubernetes deployments, the system checks:
- Pod status
- Readiness probes
- Liveness probes

## Rollback Procedures

### Automatic Rollback

If `auto_rollback: true` is enabled, the system automatically rolls back failed updates.

### Manual Rollback

For Kubernetes deployments:
```bash
./scripts/rollback.sh deployment myapp default
```

For Helm releases:
```bash
./scripts/rollback.sh helm myapp default
```

Roll back to a specific revision:
```bash
./scripts/rollback.sh deployment myapp default 3
```

## Monitoring and Logs

### View Logs

Python installation:
```bash
tail -f logs/safe-auto-updater.log
```

Docker installation:
```bash
docker logs -f safe-auto-updater
```

Kubernetes installation:
```bash
kubectl logs -n safe-auto-updater deployment/safe-auto-updater -f
```

### Log Levels

Available log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Configure in `config.yaml`:
```yaml
logging:
  level: INFO
  file: /app/logs/safe-auto-updater.log
```

## Best Practices

1. **Start with Dry-Run**: Always test with `--dry-run` first
2. **Monitor Logs**: Watch logs during updates
3. **Test Rollback**: Verify rollback procedures work
4. **Use Health Checks**: Define proper health checks for your services
5. **Start Conservative**: Begin with patch updates only
6. **Backup Regularly**: Enable `create_backup: true`
7. **Label Resources**: Use labels to control which resources are updated

## Troubleshooting

### No Updates Detected
- Verify registry access
- Check version detection logic
- Review logs for errors

### Update Failed
- Check health check configuration
- Review rollback logs
- Verify resource permissions

### Health Check Timeout
- Increase timeout value
- Check application startup time
- Review readiness probe configuration

## Next Steps

- Review the [API Documentation](API.md) for integration
- Check [Configuration Reference](CONFIG.md) for all options
- See [Examples](EXAMPLES.md) for common scenarios
