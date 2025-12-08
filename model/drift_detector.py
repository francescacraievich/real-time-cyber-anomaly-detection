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
    def __init__(self, threshold=0.002, window_size=100, change_threshold=0.08):
        # ADWIN for detecting changes in average values
        self.adwin = drift.ADWIN(delta=threshold)
        self.history = deque(maxlen=window_size)  # Current window
        self.drift_detected = False
        self.processed_samples = 0
        self.change_threshold = change_threshold  # 8% change triggers drift
        self.last_reported_rate = None  # Track last rate when drift was reported/checked
        self.check_interval = 50  # Check for drift every N samples
        self.last_drift_sample = None  # Track when last drift occurred
        self.min_unstable_duration = 100  # Stay UNSTABLE for at least N samples (~4 sec)

    def update(self, is_anomaly):
        # Convert boolean to integer (1 for Anomaly, 0 for Benign)
        val = 1 if is_anomaly else 0

        # Update our sliding window history
        self.history.append(val)
        self.processed_samples += 1

        # Feed the binary value to ADWIN
        self.adwin.update(val)

        # Update metrics
        if METRICS_ENABLED:
            anomaly_rate_gauge.set(self.get_current_anomaly_rate())
            samples_since_drift.set(self.processed_samples)

        # Check for drift using multiple methods
        drift_occurred = False

        # Method 1: ADWIN detection
        if self.adwin.drift_detected:
            drift_occurred = True
            print(f"[DriftDetector] ADWIN detected drift at sample {self.processed_samples}")

        # Method 2: Simple threshold-based detection (check every N samples after window is full)
        if len(self.history) >= self.history.maxlen and self.processed_samples % self.check_interval == 0:
            current_rate = self.get_current_anomaly_rate()

            # Initialize last_reported_rate on first check
            if self.last_reported_rate is None:
                self.last_reported_rate = current_rate
            else:
                # Check if current rate differs significantly from last reported
                rate_change = abs(current_rate - self.last_reported_rate)
                if rate_change >= self.change_threshold:
                    drift_occurred = True
                    print(f"[DriftDetector] Rate change detected: {self.last_reported_rate:.2%} -> {current_rate:.2%} (delta: {rate_change:.2%})")
                    self.last_reported_rate = current_rate

        if drift_occurred:
            self.drift_detected = True
            self.last_drift_sample = self.processed_samples
            if METRICS_ENABLED:
                drift_detected_total.inc()
                drift_detected_flag.set(1)
            return True

        # If we just did a check (every check_interval) and no drift was found
        if len(self.history) >= self.history.maxlen and self.processed_samples % self.check_interval == 0:
            # Only go back to stable if enough time has passed since last drift
            if self.last_drift_sample is None:
                # No drift ever detected, stay stable
                self.drift_detected = False
                if METRICS_ENABLED:
                    drift_detected_flag.set(0)
            else:
                samples_since_last = self.processed_samples - self.last_drift_sample
                if samples_since_last >= self.min_unstable_duration:
                    # Enough time passed, back to stable
                    self.drift_detected = False
                    if METRICS_ENABLED:
                        drift_detected_flag.set(0)
                # else: stay UNSTABLE until min_unstable_duration passes

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
        self.last_reported_rate = None
        self.last_drift_sample = None
        self.processed_samples = 0

        if METRICS_ENABLED:
            samples_since_drift.set(0)
            drift_detected_flag.set(0)