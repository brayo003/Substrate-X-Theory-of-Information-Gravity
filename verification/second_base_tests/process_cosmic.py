#!/usr/bin/env python3
"""
Cosmic expansion diagnostics.

Generates:
  - Mean field/acceleration trend plot
  - Power spectrum comparison for initial vs. final snapshots
  - JSON summary of drift magnitudes
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).resolve().parent / "results"
STATS_PATH = RESULTS_DIR / "cosmic_stats.json"
SNAPSHOT_FILE = RESULTS_DIR / "cosmic_snapshots.npz"
SUMMARY_PATH = RESULTS_DIR / "cosmic_diagnostics.json"


def load_stats():
    data = json.loads(STATS_PATH.read_text())
    times = np.array([rec["time"] for rec in data["records"]])
    mean_s = np.array([rec["mean_s"] for rec in data["records"]])
    mean_acc = np.array([rec["mean_acceleration"] for rec in data["records"]])
    return times, mean_s, mean_acc


def plot_trends(times, mean_s, mean_acc):
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax[0].plot(times / 1e12, mean_s)
    ax[0].set_ylabel("⟨s⟩")
    ax[0].grid(True, ls="--", alpha=0.4)
    ax[1].plot(times / 1e12, mean_acc)
    ax[1].set_xlabel("Time (10^12 s)")
    ax[1].set_ylabel("⟨∂²s/∂t²⟩")
    ax[1].grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "cosmic_mean_trends.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def power_spectrum(snapshot, label):
    fft = np.fft.fftn(snapshot)
    psd = np.abs(fft) ** 2
    k = np.fft.fftfreq(snapshot.shape[0])
    k_grid = np.sqrt(k[:, None] ** 2 + k[None, :] ** 2)
    return k_grid.flatten(), psd.flatten()


def compare_spectra():
    snaps = np.load(SNAPSHOT_FILE)
    k_i, p_i = power_spectrum(snaps["initial"], "initial")
    k_f, p_f = power_spectrum(snaps["final"], "final")
    bins = np.linspace(0, np.max(k_i), 100)
    def radial_avg(k, p):
        idx = np.digitize(k, bins) - 1
        accum = np.zeros(len(bins))
        counts = np.zeros(len(bins))
        for i, val in enumerate(p):
            if 0 <= idx[i] < len(bins):
                accum[idx[i]] += val
                counts[idx[i]] += 1
        counts[counts == 0] = 1
        return bins, accum / counts
    kb, pi = radial_avg(k_i, p_i)
    _, pf = radial_avg(k_f, p_f)
    plt.figure(figsize=(8, 4))
    plt.plot(kb, pi / np.max(pi), label="Initial")
    plt.plot(kb, pf / np.max(pf), label="Final")
    plt.xlabel("k (arb.)")
    plt.ylabel("Normalized power")
    plt.title("Cosmic power spectrum drift")
    plt.legend()
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "cosmic_power_spectrum.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def main():
    times, mean_s, mean_acc = load_stats()
    trend_plot = plot_trends(times, mean_s, mean_acc)
    spectrum_plot = compare_spectra()
    summary = {
        "trend_plot": str(trend_plot.relative_to(Path.cwd())),
        "spectrum_plot": str(spectrum_plot.relative_to(Path.cwd())),
        "mean_s_drift": float(mean_s[-1] - mean_s[0]),
        "mean_acc_sign": float(np.sign(np.mean(mean_acc))),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Cosmic diagnostics complete.")


if __name__ == "__main__":
    main()

