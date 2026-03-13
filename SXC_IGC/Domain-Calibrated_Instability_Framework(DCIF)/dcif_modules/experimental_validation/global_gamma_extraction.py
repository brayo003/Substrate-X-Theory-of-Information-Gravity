import numpy as np
import pandas as pd

def extract_gamma(signal):
    # We measure the decay between successive peaks to find the TRUE Gamma
    peaks = [i for i in range(1, len(signal)-1) if signal[i-1] < signal[i] > signal[i+1]]
    if len(peaks) < 2: return 0.0
    
    # Logarithmic Decrement formula: gamma = (1/pi) * ln(A1/A2)
    ratios = []
    for i in range(len(peaks)-1):
        ratios.append(signal[peaks[i]] / signal[peaks[i+1]])
    
    avg_ratio = np.mean(ratios)
    emergent_gamma = np.log(avg_ratio) / np.pi
    return emergent_gamma, avg_ratio

# MOCK DATA REPRESENTING YOUR MODULES (Replace with actual module loads if needed)
domains = {
    "Finance": np.exp(-0.2 * np.linspace(0, 10, 100)) * np.cos(2 * np.pi * np.linspace(0, 10, 100)),
    "Seismic": np.exp(-0.153 * np.linspace(0, 10, 100)) * np.cos(2 * np.pi * np.linspace(0, 10, 100)),
    "Particle": np.exp(-0.05 * np.linspace(0, 10, 100)) * np.cos(2 * np.pi * np.linspace(0, 10, 100))
}

print(f"{'Domain':<12} | {'Emergent Gamma':<15} | {'Decay Ratio':<15} | {'Phi Match?'}")
print("-" * 60)

for name, signal in domains.items():
    g, r = extract_gamma(signal)
    phi_match = "YES (0.153)" if abs(g - 0.153) < 0.01 else "NO"
    print(f"{name:<12} | {g:<15.4f} | {r:<15.4f} | {phi_match}")

