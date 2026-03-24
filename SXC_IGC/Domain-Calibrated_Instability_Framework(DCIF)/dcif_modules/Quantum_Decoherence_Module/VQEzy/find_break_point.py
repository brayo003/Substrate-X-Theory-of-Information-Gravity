import numpy as np

toronto_tension = [0.5238, 0.7257, 0.5749, 0.6151, 0.4280]

def simulate_load(beta_value):
    t_sys = 0.0
    phase = 'NOMINAL'
    for t in toronto_tension:
        E = 1 - np.exp(-t * 2.0)
        gamma_eff = 5.0 if phase == 'FIREWALL' else 1.0
        t_sys += (E * beta_value - gamma_eff * 0.8 * t_sys) * 0.05
        if t_sys > 1.0: phase = 'FIREWALL'
    return t_sys, phase

print("=== DCIF: SEARCHING FOR SUBSTRATE BREAK-POINT ===")
for b in range(1, 21):
    final_t, status = simulate_load(b)
    indicator = "!!!" if status == 'FIREWALL' else "..."
    print(f"Beta (Gate Density) {b:2}: Stress {final_t:.4f} | {status} {indicator}")
