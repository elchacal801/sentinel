"""
Multi-INT Fusion Service
Correlates intelligence from multiple sources (OSINT, SIGINT, CYBINT, etc.)
"""

from .correlator import MultiINTCorrelator, ConfidenceScorer

__all__ = ["MultiINTCorrelator", "ConfidenceScorer"]
