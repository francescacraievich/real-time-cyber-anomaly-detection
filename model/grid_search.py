import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.metrics import f1_score
from itertools import product


class GridSearchOptimizer:
    def __init__(self, model_instance):
        self.model = model_instance
        
    def grid_search_hyperparameters(self, df_benign, df_test=None, max_train_samples=5000):
        """Perform grid search to find optimal hyperparameters"""
        print("\n" + "="*60)
        print("GRID SEARCH HYPERPARAMETER OPTIMIZATION")
        print("="*60)

        # Configure features
        print("[GridSearch] Configuring features...")
        self.model._configure_features(df_benign)

        # Prepare data
        X_benign = df_benign.drop(columns=self.model.features_to_drop, errors='ignore')

        # Downsample for speed
        if len(X_benign) > max_train_samples:
            X_benign = X_benign.sample(n=max_train_samples, random_state=self.model.random_state)
            print(f"[GridSearch] Using {max_train_samples} samples for grid search")

        # Fit preprocessor
        self.model.preprocessor.fit(X_benign)
        X_processed = self.model.preprocessor.transform(X_benign)

        # Define parameter grid
        param_grid = self._get_parameter_grid()

        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_grid)
        print(f"[GridSearch] Testing {len(param_combinations)} parameter combinations...")

        # Run grid search
        best_params, best_score, results = self._run_grid_search(
            param_combinations, X_processed, df_test
        )

        # Update model with best parameters
        self.model.update_model_parameters(best_params)
        
        # Display results
        self._display_results(best_params, best_score, results)
        
        return best_params, best_score, results
    
    

    def _get_parameter_grid(self):
        """Define parameter grid based on search type"""
        #if quick_search:
        return {
                'nu': [0.05, 0.1, 0.15, 0.2],
                'kernel': ['rbf', 'linear'], 
                'gamma': ['scale', 'auto']
        }
        

#else:
#return {
#'nu': [0.01, 0.05, 0.1, 0.15, 0.2, 0.3],
#'kernel': ['rbf', 'linear', 'poly'],
#'gamma': ['scale', 'auto', 0.001, 0.01]
#}
        

    
    def _generate_param_combinations(self, param_grid):
        """Generate all parameter combinations"""
        param_combinations = []
        for nu in param_grid['nu']:
            for kernel in param_grid['kernel']:
                for gamma in param_grid['gamma']:
                    param_combinations.append({'nu': nu, 'kernel': kernel, 'gamma': gamma})
        return param_combinations



    def _run_grid_search(self, param_combinations, X_processed, df_test):
        """Execute grid search over parameter combinations"""
        best_score = -np.inf
        best_params = None
        results = []

        for i, params in enumerate(param_combinations):
            try:
                print(f"\n[{i+1}/{len(param_combinations)}] Testing: {params}")
            
                # Create and train model
                model = OneClassSVM(**params)
                model.fit(X_processed)
            
                # Evaluate model
                if df_test is not None and len(df_test) > 100:
                    score = self._evaluate_with_test_set(model, df_test)
                else:
                    score = self._evaluate_unsupervised(model, X_processed)
            
                results.append({'params': params, 'score': score})
                print(f"   Score: {score:.4f}")
            
                # Update best
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    print(f"   *** New best score: {best_score:.4f} ***")
                
            except Exception as e:
                print(f"   Error: {e}")
                continue

        return best_params, best_score, results
    


    def _evaluate_with_test_set(self, model, df_test):
        """Evaluate using labeled test data"""
        try:
            # Sample test data if too large
            test_sample = df_test.sample(n=min(1000, len(df_test)), random_state=42)
        
            # Prepare test data
            X_test = test_sample.drop(columns=self.model.features_to_drop, errors='ignore')
            y_true = test_sample['label']
        
            # Get predictions
            X_test_processed = self.model.preprocessor.transform(X_test)
            predictions = model.predict(X_test_processed)
        
            # Convert to binary
            y_pred = [1 if pred == -1 else 0 for pred in predictions]
            y_true_binary = [0 if label == "benign" else 1 for label in y_true]
        
            # Calculate F1-score
            score = f1_score(y_true_binary, y_pred, zero_division=0)
            return score
        
        except Exception as e:
            print(f"   Test evaluation error: {e}")
            return 0.0
        


    def _evaluate_unsupervised(self, model, X_processed):
        """Evaluate using decision function statistics"""
        try:
            scores = model.decision_function(X_processed)
        
            outlier_fraction = np.sum(scores < 0) / len(scores)
            mean_score = np.mean(scores)
        
            target_outlier_fraction = 0.1
            outlier_penalty = abs(outlier_fraction - target_outlier_fraction)
        
            score = mean_score - outlier_penalty * 2
            return score
        
        except Exception as e:
            print(f"   Unsupervised evaluation error: {e}")
            return -1.0
        


    def _display_results(self, best_params, best_score, results):
        """Display grid search results"""
        print(f"\n" + "="*50)
        print("GRID SEARCH COMPLETED")
        print("="*50)
        print(f"Best Parameters: {best_params}")
        print(f"Best Score: {best_score:.4f}")



    def fit_with_grid_search(self, df_benign, df_test=None, max_train_samples=10000, 
                            contamination=0.1):
        """Train model with grid search optimization"""
        print("\n" + "="*50)
        print("TRAINING WITH GRID SEARCH")
        print("="*50)
    
        # Run grid search
        best_params, best_score, results = self.grid_search_hyperparameters(
            df_benign, df_test, max_train_samples//2
        )
    
        # Train final model with best parameters
        print(f"\n[Final Training] Using best parameters: {best_params}")
        # The fit part of the model is here! 
        self.model.fit(df_benign, max_train_samples, contamination)
    
        return best_params, best_score



    def fit_or_load_with_grid_search(self, df_benign, df_test=None, max_train_samples=10000, 
                                    contamination=0.1, force_retrain=False):
        """Load existing model or train new one with grid search"""
        if self.model.model_exists() and not force_retrain:
            print("[System] Found existing model files.")
            if self.model.load_model():
                print("[System] Successfully loaded existing model.")
                if self.model.best_params:
                    print(f"[System] Loaded model was trained with: {self.model.best_params}")
                return True
            else:
                print("[System] Failed to load existing model. Training new one...")
        else:
            print("[System] Training new model with grid search...")
    
        # Train with grid search
        best_params, best_score = self.fit_with_grid_search(
            df_benign, df_test, max_train_samples, contamination
        )
    
        print(f"\n[System] Training completed with best F1-score: {best_score:.3f}")
        return True