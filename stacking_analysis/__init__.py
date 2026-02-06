"""
Stacking Analysis - Bilayer Stacking Configuration Analysis Tool

This package provides tools for analyzing atomic stacking configurations
in bilayer materials, particularly for transition metal dichalcogenides (TMDs).
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import classify_stacking_type
from .analyzer import StackingAnalyzer

__all__ = ['classify_stacking_type', 'StackingAnalyzer']
