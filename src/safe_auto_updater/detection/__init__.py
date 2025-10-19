"""
Detection Module

Detects and evaluates changes with SemVer and diff gates.
"""

from .change_detector import ChangeDetector
from .semver_evaluator import SemVerEvaluator
from .diff_analyzer import DiffAnalyzer

__all__ = ["ChangeDetector", "SemVerEvaluator", "DiffAnalyzer"]
