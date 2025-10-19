"""Semantic Version Evaluator

Evaluates version changes using Semantic Versioning rules.
"""

import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class SemVerEvaluator:
    """Evaluates version changes using SemVer rules."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SemVer evaluator.
        
        Args:
            config: Configuration dictionary with update policies
        """
        self.config = config or {}
        self.allow_major = self.config.get('allow_major_updates', False)
        self.allow_minor = self.config.get('allow_minor_updates', True)
        self.allow_patch = self.config.get('allow_patch_updates', True)
        
    def parse_version(self, version: str) -> Optional[Dict[str, int]]:
        """Parse a semantic version string.
        
        Args:
            version: Version string (e.g., "1.2.3")
            
        Returns:
            Dictionary with major, minor, patch numbers
        """
        match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)', version)
        if match:
            return {
                'major': int(match.group(1)),
                'minor': int(match.group(2)),
                'patch': int(match.group(3))
            }
        return None
    
    def evaluate_update(self, current: str, available: str) -> Dict[str, Any]:
        """Evaluate if an update should be applied.
        
        Args:
            current: Current version string
            available: Available version string
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating update: {current} -> {available}")
        
        current_ver = self.parse_version(current)
        available_ver = self.parse_version(available)
        
        if not current_ver or not available_ver:
            return {
                'allowed': False,
                'reason': 'Invalid version format',
                'change_type': 'unknown'
            }
        
        if current_ver['major'] < available_ver['major']:
            return {
                'allowed': self.allow_major,
                'reason': 'Major version change',
                'change_type': 'major'
            }
        elif current_ver['minor'] < available_ver['minor']:
            return {
                'allowed': self.allow_minor,
                'reason': 'Minor version change',
                'change_type': 'minor'
            }
        elif current_ver['patch'] < available_ver['patch']:
            return {
                'allowed': self.allow_patch,
                'reason': 'Patch version change',
                'change_type': 'patch'
            }
        
        return {
            'allowed': False,
            'reason': 'No version increase',
            'change_type': 'none'
        }
