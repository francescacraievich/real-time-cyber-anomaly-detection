"""
Aggregation Functions Module

Feature engineering functions for network traffic anomaly detection.
"""

# Import functions as you create them
from .metrics_features import (
    calculate_total_events_processed,
)

__all__ = [
    'calculate_total_events_processed',
]