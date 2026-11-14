import matplotlib.pyplot as plt
import numpy as np

def plot_scaling():
    scales = [1e-15, 1e3, 1e6] # Quantum, Logistics, Seismic
    ratios = [24.1, 25.0, 457.5] # beta/gamma
    labels = ["Quantum", "Logistics", "Seismic"]
    
    plt.figure(figsize=(10, 6))
    plt.loglog(scales, ratios, 'ro-', lw=2)
    for i, label in enumerate(labels):
        plt.annotate(label, (scales[i], ratios[i]), textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.title("SXC-V12: Substrate Scaling Law (Log-Log)")
    plt.xlabel("Spatial Scale (meters)")
    plt.ylabel("Potential Ratio (beta/gamma)")
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.savefig('universal_scaling.png')
    print("SUCCESS: universal_scaling.png generated.")

if __name__ == "__main__":
    plot_scaling()
