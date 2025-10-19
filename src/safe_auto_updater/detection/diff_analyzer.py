"""
Diff Analyzer

Analyzes configuration differences to assess update impact.
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class DiffAnalyzer:
    """Analyzes configuration diffs for update impact assessment."""

    def __init__(self):
        """Initialize diff analyzer."""
        logger.info("DiffAnalyzer initialized")

    def analyze_config_diff(self, current_config: Dict, new_config: Dict) -> Dict:
        """
        Analyze differences between configurations.

        Args:
            current_config: Current configuration dictionary
            new_config: New configuration dictionary

        Returns:
            Dictionary containing diff analysis results
        """
        diff_result = {
            "added": [],
            "removed": [],
            "modified": [],
            "risk_level": "unknown"
        }

        try:
            # Analyze added keys
            added_keys = set(new_config.keys()) - set(current_config.keys())
            diff_result["added"] = list(added_keys)

            # Analyze removed keys
            removed_keys = set(current_config.keys()) - set(new_config.keys())
            diff_result["removed"] = list(removed_keys)

            # Analyze modified keys
            common_keys = set(current_config.keys()) & set(new_config.keys())
            for key in common_keys:
                if current_config[key] != new_config[key]:
                    diff_result["modified"].append({
                        "key": key,
                        "old_value": current_config[key],
                        "new_value": new_config[key]
                    })

            # Assess risk level
            diff_result["risk_level"] = self._assess_risk_level(diff_result)

            logger.info(f"Config diff analysis complete: {len(diff_result['added'])} added, "
                       f"{len(diff_result['removed'])} removed, {len(diff_result['modified'])} modified")

        except Exception as e:
            logger.error(f"Error analyzing config diff: {e}")

        return diff_result

    def _assess_risk_level(self, diff_result: Dict) -> str:
        """
        Assess risk level based on diff analysis.

        Args:
            diff_result: Diff analysis results

        Returns:
            Risk level string: low, medium, high, or critical
        """
        removed_count = len(diff_result.get("removed", []))
        modified_count = len(diff_result.get("modified", []))

        if removed_count > 0:
            return "high"
        elif modified_count > 5:
            return "medium"
        elif modified_count > 0:
            return "low"
        else:
            return "minimal"

    def has_critical_changes(self, diff_result: Dict) -> bool:
        """
        Check if diff contains critical changes.

        Args:
            diff_result: Diff analysis results

        Returns:
            True if critical changes detected, False otherwise
        """
        critical_keys = ["security", "authentication", "database", "secrets"]
        
        for modified in diff_result.get("modified", []):
            if any(crit_key in modified.get("key", "").lower() 
                   for crit_key in critical_keys):
                return True

        return False
