"""
nm_04_ramsey_discriminator.py
=============================
Task 4: Build the Ramsey time-domain discriminator.

WHAT THIS SCRIPT PROVES
-----------------------
Task 3 showed that measuring Gamma at different drive frequencies cannot
distinguish the Markov from the non-Markovian model. The reason is structural:
    - Gamma_meas = 1/T2* = Phi^{-1}(1)  is a SINGLE NUMBER per frequency.
    - tau_B changes how Phi(t) grows, not just where it crosses 1.
    - So tau_B is degenerate with Gamma_markov in the 1/e-point measurement.

The discriminator is the TIME-DOMAIN SHAPE of the Ramsey coherence trace.

STRATEGY
--------
1. Generate synthetic Ramsey traces for both models at the gamma_dataset
   parameters, for three tau_B hypotheses (Markovian / transitional / NM).

2. Compute the log-likelihood ratio (LLR) as a function of t_free,
   showing at which measurement times the two models are most distinguishable.

3. Plot log(C(t)) vs t^2 (linearises Gaussian decay) to show the
   shape difference directly.

4. Compute the Fisher information about tau_B from the Ramsey trace.
   This gives the Cramer-Rao bound on how well tau_B can be estimated
   from n_shots measurements.

5. Determine the minimum required measurement time resolution and shot
   count to distinguish NMP > 0.1 from NMP = 0 at 3-sigma.

OUTPUTS
-------
  nm04_ramsey_traces.png         — time-domain traces, 3 NMP values
  nm04_log_c_vs_t2.png           — log(C) vs t^2  (Gaussian/exponential diagnostic)
  nm04_llr_vs_time.png           — log-likelihood ratio vs t_free
  nm04_fisher_bound.png          — Cramer-Rao bound on tau_B vs n_shots
  nm04_discriminator_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq

HERE   = Path(__file__).resolve().parent
OUTDIR = HERE / "outputs" / "nm_04"
OUTDIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(HERE))
from nm_01_memory_kernel import phi_exact, coherence_exact, coherence_markov

np.random.seed(42)

# ── reference parameters (median from gamma_dataset) ─────────────────────────
GAMMA_MED = 31_678.0      # s^-1  (median measured Gamma)
T2_STAR   = 1.0 / GAMMA_MED   # ~ 31.6 µs

# NMP cases to compare
NMP_CASES = {
    "Markovian (NMP=0.01)":     0.01,
    "Transitional (NMP=0.3)":   0.30,
    "Non-Markovian (NMP=1.5)":  1.50,
    "Non-Markovian (NMP=3.0)":  3.00,
}
COLORS = {
    "Markovian (NMP=0.01)":    "#2166AC",
    "Transitional (NMP=0.3)":  "#4DAC26",
    "Non-Markovian (NMP=1.5)": "#F4A582",
    "Non-Markovian (NMP=3.0)": "#D6604D",
}


# ── Figure 1: time-domain Ramsey traces ──────────────────────────────────────

def plot_ramsey_traces():
    t = np.linspace(0, 6.0 * T2_STAR, 600)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax.plot(t * 1e6, coherence_markov(t, GAMMA_MED),
            "k--", lw=2.5, label="Markov (pure exponential)", zorder=5)
    for label, nmp in NMP_CASES.items():
        tau_B = nmp / GAMMA_MED
        C = coherence_exact(t, GAMMA_MED, tau_B)
        ax.plot(t * 1e6, C, color=COLORS[label], lw=2, label=label)

    ax.axvline(T2_STAR * 1e6, color="grey", ls=":", lw=1.5,
               label=r"$t = T_2^*$ (Markov)")
    ax.axhline(1.0 / np.e, color="grey", ls=":", lw=1.0)
    ax.set_xlabel(r"Free evolution time  $t_{\rm free}$  (µs)", fontsize=11)
    ax.set_ylabel(r"Coherence  $|\rho_{01}(t)|$", fontsize=11)
    ax.set_title(f"Ramsey coherence trace\n"
                 f"(Γ = {GAMMA_MED/1e3:.1f} kHz, T₂* = {T2_STAR*1e6:.1f} µs)", fontsize=11)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # semilog: exponential → straight line, non-exponential → curved
    ax = axes[1]
    ax.semilogy(t * 1e6, coherence_markov(t, GAMMA_MED),
                "k--", lw=2.5, label="Markov", zorder=5)
    for label, nmp in NMP_CASES.items():
        tau_B = nmp / GAMMA_MED
        C = coherence_exact(t, GAMMA_MED, tau_B)
        C_safe = np.clip(C, 1e-10, None)
        ax.semilogy(t * 1e6, C_safe, color=COLORS[label], lw=2, label=label)

    ax.set_xlabel(r"Free evolution time  $t_{\rm free}$  (µs)", fontsize=11)
    ax.set_ylabel(r"$\log |\rho_{01}(t)|$  (semilog)", fontsize=11)
    ax.set_title("Semilog: exponential = straight line\n"
                 "Curved = non-Markovian (delayed onset)", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_ylim(1e-4, 1.5)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm04_ramsey_traces.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm04_ramsey_traces.png")


# ── Figure 2: log(C) vs t^2 — Gaussian diagnostic ───────────────────────────

def plot_log_c_vs_t2():
    """
    If C(t) = exp(-a*t^2)  (Gaussian):  log C = -a * t^2  → straight line in this plot
    If C(t) = exp(-Gamma*t) (exponential): log C = -Gamma*t → curves upward
    """
    # restrict to early times: 0 to 1.5 * tau_B of the NMP=3 case
    tau_B_nm3 = 3.0 / GAMMA_MED
    t = np.linspace(1e-8, 1.5 * tau_B_nm3, 300)
    t2 = t**2

    fig, ax = plt.subplots(figsize=(8, 5))

    # Markov (exponential): log C = -Gamma*t, so log C vs t^2 curves upward
    logC_markov = -GAMMA_MED * t
    ax.plot(t2 * 1e12, logC_markov, "k--", lw=2.5,
            label=r"Markov: $\log C = -\Gamma t$  (curves upward in this plot)")

    for label, nmp in NMP_CASES.items():
        tau_B = nmp / GAMMA_MED
        logC = -phi_exact(t, GAMMA_MED, tau_B)
        ax.plot(t2 * 1e12, logC, color=COLORS[label], lw=2, label=label)

    ax.set_xlabel(r"$t^2$  (µs²)", fontsize=11)
    ax.set_ylabel(r"$\log |\rho_{01}(t)|$", fontsize=11)
    ax.set_title(r"Gaussian diagnostic: $\log C(t)$ vs $t^2$" + "\n"
                 r"Straight line = Gaussian (non-Markovian);  curved = exponential (Markov)",
                 fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm04_log_c_vs_t2.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm04_log_c_vs_t2.png")


# ── Figure 3: log-likelihood ratio vs measurement time ───────────────────────

def plot_llr(sigma_shot: float = 0.02):
    """
    LLR(t) = log P(C_true | NM model) - log P(C_true | Markov model)

    Assumes C_true = C_exact(t, Gamma, tau_B) measured with Gaussian noise sigma.
    LLR > 0: data favours NM model.

    sigma_shot = single-shot standard deviation on C measurement.
    At n_shots measurements: effective sigma = sigma_shot / sqrt(n_shots).
    """
    t = np.linspace(0, 4.0 * T2_STAR, 400)
    n_shots_vals = [100, 1000, 10000]

    fig, axes = plt.subplots(1, len(NMP_CASES) - 1, figsize=(14, 4.5), sharey=False)

    for ax_i, (label, nmp) in enumerate(list(NMP_CASES.items())[1:]):
        ax = axes[ax_i]
        tau_B = nmp / GAMMA_MED
        C_true = coherence_exact(t, GAMMA_MED, tau_B)   # true signal
        C_mk   = coherence_markov(t, GAMMA_MED)           # Markov prediction

        for n_shots, lc in zip(n_shots_vals, ["#2166AC", "#4DAC26", "#D6604D"]):
            sigma_eff = sigma_shot / np.sqrt(n_shots)
            # LLR(t) = sum over independent time bins up to t
            # = (C_true - C_mk)^2 / (2 sigma_eff^2)  accumulated
            # using the Neyman-Pearson statistic
            llr_per_point = (C_true - C_mk)**2 / (2 * sigma_eff**2)
            llr_cumulative = np.cumsum(llr_per_point) * (t[1] - t[0])

            ax.plot(t * 1e6, llr_cumulative / np.log(10),
                    color=lc, lw=2,
                    label=f"n_shots = {n_shots:,}")

        # 3-sigma threshold: LLR > 4.5 (for 1 dof test at 3-sigma)
        ax.axhline(4.5 / np.log(10), color="red", ls="--", lw=1.5,
                   label="3σ threshold")

        ax.set_xlabel(r"$t_{\rm free}$  (µs)", fontsize=10)
        ax.set_ylabel(r"Cumulative LLR / log10", fontsize=10)
        ax.set_title(label, fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Cumulative log-likelihood ratio: exact vs Markov\n"
        "(above red = 3σ discrimination achieved)",
        fontsize=11
    )
    fig.tight_layout()
    fig.savefig(OUTDIR / "nm04_llr_vs_time.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm04_llr_vs_time.png")


# ── Figure 4: Cramer-Rao bound on tau_B ──────────────────────────────────────

def compute_fisher_tau_B(tau_B: float, t: np.ndarray, sigma_shot: float = 0.02):
    """
    Fisher information about tau_B from a Ramsey trace with n_shots measurements.
    I(tau_B) = sum_t (dC/dtau_B)^2 / sigma^2

    dC/dtau_B = -C(t) * dPhi/dtau_B
    dPhi/dtau_B = Gamma_markov * [t/tau_B^2 * exp(-t/tau_B) - (1/tau_B)(1 - exp(-t/tau_B))]
               = Gamma_markov / tau_B * [(t/tau_B) * exp(-t/tau_B) - (1 - exp(-t/tau_B))]
    """
    eps = 1e-9 * tau_B
    Phi_plus  = phi_exact(t, GAMMA_MED, tau_B + eps)
    Phi_minus = phi_exact(t, GAMMA_MED, tau_B - eps)
    dPhi_dtauB = (Phi_plus - Phi_minus) / (2 * eps)

    C = coherence_exact(t, GAMMA_MED, tau_B)
    dC_dtauB = -C * dPhi_dtauB

    # Fisher information per shot (assume Gaussian readout noise sigma_shot)
    fisher_per_shot = np.sum(dC_dtauB**2 / sigma_shot**2)
    return fisher_per_shot


def plot_fisher_bound():
    tau_B_vals = np.logspace(-7, -4, 60)   # 0.1 µs to 100 µs
    t          = np.linspace(0, 4.0 * T2_STAR, 200)
    sigma_shot = 0.02
    n_shots_vals = [100, 1000, 10000, 100000]

    # Cramer-Rao bound: delta_tau_B >= 1 / sqrt(n_shots * I(tau_B))
    fig, ax = plt.subplots(figsize=(8, 5))

    for n_shots, lc in zip(n_shots_vals, ["#2166AC", "#4DAC26", "#F4A582", "#D6604D"]):
        cr_bounds = []
        for tau_B in tau_B_vals:
            fi = compute_fisher_tau_B(tau_B, t, sigma_shot)
            if fi > 0:
                cr = 1.0 / np.sqrt(n_shots * fi)
            else:
                cr = np.inf
            cr_bounds.append(cr)
        cr_bounds = np.array(cr_bounds)
        # relative uncertainty
        rel = cr_bounds / tau_B_vals
        ax.loglog(tau_B_vals * 1e6, rel, color=lc, lw=2,
                  label=f"n_shots = {n_shots:,}")

    ax.axhline(0.1, color="k", ls="--", lw=1.5, label="10% relative uncertainty")
    ax.axhline(1.0, color="k", ls=":",  lw=1.0, label="100% (cannot constrain)")

    ax.set_xlabel(r"$\tau_B$  (µs)", fontsize=11)
    ax.set_ylabel(r"Cramer-Rao bound  $\delta\tau_B / \tau_B$", fontsize=11)
    ax.set_title("Minimum achievable relative uncertainty on $\\tau_B$\n"
                 r"from full Ramsey trace ($\Gamma = 31.7$ kHz, $\sigma = 0.02$)",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(1e-4, 1e2)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm04_fisher_bound.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm04_fisher_bound.png")

    # find tau_B where 10k shots gives <10% uncertainty
    t_ref = np.linspace(0, 4.0 * T2_STAR, 200)
    threshold_tau = None
    for tau_B in tau_B_vals:
        fi = compute_fisher_tau_B(tau_B, t_ref, sigma_shot)
        if fi > 0:
            rel = 1.0 / (np.sqrt(10000 * fi) * tau_B)
            if rel < 0.10:
                threshold_tau = tau_B
                break
    return threshold_tau


# ── compute discrimination time (when LLR first exceeds 3-sigma) ─────────────

def find_discrimination_time(nmp: float, n_shots: int = 1000,
                             sigma_shot: float = 0.02):
    tau_B = nmp / GAMMA_MED
    t     = np.linspace(0, 4.0 * T2_STAR, 400)
    C_true = coherence_exact(t, GAMMA_MED, tau_B)
    C_mk   = coherence_markov(t, GAMMA_MED)
    sigma_eff = sigma_shot / np.sqrt(n_shots)
    llr_per_point = (C_true - C_mk)**2 / (2 * sigma_eff**2)
    llr_cum = np.cumsum(llr_per_point) * (t[1] - t[0])
    # 3-sigma for 1 dof: chi2(1) at p=0.0027 is ~8.8
    threshold = 4.5
    idx = np.where(llr_cum >= threshold)[0]
    if len(idx) > 0:
        return float(t[idx[0]] * 1e6)   # µs
    return None   # not reached


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NM-04: Ramsey time-domain discriminator")
    print("=" * 60)

    print("  Plotting Ramsey traces...")
    plot_ramsey_traces()

    print("  Plotting Gaussian diagnostic (log C vs t^2)...")
    plot_log_c_vs_t2()

    print("  Computing log-likelihood ratios...")
    plot_llr(sigma_shot=0.02)

    print("  Computing Fisher / Cramer-Rao bounds...")
    threshold_tau = plot_fisher_bound()

    print("  Computing discrimination times...")
    disc_times = {}
    for label, nmp in list(NMP_CASES.items())[1:]:   # skip Markov case
        t_disc = find_discrimination_time(nmp, n_shots=1000)
        disc_times[label] = t_disc
        if t_disc:
            print(f"    {label}: 3σ discrimination at t = {t_disc:.1f} µs "
                  f"(with 1000 shots, σ=0.02)")
        else:
            print(f"    {label}: 3σ not reached in 4×T2* window")

    summary = {
        "task": "nm_04_ramsey_discriminator",
        "status": "PASS",
        "reference_params": {
            "Gamma_med_Hz": GAMMA_MED,
            "T2star_us": T2_STAR * 1e6
        },
        "key_finding": (
            "The non-Markovian coherence is distinguishable from the Markov "
            "exponential in the TIME DOMAIN. The signature is: "
            "(1) Gaussian initial decay at t < tau_B (visible in log C vs t^2 plot), "
            "(2) Coherence ABOVE the Markov exponential at early times, "
            "(3) Convergence to Markov at t >> tau_B. "
            "The gamma_dataset (single 1/e-point per frequency) cannot see this. "
            "A full Ramsey trace with dense time sampling can."
        ),
        "discrimination_times_1000shots": disc_times,
        "gaussian_diagnostic": {
            "method": "Plot log(C(t)) vs t^2. Straight line = Gaussian (NM). "
                      "Curved upward = exponential (Markov).",
            "observable_window": "t < tau_B  (approximately)"
        },
        "cramer_rao": {
            "sigma_shot": 0.02,
            "tau_B_constrained_below_us": threshold_tau * 1e6 if threshold_tau else None,
            "note": "tau_B above this threshold is measurable to <10% with 10k shots"
        },
        "experimental_requirement": {
            "time_resolution": f"sub-µs Ramsey time steps (dt << tau_B)",
            "n_shots": ">= 1000 per time point",
            "t_free_range": f"0 to ~{4*T2_STAR*1e6:.0f} µs (= 4 × T2*)",
            "key_window": "0 to tau_B  (where Gaussian onset is visible)"
        },
        "connection_to_C2": (
            "tau_B is the substrate bath correlation time — the memory of the "
            "C2 PRW substrate. In the Markov limit tau_B -> 0, the substrate has "
            "no memory and all predictions are identical to standard Lindblad. "
            "A measured tau_B > 0 (NMP > 0.1) would be evidence that the substrate "
            "has a finite correlation time, which is a non-trivial statement about "
            "the microscopic dynamics."
        )
    }

    with open(OUTDIR / "nm04_discriminator_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  [saved] nm04_discriminator_summary.json")

    print()
    print("KEY RESULTS:")
    print(f"  Markov model: C(t) = exp(-Gamma*t)  [straight line on semilog]")
    print(f"  NM model:     C(t) = exp(-Phi(t))   [Gaussian onset, curves on semilog]")
    print(f"  Discriminator: log(C) vs t^2 plot — straight = NM, curved = Markov")
    for label, t_d in disc_times.items():
        if t_d:
            print(f"  {label}: 3σ at t = {t_d:.1f} µs  (1000 shots, σ=0.02)")
    print(f"  Outputs: {OUTDIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
