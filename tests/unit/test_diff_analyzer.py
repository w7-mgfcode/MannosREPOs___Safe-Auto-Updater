"""Unit tests for Diff Analyzer"""

import pytest
from safe_auto_updater.detection.diff_analyzer import DiffAnalyzer


class TestDiffAnalyzer:
    """Test cases for DiffAnalyzer"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = DiffAnalyzer()

    def test_analyze_no_changes(self):
        """Test analyzing configs with no changes"""
        config = {"key1": "value1", "key2": "value2"}
        result = self.analyzer.analyze_config_diff(config, config)
        
        assert len(result["added"]) == 0
        assert len(result["removed"]) == 0
        assert len(result["modified"]) == 0
        assert result["risk_level"] == "minimal"

    def test_analyze_added_keys(self):
        """Test analyzing configs with added keys"""
        current = {"key1": "value1"}
        new = {"key1": "value1", "key2": "value2"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert "key2" in result["added"]

    def test_analyze_removed_keys(self):
        """Test analyzing configs with removed keys"""
        current = {"key1": "value1", "key2": "value2"}
        new = {"key1": "value1"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert "key2" in result["removed"]
        assert result["risk_level"] == "high"

    def test_analyze_modified_keys(self):
        """Test analyzing configs with modified keys"""
        current = {"key1": "value1"}
        new = {"key1": "value2"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert len(result["modified"]) == 1
        assert result["modified"][0]["key"] == "key1"
        assert result["modified"][0]["old_value"] == "value1"
        assert result["modified"][0]["new_value"] == "value2"

    def test_has_critical_changes_true(self):
        """Test detecting critical changes"""
        current = {"security": "old"}
        new = {"security": "new"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert self.analyzer.has_critical_changes(result) is True

    def test_has_critical_changes_false(self):
        """Test detecting non-critical changes"""
        current = {"app_name": "old"}
        new = {"app_name": "new"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert self.analyzer.has_critical_changes(result) is False

    def test_risk_level_assessment(self):
        """Test risk level assessment"""
        # Test with multiple modifications
        current = {"k1": "v1", "k2": "v2", "k3": "v3", "k4": "v4", "k5": "v5", "k6": "v6"}
        new = {"k1": "new1", "k2": "new2", "k3": "new3", "k4": "new4", "k5": "new5", "k6": "new6"}
        
        result = self.analyzer.analyze_config_diff(current, new)
        assert result["risk_level"] == "medium"
