import os
import sys
from pathlib import Path




project_root = Path(__file__).resolve().parents[1]
# Add feature_engineering to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    

from oneCSVM_model import OneClassSVMModel
from grid_search import GridSearchOptimizer  
from simulation_evaluation import SimulationEvaluator
import pandas as pd


def load_datasets():
    """Load and prepare datasets"""
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "processed"
    
    print("1. Loading Datasets...")
    try:
        df_benign = pd.read_csv(data_path / "normal_traffic_formatted.csv")
        df_combined = pd.read_csv(data_path / "combined_shuffled_dataset.csv")
        print(f" -> Loaded {len(df_benign)} benign logs and {len(df_combined)} combined logs.")
        
        # Ensure benign label column exists
        if 'label' not in df_benign.columns: 
            df_benign['label'] = 'benign'

        return df_benign, df_combined

    except FileNotFoundError:
        print("\n[ERROR] Files not found.")
        return None, None
    


def main():
    """Main execution function"""
    
    # Load datasets
    df_benign, df_combined = load_datasets()
    if df_benign is None:
        return

    print("\n2. Initializing One-Class SVM System...")
    
    # Initialize core components
    svm_model = OneClassSVMModel()
    grid_search = GridSearchOptimizer(svm_model)
    evaluator = SimulationEvaluator(svm_model)

    print("\n3. Training with grid search optimization...")
    
    # Prepare test data for grid search
    test_for_tuning = df_combined.sample(n=4000, random_state=42)
    
    # Train or load model with grid search
    grid_search.fit_or_load_with_grid_search(
        df_benign, 
        df_test=test_for_tuning,
        max_train_samples=8000,
        contamination=0.1,
        force_retrain=False,  # Set to True to force retraining
        #quick_search=True     # Set to False for exhaustive search
    )

    print("\n4. Evaluating model performance...")
    # Comprehensive evaluation
    test_sample = df_combined.sample(n=10000, random_state=42)
    performance_metrics = evaluator.evaluate_model_performance(test_sample)

    print("\n5. Running real-time simulation...")
    evaluator.run_simulation(df_combined, chunk_size=10)

    print("\n6. Running detailed simulation...")
    simulation_results = evaluator.run_detailed_simulation(test_sample)
    
    print("\n7. Final Assessment:")
    print(f" Best parameters found: {svm_model.best_params}")
    print(f" F1-Score: {performance_metrics['f1_score']:.3f}")
    print(f" Detection Rate: {simulation_results['attack_detection_rate']:.3f}")
    print(f" False Alarm Rate: {simulation_results['false_alarm_rate']:.3f}")

    # Quality assessment
    assess_model_quality(performance_metrics, simulation_results)



def assess_model_quality(performance_metrics, simulation_results):
    """Assess and display model quality"""
    print("\n7. Quality Assessment:")
    
    if performance_metrics['f1_score'] > 0.7:
        print(" Good F1-Score (>0.7)")
    else:
        print(" Low F1-Score (<0.7) - Consider tuning parameters")
    
    if simulation_results['false_alarm_rate'] < 0.1:
        print(" Low False Alarm Rate (<10%)")
    else:
        print(" High False Alarm Rate (>10%) - Too many false positives")
    
    if simulation_results['attack_detection_rate'] > 0.8:
        print(" Good Attack Detection Rate (>80%)")
    else:
        print(" Low Attack Detection Rate (<80%) - Missing too many attacks")


if __name__ == "__main__":
    main()