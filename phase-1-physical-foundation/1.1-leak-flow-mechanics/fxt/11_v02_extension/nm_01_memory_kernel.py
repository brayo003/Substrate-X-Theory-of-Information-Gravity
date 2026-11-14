"""
nm_01_memory_kernel.py
======================
Task 1: Non-Markovian memory-kernel master equation for the C2 substrate
        dephasing channel.

DERIVATION SUMMARY
------------------
Starting point: the full Nakajima-Zwanzig / cumulant expansion for a qubit
coupled to a Gaussian bath via H_int = g J(t) sigma_z.

The exact coherence (no Markov approximation) is:

    rho_01(t) = rho_01(0) * exp(-Phi(t))                           [EXACT]

where the dephasing function is:

    Phi(t) = (2 g^2 / hbar^2) * integral_0^t dt' (t - t') C_JJ(t')  [DEPH-FUNC]

This follows from the second-order cumulant expansion of the time-ordered
propagator, which is exact for Gaussian noise (see Kubo 1963; Breuer & Petruccione
Ch.3).  No Born-Markov approximation has been applied.

For the C2 substrate:
    C_JJ(t') = S0 * exp(-t' / tau_B)                               [CORR]

where:
    S0 = (2/3) s0^2 omega_rot^2 r_q^2    (rotational current variance)
    tau_B                                  (substrate bath correlation time)

Substituting [CORR] into [DEPH-FUNC] and integrating exactly:

    Phi(t) = (2 g^2 S0 / hbar^2) * tau_B * [t - tau_B * (1 - exp(-t/tau_B))]
           = Gamma_markov * tau_B * [t - tau_B * (1 - exp(-t/tau_B))]  [EXACT-PHI]

where  Gamma_markov = 2 g^2 S0 tau_B / hbar^2  is the Markov rate.

LIMITS
------
Markov limit (t >> tau_B):
    Phi(t) -> Gamma_markov * t                   (pure exponential decay)

Short-time / non-Markovian limit (t << tau_B):
    Phi(t) -> Gamma_markov * t^2 / (2 tau_B)    (Gaussian initial decay)
            = (Gamma_markov / (2 tau_B)) * t^2

This Gaussian onset is the experimentally distinguishable prediction.
The crossover occurs at t* ~ tau_B.

The Markovian approximation replaces [EXACT-PHI] with Gamma_markov * t.
The mismatch at time t is:
    delta(t) = Phi_exact(t) - Gamma_markov * t
             = -Gamma_markov * tau_B * (1 - exp(-t/tau_B))

At t = tau_B: delta = -Gamma_markov * tau_B * (1 - 1/e) ~ -0.63 * Gamma_markov * tau_B

This script:
1. Implements Phi(t) exactly.
2. Compares coherence under exact vs Markov models.
3. Derives the effective non-Markovian rate Gamma_eff(t) = dPhi/dt.
4. Saves outputs to 11_v02_extension/outputs/nm_01/
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── output directory ────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
OUTDIR = HERE / "outputs" / "nm_01"
OUTDIR.mkdir(parents=True, exist_ok=True)

# ── physical constants (dimensionless units: hbar=1, g=1, s0=1, etc.) ──────
# We work in units where Gamma_markov is the control variable.
# The shape of the coherence depends only on the dimensionless product
# x = Gamma_markov * tau_B  (called "non-Markovianity parameter" NMP).


def phi_exact(t: np.ndarray, gamma_markov: float, tau_B: float) -> np.ndarray:
    """
    Exact dephasing function Phi(t) from [EXACT-PHI].

    Parameters
    ----------
    t           : time array (s or dimensionless)
    gamma_markov: Markov dephasing rate = 2 g^2 S0 tau_B / hbar^2   (s^-1)
    tau_B       : substrate bath correlation time (s)

    Returns
    -------
    Phi(t) >= 0  (monotonically increasing)
    """
    return gamma_markov * tau_B * (t / tau_B - 1.0 + np.exp(-t / tau_B))


def phi_markov(t: np.ndarray, gamma_markov: float) -> np.ndarray:
    """Markov approximation: Phi(t) = Gamma * t."""
    return gamma_markov * t


def coherence_exact(t, gamma_markov, tau_B):
    return np.exp(-phi_exact(t, gamma_markov, tau_B))


def coherence_markov(t, gamma_markov):
    return np.exp(-phi_markov(t, gamma_markov))


def gamma_eff(t: np.ndarray, gamma_markov: float, tau_B: float) -> np.ndarray:
    """
    Instantaneous / time-local dephasing rate = dPhi/dt.

    gamma_eff(t) = Gamma_markov * (1 - exp(-t/tau_B))

    At t=0: gamma_eff = 0   (no instantaneous decay at start)
    At t>>tau_B: gamma_eff -> Gamma_markov  (recovers Markov rate)
    """
    return gamma_markov * (1.0 - np.exp(-t / tau_B))


# ── mismatch between exact and Markov models ────────────────────────────────

def coherence_mismatch(t, gamma_markov, tau_B):
    """
    |C_exact(t) - C_markov(t)|  -- absolute difference in coherence.
    """
    return np.abs(coherence_exact(t, gamma_markov, tau_B)
                  - coherence_markov(t, gamma_markov))


# ── Figure 1: coherence traces for three NMP regimes ────────────────────────

def plot_coherence_regimes(gamma_markov: float = 1.0):
    """
    Plot coherence Re[rho_01(t)] for three values of NMP = Gamma * tau_B:
      - Markovian:      NMP = 0.01
      - Transitional:   NMP = 0.3
      - Non-Markovian:  NMP = 3.0
    """
    nmp_vals = [0.01, 0.3, 1.0, 3.0]
    labels   = [f"NMP = {x}" for x in nmp_vals]
    colors   = ["#2166AC", "#4DAC26", "#F4A582", "#D6604D"]

    # time in units of 1/Gamma_markov
    t_norm = np.linspace(0, 5.0, 500)  # t * Gamma_markov

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.plot(t_norm, np.exp(-t_norm), "k--", lw=2, label="Markov (reference)", zorder=5)
    for nmp, label, c in zip(nmp_vals, labels, colors):
        tau_B = nmp / gamma_markov
        C = coherence_exact(t_norm / gamma_markov, gamma_markov, tau_B)
        ax.plot(t_norm, C, color=c, lw=2, label=label)
    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$")
    ax.set_ylabel(r"Coherence $|\rho_{01}(t)|$")
    ax.set_title("Non-Markovian coherence decay\nvs. Markov exponential")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(t_norm, np.zeros_like(t_norm), "k--", lw=1.5, alpha=0.5)
    for nmp, label, c in zip(nmp_vals, labels, colors):
        tau_B = nmp / gamma_markov
        delta = coherence_exact(t_norm / gamma_markov, gamma_markov, tau_B) \
              - np.exp(-t_norm)
        ax.plot(t_norm, delta, color=c, lw=2, label=label)
    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$")
    ax.set_ylabel(r"$C_{\rm exact}(t) - C_{\rm Markov}(t)$")
    ax.set_title("Mismatch: exact − Markov\n(positive = Markov underestimates coherence)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm01_coherence_regimes.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm01_coherence_regimes.png")


# ── Figure 2: effective rate Gamma_eff(t) ────────────────────────────────────

def plot_gamma_eff(gamma_markov: float = 1.0):
    t_norm = np.linspace(0, 5.0, 500)
    nmp_vals = [0.1, 0.5, 1.0, 3.0]
    colors   = ["#2166AC", "#4DAC26", "#F4A582", "#D6604D"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.axhline(gamma_markov, color="k", ls="--", lw=2, label=r"$\Gamma_{\rm Markov}$")
    for nmp, c in zip(nmp_vals, colors):
        tau_B = nmp / gamma_markov
        g_eff = gamma_eff(t_norm / gamma_markov, gamma_markov, tau_B)
        ax.plot(t_norm, g_eff, color=c, lw=2, label=f"NMP = {nmp}")
    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$")
    ax.set_ylabel(r"$\Gamma_{\rm eff}(t) = d\Phi/dt$")
    ax.set_title("Time-local (instantaneous) dephasing rate\n"
                 r"$\Gamma_{\rm eff}(t) = \Gamma_{\rm Markov}(1 - e^{-t/\tau_B})$")
    ax.legend(fontsize=9)
    ax.set_ylim(0, gamma_markov * 1.15)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "nm01_gamma_eff.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm01_gamma_eff.png")


# ── Figure 3: short-time Gaussian onset ─────────────────────────────────────

def plot_gaussian_onset(gamma_markov: float = 1.0, nmp: float = 2.0):
    """
    Zoom into t << tau_B to show the Gaussian onset.
    Exact:  Phi(t) ~ Gamma * t^2 / (2 tau_B)
    Markov: Phi(t) = Gamma * t
    """
    tau_B  = nmp / gamma_markov
    t      = np.linspace(0, 0.8 * tau_B, 300)
    t_norm = t * gamma_markov

    phi_ex  = phi_exact(t, gamma_markov, tau_B)
    phi_mk  = phi_markov(t, gamma_markov)
    phi_gauss = gamma_markov * t**2 / (2.0 * tau_B)  # short-time approximation

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.plot(t_norm, phi_ex,    lw=2, color="#D6604D", label=r"Exact $\Phi(t)$")
    ax.plot(t_norm, phi_mk,    lw=2, color="#2166AC", ls="--", label=r"Markov $\Gamma t$")
    ax.plot(t_norm, phi_gauss, lw=2, color="#4DAC26", ls=":", label=r"Gaussian approx $\Gamma t^2/(2\tau_B)$")
    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$")
    ax.set_ylabel(r"$\Phi(t)$  (dephasing function)")
    ax.set_title(f"Short-time behaviour (NMP = {nmp})\nt restricted to $t < 0.8 \\tau_B$")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    C_ex    = np.exp(-phi_ex)
    C_mk    = np.exp(-phi_mk)
    C_gauss = np.exp(-phi_gauss)
    ax.plot(t_norm, C_ex,    lw=2, color="#D6604D", label="Exact coherence")
    ax.plot(t_norm, C_mk,    lw=2, color="#2166AC", ls="--", label="Markov (exponential)")
    ax.plot(t_norm, C_gauss, lw=2, color="#4DAC26", ls=":", label="Gaussian approximation")
    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$")
    ax.set_ylabel(r"$|\rho_{01}(t)|$")
    ax.set_title("Coherence: Gaussian onset vs exponential\n"
                 "(Non-Markovian signature in this window)")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm01_gaussian_onset.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm01_gaussian_onset.png")


# ── Numerical verification of the exact formula ─────────────────────────────

def verify_exact_formula(gamma_markov: float = 1.0, tau_B: float = 1.0):
    """
    Verify [EXACT-PHI] by numerical integration of [DEPH-FUNC].
    Both should agree to machine precision.
    """
    t_vals = np.linspace(0, 5.0 / gamma_markov, 200)
    errors = []
    for t in t_vals:
        # numerical integral: int_0^t (t - t') * S0 * exp(-t'/tau_B) dt'
        # with g^2/hbar^2 * 2 * S0 absorbed into gamma_markov = 2g^2 S0 tau_B/hbar^2
        # so integrand = (gamma_markov / tau_B) * (t - t') * exp(-t'/tau_B)
        t_prime = np.linspace(0, t, 2000)
        if len(t_prime) < 2:
            continue
        integrand = (gamma_markov / tau_B) * (t - t_prime) * np.exp(-t_prime / tau_B)
        phi_numerical = np.trapz(integrand, t_prime)
        phi_analytic  = phi_exact(np.array([t]), gamma_markov, tau_B)[0]
        errors.append(abs(phi_numerical - phi_analytic))

    max_err = max(errors) if errors else 0.0
    # 2000-point trapz gives ~3e-6 quadrature error; analytic formula is exact
    status  = "PASS" if max_err < 1e-5 else "FAIL"
    print(f"  Numerical vs analytic Phi(t) verification: max error = {max_err:.2e}  [{status}]")
    return max_err, status


# ── Summary JSON ─────────────────────────────────────────────────────────────

def write_summary(max_err: float, status: str):
    summary = {
        "task": "nm_01_memory_kernel",
        "status": status,
        "derivation": {
            "exact_coherence": "rho_01(t) = rho_01(0) * exp(-Phi(t))",
            "dephasing_function": "Phi(t) = Gamma_markov * tau_B * [t/tau_B - 1 + exp(-t/tau_B)]",
            "correlation_function": "C_JJ(t) = S0 * exp(-t/tau_B)",
            "S0_definition": "S0 = (2/3) * s0^2 * omega_rot^2 * r_q^2",
            "Gamma_markov_definition": "Gamma_markov = 2 g^2 S0 tau_B / hbar^2",
            "method": "Second-order cumulant expansion (exact for Gaussian noise, no Markov approx)",
            "reference": "Kubo 1963; Breuer & Petruccione Ch.3"
        },
        "limits": {
            "Markov_limit": "tau_B -> 0, Phi(t) -> Gamma_markov * t  (exponential)",
            "short_time_NM": "t << tau_B, Phi(t) ~ Gamma_markov * t^2 / (2 tau_B)  (Gaussian)",
            "crossover_time": "t* ~ tau_B"
        },
        "distinguishable_prediction": {
            "signature": "Gaussian initial decay instead of exponential at t < tau_B",
            "effective_rate": "Gamma_eff(t) = Gamma_markov * (1 - exp(-t/tau_B))",
            "NM_parameter": "NMP = Gamma_markov * tau_B  (NMP >> 1 = strongly non-Markovian)",
            "stress_test_mismatch_at_NMP_1": "~0.34 (from 07_derivation_stress)",
            "stress_test_mismatch_at_NMP_10": "~0.70 (from 07_derivation_stress)"
        },
        "verification": {
            "numerical_vs_analytic_max_error": max_err,
            "result": status
        },
        "new_free_parameter": "tau_B (substrate bath correlation time)",
        "old_free_parameters": ["Gamma0", "k_rot", "omega_max"],
        "next_task": "nm_02_parameter_space.py — map distinguishability across (omega_rot, tau_B)"
    }
    path = OUTDIR / "nm01_summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [saved] nm01_summary.json")
    return summary


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NM-01: Memory-kernel master equation")
    print("=" * 60)

    max_err, status = verify_exact_formula(gamma_markov=1.0, tau_B=1.0)

    print("  Generating figures...")
    plot_coherence_regimes(gamma_markov=1.0)
    plot_gamma_eff(gamma_markov=1.0)
    plot_gaussian_onset(gamma_markov=1.0, nmp=2.0)

    summary = write_summary(max_err, status)

    print()
    print("KEY RESULT:")
    print("  Exact coherence: C(t) = exp(-Phi(t))")
    print("  Phi(t) = Gamma * tau_B * [t/tau_B - 1 + exp(-t/tau_B)]")
    print("  Short time (t << tau_B): C(t) ~ exp(-Gamma * t^2 / (2*tau_B))  [GAUSSIAN]")
    print("  Long  time (t >> tau_B): C(t) ~ exp(-Gamma * t)                [EXPONENTIAL]")
    print("  This Gaussian onset is absent from the Markov model.")
    print("  It is experimentally distinguishable at t_free < tau_B.")
    print()
    print(f"  Verification status: {status}")
    print(f"  Outputs: {OUTDIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
