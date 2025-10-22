"""
Rollback manager for automatic failure recovery.
"""

import time
import json
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from ..config.schema import RollbackConfig
from ..health.health_checker import HealthCheckResult, HealthStatus
from ..updater.helm_updater import HelmUpdater, UpdateResult


@dataclass
class RollbackEvent:
    """Record of a rollback event."""
    timestamp: str
    asset_id: str
    asset_name: str
    namespace: str
    reason: str
    from_version: str
    to_version: Optional[str]
    success: bool
    duration_seconds: float
    health_before: Optional[dict] = None
    health_after: Optional[dict] = None


class RollbackManager:
    """Manages automatic and manual rollbacks with loop prevention."""

    def __init__(
        self,
        config: RollbackConfig,
        helm_updater: Optional[HelmUpdater] = None,
        audit_file: str = ".rollback-audit.json"
    ):
        """
        Initialize rollback manager.

        Args:
            config: Rollback configuration.
            helm_updater: Helm updater instance.
            audit_file: Path to audit log file.
        """
        self.config = config
        self.helm_updater = helm_updater or HelmUpdater()
        self.audit_file = Path(audit_file)
        self._rollback_history: List[RollbackEvent] = []
        self._load_history()

    def _load_history(self):
        """Load rollback history from audit file."""
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._rollback_history = [
                        RollbackEvent(**event) for event in data.get('events', [])
                    ]
            except Exception as e:
                print(f"Warning: Failed to load rollback history: {e}")

    def _save_history(self):
        """Save rollback history to audit file."""
        try:
            self.audit_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'events': [asdict(event) for event in self._rollback_history],
                    'last_saved': datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving rollback history: {e}")

    def should_rollback(self, health: HealthCheckResult) -> bool:
        """
        Determine if rollback should be triggered based on health.

        Args:
            health: Current health check result.

        Returns:
            True if rollback should be triggered.
        """
        if not self.config.auto_rollback:
            return False

        # Check health percentage against threshold
        failure_percentage = self.config.failure_threshold
        current_health = health.health_percentage / 100.0

        if current_health < (1.0 - failure_percentage):
            return True

        # Check if completely unhealthy
        if health.status == HealthStatus.UNHEALTHY:
            return True

        return False

    def rollback_helm(
        self,
        release: str,
        namespace: str = "default",
        revision: Optional[int] = None,
        asset_id: Optional[str] = None,
        reason: str = "Health check failed"
    ) -> UpdateResult:
        """
        Execute Helm rollback.

        Args:
            release: Release name.
            namespace: Kubernetes namespace.
            revision: Specific revision to rollback to (None = previous).
            asset_id: Asset identifier for tracking.
            reason: Reason for rollback.

        Returns:
            UpdateResult from rollback operation.
        """
        # Check if we're in a rollback loop
        if asset_id and self.is_rollback_loop(asset_id):
            print(f"⚠️  Rollback loop detected for {asset_id}. Manual intervention required.")
            return UpdateResult(
                success=False,
                status="failed",
                message="Rollback loop detected - manual intervention required",
                error="Too many recent rollbacks"
            )

        # Check max rollback attempts
        if asset_id:
            recent_count = self.get_rollback_count(asset_id, window=3600)
            if recent_count >= self.config.max_rollback_attempts:
                print(f"⚠️  Max rollback attempts ({self.config.max_rollback_attempts}) reached for {asset_id}")
                return UpdateResult(
                    success=False,
                    status="failed",
                    message="Max rollback attempts reached",
                    error=f"Already rolled back {recent_count} times in the last hour"
                )

        # Execute rollback
        start_time = datetime.utcnow()

        result = self.helm_updater.rollback(
            release=release,
            namespace=namespace,
            revision=revision,
            wait=True,
            timeout=self.config.monitoring_duration
        )

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Record rollback event
        event = RollbackEvent(
            timestamp=datetime.utcnow().isoformat(),
            asset_id=asset_id or f"{namespace}/{release}",
            asset_name=release,
            namespace=namespace,
            reason=reason,
            from_version="unknown",  # Could be enriched
            to_version=str(revision) if revision else "previous",
            success=result.success,
            duration_seconds=duration
        )

        self.record_rollback(event)

        return result

    def record_rollback(self, event: RollbackEvent):
        """
        Record a rollback event in history.

        Args:
            event: RollbackEvent to record.
        """
        self._rollback_history.append(event)

        # Keep only recent history (last 1000 events)
        if len(self._rollback_history) > 1000:
            self._rollback_history = self._rollback_history[-1000:]

        self._save_history()

        # Log to console
        status = "✅ SUCCESS" if event.success else "❌ FAILED"
        print(f"[ROLLBACK {status}] {event.asset_name} in {event.namespace}")
        print(f"  Reason: {event.reason}")
        print(f"  Duration: {event.duration_seconds:.1f}s")

    def get_rollback_count(self, asset_id: str, window: int = 3600) -> int:
        """
        Get number of rollbacks for an asset in a time window.

        Args:
            asset_id: Asset identifier.
            window: Time window in seconds (default: 1 hour).

        Returns:
            Number of rollbacks in the window.
        """
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)

        count = 0
        for event in self._rollback_history:
            if event.asset_id == asset_id:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time > cutoff_time:
                    count += 1

        return count

    def is_rollback_loop(self, asset_id: str, window: int = 3600, threshold: int = 3) -> bool:
        """
        Detect if asset is stuck in an update-rollback loop.

        Args:
            asset_id: Asset identifier.
            window: Time window in seconds.
            threshold: Number of rollbacks indicating a loop.

        Returns:
            True if loop detected.
        """
        recent_count = self.get_rollback_count(asset_id, window)
        return recent_count >= threshold

    def get_rollback_history(
        self,
        asset_id: Optional[str] = None,
        limit: int = 10
    ) -> List[RollbackEvent]:
        """
        Get rollback history.

        Args:
            asset_id: Filter by asset ID (None = all).
            limit: Maximum number of events to return.

        Returns:
            List of RollbackEvent objects.
        """
        if asset_id:
            history = [e for e in self._rollback_history if e.asset_id == asset_id]
        else:
            history = self._rollback_history

        # Return most recent first
        return list(reversed(history[-limit:]))

    def monitor_and_rollback(
        self,
        asset_id: str,
        release: str,
        namespace: str,
        health_checker,
        asset
    ) -> tuple[bool, Optional[UpdateResult]]:
        """
        Monitor health and automatically rollback if needed.

        Args:
            asset_id: Asset identifier.
            release: Release name.
            namespace: Namespace.
            health_checker: HealthChecker instance.
            asset: Asset object.

        Returns:
            Tuple of (stayed_healthy, rollback_result).
        """
        monitoring_duration = self.config.monitoring_duration
        start_time = time.time()

        print(f"⏱️  Monitoring health for {monitoring_duration}s...")

        while time.time() - start_time < monitoring_duration:
            # Check health
            health = health_checker.check_kubernetes(asset)

            print(f"  Health: {health.health_percentage:.1f}% ({health.ready_replicas}/{health.total_replicas} ready)")

            # Check if rollback needed
            if self.should_rollback(health):
                print(f"⚠️  Health threshold breached! Triggering rollback...")

                rollback_result = self.rollback_helm(
                    release=release,
                    namespace=namespace,
                    asset_id=asset_id,
                    reason=f"Health check failed: {health.message}"
                )

                return False, rollback_result

            # If healthy, continue monitoring
            if health.healthy:
                print(f"✅ Healthy!")

            # Wait before next check
            time.sleep(30)  # Check every 30 seconds

        # Monitoring complete without issues
        print(f"✅ Monitoring complete - asset remained healthy")
        return True, None

    def get_statistics(self) -> Dict:
        """
        Get rollback statistics.

        Returns:
            Dictionary with statistics.
        """
        total = len(self._rollback_history)
        successful = sum(1 for e in self._rollback_history if e.success)
        failed = total - successful

        # Recent rollbacks (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = sum(
            1 for e in self._rollback_history
            if datetime.fromisoformat(e.timestamp) > cutoff
        )

        # Group by asset
        by_asset = {}
        for event in self._rollback_history:
            by_asset[event.asset_id] = by_asset.get(event.asset_id, 0) + 1

        return {
            'total_rollbacks': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0.0,
            'recent_24h': recent,
            'by_asset': by_asset
        }
