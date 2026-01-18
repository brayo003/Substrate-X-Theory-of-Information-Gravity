import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma

def simulate_vacuum_extraction():
    # Extraction levels from 0% to 99.9% of the 'Universal Limit'
    extraction_levels = np.linspace(0.01, 0.999, 100)
    
    # V12-G Health: As extraction goes up, health goes down
    health = 1.0 - extraction_levels
    
    # V12-G Tension: The Gamma Radar
    # We use abs(gamma(h)) to map the proximity to the Pole at 0.0
    tension = [abs(gamma(h)) for h in health]
    
    # Thresholds
    safety_limit = 5.0
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(extraction_levels * 100, tension, label='Substrate Tension (Gamma)', color='cyan', linewidth=2)
    plt.axhline(y=safety_limit, color='red', linestyle='--', label='V12-G Safety Redline (Reset Trigger)')
    
    plt.title("SXC-V12-G: Quantum Vacuum Stability Map", fontsize=14)
    plt.xlabel("Energy Extraction Level (%)", fontsize=12)
    plt.ylabel("Topological Tension ($|\Gamma(h)|$)", fontsize=12)
    plt.yscale('log') # Log scale to see the spike toward the Pole
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()
    
    # Save the visual evidence
    plt.savefig('vacuum_stability_radar.png')
    print("Simulation Complete. 'vacuum_stability_radar.png' generated.")
    
    # Data Summary
    critical_index = np.where(np.array(tension) >= safety_limit)[0][0]
    print(f"CRITICAL DATA: Vacuum unstable at {round(extraction_levels[critical_index]*100, 2)}% extraction.")

if __name__ == "__main__":
    simulate_vacuum_extraction()
