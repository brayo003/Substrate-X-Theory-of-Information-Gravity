import numpy as np

# Load your STD data
stds = []
with open('std_structure.txt', 'r') as f:
    for line in f:
        if line.startswith('std_'):
            stds.append(float(line.split(':')[1]))

stds = np.array(stds)
times = np.arange(len(stds)) * 41.0  # Each chunk ~41 seconds (16777216/4096/100)

print("=== PHYSICAL CORRELATIONS ===")
print(f"STDs: {len(stds)} points over {times[-1]/3600:.1f} hours")

# 1. Check for daily period (24 hours = 86400 seconds)
from scipy import signal
freqs, psd = signal.welch(stds, fs=1/41.0)
# Look for low frequencies (daily = 0.0000116 Hz)
low_freq_mask = freqs < 0.0001
if np.any(low_freq_mask):
    daily_peak = np.max(psd[low_freq_mask])
    daily_freq = freqs[low_freq_mask][np.argmax(psd[low_freq_mask])]
    print(f"\n1. DAILY CYCLE CHECK:")
    print(f"   Peak at {1/daily_freq/3600:.1f} hours")
    if 20 < 1/daily_freq/3600 < 28:
        print("   → MATCHES EARTH ROTATION (24h)")
    else:
        print("   → NOT 24h")

# 2. Check for 27.3 day lunar cycle
# Our data is only ~1.1 hours, so we can't see this directly
print(f"\n2. LUNAR CYCLE:")
print(f"   Data too short (1.1 hours) vs lunar cycle (655 hours)")

# 3. Look for sudden jumps (like std_72)
jumps = np.where(np.abs(np.diff(stds)) > 3*np.std(np.diff(stds)))[0]
print(f"\n3. SUDDEN JUMPS (>3σ changes):")
if len(jumps) > 0:
    for j in jumps:
        print(f"   Time {times[j]/60:.1f} min: {stds[j]:.2e} → {stds[j+1]:.2e}")
    print(f"   Total jumps: {len(jumps)}")
else:
    print("   No significant jumps")

# 4. Calculate what η variation this implies in your framework
# Assuming STD ∝ √η
eta_min = (np.min(stds) / np.mean(stds))**2
eta_max = (np.max(stds) / np.mean(stds))**2
print(f"\n4. IMPLIED η VARIATION (IF STD ∝ √η):")
print(f"   η_min/η_mean: {eta_min:.3f}")
print(f"   η_max/η_mean: {eta_max:.3f}")
print(f"   Total variation: {eta_max/eta_min:.1f}×")

# Save for your tension framework
with open('eta_variation.txt', 'w') as f:
    f.write(f"std_min:{np.min(stds):.6e}\n")
    f.write(f"std_max:{np.max(stds):.6e}\n")
    f.write(f"std_mean:{np.mean(stds):.6e}\n")
    f.write(f"eta_min_ratio:{eta_min:.6f}\n")
    f.write(f"eta_max_ratio:{eta_max:.6f}\n")
    f.write(f"implied_eta_variation:{eta_max/eta_min:.3f}\n")

print(f"\nSaved to 'eta_variation.txt'")
