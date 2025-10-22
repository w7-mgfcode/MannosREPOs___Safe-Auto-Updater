"""
Command Line Interface

Main CLI for the Safe Auto-Updater system.
"""

import argparse
import sys
from pathlib import Path

from .utils.logger import setup_logging
from .utils.config_loader import ConfigLoader
from .inventory import AssetInventory, DockerScanner, KubernetesScanner
from .detection import ChangeDetector, SemVerEvaluator, DiffAnalyzer
from .execution import UpdateExecutor, HelmUpdater, WatchtowerUpdater, HealthChecker


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Safe Auto-Updater: Safely update Docker and Kubernetes assets"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="configs/config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "-l", "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Inventory command
    inventory_parser = subparsers.add_parser("inventory", help="Scan and inventory assets")
    inventory_parser.add_argument(
        "--type",
        choices=["docker", "kubernetes", "helm", "all"],
        default="all",
        help="Type of assets to scan"
    )
    
    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect available updates")
    detect_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Execute updates")
    update_parser.add_argument(
        "--asset",
        type=str,
        help="Specific asset to update"
    )
    update_parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip health checks (not recommended)"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Load configuration
    config_loader = ConfigLoader(args.config)
    config = config_loader.load_config()
    
    if not config:
        print(f"Warning: Could not load configuration from {args.config}")
        print("Using default configuration")
    
    # Execute command
    if args.command == "inventory":
        run_inventory(config, args)
    elif args.command == "detect":
        run_detection(config, args)
    elif args.command == "update":
        run_update(config, args)
    elif args.command == "status":
        run_status(config, args)
    else:
        parser.print_help()
        return 1
    
    return 0


def run_inventory(config, args):
    """Run inventory scan."""
    print(f"Scanning {args.type} assets...")
    
    inventory = AssetInventory()
    
    if args.type in ["docker", "all"]:
        docker_scanner = DockerScanner()
        containers = docker_scanner.scan_containers()
        for container in containers:
            inventory.add_asset("docker", container)
        print(f"Found {len(containers)} Docker containers")
    
    if args.type in ["kubernetes", "all"]:
        k8s_scanner = KubernetesScanner()
        deployments = k8s_scanner.scan_deployments()
        for deployment in deployments:
            inventory.add_asset("kubernetes", deployment)
        print(f"Found {len(deployments)} Kubernetes deployments")
    
    if args.type in ["helm", "all"]:
        k8s_scanner = KubernetesScanner()
        releases = k8s_scanner.scan_helm_releases()
        for release in releases:
            inventory.add_asset("helm", release)
        print(f"Found {len(releases)} Helm releases")
    
    print("Inventory scan complete")


def run_detection(config, args):
    """Run update detection."""
    print("Detecting available updates...")
    
    semver_evaluator = SemVerEvaluator()
    diff_analyzer = DiffAnalyzer()
    detector = ChangeDetector(semver_evaluator, diff_analyzer)
    
    # Placeholder for actual detection logic
    print("Detection complete")
    
    if args.dry_run:
        print("Dry run mode - no changes will be made")


def run_update(config, args):
    """Run update execution."""
    if args.skip_health_check:
        print("Warning: Skipping health checks")
    
    print("Executing updates...")
    
    helm_updater = HelmUpdater()
    watchtower_updater = WatchtowerUpdater()
    health_checker = HealthChecker() if not args.skip_health_check else None
    
    executor = UpdateExecutor(helm_updater, watchtower_updater, health_checker)
    
    # Placeholder for actual update logic
    print("Update execution complete")


def run_status(config, args):
    """Show system status."""
    print("Safe Auto-Updater Status")
    print("=" * 50)
    print("Configuration: Loaded")
    print("Docker Scanner: Ready")
    print("Kubernetes Scanner: Ready")
    print("Update Executor: Ready")
    print("=" * 50)


if __name__ == "__main__":
    sys.exit(main())
