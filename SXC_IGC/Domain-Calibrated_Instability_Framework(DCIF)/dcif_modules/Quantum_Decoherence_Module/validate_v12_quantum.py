import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# 1. Load your V12 calibration results
v12_df = pd.read_csv('quantum_v12_calibration.csv')

# 2. Load IBM error rates (you'll need to parse the actual file)
# This is a TEMPLATE - adjust based on actual file format
error_data = """
# Format depends on the actual file - here's what the APS data contains:
# Qubit, T1(us), T2(us), freq(GHz), gate_error, readout_error
0, 7.45e-05, 5.08e-05, 5.225, 0.0012, 0.023
1, 9.87e-05, 1.61e-04, 5.003, 0.0009, 0.018
# ... etc for all 27 qubits
"""

# Parse error data (adjust based on actual format)
# For now, we'll simulate with realistic values from literature
# From Nature paper: median gate error ~0.00046 for SX gate [citation:2]
np.random.seed(42)
n_qubits = len(v12_df)
error_df = pd.DataFrame({
    'qubit': v12_df['qubit'],
    'gate_error': 0.0003 + 0.001 * np.random.rand(n_qubits),  # Placeholder
    'readout_error': 0.01 + 0.02 * np.random.rand(n_qubits)   # Placeholder
})

# 3. Merge with your V12 data
merged = pd.merge(v12_df, error_df, on='qubit')

print("=== VALIDATION DATASET ===")
print(merged[['qubit', 'T', 'gate_error', 'readout_error']].head(10))

# 4. Calculate correlations
corr_gate, p_gate = pearsonr(merged['T'], merged['gate_error'])
corr_readout, p_readout = pearsonr(merged['T'], merged['readout_error'])
corr_spearman, p_spearman = spearmanr(merged['T'], merged['gate_error'])

print("\n=== CORRELATION RESULTS ===")
print(f"Pearson r (T vs gate error): {corr_gate:.4f} (p={p_gate:.4f})")
print(f"Pearson r (T vs readout error): {corr_readout:.4f} (p={p_readout:.4f})")
print(f"Spearman ρ (T vs gate error): {corr_spearman:.4f} (p={p_spearman:.4f})")

# 5. Interpretation
if abs(corr_gate) > 0.7:
    print("\n✅ STRONG CORRELATION: V12 tension predicts gate errors!")
elif abs(corr_gate) > 0.5:
    print("\n⚠️ MODERATE CORRELATION: V12 captures some signal")
else:
    print("\n❌ WEAK CORRELATION: V12 may not predict errors well")

# 6. Visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# T vs gate error
axes[0].scatter(merged['T'], merged['gate_error']*1000, alpha=0.7, s=80)
axes[0].set_xlabel('V12 Tension T', fontsize=12)
axes[0].set_ylabel('Gate Error Rate (×10⁻³)', fontsize=12)
axes[0].set_title(f'T vs Gate Error (r={corr_gate:.3f})', fontsize=14)
axes[0].grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(merged['T'], merged['gate_error'], 1)
p = np.poly1d(z)
axes[0].plot(sorted(merged['T']), p(sorted(merged['T'])), 'r--', alpha=0.8)

# T vs readout error
axes[1].scatter(merged['T'], merged['readout_error']*100, alpha=0.7, s=80, color='green')
axes[1].set_xlabel('V12 Tension T', fontsize=12)
axes[1].set_ylabel('Readout Error (%)', fontsize=12)
axes[1].set_title(f'T vs Readout Error (r={corr_readout:.3f})', fontsize=14)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('v12_quantum_validation.png', dpi=150)
print("\nPlot saved to v12_quantum_validation.png")

# 7. Identify best/worst predictions
merged['error_rank'] = merged['gate_error'].rank()
merged['t_rank'] = merged['T'].rank()
merged['rank_diff'] = abs(merged['error_rank'] - merged['t_rank'])

print("\n=== QUBITS WHERE V12 EXCELS ===")
print(merged.nsmallest(3, 'rank_diff')[['qubit', 'T', 'gate_error', 'rank_diff']])

print("\n=== QUBITS WHERE V12 STRUGGLES ===")
print(merged.nlargest(3, 'rank_diff')[['qubit', 'T', 'gate_error', 'rank_diff']])

# 8. Save merged data
merged.to_csv('v12_validation_results.csv', index=False)
print("\nSaved to v12_validation_results.csv")
