from pathlib import Path
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "data/processed/bci_iv_2a_epochs_v1"
FILTERED = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
OUT = ROOT / "bci_evidence_experiment/results/extreme_waveforms"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("A03E", 178),
    ("A04T", 179),
    ("A08T", 81),
]

def load_session(session, trial):
    base_path = BASELINE / f"{session}_epochs.npz"
    filtered_path = FILTERED / f"{session}.npz"

    with np.load(base_path, allow_pickle=True) as base, \
         np.load(filtered_path, allow_pickle=True) as filt:

        x_base = np.asarray(base["eeg_uV"][trial], dtype=np.float64)
        x_filt = np.asarray(filt["eeg_uV"][trial], dtype=np.float64)

        base_channels = [str(x) for x in base["eeg_channel_names"]]
        filt_channels = [str(x) for x in filt["channel_names"]]

        if base_channels != filt_channels:
            raise ValueError(f"{session}: baseline/filtered channel order differs")

        if x_base.shape != x_filt.shape:
            raise ValueError(f"{session}: baseline/filtered trial shapes differ")

        if not np.array_equal(base["labels"], filt["labels"]):
            raise ValueError(f"{session}: labels differ")

        if not np.array_equal(base["artifact_flags"], filt["artifact_flags"]):
            raise ValueError(f"{session}: artifact flags differ")

        if int(base["artifact_flags"][trial]) != 1:
            raise ValueError(
                f"{session} trial {trial}: expected artifact flag 1"
            )

        return x_base, x_filt, base_channels

summary = []

for session, trial in TARGETS:
    xb, xf, channels = load_session(session, trial)
    t = np.arange(xb.shape[1]) / 250.0 + 2.0

    fig, axes = plt.subplots(11, 2, figsize=(17, 23), sharex=True)
    fig.suptitle(
        f"{session}, trial {trial} (0-based) — baseline vs 8–30 Hz",
        fontsize=14
    )

    for i, channel in enumerate(channels):
        row = i if i < 11 else i - 11
        col = 0 if i < 11 else 1
        ax = axes[row, col]

        ax.plot(t, xb[i], linewidth=0.7, label="Baseline")
        ax.plot(t, xf[i], linewidth=0.7, label="8–30 Hz")
        ax.set_title(channel)
        ax.set_ylabel("µV")
        ax.grid(alpha=0.25)

    axes[0, 0].legend(loc="upper right", fontsize=8)
    axes[-1, 0].set_xlabel("Time from trial onset (s)")
    axes[-1, 1].set_xlabel("Time from trial onset (s)")

    fig.tight_layout(rect=[0, 0, 1, 0.98])
    image_path = OUT / f"{session}_trial_{trial}_all_channels.png"
    fig.savefig(image_path, dpi=150)
    plt.close(fig)

    for i, channel in enumerate(channels):
        def excess_kurtosis(x):
            sd = np.std(x)
            if sd <= 1e-12:
                return float("nan")
            z = (x - np.mean(x)) / sd
            return float(np.mean(z ** 4) - 3.0)

        summary.append({
            "session": session,
            "trial_index_0based": trial,
            "channel": channel,
            "artifact_flag": 1,
            "baseline_peak_abs_uV": float(np.max(np.abs(xb[i]))),
            "filtered_peak_abs_uV": float(np.max(np.abs(xf[i]))),
            "baseline_peak_to_peak_uV": float(np.ptp(xb[i])),
            "filtered_peak_to_peak_uV": float(np.ptp(xf[i])),
            "baseline_kurtosis": excess_kurtosis(xb[i]),
            "filtered_kurtosis": excess_kurtosis(xf[i]),
        })

    print(f"{session}: saved {image_path}")

csv_path = OUT / "extreme_waveform_metrics.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

print("\nWAVEFORM INSPECTION COMPLETE")
print(f"Images: {OUT}")
print(f"Metrics: {csv_path}")
