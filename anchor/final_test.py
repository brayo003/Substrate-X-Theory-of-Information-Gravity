import h5py
import numpy as np

with h5py.File('H-H1_LOSC_4_V1-1126256640-4096.hdf5', 'r') as f:
    data = f['strain/Strain'][:]

# Find exact location of std_72 outlier
chunk_size = len(data) // 100
outlier_start = 72 * chunk_size
outlier_end = 73 * chunk_size
outlier_data = data[outlier_start:outlier_end]

print("=== OUTLIER STD_72 ANALYSIS ===")
print(f"Position: samples {outlier_start} to {outlier_end}")
print(f"Time: {outlier_start/4096:.1f} to {outlier_end/4096:.1f} seconds from start")
print(f"Chunk STD: {np.std(outlier_data):.2e}")
print(f"Chunk mean: {np.mean(outlier_data):.2e}")
print(f"Chunk min: {np.min(outlier_data):.2e}")
print(f"Chunk max: {np.max(outlier_data):.2e}")

# Check if it's a single spike or sustained
peak_threshold = 5 * np.std(data)  # 5 sigma
peaks = np.where(np.abs(outlier_data) > peak_threshold)[0]

print(f"\n=== SPIKE ANALYSIS ===")
print(f"5σ threshold: {peak_threshold:.2e}")
print(f"Number of >5σ points: {len(peaks)}")

if len(peaks) > 0:
    print("First few peak values:")
    for i in peaks[:5]:
        print(f"  Sample {i}: {outlier_data[i]:.2e} ({np.abs(outlier_data[i])/np.std(data):.1f}σ)")
    
    # Check spacing
    if len(peaks) > 1:
        spacings = np.diff(peaks)
        print(f"\nPeak spacings (samples): {spacings[:5]}")
        if np.all(spacings == 1):
            print("→ CONSECUTIVE SAMPLES (likely glitch)")
        else:
            print("→ SPREAD OUT (possible physical)")
else:
    print("No extreme spikes (>5σ)")

# Compare with neighboring chunks
print(f"\n=== NEIGHBOR COMPARISON ===")
for offset in [-2, -1, 0, 1, 2]:
    idx = 72 + offset
    if 0 <= idx < 100:
        chunk = data[idx*chunk_size:(idx+1)*chunk_size]
        print(f"Chunk {idx}: STD={np.std(chunk):.2e}, mean={np.mean(chunk):.2e}")

# LIGO-specific: check if this time has known issues
# GW150914 merger was at GPS 1126259462.4
# Our data starts at GPS 1126256640 (from filename)
gps_start = 1126256640
outlier_gps = gps_start + (outlier_start + outlier_end)/(2*4096)
print(f"\n=== TIMING CONTEXT ===")
print(f"Data start GPS: {gps_start}")
print(f"Outlier mid GPS: {outlier_gps:.1f}")
print(f"Time before GW150914: {1126259462.4 - outlier_gps:.1f} seconds")
print(f"That's {(1126259462.4 - outlier_gps)/3600:.1f} hours before the merger")

# Final empirical verdict
print(f"\n=== EMPIRICAL VERDICT ===")
std_ratio = np.std(outlier_data) / np.mean([np.std(data[70*chunk_size:71*chunk_size]), 
                                            np.std(data[73*chunk_size:74*chunk_size])])
if std_ratio > 3:
    if len(peaks) > 10 and np.mean(np.diff(peaks)) == 1:
        print("STATUS: INSTRUMENTAL GLITCH (consecutive samples spiking)")
    elif len(peaks) < 3:
        print("STATUS: SUSPICIOUS (high STD but few spikes)")
        print("Could be: substrate fluctuation OR rare event")
    else:
        print("STATUS: UNKNOWN (needs more data)")
else:
    print("STATUS: WITHIN EXPECTED VARIATION")

# Save the raw outlier data for your records
np.savetxt('outlier_samples.txt', outlier_data[:1000], fmt='%.6e')
print(f"\nFirst 1000 samples saved to 'outlier_samples.txt'")
