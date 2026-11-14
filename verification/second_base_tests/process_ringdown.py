#!/usr/bin/env python3
"""
Ringdown diagnostics for the LIGO-aligned scenario.

Fits the late-time waveform to a damped sinusoid, extracts
frequency, damping time, and quality factor, and compares them
to the GR target computed from the meta information.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import hilbert

RESULTS_DIR = Path(__file__).resolve().parent / "results"
WAVEFORM_FILE = RESULTS_DIR / "ligo_waveform_data.npz"
META_FILE = RESULTS_DIR / "ringdown_meta.json"
SUMMARY_PATH = RESULTS_DIR / "ringdown_diagnostics.json"


def fit_ringdown(times, signal, fraction=0.6):
    start_idx = int(len(times) * fraction)
    t = times[start_idx:] - times[start_idx]
    y = signal[start_idx:] - np.mean(signal[start_idx:])
    if len(t) < 10:
        raise ValueError("Not enough data for ringdown fit")
    dt = np.mean(np.diff(t))
    freqs = np.fft.rfftfreq(len(y), d=dt)
    spectrum = np.abs(np.fft.rfft(y))
    peak_idx = np.argmax(spectrum[1:]) + 1
    peak_freq = freqs[peak_idx]

    analytic = hilbert(y)
    envelope = np.abs(analytic)
    positive = envelope > 0
    if np.sum(positive) < 5:
        raise ValueError("Envelope not well defined for fit")
    slope, intercept = np.polyfit(t[positive], np.log(envelope[positive]), 1)
    tau = -1.0 / slope
    q_factor = np.pi * peak_freq * tau
    fit_envelope = np.exp(intercept + slope * t)
    return peak_freq, tau, q_factor, t, y, fit_envelope


def main():
    meta = json.loads(META_FILE.read_text())
    data = np.load(WAVEFORM_FILE)
    times = data["times"]
    signal = data["signal"]
    f_sub, tau_sub, q_sub, t_fit, y_fit, env_fit = fit_ringdown(times, signal)

    plt.figure(figsize=(8, 4))
    plt.plot(times, signal, label="Detector signal")
    plt.axvline(times[int(len(times) * 0.6)], color="gray", linestyle="--", label="Fit start")
    plt.xlabel("Time (s)")
    plt.ylabel("s")
    plt.title("LIGO-like ringdown waveform")
    plt.grid(True, ls="--", alpha=0.4)
    waveform_plot = RESULTS_DIR / "ringdown_waveform.png"
    plt.tight_layout()
    plt.savefig(waveform_plot, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(t_fit, np.abs(y_fit), label="Envelope |s|")
    plt.plot(t_fit, env_fit, label="Exponential fit", linestyle="--")
    plt.xlabel("Time since fit start (s)")
    plt.ylabel("Amplitude")
    plt.yscale("log")
    plt.grid(True, ls="--", alpha=0.4)
    plt.legend()
    envelope_plot = RESULTS_DIR / "ringdown_envelope.png"
    plt.tight_layout()
    plt.savefig(envelope_plot, dpi=150)
    plt.close()

    summary = {
        "f_sub_Hz": f_sub,
        "tau_sub_s": tau_sub,
        "Q_sub": q_sub,
        "f_GR_Hz": meta["gr_freq_Hz"],
        "tau_GR_s": meta["gr_tau_s"],
        "Q_GR": meta["gr_Q"],
        "waveform_plot": str(waveform_plot.relative_to(Path.cwd())),
        "envelope_plot": str(envelope_plot.relative_to(Path.cwd())),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    print("Ringdown diagnostics complete.")


if __name__ == "__main__":
    main()

