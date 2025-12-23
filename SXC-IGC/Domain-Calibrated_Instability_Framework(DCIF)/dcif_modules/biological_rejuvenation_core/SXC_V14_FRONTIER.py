import numpy as np
from SXC_V13_FINAL import SXCUnifiedEngine

def find_sustainability():
    print(f"{'TAX RATE':<10} | {'LIFETIMES':<10} | {'SURVIVABILITY'}")
    print("-" * 45)
    
    for tax in [0.02, 0.01, 0.005, 0.003, 0.001]:
        engine = SXCUnifiedEngine()
        engine.cost_per_pulse = tax
        lifetimes = 0
        
        while engine.integrity > 0.1 and lifetimes < 200:
            lifetimes += 1
            for _ in range(500): engine.step(25.0) 
            for _ in range(20): engine.step(85.0)
            for _ in range(3): engine.apply_intervention()
            
        status = "HIGH" if lifetimes > 100 else "CRITICAL"
        print(f"{tax:<10} | {lifetimes:<10} | {status}")

find_sustainability()
