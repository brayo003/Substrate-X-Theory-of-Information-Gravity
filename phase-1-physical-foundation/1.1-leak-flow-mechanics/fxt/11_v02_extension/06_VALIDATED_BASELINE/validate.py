#!/usr/bin/env python3
"""Gate 4/5 comparisons against digitized (not raw) paper figures."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from spin_echo import echo_phase, gaussian_envelope

HERE = Path(__file__).resolve().parent


def read_csv(name):
    with (HERE / "digitized" / name).open() as handle:
        return list(csv.DictReader(handle))


def weighted_rmse(observed, model, sigma):
    return float(np.sqrt(np.mean(np.square((observed - model) / sigma))))


def validate_figure4(out):
    rows = read_csv("figure4a_points.csv")
    x = np.array([float(r["pulse_duration_ns"]) for r in rows]) * 1e-9
    y = np.array([float(r["normalized_contrast"]) for r in rows])
    sigma = np.array([float(r["error_bar"]) for r in rows])

    def rabi(t, offset, amplitude, frequency_hz, phase):
        return offset + amplitude * np.cos(2 * np.pi * frequency_hz * t + phase)

    popt, pcov = curve_fit(
        rabi, x, y, p0=(0.90, 0.06, 3.6e6, 0.0), sigma=sigma,
        absolute_sigma=True, bounds=([0, -1, 1e6, -2*np.pi], [2, 1, 10e6, 2*np.pi]), maxfev=100000,
    )
    pred = rabi(x, *popt)
    stderr = np.sqrt(np.diag(pcov))
    metrics = {
        "fit_frequency_mhz": float(popt[2] / 1e6),
        "fit_frequency_standard_error_mhz": float(stderr[2] / 1e6),
        "published_frequency_mhz": 3.6,
        "published_standard_error_mhz": 0.2,
        "frequency_difference_mhz": float(popt[2] / 1e6 - 3.6),
        "weighted_rmse": weighted_rmse(y, pred, sigma),
        "plain_rmse": float(np.sqrt(np.mean((y-pred)**2))),
        "fit_parameters": {"offset": float(popt[0]), "amplitude": float(popt[1]), "phase_rad": float(popt[3])},
        "status": "PARTIAL: digitized curve supports a Rabi-scale check only; readout parameters are fitted."
    }
    dense = np.linspace(0, 400e-9, 1000)
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7, 5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax.errorbar(x*1e9, y, yerr=sigma, fmt="o", label="digitized Figure 4A")
    ax.plot(dense*1e9, rabi(dense, *popt), label="fitted conventional Rabi model")
    ax.legend(); ax.set_ylabel("normalized contrast")
    rx.axhline(0, color="k", lw=0.7); rx.errorbar(x*1e9, y-pred, yerr=sigma, fmt="o")
    rx.set(xlabel="microwave pulse duration (ns)", ylabel="residual")
    fig.tight_layout(); fig.savefig(out / "figure4_residuals.png", dpi=180); plt.close(fig)
    return metrics


def validate_figure5(out):
    cfg = json.loads((HERE / "config" / "published_forward_model.json").read_text())
    rows = read_csv("figure5_rotating_points.csv")
    tau = np.array([float(r["spin_echo_time_us"]) for r in rows]) * 1e-6
    y = np.array([float(r["normalized_contrast"]) for r in rows])
    sigma = np.array([float(r["error_bar"]) for r in rows])
    envelope = gaussian_envelope(tau, cfg["echo_coherence_time_s"])

    def echo(t, field_gauss, rot_phase, contrast, offset):
        phase = echo_phase(t, field_gauss, cfg["rotation_frequency_hz"],
                           cfg["electron_gyromagnetic_ratio_hz_per_gauss"], rot_phase)
        return offset + contrast * gaussian_envelope(t, cfg["echo_coherence_time_s"]) * np.cos(phase)

    # Try phase seeds to avoid treating an arbitrary local optimizer outcome as physics.
    candidates = []
    for phase_seed in np.linspace(-np.pi, np.pi, 13):
        try:
            p, cov = curve_fit(echo, tau, y, p0=(0.088, phase_seed, 0.29, 0.0), sigma=sigma,
                               absolute_sigma=True,
                               bounds=([0, -2*np.pi, -1, -1], [0.5, 2*np.pi, 1, 1]), maxfev=100000)
            candidates.append((np.sum(np.square((y-echo(tau, *p))/sigma)), p, cov))
        except RuntimeError:
            pass
    chi2, popt, pcov = min(candidates, key=lambda item: item[0])
    pred = echo(tau, *popt)
    stderr = np.sqrt(np.diag(pcov))
    published_amplitude = cfg["effective_ac_field_gauss"]
    published_error = 0.029
    metrics = {
        "fit_effective_ac_field_gauss": float(popt[0]),
        "fit_effective_ac_field_standard_error_gauss": float(stderr[0]),
        "published_effective_ac_field_gauss": published_amplitude,
        "published_standard_error_gauss": published_error,
        "difference_from_published_gauss": float(popt[0] - published_amplitude),
        "fit_rotation_phase_rad": float(popt[1]),
        "fitted_readout_contrast": float(popt[2]),
        "fitted_readout_offset": float(popt[3]),
        "weighted_rmse": weighted_rmse(y, pred, sigma),
        "plain_rmse": float(np.sqrt(np.mean((y-pred)**2))),
        "chi_squared": float(chi2),
        "degrees_of_freedom": int(len(y)-len(popt)),
        "status": "PARTIAL: conventional Eq. (1) model fit to digitized points only; no raw data or independently fixed readout phase/contrast."
    }
    dense = np.linspace(0, 60e-6, 1000)
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(7, 5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax.errorbar(tau*1e6, y, yerr=sigma, fmt="o", label="digitized rotating Figure 5 points")
    ax.plot(dense*1e6, echo(dense, *popt), label="fitted conventional Eq. (1) model")
    ax.legend(); ax.set_ylabel("normalized contrast")
    rx.axhline(0, color="k", lw=0.7); rx.errorbar(tau*1e6, y-pred, yerr=sigma, fmt="o")
    rx.set(xlabel="spin-echo time tau (us)", ylabel="residual")
    fig.tight_layout(); fig.savefig(out / "figure5_residuals.png", dpi=180); plt.close(fig)
    return metrics


def main():
    out = HERE / "outputs" / "validation"
    out.mkdir(parents=True, exist_ok=True)
    result = {"figure4": validate_figure4(out), "figure5": validate_figure5(out)}
    (out / "validation_metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

