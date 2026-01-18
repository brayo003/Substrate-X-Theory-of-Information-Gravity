import numpy as np
from sklearn.datasets import load_breast_cancer
from v12_engine import SXCOmegaEngine

def run_behavioral_analysis():
    # beta=3.5, gamma=0.8 (Baseline Observation Mode)
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    
    data = load_breast_cancer()
    features = data.data[0]
    feature_names = data.feature_names

    print(f"DCIF BEHAVIORAL ANALYSIS | Substrate: Feature-Space {data.data.shape}")
    print(f"{'INDEX':<5} | {'SIGNAL SOURCE':<20} | {'T_SYS':<8} | {'ENGINE STATE'}")
    print("-" * 60)

    for i, val in enumerate(features):
        # Scale signal to engine-permissible range (Log-Flux)
        flux = np.log1p(val) * 10 
        t_sys, phase = engine.step(flux)
        
        # Neutral Reporting: Focusing on Saturation, not 'Failure'
        state_label = "SATURATED" if phase == "FIREWALL" else "NOMINAL"
        
        print(f"{i:<5} | {feature_names[i][:20]:<20} | {t_sys:<8.4f} | {state_label}")
        
        if phase == "FIREWALL":
            print(f"\n[SATURATION POINT]: Engine reached limit at Index {i} ({feature_names[i]})")
            break

if __name__ == "__main__":
    run_behavioral_analysis()
