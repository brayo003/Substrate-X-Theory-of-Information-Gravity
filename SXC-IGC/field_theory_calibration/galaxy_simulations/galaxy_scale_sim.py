#!/usr/bin/env python3
"""Public-ready galaxy-scale simulation placeholder."""

import argparse
import json
from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Results directory inside repo
RESULTS_DIR = Path(__file__).resolve().parent / "results" / "galaxy_scale"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_galaxy_sim(m_star_msun: float, r_eff_kpc: float, k_eff: float, smoothing_sigma: int = 2, tag: str = "MW") -> Dict:
    """Generate placeholder galaxy rotation data for demonstration."""
    r_kpc = np.linspace(0.5, 20, 500)
    
    # Dummy "substrate" field replaced by smooth random variation
    np.random.seed(0)
    v_sub = 50 + 10*np.sin(r_kpc/2) + np.random.normal(0, 2, len(r_kpc))
    
    # Newtonian circular velocity
    v_newt = np.sqrt(4.302e-6 * m_star_msun / np.maximum(r_kpc, 0.1)) * 1e3  # km/s
    
    v_total = np.sqrt(v_sub**2 + v_newt**2)
    ratio = v_sub / np.maximum(v_newt, 1e-12)
    
    # Save NPZ
    tag_full = f"{tag}_k_{k_eff:.2e}".replace("+","")
    npz_path = RESULTS_DIR / f"galaxy_{tag_full}.npz"
    np.savez(npz_path, r_kpc=r_kpc, v_sub=v_sub, v_newt=v_newt, v_total=v_total, ratio=ratio,
             k_eff=k_eff, m_star=m_star_msun, r_eff=r_eff_kpc)
    
    # Plot rotation curve
    plt.figure(figsize=(8,5))
    plt.plot(r_kpc, v_newt, '--', label='Newtonian (stars)')
    plt.plot(r_kpc, v_total, label='Total (substrate+stars)')
    plt.xlabel('Radius (kpc)')
    plt.ylabel('Circular velocity (km/s)')
    plt.title(f'Galaxy rotation placeholder, k_eff={k_eff}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plot_path = RESULTS_DIR / f"galaxy_rotation_{tag_full}.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    # JSON summary
    summary = {
        "k_eff": k_eff,
        "v_total_mean_kms": float(v_total.mean()),
        "v_newt_mean_kms": float(v_newt.mean()),
        "ratio_mean": float(ratio.mean()),
        "npz_file": str(npz_path.relative_to(RESULTS_DIR.parent.parent)),
        "plot_file": str(plot_path.relative_to(RESULTS_DIR.parent.parent)),
    }
    json_path = RESULTS_DIR / f"galaxy_summary_{tag_full}.json"
    json_path.write_text(json.dumps(summary, indent=2))
    
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Galaxy-scale simulation placeholder")
    parser.add_argument("--m-star", type=float, default=1e11)
    parser.add_argument("--r-eff", type=float, default=4.0)
    parser.add_argument("--k-eff", type=float, default=0.1)
    parser.add_argument("--sigma", type=int, default=2)
    parser.add_argument("--tag", type=str, default="MW")
    args = parser.parse_args()
    
    summary = run_galaxy_sim(args.m_star, args.r_eff, args.k_eff, smoothing_sigma=args.sigma, tag=args.tag)
    print("\nSimulation complete. Key numbers:")
    for k, v in summary.items():
        print(f"{k}: {v}")

