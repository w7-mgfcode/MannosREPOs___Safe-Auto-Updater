"""Diff Evaluator

Evaluates configuration and image diffs to determine safety of updates.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DiffEvaluator:
    """Evaluates diffs for safe update decisions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize diff evaluator.
        
        Args:
            config: Configuration dictionary with diff policies
        """
        self.config = config or {}
        self.max_file_changes = self.config.get('max_file_changes', 100)
        self.blocked_paths = self.config.get('blocked_paths', [])
        
    def evaluate_config_diff(self, old_config: Dict[str, Any], 
                            new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate configuration differences.
        
        Args:
            old_config: Old configuration dictionary
            new_config: New configuration dictionary
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info("Evaluating configuration diff...")
        
        changes = self._detect_changes(old_config, new_config)
        
        return {
            'allowed': len(changes) < self.max_file_changes,
            'changes_count': len(changes),
            'changes': changes,
            'reason': f"Configuration has {len(changes)} changes"
        }
    
    def _detect_changes(self, old: Dict[str, Any], new: Dict[str, Any]) -> List[str]:
        """Detect changes between two dictionaries.
        
        Args:
            old: Old dictionary
            new: New dictionary
            
        Returns:
            List of change descriptions
        """
        changes = []
        
        # Compare keys
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        
        added = new_keys - old_keys
        removed = old_keys - new_keys
        common = old_keys & new_keys
        
        for key in added:
            changes.append(f"Added: {key}")
        
        for key in removed:
            changes.append(f"Removed: {key}")
        
        for key in common:
            if old[key] != new[key]:
                changes.append(f"Modified: {key}")
        
        return changes
    
    def evaluate_image_diff(self, old_image: str, new_image: str) -> Dict[str, Any]:
        """Evaluate image differences.
        
        Args:
            old_image: Old image reference
            new_image: New image reference
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating image diff: {old_image} -> {new_image}")
        
        # Simple comparison for now
        return {
            'allowed': True,
            'reason': 'Image change detected',
            'old': old_image,
            'new': new_image
        }
