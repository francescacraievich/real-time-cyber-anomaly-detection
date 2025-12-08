from river import drift
import numpy as np
from collections import deque

# Prometheus metrics (optional - graceful fallback if not available)
try:
    from monitoring.metrics import (
        anomaly_rate_gauge, drift_detected_total, drift_detected_flag,
        samples_since_drift
    )
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False


class DriftDetector:
    def __init__(self, threshold=0.002, window_size=100):
        # ADWIN for detecting changes in average values
        # Lower delta = more sensitive to changes (0.002 is very sensitive)
        self.adwin = drift.ADWIN(delta=threshold)
        self.history = deque(maxlen=window_size)  # Store recent history for analysis
        self.drift_detected = False
        self.processed_samples = 0

    def update(self, is_anomaly):
        # Convert boolean to integer (1 for Anomaly, 0 for Benign)
        val = 1 if is_anomaly else 0

        # Update our sliding window history
        self.history.append(val)
        self.processed_samples += 1

        # Feed the binary value to ADWIN.
        # ADWIN will detect if the *probability* of getting a '1' changes significantly.
        self.adwin.update(val)

        # Update metrics
        if METRICS_ENABLED:
            anomaly_rate_gauge.set(self.get_current_anomaly_rate())
            samples_since_drift.set(self.processed_samples)

        if self.adwin.drift_detected:
            self.drift_detected = True
            if METRICS_ENABLED:
                drift_detected_total.inc()
                drift_detected_flag.set(1)
            return True

        if METRICS_ENABLED:
            drift_detected_flag.set(0)
        return False
    
    def get_current_anomaly_rate(self):
        # Percentage of anomalies in the current window
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)
    
    def reset(self):
        # Reset the detector after retraining
        self.adwin = drift.ADWIN(delta=self.adwin.delta)
        self.drift_detected = False
        self.history.clear()
        self.processed_samples = 0

        if METRICS_ENABLED:
            samples_since_drift.set(0)
            drift_detected_flag.set(0)