"""
Update Executor

Orchestrates the execution of updates with safety checks.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class UpdateExecutor:
    """Orchestrates safe execution of updates."""

    def __init__(self, helm_updater=None, watchtower_updater=None, health_checker=None):
        """
        Initialize update executor.

        Args:
            helm_updater: HelmUpdater instance
            watchtower_updater: WatchtowerUpdater instance
            health_checker: HealthChecker instance
        """
        self.helm_updater = helm_updater
        self.watchtower_updater = watchtower_updater
        self.health_checker = health_checker
        logger.info("UpdateExecutor initialized")

    def execute_update(self, asset: Dict, update_info: Dict) -> bool:
        """
        Execute an update for an asset.

        Args:
            asset: Asset information dictionary
            update_info: Update information dictionary

        Returns:
            True if update successful, False otherwise
        """
        asset_type = asset.get("type")
        asset_name = asset.get("name")

        logger.info(f"Executing update for {asset_type} asset: {asset_name}")

        try:
            # Pre-update health check
            if self.health_checker and not self.health_checker.check_health(asset):
                logger.warning(f"Pre-update health check failed for {asset_name}")
                return False

            # Execute update based on asset type
            success = False
            if asset_type == "helm":
                success = self._update_helm(asset, update_info)
            elif asset_type == "docker":
                success = self._update_docker(asset, update_info)
            else:
                logger.error(f"Unsupported asset type: {asset_type}")
                return False

            if not success:
                logger.error(f"Update failed for {asset_name}")
                return False

            # Post-update health check
            if self.health_checker and not self.health_checker.check_health(asset):
                logger.error(f"Post-update health check failed for {asset_name}")
                self._rollback(asset)
                return False

            logger.info(f"Update successful for {asset_name}")
            return True

        except Exception as e:
            logger.error(f"Error executing update: {e}")
            self._rollback(asset)
            return False

    def _update_helm(self, asset: Dict, update_info: Dict) -> bool:
        """
        Update Helm release.

        Args:
            asset: Asset information dictionary
            update_info: Update information dictionary

        Returns:
            True if successful, False otherwise
        """
        if not self.helm_updater:
            logger.error("Helm updater not configured")
            return False

        return self.helm_updater.upgrade_release(
            asset.get("name"),
            update_info.get("version")
        )

    def _update_docker(self, asset: Dict, update_info: Dict) -> bool:
        """
        Update Docker container via Watchtower.

        Args:
            asset: Asset information dictionary
            update_info: Update information dictionary

        Returns:
            True if successful, False otherwise
        """
        if not self.watchtower_updater:
            logger.error("Watchtower updater not configured")
            return False

        return self.watchtower_updater.trigger_update(asset.get("name"))

    def _rollback(self, asset: Dict) -> bool:
        """
        Rollback a failed update.

        Args:
            asset: Asset information dictionary

        Returns:
            True if rollback successful, False otherwise
        """
        asset_type = asset.get("type")
        asset_name = asset.get("name")

        logger.warning(f"Initiating rollback for {asset_name}")

        try:
            if asset_type == "helm" and self.helm_updater:
                return self.helm_updater.rollback_release(asset_name)
            elif asset_type == "docker":
                logger.info("Docker rollback requires manual intervention or restart")
                return False
            else:
                logger.error(f"Unsupported rollback for asset type: {asset_type}")
                return False
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
