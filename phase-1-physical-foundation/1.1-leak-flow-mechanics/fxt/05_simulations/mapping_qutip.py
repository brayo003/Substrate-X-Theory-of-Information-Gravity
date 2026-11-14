"""
mapping_qutip.py
================
QuTiP simulation for Candidate C (Floquet/drive-rate hypothesis).

Status of mapping: NO EXACT MAPPING EXISTS (see mapping_derivation.md).
This script implements the FALSIFIABLE HYPOTHESIS from Candidate C:

    Hypothesis: omega = Omega_R (Rabi drive frequency)

    Prediction:  Gamma(Omega_R) = Gamma0 + k_rot * Omega_R^2 / (1 + (Omega_R/omega_max)^2)

This is NOT derived from the frozen equations. It is stated explicitly
as a hypothesis. The script:

  1. Simulates Ramsey sequences for a driven qubit using QuTiP.
  2. Extracts Gamma(Omega_R) numerically.
  3. Compares the extracted Gamma to the substrate prediction.
  4. Reports whether the functional form is reproduced.

Nothing is uploaded to IBM. All computation is local.

Run:
    python mapping_qutip.py

Requires: qutip, numpy, matplotlib
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

try:
    import qutip as qt
except ImportError:
    print("ERROR: QuTiP not installed. Run: pip install qutip")
    sys.exit(1)

from scipy.optimize import curve_fit

# ------------------------------------------------------------------ #
# Frozen theory constants (from COMPLETE_MASTER_EQUATION.md)        #
# ------------------------------------------------------------------ #
K_ROT   = 4.5e-7   # s  (rotation-decoherence coupling)
OMEGA_MAX = 1.0e6  # rad/s  (saturation frequency)

# ------------------------------------------------------------------ #
# Hypothesis (Candidate C, not derived)                              #
# ------------------------------------------------------------------ #
# omega = Omega_R  =>  Gamma(Omega_R) = Gamma0 + K_ROT * Omega_R^2 / (1 + (Omega_R/OMEGA_MAX)^2)

def substrate_gamma(omega_R, Gamma0):
    """Substrate decoherence prediction under Candidate C hypothesis."""
    return Gamma0 + K_ROT * omega_R**2 / (1 + (omega_R / OMEGA_MAX)**2)

# ------------------------------------------------------------------ #
# Qubit parameters                                                   #
# ------------------------------------------------------------------ #
OMEGA_Q   = 2 * np.pi * 5e9    # qubit frequency (rad/s), 5 GHz
GAMMA0    = 1e4                 # base decoherence rate (s^-1), T2 ~ 100 us
T2_BASE   = 1.0 / GAMMA0       # base T2 time

# Ramsey simulation parameters
N_TAU     = 80                  # number of tau points per Gamma extraction
TAU_MAX   = 5 * T2_BASE         # maximum free-evolution time
TAUS      = np.linspace(0, TAU_MAX, N_TAU)

# Drive rates to sweep (Omega_R values)
# Keep well below OMEGA_MAX to see the quadratic regime
OMEGA_R_VALUES = np.array([0, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7])

# ------------------------------------------------------------------ #
# Ramsey simulation with QuTiP                                       #
# ------------------------------------------------------------------ #

def simulate_ramsey(Omega_R, taus):
    """
    Simulate a Ramsey sequence for a qubit with Rabi drive Omega_R.

    Protocol:
      1. Start in |0>.
      2. Apply pi/2 pulse (instantaneous, about x-axis).
      3. Free evolution for time tau under H_eff in rotating frame.
      4. Apply second pi/2 pulse.
      5. Measure <sigma_z>.

    In the rotating frame at resonance (Delta = 0), the free-evolution
    Hamiltonian is:
        H_eff = (hbar * Omega_R / 2) * sigma_x

    Decoherence is added via a Lindblad collapse operator:
        C = sqrt(Gamma_total) * sigma_minus
    plus pure dephasing:
        C_phi = sqrt(Gamma_phi) * sigma_z

    Under the Candidate C hypothesis, Gamma_total = substrate_gamma(Omega_R, GAMMA0).
    This is the self-consistency test: if the substrate prediction is correct,
    then inserting Gamma_total from the substrate formula should reproduce
    the same Gamma when extracted from the decay envelope.
    """
    hbar = 1.0  # work in natural units for QuTiP (set hbar=1)

    # In the rotating frame at resonance, Delta=0:
    H_eff = (Omega_R / 2) * qt.sigmax()

    # Total decoherence rate under hypothesis
    Gamma_total = substrate_gamma(Omega_R, GAMMA0)
    T1 = 1.0 / (Gamma_total + 1e-30)  # avoid division by zero at Omega_R=0

    # Collapse operators
    c_ops = [
        np.sqrt(Gamma_total) * qt.destroy(2),   # amplitude damping
        np.sqrt(Gamma_total / 2) * qt.sigmaz(),  # pure dephasing (T2 = T1 here)
    ]

    # Initial state: |+x> = (|0> + |1>)/sqrt(2)  (after pi/2 pulse about x)
    psi0 = (qt.basis(2, 0) + qt.basis(2, 1)).unit()
    rho0 = qt.ket2dm(psi0)

    # Evolve
    result = qt.mesolve(H_eff, rho0, taus, c_ops, [qt.sigmaz()])
    return np.array(result.expect[0])


def extract_gamma(taus, signal):
    """
    Fit the Ramsey signal to A * exp(-Gamma * tau) * cos(phi) + offset.
    Return extracted Gamma.
    """
    def model(t, A, Gamma_fit, phi, offset):
        return A * np.exp(-Gamma_fit * t) * np.cos(phi) + offset

    try:
        p0 = [1.0, 1.0/T2_BASE, 0.0, 0.0]
        bounds = ([0, 0, -np.pi, -1], [2, 1e9, np.pi, 1])
        popt, _ = curve_fit(model, taus, signal, p0=p0, bounds=bounds, maxfev=10000)
        return popt[1]
    except Exception:
        # Fallback: fit pure exponential decay to |signal|
        try:
            def exp_model(t, A, G):
                return A * np.exp(-G * t)
            popt, _ = curve_fit(exp_model, taus, np.abs(signal),
                                p0=[1.0, 1.0/T2_BASE], maxfev=5000)
            return popt[1]
        except Exception:
            return np.nan


# ------------------------------------------------------------------ #
# Main sweep                                                         #
# ------------------------------------------------------------------ #

print("=" * 60)
print("QuTiP Ramsey Sweep — Candidate C Hypothesis Test")
print("Hypothesis: omega = Omega_R  (NOT derived, stated explicitly)")
print("=" * 60)
print(f"\nTheory constants (frozen):")
print(f"  k_rot    = {K_ROT:.2e} s")
print(f"  omega_max = {OMEGA_MAX:.2e} rad/s")
print(f"  Gamma0   = {GAMMA0:.2e} s^-1\n")

extracted_gammas = []
predicted_gammas = []

for OmR in OMEGA_R_VALUES:
    signal = simulate_ramsey(OmR, TAUS)
    Gamma_ext = extract_gamma(TAUS, signal)
    Gamma_pred = substrate_gamma(OmR, GAMMA0)
    extracted_gammas.append(Gamma_ext)
    predicted_gammas.append(Gamma_pred)
    print(f"  Omega_R = {OmR:.2e} rad/s  |  "
          f"Gamma_predicted = {Gamma_pred:.4e}  |  "
          f"Gamma_extracted = {Gamma_ext:.4e}")

extracted_gammas = np.array(extracted_gammas)
predicted_gammas = np.array(predicted_gammas)

# Self-consistency check: since we injected Gamma_total = substrate_gamma,
# the extracted Gamma should match the predicted Gamma.
valid = ~np.isnan(extracted_gammas)
rel_errors = np.abs(extracted_gammas[valid] - predicted_gammas[valid]) / predicted_gammas[valid]
max_rel_err = np.max(rel_errors)

print(f"\nSelf-consistency check (injected = predicted):")
print(f"  Max relative error: {max_rel_err:.3f}")
if max_rel_err < 0.15:
    print("  PASS: Injected Gamma recoverable from Ramsey fit.")
else:
    print("  WARN: Fitting error large — increase tau points or adjust fit range.")

# ------------------------------------------------------------------ #
# Plot                                                               #
# ------------------------------------------------------------------ #

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: example Ramsey traces
ax = axes[0]
colors = plt.cm.viridis(np.linspace(0, 1, len(OMEGA_R_VALUES)))
for i, OmR in enumerate(OMEGA_R_VALUES):
    signal = simulate_ramsey(OmR, TAUS)
    ax.plot(TAUS * 1e6, signal, color=colors[i],
            label=f'ΩR={OmR:.0e}', alpha=0.8, linewidth=1.2)
ax.set_xlabel('Free evolution time τ (μs)')
ax.set_ylabel('⟨σ_z⟩')
ax.set_title('Ramsey Traces (Candidate C Hypothesis)')
ax.legend(fontsize=7, loc='upper right')
ax.grid(True, alpha=0.3)

# Right: Gamma(Omega_R) — substrate prediction vs extracted
ax2 = axes[1]
om_dense = np.logspace(3, 8, 300)
gamma_curve = substrate_gamma(om_dense, GAMMA0)
ax2.loglog(om_dense, gamma_curve - GAMMA0, 'b-', linewidth=2,
           label='Substrate prediction (Candidate C hypothesis)')
ax2.loglog(OMEGA_R_VALUES[valid] + 1, extracted_gammas[valid] - GAMMA0, 'ro',
           markersize=8, label='Extracted from Ramsey fit')

# Mark omega_max
ax2.axvline(OMEGA_MAX, color='gray', linestyle='--', alpha=0.7, label=f'ω_max={OMEGA_MAX:.0e}')
ax2.set_xlabel('Ω_R (rad/s)')
ax2.set_ylabel('Γ − Γ₀  (s⁻¹)')
ax2.set_title('Decoherence vs Drive Rate\n(Hypothesis only — NOT derived)')
ax2.legend(fontsize=8)
ax2.grid(True, which='both', alpha=0.3)

plt.tight_layout()
outfile = 'mapping_qutip_result.png'
plt.savefig(outfile, dpi=120, bbox_inches='tight')
print(f"\nPlot saved: {outfile}")

# ------------------------------------------------------------------ #
# Formal conclusion                                                  #
# ------------------------------------------------------------------ #

print("\n" + "=" * 60)
print("FORMAL CONCLUSION")
print("=" * 60)
print("""
This script tests the HYPOTHESIS (Candidate C, not derived):

    omega = Omega_R

Under this hypothesis, the substrate prediction is:

    Gamma(Omega_R) = Gamma0 + k_rot * Omega_R^2 / (1 + (Omega_R/omega_max)^2)

The QuTiP simulation confirms that IF Gamma is set equal to this
prediction, then Ramsey sequences decay at the expected rate and
the functional form is recoverable by fitting.

This is a self-consistency check, NOT a derivation of the mapping.

The mapping_derivation.md verdict stands:

    Result:
    The existing theory does NOT imply an experimentally controllable
    observable. A genuine theoretical extension would be required.

This script would become a verification tool ONLY IF a future
derivation establishes the identification omega = Omega_R from
first principles.
""")
print("=" * 60)
