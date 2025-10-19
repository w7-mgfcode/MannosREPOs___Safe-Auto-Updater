# API Documentation

This document describes the API and module interfaces for the Safe Auto-Updater system.

## Core Modules

### Inventory Module

#### DockerInventory

Manages Docker container and image inventory.

```python
from inventory.docker_inventory import DockerInventory

# Initialize
inventory = DockerInventory(docker_client=None)

# Discover containers
containers = inventory.discover_containers()

# Discover images
images = inventory.discover_images()

# Get container info
info = inventory.get_container_info("container_id")
```

#### KubernetesInventory

Manages Kubernetes resource inventory.

```python
from inventory.kubernetes_inventory import KubernetesInventory

# Initialize
inventory = KubernetesInventory(kube_client=None)

# Discover deployments
deployments = inventory.discover_deployments(namespace="default")

# Discover pods
pods = inventory.discover_pods(namespace="default")

# Discover Helm releases
releases = inventory.discover_helm_releases(namespace="default")
```

### Detection Module

#### VersionDetector

Detects version updates for images and packages.

```python
from detection.version_detector import VersionDetector

# Initialize
detector = VersionDetector()

# Check for updates
new_version = detector.check_for_updates("nginx", "1.20.0")

# Get latest version
latest = detector.get_latest_version("nginx")

# Compare versions
result = detector.compare_versions("1.20.0", "1.21.0")
```

#### ImageDetector

Detects changes in Docker images.

```python
from detection.image_detector import ImageDetector

# Initialize
detector = ImageDetector()

# Detect image changes
changed = detector.detect_image_changes("nginx:latest", "sha256:abc123")

# Get image digest
digest = detector.get_image_digest("nginx", "latest")

# Get image metadata
metadata = detector.get_image_metadata("nginx", "latest")
```

### Evaluation Module

#### SemVerEvaluator

Evaluates version changes using Semantic Versioning.

```python
from evaluation.semver_evaluator import SemVerEvaluator

# Initialize with config
config = {
    'allow_major_updates': False,
    'allow_minor_updates': True,
    'allow_patch_updates': True
}
evaluator = SemVerEvaluator(config)

# Parse version
version = evaluator.parse_version("1.2.3")

# Evaluate update
result = evaluator.evaluate_update("1.2.3", "1.3.0")
# Returns: {'allowed': True, 'reason': 'Minor version change', 'change_type': 'minor'}
```

#### DiffEvaluator

Evaluates configuration and image diffs.

```python
from evaluation.diff_evaluator import DiffEvaluator

# Initialize with config
config = {
    'max_file_changes': 100,
    'blocked_paths': ['/etc/security']
}
evaluator = DiffEvaluator(config)

# Evaluate config diff
result = evaluator.evaluate_config_diff(old_config, new_config)

# Evaluate image diff
result = evaluator.evaluate_image_diff("nginx:1.20", "nginx:1.21")
```

### Updater Module

#### DockerUpdater

Manages Docker container updates.

```python
from updater.docker_updater import DockerUpdater

# Initialize
updater = DockerUpdater(docker_client=None)

# Update container
result = updater.update_container("container_id", "nginx:1.21")

# Rollback container
result = updater.rollback_container("container_id", "nginx:1.20")
```

#### HelmUpdater

Manages Helm release updates.

```python
from updater.helm_updater import HelmUpdater

# Initialize
updater = HelmUpdater()

# Update release
result = updater.update_release(
    release_name="myapp",
    chart="myapp/chart",
    namespace="default",
    values={'replicas': 3}
)

# Rollback release
result = updater.rollback_release(
    release_name="myapp",
    revision=2,
    namespace="default"
)

# Get release history
history = updater.get_release_history("myapp", "default")
```

#### WatchtowerUpdater

Manages Watchtower integration.

```python
from updater.watchtower_updater import WatchtowerUpdater

# Initialize
updater = WatchtowerUpdater(watchtower_endpoint="http://localhost:8080")

# Configure Watchtower
result = updater.configure_watchtower(config)

# Trigger update
result = updater.trigger_update(["container1", "container2"])

# Get status
status = updater.get_watchtower_status()
```

### Utility Module

#### HealthChecker

Performs health checks on containers and services.

```python
from utils.health_check import HealthChecker

# Initialize
checker = HealthChecker(timeout=60, interval=5)

# Check container health
result = checker.check_container_health("container_id")

# Wait for healthy
is_healthy = checker.wait_for_healthy("container_id")

# Check endpoint health
result = checker.check_endpoint_health("http://localhost:8080/health")
```

#### ConfigLoader

Loads and manages configuration.

```python
from utils.config_loader import ConfigLoader

# Initialize and load
loader = ConfigLoader("configs/config.yaml")

# Get values
value = loader.get("kubernetes.namespace", default="default")

# Set values
loader.set("kubernetes.namespace", "production")

# Save config
loader.save_config("configs/config.yaml")
```

#### Logger Setup

Configure logging for the application.

```python
from utils.logger import setup_logging

# Setup logging
setup_logging(level="INFO", log_file="/var/log/safe-auto-updater.log")
```

## Main Application

### SafeAutoUpdater

Main orchestrator class.

```python
from main import SafeAutoUpdater

# Initialize
updater = SafeAutoUpdater("configs/config.yaml")

# Run the update process
updater.run()
```

## Response Formats

### Standard Response Format

All update and rollback operations return a dictionary with the following structure:

```python
{
    'success': True,  # or False
    'message': 'Operation completed successfully',
    # Additional operation-specific fields
}
```

### Error Response Format

```python
{
    'success': False,
    'error': 'Error message describing what went wrong',
    # Additional context fields
}
```

## Examples

### Complete Update Workflow

```python
from main import SafeAutoUpdater

# Initialize with configuration
updater = SafeAutoUpdater("configs/config.yaml")

# Run the complete update process
# This includes: inventory, detection, evaluation, and update phases
updater.run()
```

### Custom Update Logic

```python
from inventory.docker_inventory import DockerInventory
from detection.version_detector import VersionDetector
from evaluation.semver_evaluator import SemVerEvaluator
from updater.docker_updater import DockerUpdater
from utils.health_check import HealthChecker

# Initialize components
inventory = DockerInventory()
detector = VersionDetector()
evaluator = SemVerEvaluator({'allow_minor_updates': True})
updater = DockerUpdater()
health_checker = HealthChecker()

# Get containers
containers = inventory.discover_containers()

# For each container
for container in containers:
    # Check for updates
    new_version = detector.check_for_updates(
        container['image'], 
        container['version']
    )
    
    if new_version:
        # Evaluate if update should be applied
        evaluation = evaluator.evaluate_update(
            container['version'], 
            new_version
        )
        
        if evaluation['allowed']:
            # Perform update
            result = updater.update_container(
                container['id'], 
                f"{container['image']}:{new_version}"
            )
            
            if result['success']:
                # Wait for health check
                is_healthy = health_checker.wait_for_healthy(container['id'])
                
                if not is_healthy:
                    # Rollback on health check failure
                    updater.rollback_container(
                        container['id'], 
                        f"{container['image']}:{container['version']}"
                    )
```

## Error Handling

All methods may raise exceptions. Wrap calls in try-except blocks:

```python
try:
    result = updater.update_container("container_id", "nginx:1.21")
    if not result['success']:
        print(f"Update failed: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception during update: {e}")
```

## Next Steps

- Review [Usage Guide](USAGE.md) for practical examples
- Check [Configuration Reference](CONFIG.md) for all options
- See test files in `tests/` for more usage examples
