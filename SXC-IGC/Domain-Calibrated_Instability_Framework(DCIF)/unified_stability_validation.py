import sys
import os
import numpy as np
sys.path.append(os.getcwd())

# Force import from V12 Master Core
try:
    from SXC_V12_CORE import SXCOmegaEngine as SXC_IGC_Core
    print("=== SXC-IGC UNIFIED STABILITY VALIDATION ===")
    print("✅ SUCCESS: Linked to V12 Master Core (Alpha 1.254)\n")
except ImportError as e:
    print(f"❌ FATAL: Could not find V12 Core file. Error: {e}")
    sys.exit(1)

def run_validation(steps=17547):
    engine = SXC_IGC_Core()
    results = []
    
    print(f"=== TEST 2: LONG-RUN STABILITY ===")
    for i in range(steps):
        # Using a synthetic signal loop for validation consistency
        signal = 40 + 10 * np.sin(i / 100.0) 
        t_sys, phase = engine.step(signal)
        results.append(t_sys)
        
    final_val = results[-1]
    max_val = max(np.abs(results))
    
    print(f"✅ Engine completed {steps} steps without error.")
    print(f"   Final state: {final_val:.6e}")
    print(f"   Max absolute value: {max_val:.6e}")
    
    if max_val < 5.0:
        print("✅ Engine remained numerically bounded.\n")
    else:
        print("❌ Engine Diverged.\n")

if __name__ == "__main__":
    run_validation()
