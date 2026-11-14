import h5py
import numpy as np
from scipy.stats import kurtosis, normaltest

def inspect_noise_statistics(filename="H-H1_LOSC_4_V1-1126256640-4096.hdf5", gps_merger=1126259462.4):
    print("=== RAW NOISE INSPECTION ===")
    
    with h5py.File(filename, 'r') as f:
        strain = f['strain/Strain'][:]
        dt = f['strain/Strain'].attrs['dt']
        gps_start = f['strain/Strain'].attrs['GPSstart']
    
    times = gps_start + np.arange(len(strain)) * dt
    
    # Select 1 second of data 10 seconds BEFORE merger (pure noise)
    noise_mask = (times >= gps_merger - 20) & (times <= gps_merger - 19)
    noise_data = strain[noise_mask]
    
    if len(noise_data) == 0:
        print("ERROR: No noise data in selected window")
        return
    
    # Basic statistics
    noise_std = np.std(noise_data)
    noise_rms = np.sqrt(np.mean(noise_data**2))
    
    print(f"Noise STD: {noise_std:.2e}")
    print(f"Noise RMS: {noise_rms:.2e}")
    print(f"Sample count: {len(noise_data)}")
    
    # Gaussianity tests
    k = kurtosis(noise_data)
    _, p_val = normaltest(noise_data)
    
    print(f"\n=== GAUSSIANITY TESTS ===")
    print(f"Kurtosis: {k:.3f} (Gaussian = 0)")
    print(f"Normality test p-value: {p_val:.3e}")
    
    if p_val < 0.05:
        print("WARNING: Noise is NON-GAUSSIAN (p < 0.05)")
    else:
        print("Noise appears Gaussian (p > 0.05)")
    
    # Save results to file
    with open('noise_results.txt', 'w') as f:
        f.write(f"{noise_std:.6e}\n")
        f.write(f"{p_val:.6e}\n")
        f.write(f"{k:.6f}\n")
    
    print("\nResults saved to 'noise_results.txt'")
    return noise_std, p_val, k

if __name__ == "__main__":
    try:
        noise_std, p_val, k = inspect_noise_statistics()
    except FileNotFoundError:
        print("ERROR: HDF5 file not found. Ensure you're in the right directory.")
        print("Current file needed: H-H1_LOSC_4_V1-1126256640-4096.hdf5")
