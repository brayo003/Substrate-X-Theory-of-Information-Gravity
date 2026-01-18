import numpy as np
from SXC_V12_CORE import SXCOmegaEngine

def execute_omega_recovery(initial_tension):
    engine = SXCOmegaEngine()
    engine.T_sys = initial_tension
    engine.phase = "FIREWALL"
    target_signal = 25.0
    
    print(f"--- STARTING OMEGA RECOVERY (T={initial_tension}) ---")
    
    stack = 0
    while engine.phase == "FIREWALL":
        stack += 1
        engine.apply_intervention("DEEP")
        engine.step(target_signal)
        print(f"Stack {stack}: T={engine.T_sys:.4f} | Phase={engine.phase}")
        
    print(f"RECOVERY COMPLETE IN {stack} STEPS.\n")

execute_omega_recovery(0.9664) # Your current state
execute_omega_recovery(3.0)    # The 'Terminal' state
