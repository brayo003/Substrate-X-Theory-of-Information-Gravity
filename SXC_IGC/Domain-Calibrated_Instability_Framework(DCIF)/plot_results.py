import json
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_correlation_analysis():
    if not os.path.exists('correlation_results.json'):
        print("Error: Run extract_and_analyze.py first!")
        return
    
    with open('correlation_results.json', 'r') as f:
        results = json.load(f)
    
    # Extract data for plotting
    leads_lags = []
    correlations = []
    
    # T leads VIX (positive lags)
    for lag, corr in results['T_leads_VIX'].items():
        leads_lags.append(int(lag.replace('h', '')))
        correlations.append(corr)
    
    # T lags VIX (negative lags)
    for lag, corr in results['T_lags_VIX'].items():
        leads_lags.append(-int(lag.replace('h', '')))
        correlations.append(corr)
    
    # Sort by lag
    sorted_pairs = sorted(zip(leads_lags, correlations))
    lags_sorted, corrs_sorted = zip(*sorted_pairs)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Cross-correlation function
    plt.plot(lags_sorted, corrs_sorted, 'b-o', linewidth=2, markersize=4)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='red', linestyle='--', alpha=0.5, label='Synchrony (0 lag)')
    
    # Fill positive/negative areas
    x_fill = list(lags_sorted)
    y_fill = list(corrs_sorted)
    plt.fill_between(x_fill, 0, y_fill, where=[y>0 for y in y_fill], 
                     color='green', alpha=0.3, label='Positive correlation')
    plt.fill_between(x_fill, 0, y_fill, where=[y<0 for y in y_fill],
                     color='red', alpha=0.3, label='Negative correlation')
    
    plt.xlabel('Lag (hours, positive = T leads VIX)')
    plt.ylabel('Correlation Coefficient')
    plt.title(f'SXC-T vs VIX Cross-Correlation\nPrediction Strength: {results["prediction_strength"]:.3f}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('sxc_vix_correlation.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'sxc_vix_correlation.png'")
    
    # Create summary bar chart
    plt.figure(figsize=(8, 5))
    
    categories = ['Synchrony (0h)', 'Avg Lead', 'Avg Lag']
    sync_val = results['synchrony'].get('0h', 0)
    avg_lead = np.mean(list(results['T_leads_VIX'].values())) if results['T_leads_VIX'] else 0
    avg_lag = np.mean(list(results['T_lags_VIX'].values())) if results['T_lags_VIX'] else 0
    
    values = [sync_val, avg_lead, avg_lag]
    colors = ['blue', 'green', 'orange']
    
    bars = plt.bar(categories, values, color=colors, alpha=0.7)
    
    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}', ha='center', va='bottom' if height >= 0 else 'top')
    
    plt.axhline(y=0, color='black', linewidth=0.5)
    plt.ylabel('Correlation')
    plt.title('SXC-T Predictive Power Summary')
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('sxc_predictive_summary.png', dpi=300, bbox_inches='tight')
    print("Summary saved as 'sxc_predictive_summary.png'")
    
    plt.show()

if __name__ == "__main__":
    plot_correlation_analysis()
