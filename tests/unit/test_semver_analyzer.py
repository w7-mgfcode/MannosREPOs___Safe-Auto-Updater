"""
Unit tests for SemVer analyzer.
"""

import pytest
from src.detection.semver_analyzer import SemVerAnalyzer, VersionChangeType


class TestSemVerAnalyzer:
    """Test suite for SemVerAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return SemVerAnalyzer()

    def test_parse_standard_semver(self, analyzer):
        """Test parsing standard semantic versions."""
        version = analyzer.parse_version("1.2.3")
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_version_with_v_prefix(self, analyzer):
        """Test parsing versions with 'v' prefix."""
        version = analyzer.parse_version("v2.0.1")
        assert version is not None
        assert version.major == 2
        assert version.minor == 0
        assert version.patch == 1

    def test_parse_prerelease_version(self, analyzer):
        """Test parsing pre-release versions."""
        version = analyzer.parse_version("1.0.0-alpha.1")
        assert version is not None
        assert version.major == 1
        assert version.prerelease == "alpha.1"

    def test_compare_patch_update(self, analyzer):
        """Test comparing patch version updates."""
        comparison, change_type = analyzer.compare_versions("1.0.0", "1.0.1")
        assert comparison == 1  # new > current
        assert change_type == VersionChangeType.PATCH

    def test_compare_minor_update(self, analyzer):
        """Test comparing minor version updates."""
        comparison, change_type = analyzer.compare_versions("1.0.0", "1.1.0")
        assert comparison == 1
        assert change_type == VersionChangeType.MINOR

    def test_compare_major_update(self, analyzer):
        """Test comparing major version updates."""
        comparison, change_type = analyzer.compare_versions("1.0.0", "2.0.0")
        assert comparison == 1
        assert change_type == VersionChangeType.MAJOR

    def test_compare_downgrade(self, analyzer):
        """Test comparing version downgrades."""
        comparison, _ = analyzer.compare_versions("2.0.0", "1.0.0")
        assert comparison == -1  # new < current

    def test_compare_equal_versions(self, analyzer):
        """Test comparing equal versions."""
        comparison, change_type = analyzer.compare_versions("1.2.3", "1.2.3")
        assert comparison == 0
        assert change_type == VersionChangeType.NO_CHANGE

    def test_is_upgrade(self, analyzer):
        """Test upgrade detection."""
        assert analyzer.is_upgrade("1.0.0", "1.0.1") is True
        assert analyzer.is_upgrade("1.0.1", "1.0.0") is False
        assert analyzer.is_upgrade("1.0.0", "1.0.0") is False

    def test_is_breaking_change(self, analyzer):
        """Test breaking change detection."""
        assert analyzer.is_breaking_change("1.0.0", "2.0.0") is True
        assert analyzer.is_breaking_change("1.0.0", "1.1.0") is False
        assert analyzer.is_breaking_change("1.0.0", "1.0.1") is False

    def test_is_safe_update_patch(self, analyzer):
        """Test safe update detection for patches."""
        assert analyzer.is_safe_update("1.0.0", "1.0.1") is True

    def test_is_safe_update_minor(self, analyzer):
        """Test safe update detection for minor versions."""
        assert analyzer.is_safe_update("1.0.0", "1.1.0", allow_minor=True) is True
        assert analyzer.is_safe_update("1.0.0", "1.1.0", allow_minor=False) is False

    def test_is_safe_update_major(self, analyzer):
        """Test safe update detection for major versions."""
        assert analyzer.is_safe_update("1.0.0", "2.0.0", allow_major=False) is False
        assert analyzer.is_safe_update("1.0.0", "2.0.0", allow_major=True) is True

    def test_get_version_info(self, analyzer):
        """Test version info extraction."""
        info = analyzer.get_version_info("1.2.3")
        assert info['valid'] is True
        assert info['major'] == 1
        assert info['minor'] == 2
        assert info['patch'] == 3

    def test_docker_version_formats(self, analyzer):
        """Test parsing Docker-style version formats."""
        # X.Y.Z format
        version1 = analyzer.parse_version("1.21.0")
        assert version1 is not None
        assert version1.major == 1
        assert version1.minor == 21

        # X.Y format (coerced to X.Y.0)
        version2 = analyzer.parse_version("1.21")
        assert version2 is not None

    def test_latest_tag(self, analyzer):
        """Test handling of 'latest' tag."""
        version = analyzer.parse_version("latest")
        assert version is None

    def test_invalid_version(self, analyzer):
        """Test handling of invalid versions."""
        version = analyzer.parse_version("not-a-version")
        assert version is None
