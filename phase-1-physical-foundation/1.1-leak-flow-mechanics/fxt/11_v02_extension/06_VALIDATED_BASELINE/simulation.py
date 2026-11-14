#!/usr/bin/env python3
"""Generate the published-parameter conventional forward model for Figure 5.

This is Gate 3 infrastructure.  It cannot certify agreement until digitized
Figure 5 points are supplied and compared in Gate 5.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fluorescence import normalized_contrast
from spin_echo import echo_phase, gaussian_envelope


HERE = Path(__file__).resolve().parent


def load_config(path=HERE / "config" / "published_forward_model.json"):
    return json.loads(Path(path).read_text())


def simulate_figure5(tau_s, cfg):
    phase = echo_phase(
        tau_s,
        cfg["effective_ac_field_gauss"],
        cfg["rotation_frequency_hz"],
        cfg["electron_gyromagnetic_ratio_hz_per_gauss"],
        cfg["rotation_phase_rad"],
    )
    envelope = gaussian_envelope(tau_s, cfg["echo_coherence_time_s"])
    contrast = normalized_contrast(
        phase, envelope, cfg["readout_contrast"], cfg["readout_offset"], cfg["readout_phase_rad"]
    )
    return phase, envelope, contrast


def main():
    cfg = load_config()
    tau_s = np.linspace(0.0, 60e-6, 601)
    phase, envelope, contrast = simulate_figure5(tau_s, cfg)
    out = HERE / "outputs" / "published_forward_model"
    out.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        out / "figure5_forward_model.csv",
        np.c_[tau_s * 1e6, phase, envelope, contrast],
        delimiter=",",
        header="tau_us,echo_phase_rad,coherence_envelope,normalized_contrast",
        comments="",
    )
    (out / "run_metadata.json").write_text(json.dumps({
        "status": "FORWARD_MODEL_ONLY",
        "statement": "No digitized Figure 5 data have been compared; this output is not a validation result.",
        "config": cfg,
    }, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tau_s * 1e6, contrast, label="published-parameter conventional model")
    ax.set(xlabel="spin-echo time tau (us)", ylabel="normalized contrast")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "figure5_forward_model.png", dpi=180)
    print(out)


if __name__ == "__main__":
    main()

