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


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()
