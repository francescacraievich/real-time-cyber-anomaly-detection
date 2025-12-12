"""
Aggregation Functions Module

Feature engineering functions for network traffic anomaly detection.
"""

from .metrics_features import (
    calculate_total_anomalous_events,
    calculate_total_events_for_dst_ports,
    calculate_total_events_processed,
    calculate_total_malicious_events_per_protocol,
    calculate_total_unique_malicious_ips,
    calculate_trend_percentage_change,
)

__all__ = [
    "calculate_total_events_processed",
    "calculate_total_anomalous_events",
    "calculate_total_unique_malicious_ips",
    "calculate_trend_percentage_change",
    "calculate_total_events_for_dst_ports",
    "calculate_total_malicious_events_per_protocol",
]
