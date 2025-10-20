"""
Safe Auto-Updater main entry point and CLI.
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path

from config.policy_loader import load_config
from inventory.state_manager import StateManager
from inventory.docker_scanner import DockerScanner
from inventory.k8s_scanner import KubernetesScanner
from detection.semver_analyzer import SemVerAnalyzer
from detection.diff_gate import DiffGate
from updater.helm_updater import HelmUpdater
from health.health_checker import HealthChecker
from rollback.rollback_manager import RollbackManager

console = Console()


@click.group()
@click.option('--config', '-c', default=None, help='Path to configuration file')
@click.pass_context
def cli(ctx, config):
    """Safe Auto-Updater - Production-ready container update management."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config


@cli.command()
@click.option('--docker/--no-docker', default=True, help='Scan Docker containers')
@click.option('--kubernetes/--no-kubernetes', default=True, help='Scan Kubernetes resources')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace to scan')
@click.pass_context
def scan(ctx, docker, kubernetes, namespace):
    """Scan and inventory Docker and Kubernetes assets."""
    console.print("[bold blue]Starting asset inventory scan...[/bold blue]")

    config = load_config(ctx.obj.get('config_path'))
    state_manager = StateManager()

    total_assets = 0

    # Scan Docker containers
    if docker:
        try:
            console.print("[yellow]Scanning Docker containers...[/yellow]")
            scanner = DockerScanner(
                socket_path=config.docker.socket_path,
                state_manager=state_manager
            )
            docker_assets = scanner.scan_containers(include_stopped=False)
            console.print(f"[green]Found {len(docker_assets)} Docker containers[/green]")
            total_assets += len(docker_assets)
            scanner.close()
        except Exception as e:
            console.print(f"[red]Error scanning Docker: {e}[/red]")

    # Scan Kubernetes resources
    if kubernetes:
        try:
            console.print(f"[yellow]Scanning Kubernetes resources in namespace: {namespace}...[/yellow]")
            k8s_scanner = KubernetesScanner(
                kubeconfig_path=config.kubernetes.kubeconfig_path,
                in_cluster=config.kubernetes.in_cluster,
                namespace=namespace,
                state_manager=state_manager
            )
            k8s_assets = k8s_scanner.scan_all_resources()
            console.print(f"[green]Found {len(k8s_assets)} Kubernetes resources[/green]")
            total_assets += len(k8s_assets)
        except Exception as e:
            console.print(f"[red]Error scanning Kubernetes: {e}[/red]")

    # Display statistics
    stats = state_manager.get_statistics()
    console.print(f"\n[bold green]Total assets discovered: {total_assets}[/bold green]")

    # Create summary table
    table = Table(title="Asset Summary")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="magenta")

    for asset_type, count in stats['by_type'].items():
        table.add_row(asset_type, str(count))

    console.print(table)


@cli.command()
@click.pass_context
def list_assets(ctx):
    """List all tracked assets."""
    state_manager = StateManager()
    assets = state_manager.list_assets()

    if not assets:
        console.print("[yellow]No assets found. Run 'scan' first.[/yellow]")
        return

    table = Table(title="Tracked Assets")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Namespace", style="blue")
    table.add_column("Version", style="green")
    table.add_column("Status", style="yellow")

    for asset in assets:
        table.add_row(
            asset.name,
            asset.asset_type.value,
            asset.namespace or "N/A",
            asset.current_version,
            asset.status.value
        )

    console.print(table)


@cli.command()
@click.argument('current_version')
@click.argument('new_version')
@click.pass_context
def compare(ctx, current_version, new_version):
    """Compare two version strings."""
    analyzer = SemVerAnalyzer()

    console.print(f"\n[bold]Comparing versions:[/bold]")
    console.print(f"  Current: [cyan]{current_version}[/cyan]")
    console.print(f"  New:     [green]{new_version}[/green]\n")

    comparison, change_type = analyzer.compare_versions(current_version, new_version)

    if comparison > 0:
        console.print(f"[green]✓[/green] New version is an upgrade")
        console.print(f"  Change type: [yellow]{change_type.value}[/yellow]")
    elif comparison < 0:
        console.print(f"[red]✗[/red] New version is older")
    else:
        console.print(f"[blue]=[/blue] Versions are equal or unknown")

    # Get detailed version info
    console.print(f"\n[bold]Version Details:[/bold]")
    current_info = analyzer.get_version_info(current_version)
    new_info = analyzer.get_version_info(new_version)

    console.print(f"\nCurrent: {current_info}")
    console.print(f"New:     {new_info}")


