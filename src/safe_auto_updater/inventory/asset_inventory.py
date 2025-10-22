"""
Asset Inventory Management

Manages the inventory of Docker and Kubernetes assets.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AssetInventory:
    """Manages inventory of Docker and Kubernetes assets."""

    def __init__(self):
        """Initialize the asset inventory."""
        self.assets: Dict[str, List[Dict]] = {
            "docker": [],
            "kubernetes": [],
            "helm": []
        }
        logger.info("AssetInventory initialized")

    def add_asset(self, asset_type: str, asset: Dict) -> None:
        """
        Add an asset to the inventory.

        Args:
            asset_type: Type of asset (docker, kubernetes, helm)
            asset: Asset information dictionary
        """
        if asset_type not in self.assets:
            raise ValueError(f"Invalid asset type: {asset_type}")

        self.assets[asset_type].append(asset)
        logger.info(f"Added {asset_type} asset: {asset.get('name', 'unknown')}")

    def get_assets(self, asset_type: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Retrieve assets from inventory.

        Args:
            asset_type: Optional filter by asset type

        Returns:
            Dictionary of assets
        """
        if asset_type:
            return {asset_type: self.assets.get(asset_type, [])}
        return self.assets

    def clear(self) -> None:
        """Clear all assets from inventory."""
        self.assets = {
            "docker": [],
            "kubernetes": [],
            "helm": []
        }
        logger.info("Inventory cleared")
