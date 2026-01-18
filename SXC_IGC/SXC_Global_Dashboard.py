import time
import sys
import os
from engine import SXCOmegaEngine
from bridge_validator import validate_substrate_integrity

# Path linking to domain modules
sys.path.append(os.path.abspath("./Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/Information_ecosystems_module"))
from fetch_ecosystem_data import EcosystemDataFetcher

def run_dashboard():
    # Initial Integrity Check (Ramanujan-Sato Verification)
    validate_substrate_integrity()
    
    engine = SXCOmegaEngine()
    fetcher = EcosystemDataFetcher(mode="BURSTY") # Test for singularities
    
    print("\n" + "="*50)
    print("      SXC GLOBAL STABILITY DASHBOARD (V12)")
    print("="*50)
    
    try:
        while True:
            signal = fetcher.fetch_latest_tension_signal()
            t_sys, phase = engine.step(signal)
            
            # Dashboard Visualization
            status_bar = "█" * int(t_sys * 20) if t_sys > 0 else ""
            print(f"SIGNAL: {signal:>5.2f} SU | TENSION: [{status_bar:<20}] {t_sys:.4f} | PHASE: {phase}")
            
            if phase == "FIREWALL":
                print(">> [ALERT] SYSTEMIC SATURATION DETECTED. INTERVENTION ACTIVE.")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard Hibernated. Integrity maintained.")

if __name__ == "__main__":
    run_dashboard()
