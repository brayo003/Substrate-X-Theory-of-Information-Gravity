from pathlib import Path
import csv
import numpy as np

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

rows = []

for session, trial in TARGETS:
    files = [
        ("baseline", BASELINE / f"{session}_epochs.npz",
         "eeg_channel_names"),
        ("filtered", FILTERED / f"{session}.npz",
         "channel_names"),
    ]

    for source, path, channel_key in files:
        with np.load(path, allow_pickle=True) as data:
            x = np.asarray(data["eeg_uV"][trial], dtype=np.float64)
            channels = [str(v) for v in data[channel_key]]

        print(f"\n{'=' * 90}")
        print(f"{session} trial {trial} | {source}")

        for ci, channel in enumerate(channels):
            signal = x[ci]
            abs_signal = np.abs(signal)

            near_100 = np.isclose(abs_signal, 100.0, atol=1e-5)
            near_1000 = np.isclose(abs_signal, 1000.0, atol=1e-5)

            max_abs = float(np.max(abs_signal))
            max_indices = np.flatnonzero(
                np.isclose(abs_signal, max_abs, atol=1e-9)
            )

            exact_100 = int(np.sum(near_100))
            exact_1000 = int(np.sum(near_1000))

            row = {
                "session": session,
                "trial": trial,
                "source": source,
                "channel": channel,
                "min_uV": float(np.min(signal)),
                "max_uV": float(np.max(signal)),
                "max_abs_uV": max_abs,
                "count_near_plusminus_100": exact_100,
                "count_near_plusminus_1000": exact_1000,
                "count_unique_samples": int(np.unique(signal).size),
                "max_abs_sample_indices": ";".join(
                    str(int(i)) for i in max_indices[:20]
                ),
            }
            rows.append(row)

            if max_abs >= 90 or exact_1000:
                print(
                    f"{channel:5s} "
                    f"min={row['min_uV']:10.3f} "
                    f"max={row['max_uV']:10.3f} "
                    f"max_abs={max_abs:10.3f} "
                    f"near_100={exact_100:4d} "
                    f"near_1000={exact_1000:4d} "
                    f"unique={row['count_unique_samples']:4d} "
                    f"extrema_idx={row['max_abs_sample_indices']}"
                )

csv_path = OUT / "extreme_sample_boundary_audit.csv"

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nBOUNDARY AUDIT COMPLETE")
print(csv_path)
