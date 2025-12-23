#!/usr/bin/env python3
"""
Solar-system / Kepler diagnostics.

Creates:
  - Residual plot between substrate and Newtonian accelerations
  - Simple tracer orbit integration using the measured acceleration profile
"""

from pathlib import Path

import json

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).resolve().parent / "results"
ACCEL_FILE = RESULTS_DIR / "kepler_accel_data.npz"
SUMMARY_PATH = RESULTS_DIR / "kepler_diagnostics.json"


def load_data():
    data = np.load(ACCEL_FILE)
    return data["radii"], data["accel_sub"], data["accel_newtonian"], data["ratio"]


def plot_residuals(radii, accel_sub, accel_newt):
    residual = accel_sub - accel_newt
    plt.figure(figsize=(8, 4))
    plt.plot(radii / 1e9, residual)
    plt.xlabel("Radius (billion m)")
    plt.ylabel("Δa (m/s²)")
    plt.title("Substrate vs Newtonian acceleration residuals")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "kepler_residuals.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out, residual


def integrate_orbit(radii, accel_sub, dt=500.0, steps=20000):
    interp_accel = lambda r: np.interp(r, radii, accel_sub, left=accel_sub[0], right=accel_sub[-1])
    pos = np.array([1.5e11, 0.0])
    vel = np.array([0.0, 30000.0])
    positions = []
    for _ in range(steps):
        r = np.linalg.norm(pos)
        acc_mag = interp_accel(r)
        acc = -acc_mag * pos / (r + 1e-12)
        vel += acc * dt
        pos += vel * dt
        positions.append(pos.copy())
    positions = np.array(positions)
    plt.figure(figsize=(5, 5))
    plt.plot(positions[:, 0] / 1e11, positions[:, 1] / 1e11)
    plt.xlabel("x (0.1 AU)")
    plt.ylabel("y (0.1 AU)")
    plt.title("Tracer orbit under substrate acceleration")
    plt.axis("equal")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "kepler_orbit.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    peri = np.min(np.linalg.norm(positions, axis=1))
    apo = np.max(np.linalg.norm(positions, axis=1))
    return out, peri, apo


def main():
    radii, accel_sub, accel_newt, ratio = load_data()
    residual_plot, residual = plot_residuals(radii, accel_sub, accel_newt)
    orbit_plot, peri, apo = integrate_orbit(radii, accel_sub)
    summary = {
        "residual_plot": str(residual_plot.relative_to(Path.cwd())),
        "orbit_plot": str(orbit_plot.relative_to(Path.cwd())),
        "residual_std": float(np.std(residual)),
        "perihelion_m": peri,
        "aphelion_m": apo,
        "mean_ratio": float(np.nanmean(ratio)),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Kepler diagnostics complete.")


if __name__ == "__main__":
    main()

