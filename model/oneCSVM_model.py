import os
import sys
from pathlib import Path

from matplotlib import cm
from sklearn.metrics import confusion_matrix


project_root = Path(__file__).resolve().parents[1]

 
# Add feature_engineering to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#from feature_engineering.df_initializing.handler_init_dfs import DataFrameInitializer
#from feature_engineering.df_formatting.handler_df_formatter import DataFrameFormatter
import pandas as pd
import numpy as np
import joblib
import pickle
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score



class OneClassSVMModel:
    def __init__(self, nu=0.5, kernel="rbf", gamma='scale'):

        self.random_state = 42

        # One-Class SVM (Kernel='rbf' is standard for non-linear boundaries)
        self.model = OneClassSVM(
            kernel=kernel,
            nu=nu,
            gamma=gamma,
            verbose=True # Useful to see progress as SVM is slow
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
    
    def _configure_features(self, df):
        # Identify categorical and numerical features
        self.features_to_drop = ['source_ip', 'destination_ip', 'timestamp_start', 'label',
            'malicious_events_in_window', 'unique_malicious_ips', 
            'malicious_events_pct_change', 'malicious_events_for_protocol', 
            'malicious_ratio_for_protocol'
        ]

        self.cat_features = [
            'transport_protocol', 'application_protocol', 'direction',
            'day_of_week', 'is_weekend', 'is_business_hours', 'src_is_private',
           'dst_is_private', 'is_internal', 'dst_port_is_common'
        ]

         

        self.num_features = [col for col in df.columns if col not in self.cat_features and col not in self.features_to_drop]

        self.preprocessor = ColumnTransformer(
            transformers = [
                ('num', RobustScaler(), self.num_features),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output= False), 
                 [col for col in self.cat_features if col in df.columns])
            ]
        )
        
    def save_model(self):
        """Save the trained model, preprocessor, and configuration"""
        try:
            print("[System] Saving model components...")
            
            # Save the SVM model
            joblib.dump(self.model, self.model_path)
            
            # Save the preprocessor
            joblib.dump(self.preprocessor, self.preprocessor_path)
            
            # Save configuration (features, threshold, etc.)
            config = {
                'threshold_boundary': self.threshold_boundary,
                'features_to_drop': self.features_to_drop,
                'cat_features': self.cat_features,
                'num_features': self.num_features,
                'random_state': self.random_state
            }
            with open(self.config_path, 'wb') as f:
                pickle.dump(config, f)
            
            print(f"   -> Model saved to: {self.model_path}")
            print(f"   -> Preprocessor saved to: {self.preprocessor_path}")
            print(f"   -> Config saved to: {self.config_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save model: {e}")
    
    def load_model(self):
        """Load the trained model, preprocessor, and configuration"""
        try:
            print("[System] Loading existing model...")
            
            # Load the SVM model
            self.model = joblib.load(self.model_path)
            
            # Load the preprocessor
            self.preprocessor = joblib.load(self.preprocessor_path)
            
            # Load configuration
            with open(self.config_path, 'rb') as f:
                config = pickle.load(f)
            
            self.threshold_boundary = config['threshold_boundary']
            self.features_to_drop = config['features_to_drop']
            self.cat_features = config['cat_features']
            self.num_features = config['num_features']
            self.random_state = config['random_state']
            
            print(f"   -> Model loaded from: {self.model_path}")
            print(f"   -> Threshold boundary: {self.threshold_boundary:.4f}")
            print(f"   -> Features configured: {len(self.num_features)} numeric, {len(self.cat_features)} categorical")
            
            return True
            
        except Exception as e:
            print(f"[System] Could not load existing model: {e}")
            return False
    
    def model_exists(self):
        """Check if all required model files exist"""
        return (self.model_path.exists() and 
                self.preprocessor_path.exists() and 
                self.config_path.exists())

    def fit(self, df_benign, max_train_samples=50000, contamination=0.05):
        """
        Trains the One-Class SVM on Benign data.
        
        Args:
            max_train_samples (int): SVM scales poorly (O(n^2)). 
            We limit training size to keep it fast.
        """

        print("[System] Configuring features...")
        self._configure_features(df_benign)

        print("[System] Configuring features...")
        X_benign = df_benign.drop(columns=self.features_to_drop, errors='ignore')

        # 1. Split for Train/Validation
        X_train, X_val = train_test_split(
            X_benign, test_size=0.2, random_state=self.random_state
        )

        # 2. Downsample for SVM Speed (Critical Step for Large Datasets)
        if len(X_train) > max_train_samples:
            X_train = X_train.sample(n=max_train_samples, random_state=self.random_state)

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

        # We set the boundary such that 99% of our validation data is considered "Normal"
        self.threshold_boundary = np.percentile(scores, contamination * 100)
        print(f"   -> Decision Boundary adjusted to: {self.threshold_boundary:.4f}")

        # 6. Save Model
        self.save_model()

    
    def fit_or_load(self, df_benign, max_train_samples=50000, contamination=0.05):
        """
        Either load existing model or train a new one
        """
        if self.model_exists():
            print("[System] Found existing model files.")
            if self.load_model():
                print("[System] Successfully loaded existing model.")
                return True
            else:
                print("[System] Failed to load existing model. Training new one...")
        else:
            print("[System] No existing model found. Training new model...")
        
        # Train new model
        self.fit(df_benign, max_train_samples, contamination)
        return True
    
    
    def predict(self, row_data):
        """
        Returns: (severity_color, description, distance_score)
        """
        try:
            X_processed = self.preprocessor.transform(row_data)
        except Exception as e:
            return [("ERROR", str(e), 0.0)] * len(row_data)

        scores = self.model.decision_function(X_processed)

        results = []
        for i in range(len(row_data)):
            score = scores[i]
            
            # Distance logic
            if score < self.threshold_boundary:
                # Far outside the boundary -> High Severity
                if score < (self.threshold_boundary - 0.5): 
                    results.append(("RED", "CRITICAL: Far outside normal boundary", score))
                else:
                    results.append(("ORANGE", "SUSPICIOUS: Just outside boundary", score))
            else:
                results.append(("GREEN", "Normal", score))
                
        return results
    

    
    def run_simulation(self, stream_df, chunk_size=10):
        print("\n" + "="*50)
        print("STARTING ONE-CLASS SVM STREAM")
        print("="*50)

        # Check for labels in the combined dataset
        has_labels = 'label' in stream_df.columns
        true_labels = stream_df['label'] if has_labels else None

        stream_input = stream_df.drop(columns=self.features_to_drop, errors='ignore')

        COLOR_RED = '\033[91m'
        COLOR_ORANGE = '\033[93m'
        COLOR_RESET = '\033[0m'

        anomaly_count = 0
        total_processed = 0

        for i in range(0, len(stream_input), chunk_size):
            time.sleep(0.1)
            chunk = stream_input.iloc[i : i+chunk_size]
            if chunk.empty: break
            
            batch_results = self.predict(chunk)
            
            print(f"\n--- Batch {i//chunk_size + 1} ---")
            for idx, (severity, msg, score) in enumerate(batch_results):
                global_idx = i + idx
                total_processed += 1
                
                # Format "Actual" label if available
                actual_text = ""
                if has_labels:
                    lbl = true_labels.iloc[global_idx]
                    actual_text = f"| Actual: {lbl}"

                # Apply colors based on severity
                if severity != "GREEN":
                    color = COLOR_RED if severity == "RED" else COLOR_ORANGE
                    print(f"{color}[{severity}] [ROW {global_idx}] {msg} | Dist: {score:.3f} {actual_text}{COLOR_RESET}")
                    anomaly_count += 1
            
            if i > 100: 
                break

        print(f"\n[Simulation stopped - Processed {total_processed} samples]")
        print(f"[Detection Summary: {anomaly_count} anomalies detected out of {total_processed} samples]")
    
        






    def run_detailed_simulation(self, stream_df, chunk_size=50):
        print("\n" + "="*50)
        print("DETAILED ONE-CLASS SVM ANALYSIS")
        print("="*50)

        # Check for labels
        has_labels = 'label' in stream_df.columns
        if not has_labels:
            print("[Warning] No labels found. Cannot evaluate performance.")
            return

        stream_input = stream_df.drop(columns=self.features_to_drop, errors='ignore')
        true_labels = stream_df['label']

        # Track performance by label type
        benign_correct = 0
        benign_total = 0
        attack_detected = 0
        attack_total = 0
    
        # Track severity distribution
        severity_counts = {'GREEN': 0, 'ORANGE': 0, 'RED': 0}
    
        # Track by attack type if available
        attack_types = {}

        print(f"Processing {len(stream_df)} samples...")
    
        # Process in larger chunks for efficiency
        for i in range(0, len(stream_input), chunk_size):
            chunk_input = stream_input.iloc[i:i+chunk_size]
            chunk_labels = true_labels.iloc[i:i+chunk_size]
        
            if chunk_input.empty:
                break
            
            batch_results = self.predict(chunk_input)
        
            # Analyze each prediction
            for idx, (severity, msg, score) in enumerate(batch_results):
                actual_label = chunk_labels.iloc[idx]
            
                # Count severity distribution
                severity_counts[severity] += 1
            
                # Track performance by actual label
                if actual_label == "benign":
                    benign_total += 1
                    if severity == "GREEN":
                        benign_correct += 1
                else:
                    attack_total += 1
                    if severity != "GREEN":
                        attack_detected += 1
                
                    # Track attack types
                    if actual_label not in attack_types:
                        attack_types[actual_label] = {'detected': 0, 'total': 0}
                    attack_types[actual_label]['total'] += 1
                    if severity != "GREEN":
                        attack_types[actual_label]['detected'] += 1
        
            # Print progress every 500 samples
            if (i + chunk_size) % 500 == 0:
                processed = min(i + chunk_size, len(stream_input))
                print(f"   Processed: {processed}/{len(stream_input)} samples...")
    
        # Print detailed results
        print(f"\n SIMULATION RESULTS:")
        print(f"   Total Samples: {len(stream_df)}")
        print(f"   Benign Samples: {benign_total}")
        print(f"   Attack Samples: {attack_total}")
    
        print(f"\n DETECTION PERFORMANCE:")
        if benign_total > 0:
            benign_accuracy = benign_correct / benign_total
            false_alarm_rate = (benign_total - benign_correct) / benign_total
            print(f"   • Benign Classification: {benign_correct}/{benign_total} ({benign_accuracy:.3f})")
            print(f"   • False Alarm Rate: {false_alarm_rate:.3f}")
    
        if attack_total > 0:
            attack_detection_rate = attack_detected / attack_total
            print(f"   • Attack Detection: {attack_detected}/{attack_total} ({attack_detection_rate:.3f})")
    
        #print(f"\n SEVERITY DISTRIBUTION:")
        #for severity, count in severity_counts.items():
           # percentage = (count / len(stream_df)) * 100
            #print(f"   • {severity}: {count} ({percentage:.1f}%)")
    
        if attack_types:
            print(f"\n PERFORMANCE BY ATTACK TYPE:")
            for attack_type, stats in attack_types.items():
                detection_rate = stats['detected'] / stats['total']
                print(f"   • {attack_type}: {stats['detected']}/{stats['total']} ({detection_rate:.3f})")

        return {
            'benign_accuracy': benign_correct / benign_total if benign_total > 0 else 0,
            'attack_detection_rate': attack_detected / attack_total if attack_total > 0 else 0,
            'false_alarm_rate': (benign_total - benign_correct) / benign_total if benign_total > 0 else 0,
            'severity_distribution': severity_counts,
            'attack_type_performance': attack_types
        }
    

    def evaluate_model_performance(self, test_df):
        print("\n" + "="*60)
        print("MODEL PERFORMANCE EVALUATION")
        print("="*60)
    
        # Prepare test data
        stream_input = test_df.drop(columns=self.features_to_drop, errors='ignore')
        true_labels = test_df['label']
    
        # Get predictions
        predictions = self.predict(stream_input)
    
        # Convert predictions to binary (0 = normal, 1 = anomaly)
        predicted_labels = [1 if pred[0] != "GREEN" else 0 for pred in predictions]
    
        # Convert true labels to binary
        true_binary = [0 if label == "benign" else 1 for label in true_labels]
    
        # Calculate metrics
        precision = precision_score(true_binary, predicted_labels, zero_division=0)
        recall = recall_score(true_binary, predicted_labels, zero_division=0)
        f1 = f1_score(true_binary, predicted_labels, zero_division=0)
    
        print(f"PERFORMANCE METRICS:")
        print(f"   • Precision: {precision:.3f} (What % of flagged anomalies are actually anomalies)")
        print(f"   • Recall:    {recall:.3f} (What % of actual anomalies were detected)")
        print(f"   • F1-Score:  {f1:.3f} (Overall balance between precision and recall)")
    
        # Confusion Matrix
        cm = confusion_matrix(true_binary, predicted_labels)
        print(f"\n CONFUSION MATRIX:")
        print("              Predicted")
        print("              Normal  Anomaly")
        print(f"Actual Normal   {cm[0][0]:4d}    {cm[0][1]:4d}")
        print(f"Actual Anomaly  {cm[1][0]:4d}    {cm[1][1]:4d}")
    
        # Detailed breakdown
        tn, fp, fn, tp = cm.ravel()
        print(f"\n DETAILED BREAKDOWN:")
        print(f"   • True Negatives (Correct Normal):     {tn:4d}")
        print(f"   • False Positives (False Alarms):      {fp:4d}")
        print(f"   • False Negatives (Missed Attacks):    {fn:4d}")
        print(f"   • True Positives (Detected Attacks):   {tp:4d}")
    
        # Calculate rates
        total_normal = tn + fp
        total_anomaly = fn + tp
        false_alarm_rate = fp / total_normal if total_normal > 0 else 0
        detection_rate = tp / total_anomaly if total_anomaly > 0 else 0
    
        print(f"\n KEY RATES:")
        print(f"   • Detection Rate:    {detection_rate:.3f} ({detection_rate*100:.1f}%)")
        print(f"   • False Alarm Rate:  {false_alarm_rate:.3f} ({false_alarm_rate*100:.1f}%)")
    
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'detection_rate': detection_rate,
            'false_alarm_rate': false_alarm_rate,
            'confusion_matrix': cm
        }





