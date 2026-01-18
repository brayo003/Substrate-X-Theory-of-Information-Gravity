import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Mocking data based on verified V7.1 and V7.2 trajectories
def generate_comparison():
    steps = np.linspace(0, 100, 100)
    
    # Model A: High Coupling (0.05) - High Contagion
    fragile_soc = 4.2 * (1 - np.exp(-0.05 * steps)) 
    
    # Model B: Low Coupling (0.005) - Resilient
    resilient_soc = 0.4 * (1 - np.exp(-0.04 * steps))

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(steps, fragile_soc, color='#ff4444', label='Fragile (w=0.05): Systemic Collapse', linewidth=2)
    ax.plot(steps, resilient_soc, color='#00ffcc', label='Resilient (w=0.005): Calibrated Buffer', linewidth=2)
    
    # Phase Markers
    ax.axhline(y=1.0, color='white', linestyle='--', alpha=0.3, label='Social Critical Threshold')
    ax.fill_between(steps, 1.0, 5.0, alpha=0.1, color='red')

    ax.set_title('Substrate Coupling Sensitivity: Information Gravity Propagation', fontsize=14)
    ax.set_xlabel('Integration Steps (Time)')
    ax.set_ylabel('Social Substrate Tension (T_soc)')
    ax.legend()
    ax.grid(alpha=0.1)

    plt.savefig('Coupling_Comparison.png')
    print("[SUCCESS] Comparison chart saved: Coupling_Comparison.png")
    plt.show()

if __name__ == "__main__":
    generate_comparison()
