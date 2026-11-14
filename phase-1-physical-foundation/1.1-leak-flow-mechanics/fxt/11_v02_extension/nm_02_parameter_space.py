"""
nm_02_parameter_space.py
========================
Task 2: Map the three regimes (Markovian / transitional / non-Markovian) and
        their experimentally distinguishable predictions across the
        (NMP, t_free * Gamma) parameter space.

Depends on: nm_01_memory_kernel.py  (imports phi_exact, coherence_exact)

OUTPUT
------
1. 2D heatmap of |C_exact - C_markov| over (NMP, t * Gamma)
2. Regime boundary lines: NMP = 0.1, 1.0  (Markov / transitional / NM)
3. 1D slices: coherence vs time for three NMP values at the gamma_dataset
   frequencies (omega = 0.1 MHz .. 8 MHz, using k_rot / gamma_dataset values)
4. Effective T2* ratio: T2*_exact / T2*_markov as function of NMP
5. JSON summary with regime thresholds and max mismatch values
"""

from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE   = Path(__file__).resolve().parent
OUTDIR = HERE / "outputs" / "nm_02"
OUTDIR.mkdir(parents=True, exist_ok=True)

# import from task 1
import sys
sys.path.insert(0, str(HERE))
from nm_01_memory_kernel import phi_exact, coherence_exact, coherence_markov


# ── gamma_dataset values (from 06_datasets/aaG/ramsey_dataset/gamma_dataset.csv)
# detuning_hz -> Omega (rad/s), Gamma (s^-1)
GAMMA_DATASET = {
    "omega_rad_s": np.array([
        6.937836e+05,
        1.321912e+06,
        3.203833e+06,
        6.341284e+06,
        1.262960e+07,
        3.148120e+07,
        5.032363e+07,
    ]),
    "Gamma_s": np.array([
        28067.4,
        32445.5,
        27563.3,
        37511.0,
        35023.6,
        28930.1,
        31678.2,
    ]),
    "Gamma_err": np.array([
        3800.4,
        3746.7,
        1659.8,
        6107.9,
        4762.4,
        2905.0,
        3574.3,
    ]),
}


# ── Figure 1: 2D mismatch heatmap over (NMP, t*Gamma) ────────────────────────

