from pathlib import Path
import importlib.util
import csv

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
BASELINE = ROOT / "data/processed/bci_iv_2a_epochs_v1"
OUT = ROOT / "bci_evidence_experiment/results/extreme_waveforms"
OUT.mkdir(parents=True, exist_ok=True)

BUILDER_PATH = (
    ROOT / "bci_evidence_experiment/preprocessing/"
    "build_bci_8_30hz_epochs.py"
)

spec = importlib.util.spec_from_file_location(
    "bci_builder", BUILDER_PATH
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

TARGETS = [
    ("A03E", 178),
    ("A04T", 179),
    ("A08T", 81),
]

rows = []

for session, global_trial in TARGETS:
    mat_path = SOURCE / f"{session}.mat"
    baseline_path = BASELINE / f"{session}_epochs.npz"

    mat = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False
    )
    entries = builder.get_run_entries(mat)

    with np.load(baseline_path, allow_pickle=True) as base:
        run_id = int(base["run_ids"][global_trial])
        trial_id = int(base["trial_ids"][global_trial])
        event_sample = int(
            base["event_samples_1based"][global_trial]
        )
        baseline_epoch = np.asarray(
            base["eeg_uV"][global_trial],
            dtype=np.float64
        )
        channels = [
            str(v) for v in base["eeg_channel_names"]
        ]

    entry = entries[run_id - 1]

    x = builder.continuous_samples_by_channels(
        entry.X, session, run_id
    )

    fs = int(round(float(builder.scalar(entry.fs))))
    event_index = event_sample - 1
    start = event_index + 2 * fs
    stop = event_index + 6 * fs

    source_epoch = x[start:stop, :][:, builder.EEG_INDICES].T
    source_epoch = np.asarray(source_epoch, dtype=np.float64)

    if source_epoch.shape != baseline_epoch.shape:
        raise ValueError(
            f"{session}: source shape {source_epoch.shape} "
            f"!= baseline shape {baseline_epoch.shape}"
        )

    difference = source_epoch - baseline_epoch

    print("\n" + "=" * 90)
    print(
        f"{session}: global={global_trial}, run={run_id}, "
        f"trial={trial_id}, event={event_sample}"
    )
    print("Source X shape:", x.shape)
    print("Source epoch shape:", source_epoch.shape)
    print("Baseline epoch shape:", baseline_epoch.shape)
    print("Maximum absolute source-baseline difference:",
          float(np.max(np.abs(difference))))
    print("Mean absolute source-baseline difference:",
          float(np.mean(np.abs(difference))))
    print("Exact array equality:", np.array_equal(
        source_epoch, baseline_epoch
    ))

    print("\nChannel-level boundary comparison:")

    for ci, channel in enumerate(channels):
        src = source_epoch[ci]
        base_signal = baseline_epoch[ci]

        src_100 = int(np.sum(
            np.isclose(np.abs(src), 100.0, atol=1e-5)
        ))
        base_100 = int(np.sum(
            np.isclose(np.abs(base_signal), 100.0, atol=1e-5)
        ))

        src_1000 = int(np.sum(
            np.isclose(np.abs(src), 1000.0, atol=1e-5)
        ))
        base_1000 = int(np.sum(
            np.isclose(np.abs(base_signal), 1000.0, atol=1e-5)
        ))

        max_diff = float(np.max(np.abs(src - base_signal)))

        record = {
            "session": session,
            "global_trial": global_trial,
            "run": run_id,
            "trial_within_run": trial_id,
            "channel": channel,
            "source_min_uV": float(np.min(src)),
            "source_max_uV": float(np.max(src)),
            "baseline_min_uV": float(np.min(base_signal)),
            "baseline_max_uV": float(np.max(base_signal)),
            "source_count_abs_100": src_100,
            "baseline_count_abs_100": base_100,
            "source_count_abs_1000": src_1000,
            "baseline_count_abs_1000": base_1000,
            "max_abs_difference_uV": max_diff,
        }
        rows.append(record)

        if (
            src_100 or base_100 or src_1000 or base_1000
            or max_diff > 1e-5
        ):
            print(
                f"{channel:5s} "
                f"source=[{np.min(src):9.3f}, {np.max(src):9.3f}] "
                f"baseline=[{np.min(base_signal):9.3f}, "
                f"{np.max(base_signal):9.3f}] "
                f"source_100={src_100:4d} "
                f"base_100={base_100:4d} "
                f"source_1000={src_1000:4d} "
                f"base_1000={base_1000:4d} "
                f"max_diff={max_diff:.8f}"
            )

csv_path = OUT / "source_mat_vs_baseline_extreme_trials.csv"

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nSOURCE-TO-BASELINE COMPARISON COMPLETE")
print("CSV:", csv_path)