@cli.command()
@click.argument('current_version')
@click.argument('new_version')
@click.pass_context
def evaluate(ctx, current_version, new_version):
    """Evaluate if an update should be approved."""
    config = load_config(ctx.obj.get('config_path'))
    diff_gate = DiffGate(semver_gates=config.auto_update.semver_gates)

    result = diff_gate.evaluate_update(current_version, new_version)

    console.print(f"\n[bold]Update Evaluation:[/bold]")
    console.print(f"  Current: [cyan]{current_version}[/cyan]")
    console.print(f"  New:     [green]{new_version}[/green]")
    console.print(f"  Change:  [yellow]{result['change_type']}[/yellow]")

    decision = result['decision']
    if decision == 'approve':
        console.print(f"  Decision: [bold green]✓ APPROVED[/bold green]")
    elif decision == 'review_required':
        console.print(f"  Decision: [bold yellow]⚠ REVIEW REQUIRED[/bold yellow]")
    elif decision == 'manual_approval':
        console.print(f"  Decision: [bold blue]🔍 MANUAL APPROVAL[/bold blue]")
    else:
        console.print(f"  Decision: [bold red]✗ REJECTED[/bold red]")

    console.print(f"  Reason:   {result['reason']}")
    console.print(f"  Safe:     {result['safe']}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Display statistics about tracked assets."""
    state_manager = StateManager()
    stats = state_manager.get_statistics()

    console.print(f"\n[bold]Asset Statistics:[/bold]")
    console.print(f"  Total assets: {stats['total_assets']}")

    if stats['by_type']:
        console.print(f"\n[bold]By Type:[/bold]")
        for asset_type, count in stats['by_type'].items():
            console.print(f"  {asset_type}: {count}")

    if stats['by_status']:
        console.print(f"\n[bold]By Status:[/bold]")
        for status, count in stats['by_status'].items():
            console.print(f"  {status}: {count}")


@cli.command()
@click.option('--output', '-o', help='Output file path')
def generate_config(output):
    """Generate a default configuration file."""
    from config.policy_loader import PolicyLoader
    from config.schema import SafeUpdaterConfig

    default_config = SafeUpdaterConfig()
    loader = PolicyLoader()

    output_path = output or 'config/policy.yaml'

    try:
        loader.save(default_config, output_path)
        console.print(f"[green]✓[/green] Configuration file generated: {output_path}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate config: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config-file', '-c', help='Configuration file to validate')
def validate_config(config_file):
    """Validate configuration file."""
    try:
        config = load_config(config_file)
        console.print(f"[green]✓[/green] Configuration is valid")
        console.print(f"\nLoaded configuration:")
        console.print(f"  Auto-update enabled: {config.auto_update.update_policy.enabled}")
        console.print(f"  Max concurrent updates: {config.auto_update.update_policy.max_concurrent}")
        console.print(f"  Patch updates: {config.auto_update.semver_gates.patch.value}")
        console.print(f"  Minor updates: {config.auto_update.semver_gates.minor.value}")
        console.print(f"  Major updates: {config.auto_update.semver_gates.major.value}")
    except Exception as e:
        console.print(f"[red]✗[/red] Configuration validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--workers', default=1, type=int, help='Number of worker processes')
@click.option('--reload', is_flag=True, help='Enable auto-reload (development)')
@click.pass_context
def serve(ctx, host, port, workers, reload):
    """Start the REST API server."""
    console.print("[bold blue]Starting Safe Auto-Updater API Server...[/bold blue]")
    
    try:
        from api.server import start_server
        
        config_path = ctx.obj.get('config_path')
        
        start_server(
            host=host,
            port=port,
            config_path=config_path,
            reload=reload,
            workers=workers if not reload else 1  # Single worker in reload mode
        )
    except ImportError as e:
        console.print(f"[red]✗[/red] Failed to import API server: {e}")
        console.print("[yellow]Make sure FastAPI and uvicorn are installed:[/yellow]")
        console.print("  pip install 'fastapi>=0.109.0' 'uvicorn[standard]>=0.27.0'")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to start server: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()


@cli.command()
@click.argument('asset_name')
@click.option('--to-version', required=True, help='Target version')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--dry-run', is_flag=True, help='Simulate without executing')
@click.option('--force', is_flag=True, help='Skip policy gates')
@click.option('--wait', is_flag=True, default=True, help='Wait for completion')
@click.option('--timeout', default=300, help='Timeout in seconds')
@click.pass_context
def update(ctx, asset_name, to_version, namespace, dry_run, force, wait, timeout):
    """Execute update for specified asset."""
    console.print(f"[bold blue]Updating {asset_name} to version {to_version}[/bold blue]")

    config = load_config(ctx.obj.get('config_path'))
    state_manager = StateManager()

    # Get asset from inventory
    assets = state_manager.list_assets()
    asset = next((a for a in assets if a.name == asset_name and a.namespace == namespace), None)

    if not asset:
        console.print(f"[red]✗[/red] Asset {asset_name} not found in namespace {namespace}")
        console.print("[yellow]Tip: Run 'safe-updater scan' first to discover assets[/yellow]")
        sys.exit(1)

    # Evaluate policy (unless forced)
    if not force:
        diff_gate = DiffGate(semver_gates=config.auto_update.semver_gates)
        decision = diff_gate.evaluate_update(asset.current_version, to_version)

        console.print(f"\n[bold]Policy Evaluation:[/bold]")
        console.print(f"  Current version: {asset.current_version}")
        console.print(f"  Target version:  {to_version}")
        console.print(f"  Change type:     {decision['change_type']}")
        console.print(f"  Decision:        {decision['decision']}")
        console.print(f"  Reason:          {decision['reason']}")

        if decision['decision'] not in ['approve', 'review_required']:
            console.print(f"\n[red]✗[/red] Update blocked by policy")
            console.print(f"[yellow]Use --force to override (not recommended)[/yellow]")
            sys.exit(10)  # Policy violation exit code
        elif decision['decision'] == 'review_required':
            console.print(f"\n[yellow]⚠[/yellow] Review required but proceeding...")

    # Initialize updater
    try:
        helm_updater = HelmUpdater()
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)

    # Execute update
    console.print(f"\n[yellow]{'Simulating' if dry_run else 'Executing'} Helm upgrade...[/yellow]")

    # Extract chart from asset metadata (if available)
    chart = asset.metadata.get('chart', asset.name)

    result = helm_updater.upgrade(
        release=asset_name,
        chart=chart,
        version=to_version,
        namespace=namespace,
        dry_run=dry_run,
        atomic=True,
        timeout=timeout,
        wait=wait
    )

    if result.success:
        console.print(f"[green]✓[/green] {result.message}")
        console.print(f"  Revision: {result.revision}")
        console.print(f"  Duration: {result.duration_seconds:.1f}s")

        if not dry_run:
            # Update state
            state_manager.update_version(asset.id, to_version)
            state_manager.update_status(asset.id, "active")

            # Health monitoring
            console.print(f"\n[yellow]Monitoring health for {config.auto_update.rollback.monitoring_duration}s...[/yellow]")

            # Initialize health checker
            from kubernetes import client, config as k8s_config
            try:
                if config.kubernetes.in_cluster:
                    k8s_config.load_incluster_config()
                else:
                    k8s_config.load_kube_config(config_file=config.kubernetes.kubeconfig_path)

                apps_api = client.AppsV1Api()
                core_api = client.CoreV1Api()
                health_checker = HealthChecker(k8s_apps_api=apps_api, k8s_core_api=core_api)

                # Create rollback manager
                rollback_manager = RollbackManager(
                    config=config.auto_update.rollback,
                    helm_updater=helm_updater
                )

                # Monitor and potentially rollback
                stayed_healthy, rollback_result = rollback_manager.monitor_and_rollback(
                    asset_id=asset.id,
                    release=asset_name,
                    namespace=namespace,
                    health_checker=health_checker,
                    asset=asset
                )

                if stayed_healthy:
                    console.print(f"[green]✓[/green] Update completed successfully!")
                else:
                    console.print(f"[red]✗[/red] Update failed - rolled back")
                    if rollback_result:
                        console.print(f"  Rollback: {rollback_result.message}")
                    sys.exit(20)  # Health check failed exit code

            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not perform health checks: {e}")
                console.print(f"[green]Update completed, but health monitoring skipped[/green]")
    else:
        console.print(f"[red]✗[/red] {result.message}")
        if result.error:
            console.print(f"  Error: {result.error}")
        sys.exit(4)  # Update error exit code


@cli.command()
@click.argument('asset_name')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--revision', type=int, help='Specific revision to rollback to')
@click.option('--to-version', help='Version to rollback to')
@click.pass_context
def rollback(ctx, asset_name, namespace, revision, to_version):
    """Rollback a failed update."""
    console.print(f"[bold yellow]Rolling back {asset_name}[/bold yellow]")

    # Initialize Helm updater
    try:
        helm_updater = HelmUpdater()
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)

    # Get release history
    console.print(f"\n[cyan]Fetching release history...[/cyan]")
    history = helm_updater.get_release_history(asset_name, namespace, max_revisions=10)

    if not history:
        console.print(f"[red]✗[/red] No release history found for {asset_name}")
        sys.exit(1)

    # Display history
    table = Table(title=f"Release History: {asset_name}")
    table.add_column("Revision", style="cyan")
    table.add_column("Updated", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Chart", style="magenta")
    table.add_column("App Version", style="yellow")

    for rel in reversed(history):
        table.add_row(
            str(rel.revision),
            rel.updated,
            rel.status,
            rel.chart,
            rel.app_version
        )

    console.print(table)

    # Execute rollback
    console.print(f"\n[yellow]Executing rollback...[/yellow]")

    result = helm_updater.rollback(
        release=asset_name,
        namespace=namespace,
        revision=revision,
        wait=True,
        timeout=300
    )

    if result.success:
        console.print(f"[green]✓[/green] {result.message}")
        console.print(f"  New revision: {result.revision}")
        console.print(f"  Duration: {result.duration_seconds:.1f}s")

        # Update state
        state_manager = StateManager()
        state_manager.update_status(f"k8s-deployment-{namespace}-{asset_name}", "active")
    else:
        console.print(f"[red]✗[/red] {result.message}")
        if result.error:
            console.print(f"  Error: {result.error}")
        sys.exit(5)  # Rollback error exit code


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()
