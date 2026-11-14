#!/usr/bin/env python3
"""
Binary waveform diagnostics.

Produces:
  - FFT magnitude plot
  - Amplitude envelope plot
  - Energy-flux estimate at detector
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).resolve().parent / "results"
WAVEFORM_FILE = RESULTS_DIR / "binary_waveform_data.npz"
STATS_PATH = RESULTS_DIR / "binary_stats.json"
SUMMARY_PATH = RESULTS_DIR / "binary_diagnostics.json"


def load_waveform():
    data = np.load(WAVEFORM_FILE)
    return data["times"], data["signal"]


def fft_plot(times, signal):
    dt = np.mean(np.diff(times))
    freqs = np.fft.rfftfreq(len(signal), d=dt)
    spectrum = np.abs(np.fft.rfft(signal))
    plt.figure(figsize=(8, 4))
    plt.plot(freqs, spectrum / np.max(spectrum))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Normalized amplitude")
    plt.title("Binary waveform FFT")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "binary_fft.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    peak_idx = np.argmax(spectrum[1:]) + 1
    return out, float(freqs[peak_idx])


def amplitude_plot(times, signal):
    env = np.abs(signal)
    plt.figure(figsize=(8, 4))
    plt.plot(times, env)
    plt.xlabel("Time (s)")
    plt.ylabel("|s|")
    plt.title("Binary waveform amplitude envelope")
    plt.grid(True, ls="--", alpha=0.4)
    out = RESULTS_DIR / "binary_amplitude.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out, float(np.max(env))


def energy_flux(times, signal):
    dt = np.mean(np.diff(times))
    ds_dt = np.gradient(signal, dt)
    flux = ds_dt**2
    avg_flux = float(np.mean(flux))
    out = RESULTS_DIR / "binary_flux.npy"
    np.save(out, flux)
    return out, avg_flux


def main():
    times, signal = load_waveform()
    fft_path, peak_freq = fft_plot(times, signal)
    amp_path, amp_peak = amplitude_plot(times, signal)
    flux_path, avg_flux = energy_flux(times, signal)
    stats = json.loads(STATS_PATH.read_text())
    summary = {
        "fft_plot": str(fft_path.relative_to(Path.cwd())),
        "amplitude_plot": str(amp_path.relative_to(Path.cwd())),
        "flux_file": str(flux_path.relative_to(Path.cwd())),
        "peak_frequency_Hz": peak_freq,
        "peak_amplitude": amp_peak,
        "avg_flux": avg_flux,
        "expected_double_frequency": stats["records"][0].get("mean_acceleration", None),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Binary diagnostics complete.")


if __name__ == "__main__":
    main()

