import re
import json
import numpy as np
from datetime import datetime

def parse_hud_logs(log_file_path):
    """Parse your SXC_HUD.sh output logs"""
    pattern = r'(\d{2}:\d{2}:\d{2})\s+\|\s+Tension:\s+([\d.]+)\s+\|\s+Phase:\s+(\w+)\s+\|\s+VIX:\s+([\d.]+)'
    
    timestamps = []
    tensions = []
    vix_values = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                time_str, tension_str, phase, vix_str = match.groups()
                timestamps.append(time_str)
                tensions.append(float(tension_str))
                vix_values.append(float(vix_str))
    
    return {
        'timestamps': timestamps,
        'tensions': tensions,
        'vix_values': vix_values,
        'sample_count': len(tensions)
    }

def analyze_sxc_vix_correlation(T_series, VIX_series, max_lag_hours=48):
    """Comprehensive lag analysis"""
    min_len = min(len(T_series), len(VIX_series))
    T = T_series[:min_len]
    VIX = VIX_series[:min_len]
    
    results = {
        'T_leads_VIX': {},
        'T_lags_VIX': {},
        'synchrony': {},
        'best_predictive_lag': None,
        'max_correlation': -1,
        'prediction_strength': 0
    }
    
    # Test T leading VIX (predictive power)
    for lag_hours in range(1, min(max_lag_hours, min_len // 2) + 1):
        if lag_hours >= min_len:
            break
        correlation = np.corrcoef(T[:-lag_hours], VIX[lag_hours:])[0, 1]
        results['T_leads_VIX'][f'{lag_hours}h'] = correlation
        
        if abs(correlation) > abs(results['max_correlation']):
            results['max_correlation'] = correlation
            results['best_predictive_lag'] = f'T leads by {lag_hours}h'
    
    # Test T lagging VIX (reactive indicator)
    for lag_hours in range(1, min(max_lag_hours, min_len // 2) + 1):
        if lag_hours >= min_len:
            break
        correlation = np.corrcoef(T[lag_hours:], VIX[:-lag_hours])[0, 1]
        results['T_lags_VIX'][f'{lag_hours}h'] = correlation
        
        if abs(correlation) > abs(results['max_correlation']):
            results['max_correlation'] = correlation
            results['best_predictive_lag'] = f'T lags by {lag_hours}h'
    
    # Test synchrony (same time)
    results['synchrony']['0h'] = np.corrcoef(T, VIX)[0, 1]
    
    # Calculate predictive strength
    avg_lead = np.mean(list(results['T_leads_VIX'].values())) if results['T_leads_VIX'] else 0
    avg_lag = np.mean(list(results['T_lags_VIX'].values())) if results['T_lags_VIX'] else 0
    results['prediction_strength'] = avg_lead - avg_lag
    
    return results

def run_full_analysis():
    print("Loading SXC-HUD logs...")
    data = parse_hud_logs('sxc_hud_logs.txt')
    
    print(f"Loaded {data['sample_count']} data points")
    print(f"Time range: {data['timestamps'][0]} to {data['timestamps'][-1]}")
    
    # Run correlation analysis
    max_lag = min(24, data['sample_count'] // 4)  # Conservative
    results = analyze_sxc_vix_correlation(data['tensions'], data['vix_values'], max_lag)
    
    print("\n" + "="*60)
    print("SXC-T vs VIX CROSS-CORRELATION ANALYSIS")
    print("="*60)
    
    print(f"\nSynchrony (0 lag): {results['synchrony'].get('0h', 0):.3f}")
    
    print("\nT leads VIX (Predictive Power):")
    for lag, corr in sorted(results['T_leads_VIX'].items(), key=lambda x: int(x[0].replace('h', '')))[:5]:
        print(f"  T leads by {lag}: {corr:.3f}")
    
    print("\nT lags VIX (Reactive Power):")
    for lag, corr in sorted(results['T_lags_VIX'].items(), key=lambda x: int(x[0].replace('h', '')))[:5]:
        print(f"  T lags by {lag}: {corr:.3f}")
    
    print(f"\nPrediction Strength Score: {results['prediction_strength']:.3f}")
    print(f"Best correlation: {results['max_correlation']:.3f} at {results['best_predictive_lag']}")
    
    # Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION:")
    
    if results['prediction_strength'] > 0.1:
        print("✅ STRONG PREDICTIVE POWER: SXC-T leads VIX movements")
    elif results['prediction_strength'] > 0.02:
        print("⚠️  WEAK PREDICTIVE POWER: SXC-T slightly leads VIX")
    elif results['prediction_strength'] > -0.02:
        print("📊 SYNCHRONOUS INDICATOR: SXC-T tracks VIX in real-time")
    elif results['prediction_strength'] > -0.1:
        print("⚠️  WEAKLY REACTIVE: SXC-T slightly lags VIX")
    else:
        print("🔻 REACTIVE INDICATOR: SXC-T lags VIX movements")
    
    # Save results
    with open('correlation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to 'correlation_results.json'")
    
    return results

if __name__ == "__main__":
    run_full_analysis()
