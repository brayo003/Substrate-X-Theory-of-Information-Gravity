import json
import matplotlib.pyplot as plt
import numpy as np

def plot_correlation_analysis():
    with open('correlation_results.json', 'r') as f:
        results = json.load(f)
    
    # Extract data for plotting
    leads_lags = []
    correlations = []
    labels = []
    
    # T leads VIX (positive lags)
    for lag, corr in results['T_leads_VIX'].items():
        leads_lags.append(int(lag.replace('h', '')))
        correlations.append(corr)
        labels.append(f'T+{lag}')
    
    # T lags VIX (negative lags)
    for lag, corr in results['T_lags_VIX'].items():
        leads_lags.append(-int(lag.replace('h', '')))
        correlations.append(corr)
        labels.append(f'T-{lag}')
    
    # Sort by lag
    sorted_data = sorted(zip(leads_lags, correlations, labels))
    lags_sorted, corrs_sorted, labels_sorted = zip(*sorted_data)
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 1. Cross-correlation function
    ax1.plot(lags_sorted, corrs_sorted, 'b-o', linewidth=2, markersize=4)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Synchrony')
    ax1.fill_between(lags_sorted, 0, corrs_sorted, 
                     where=np.array(corrs_sorted)>0, 
                     color='green', alpha=0.3, label='Positive correlation')
    ax1.fill_between(lags_sorted, 0, corrs_sorted, 
                     where=np.array(corrs_sorted)<0, 
                     color='red', alpha=0.3, label='Negative correlation')
    ax1.set_xlabel('Lag (hours, positive = T leads VIX)')
    ax1.set_ylabel('Correlation Coefficient')
    ax1.set_title('Cross-Correlation: SXC-T vs VIX (Lead/Lag Analysis)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Predictive power summary
    categories = ['T leads VIX', 'T lags VIX', 'Synchrony']
    values = [
        np.mean(list(results['T_leads_VIX'].values())) if results['T_leads_VIX'] else 0,
        np.mean(list(results['T_lags_VIX'].values())) if results['T_lags_VIX'] else 0,
        results['synchrony'].get('0h', 0)
    ]
    
    colors = ['green' if v > 0 else 'red' for v in values]
    bars = ax2.bar(categories, values, color=colors, alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}', ha='center', va='bottom' if height >= 0 else 'top')
    
    ax2.axhline(y=0, color='black', linewidth=0.5)
    ax2.set_ylabel('Average Correlation')
    ax2.set_title(f'Predictive Power Assessment (Strength: {results["prediction_strength"]:.3f})')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('sxc_vix_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'sxc_vix_correlation_analysis.png'")
    
    # Print statistical significance
    print("\n" + "="*60)
    print("STATISTICAL SIGNIFICANCE ASSESSMENT:")
    
    # Simple t-test simulation (for illustration)
    n = len(results['T_leads_VIX']) + len(results['T_lags_VIX'])
    if n > 10:  # Enough data for rough significance test
        lead_mean = np.mean(list(results['T_leads_VIX'].values())) if results['T_leads_VIX'] else 0
        lag_mean = np.mean(list(results['T_lags_VIX'].values())) if results['T_lags_VIX'] else 0
        
        # Approximate t-statistic (simplified)
        t_stat = (lead_mean - lag_mean) / (0.1 / np.sqrt(n))  # Assuming std ~0.1
        
        if abs(t_stat) > 2.0:
            print(f"✅ Statistically significant difference (|t| = {abs(t_stat):.2f})")
            if lead_mean > lag_mean:
                print("   SXC-T likely has genuine predictive power")
            else:
                print("   SXC-T likely reacts to VIX (not predictive)")
        else:
            print(f"⚠️  Not statistically significant (|t| = {abs(t_stat):.2f})")
            print("   Need more data for conclusive results")
    else:
        print("⚠️  Insufficient data for statistical significance test")

if __name__ == "__main__":
    plot_correlation_analysis()
