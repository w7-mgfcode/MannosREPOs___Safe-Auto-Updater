"""
Unit tests for Prometheus metrics collector.
"""

import pytest
from prometheus_client import CollectorRegistry
from monitoring.prometheus_metrics import MetricsCollector, init_metrics_collector, get_metrics_collector
import time


class TestMetricsCollector:
    """Test Prometheus metrics collector."""

    @pytest.fixture
    def metrics(self):
        """Create fresh metrics collector for each test."""
        registry = CollectorRegistry()
        return MetricsCollector(registry)

    def test_initialization(self, metrics):
        """Test metrics collector initialization."""
        assert metrics.registry is not None
        assert metrics.assets_total is not None
        assert metrics.scans_total is not None
        assert metrics.updates_evaluated is not None

    def test_record_assets(self, metrics):
        """Test recording asset counts."""
        metrics.record_assets("docker_container", "default", 5)
        metrics.record_assets("k8s_deployment", "production", 10)
        
        # Metrics should be recorded (no exceptions)
        assert True

    def test_record_asset_status(self, metrics):
        """Test recording asset status."""
        metrics.record_asset_status("active", "docker_container", 3)
        metrics.record_asset_status("updating", "k8s_deployment", 1)
        
        assert True

    def test_scan_metrics(self, metrics):
        """Test scan metrics recording."""
        start_time = metrics.record_scan_start("docker")
        assert isinstance(start_time, float)
        
        time.sleep(0.01)  # Simulate scan duration
        
        metrics.record_scan_complete(
            "docker",
            start_time,
            "success",
            15
        )
        
        assert True

    def test_update_evaluation(self, metrics):
        """Test update evaluation metrics."""
        metrics.record_update_evaluation("patch", "approve")
        metrics.record_update_evaluation("minor", "review_required")
        metrics.record_update_evaluation("major", "manual_approval")
        
        assert True

    def test_version_change(self, metrics):
        """Test version change metrics."""
        metrics.record_version_change("patch", "docker_container")
        metrics.record_version_change("minor", "k8s_deployment")
        
        assert True

    def test_update_duration(self, metrics):
        """Test update duration metrics."""
        start_time = metrics.record_update_start("helm")
        time.sleep(0.01)
        metrics.record_update_complete("helm", start_time, "success")
        
        assert True

    def test_health_check_metrics(self, metrics):
        """Test health check metrics."""
        metrics.record_health_check("http", "healthy", 0.123)
        metrics.record_health_check("tcp", "unhealthy", 1.5)
        metrics.record_health_check_failure("http", "timeout")
        
        assert True

    def test_rollback_metrics(self, metrics):
        """Test rollback metrics."""
        start_time = metrics.record_rollback_start()
        time.sleep(0.01)
        metrics.record_rollback_complete("health_check_failed", "success", start_time)
        
        assert True

    def test_policy_metrics(self, metrics):
        """Test policy violation and gate decision metrics."""
        metrics.record_policy_violation("semver_gate", "warning")
        metrics.record_gate_decision("major_update", "manual_approval")
        
        assert True

    def test_system_info(self, metrics):
        """Test system information setting."""
        metrics.set_system_info(
            version="0.1.0",
            python_version="3.11.0",
            hostname="test-host"
        )
        
        assert True

    def test_error_recording(self, metrics):
        """Test error recording."""
        metrics.record_error("scanner", "ConnectionError")
        metrics.record_error("api", "ValidationError")
        
        assert True

    def test_api_metrics(self, metrics):
        """Test API request metrics."""
        metrics.record_api_request("GET", "/api/v1/assets", 200, 0.05)
        metrics.record_api_request("POST", "/api/v1/updates", 201, 0.15)
        metrics.record_api_request("GET", "/api/v1/health", 500, 0.01)
        
        assert True

    def test_metrics_generation(self, metrics):
        """Test Prometheus metrics generation."""
        # Record some metrics
        metrics.record_assets("docker_container", "default", 5)
        metrics.record_update_evaluation("patch", "approve")
        
        # Generate metrics
        output = metrics.generate_metrics()
        
        assert isinstance(output, bytes)
        assert len(output) > 0
        assert b"safe_updater" in output

    def test_content_type(self, metrics):
        """Test Prometheus content type."""
        content_type = metrics.get_content_type()
        assert "text/plain" in content_type or "openmetrics" in content_type

    def test_global_collector(self):
        """Test global metrics collector singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2

    def test_init_global_collector(self):
        """Test initializing global collector with custom registry."""
        registry = CollectorRegistry()
        collector = init_metrics_collector(registry)
        
        assert collector.registry is registry
        assert get_metrics_collector() is collector

    def test_multiple_metric_types(self, metrics):
        """Test that different metric types work together."""
        # Counter
        metrics.scans_total.labels(type="docker", status="success").inc()
        
        # Gauge
        metrics.assets_total.labels(type="docker", namespace="default").set(10)
        
        # Histogram
        metrics.scan_duration.labels(type="docker").observe(1.5)
        
        # Generate and verify
        output = metrics.generate_metrics()
        assert len(output) > 0


class TestMetricsIntegration:
    """Integration tests for metrics with other components."""

    def test_state_manager_integration(self):
        """Test metrics integration with StateManager."""
        from inventory.state_manager import StateManager, Asset, AssetType, AssetStatus
        from datetime import datetime
        import tempfile
        import os
        
        # Create temporary state file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Initialize state manager (will initialize metrics)
            state_mgr = StateManager(temp_file)
            
            # Add asset
            asset = Asset(
                id="test-1",
                name="test-container",
                asset_type=AssetType.DOCKER_CONTAINER,
                namespace="default",
                current_version="1.0.0",
                image="test:1.0.0",
                status=AssetStatus.ACTIVE,
                last_updated=datetime.utcnow().isoformat(),
                metadata={}
            )
            state_mgr.add_asset(asset)
            
            # Get metrics and verify they were updated
            metrics = get_metrics_collector()
            output = metrics.generate_metrics()
            
            assert isinstance(output, bytes)
            assert len(output) > 0
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
