#!/usr/bin/env python3
"""Coupling sweep for dwarf galaxy rotation curve.

This script keeps the dwarf galaxy configuration fixed (M* = 1e8 Msun, R_eff = 1 kpc)
and sweeps an effective coupling parameter k_eff that maps the substrate field
radial gradient into a circular velocity:

    v_sub^2(r; k_eff) = k_eff * r * dPhi_dr(r),  with  Phi ~ s(r)

For each k_eff it:
  * runs the dwarf-like substrate simulation once,
  * computes a radial profile s(r) and dPhi_dr(r),
  * computes v_sub(r; k_eff), v_newt(r), and ratio(r) = v_sub / v_newt,
  * saves an NPZ per k_eff, and
  * records summary metrics in a JSON file.

Two diagnostic plots are also generated:
  * ratio vs radius for a few representative k_eff values,
  * ratio at 2 kpc as a function of k_eff.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import matplotlib

# Non-interactive backend
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants as const
from scipy.ndimage import gaussian_filter1d

# --- Repo paths / imports ----------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "verification" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from new_num_solv import SubstrateXSolver  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results" / "dwarf_coupling_sweep"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ENABLE_LIVE_PLOTS = os.getenv("SECOND_BASE_LIVE", "0") == "1"

# Chosen effective coupling band for dwarf galaxies
K_EFF_LOW = 3.0e-2       # Lower bound: gentle boost in outer regions
K_EFF_FIDUCIAL = 1.0e-1  # Fiducial: v_total ~ 1.5–2× v_newt in outer dwarf
K_EFF_HIGH = 3.0e-1      # Upper bound: strong but still plausible boost


# --- Helper functions --------------------------------------------------------

def run_dwarf_sim(m_star_msun: float = 1e8, r_eff_kpc: float = 1.0) -> Dict[str, np.ndarray]:
    """Run a single dwarf-galaxy-like substrate simulation and return field + radii.

    This is intentionally simpler than the heavy dwarf test in run_second_base_suite.
    We use more conservative solver parameters and do *not* bake in any k_eff here;
    k_eff is applied purely in post-processing.
    """

    # Galaxy scale and grid
    grid_size = 256
    domain_size_m = 5.0e20  # ~16 kpc; covers r=0.1..5 kpc nicely

    # Use the galaxy scenario's tau/tau_irr but modest couplings
    from run_second_base_suite import SCENARIO_PARAMS  # local import to avoid cycles

    cfg = SCENARIO_PARAMS["galaxy"]

    solver = SubstrateXSolver(
        grid_size=grid_size,
        domain_size=domain_size_m,
        tau=cfg["tau"],
        tau_irr=cfg["tau_irr"],
        alpha=5e-11,
        beta=5e-11,
        gamma=5e-11,
        chi=1e6,
        k_E=cfg["k_E"],
        k_E_adv=cfg["k_E_adv"],
        k_F=cfg["k_F"],
        k_vsub=cfg["k_vsub"],
        k_u=cfg["k_u"],
    )

    # Add stellar mass as a central point mass
    solver.add_point_mass(m_star_msun * solver.M_sun, (0.0, 0.0))

    # Run for a moderate number of steps to let the substrate respond
    solver.simulate(
        n_steps=600,
        plot_interval=10_000,
        enable_plots=ENABLE_LIVE_PLOTS,
        analyze=False,
    )

    # Build radius array matching solver grid
    x = np.linspace(-solver.domain_size / 2, solver.domain_size / 2, solver.grid_size)
    y = np.linspace(-solver.domain_size / 2, solver.domain_size / 2, solver.grid_size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X ** 2 + Y ** 2)

    return {"s": solver.s.copy(), "R": R, "M_star": m_star_msun, "domain_size": solver.domain_size}


def radial_profile(field: np.ndarray, radii: np.ndarray, n_bins: int = 200) -> Dict[str, np.ndarray]:
    """Compute a simple radial profile <field>(r) with linear bins."""
    flat_r = radii.ravel()
    flat_f = field.ravel()

    r_max = flat_r.max()
    bin_edges = np.linspace(0.0, r_max, n_bins + 1)
    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

    profile = np.zeros(n_bins)
    counts = np.zeros(n_bins)
    idxs = np.digitize(flat_r, bin_edges) - 1
    for idx, val in zip(idxs, flat_f):
        if 0 <= idx < n_bins:
            profile[idx] += val
            counts[idx] += 1

    counts[counts == 0] = 1.0
    profile /= counts

    # Light smoothing
    profile_smooth = gaussian_filter1d(profile, sigma=2)

    return {"r": bin_centers, "profile": profile_smooth}


def compute_velocities_from_profile(
    r_bins: np.ndarray,
    s_profile: np.ndarray,
    m_star_msun: float,
    k_eff: float,
) -> Dict[str, np.ndarray]:
    """Given s(r) and k_eff, compute v_newt, v_sub, and ratio on 0.1–5 kpc grid."""

    # Derivative of potential proxy Phi ~ s
    dPhi_dr = np.gradient(s_profile, r_bins)

    # Radial grid for output (0.1–5 kpc)
    r_kpc = np.linspace(0.1, 5.0, 500)
    r_m = r_kpc * 3.086e19

    # Interpolate dPhi/dr to this grid
    from scipy.interpolate import interp1d

    interp_dphi = interp1d(
        r_bins,
        dPhi_dr,
        kind="cubic",
        bounds_error=False,
        fill_value=(dPhi_dr[0], dPhi_dr[-1]),
    )

    dphi_out = interp_dphi(r_m)

    # Newtonian circular velocity (stars only)
    M_SUN = 1.98847e30  # kg
    v_newt = np.sqrt(const.G * m_star_msun * M_SUN / np.maximum(r_m, 1e3))

    # Substrate-induced velocity: v_sub^2 = k_eff * r * dPhi/dr
    v2_sub = k_eff * r_m * dphi_out
    v2_sub = np.maximum(np.abs(v2_sub), 0.0)
    v_sub = np.sqrt(v2_sub)

    ratio = np.zeros_like(r_m)
    mask = v_newt > 0
    ratio[mask] = v_sub[mask] / v_newt[mask]

    return {"r_kpc": r_kpc, "v_newt": v_newt, "v_sub": v_sub, "ratio": ratio}


# --- Main sweep --------------------------------------------------------------

def run_coupling_sweep() -> None:
    # Fixed dwarf parameters
    m_star = 1e8  # Msun
    r_eff = 1.0   # kpc (recorded for metadata only)

    # Effective coupling values to explore (user-targeted list)
    # Focus on regime where v_sub is ~1.5–3× v_newt in outer dwarf galaxies.
    # Includes the designated low/fiducial/high values plus bracketing points.
    k_values = np.array([
        1.0e-3,
        3.0e-3,
        1.0e-2,
        K_EFF_LOW,
        K_EFF_FIDUCIAL,
        K_EFF_HIGH,
        1.0e0,
    ])

    summary: List[Dict] = []

    for k_eff in k_values:
        print(f"Running dwarf simulation for k_eff = {k_eff:.2e} ...")

        sim = run_dwarf_sim(m_star_msun=m_star, r_eff_kpc=r_eff)
        prof = radial_profile(sim["s"], sim["R"], n_bins=240)

        vel = compute_velocities_from_profile(
            r_bins=prof["r"],
            s_profile=prof["profile"],
            m_star_msun=m_star,
            k_eff=k_eff,
        )

        # Save per-k_eff NPZ
        tag = f"{k_eff:.1e}".replace("+", "").replace("-", "m")
        npz_path = RESULTS_DIR / f"dwarf_coupling_k_{tag}.npz"
        np.savez(
            npz_path,
            r_kpc=vel["r_kpc"],
            v_sub=vel["v_sub"],
            v_newt=vel["v_newt"],
            ratio=vel["ratio"],
            k_eff=k_eff,
            m_star=m_star,
            r_eff=r_eff,
        )

        # Compute summary metrics
        r = vel["r_kpc"]
        ratio = vel["ratio"]
        v_sub = vel["v_sub"]
        v_newt = vel["v_newt"]

        def interp_at(target_kpc: float) -> float:
            from numpy import interp

            return float(interp(target_kpc, r, ratio))

        outer_mask = r >= 4.0
        outer_mean = float(ratio[outer_mask].mean()) if np.any(outer_mask) else float("nan")

        # Label this k_eff relative to the chosen dwarf band
        if np.isclose(k_eff, K_EFF_FIDUCIAL):
            role = "fiducial"
        elif np.isclose(k_eff, K_EFF_LOW):
            role = "low"
        elif np.isclose(k_eff, K_EFF_HIGH):
            role = "high"
        else:
            role = "scan"

        entry = {
            "k_eff": float(k_eff),
            "role": role,
            "max_ratio": float(ratio.max()),
            "max_v_sub_kms": float(v_sub.max() / 1e3),
            "max_v_newt_kms": float(v_newt.max() / 1e3),
            "ratio_1kpc": interp_at(1.0),
            "ratio_2kpc": interp_at(2.0),
            "ratio_5kpc": interp_at(5.0),
            "outer_mean_ratio_r>=4kpc": outer_mean,
            "npz_file": str(npz_path.relative_to(REPO_ROOT)),
        }
        summary.append(entry)

    # Save summary JSON
    summary_path = RESULTS_DIR / "coupling_sweep_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Saved coupling sweep summary to {summary_path}")

    # Generate verification plots
    make_verification_plots(summary)


def make_verification_plots(summary: List[Dict]) -> None:
    # Plot ratio vs radius for three representative k_eff values
    if not summary:
        return

    # Sort summary by k_eff
    summary_sorted = sorted(summary, key=lambda e: e["k_eff"])
    ks = [e["k_eff"] for e in summary_sorted]

    # Pick min, mid, and max k_eff
    pick_idxs = [0, len(ks) // 2, len(ks) - 1]

    plt.figure(figsize=(8, 5))
    for idx in pick_idxs:
        entry = summary_sorted[idx]
        npz_full = REPO_ROOT / entry["npz_file"]
        data = np.load(npz_full)
        r_kpc = data["r_kpc"]
        ratio = data["ratio"]
        plt.plot(r_kpc, ratio, label=f"k_eff={entry['k_eff']:.1e}")

    plt.xlabel("Radius (kpc)")
    plt.ylabel("v_sub / v_newt")
    plt.title("Dwarf galaxy: velocity ratio vs radius for selected k_eff")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "ratio_vs_radius_selected_k.png", dpi=150)
    plt.close()

    # Plot ratio at 2 kpc vs k_eff
    ks_plot = []
    ratio_2 = []
    for entry in summary_sorted:
        ks_plot.append(entry["k_eff"])
        ratio_2.append(entry["ratio_2kpc"])

    plt.figure(figsize=(7, 5))
    plt.loglog(ks_plot, ratio_2, marker="o")
    plt.xlabel("k_eff")
    plt.ylabel("v_sub / v_newt at 2 kpc")
    plt.title("Coupling sweep: ratio at 2 kpc vs k_eff")
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "ratio_at_2kpc_vs_k.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    run_coupling_sweep()
