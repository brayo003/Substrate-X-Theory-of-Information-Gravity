import numpy as np
from SXC_V12_CORE import SXCOmegaEngine

def find_mst():
    print(f"{'SIGNAL':<8} | {'FINAL TENSION':<15} | {'STATUS'}")
    print("-" * 45)
    
    for test_signal in range(120, 501, 20):
        engine = SXCOmegaEngine()
        stable = True
        for day in range(200):
            engine.apply_intervention("DEEP") # Maximum possible daily repair
            t, p = engine.step(test_signal)
            if t > 10.0:
                stable = False
                break
        
        status = "STABLE-SATURATED" if stable else "SYSTEMIC COLLAPSE"
        print(f"{test_signal:<8} | {t:>13.4f} | {status}")

find_mst()
