import numpy as np

# Experimental Limit from NA48/2 (CERN)
# For m_x = 17 MeV, the coupling to protons (g_p) must be very small
NA48_LIMIT_GP = 8e-4 

# Your Model Values
g_b = 1.15e-3 # Your validated Baryon coupling
protophobic_suppression = 0.05 # Suppression factor for protons

g_p_actual = g_b * protophobic_suppression
g_n_actual = g_b * (1 - protophobic_suppression)

print("--- PROTOPHOBIC INTEGRITY CHECK ---")
print(f"Baryon Coupling (g_b): {g_b:.2e}")
print(f"Calculated g_p:         {g_p_actual:.2e}")
print(f"Calculated g_n:         {g_n_actual:.2e}")

print("-" * 35)
if g_p_actual < NA48_LIMIT_GP:
    print(f"STATUS: SAFE vs NA48/2 (CERN) ✓")
    print(f"Ratio g_n/g_p: {g_n_actual/g_p_actual:.1f} (High Protophobicity)")
else:
    print(f"STATUS: FALSIFIED (g_p too high) ❌")

# Final verification for 8Be signal
# The signal strength depends on (g_p + g_n)
signal_strength = abs(g_p_actual + g_n_actual)
print(f"Effective 8Be Signal:  {signal_strength:.2e}")
