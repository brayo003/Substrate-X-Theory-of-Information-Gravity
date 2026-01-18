import h5py
import numpy as np

with h5py.File('H-H1_LOSC_4_V1-1126256640-4096.hdf5', 'r') as f:
    data = f['strain/Strain'][:]

# More chunks for better resolution
n_chunks = 100
chunk_size = len(data) // n_chunks
stds = []

for i in range(n_chunks):
    chunk = data[i*chunk_size:(i+1)*chunk_size]
    stds.append(np.std(chunk))

# Convert to numpy
stds = np.array(stds)
times = np.arange(n_chunks) * (chunk_size/4096)  # Time in seconds

print("=== STD TIME SERIES ANALYSIS ===")
print(f"STD mean: {np.mean(stds):.2e}")
print(f"STD STD: {np.std(stds):.2e} ({np.std(stds)/np.mean(stds)*100:.1f}% variation)")

# Check for periodicity
from scipy import signal
freqs, psd = signal.welch(stds - np.mean(stds), fs=1/(chunk_size/4096))
peak_freq = freqs[np.argmax(psd[1:]) + 1]  # Skip DC
peak_power = np.max(psd[1:])

print(f"\n=== PERIODICITY CHECK ===")
print(f"Peak frequency: {peak_freq:.3f} Hz")
print(f"Period: {1/peak_freq:.1f} seconds" if peak_freq > 0 else "No clear periodicity")

# Statistical test: Is the variation random or structured?
# Calculate autocorrelation
autocorr = np.correlate(stds - np.mean(stds), stds - np.mean(stds), mode='full')
autocorr = autocorr[len(autocorr)//2:]
autocorr = autocorr / autocorr[0]  # Normalize

# Significance: autocorrelation at lag 1
lag1 = autocorr[1]
print(f"\n=== AUTOCORRELATION ===")
print(f"Lag-1 autocorrelation: {lag1:.3f}")
if abs(lag1) > 0.2:
    print("STATUS: STD HAS MEMORY (not random)")
    print("The noise level at time t depends on time t-1")
    print("Possible: substrate density drifts slowly")
else:
    print("STATUS: STD is random (white noise)")

# Save for your framework
with open('std_structure.txt', 'w') as f:
    f.write(f"mean_std:{np.mean(stds):.6e}\n")
    f.write(f"std_of_stds:{np.std(stds):.6e}\n")
    f.write(f"percent_variation:{np.std(stds)/np.mean(stds)*100:.3f}\n")
    f.write(f"lag1_autocorr:{lag1:.6f}\n")
    f.write(f"peak_freq:{peak_freq:.6f}\n")
    for i, s in enumerate(stds):
        f.write(f"std_{i}:{s:.6e}\n")

print(f"\nSaved to 'std_structure.txt'")

# Quick plot
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(times, stds, 'b.-', alpha=0.7)
plt.xlabel('Time (seconds)')
plt.ylabel('STD')
plt.title('Noise STD over 68 minutes')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.hist(stds, bins=20, alpha=0.7)
plt.xlabel('STD')
plt.ylabel('Count')
plt.title('Distribution of STD values')

plt.tight_layout()
plt.savefig('std_analysis.png', dpi=120)
print("Plot saved as 'std_analysis.png'")
