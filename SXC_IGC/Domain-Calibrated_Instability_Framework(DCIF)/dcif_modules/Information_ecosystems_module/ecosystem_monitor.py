import numpy as np
import time
from fetch_ecosystem_data import EcosystemDataFetcher
# Assuming your SXCOmegaEngine is in a file named engine.py
from engine import SXCOmegaEngine 

def run_global_monitor():
    fetcher = EcosystemDataFetcher()
    engine = SXCOmegaEngine()
    
    print("=== SXC GLOBAL ECOSYSTEM MONITOR ACTIVE ===")
    
    while True:
        # Pull real signal from the world
        signal = fetcher.fetch_latest_tension_signal()
        
        # Process through V12 Logic
        t_sys, phase = engine.step(signal)
        
        print(f"SIGNAL: {signal:.2f} | T_SYS: {t_sys:.4f} | PHASE: {phase}")
        
        if phase == "FIREWALL":
            print("⚠️ WARNING: SOCIAL SINGULARITY DETECTED. APPLYING FILTER.")
            
        time.sleep(5) # Real-time polling interval

if __name__ == "__main__":
    run_global_monitor()
