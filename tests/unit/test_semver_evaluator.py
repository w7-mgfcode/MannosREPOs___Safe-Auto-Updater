"""Unit tests for SemVer Evaluator"""

import pytest
from safe_auto_updater.detection.semver_evaluator import SemVerEvaluator


class TestSemVerEvaluator:
    """Test cases for SemVerEvaluator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.evaluator = SemVerEvaluator()

    def test_parse_valid_version(self):
        """Test parsing valid semantic version"""
        result = self.evaluator.parse_version("1.2.3")
        assert result == (1, 2, 3)

    def test_parse_version_with_v_prefix(self):
        """Test parsing version with v prefix"""
        result = self.evaluator.parse_version("v2.0.1")
        assert result == (2, 0, 1)

    def test_parse_invalid_version(self):
        """Test parsing invalid version"""
        result = self.evaluator.parse_version("invalid")
        assert result is None

    def test_compare_versions_equal(self):
        """Test comparing equal versions"""
        result = self.evaluator.compare_versions("1.2.3", "1.2.3")
        assert result == 0

    def test_compare_versions_less_than(self):
        """Test comparing versions where current < target"""
        result = self.evaluator.compare_versions("1.2.3", "1.2.4")
        assert result == -1

    def test_compare_versions_greater_than(self):
        """Test comparing versions where current > target"""
        result = self.evaluator.compare_versions("2.0.0", "1.9.9")
        assert result == 1

    def test_is_breaking_change(self):
        """Test breaking change detection"""
        assert self.evaluator.is_breaking_change("1.2.3", "2.0.0") is True
        assert self.evaluator.is_breaking_change("1.2.3", "1.3.0") is False

    def test_is_minor_update(self):
        """Test minor update detection"""
        assert self.evaluator.is_minor_update("1.2.3", "1.3.0") is True
        assert self.evaluator.is_minor_update("1.2.3", "2.0.0") is False

    def test_is_patch_update(self):
        """Test patch update detection"""
        assert self.evaluator.is_patch_update("1.2.3", "1.2.4") is True
        assert self.evaluator.is_patch_update("1.2.3", "1.3.0") is False
