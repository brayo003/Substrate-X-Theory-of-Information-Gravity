#!/usr/bin/env python3
"""
Collapse diagnostics script.

Outputs:
  - Central field time series plot (already provided) -> compute stats
  - Radial profile comparison (initial/mid/final)
  - Horizon-radius estimate from |v_sub|
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants as const

RESULTS_DIR = Path(__file__).resolve().parent / "results"
HISTORY_FILE = RESULTS_DIR / "collapse_center_history.npz"
SNAPSHOT_FILE = RESULTS_DIR / "collapse_snapshots.npz"
VELOCITY_FILE = RESULTS_DIR / "collapse_velocity_mag.npy"
META_FILE = RESULTS_DIR / "collapse_meta.json"
SUMMARY_PATH = RESULTS_DIR / "collapse_diagnostics.json"


def radial_profile(field, grid_size, domain_size):
    coords = np.linspace(-domain_size / 2, domain_size / 2, grid_size)
    X, Y = np.meshgrid(coords, coords)
    R = np.sqrt(X**2 + Y**2)
    radii = np.linspace(0, domain_size / 2, 200)
    profile = np.zeros_like(radii)
    for i, r in enumerate(radii):
        mask = (R >= r - domain_size / (2 * grid_size)) & (R < r + domain_size / (2 * grid_size))
        if np.any(mask):
            profile[i] = np.mean(field[mask])
    return radii, profile


def plot_profiles(meta):
    snaps = np.load(SNAPSHOT_FILE)
    radii, p_init = radial_profile(snaps["initial"], meta["grid_size"], meta["domain_size"])
    _, p_mid = radial_profile(snaps["mid"], meta["grid_size"], meta["domain_size"])
    _, p_final = radial_profile(snaps["final"], meta["grid_size"], meta["domain_size"])
    plt.figure(figsize=(8, 4))
    plt.plot(radii / 1e9, p_init, label="Initial")
    plt.plot(radii / 1e9, p_mid, label="Mid")
    plt.plot(radii / 1e9, p_final, label="Final")
    plt.xlabel("Radius (billion m)")
    plt.ylabel("Average s")
    plt.title("Collapse radial profiles")
    plt.legend()
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "collapse_profiles.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def horizon_radius(meta):
    v_mag = np.load(VELOCITY_FILE)
    coords = np.linspace(-meta["domain_size"] / 2, meta["domain_size"] / 2, meta["grid_size"])
    X, Y = np.meshgrid(coords, coords)
    R = np.sqrt(X**2 + Y**2)
    mask = v_mag >= 0.9 * const.c
    if not np.any(mask):
        return None
    return float(np.min(R[mask]))


def main():
    history = np.load(HISTORY_FILE)
    times = history["times"]
    values = history["values"]
    mean_abs = float(np.mean(np.abs(values)))
    meta = json.loads(META_FILE.read_text())
    profile_plot = plot_profiles(meta)
    horizon = horizon_radius(meta)
    summary = {
        "mean_abs_center": mean_abs,
        "horizon_radius_m": horizon,
        "profile_plot": str(profile_plot.relative_to(Path.cwd())),
        "central_bounds": [float(values.min()), float(values.max())],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Collapse diagnostics complete.")


if __name__ == "__main__":
    main()

