# Safe Auto-Updater Architecture

## Overview

The Safe Auto-Updater is a production-ready system designed to safely manage updates for Docker and Kubernetes assets with automated health checks and rollback capabilities.

## System Components

### 1. Inventory Module

The inventory module is responsible for discovering and cataloging assets:

- **AssetInventory**: Central registry for all discovered assets
- **DockerScanner**: Scans Docker containers and images
- **KubernetesScanner**: Scans Kubernetes deployments and Helm releases

### 2. Detection Module

The detection module identifies available updates and evaluates their safety:

- **ChangeDetector**: Identifies when updates are available
- **SemVerEvaluator**: Analyzes semantic versioning to determine update type (patch, minor, major)
- **DiffAnalyzer**: Analyzes configuration differences to assess risk

### 3. Execution Module

The execution module safely applies updates with health checks:

- **UpdateExecutor**: Orchestrates the update process
- **HelmUpdater**: Manages Helm release upgrades and rollbacks
- **WatchtowerUpdater**: Triggers Docker container updates via Watchtower
- **HealthChecker**: Performs health checks before and after updates

### 4. Utilities

Common utilities used across the system:

- **ConfigLoader**: Loads and validates configuration files
- **Logger**: Centralized logging configuration

## Data Flow

```
1. Inventory Scan
   └─> Docker/Kubernetes/Helm assets discovered

2. Change Detection
   └─> Available updates identified
   └─> SemVer evaluation performed
   └─> Configuration diffs analyzed

3. Safety Evaluation
   └─> Update safety assessed
   └─> Risk level determined

4. Update Execution
   └─> Pre-update health check
   └─> Update applied
   └─> Post-update health check
   └─> Rollback if health check fails

5. Monitoring & Reporting
   └─> Status updates
   └─> Notifications (optional)
```

## Configuration

The system is configured via YAML files with the following sections:

- **inventory**: Asset scanning settings
- **detection**: Update detection and evaluation rules
- **execution**: Update execution and health check settings
- **notifications**: Optional notification configuration

## Deployment Options

### Docker Compose

Deploy as a Docker container alongside Watchtower for Docker container updates.

### Kubernetes

Deploy as a Kubernetes Deployment with RBAC permissions for cluster management.

### Helm Chart

Deploy using Helm for simplified configuration and management.

## Safety Features

1. **SemVer-Based Updates**: Only apply updates that match configured version policies
2. **Configuration Diff Analysis**: Analyze configuration changes before applying
3. **Health Checks**: Verify application health before and after updates
4. **Automatic Rollback**: Roll back failed updates automatically
5. **Dry Run Mode**: Preview updates without applying changes

## Extension Points

The system is designed to be extensible:

- Custom health check implementations
- Additional asset scanners
- Custom notification handlers
- Policy-based update rules
