import numpy as np
from SXC_V12_CORE import SXCOmegaEngine

engine = SXCOmegaEngine()
# We force a massive signal (terminal disease or market total collapse)
terminal_signal = 120.0 

print(f"{'DAY':<5} | {'TENSION':<8} | {'γ (REPAIR)':<12} | {'INTERVENTION'}")
print("-" * 55)

for day in range(1, 101):
    # Attempt a "DEEP CLEAN" every single day to see if it can stop the rise
    engine.apply_intervention("DEEP")
    t, p = engine.step(terminal_signal)
    
    if day % 5 == 0:
        print(f"{day:<5} | {t:>8.4f} | {engine.gamma:>12.4f} | ATTEMPTED RESET")
    
    if t > 10.0:
        print(f"\n[!!!] SYSTEMIC COLLAPSE AT DAY {day} [!!!]")
        print(f"Final Tension: {t:.4f} | The 'Gravity' is now Infinite.")
        break
