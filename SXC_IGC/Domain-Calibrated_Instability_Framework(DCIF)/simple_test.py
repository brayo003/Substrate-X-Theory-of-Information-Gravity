"""
Quick test to see if SXC-T leads or lags VIX
"""
import numpy as np

# Simpler version that just answers: Does T lead VIX?
def quick_lead_lag_test(tensions, vix_values):
    """Simple lead/lag test"""
    n = min(len(tensions), len(vix_values))
    tensions = tensions[:n]
    vix_values = vix_values[:n]
    
    # Test small lags (1-10 steps)
    best_lead_corr = -1
    best_lag_corr = -1
    best_lead = 0
    best_lag = 0
    
    for lag in range(1, min(10, n//2)):
        # T leads VIX
        if lag < n:
            lead_corr = np.corrcoef(tensions[:-lag], vix_values[lag:])[0,1]
            if lead_corr > best_lead_corr:
                best_lead_corr = lead_corr
                best_lead = lag
        
        # T lags VIX
        lag_corr = np.corrcoef(tensions[lag:], vix_values[:-lag])[0,1]
        if lag_corr > best_lag_corr:
            best_lag_corr = lag_corr
            best_lag = lag
    
    # Synchrony
    sync_corr = np.corrcoef(tensions, vix_values)[0,1]
    
    print("QUICK LEAD/LAG TEST RESULTS")
    print("="*40)
    print(f"Synchrony (0 lag): {sync_corr:.3f}")
    print(f"Best lead (T → VIX): {best_lead} steps, correlation: {best_lead_corr:.3f}")
    print(f"Best lag (VIX → T): {best_lag} steps, correlation: {best_lag_corr:.3f}")
    
    if best_lead_corr > best_lag_corr + 0.1:
        print("\n✅ T leads VIX (predictive power)")
    elif best_lag_corr > best_lead_corr + 0.1:
        print("\n🔻 T lags VIX (reactive indicator)")
    else:
        print("\n📊 T and VIX move together (synchronous)")
    
    return {
        'sync': sync_corr,
        'lead_corr': best_lead_corr,
        'lag_corr': best_lag_corr,
        'lead_steps': best_lead,
        'lag_steps': best_lag
    }

# Test with sample data (or replace with your actual data)
if __name__ == "__main__":
    # Sample data - replace with your actual tensions and VIX values
    sample_t = [0.1, 0.2, 0.5, 0.8, 1.0, 1.2, 1.0, 0.8, 0.5, 0.3]
    sample_vix = [18, 19, 22, 25, 28, 30, 28, 25, 22, 20]
    
    print("Testing with sample data...")
    print("Replace with your actual data in the code!")
    results = quick_lead_lag_test(sample_t, sample_vix)
    
    print("\nTo use your actual data:")
    print("1. Copy your tensions list into sample_t")
    print("2. Copy your VIX values into sample_vix")
    print("3. Run again")
