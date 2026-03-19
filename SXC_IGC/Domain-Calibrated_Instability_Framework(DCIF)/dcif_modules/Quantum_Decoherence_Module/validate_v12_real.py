import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# 1. Load your V12 calibration
v12_df = pd.read_csv('quantum_v12_calibration.csv')

# 2. Load REAL IBM Toronto data from APS supplemental
# Parse the actual file format
real_data = []
with open('Data_analysis/backend_info/ibmq_toronto.txt', 'r') as f:
    for line in f:
        if 'Qubit' in line:
            # Parse based on actual format
            # You'll need to see the exact structure
            parts = line.split()
            # Extract qubit number, T1, T2, gate error, readout error
            # This is a TEMPLATE – adjust after seeing the file
            qubit = int(parts[1])
            t1 = float(parts[3])
            t2 = float(parts[5])
            gate_err = float(parts[7])
            readout_err = float(parts[9])
            real_data.append([qubit, t1, t2, gate_err, readout_err])

real_df = pd.DataFrame(real_data, columns=['qubit', 'T1', 'T2', 'gate_error', 'readout_error'])

# 3. Merge with V12 data
merged = pd.merge(v12_df, real_df, on='qubit')

# 4. Calculate REAL correlations
corr_gate, p_gate = pearsonr(merged['T'], merged['gate_error'])
corr_readout, p_readout = pearsonr(merged['T'], merged['readout_error'])

print(f"✅ REAL CORRELATION: T vs gate error = {corr_gate:.4f} (p={p_gate:.4f})")
print(f"✅ REAL CORRELATION: T vs readout error = {corr_readout:.4f} (p={p_readout:.4f})")

if abs(corr_gate) > 0.7:
    print("\n🎉 V12 WORKS! It predicts real quantum errors.")
elif abs(corr_gate) > 0.5:
    print("\n👍 Decent correlation – V12 captures some signal.")
else:
    print("\n📉 Weak correlation – need better calibration.")
