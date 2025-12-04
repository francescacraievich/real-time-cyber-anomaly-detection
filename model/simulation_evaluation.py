import time
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from drift_detector import DriftDetector


class SimulationEvaluator:
    def __init__(self, model_instance):
        self.model = model_instance
        self.drift_detector = DriftDetector(threshold=0.001)


            ###########      SIMULATION METHODS      ###########


    def run_simulation(self, stream_df, chunk_size=10):
        
        print("\n" + "="*50)
        print("STARTING ONE-CLASS SVM STREAM")
        print("="*50)

        # Check for labels in the combined dataset
        has_labels = 'label' in stream_df.columns
        true_labels = stream_df['label'] if has_labels else None

        stream_input = stream_df.drop(columns=self.model.features_to_drop, errors='ignore')

        COLOR_RED = '\033[91m'
        COLOR_ORANGE = '\033[93m'
        COLOR_GREEN = '\033[92m'
        COLOR_RESET = '\033[0m'

        anomaly_count = 0
        total_processed = 0


        print("STARTING STREAM WITH DRIFT DETECTION")
        for i in range(0, len(stream_input), chunk_size):
            #time.sleep(1)  # Simulate real-time delay
            chunk = stream_input.iloc[i : i+chunk_size]
            if chunk.empty: 
                break
            
            # Add data to model buffer
            self.model.add_to_buffer(chunk)

            # Predict
            batch_results = self.model.predict(chunk)  

            # Checking for drift
            drift_flag = False
            for severity, msg, score in batch_results:
                # Determine if this specific log is an anomaly
                is_anomaly = (severity != "GREEN")
                
                # Update detector with the BOOLEAN status, not the score
                if self.drift_detector.update(is_anomaly):
                    drift_flag = True
            
            if drift_flag:
                current_rate = self.drift_detector.get_current_anomaly_rate()
                print(f" CONCEPT DRIFT DETECTED! Anomaly Rate shifted to {current_rate:.1%}")
                
                if self.model.retrain():
                    self.drift_detector.reset()
                    print(" Resuming stream with updated model...")
                    
            
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
                if severity == "RED":
                    color = COLOR_RED
                    anomaly_count += 1
                elif severity == "ORANGE":
                    color = COLOR_ORANGE
                    anomaly_count += 1
                else:  # severity == "GREEN"
                    color = COLOR_GREEN
                    
                print(f"{color}[{severity}] [ROW {global_idx}] {msg} | Dist: {score:.3f} {actual_text}{COLOR_RESET}")
                time.sleep(1)  
            
            if i > 100: 
                break

        print(f"\n[Simulation stopped - Processed {total_processed} samples]")
        print(f"[Detection Summary: {anomaly_count} anomalies detected out of {total_processed} samples]")




    def run_detailed_simulation(self, stream_df, chunk_size=50):
        """Run detailed simulation with performance tracking"""
        print("\n" + "="*50)
        print("DETAILED ONE-CLASS SVM ANALYSIS")
        print("="*50)

        # Check for labels
        has_labels = 'label' in stream_df.columns
        if not has_labels:
            print("[Warning] No labels found. Cannot evaluate performance.")
            return

        stream_input = stream_df.drop(columns=self.model.features_to_drop, errors='ignore')
        true_labels = stream_df['label']

        # Initialize tracking variables
        performance_stats = self._initialize_performance_stats()
        
        print(f"Processing {len(stream_df)} samples...")
    
        # Process in chunks
        for i in range(0, len(stream_input), chunk_size):
            chunk_input = stream_input.iloc[i:i+chunk_size]
            chunk_labels = true_labels.iloc[i:i+chunk_size]
        
            if chunk_input.empty:
                break
            
            batch_results = self.model.predict(chunk_input)
            
            # Update performance statistics
            self._update_performance_stats(performance_stats, batch_results, chunk_labels)
        
            # Print progress
            if (i + chunk_size) % 500 == 0:
                processed = min(i + chunk_size, len(stream_input))
                print(f"   Processed: {processed}/{len(stream_input)} samples...")
    
        # Calculate final metrics and display results
        final_metrics = self._calculate_final_metrics(performance_stats, len(stream_df))
        self._display_simulation_results(final_metrics)

        return final_metrics

    def _initialize_performance_stats(self):
        """Initialize performance tracking variables"""
        return {
            'benign_correct': 0,
            'benign_total': 0,
            'attack_detected': 0,
            'attack_total': 0,
            'severity_counts': {'GREEN': 0, 'ORANGE': 0, 'RED': 0},
            'attack_types': {}
        }

    def _update_performance_stats(self, stats, batch_results, chunk_labels):
        """Update performance statistics with batch results"""
        for idx, (severity, msg, score) in enumerate(batch_results):
            actual_label = chunk_labels.iloc[idx]
        
            # Count severity distribution
            stats['severity_counts'][severity] += 1
        
            # Track performance by actual label
            if actual_label == "benign":
                stats['benign_total'] += 1
                if severity == "GREEN":
                    stats['benign_correct'] += 1
            else:
                stats['attack_total'] += 1
                if severity != "GREEN":
                    stats['attack_detected'] += 1
            
                # Track attack types
                if actual_label not in stats['attack_types']:
                    stats['attack_types'][actual_label] = {'detected': 0, 'total': 0}
                stats['attack_types'][actual_label]['total'] += 1
                if severity != "GREEN":
                    stats['attack_types'][actual_label]['detected'] += 1

    def _calculate_final_metrics(self, stats, total_samples):
        """Calculate final performance metrics"""
        return {
            'total_samples': total_samples,
            'benign_total': stats['benign_total'],
            'attack_total': stats['attack_total'],
            'benign_accuracy': stats['benign_correct'] / stats['benign_total'] if stats['benign_total'] > 0 else 0,
            'attack_detection_rate': stats['attack_detected'] / stats['attack_total'] if stats['attack_total'] > 0 else 0,
            'false_alarm_rate': (stats['benign_total'] - stats['benign_correct']) / stats['benign_total'] if stats['benign_total'] > 0 else 0,
            'severity_distribution': stats['severity_counts'],
            'attack_type_performance': stats['attack_types']
        }

    def _display_simulation_results(self, metrics):
        """Display simulation results"""
        print(f"\n SIMULATION RESULTS:")
        print(f" Total Samples: {metrics['total_samples']}")
        print(f" Benign Samples: {metrics['benign_total']}")
        print(f" Attack Samples: {metrics['attack_total']}")
    
        print(f"\n DETECTION PERFORMANCE:")
        if metrics['benign_total'] > 0:
            print(f" • Benign Classification: {metrics['benign_accuracy']:.3f}")
            print(f" • False Alarm Rate: {metrics['false_alarm_rate']:.3f}")
    
        if metrics['attack_total'] > 0:
            print(f" • Attack Detection: {metrics['attack_detection_rate']:.3f}")
    
        if metrics['attack_type_performance']:
            print(f"\n PERFORMANCE BY ATTACK TYPE:")
            for attack_type, stats in metrics['attack_type_performance'].items():
                detection_rate = stats['detected'] / stats['total']
                print(f" • {attack_type}: {stats['detected']}/{stats['total']} ({detection_rate:.3f})")




            ############      EVALUATION METHODS      ###########



    def evaluate_model_performance(self, test_df):
        """Comprehensive model performance evaluation"""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE EVALUATION")
        print("="*60)
    
        # Prepare test data
        stream_input = test_df.drop(columns=self.model.features_to_drop, errors='ignore')
        true_labels = test_df['label']
    
        # Get predictions
        predictions = self.model.predict(stream_input)
    
        # Convert predictions to binary
        predicted_labels = [1 if pred[0] != "GREEN" else 0 for pred in predictions]
        true_binary = [0 if label == "benign" else 1 for label in true_labels]
    
        # Calculate metrics
        metrics = self._calculate_classification_metrics(true_binary, predicted_labels)
        
        # Display results
        self._display_evaluation_results(metrics, true_binary, predicted_labels)
    
        return metrics

    def _calculate_classification_metrics(self, true_binary, predicted_labels):
        """Calculate classification metrics"""
        precision = precision_score(true_binary, predicted_labels, zero_division=0)
        recall = recall_score(true_binary, predicted_labels, zero_division=0)
        f1 = f1_score(true_binary, predicted_labels, zero_division=0)
        
        cm = confusion_matrix(true_binary, predicted_labels)
        tn, fp, fn, tp = cm.ravel()
        
        total_normal = tn + fp
        total_anomaly = fn + tp
        false_alarm_rate = fp / total_normal if total_normal > 0 else 0
        detection_rate = tp / total_anomaly if total_anomaly > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'detection_rate': detection_rate,
            'false_alarm_rate': false_alarm_rate,
            'confusion_matrix': cm,
            'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp
        }

    def _display_evaluation_results(self, metrics, true_binary, predicted_labels):
        """Display evaluation results"""
        print(f"PERFORMANCE METRICS:")
        print(f" • Precision: {metrics['precision']:.3f}")
        print(f" • Recall:    {metrics['recall']:.3f}")
        print(f" • F1-Score:  {metrics['f1_score']:.3f}")
    
        print(f"\n CONFUSION MATRIX:")
        print("              Predicted")
        print("              Normal  Anomaly")
        print(f"Actual Normal   {metrics['tn']:4d}    {metrics['fp']:4d}")
        print(f"Actual Anomaly  {metrics['fn']:4d}    {metrics['tp']:4d}")
    
        print(f"\n DETAILED BREAKDOWN:")
        print(f" • True Negatives (Correct Normal):     {metrics['tn']:4d}")
        print(f" • False Positives (False Alarms):      {metrics['fp']:4d}")
        print(f" • False Negatives (Missed Attacks):    {metrics['fn']:4d}")
        print(f" • True Positives (Detected Attacks):   {metrics['tp']:4d}")
    
        print(f"\n KEY RATES:")
        print(f" • Detection Rate:    {metrics['detection_rate']:.3f} ({metrics['detection_rate']*100:.1f}%)")
        print(f" • False Alarm Rate:  {metrics['false_alarm_rate']:.3f} ({metrics['false_alarm_rate']*100:.1f}%)")



        
