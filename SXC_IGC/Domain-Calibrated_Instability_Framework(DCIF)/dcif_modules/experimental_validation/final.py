import json
import os
import numpy as np

def run_stress_test():
    modules_dir = '.'
    # Target specific anchor points in the Fragility Spectrum
    targets = [
        'Quantum_Decoherence_Module', # Brittle (24.26)
        'seismic_module',              # Extreme Brittle (456.37)
        'energy_module',               # Stiff (5.31)
        'social_module',               # Stiff (4.31)
        'dark_matter_module'           # Elastic (0.04)
    ]
    
    # Global Excitation Signal (0 to 1.0)
    signals = np.linspace(0, 1.0, 11)
    
    print(f"{'SIGNAL':<8} | {'QUANTUM T':<10} | {'ENERGY T':<10} | {'SEISMIC T':<10} | {'DARKMAT T'}")
    print("-" * 70)

    # Load coefficients for each target
    configs = {}
    for t in targets:
        path = os.path.join(t, 'coefficients.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                configs[t] = data.get('coefficients', {})

    for s in signals:
        row = [f"{s:.1f}"]
        for t in targets:
            c = configs.get(t, {})
            b, g = c.get('beta', 0), c.get('gamma', 0)
            
            # The DCIF Tension Formula: T = beta*E - gamma*F
            # We assume F (Infrastructure) is constant at 0.5 for this stress test
            tension = (b * s) - (g * 0.5)
            tension = max(0, min(1.0, tension)) # Clamp to 0-1 range
            
            row.append(f"{tension:.4f}")
        
        print(" | ".join(row))

if __name__ == "__main__":
    run_stress_test()
