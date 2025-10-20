"""
State management for tracked assets.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class AssetType(str, Enum):
    """Types of managed assets."""
    DOCKER_CONTAINER = "docker_container"
    K8S_DEPLOYMENT = "k8s_deployment"
    K8S_STATEFULSET = "k8s_statefulset"
    K8S_DAEMONSET = "k8s_daemonset"
    HELM_RELEASE = "helm_release"


class AssetStatus(str, Enum):
    """Status of managed assets."""
    ACTIVE = "active"
    UPDATING = "updating"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    UNKNOWN = "unknown"


@dataclass
class Asset:
    """Represents a managed asset."""
    id: str
    name: str
    asset_type: AssetType
    namespace: Optional[str]
    current_version: str
    image: str
    status: AssetStatus
    last_updated: str
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Asset':
        """Create from dictionary."""
        return cls(**data)


class StateManager:
    """Manages state of all tracked assets."""

    def __init__(self, state_file: str = ".safe-updater-state.json"):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file for persistence.
        """
        self.state_file = Path(state_file)
        self.assets: Dict[str, Asset] = {}
        self._load_state()

    def _load_state(self):
        """Load state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.assets = {
                        asset_id: Asset.from_dict(asset_data)
                        for asset_id, asset_data in data.get('assets', {}).items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load state file: {e}")
                self.assets = {}

    def _save_state(self):
        """Save state to disk."""
        data = {
            'assets': {
                asset_id: asset.to_dict()
                for asset_id, asset in self.assets.items()
            },
            'last_saved': datetime.utcnow().isoformat()
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def add_asset(self, asset: Asset) -> None:
        """
        Add or update an asset.

        Args:
            asset: Asset to add or update.
        """
        self.assets[asset.id] = asset
        self._save_state()

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        Get asset by ID.

        Args:
            asset_id: Asset identifier.

        Returns:
            Asset if found, None otherwise.
        """
        return self.assets.get(asset_id)

    def remove_asset(self, asset_id: str) -> bool:
        """
        Remove an asset.

        Args:
            asset_id: Asset identifier.

        Returns:
            True if removed, False if not found.
        """
        if asset_id in self.assets:
            del self.assets[asset_id]
            self._save_state()
            return True
        return False

    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        namespace: Optional[str] = None,
        status: Optional[AssetStatus] = None
    ) -> List[Asset]:
        """
        List assets with optional filters.

        Args:
            asset_type: Filter by asset type.
            namespace: Filter by namespace.
            status: Filter by status.

        Returns:
            List of matching assets.
        """
        assets = list(self.assets.values())

        if asset_type:
            assets = [a for a in assets if a.asset_type == asset_type]

        if namespace:
            assets = [a for a in assets if a.namespace == namespace]

        if status:
            assets = [a for a in assets if a.status == status]

        return assets

    def update_status(self, asset_id: str, status: AssetStatus) -> bool:
        """
        Update asset status.

        Args:
            asset_id: Asset identifier.
            status: New status.

        Returns:
            True if updated, False if asset not found.
        """
        asset = self.get_asset(asset_id)
        if asset:
            asset.status = status
            asset.last_updated = datetime.utcnow().isoformat()
            self._save_state()
            return True
        return False

    def update_version(self, asset_id: str, new_version: str) -> bool:
        """
        Update asset version.

        Args:
            asset_id: Asset identifier.
            new_version: New version string.

        Returns:
            True if updated, False if asset not found.
        """
        asset = self.get_asset(asset_id)
        if asset:
            asset.current_version = new_version
            asset.last_updated = datetime.utcnow().isoformat()
            self._save_state()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about managed assets.

        Returns:
            Dictionary with statistics.
        """
        total = len(self.assets)
        by_type = {}
        by_status = {}

        for asset in self.assets.values():
            by_type[asset.asset_type.value] = by_type.get(asset.asset_type.value, 0) + 1
            by_status[asset.status.value] = by_status.get(asset.status.value, 0) + 1

        return {
            'total_assets': total,
            'by_type': by_type,
            'by_status': by_status
        }
