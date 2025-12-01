from river import drift
import numpy as np

class DriftDetector:
    def __init__(self, threshold=0.002):
        # ADWIN for detecting changes in average values
        self.adwin = drift.ADWIN(delta=threshold)
        self.drift_detected = False
        self.processed_samples = 0

    def update(self, anomaly_score):
        # Updating drift detector with latest anomaly score
        self.adwin.update(anomaly_score)
        self.processed_samples += 1

        if self.adwin.drift_detected:
            self.drift_detected = True
            return True
        
        return False
    
    def reset(self):
        # Reset the detector after retraining
        self.adwin = drift.ADWIN(delta=self.adwin.delta)
        self.drift_detected = False