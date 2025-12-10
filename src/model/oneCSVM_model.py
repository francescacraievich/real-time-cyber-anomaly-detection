# from feature_engineering.df_initializing.handler_init_dfs import DataFrameInitializer
# from feature_engineering.df_formatting.handler_df_formatter import DataFrameFormatter
import os
import pickle
import sys
import time
from collections import deque
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.svm import OneClassSVM

# Prometheus metrics (optional - graceful fallback if not available)
try:
    from src.monitoring.metrics import (
        anomalies_detected_total,
        decision_score_histogram,
        model_info,
        model_retrain_total,
        prediction_latency,
        predictions_total,
        retrain_buffer_size,
        samples_processed_total,
    )
    from src.monitoring.metrics import threshold_boundary as threshold_boundary_metric

    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False


project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class OneClassSVMModel:
    def __init__(self, nu=0.5, kernel="rbf", gamma="scale"):

        self.random_state = 42

        # One-Class SVM (Kernel='rbf' is standard for non-linear boundaries)
        self.model = OneClassSVM(
            kernel=kernel,
            nu=nu,
            gamma=gamma,
            verbose=True,  # Useful to see progress as SVM is slow
        )

        self.preprocessor = None
        self.threshold_boundary = 0.0
        self.features_to_drop = []
        self.cat_features = []
        self.num_features = []

        # Model persistence
        self.model_dir = Path(__file__).parent  # model folder
        self.model_path = self.model_dir / "oneclass_svm_model.pkl"
        self.preprocessor_path = self.model_dir / "oneclass_svm_preprocessor.pkl"
        self.config_path = self.model_dir / "oneclass_svm_config.pkl"

        # Best parameters from tuning
        self.best_params = None

        # Add a buffer for retraining
        self.retrain_buffer = deque(
            maxlen=5000
        )  # Store recent samples for potential retraining

    def add_to_buffer(self, df_chunk):
        # Storing recent data for potential retraining
        for _, row in df_chunk.iterrows():
            self.retrain_buffer.append(row)

        # Update metrics
        if METRICS_ENABLED:
            retrain_buffer_size.set(len(self.retrain_buffer))

    def retrain(self):
        # Retraining model on buffered data
        if len(self.retrain_buffer) < 1000:
            print("[System] Not enough data in buffer to retrain.")
            return False

        print(
            f"[Drift] Retraining model on {len(self.retrain_buffer)} recent samples..."
        )

        # Converting buffer back to DataFrame
        df_recent = pd.DataFrame(self.retrain_buffer)

        self.fit(df_recent, max_train_samples=len(df_recent), contamination=0.1)

        # Update metrics
        if METRICS_ENABLED:
            model_retrain_total.inc()
            retrain_buffer_size.set(len(self.retrain_buffer))

        print("[Drift] Model retrained successfully.")
        return True

    def _configure_features(self, df):
        # Identify categorical and numerical features
        self.features_to_drop = [
            "source_ip",
            "destination_ip",
            "timestamp_start",
            "label",
            "malicious_events_in_window",
            "unique_malicious_ips",
            "malicious_events_pct_change",
            "malicious_events_for_protocol",
            "malicious_ratio_for_protocol",
        ]

        self.cat_features = [
            "transport_protocol",
            "application_protocol",
            "direction",
            "day_of_week",
            "is_weekend",
            "is_business_hours",
            "src_is_private",
            "dst_is_private",
            "is_internal",
            "dst_port_is_common",
        ]

        self.num_features = [
            col
            for col in df.columns
            if col not in self.cat_features and col not in self.features_to_drop
        ]

        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", RobustScaler(), self.num_features),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    [col for col in self.cat_features if col in df.columns],
                ),
            ]
        )

    def save_model(self):
        # Saving the model, preprocessor and configuration in suitable pickle files

        try:
            print("[System] Saving model components...")

            # Save the SVM model
            joblib.dump(self.model, self.model_path)

            # Save the preprocessor
            joblib.dump(self.preprocessor, self.preprocessor_path)

            # Save configuration (features, threshold, etc.)
            config = {
                "threshold_boundary": self.threshold_boundary,
                "features_to_drop": self.features_to_drop,
                "cat_features": self.cat_features,
                "num_features": self.num_features,
                "random_state": self.random_state,
            }
            with open(self.config_path, "wb") as f:
                pickle.dump(config, f)

            print(f" -> Model saved to: {self.model_path}")
            print(f" -> Preprocessor saved to: {self.preprocessor_path}")
            print(f" -> Config saved to: {self.config_path}")

        except Exception as e:
            print(f"[ERROR] Failed to save model: {e}")

    def load_model(self):
        # Loading the model, preprocessor and configuration files
        try:
            print("[System] Loading existing model...")

            # Load the SVM model
            self.model = joblib.load(self.model_path)

            # Load the preprocessor
            self.preprocessor = joblib.load(self.preprocessor_path)

            # Load configuration
            with open(self.config_path, "rb") as f:
                config = pickle.load(f)

            self.threshold_boundary = config["threshold_boundary"]
            self.features_to_drop = config["features_to_drop"]
            self.cat_features = config["cat_features"]
            self.num_features = config["num_features"]
            self.random_state = config["random_state"]

            if "best_params" in config:
                self.best_params = config["best_params"]
                print(f"   -> Best parameters: {self.best_params}")

            print(f" -> Model loaded from: {self.model_path}")
            print(f" -> Threshold boundary: {self.threshold_boundary:.4f}")

            # Update Prometheus metric
            if METRICS_ENABLED:
                threshold_boundary_metric.set(self.threshold_boundary)
            print(
                f" -> Features configured: {len(self.num_features)} numeric, {len(self.cat_features)} categorical"
            )

            return True

        except Exception as e:
            print(f"[System] Could not load existing model: {e}")
            return False

    def model_exists(self):
        # Checking if all model components exist
        return (
            self.model_path.exists()
            and self.preprocessor_path.exists()
            and self.config_path.exists()
        )

    def fit(self, df_benign, max_train_samples=50000, contamination=0.05):

        print("[System] Configuring features...")
        self._configure_features(df_benign)

        print("[System] Dropping selected features...")
        X_benign = df_benign.drop(columns=self.features_to_drop, errors="ignore")

        # 1. Split for Train/Validation
        X_train, X_val = train_test_split(
            X_benign, test_size=0.2, random_state=self.random_state
        )

        # 2. Downsample for SVM Speed (Critical Step for Large Datasets)
        if len(X_train) > max_train_samples:
            X_train = X_train.sample(
                n=max_train_samples, random_state=self.random_state
            )

        # 3. Fit Preprocessor
        self.preprocessor.fit(X_train)
        X_train_processed = self.preprocessor.transform(X_train)

        # 4. Train SVM
        print("[System] Training One-Class SVM (This may take a moment)...")
        self.model.fit(X_train_processed)
        print("[System] Training Complete.")

        # 5. Calibrate Thresholds
        print("[System] Calibrating Threshold on Validation Set...")
        X_val_processed = self.preprocessor.transform(X_val)
        scores = self.model.decision_function(X_val_processed)

        self.threshold_boundary = np.percentile(scores, contamination * 100)
        print(f" -> Decision Boundary adjusted to: {self.threshold_boundary:.4f}")

        # Update metrics
        if METRICS_ENABLED:
            threshold_boundary_metric.set(self.threshold_boundary)

        # 6. Save Model
        self.save_model()

    def predict(self, row_data):
        # Predicting distance scores and severity levels for new data
        start_time = time.time()

        try:
            X_processed = self.preprocessor.transform(row_data)
        except Exception as e:
            return [("ERROR", str(e), 0.0)] * len(row_data)

        scores = self.model.decision_function(X_processed)

        results = []
        for i in range(len(row_data)):
            score = scores[i]

            # Record decision score in histogram
            if METRICS_ENABLED:
                decision_score_histogram.observe(score)

            # Distance logic
            if score < self.threshold_boundary:
                # Far outside the boundary -> High Severity
                if score < (self.threshold_boundary - 0.5):
                    results.append(
                        ("RED", "CRITICAL: Far outside normal boundary", score)
                    )
                else:
                    results.append(
                        ("ORANGE", "SUSPICIOUS: Just outside boundary", score)
                    )
            else:
                results.append(("GREEN", "Normal", score))

        # Update metrics
        if METRICS_ENABLED:
            duration = time.time() - start_time
            prediction_latency.observe(duration)
            samples_processed_total.inc(len(row_data))

            for severity, _, _ in results:
                predictions_total.labels(severity=severity).inc()
                if severity != "GREEN":
                    anomalies_detected_total.inc()

        return results

    def update_model_parameters(self, best_params):
        # Update model with new parameters
        self.best_params = best_params
        self.model = OneClassSVM(**best_params)
