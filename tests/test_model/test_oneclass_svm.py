import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.svm import OneClassSVM

# Import your actual classes
# Adjust the import path based on your project structure
import sys
sys.path.append(str(Path(__file__).parents[2])) # Add project root to path

from model.oneCSVM_model import OneClassSVMModel
from model.drift_detector import DriftDetector

# --- Fixtures (Setup data for tests) ---

@pytest.fixture
def sample_data():
    # Creating dummy dataset for testing
    df = pd.DataFrame({
        'source_ip': ['192.168.1.1', '10.0.0.1', '192.168.1.2'] * 10,
        'destination_ip': ['8.8.8.8', '1.1.1.1', '8.8.4.4'] * 10,
        'bytes_in': np.random.randint(100, 1000, 30),
        'bytes_out': np.random.randint(100, 1000, 30),
        'transport_protocol': ['TCP', 'UDP', 'TCP'] * 10,
        'application_protocol': ['HTTP', 'DNS', 'HTTPS'] * 10,
        'label': ['benign'] * 30
    })
    # Add necessary columns that might be expected by feature engineering
    df['direction'] = 'outbound'
    df['day_of_week'] = 1
    df['is_weekend'] = 0
    df['is_business_hours'] = 1
    df['src_is_private'] = 1
    df['dst_is_private'] = 0
    df['is_internal'] = 0
    df['dst_port_is_common'] = 1
    
    return df

@pytest.fixture
def model_instance():
    # Creating a fresh model instance -> UNTRAINED
    return OneClassSVMModel(nu=0.1, kernel='rbf', gamma='scale')





# --- Tests for OneClassSVMModel ---

class TestOneClassSVMModel:

    def test_initialization(self, model_instance):
        """Test if model initializes with correct parameters"""
        assert isinstance(model_instance.model, OneClassSVM)
        assert model_instance.model.nu == 0.1
        assert model_instance.model.kernel == 'rbf'

    def test_fit_runs_without_error(self, model_instance, sample_data):
        """Test if the fit method runs successfully on benign data"""
        try:
            # Run fit with a small sample count
            model_instance.fit(sample_data, max_train_samples=20, contamination=0.1)
            assert model_instance.threshold_boundary != 0.0
            assert model_instance.preprocessor is not None
        except Exception as e:
            pytest.fail(f"Model fitting failed with error: {e}")

    def test_prediction_structure(self, model_instance, sample_data):
        """Test if predict returns the correct format (severity, message, score)"""
        # Train first
        model_instance.fit(sample_data, max_train_samples=20)
        
        # Predict on a few rows
        test_rows = sample_data.iloc[:5]
        results = model_instance.predict(test_rows)
        
        assert len(results) == 5
        for res in results:
            assert len(res) == 3 # (severity, msg, score)
            assert res[0] in ["GREEN", "ORANGE", "RED"]
            assert isinstance(res[2], float)

    def test_save_and_load(self, model_instance, sample_data, tmp_path):
        """Test if model can be saved and loaded correctly"""
        # Override paths to use temporary test directory
        model_instance.model_path = tmp_path / "test_model.pkl"
        model_instance.preprocessor_path = tmp_path / "test_preprocessor.pkl"
        model_instance.config_path = tmp_path / "test_config.pkl"
        
        # Train and save
        model_instance.fit(sample_data, max_train_samples=20)
        model_instance.save_model()
        
        assert model_instance.model_path.exists()
        
        # Create new instance and load
        new_model = OneClassSVMModel()
        new_model.model_path = tmp_path / "test_model.pkl"
        new_model.preprocessor_path = tmp_path / "test_preprocessor.pkl"
        new_model.config_path = tmp_path / "test_config.pkl"
        
        loaded = new_model.load_model()
        
        assert loaded is True
        assert new_model.threshold_boundary == model_instance.threshold_boundary





# --- Tests for DriftDetector ---

class TestDriftDetector:
    
    def test_drift_detection_logic(self):
        """Test if drift detector triggers on changing anomaly rate"""
        # Use a small threshold for faster detection in tests
        detector = DriftDetector(threshold=0.01)
        
        # Phase 1: Stable Normal Traffic (All Green / False)
        # The anomaly rate is 0%
        drift_detected = False
        for _ in range(50):
            # update() now takes a boolean: False = Normal
            if detector.update(False): 
                drift_detected = True
        
        assert drift_detected is False, "Drift detected too early on stable data"
        
        # Phase 2: Sudden Attack (All Red / True)
        # The anomaly rate shifts from 0% to 100%
        drift_detected = False
        for _ in range(100):
            # update() now takes a boolean: True = Anomaly
            if detector.update(True): 
                drift_detected = True
                break
                
        assert drift_detected is True, "Drift failed to detect shift from Normal to Anomaly"

    def test_reset(self):
        """Test if reset clears the state"""
        detector = DriftDetector()
        detector.drift_detected = True
        
        # Add some history
        detector.history.append(1)
        
        detector.reset()
        
        assert detector.drift_detected is False
        assert len(detector.history) == 0 # History should be cleared too