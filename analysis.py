import numpy as np
from scipy import stats
import pandas as pd
from sklearn.linear_model import BayesianRidge
from sklearn.preprocessing import StandardScaler

def perform_bayesian_analysis(data_df):
    """
    Perform statistical analysis on the relationship between user characteristics
    and deepfake detection ability using Bayesian Ridge Regression.
    """
    # Prepare the data
    X = data_df[['age', 'social_media_hours']]
    y = data_df['accuracy']
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit Bayesian Ridge Regression
    brr = BayesianRidge(max_iter=1000, tol=1e-6, alpha_init=1e-6, lambda_init=1e-6)
    brr.fit(X_scaled, y)
    
    # Calculate 95% confidence intervals using bootstrapping
    predictions = []
    intercepts = []
    n_iterations = 1000
    for _ in range(n_iterations):
        indices = np.random.choice(len(X), len(X), replace=True)
        X_bootstrap = X_scaled[indices]
        y_bootstrap = y.iloc[indices]
        brr_bootstrap = BayesianRidge(max_iter=300, tol=1e-6)
        brr_bootstrap.fit(X_bootstrap, y_bootstrap)
        predictions.append(brr_bootstrap.coef_)
        intercepts.append(brr_bootstrap.intercept_)
    
    predictions = np.array(predictions)
    intercepts = np.array(intercepts)
    
    # Calculate correlations using scipy.stats
    age=data_df['age']
    numeric_age = pd.to_numeric(age)
    numeric_accuracy = pd.to_numeric(data_df['accuracy'])
    numeric_social_media_hours = pd.to_numeric(data_df['social_media_hours'])
    age_corr, age_p = stats.pearsonr(numeric_age, numeric_accuracy )
    social_corr, social_p = stats.pearsonr(numeric_social_media_hours, numeric_accuracy)
    
    # Prepare results
    results = {
        'age_effect': {
            'mean': float(brr.coef_[0]),
            'std': float(np.std(predictions[:, 0])),
            'ci_low': float(np.percentile(predictions[:, 0], 2.5)),
            'ci_high': float(np.percentile(predictions[:, 0], 97.5)),
            'correlation': float(age_corr),
            'p_value': float(age_p)
        },
        'social_media_effect': {
            'mean': float(brr.coef_[1]),
            'std': float(np.std(predictions[:, 1])),
            'ci_low': float(np.percentile(predictions[:, 1], 2.5)),
            'ci_high': float(np.percentile(predictions[:, 1], 97.5)),
            'correlation': float(social_corr),
            'p_value': float(social_p)
        },
        'baseline_accuracy': {
            'mean': float(brr.intercept_),
            'std': float(np.std(intercepts)),
            'ci_low': float(np.percentile(intercepts, 2.5)),
            'ci_high': float(np.percentile(intercepts, 97.5))
        },
        'model_score': float(brr.score(X_scaled, y))
    }
    
    return results

# Example usage:
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'age': np.random.normal(30, 10, 100),
        'social_media_hours': np.random.normal(3, 1, 100),
        'accuracy': np.random.normal(0.7, 0.1, 100)
    })
    
    results = perform_bayesian_analysis(data)
    
    # Print results in a formatted way
    print("\nAnalysis Results:")
    print("-" * 50)
    print("Age Effect:")
    print(f"  Coefficient: {results['age_effect']['mean']:.4f}")
    print(f"  95% CI: [{results['age_effect']['ci_low']:.4f}, {results['age_effect']['ci_high']:.4f}]")
    print(f"  Correlation: {results['age_effect']['correlation']:.4f}")
    print(f"  P-value: {results['age_effect']['p_value']:.4f}")
    
    print("\nSocial Media Effect:")
    print(f"  Coefficient: {results['social_media_effect']['mean']:.4f}")
    print(f"  95% CI: [{results['social_media_effect']['ci_low']:.4f}, {results['social_media_effect']['ci_high']:.4f}]")
    print(f"  Correlation: {results['social_media_effect']['correlation']:.4f}")
    print(f"  P-value: {results['social_media_effect']['p_value']:.4f}")
    
    print("\nBaseline Accuracy:")
    print(f"  Intercept Mean: {results['baseline_accuracy']['mean']:.4f}")
    print(f"  95% CI: [{results['baseline_accuracy']['ci_low']:.4f}, {results['baseline_accuracy']['ci_high']:.4f}]")
    
    print("\nModel Score (R²):", f"{results['model_score']:.4f}")
