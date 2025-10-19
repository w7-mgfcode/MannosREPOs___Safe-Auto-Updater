"""
SemVer Evaluator

Evaluates semantic versioning to determine update safety.
"""

from typing import Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)


class SemVerEvaluator:
    """Evaluates semantic versioning for update decisions."""

    def __init__(self):
        """Initialize SemVer evaluator."""
        self.semver_pattern = re.compile(
            r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        )
        logger.info("SemVerEvaluator initialized")

    def parse_version(self, version: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse a semantic version string.

        Args:
            version: Version string to parse

        Returns:
            Tuple of (major, minor, patch) or None if invalid
        """
        match = self.semver_pattern.match(version)
        if not match:
            logger.warning(f"Invalid semver format: {version}")
            return None

        major, minor, patch = match.groups()[:3]
        return (int(major), int(minor), int(patch))

    def compare_versions(self, current: str, target: str) -> int:
        """
        Compare two semantic versions.

        Args:
            current: Current version string
            target: Target version string

        Returns:
            -1 if current < target, 0 if equal, 1 if current > target
        """
        current_parsed = self.parse_version(current)
        target_parsed = self.parse_version(target)

        if not current_parsed or not target_parsed:
            logger.error("Cannot compare invalid version strings")
            return 0

        if current_parsed < target_parsed:
            return -1
        elif current_parsed > target_parsed:
            return 1
        return 0

    def is_breaking_change(self, current: str, target: str) -> bool:
        """
        Determine if version change is a breaking change.

        Args:
            current: Current version string
            target: Target version string

        Returns:
            True if major version changed, False otherwise
        """
        current_parsed = self.parse_version(current)
        target_parsed = self.parse_version(target)

        if not current_parsed or not target_parsed:
            return False

        return target_parsed[0] > current_parsed[0]

    def is_minor_update(self, current: str, target: str) -> bool:
        """
        Determine if version change is a minor update.

        Args:
            current: Current version string
            target: Target version string

        Returns:
            True if minor version changed (major same), False otherwise
        """
        current_parsed = self.parse_version(current)
        target_parsed = self.parse_version(target)

        if not current_parsed or not target_parsed:
            return False

        return (target_parsed[0] == current_parsed[0] and
                target_parsed[1] > current_parsed[1])

    def is_patch_update(self, current: str, target: str) -> bool:
        """
        Determine if version change is a patch update.

        Args:
            current: Current version string
            target: Target version string

        Returns:
            True if only patch version changed, False otherwise
        """
        current_parsed = self.parse_version(current)
        target_parsed = self.parse_version(target)

        if not current_parsed or not target_parsed:
            return False

        return (target_parsed[0] == current_parsed[0] and
                target_parsed[1] == current_parsed[1] and
                target_parsed[2] > current_parsed[2])
