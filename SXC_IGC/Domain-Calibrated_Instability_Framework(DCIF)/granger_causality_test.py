"""
Granger Causality Test for SXC-T → VIX
Tests if past T values help predict VIX better than just past VIX values
"""
import numpy as np
from scipy import stats

def simple_granger_test(T_series, VIX_series, max_lag=24):
    """
    Simplified Granger causality test
    Returns: p-value for null hypothesis "T does not Granger-cause VIX"
    Lower p-value (<0.05) means T helps predict VIX
    """
    
    # Ensure stationary data (first difference if needed)
    T_diff = np.diff(T_series)
    VIX_diff = np.diff(VIX_series)
    
    n = len(T_diff) - max_lag
    
    if n < 10:
        return None  # Not enough data
    
    # Restricted model (only past VIX)
    errors_restricted = []
    for i in range(max_lag, len(VIX_diff)):
        # Use only past VIX values
        X = np.array([VIX_diff[i-l] for l in range(1, max_lag+1)])
        y = VIX_diff[i]
        
        # Simple linear prediction
        if np.std(X) > 0:
            pred = np.mean(X)  # Simplified
            errors_restricted.append((y - pred)**2)
    
    # Unrestricted model (past VIX + past T)
    errors_unrestricted = []
    for i in range(max_lag, len(VIX_diff)):
        # Use past VIX AND past T values
        X_vix = np.array([VIX_diff[i-l] for l in range(1, max_lag+1)])
        X_t = np.array([T_diff[i-l] for l in range(1, max_lag+1)])
        X = np.concatenate([X_vix, X_t])
        y = VIX_diff[i]
        
        if np.std(X) > 0:
            pred = np.mean(X)  # Simplified
            errors_unrestricted.append((y - pred)**2)
    
    # F-test for model comparison
    SSR_restricted = np.sum(errors_restricted)
    SSR_unrestricted = np.sum(errors_unrestricted)
    
    m = max_lag  # Number of restrictions
    n_obs = len(errors_restricted)
    k = 2 * max_lag  # Parameters in unrestricted model
    
    F_stat = ((SSR_restricted - SSR_unrestricted) / m) / (SSR_unrestricted / (n_obs - k))
    
    # Calculate p-value
    p_value = 1 - stats.f.cdf(F_stat, m, n_obs - k)
    
    return {
        'F_statistic': F_stat,
        'p_value': p_value,
        'granger_causes': p_value < 0.05,
        'improvement_ratio': SSR_restricted / SSR_unrestricted if SSR_unrestricted > 0 else 1
    }

# Usage with your data
def test_granger_causality():
    # Load your data
    data = parse_hud_logs('SXC_HUD_output.log')  # Use previous function
    
    # Run Granger test at different lags
    print("Granger Causality Tests: Does SXC-T predict VIX?")
    print("="*60)
    
    for lag in [1, 6, 12, 24]:
        result = simple_granger_test(data['tensions'], data['vix_values'], max_lag=lag)
        
        if result:
            print(f"\nLag {lag}h:")
            print(f"  F-statistic: {result['F_statistic']:.3f}")
            print(f"  p-value: {result['p_value']:.4f}")
            
            if result['p_value'] < 0.05:
                print(f"  ✅ SIGNIFICANT: SXC-T Granger-causes VIX at {lag}h lag")
                print(f"     Model improves by {result['improvement_ratio']:.1%}")
            else:
                print(f"  ❌ NOT SIGNIFICANT: No evidence SXC-T predicts VIX at {lag}h")
                print(f"     (p > 0.05)")
