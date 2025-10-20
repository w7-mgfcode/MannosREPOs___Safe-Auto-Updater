"""
Unit tests for DiffGate.
"""

import pytest
from src.detection.diff_gate import DiffGate, UpdateDecision
from src.config.schema import SemVerGates, UpdateAction


class TestDiffGate:
    """Test suite for DiffGate."""

    @pytest.fixture
    def default_gate(self):
        """Create diff gate with default policy."""
        return DiffGate()

    @pytest.fixture
    def strict_gate(self):
        """Create diff gate with strict policy."""
        gates = SemVerGates(
            patch=UpdateAction.AUTO,
            minor=UpdateAction.MANUAL,
            major=UpdateAction.MANUAL,
            prerelease=UpdateAction.SKIP
        )
        return DiffGate(semver_gates=gates)

    @pytest.fixture
    def permissive_gate(self):
        """Create diff gate with permissive policy."""
        gates = SemVerGates(
            patch=UpdateAction.AUTO,
            minor=UpdateAction.AUTO,
            major=UpdateAction.REVIEW,
            prerelease=UpdateAction.REVIEW
        )
        return DiffGate(semver_gates=gates)

    def test_evaluate_patch_update_default(self, default_gate):
        """Test evaluation of patch updates with default policy."""
        result = default_gate.evaluate_update("1.0.0", "1.0.1")
        assert result['decision'] == UpdateDecision.APPROVE.value
        assert result['change_type'] == 'patch'
        assert result['safe'] is True

    def test_evaluate_minor_update_default(self, default_gate):
        """Test evaluation of minor updates with default policy."""
        result = default_gate.evaluate_update("1.0.0", "1.1.0")
        assert result['decision'] == UpdateDecision.REVIEW_REQUIRED.value
        assert result['change_type'] == 'minor'

    def test_evaluate_major_update_default(self, default_gate):
        """Test evaluation of major updates with default policy."""
        result = default_gate.evaluate_update("1.0.0", "2.0.0")
        assert result['decision'] == UpdateDecision.MANUAL_APPROVAL.value
        assert result['change_type'] == 'major'
        assert result['safe'] is False

    def test_evaluate_downgrade(self, default_gate):
        """Test evaluation of version downgrades."""
        result = default_gate.evaluate_update("2.0.0", "1.0.0")
        assert result['decision'] == UpdateDecision.REJECT.value

    def test_strict_policy_minor(self, strict_gate):
        """Test strict policy for minor updates."""
        result = strict_gate.evaluate_update("1.0.0", "1.1.0")
        assert result['decision'] == UpdateDecision.MANUAL_APPROVAL.value

    def test_permissive_policy_minor(self, permissive_gate):
        """Test permissive policy for minor updates."""
        result = permissive_gate.evaluate_update("1.0.0", "1.1.0")
        assert result['decision'] == UpdateDecision.APPROVE.value

    def test_should_auto_update_patch(self, default_gate):
        """Test auto-update decision for patches."""
        assert default_gate.should_auto_update("1.0.0", "1.0.1") is True

    def test_should_auto_update_major(self, default_gate):
        """Test auto-update decision for major versions."""
        assert default_gate.should_auto_update("1.0.0", "2.0.0") is False

    def test_get_risk_level(self, default_gate):
        """Test risk level determination."""
        from src.detection.semver_analyzer import VersionChangeType

        assert default_gate.get_risk_level(VersionChangeType.PATCH) == "low"
        assert default_gate.get_risk_level(VersionChangeType.MINOR) == "medium"
        assert default_gate.get_risk_level(VersionChangeType.MAJOR) == "high"

    def test_batch_evaluate(self, default_gate):
        """Test batch evaluation of multiple updates."""
        updates = [
            ("asset1", "1.0.0", "1.0.1"),  # patch - approve
            ("asset2", "1.0.0", "1.1.0"),  # minor - review
            ("asset3", "1.0.0", "2.0.0"),  # major - manual
        ]

        results = default_gate.batch_evaluate(updates)

        assert results['summary']['total'] == 3
        assert results['summary']['approved'] == 1
        assert results['summary']['review_required'] == 1
        assert results['summary']['manual_approval'] == 1

    def test_evaluation_with_metadata(self, default_gate):
        """Test evaluation includes metadata."""
        metadata = {'asset_name': 'test-app', 'namespace': 'production'}
        result = default_gate.evaluate_update(
            "1.0.0",
            "1.0.1",
            metadata=metadata
        )
        assert 'metadata' in result
        assert result['metadata'] == metadata

    def test_reason_generation(self, default_gate):
        """Test that evaluation includes human-readable reasons."""
        result = default_gate.evaluate_update("1.0.0", "1.0.1")
        assert 'reason' in result
        assert isinstance(result['reason'], str)
        assert len(result['reason']) > 0
