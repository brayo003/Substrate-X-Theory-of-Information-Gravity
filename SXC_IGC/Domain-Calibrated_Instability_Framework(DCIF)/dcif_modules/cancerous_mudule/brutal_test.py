import numpy as np
from v12_engine import SXCOmegaEngine

def run_unregulated_test():
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    
    # NO HOMEOPATHY, NO REGULATION. Just raw, accumulating noise.
    current_signal = 10.0 
    print(f"STARTING BRUTAL TEST: Zero Regulation")
    print("-" * 45)
    
    for i in range(100):
        # The signal just grows and fluctuates with no one to pull it back
        current_signal += np.random.normal(2, 5.0) 
        
        abs_s = abs(current_signal)
        t_sys, phase = engine.step(abs_s)
        
        if i % 10 == 0 or phase == "FIREWALL":
            print(f"Step {i:03d} | Signal: {abs_s:6.2f} | T_SYS: {t_sys:6.4f} | Phase: {phase}")
            if phase == "FIREWALL":
                break

if __name__ == "__main__":
    run_unregulated_test()
