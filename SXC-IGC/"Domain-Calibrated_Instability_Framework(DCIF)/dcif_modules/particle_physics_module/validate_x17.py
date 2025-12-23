import numpy as np
import pandas as pd

# Theoretical Parameters
M_X17 = 17.01  # MeV
G_B_THEORY = 1.15e-3 # Our refined Baryon coupling

def check_consistency():
    df = pd.read_csv('global_constraints.csv')
    print(f"--- X17 PARAMETER VALIDATION (Mass: {M_X17} MeV) ---")
    
    for _, row in df.iterrows():
        limit = row['coupling_limit']
        status = row['status']
        
        if status == "SIGNAL":
            match = "VALID" if abs(G_B_THEORY - limit)/limit < 0.2 else "OFF-TARGET"
            print(f"[Nuclear] {row['target']}: Theory {G_B_THEORY:.2e} vs Exp {limit:.2e} -> {match}")
        
        if status == "EXCLUSION":
            # For Protophobic: g_p is suppressed, so we check if our g_b stays safe
            safe = "SAFE" if G_B_THEORY * 0.1 < limit else "VIOLATED"
            print(f"[Particle] {row['target']}: Exclusion {limit:.2e} -> {safe} (Assumes Protophobia)")

check_consistency()
