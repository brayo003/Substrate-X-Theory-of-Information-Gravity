import json
import numpy as np
from v12_engine import SXCOmegaEngine

def run_dcif_bio_experiment():
    engine = SXCOmegaEngine(beta=4.2, gamma=0.75) # Aggressive Bio Tuning
    
    # In a real run, we parse tcga_sample.json. 
    # Here, we generate a high-entropy signal based on TCGA volatility profiles.
    # Sigma 0.8 represents the instability of late-stage dysregulation.
    biological_signals = np.random.lognormal(mean=3.0, sigma=0.8, size=50)
    
    print(f"{'STEP':<5} | {'SIGNAL':<10} | {'T_SYS':<10} | {'PHASE':<10}")
    print("-" * 45)
    
    for i, s in enumerate(biological_signals):
        t_sys, phase = engine.step(s)
        if i % 5 == 0:
            print(f"{i:<5} | {s:<10.2f} | {t_sys:<10.4f} | {phase:<10}")

if __name__ == "__main__":
    run_dcif_bio_experiment()
