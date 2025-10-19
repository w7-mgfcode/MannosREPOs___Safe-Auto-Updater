"""Unit tests for Asset Inventory"""

import pytest
from safe_auto_updater.inventory.asset_inventory import AssetInventory


class TestAssetInventory:
    """Test cases for AssetInventory"""

    def setup_method(self):
        """Setup test fixtures"""
        self.inventory = AssetInventory()

    def test_initialization(self):
        """Test inventory initialization"""
        assert len(self.inventory.assets["docker"]) == 0
        assert len(self.inventory.assets["kubernetes"]) == 0
        assert len(self.inventory.assets["helm"]) == 0

    def test_add_docker_asset(self):
        """Test adding Docker asset"""
        asset = {"name": "test-container", "version": "1.0.0"}
        self.inventory.add_asset("docker", asset)
        assert len(self.inventory.assets["docker"]) == 1
        assert self.inventory.assets["docker"][0]["name"] == "test-container"

    def test_add_kubernetes_asset(self):
        """Test adding Kubernetes asset"""
        asset = {"name": "test-deployment", "version": "1.0.0"}
        self.inventory.add_asset("kubernetes", asset)
        assert len(self.inventory.assets["kubernetes"]) == 1

    def test_add_invalid_asset_type(self):
        """Test adding asset with invalid type"""
        with pytest.raises(ValueError):
            self.inventory.add_asset("invalid", {})

    def test_get_all_assets(self):
        """Test getting all assets"""
        docker_asset = {"name": "test-docker", "version": "1.0.0"}
        k8s_asset = {"name": "test-k8s", "version": "1.0.0"}
        
        self.inventory.add_asset("docker", docker_asset)
        self.inventory.add_asset("kubernetes", k8s_asset)
        
        assets = self.inventory.get_assets()
        assert len(assets["docker"]) == 1
        assert len(assets["kubernetes"]) == 1

    def test_get_assets_by_type(self):
        """Test getting assets by type"""
        docker_asset = {"name": "test-docker", "version": "1.0.0"}
        self.inventory.add_asset("docker", docker_asset)
        
        assets = self.inventory.get_assets("docker")
        assert "docker" in assets
        assert len(assets["docker"]) == 1

    def test_clear_inventory(self):
        """Test clearing inventory"""
        asset = {"name": "test", "version": "1.0.0"}
        self.inventory.add_asset("docker", asset)
        self.inventory.clear()
        
        assert len(self.inventory.assets["docker"]) == 0
        assert len(self.inventory.assets["kubernetes"]) == 0
