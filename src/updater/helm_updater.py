"""
Helm release updater for safe Kubernetes updates.
"""

import subprocess
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UpdateStatus(str, Enum):
    """Status of update operation."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    ROLLED_BACK = "rolled_back"


@dataclass
class UpdateResult:
    """Result of an update operation."""
    success: bool
    status: UpdateStatus
    message: str
    revision: Optional[int] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


@dataclass
class HelmRelease:
    """Represents a Helm release."""
    name: str
    namespace: str
    revision: int
    updated: str
    status: str
    chart: str
    app_version: str


class HelmUpdater:
    """Safe Helm release updater with validation and rollback."""

    def __init__(self, helm_bin: str = "helm"):
        """
        Initialize Helm updater.

        Args:
            helm_bin: Path to helm binary.

        Raises:
            FileNotFoundError: If helm binary not found.
        """
        self.helm_bin = helm_bin
        self._verify_helm()

    def _verify_helm(self):
        """Verify Helm is installed and accessible."""
        try:
            result = subprocess.run(
                [self.helm_bin, "version", "--short"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise FileNotFoundError("Helm binary found but not functional")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise FileNotFoundError(
                f"Helm not found or not accessible: {e}. "
                "Please install Helm 3.x: https://helm.sh/docs/intro/install/"
            )

    def upgrade(
        self,
        release: str,
        chart: str,
        version: str,
        namespace: str = "default",
        dry_run: bool = False,
        atomic: bool = True,
        timeout: int = 300,
        values: Optional[Dict[str, Any]] = None,
        wait: bool = True
    ) -> UpdateResult:
        """
        Upgrade a Helm release safely.

        Args:
            release: Release name.
            chart: Chart name (e.g., 'stable/nginx').
            version: Chart version to upgrade to.
            namespace: Kubernetes namespace.
            dry_run: Simulate upgrade without applying.
            atomic: Rollback on failure.
            timeout: Timeout in seconds.
            values: Custom values for chart.
            wait: Wait for resources to be ready.

        Returns:
            UpdateResult with operation details.
        """
        start_time = datetime.utcnow()

        # Build helm command
        cmd = [
            self.helm_bin,
            "upgrade",
            "--install",  # Install if doesn't exist
            release,
            chart,
            "--version", version,
            "--namespace", namespace,
            "--timeout", f"{timeout}s",
        ]

        if dry_run:
            cmd.append("--dry-run")

        if atomic and not dry_run:
            cmd.append("--atomic")

        if wait and not dry_run:
            cmd.append("--wait")

        # Add custom values if provided
        if values:
            # Create temporary values file
            import tempfile
            import yaml
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(values, f)
                cmd.extend(['--values', f.name])

        # Execute upgrade
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10  # Add buffer to timeout
            )

            duration = (datetime.utcnow() - start_time).total_seconds()

            if result.returncode == 0:
                # Get new revision
                revision = self._get_current_revision(release, namespace)

                return UpdateResult(
                    success=True,
                    status=UpdateStatus.SUCCESS,
                    message=f"Successfully upgraded {release} to {version}",
                    revision=revision,
                    duration_seconds=duration
                )
            else:
                return UpdateResult(
                    success=False,
                    status=UpdateStatus.FAILED,
                    message=f"Upgrade failed: {result.stderr}",
                    error=result.stderr,
                    duration_seconds=duration
                )

        except subprocess.TimeoutExpired:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"Upgrade timed out after {timeout} seconds",
                error="Timeout",
                duration_seconds=timeout
            )
        except Exception as e:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"Unexpected error during upgrade: {str(e)}",
                error=str(e)
            )

    def get_release_history(
        self,
        release: str,
        namespace: str = "default",
        max_revisions: int = 10
    ) -> List[HelmRelease]:
        """
        Get release history.

        Args:
            release: Release name.
            namespace: Kubernetes namespace.
            max_revisions: Maximum number of revisions to return.

        Returns:
            List of HelmRelease objects.
        """
        cmd = [
            self.helm_bin,
            "history",
            release,
            "--namespace", namespace,
            "--output", "json",
            "--max", str(max_revisions)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                history_data = json.loads(result.stdout)
                return [
                    HelmRelease(
                        name=release,
                        namespace=namespace,
                        revision=item['revision'],
                        updated=item['updated'],
                        status=item['status'],
                        chart=item['chart'],
                        app_version=item['app_version']
                    )
                    for item in history_data
                ]
            else:
                return []

        except Exception as e:
            print(f"Error getting release history: {e}")
            return []

    def get_current_version(
        self,
        release: str,
        namespace: str = "default"
    ) -> Optional[str]:
        """
        Get current chart version of a release.

        Args:
            release: Release name.
            namespace: Kubernetes namespace.

        Returns:
            Current chart version or None if not found.
        """
        cmd = [
            self.helm_bin,
            "list",
            "--filter", release,
            "--namespace", namespace,
            "--output", "json"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout:
                releases = json.loads(result.stdout)
                if releases:
                    # Chart version is in format "chart-version"
                    chart_info = releases[0].get('chart', '')
                    # Extract version (e.g., "nginx-1.2.3" -> "1.2.3")
                    parts = chart_info.rsplit('-', 1)
                    if len(parts) == 2:
                        return parts[1]

            return None

        except Exception as e:
            print(f"Error getting current version: {e}")
            return None

    def _get_current_revision(
        self,
        release: str,
        namespace: str = "default"
    ) -> Optional[int]:
        """Get current revision number."""
        cmd = [
            self.helm_bin,
            "list",
            "--filter", release,
            "--namespace", namespace,
            "--output", "json"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and result.stdout:
                releases = json.loads(result.stdout)
                if releases:
                    return releases[0].get('revision')

            return None

        except Exception:
            return None

    def validate_upgrade(
        self,
        release: str,
        chart: str,
        version: str,
        namespace: str = "default"
    ) -> tuple[bool, str]:
        """
        Validate if upgrade is possible.

        Args:
            release: Release name.
            chart: Chart name.
            version: Target version.
            namespace: Kubernetes namespace.

        Returns:
            Tuple of (is_valid, message).
        """
        # Check if chart and version exist
        cmd = [
            self.helm_bin,
            "search", "repo",
            chart,
            "--version", version,
            "--output", "json"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                search_results = json.loads(result.stdout) if result.stdout else []
                if not search_results:
                    return False, f"Chart {chart} version {version} not found in repositories"

            # Check if release exists (optional - upgrade --install handles this)
            current_version = self.get_current_version(release, namespace)

            if current_version:
                return True, f"Release {release} found with version {current_version}, ready to upgrade"
            else:
                return True, f"Release {release} not found, will be installed"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def rollback(
        self,
        release: str,
        namespace: str = "default",
        revision: Optional[int] = None,
        wait: bool = True,
        timeout: int = 300
    ) -> UpdateResult:
        """
        Rollback a release to a previous revision.

        Args:
            release: Release name.
            namespace: Kubernetes namespace.
            revision: Specific revision to rollback to (0 = previous).
            wait: Wait for rollback to complete.
            timeout: Timeout in seconds.

        Returns:
            UpdateResult with operation details.
        """
        start_time = datetime.utcnow()

        cmd = [
            self.helm_bin,
            "rollback",
            release,
            "--namespace", namespace,
            "--timeout", f"{timeout}s"
        ]

        if revision is not None and revision > 0:
            cmd.append(str(revision))

        if wait:
            cmd.append("--wait")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )

            duration = (datetime.utcnow() - start_time).total_seconds()

            if result.returncode == 0:
                new_revision = self._get_current_revision(release, namespace)

                return UpdateResult(
                    success=True,
                    status=UpdateStatus.ROLLED_BACK,
                    message=f"Successfully rolled back {release}",
                    revision=new_revision,
                    duration_seconds=duration
                )
            else:
                return UpdateResult(
                    success=False,
                    status=UpdateStatus.FAILED,
                    message=f"Rollback failed: {result.stderr}",
                    error=result.stderr,
                    duration_seconds=duration
                )

        except subprocess.TimeoutExpired:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"Rollback timed out after {timeout} seconds",
                error="Timeout",
                duration_seconds=timeout
            )
        except Exception as e:
            return UpdateResult(
                success=False,
                status=UpdateStatus.FAILED,
                message=f"Unexpected error during rollback: {str(e)}",
                error=str(e)
            )
