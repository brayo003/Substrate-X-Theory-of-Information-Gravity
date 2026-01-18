#!/usr/bin/env python3
"""
Post-processing for the quantum standing-wave scenario.

Loads the latest solver outputs (fields + stats) and generates:
  1. Radial mode count verification
  2. Time-series FFT at a chosen radius
  3. Energy evolution plot (from stats)
  4. Dispersion estimate comparing measured ω(k) to theory
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
STATS_PATH = RESULTS_DIR / "quantum_stats.json"
FIELD_PATH = RESULTS_DIR / "quantum_radial_profile.npz"
SERIES_PATH = RESULTS_DIR / "quantum_time_series.npz"

def load_stats():
    data = json.loads(STATS_PATH.read_text())
    times = np.array([record["time"] for record in data["records"]])
    energy = np.array([record["total_energy"] for record in data["records"]])
    return times, energy

def radial_mode_count():
    data = np.load(FIELD_PATH)
    radii = data["radii"]
    profile = data["profile"]
    deriv = np.gradient(profile, radii)
    zero_cross = np.where(np.sign(deriv[:-1]) * np.sign(deriv[1:]) < 0)[0]
    return zero_cross, radii[zero_cross]

def fft_at_radius():
    if not SERIES_PATH.exists():
        return None
    data = np.load(SERIES_PATH)
    times = data["times"]
    values = data["values"]
    if len(times) < 2:
        return None
    dt = np.mean(np.diff(times))
    freqs = np.fft.rfftfreq(len(values), d=dt)
    spectrum = np.abs(np.fft.rfft(values - np.mean(values)))
    plt.figure(figsize=(8, 4))
    plt.plot(freqs, spectrum / np.max(spectrum))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Normalized amplitude")
    plt.title("Quantum test FFT at sample radius")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "quantum_fft.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return freqs, spectrum, out

def plot_energy(times, energy):
    plt.figure(figsize=(8, 4))
    plt.plot(times, energy / np.max(energy))
    plt.xlabel("Time (s)")
    plt.ylabel("Total energy / max")
    plt.title("Quantum test energy evolution")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "quantum_energy.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out

def dispersion_estimate(radii, profile, peak_indices):
    shell_centers = radii[peak_indices]
    k_values = np.pi * np.arange(1, len(shell_centers) + 1) / radii[-1]
    fft_result = fft_at_radius()
    if fft_result is None:
        return None
    freqs, spectrum, _ = fft_result
    dominant = freqs[np.argmax(spectrum[1:]) + 1]
    dispersion_data = np.column_stack([k_values, np.full_like(k_values, dominant)])
    out = RESULTS_DIR / "quantum_dispersion.npy"
    np.save(out, dispersion_data)
    return out

def main():
    times, energy = load_stats()
    peak_indices, peak_positions = radial_mode_count()
    plot_energy(times, energy)
    data = np.load(FIELD_PATH)
    dispersion_estimate(data["radii"], data["profile"], peak_indices)
    print(f"Quantum diagnostics complete. Mode count = {len(peak_indices)}")

if __name__ == "__main__":
    main()