if __name__ == "__main__":
    data_path = project_root / "data" / "processed"
    
    print("1. Loading Datasets...")

    try:
        # Load specific files
        df_benign = pd.read_csv(data_path / "normal_traffic_formatted.csv")
        df_combined = pd.read_csv(data_path / "combined_shuffled_dataset.csv")
        #df_suricata = pd.read_csv(data_path / "suricata_formatted.csv")
        print(f"   -> Loaded {len(df_benign)} benign logs and {len(df_combined)} bombined logs.")
        
        # Ensure benign label column exists (mostly for consistency, SVM ignores the column anyway)
        if 'label' not in df_benign.columns: df_benign['label'] = 'benign'

    except FileNotFoundError:
        print("\n[ERROR] Files not found. Please update PATH variables in the script.")
        print("Please ensure the CSV files exist in the 'data/processed' directory.\n")


    # Running system
    print("\n2. Initializing One-Class SVM...")
    svm_detector = OneClassSVMModel(nu=0.2, gamma='scale')

    print("\n3. Training or loading model...")
    svm_detector.fit_or_load(df_benign, max_train_samples=10000, contamination=0.1)

    print("\n4. Running anomaly detection simulation on new_df_combined...")
    #new_df_combined = df_combined.sample(n=40000, random_state=42)
    print(df_combined['label'].head(40))
    svm_detector.run_simulation(df_combined)


    print("5. Evaluating model performance...")
    # Test on a subset for evaluation
    test_sample = df_combined.sample(n=10000, random_state=42)  # Sample for faster evaluation
    
    # Method 1: Detailed performance metrics
    performance_metrics = svm_detector.evaluate_model_performance(test_sample)
    

    print("\n6. Running anomaly detection detailed simulation...")
    # Method 2: Detailed simulation
    simulation_results = svm_detector.run_detailed_simulation(test_sample)
    
    print("\n7. Model Quality Assessment:")
    
    # Good performance indicators:
    if performance_metrics['f1_score'] > 0.7:
        print(" Good F1-Score (>0.7)")
    else:
        print("  Low F1-Score (<0.7) - Consider tuning parameters")
    
    if simulation_results['false_alarm_rate'] < 0.1:
        print(" Low False Alarm Rate (<10%)")
    else:
        print("  High False Alarm Rate (>10%) - Too many false positives")
    
    if simulation_results['attack_detection_rate'] > 0.8:
        print(" Good Attack Detection Rate (>80%)")
    else:
        print("  Low Attack Detection Rate (<80%) - Missing too many attacks")

    