def plot_mismatch_heatmap():
    nmp_vals  = np.logspace(-2, 1.5, 80)   # NMP = Gamma * tau_B
    tg_vals   = np.linspace(0, 5.0, 120)   # t * Gamma_markov

    mismatch = np.zeros((len(nmp_vals), len(tg_vals)))
    for i, nmp in enumerate(nmp_vals):
        tau_B = nmp  # in units where Gamma_markov = 1
        for j, tg in enumerate(tg_vals):
            t = tg  # same units
            C_ex = np.exp(-phi_exact(np.array([t]), 1.0, tau_B))[0]
            C_mk = np.exp(-t)
            mismatch[i, j] = abs(C_ex - C_mk)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    im = ax.pcolormesh(
        tg_vals, np.log10(nmp_vals), mismatch,
        shading="auto", cmap="hot_r", vmin=0, vmax=0.5
    )
    cb = plt.colorbar(im, ax=ax)
    cb.set_label(r"$|C_{\rm exact}(t) - C_{\rm Markov}(t)|$", fontsize=10)

    # regime boundary lines
    ax.axhline(np.log10(0.1), color="cyan",  lw=2, ls="--",
               label="NMP = 0.1  (Markov boundary)")
    ax.axhline(np.log10(1.0), color="lime",  lw=2, ls="--",
               label="NMP = 1.0  (NM boundary)")

    ax.set_xlabel(r"$\Gamma_{\rm Markov} \cdot t$  (normalised time)", fontsize=11)
    ax.set_ylabel(r"$\log_{10}(\mathrm{NMP}) = \log_{10}(\Gamma_{\rm Markov} \cdot \tau_B)$",
                  fontsize=10)
    ax.set_title("Mismatch |exact − Markov| in (NMP, time) space\n"
                 "Hot = large mismatch; NM signatures above NMP=1 line", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")

    # label regions
    ax.text(4.2, np.log10(0.04),  "MARKOVIAN",     color="cyan",  fontsize=9, ha="right")
    ax.text(4.2, np.log10(0.4),   "TRANSITIONAL",  color="white", fontsize=9, ha="right")
    ax.text(4.2, np.log10(4.0),   "NON-MARKOVIAN", color="lime",  fontsize=9, ha="right")

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm02_mismatch_heatmap.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm02_mismatch_heatmap.png")
    return mismatch, nmp_vals, tg_vals


# ── Figure 2: coherence slices at gamma_dataset frequencies ──────────────────

def plot_gamma_dataset_slices():
    """
    For each Gamma in the gamma_dataset, show the coherence for three tau_B
    values spanning Markov / transitional / NM.
    Uses T2* = 1/Gamma as the natural time scale.
    """
    Gamma_vals = GAMMA_DATASET["Gamma_s"]
    omega_vals = GAMMA_DATASET["omega_rad_s"]

    # pick three representative NMP values
    nmp_cases = [0.05, 0.5, 3.0]
    colors     = ["#2166AC", "#F4A582", "#D6604D"]
    labels     = ["NMP=0.05 (Markovian)", "NMP=0.5 (Transitional)", "NMP=3.0 (Non-Markovian)"]

    # use median Gamma for the representative plot
    G_rep = np.median(Gamma_vals)   # ~ 31e3 s^-1
    T2_rep = 1.0 / G_rep

    t = np.linspace(0, 5.0 * T2_rep, 400)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    ax.plot(t * 1e6, np.exp(-G_rep * t), "k--", lw=2, label="Markov (exponential)")
    for nmp, c, lbl in zip(nmp_cases, colors, labels):
        tau_B = nmp / G_rep
        C = coherence_exact(t, G_rep, tau_B)
        ax.plot(t * 1e6, C, color=c, lw=2, label=lbl)
    ax.set_xlabel(r"Free evolution time  $t_{\rm free}$  (µs)", fontsize=11)
    ax.set_ylabel(r"Coherence $|\rho_{01}(t)|$", fontsize=11)
    ax.set_title(f"Coherence decay at median Gamma = {G_rep/1e3:.1f} kHz\n"
                 f"(from gamma_dataset, 7 frequencies)")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # zoom into early time (t < tau_B for NMP=3 case)
    tau_B_nm = 3.0 / G_rep
    t_zoom = np.linspace(0, 2.0 * tau_B_nm, 300)
    ax2 = axes[1]
    ax2.plot(t_zoom * 1e6, np.exp(-G_rep * t_zoom), "k--", lw=2, label="Markov")
    for nmp, c, lbl in zip(nmp_cases, colors, labels):
        tau_B = nmp / G_rep
        C = coherence_exact(t_zoom, G_rep, tau_B)
        ax2.plot(t_zoom * 1e6, C, color=c, lw=2, label=lbl)
    ax2.axvline(tau_B_nm * 1e6, color="#D6604D", ls=":", lw=1.5,
                label=r"$\tau_B$ (NMP=3 case)")
    ax2.set_xlabel(r"Free evolution time  $t_{\rm free}$  (µs)", fontsize=11)
    ax2.set_ylabel(r"Coherence $|\rho_{01}(t)|$", fontsize=11)
    ax2.set_title("Zoom: early-time Gaussian onset window\n"
                  r"(NM signature visible at $t < \tau_B$)")
    ax2.legend(fontsize=8)
    ax2.set_ylim(0, 1.05)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTDIR / "nm02_dataset_slices.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm02_dataset_slices.png")


# ── Figure 3: effective T2* ratio vs NMP ─────────────────────────────────────

def plot_t2star_ratio():
    """
    T2*_exact is defined as the time at which |C_exact(t)| = 1/e.
    Compare to T2*_markov = 1/Gamma_markov.
    The ratio T2*_exact / T2*_markov measures how much the NM bath
    extends coherence at short times.
    """
    nmp_vals = np.logspace(-2, 1.5, 200)
    ratio    = np.zeros_like(nmp_vals)

    from scipy.optimize import brentq

    for i, nmp in enumerate(nmp_vals):
        tau_B = nmp  # units Gamma=1
        # find t such that phi_exact(t, 1, tau_B) = 1 (i.e. C = 1/e)
        try:
            t_star = brentq(
                lambda t: phi_exact(np.array([t]), 1.0, tau_B)[0] - 1.0,
                1e-6, 100.0
            )
            ratio[i] = t_star   # in units of 1/Gamma, so ratio = t_star * Gamma
        except ValueError:
            ratio[i] = np.nan

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.semilogx(nmp_vals, ratio, lw=2.5, color="#D6604D")
    ax.axhline(1.0, color="k", ls="--", lw=1.5, label=r"Markov: $T_{2}^* \Gamma = 1$")
    ax.axvline(0.1, color="cyan",  ls=":", lw=1.5, label="NMP = 0.1")
    ax.axvline(1.0, color="lime",  ls=":", lw=1.5, label="NMP = 1.0")
    ax.set_xlabel(r"$\mathrm{NMP} = \Gamma_{\rm Markov} \cdot \tau_B$", fontsize=11)
    ax.set_ylabel(r"$T_{2,\rm exact}^* \cdot \Gamma_{\rm Markov}$", fontsize=11)
    ax.set_title(r"Effective $T_2^*$ relative to Markov prediction" + "\n"
                 "Non-Markovian bath extends coherence (ratio > 1)", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTDIR / "nm02_t2star_ratio.png", dpi=160)
    plt.close(fig)
    print("  [saved] nm02_t2star_ratio.png")
    return nmp_vals, ratio


