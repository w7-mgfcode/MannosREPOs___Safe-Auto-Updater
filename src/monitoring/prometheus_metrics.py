"""
Prometheus metrics collector for Safe Auto-Updater.

This module provides comprehensive metrics for monitoring:
- Asset inventory and status
- Update operations and outcomes
- Health check results
- System performance
"""

from typing import Dict, Optional
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST
)
import time


class MetricsCollector:
    """
    Central metrics collector for Safe Auto-Updater.
    
    Provides Prometheus metrics for all system operations including:
    - Asset discovery and tracking
    - Update operations (success/failure/rollback)
    - Health checks
    - Performance metrics
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics collector.
        
        Args:
            registry: Prometheus registry (creates new if None)
        """
        self.registry = registry or CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup all Prometheus metrics."""
        
        # ===== ASSET METRICS =====
        self.assets_total = Gauge(
            'safe_updater_assets_total',
            'Total number of tracked assets',
            ['type', 'namespace'],
            registry=self.registry
        )
        
        self.assets_by_status = Gauge(
            'safe_updater_assets_by_status',
            'Assets grouped by status',
            ['status', 'type'],
            registry=self.registry
        )
        
        self.asset_versions = Info(
            'safe_updater_asset_version',
            'Current version of tracked assets',
            registry=self.registry
        )
        
        # ===== SCAN METRICS =====
        self.scans_total = Counter(
            'safe_updater_scans_total',
            'Total number of asset scans',
            ['type', 'status'],
            registry=self.registry
        )
        
        self.scan_duration = Histogram(
            'safe_updater_scan_duration_seconds',
            'Duration of asset scans',
            ['type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.scan_assets_discovered = Counter(
            'safe_updater_scan_assets_discovered_total',
            'Total assets discovered during scans',
            ['type'],
            registry=self.registry
        )
        
        # ===== UPDATE METRICS =====
        self.updates_evaluated = Counter(
            'safe_updater_updates_evaluated_total',
            'Total updates evaluated',
            ['change_type', 'decision'],
            registry=self.registry
        )
        
        self.updates_applied = Counter(
            'safe_updater_updates_applied_total',
            'Total updates applied',
            ['type', 'status'],
            registry=self.registry
        )
        
        self.update_duration = Histogram(
            'safe_updater_update_duration_seconds',
            'Duration of update operations',
            ['type'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0],
            registry=self.registry
        )
        
        self.version_changes = Counter(
            'safe_updater_version_changes_total',
            'Version changes by type',
            ['change_type', 'asset_type'],
            registry=self.registry
        )
        
        # ===== HEALTH CHECK METRICS =====
        self.health_checks_total = Counter(
            'safe_updater_health_checks_total',
            'Total health checks performed',
            ['type', 'status'],
            registry=self.registry
        )
        
        self.health_check_duration = Summary(
            'safe_updater_health_check_duration_seconds',
            'Duration of health checks',
            ['type'],
            registry=self.registry
        )
        
        self.health_check_failures = Counter(
            'safe_updater_health_check_failures_total',
            'Total health check failures',
            ['type', 'reason'],
            registry=self.registry
        )
        
        # ===== ROLLBACK METRICS =====
        self.rollbacks_total = Counter(
            'safe_updater_rollbacks_total',
            'Total rollback operations',
            ['reason', 'status'],
            registry=self.registry
        )
        
        self.rollback_duration = Histogram(
            'safe_updater_rollback_duration_seconds',
            'Duration of rollback operations',
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0],
            registry=self.registry
        )
        
        # ===== POLICY METRICS =====
        self.policy_violations = Counter(
            'safe_updater_policy_violations_total',
            'Policy violations detected',
            ['policy_type', 'severity'],
            registry=self.registry
        )
        
        self.gate_decisions = Counter(
            'safe_updater_gate_decisions_total',
            'Update gate decisions',
            ['gate_type', 'decision'],
            registry=self.registry
        )
        
        # ===== SYSTEM METRICS =====
        self.system_info = Info(
            'safe_updater_system',
            'System information',
            registry=self.registry
        )
        
        self.last_scan_timestamp = Gauge(
            'safe_updater_last_scan_timestamp',
            'Timestamp of last successful scan',
            ['type'],
            registry=self.registry
        )
        
        self.errors_total = Counter(
            'safe_updater_errors_total',
            'Total errors encountered',
            ['component', 'error_type'],
            registry=self.registry
        )
        
        self.api_requests_total = Counter(
            'safe_updater_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'safe_updater_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
    
    # ===== ASSET TRACKING METHODS =====
    
    def record_assets(self, asset_type: str, namespace: str, count: int):
        """Record total assets of a specific type."""
        self.assets_total.labels(type=asset_type, namespace=namespace).set(count)
    
    def record_asset_status(self, status: str, asset_type: str, count: int):
        """Record assets by status."""
        self.assets_by_status.labels(status=status, type=asset_type).set(count)
    
    # ===== SCAN TRACKING METHODS =====
    
    def record_scan_start(self, scan_type: str) -> float:
        """Record scan start and return start time."""
        return time.time()
    
    def record_scan_complete(self, scan_type: str, start_time: float, 
                            status: str, assets_found: int):
        """Record scan completion with metrics."""
        duration = time.time() - start_time
        self.scans_total.labels(type=scan_type, status=status).inc()
        self.scan_duration.labels(type=scan_type).observe(duration)
        self.scan_assets_discovered.labels(type=scan_type).inc(assets_found)
        self.last_scan_timestamp.labels(type=scan_type).set(time.time())
    
    # ===== UPDATE TRACKING METHODS =====
    
    def record_update_evaluation(self, change_type: str, decision: str):
        """Record update evaluation decision."""
        self.updates_evaluated.labels(
            change_type=change_type,
            decision=decision
        ).inc()
    
    def record_version_change(self, change_type: str, asset_type: str):
        """Record version change by type."""
        self.version_changes.labels(
            change_type=change_type,
            asset_type=asset_type
        ).inc()
    
    def record_update_start(self, update_type: str) -> float:
        """Record update start and return start time."""
        return time.time()
    
    def record_update_complete(self, update_type: str, start_time: float, 
                              status: str):
        """Record update completion."""
        duration = time.time() - start_time
        self.updates_applied.labels(type=update_type, status=status).inc()
        self.update_duration.labels(type=update_type).observe(duration)
    
    # ===== HEALTH CHECK METHODS =====
    
    def record_health_check(self, check_type: str, status: str, 
                           duration: float):
        """Record health check execution."""
        self.health_checks_total.labels(type=check_type, status=status).inc()
        self.health_check_duration.labels(type=check_type).observe(duration)
    
    def record_health_check_failure(self, check_type: str, reason: str):
        """Record health check failure."""
        self.health_check_failures.labels(type=check_type, reason=reason).inc()
    
    # ===== ROLLBACK METHODS =====
    
    def record_rollback_start(self) -> float:
        """Record rollback start and return start time."""
        return time.time()
    
    def record_rollback_complete(self, reason: str, status: str, 
                                start_time: float):
        """Record rollback completion."""
        duration = time.time() - start_time
        self.rollbacks_total.labels(reason=reason, status=status).inc()
        self.rollback_duration.observe(duration)
    
    # ===== POLICY METHODS =====
    
    def record_policy_violation(self, policy_type: str, severity: str):
        """Record policy violation."""
        self.policy_violations.labels(
            policy_type=policy_type,
            severity=severity
        ).inc()
    
    def record_gate_decision(self, gate_type: str, decision: str):
        """Record update gate decision."""
        self.gate_decisions.labels(gate_type=gate_type, decision=decision).inc()
    
    # ===== SYSTEM METHODS =====
    
    def set_system_info(self, version: str, python_version: str, 
                       hostname: str):
        """Set system information."""
        self.system_info.info({
            'version': version,
            'python_version': python_version,
            'hostname': hostname
        })
    
    def record_error(self, component: str, error_type: str):
        """Record system error."""
        self.errors_total.labels(
            component=component,
            error_type=error_type
        ).inc()
    
    # ===== API METHODS =====
    
    def record_api_request(self, method: str, endpoint: str, status: int, 
                          duration: float):
        """Record API request metrics."""
        self.api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        self.api_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    # ===== EXPORT METHODS =====
    
    def generate_metrics(self) -> bytes:
        """Generate Prometheus metrics in text format."""
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """Get Prometheus content type."""
        return CONTENT_TYPE_LATEST
    
    def reset(self):
        """Reset all metrics (useful for testing)."""
        # Note: Counters cannot be reset in Prometheus, only recreate registry
        pass


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def init_metrics_collector(registry: Optional[CollectorRegistry] = None) -> MetricsCollector:
    """Initialize global metrics collector with custom registry."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(registry)
    return _metrics_collector
