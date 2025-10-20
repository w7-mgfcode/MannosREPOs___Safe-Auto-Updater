"""
Python client example for Safe Auto-Updater API.

This script demonstrates how to interact with the Safe Auto-Updater REST API
for managing container updates programmatically.
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class SafeUpdaterClient:
    """Client for Safe Auto-Updater REST API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if api_key:
            self.session.headers['X-API-Key'] = api_key
    
    # ===== Health & Status =====
    
    def get_health(self) -> Dict[str, Any]:
        """Get system health status."""
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def get_version(self) -> Dict[str, str]:
        """Get version information."""
        response = self.session.get(f"{self.base_url}/api/v1/version")
        response.raise_for_status()
        return response.json()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        response = self.session.get(f"{self.base_url}/api/v1/config")
        response.raise_for_status()
        return response.json()
    
    # ===== Asset Management =====
    
    def list_assets(
        self,
        asset_type: Optional[str] = None,
        namespace: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        List assets with optional filtering.
        
        Args:
            asset_type: Filter by asset type (docker, kubernetes, helm)
            namespace: Filter by namespace
            status: Filter by status
            page: Page number
            page_size: Items per page
        
        Returns:
            Dictionary with assets list and pagination info
        """
        params = {'page': page, 'page_size': page_size}
        
        if asset_type:
            params['asset_type'] = asset_type
        if namespace:
            params['namespace'] = namespace
        if status:
            params['status'] = status
        
        response = self.session.get(
            f"{self.base_url}/api/v1/assets/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get details of a specific asset."""
        response = self.session.get(f"{self.base_url}/api/v1/assets/{asset_id}")
        response.raise_for_status()
        return response.json()
    
    def get_asset_stats(self) -> Dict[str, Any]:
        """Get asset statistics."""
        response = self.session.get(f"{self.base_url}/api/v1/assets/stats")
        response.raise_for_status()
        return response.json()
    
    # ===== Update Operations =====
    
    def evaluate_update(
        self,
        current_version: str,
        new_version: str,
        asset_id: Optional[str] = None,
        asset_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate whether an update should be applied.
        
        Args:
            current_version: Current version string
            new_version: New version string
            asset_id: Optional asset ID
            asset_type: Optional asset type
        
        Returns:
            Evaluation result with decision and reasoning
        """
        data = {
            'current_version': current_version,
            'new_version': new_version
        }
        
        if asset_id:
            data['asset_id'] = asset_id
        if asset_type:
            data['asset_type'] = asset_type
        
        response = self.session.post(
            f"{self.base_url}/api/v1/updates/evaluate",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def scan_assets(
        self,
        docker: bool = True,
        kubernetes: bool = True,
        namespace: str = "default",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Trigger asset scanning.
        
        Args:
            docker: Scan Docker containers
            kubernetes: Scan Kubernetes resources
            namespace: Kubernetes namespace to scan
            force_refresh: Force refresh cached data
        
        Returns:
            Scan results with discovered assets count
        """
        data = {
            'docker': docker,
            'kubernetes': kubernetes,
            'namespace': namespace,
            'force_refresh': force_refresh
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/updates/scan",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def apply_update(
        self,
        asset_id: str,
        target_version: str,
        force: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply an update to an asset.
        
        Args:
            asset_id: Asset identifier
            target_version: Target version to update to
            force: Force update even if not recommended
            dry_run: Perform dry run without actual update
        
        Returns:
            Update operation result
        """
        data = {
            'asset_id': asset_id,
            'target_version': target_version,
            'force': force,
            'dry_run': dry_run
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/updates/apply",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_update_history(
        self,
        asset_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get update history.
        
        Args:
            asset_id: Optional asset ID to filter by
            limit: Maximum number of records
        
        Returns:
            List of update history entries
        """
        params = {'limit': limit}
        if asset_id:
            params['asset_id'] = asset_id
        
        response = self.session.get(
            f"{self.base_url}/api/v1/updates/history",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    # ===== Metrics =====
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        response = self.session.get(f"{self.base_url}/api/v1/metrics")
        response.raise_for_status()
        return response.text


# ===== Example Usage =====

def main():
    """Example usage of the Safe Auto-Updater client."""
    
    # Initialize client
    client = SafeUpdaterClient(base_url="http://localhost:8000")
    
    print("=== Safe Auto-Updater API Client Example ===\n")
    
    # 1. Check health
    print("1. Checking system health...")
    health = client.get_health()
    print(f"   Status: {health['status']}")
    print(f"   Uptime: {health['uptime_seconds']:.1f}s")
    print(f"   Components: {len(health['checks'])} checks\n")
    
    # 2. Get version
    print("2. Getting version info...")
    version = client.get_version()
    print(f"   Version: {version['version']}")
    print(f"   Python: {version['python_version']}\n")
    
    # 3. Get statistics
    print("3. Getting asset statistics...")
    stats = client.get_asset_stats()
    print(f"   Total assets: {stats['total_assets']}")
    print(f"   By type: {stats['by_type']}")
    print(f"   By status: {stats['by_status']}\n")
    
    # 4. List assets
    print("4. Listing assets...")
    assets = client.list_assets(page_size=5)
    print(f"   Found {assets['total']} assets")
    for asset in assets['assets'][:3]:
        print(f"   - {asset['name']} ({asset['asset_type']}): {asset['current_version']}")
    print()
    
    # 5. Evaluate updates
    print("5. Evaluating version updates...")
    
    test_cases = [
        ("1.0.0", "1.0.1", "Patch update"),
        ("1.0.0", "1.1.0", "Minor update"),
        ("1.0.0", "2.0.0", "Major update"),
    ]
    
    for current, new, description in test_cases:
        result = client.evaluate_update(current, new)
        print(f"   {description} ({current} → {new}):")
        print(f"     Decision: {result['decision']}")
        print(f"     Safe: {result['safe']}")
        print(f"     Reason: {result['reason']}")
    print()
    
    # 6. Trigger scan (dry run - no actual scanning)
    print("6. Triggering asset scan...")
    try:
        scan_result = client.scan_assets(
            docker=False,  # Don't actually scan
            kubernetes=False
        )
        print(f"   Status: {scan_result['status']}")
        print(f"   Assets discovered: {scan_result['assets_discovered']}")
        print(f"   Duration: {scan_result['duration_seconds']:.2f}s\n")
    except Exception as e:
        print(f"   Note: Scan may not work if Docker/K8s not configured\n")
    
    # 7. Get metrics
    print("7. Getting Prometheus metrics...")
    metrics = client.get_metrics()
    lines = metrics.split('\n')
    metric_lines = [l for l in lines if l and not l.startswith('#')]
    print(f"   Total metric lines: {len(metric_lines)}")
    print(f"   Sample metrics:")
    for line in metric_lines[:3]:
        print(f"     {line}")
    print()
    
    print("=== Example Complete ===")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Safe Auto-Updater API")
        print("Make sure the server is running: safe-updater serve")
    except Exception as e:
        print(f"ERROR: {e}")
