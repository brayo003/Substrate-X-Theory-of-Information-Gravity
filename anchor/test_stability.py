import h5py
import numpy as np
from scipy.stats import normaltest

with h5py.File('H-H1_LOSC_4_V1-1126256640-4096.hdf5', 'r') as f:
    data = f['strain/Strain'][:]

# Split data into 10 chunks, test each for Gaussianity
n_chunks = 10
chunk_size = len(data) // n_chunks
p_values = []
stds = []

print("=== TEMPORAL STABILITY OF NON-GAUSSIANITY ===")
for i in range(n_chunks):
    chunk = data[i*chunk_size:(i+1)*chunk_size]
    _, p = normaltest(chunk)
    p_values.append(p)
    stds.append(np.std(chunk))
    
    status = "NON-GAUSSIAN" if p < 0.05 else "Gaussian"
    print(f"Chunk {i}: p={p:.3e}, std={np.std(chunk):.2e} → {status}")

# Calculate variation
p_mean = np.mean(p_values)
p_std = np.std(p_values)
std_mean = np.mean(stds)
std_std = np.std(stds)

print(f"\n=== SUMMARY ===")
print(f"Mean p-value: {p_mean:.3e} ± {p_std:.3e}")
print(f"Mean STD: {std_mean:.2e} ± {std_std:.2e}")

# Interpretation
if p_mean < 0.05 and p_std/p_mean < 0.5:
    print("\nSTATUS: CONSISTENTLY NON-GAUSSIAN")
    print("This is stable across time → likely INSTRUMENTAL")
elif p_mean < 0.05 and p_std/p_mean > 0.5:
    print("\nSTATUS: VARIABLY NON-GAUSSIAN")  
    print("p-value fluctuates → possible SUBSTRATE INTERACTION")
else:
    print("\nSTATUS: GAUSSIAN OR INCONCLUSIVE")

# Save for your framework
with open('stability_facts.txt', 'w') as f:
    for i, (p, s) in enumerate(zip(p_values, stds)):
        f.write(f"chunk_{i}:p={p:.6e},std={s:.6e}\n")
    f.write(f"p_mean:{p_mean:.6e}\n")
    f.write(f"p_std:{p_std:.6e}\n")
    f.write(f"std_mean:{std_mean:.6e}\n")
    f.write(f"std_std:{std_std:.6e}\n")

print("\nSaved to 'stability_facts.txt'")
