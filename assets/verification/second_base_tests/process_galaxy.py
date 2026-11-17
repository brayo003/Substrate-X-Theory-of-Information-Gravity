#!/usr/bin/env python3
"""
Galaxy rotation diagnostics.

Outputs:
  - Ratio plot of v_sub vs v_newt
  - Stability plot of inner/outer velocities over time
  - JSON summary with flattening metrics
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).resolve().parent / "results"
CURVE_FILE = RESULTS_DIR / "galaxy_rotation_curve.npz"
HISTORY_FILE = RESULTS_DIR / "galaxy_rotation_history.json"
SUMMARY_PATH = RESULTS_DIR / "galaxy_diagnostics.json"


def load_curve():
    data = np.load(CURVE_FILE)
    return data["radii"], data["v_sub"], data["v_newtonian"]


def plot_ratio(radii, v_sub, v_newt):
    ratio = v_sub / np.maximum(v_newt, 1e-9)
    plt.figure(figsize=(8, 4))
    plt.plot(radii / 1e19, ratio)
    plt.xlabel("Radius (1e19 m)")
    plt.ylabel("v_sub / v_newt")
    plt.title("Rotation curve flattening ratio")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "galaxy_ratio.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out, ratio


def plot_history():
    history = json.loads(HISTORY_FILE.read_text())
    times = np.array([entry["time"] for entry in history])
    outer = np.array([entry["outer_velocity"] for entry in history])
    inner = np.array([entry["inner_velocity"] for entry in history])
    plt.figure(figsize=(8, 4))
    plt.plot(times / 1e9, outer / 1e3, label="Outer velocity (km/s)")
    plt.plot(times / 1e9, inner / 1e3, label="Inner velocity (km/s)")
    plt.xlabel("Time (10^9 s)")
    plt.ylabel("Velocity (km/s)")
    plt.title("Rotation curve stability")
    plt.legend()
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "galaxy_stability.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out, float(np.std(outer[-5:]) / np.mean(outer[-5:]))


def main():
    radii, v_sub, v_newt = load_curve()
    ratio_plot, ratio = plot_ratio(radii, v_sub, v_newt)
    history_plot, outer_rel_std = plot_history()
    summary = {
        "ratio_plot": str(ratio_plot.relative_to(Path.cwd())),
        "stability_plot": str(history_plot.relative_to(Path.cwd())),
        "outer_ratio_mean": float(np.nanmean(ratio[-30:])),
        "outer_ratio_std": float(np.nanstd(ratio[-30:])),
        "outer_velocity_rel_std": outer_rel_std,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Galaxy diagnostics complete.")


if __name__ == "__main__":
    main()

