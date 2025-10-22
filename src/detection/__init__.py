"""Change Detection Module

This module handles detection of available updates and changes.
"""

from .version_detector import VersionDetector
from .image_detector import ImageDetector

__all__ = ['VersionDetector', 'ImageDetector']
