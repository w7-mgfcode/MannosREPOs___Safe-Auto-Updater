# API Reference

## Inventory Module

### AssetInventory

Main class for managing asset inventory.

```python
from safe_auto_updater.inventory import AssetInventory

inventory = AssetInventory()
```

#### Methods

- `add_asset(asset_type: str, asset: Dict) -> None`: Add an asset to inventory
- `get_assets(asset_type: Optional[str] = None) -> Dict`: Retrieve assets
- `clear() -> None`: Clear all assets from inventory

### DockerScanner

Scans Docker containers and images.

```python
from safe_auto_updater.inventory import DockerScanner

scanner = DockerScanner(docker_client)
containers = scanner.scan_containers()
images = scanner.scan_images()
```

### KubernetesScanner

Scans Kubernetes resources.

```python
from safe_auto_updater.inventory import KubernetesScanner

scanner = KubernetesScanner(k8s_client)
deployments = scanner.scan_deployments(namespace="default")
releases = scanner.scan_helm_releases(namespace="default")
```

## Detection Module

### SemVerEvaluator

Evaluates semantic versioning.

```python
from safe_auto_updater.detection import SemVerEvaluator

evaluator = SemVerEvaluator()
```

#### Methods

- `parse_version(version: str) -> Optional[Tuple[int, int, int]]`: Parse version string
- `compare_versions(current: str, target: str) -> int`: Compare versions
- `is_breaking_change(current: str, target: str) -> bool`: Check for breaking changes
- `is_minor_update(current: str, target: str) -> bool`: Check for minor updates
- `is_patch_update(current: str, target: str) -> bool`: Check for patch updates

### DiffAnalyzer

Analyzes configuration differences.

```python
from safe_auto_updater.detection import DiffAnalyzer

analyzer = DiffAnalyzer()
diff = analyzer.analyze_config_diff(current_config, new_config)
```

#### Methods

- `analyze_config_diff(current_config: Dict, new_config: Dict) -> Dict`: Analyze differences
- `has_critical_changes(diff_result: Dict) -> bool`: Check for critical changes

### ChangeDetector

Detects changes and available updates.

```python
from safe_auto_updater.detection import ChangeDetector

detector = ChangeDetector(semver_evaluator, diff_analyzer)
```

#### Methods

- `detect_updates(asset: Dict) -> Optional[Dict]`: Detect available updates
- `check_update_safety(update: Dict) -> bool`: Check if update is safe

## Execution Module

### UpdateExecutor

Orchestrates update execution.

```python
from safe_auto_updater.execution import UpdateExecutor

executor = UpdateExecutor(helm_updater, watchtower_updater, health_checker)
success = executor.execute_update(asset, update_info)
```

#### Methods

- `execute_update(asset: Dict, update_info: Dict) -> bool`: Execute an update

### HelmUpdater

Manages Helm releases.

```python
from safe_auto_updater.execution import HelmUpdater

updater = HelmUpdater(namespace="default")
```

#### Methods

- `upgrade_release(release_name: str, chart_version: str, ...) -> bool`: Upgrade release
- `rollback_release(release_name: str, revision: Optional[int]) -> bool`: Rollback release
- `get_release_history(release_name: str) -> list`: Get release history

### WatchtowerUpdater

Manages Docker updates via Watchtower.

```python
from safe_auto_updater.execution import WatchtowerUpdater

updater = WatchtowerUpdater(watchtower_api_url)
```

#### Methods

- `trigger_update(container_name: str) -> bool`: Trigger container update
- `check_watchtower_status() -> Dict`: Check Watchtower status
- `configure_container_labels(container_name: str, enable: bool) -> bool`: Configure labels

### HealthChecker

Performs health checks.

```python
from safe_auto_updater.execution import HealthChecker

checker = HealthChecker(retry_count=3, retry_delay=5)
healthy = checker.check_health(asset)
```

#### Methods

- `check_health(asset: Dict) -> bool`: Perform health check
- `check_endpoint(url: str, expected_status: int) -> bool`: Check HTTP endpoint

## Utilities Module

### ConfigLoader

Loads and manages configuration.

```python
from safe_auto_updater.utils import ConfigLoader

loader = ConfigLoader("config.yaml")
config = loader.load_config()
value = loader.get("inventory.docker.enabled", default=True)
```

#### Methods

- `load_config(config_path: Optional[str]) -> Dict`: Load configuration
- `get(key: str, default: Any) -> Any`: Get configuration value
- `validate_config() -> bool`: Validate configuration

### Logger Setup

Configure logging.

```python
from safe_auto_updater.utils import setup_logging

setup_logging(level="INFO", log_file="/var/log/updater.log")
```

## Examples

### Complete Update Workflow

```python
from safe_auto_updater import AssetInventory, ChangeDetector, UpdateExecutor
from safe_auto_updater.detection import SemVerEvaluator, DiffAnalyzer
from safe_auto_updater.execution import HelmUpdater, HealthChecker

# Initialize components
inventory = AssetInventory()
evaluator = SemVerEvaluator()
analyzer = DiffAnalyzer()
detector = ChangeDetector(evaluator, analyzer)

helm_updater = HelmUpdater()
health_checker = HealthChecker()
executor = UpdateExecutor(helm_updater, None, health_checker)

# Scan assets
# ... add assets to inventory ...

# Detect and execute updates
for asset in inventory.get_assets()["helm"]:
    update = detector.detect_updates(asset)
    if update and detector.check_update_safety(update):
        executor.execute_update(asset, update)
```
