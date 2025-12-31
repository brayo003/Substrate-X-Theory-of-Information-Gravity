import re
import json
from datetime import datetime, timedelta

def parse_hud_logs(log_file_path):
    """
    Parse your SXC_HUD.sh output logs
    Expected format:
    22:51:41 | Tension:   1.0844  | Phase: FIREWALL | VIX:   19.38
    """
    
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

def run_full_analysis():
    # Parse your logs
    data = parse_hud_logs('SXC_HUD_output.log')
    
    print(f"Loaded {data['sample_count']} data points")
    print(f"Time range: {data['timestamps'][0]} to {data['timestamps'][-1]}")
    
    # Run correlation analysis
    results = analyze_sxc_vix_correlation(
        data['tensions'],
        data['vix_values'],
        max_lag_hours=min(48, data['sample_count'] // 2)
    )
    
    # Print results
    print("\n" + "="*60)
    print("SXC-T vs VIX CROSS-CORRELATION ANALYSIS")
    print("="*60)
    
    print(f"\nSynchrony (0 lag): {results['synchrony'].get('0h', 0):.3f}")
    
    print("\nT leads VIX (Predictive Power):")
    for lag, corr in list(results['T_leads_VIX'].items())[:5]:  # Top 5
        print(f"  T leads by {lag}: {corr:.3f}")
    
    print("\nT lags VIX (Reactive Power):")
    for lag, corr in list(results['T_lags_VIX'].items())[:5]:  # Top 5
        print(f"  T lags by {lag}: {corr:.3f}")
    
    print(f"\nPrediction Strength Score: {results['prediction_strength']:.3f}")
    print(f"Best correlation: {results['max_correlation']:.3f} at {results['best_predictive_lag']}")
    
    # Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION:")
    
    if results['prediction_strength'] > 0.1:
        print("✅ STRONG PREDICTIVE POWER: SXC-T leads VIX movements")
        print(f"   Can predict VIX changes {results['prediction_strength']:.1%} better than tracking")
        
    elif results['prediction_strength'] > 0:
        print("⚠️  WEAK PREDICTIVE POWER: SXC-T slightly leads VIX")
        print("   More data needed for statistical significance")
        
    elif results['prediction_strength'] > -0.1:
        print("📊 SYNCHRONOUS INDICATOR: SXC-T tracks VIX in real-time")
        print("   Useful for monitoring, not prediction")
        
    else:
        print("🔻 REACTIVE INDICATOR: SXC-T lags VIX movements")
        print("   Reflects market stress, doesn't predict it")
    
    # Save results for visualization
    with open('correlation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    run_full_analysis()
