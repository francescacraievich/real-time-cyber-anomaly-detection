from river import drift
import numpy as np
from collections import deque

class DriftDetector:
    def __init__(self, threshold=0.05, window_size=10):
        # ADWIN for detecting changes in average values
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

        if self.adwin.drift_detected:
            self.drift_detected = True
            return True
        
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