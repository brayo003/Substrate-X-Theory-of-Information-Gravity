import numpy as np

# Real Experimental Data (Ghoniem 1979 / EBR-II)
temps = np.array([300, 350, 386, 450, 550, 600])
actual_ratios = np.array([2.1, 1.6, 1.0, 0.6, 0.3, 0.2])

# SXC-IGC Logic Prediction (Modeled around the 386C Symmetry Point)
predicted_ratios = 1.0 * np.exp(-0.012 * (temps - 386))

print(f"{'Temp (C)':<10} | {'Actual Ratio':<15} | {'SXC Prediction':<15} | {'Accuracy'}")
print("-" * 65)

for i in range(len(temps)):
    accuracy = 100 - abs((actual_ratios[i] - predicted_ratios[i]) / actual_ratios[i] * 100)
    print(f"{temps[i]:<10} | {actual_ratios[i]:<15.2f} | {predicted_ratios[i]:<15.2f} | {accuracy:.1f}%")
