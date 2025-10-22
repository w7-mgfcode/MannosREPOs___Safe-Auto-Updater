"""
Semantic versioning analysis and comparison.
"""

from typing import Optional, Tuple
from enum import Enum
import re
import semver


class VersionChangeType(str, Enum):
    """Types of version changes."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD = "build"
    UNKNOWN = "unknown"
    NO_CHANGE = "no_change"


class SemVerAnalyzer:
    """Analyzes and compares semantic versions."""

    # Common version patterns
    SEMVER_PATTERN = re.compile(
        r'^v?(\d+)\.(\d+)\.(\d+)'
        r'(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'
        r'(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    )

    # Docker-style version patterns
    DOCKER_PATTERNS = [
        re.compile(r'^(\d+)\.(\d+)\.(\d+)'),  # X.Y.Z
        re.compile(r'^(\d+)\.(\d+)'),         # X.Y (treat as X.Y.0)
        re.compile(r'^(\d+)'),                # X (treat as X.0.0)
    ]

    def __init__(self):
        """Initialize SemVer analyzer."""
        pass

    def parse_version(self, version_string: str) -> Optional[semver.Version]:
        """
        Parse version string into semver.Version.

        Args:
            version_string: Version string to parse.

        Returns:
            semver.Version object or None if parsing fails.
        """
        if not version_string or version_string == 'latest':
            return None

        # Try standard semver parsing first
        try:
            # Remove 'v' prefix if present
            clean_version = version_string.lstrip('v')
            return semver.Version.parse(clean_version)
        except ValueError:
            pass

        # Try to coerce non-standard versions
        return self._coerce_version(version_string)

    def _coerce_version(self, version_string: str) -> Optional[semver.Version]:
        """
        Attempt to coerce non-standard version strings to semver.

        Args:
            version_string: Version string to coerce.

        Returns:
            semver.Version object or None.
        """
        clean_version = version_string.lstrip('v')

        # Try Docker-style patterns
        for pattern in self.DOCKER_PATTERNS:
            match = pattern.match(clean_version)
            if match:
                groups = match.groups()
                major = int(groups[0])
                minor = int(groups[1]) if len(groups) > 1 and groups[1] else 0
                patch = int(groups[2]) if len(groups) > 2 and groups[2] else 0

                try:
                    return semver.Version(major=major, minor=minor, patch=patch)
                except ValueError:
                    pass

        # Try coercion as last resort
        try:
            return semver.Version.parse(semver.Version.coerce(clean_version))
        except (ValueError, TypeError):
            return None

    def compare_versions(
        self,
        current: str,
        new: str
    ) -> Tuple[int, VersionChangeType]:
        """
        Compare two version strings.

        Args:
            current: Current version string.
            new: New version string.

        Returns:
            Tuple of (comparison_result, change_type)
            comparison_result: -1 (new < current), 0 (equal), 1 (new > current)
            change_type: Type of version change
        """
        current_ver = self.parse_version(current)
        new_ver = self.parse_version(new)

        if current_ver is None or new_ver is None:
            return (0, VersionChangeType.UNKNOWN)

        # Compare versions
        if new_ver > current_ver:
            change_type = self._determine_change_type(current_ver, new_ver)
            return (1, change_type)
        elif new_ver < current_ver:
            return (-1, VersionChangeType.UNKNOWN)
        else:
            return (0, VersionChangeType.NO_CHANGE)

    def _determine_change_type(
        self,
        current: semver.Version,
        new: semver.Version
    ) -> VersionChangeType:
        """
        Determine the type of version change.

        Args:
            current: Current version.
            new: New version.

        Returns:
            VersionChangeType enum value.
        """
        if new.major > current.major:
            return VersionChangeType.MAJOR

        if new.minor > current.minor:
            return VersionChangeType.MINOR

        if new.patch > current.patch:
            return VersionChangeType.PATCH

        if new.prerelease and new.prerelease != current.prerelease:
            return VersionChangeType.PRERELEASE

        if new.build and new.build != current.build:
            return VersionChangeType.BUILD

        return VersionChangeType.NO_CHANGE

    def is_upgrade(self, current: str, new: str) -> bool:
        """
        Check if new version is an upgrade.

        Args:
            current: Current version string.
            new: New version string.

        Returns:
            True if new version is higher than current.
        """
        comparison, _ = self.compare_versions(current, new)
        return comparison > 0

    def is_breaking_change(self, current: str, new: str) -> bool:
        """
        Check if version change is potentially breaking (major version bump).

        Args:
            current: Current version string.
            new: New version string.

        Returns:
            True if major version increased.
        """
        _, change_type = self.compare_versions(current, new)
        return change_type == VersionChangeType.MAJOR

    def is_safe_update(
        self,
        current: str,
        new: str,
        allow_minor: bool = True,
        allow_major: bool = False
    ) -> bool:
        """
        Determine if update is considered safe based on policies.

        Args:
            current: Current version string.
            new: New version string.
            allow_minor: Allow minor version updates.
            allow_major: Allow major version updates.

        Returns:
            True if update is considered safe.
        """
        comparison, change_type = self.compare_versions(current, new)

        if comparison <= 0:
            return False  # Not an upgrade or unknown

        if change_type == VersionChangeType.PATCH:
            return True  # Patches are always safe

        if change_type == VersionChangeType.MINOR:
            return allow_minor

        if change_type == VersionChangeType.MAJOR:
            return allow_major

        # Prerelease and build changes need review
        return False

    def get_version_info(self, version: str) -> dict:
        """
        Get detailed information about a version.

        Args:
            version: Version string.

        Returns:
            Dictionary with version details.
        """
        parsed = self.parse_version(version)

        if parsed is None:
            return {
                'valid': False,
                'original': version,
                'error': 'Unable to parse version'
            }

        return {
            'valid': True,
            'original': version,
            'major': parsed.major,
            'minor': parsed.minor,
            'patch': parsed.patch,
            'prerelease': parsed.prerelease or None,
            'build': parsed.build or None,
            'is_prerelease': bool(parsed.prerelease),
            'string': str(parsed)
        }
