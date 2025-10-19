"""Unit tests for SemVer Evaluator."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from evaluation.semver_evaluator import SemVerEvaluator


class TestSemVerEvaluator:
    """Tests for SemVerEvaluator class."""
    
    def test_parse_version_valid(self):
        """Test parsing valid version strings."""
        evaluator = SemVerEvaluator()
        
        result = evaluator.parse_version("1.2.3")
        assert result == {'major': 1, 'minor': 2, 'patch': 3}
        
        result = evaluator.parse_version("v2.0.1")
        assert result == {'major': 2, 'minor': 0, 'patch': 1}
    
    def test_parse_version_invalid(self):
        """Test parsing invalid version strings."""
        evaluator = SemVerEvaluator()
        
        result = evaluator.parse_version("invalid")
        assert result is None
        
        result = evaluator.parse_version("1.2")
        assert result is None
    
    def test_evaluate_update_patch(self):
        """Test evaluation of patch updates."""
        config = {
            'allow_major_updates': False,
            'allow_minor_updates': True,
            'allow_patch_updates': True
        }
        evaluator = SemVerEvaluator(config)
        
        result = evaluator.evaluate_update("1.2.3", "1.2.4")
        assert result['allowed'] is True
        assert result['change_type'] == 'patch'
    
    def test_evaluate_update_minor(self):
        """Test evaluation of minor updates."""
        config = {
            'allow_major_updates': False,
            'allow_minor_updates': True,
            'allow_patch_updates': True
        }
        evaluator = SemVerEvaluator(config)
        
        result = evaluator.evaluate_update("1.2.3", "1.3.0")
        assert result['allowed'] is True
        assert result['change_type'] == 'minor'
    
    def test_evaluate_update_major_blocked(self):
        """Test evaluation of major updates when blocked."""
        config = {
            'allow_major_updates': False,
            'allow_minor_updates': True,
            'allow_patch_updates': True
        }
        evaluator = SemVerEvaluator(config)
        
        result = evaluator.evaluate_update("1.2.3", "2.0.0")
        assert result['allowed'] is False
        assert result['change_type'] == 'major'
    
    def test_evaluate_update_major_allowed(self):
        """Test evaluation of major updates when allowed."""
        config = {
            'allow_major_updates': True,
            'allow_minor_updates': True,
            'allow_patch_updates': True
        }
        evaluator = SemVerEvaluator(config)
        
        result = evaluator.evaluate_update("1.2.3", "2.0.0")
        assert result['allowed'] is True
        assert result['change_type'] == 'major'
    
    def test_evaluate_update_no_change(self):
        """Test evaluation when no version increase."""
        evaluator = SemVerEvaluator()
        
        result = evaluator.evaluate_update("1.2.3", "1.2.3")
        assert result['allowed'] is False
        assert result['change_type'] == 'none'
