#!/usr/bin/env python3
"""Single-run galaxy-scale substrate simulation.

Given stellar mass M_star (Msun), effective radius R_eff (kpc) and an effective
coupling k_eff, this script:
  • runs a substrate simulation on a 2-D grid sized to cover ∼6 R_eff,
  • builds a radial profile of the substrate field s(r),
  • converts that to substrate circular velocity using v_sub^2 = k_eff r dΦ/dr,
  • compares with Newtonian stellar velocity v_newt,
  • saves NPZ of r, v_sub, v_newt, and v_total, plus a JSON summary, and
  • makes a quick rotation-curve plot.

Usage (Milky Way fiducial example):

    python galaxy_scale_sim.py --m-star 1e11 \
                               --r-eff 4 \
                               --k-eff 0.1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants as const
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

# Repo import path ------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "verification" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from new_num_solv import SubstrateXSolver  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results" / "galaxy_scale"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

M_SUN = 1.98847e30  # SI kg

# -----------------------------------------------------------------------------

def run_galaxy_sim(m_star_msun: float, r_eff_kpc: float, k_eff: float, smoothing_sigma: int = 2, tag: str = "MW") -> Dict:
    """Run substrate simulation and return computed curves + paths."""

    # Choose domain to cover ~6× effective radius
    r_max_kpc = 20.0  # we'll sample out to 20 kpc regardless
    domain_size_m = r_max_kpc * 3.086e19 * 2  # full diameter

    grid_size = 512

    solver = SubstrateXSolver(
        grid_size=grid_size,
        domain_size=domain_size_m,
        tau=1.6e6,      # Milky-Way-like dampings (from galaxy scenario)
        tau_irr=2.5e6,
        alpha=5e-11,
        beta=5e-11,
        gamma=5e-11,
        chi=1e6,
        k_E=1e-4,
        k_E_adv=1e-5,
        k_F=1e-5,
        k_vsub=1e-5,
        k_u=1e-5,
    )

    solver.add_point_mass(m_star_msun * M_SUN, (0.0, 0.0))

    solver.simulate(n_steps=800, plot_interval=10_000, enable_plots=False, analyze=False)

    # Build radial coordinates
    x = np.linspace(-solver.domain_size/2, solver.domain_size/2, solver.grid_size)
    y = x.copy()
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    # Radial profile of substrate field (smoothed)
    n_bins = 300
    flat_r = R.ravel()
    flat_s = solver.s.ravel()
    bin_edges = np.linspace(0.0, flat_r.max(), n_bins+1)
    bin_centers = 0.5*(bin_edges[1:]+bin_edges[:-1])
    sums = np.zeros(n_bins)
    counts = np.zeros(n_bins)
    idxs = np.digitize(flat_r, bin_edges) - 1
    for idx,val in zip(idxs, flat_s):
        if 0<=idx<n_bins:
            sums[idx]+=val
            counts[idx]+=1
    counts[counts==0]=1.0
    profile = sums/counts
    # Heavier smoothing to suppress grid-scale ripples
    profile = gaussian_filter1d(profile, sigma=smoothing_sigma)

    # Derivative and velocities
    dphi_dr = np.gradient(profile, bin_centers)
    r_kpc = np.linspace(0.5, r_max_kpc, 500)
    r_m = r_kpc*3.086e19
    dphi_interp = interp1d(bin_centers, dphi_dr, kind="cubic", bounds_error=False, fill_value="extrapolate")
    dphi_out = dphi_interp(r_m)

    v2_sub = k_eff * r_m * dphi_out
    v_sub = np.sqrt(np.maximum(np.abs(v2_sub),0))
    v_newt = np.sqrt(const.G * m_star_msun * M_SUN / np.maximum(r_m,1e3))
    v_total = np.sqrt(v_sub**2 + v_newt**2)
    ratio = v_sub/np.maximum(v_newt,1e-12)

    # Save NPZ
    tag_full = f"{tag}_k_{k_eff:.2e}".replace("+","")
    npz_path = RESULTS_DIR / f"galaxy_{tag_full}.npz"
    np.savez(npz_path, r_kpc=r_kpc,v_sub=v_sub,v_newt=v_newt,v_total=v_total,ratio=ratio,
             k_eff=k_eff,m_star=m_star_msun,r_eff=r_eff_kpc)

    # Plot rotation curve
    plt.figure(figsize=(8,5))
    plt.plot(r_kpc, v_newt/1e3,'--',label='Newtonian (stars)')
    plt.plot(r_kpc, v_total/1e3,label='Total (substrate+stars)')
    plt.xlabel('Radius (kpc)')
    plt.ylabel('Circular velocity (km/s)')
    plt.title(f'Milky Way rotation, k_eff={k_eff}')
    plt.grid(True,alpha=0.3)
    plt.legend()
    plot_path = RESULTS_DIR / f"galaxy_rotation_{tag_full}.png"
    plt.tight_layout(); plt.savefig(plot_path,dpi=150); plt.close()

    # Summary metrics
    outer_mask = r_kpc>=8
    summary = {
        "smoothing_sigma": smoothing_sigma,
        "k_eff": k_eff,
        "v_total_8_15kpc_mean_kms": float(v_total[outer_mask].mean()/1e3),
        "v_newt_8_15kpc_mean_kms": float(v_newt[outer_mask].mean()/1e3),
        "ratio_outer_mean": float(ratio[outer_mask].mean()),
        "max_v_total_kms": float(v_total.max()/1e3),
        "npz_file": str(npz_path.relative_to(REPO_ROOT)),
        "plot_file": str(plot_path.relative_to(REPO_ROOT)),
    }
    json_path = RESULTS_DIR / f"galaxy_summary_{tag_full}.json"
    json_path.write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Galaxy-scale substrate simulation")
    parser.add_argument("--m-star", type=float, default=1e11, help="Stellar mass in Msun (default 1e11)")
    parser.add_argument("--r-eff", type=float, default=4.0, help="Effective radius in kpc (default 4 kpc)")
    parser.add_argument("--k-eff", type=float, default=0.1, help="Effective coupling k_eff (default 0.1)")
    parser.add_argument("--sigma", type=int, default=2, help="Gaussian smoothing sigma (default 2)")
    parser.add_argument("--tag", type=str, default="MW", help="Short tag for output filenames (default MW)")
    args = parser.parse_args()

    summary = run_galaxy_sim(args.m_star, args.r_eff, args.k_eff, smoothing_sigma=args.sigma, tag=args.tag)
    print("\nSimulation complete. Key numbers:")
    for k,v in summary.items():
        print(f"{k}: {v}")
