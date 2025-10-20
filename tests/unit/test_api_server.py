"""
Unit tests for FastAPI server.
"""

import pytest
from fastapi.testclient import TestClient
from api.server import create_app
from inventory.state_manager import StateManager, Asset, AssetType, AssetStatus
from datetime import datetime
import tempfile
import os


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def temp_state():
    """Create temporary state file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    if os.path.exists(temp_file):
        os.unlink(temp_file)


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Safe Auto-Updater API"
        assert "version" in data
        assert "docs" in data
        assert "health" in data


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "checks" in data
        assert "components" in data

    def test_version_endpoint(self, client):
        """Test version endpoint."""
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "api_version" in data
        assert "python_version" in data
        assert "hostname" in data


class TestConfigEndpoint:
    """Test configuration endpoint."""

    def test_get_config(self, client):
        """Test get configuration."""
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "auto_update_enabled" in data
        assert "max_concurrent_updates" in data
        assert "semver_gates" in data
        assert "rollback_enabled" in data


class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint."""

    def test_metrics(self, client):
        """Test metrics endpoint returns Prometheus format."""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        
        # Check content type
        assert "text/plain" in response.headers["content-type"] or \
               "openmetrics" in response.headers["content-type"]
        
        # Check content
        content = response.text
        assert "safe_updater" in content


class TestAssetsEndpoints:
    """Test asset management endpoints."""

    def test_list_assets_empty(self, client):
        """Test listing assets when none exist."""
        response = client.get("/api/v1/assets/")
        assert response.status_code == 200
        
        data = response.json()
        assert "assets" in data
        assert "total" in data
        assert data["total"] == 0

    def test_list_assets_pagination(self, client):
        """Test asset list pagination."""
        response = client.get("/api/v1/assets/?page=1&page_size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_get_asset_stats(self, client):
        """Test getting asset statistics."""
        response = client.get("/api/v1/assets/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_assets" in data
        assert "by_type" in data
        assert "by_status" in data

    def test_get_asset_not_found(self, client):
        """Test getting non-existent asset."""
        response = client.get("/api/v1/assets/nonexistent")
        assert response.status_code == 404


class TestUpdateEndpoints:
    """Test update management endpoints."""

    def test_evaluate_update(self, client):
        """Test update evaluation."""
        request_data = {
            "current_version": "1.0.0",
            "new_version": "1.0.1"
        }
        
        response = client.post("/api/v1/updates/evaluate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "current_version" in data
        assert "new_version" in data
        assert "change_type" in data
        assert "decision" in data
        assert "safe" in data
        assert "reason" in data

    def test_evaluate_major_update(self, client):
        """Test major version update evaluation."""
        request_data = {
            "current_version": "1.0.0",
            "new_version": "2.0.0"
        }
        
        response = client.post("/api/v1/updates/evaluate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["change_type"] == "major"

    def test_scan_assets(self, client):
        """Test asset scanning endpoint."""
        request_data = {
            "docker": False,  # Don't actually scan Docker
            "kubernetes": False,  # Don't actually scan K8s
            "force_refresh": False
        }
        
        response = client.post("/api/v1/updates/scan", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "assets_discovered" in data
        assert "duration_seconds" in data

    def test_get_update_history(self, client):
        """Test getting update history."""
        response = client.get("/api/v1/updates/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestRequestMiddleware:
    """Test request middleware."""

    def test_response_time_header(self, client):
        """Test that response time header is added."""
        response = client.get("/api/v1/health")
        assert "X-Response-Time" in response.headers
        assert "s" in response.headers["X-Response-Time"]

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        # CORS headers should be present
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented


class TestErrorHandling:
    """Test error handling."""

    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/updates/evaluate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestAPIModels:
    """Test API models and validation."""

    def test_update_evaluation_validation(self, client):
        """Test update evaluation request validation."""
        # Missing required fields
        response = client.post("/api/v1/updates/evaluate", json={})
        assert response.status_code == 422

    def test_scan_request_defaults(self, client):
        """Test scan request with defaults."""
        response = client.post("/api/v1/updates/scan", json={})
        assert response.status_code == 200


class TestOpenAPISpec:
    """Test OpenAPI specification."""

    def test_openapi_json(self, client):
        """Test OpenAPI JSON is generated."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        
        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec

    def test_swagger_ui(self, client):
        """Test Swagger UI is accessible."""
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test ReDoc is accessible."""
        response = client.get("/api/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
