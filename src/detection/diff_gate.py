"""
Change evaluation and diff gate logic.
"""

from typing import Dict, Any, Optional
from enum import Enum
from .semver_analyzer import SemVerAnalyzer, VersionChangeType
from ..config.schema import UpdateAction, SemVerGates


class UpdateDecision(str, Enum):
    """Decision on whether to proceed with update."""
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW_REQUIRED = "review_required"
    MANUAL_APPROVAL = "manual_approval"


class DiffGate:
    """Evaluates changes and determines update safety."""

    def __init__(self, semver_gates: Optional[SemVerGates] = None):
        """
        Initialize diff gate.

        Args:
            semver_gates: SemVer gate policy configuration.
        """
        self.semver_gates = semver_gates or SemVerGates()
        self.analyzer = SemVerAnalyzer()

    def evaluate_update(
        self,
        current_version: str,
        new_version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate whether an update should proceed.

        Args:
            current_version: Current version string.
            new_version: New version string.
            metadata: Optional metadata about the asset.

        Returns:
            Dictionary with evaluation results including decision and reasoning.
        """
        # Parse and compare versions
        comparison, change_type = self.analyzer.compare_versions(
            current_version,
            new_version
        )

        # Not an upgrade
        if comparison <= 0:
            return {
                'decision': UpdateDecision.REJECT,
                'change_type': change_type.value,
                'current_version': current_version,
                'new_version': new_version,
                'reason': 'Not an upgrade or unknown version format',
                'safe': False
            }

        # Get action based on change type
        action = self._get_action_for_change_type(change_type)

        # Make decision based on action
        decision = self._action_to_decision(action)

        # Check if it's a safe update
        safe = self._is_safe_change(change_type, action)

        result = {
            'decision': decision.value,
            'change_type': change_type.value,
            'current_version': current_version,
            'new_version': new_version,
            'action': action.value,
            'safe': safe,
            'reason': self._generate_reason(change_type, action, decision)
        }

        # Add metadata if provided
        if metadata:
            result['metadata'] = metadata

        return result

    def _get_action_for_change_type(self, change_type: VersionChangeType) -> UpdateAction:
        """
        Get configured action for a change type.

        Args:
            change_type: Type of version change.

        Returns:
            UpdateAction enum value.
        """
        if change_type == VersionChangeType.PATCH:
            return self.semver_gates.patch
        elif change_type == VersionChangeType.MINOR:
            return self.semver_gates.minor
        elif change_type == VersionChangeType.MAJOR:
            return self.semver_gates.major
        elif change_type == VersionChangeType.PRERELEASE:
            return self.semver_gates.prerelease
        else:
            return UpdateAction.MANUAL  # Default to manual for unknown

    def _action_to_decision(self, action: UpdateAction) -> UpdateDecision:
        """
        Convert UpdateAction to UpdateDecision.

        Args:
            action: Update action from policy.

        Returns:
            UpdateDecision enum value.
        """
        if action == UpdateAction.AUTO:
            return UpdateDecision.APPROVE
        elif action == UpdateAction.REVIEW:
            return UpdateDecision.REVIEW_REQUIRED
        elif action == UpdateAction.MANUAL:
            return UpdateDecision.MANUAL_APPROVAL
        elif action == UpdateAction.SKIP:
            return UpdateDecision.REJECT
        else:
            return UpdateDecision.MANUAL_APPROVAL

    def _is_safe_change(self, change_type: VersionChangeType, action: UpdateAction) -> bool:
        """
        Determine if a change is considered safe.

        Args:
            change_type: Type of version change.
            action: Configured action for this change type.

        Returns:
            True if change is safe.
        """
        # Patch updates are generally safe
        if change_type == VersionChangeType.PATCH:
            return True

        # Minor updates can be safe if auto-approved
        if change_type == VersionChangeType.MINOR and action == UpdateAction.AUTO:
            return True

        # Major updates and prereleases are not automatically safe
        return False

    def _generate_reason(
        self,
        change_type: VersionChangeType,
        action: UpdateAction,
        decision: UpdateDecision
    ) -> str:
        """
        Generate human-readable reason for decision.

        Args:
            change_type: Type of version change.
            action: Configured action.
            decision: Update decision.

        Returns:
            Reason string.
        """
        if decision == UpdateDecision.APPROVE:
            return f"{change_type.value.capitalize()} version update - auto-approved by policy"
        elif decision == UpdateDecision.REVIEW_REQUIRED:
            return f"{change_type.value.capitalize()} version update - requires review"
        elif decision == UpdateDecision.MANUAL_APPROVAL:
            return f"{change_type.value.capitalize()} version update - requires manual approval"
        elif decision == UpdateDecision.REJECT:
            return f"{change_type.value.capitalize()} version update - rejected by policy"
        else:
            return "Unknown decision reason"

    def should_auto_update(
        self,
        current_version: str,
        new_version: str
    ) -> bool:
        """
        Quick check if update should proceed automatically.

        Args:
            current_version: Current version.
            new_version: New version.

        Returns:
            True if update should proceed automatically.
        """
        evaluation = self.evaluate_update(current_version, new_version)
        return evaluation['decision'] == UpdateDecision.APPROVE.value

    def get_risk_level(self, change_type: VersionChangeType) -> str:
        """
        Get risk level for a change type.

        Args:
            change_type: Type of version change.

        Returns:
            Risk level string: low, medium, high.
        """
        if change_type == VersionChangeType.PATCH:
            return "low"
        elif change_type == VersionChangeType.MINOR:
            return "medium"
        elif change_type in [VersionChangeType.MAJOR, VersionChangeType.PRERELEASE]:
            return "high"
        else:
            return "unknown"

    def batch_evaluate(
        self,
        updates: list[tuple[str, str, str]]
    ) -> Dict[str, Any]:
        """
        Evaluate multiple updates at once.

        Args:
            updates: List of (asset_id, current_version, new_version) tuples.

        Returns:
            Dictionary with batch evaluation results.
        """
        results = {}
        summary = {
            'total': len(updates),
            'approved': 0,
            'review_required': 0,
            'manual_approval': 0,
            'rejected': 0
        }

        for asset_id, current, new in updates:
            evaluation = self.evaluate_update(current, new)
            results[asset_id] = evaluation

            # Update summary
            decision = evaluation['decision']
            if decision == UpdateDecision.APPROVE.value:
                summary['approved'] += 1
            elif decision == UpdateDecision.REVIEW_REQUIRED.value:
                summary['review_required'] += 1
            elif decision == UpdateDecision.MANUAL_APPROVAL.value:
                summary['manual_approval'] += 1
            else:
                summary['rejected'] += 1

        return {
            'evaluations': results,
            'summary': summary
        }