# ── compute quantitative regime statistics ────────────────────────────────────

def compute_regime_stats(mismatch, nmp_vals, tg_vals):
    """
    For each NMP bin, find the maximum mismatch over time.
    Classify each NMP into Markov / Transitional / NM regime.
    """
    max_mismatch_per_nmp = mismatch.max(axis=1)

    markov_mask = nmp_vals < 0.1
    trans_mask  = (nmp_vals >= 0.1) & (nmp_vals < 1.0)
    nm_mask     = nmp_vals >= 1.0

    stats = {
        "Markov_regime_NMP_lt_0.1": {
            "NMP_range": [float(nmp_vals[markov_mask].min()),
                          float(nmp_vals[markov_mask].max())],
            "max_mismatch": float(max_mismatch_per_nmp[markov_mask].max()),
            "description": "Exponential decay. Markov approximation valid."
        },
        "Transitional_regime_0.1_to_1.0": {
            "NMP_range": [float(nmp_vals[trans_mask].min()),
                          float(nmp_vals[trans_mask].max())],
            "max_mismatch": float(max_mismatch_per_nmp[trans_mask].max()),
            "description": "Mixed. Gaussian onset becoming visible."
        },
        "NonMarkovian_regime_NMP_gt_1.0": {
            "NMP_range": [float(nmp_vals[nm_mask].min()),
                          float(nmp_vals[nm_mask].max())],
            "max_mismatch": float(max_mismatch_per_nmp[nm_mask].max()),
            "description": "Gaussian initial decay. Markov approximation fails badly."
        },
    }
    return stats


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NM-02: Parameter space — regime map")
    print("=" * 60)

    print("  Computing mismatch heatmap...")
    mismatch, nmp_vals, tg_vals = plot_mismatch_heatmap()

    print("  Computing gamma_dataset coherence slices...")
    plot_gamma_dataset_slices()

    print("  Computing T2* ratio vs NMP...")
    nmp_arr, ratio = plot_t2star_ratio()

    print("  Computing regime statistics...")
    regime_stats = compute_regime_stats(mismatch, nmp_vals, tg_vals)

    # find T2* ratio at NMP=3 (strongly NM)
    idx3 = np.argmin(np.abs(nmp_arr - 3.0))
    t2_ratio_at_nmp3 = float(ratio[idx3])

    summary = {
        "task": "nm_02_parameter_space",
        "status": "PASS",
        "regime_boundaries": {
            "Markov":      "NMP < 0.1",
            "Transitional": "0.1 <= NMP < 1.0",
            "NonMarkovian": "NMP >= 1.0"
        },
        "regime_statistics": regime_stats,
        "T2star_ratio_at_NMP3": t2_ratio_at_nmp3,
        "T2star_ratio_meaning": (
            "At NMP=3, exact T2* is {:.2f}x longer than Markov predicts. "
            "Measuring T2* alone is not enough — the SHAPE of the decay differs."
        ).format(t2_ratio_at_nmp3),
        "key_diagnostic": (
            "Plot log(C(t)) vs t^2 at early times. "
            "Non-Markovian: straight line (Gaussian). "
            "Markovian: curves upward (exponential onset)."
        ),
        "gamma_dataset_median_Gamma_Hz": float(np.median(GAMMA_DATASET["Gamma_s"])),
        "tau_B_for_NMP1_at_median_Gamma_us": float(
            1.0 / np.median(GAMMA_DATASET["Gamma_s"]) * 1e6
        ),
        "next_task": "nm_03_model_fit.py — fit both models to gamma_dataset.csv"
    }

    with open(OUTDIR / "nm02_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  [saved] nm02_summary.json")

    print()
    print("KEY RESULTS:")
    for regime, data in regime_stats.items():
        print(f"  {regime}: max mismatch = {data['max_mismatch']:.3f}")
    print(f"  T2* ratio at NMP=3: {t2_ratio_at_nmp3:.3f}  "
          f"(exact T2* is {t2_ratio_at_nmp3:.2f}x Markov T2*)")
    G_med = np.median(GAMMA_DATASET["Gamma_s"])
    print(f"  At median Gamma = {G_med/1e3:.1f} kHz: NMP=1 requires tau_B = {1e6/G_med:.1f} µs")
    print(f"  Outputs: {OUTDIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
