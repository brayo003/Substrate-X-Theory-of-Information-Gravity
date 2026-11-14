#!/usr/bin/env python3
"""
Minimal test of Substrate X rotation-decoherence prediction.
Formula: Γ(ω) = Γ₀ + k_rot * ω² / (1 + (ω/ω_max)²)
with k_rot = 4.5e-7 s, ω_max = 1e6 rad/s.
We simulate a two-level system (qubit) initially in a superposition,
and compute how the off-diagonal density matrix element decays under
this dephasing rate. We then plot the coherence decay for different ω.
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------- Substrate decoherence parameters ----------
Gamma0 = 1e3        # base decoherence rate (s⁻¹) – typical for a qubit
k_rot  = 4.5e-7     # from rotation-decoherence derivation (s)
omega_max = 1e6     # saturation frequency (rad/s)

def gamma(omega):
    """Total dephasing rate according to Substrate X."""
    return Gamma0 + k_rot * omega**2 / (1 + (omega/omega_max)**2)

# ---------- Simulate density matrix evolution ----------
def evolve_coherence(omega, t_max=5e-3, dt=1e-6):
    """
    Lindblad dephasing on a single qubit.
    dρ/dt = -i[H,ρ] + Γ(ω) * (σ_z ρ σ_z - ρ)
    For a free qubit (H=0) in initial state |+> = (|0>+|1>)/√2,
    the off-diagonal element ρ_01 decays as exp(-Γ * t).
    """
    Gamma = gamma(omega)
    n_steps = int(t_max / dt)
    t = np.linspace(0, t_max, n_steps)
    rho_01 = 0.5 * np.exp(-Gamma * t)  # initial coherence = 0.5
    return t, np.abs(rho_01)

# ---------- Run for several rotation frequencies ----------
frequencies = [0, 1e3, 1e4, 1e5, 5e5, 1e6, 2e6]  # rad/s
plt.figure(figsize=(10, 5))

for w in frequencies:
    t, coh = evolve_coherence(w, t_max=2e-3)
    plt.plot(t*1e3, coh, label=f'ω = {w:.0e} rad/s')

plt.xlabel('Time (ms)')
plt.ylabel('Coherence |ρ₀₁|')
plt.title('Substrate X Rotation‑Decoherence Prediction')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('decoherence_test.png')
print("Plot saved to decoherence_test.png")
plt.show()

# Print some example decoherence times
print("\nDecoherence half‑life (τ_1/2 = ln2 / Γ) for various ω:")
for w in [0, 1e3, 1e5, 1e6, 2e6]:
    g = gamma(w)
    tau = np.log(2) / g
    print(f"  ω = {w:8.0f} rad/s  →  Γ = {g:.2e} s⁻¹  →  τ½ = {tau*1e6:.2f} µs")
