#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import csv

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]

SOURCE = (
    ROOT
    / "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
)

AUDIT_DIR = (
    ROOT / "bci_evidence_experiment/results/source_boundary_audit"
)

OUT = (
    ROOT / "bci_evidence_experiment/results/"
    "continuous_boundary_event_inspection"
)
PLOT_DIR = OUT / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

BUILDER_PATH = (
    ROOT
    / "bci_evidence_experiment/preprocessing/"
    "build_bci_8_30hz_epochs.py"
)

spec = importlib.util.spec_from_file_location(
    "bci_builder", BUILDER_PATH
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

FS = 250
EPOCH_START_SECONDS = 2
EPOCH_STOP_SECONDS = 6
CONTEXT_SECONDS = 2
TOL = 1e-7

BOUNDARIES = (-100.0, -1000.0)

affected = pd.read_csv(
    AUDIT_DIR / "trial_boundary_audit.csv"
)
affected = affected[affected["has_any_boundary"] == 1].copy()

if len(affected) != 12:
    raise RuntimeError(
        f"Expected 12 affected trials; found {len(affected)}"
    )

summary_rows = []
timestamp_rows = []


def boundary_mask(data, value):
    return np.isclose(
        data, value, rtol=0.0, atol=TOL
    )


def longest_run(mask):
    mask = np.asarray(mask, dtype=bool)
    if not np.any(mask):
        return 0

    padded = np.concatenate(([False], mask, [False]))
    diff = np.diff(padded.astype(np.int8))
    starts = np.flatnonzero(diff == 1)
    stops = np.flatnonzero(diff == -1)

    return int(np.max(stops - starts))


def run_count(mask):
    mask = np.asarray(mask, dtype=bool)
    if not np.any(mask):
        return 0

    padded = np.concatenate(([False], mask, [False]))
    return int(np.sum(np.diff(padded.astype(np.int8)) == 1))


def contiguous_groups(indices):
    """Split sorted integer indices into consecutive groups."""
    if len(indices) == 0:
        return []

    indices = np.asarray(indices, dtype=int)
    cuts = np.where(np.diff(indices) > 1)[0] + 1
    return np.split(indices, cuts)


for _, trial in affected.iterrows():
    session = str(trial["session"])
    run_number = int(trial["run"])
    trial_number = int(trial["trial_within_run"])

    print(
        f"Inspecting {session}, run {run_number}, "
        f"trial {trial_number} ..."
    )

    mat_path = SOURCE / f"{session}.mat"
    mat = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False
    )

    entries = builder.get_run_entries(mat)
    entry = entries[run_number - 1]

    x = builder.continuous_samples_by_channels(
        entry.X, session, run_number
    )

    fs = int(round(float(builder.scalar(entry.fs))))
    if fs != FS:
        raise RuntimeError(
            f"{session} run {run_number}: sampling rate {fs}"
        )

    eeg = np.asarray(
        x[:, builder.EEG_INDICES],
        dtype=np.float64
    ).T

    channel_names = [
        str(name) for name in builder.CHANNEL_NAMES
    ]

    positions = np.asarray(entry.trial).reshape(-1).astype(int)
    event_sample_1based = int(
        positions[trial_number - 1]
    )

    event_index = event_sample_1based - 1
    epoch_start = event_index + EPOCH_START_SECONDS * fs
    epoch_stop = event_index + EPOCH_STOP_SECONDS * fs

    epoch = eeg[:, epoch_start:epoch_stop]

    mask100 = boundary_mask(epoch, -100.0)
    mask1000 = boundary_mask(epoch, -1000.0)

    combined = mask100 | mask1000
    boundary_time_indices = np.flatnonzero(
        np.any(combined, axis=0)
    )

    if boundary_time_indices.size == 0:
        raise RuntimeError(
            f"{session} run {run_number} trial {trial_number}: "
            "audit says affected but no boundary values were found"
        )

    first_epoch_index = int(boundary_time_indices[0])
    last_epoch_index = int(boundary_time_indices[-1])

    first_source_index = epoch_start + first_epoch_index
    last_source_index = epoch_start + last_epoch_index

    context_samples = CONTEXT_SECONDS * fs
    window_start = max(0, first_source_index - context_samples)
    window_stop = min(
        eeg.shape[1],
        last_source_index + context_samples + 1
    )

    window = eeg[:, window_start:window_stop]

    # Detailed per-channel boundary statistics in the epoch.
    channel_details = []

    for ci, channel in enumerate(channel_names):
        c100 = mask100[ci]
        c1000 = mask1000[ci]

        if np.any(c100) or np.any(c1000):
            channel_details.append({
                "channel": channel,
                "minus100_count": int(np.sum(c100)),
                "minus1000_count": int(np.sum(c1000)),
                "minus100_longest_run": longest_run(c100),
                "minus1000_longest_run": longest_run(c1000),
                "minus100_sequence_count": run_count(c100),
                "minus1000_sequence_count": run_count(c1000),
            })

    # At each sample, count channels matching each boundary.
    sim100 = np.sum(mask100, axis=0)
    sim1000 = np.sum(mask1000, axis=0)

    sync100_indices = np.flatnonzero(sim100 >= 2)
    sync1000_indices = np.flatnonzero(sim1000 >= 2)

    # Find simultaneous occurrences of either boundary.
    any_sync = np.flatnonzero(
        (sim100 >= 2) | (sim1000 >= 2)
    )

    # Save every epoch timestamp where at least one boundary occurs.
    for t in boundary_time_indices:
        channels100 = [
            channel_names[i]
            for i in np.flatnonzero(mask100[:, t])
        ]
        channels1000 = [
            channel_names[i]
            for i in np.flatnonzero(mask1000[:, t])
        ]

        timestamp_rows.append({
            "session": session,
            "run": run_number,
            "trial_within_run": trial_number,
            "epoch_sample_index_0based": int(t),
            "source_sample_index_0based": int(epoch_start + t),
            "time_after_trial_marker_seconds": (
                float((epoch_start + t - event_index) / fs)
            ),
            "time_after_epoch_start_seconds": float(t / fs),
            "minus100_channel_count": int(sim100[t]),
            "minus1000_channel_count": int(sim1000[t]),
            "minus100_channels": ";".join(channels100),
            "minus1000_channels": ";".join(channels1000),
        })

    # Context-window measurements.
    window_min = np.min(window, axis=1)
    window_max = np.max(window, axis=1)

    # Exact boundary occurrences in the context window.
    window100 = boundary_mask(window, -100.0)
    window1000 = boundary_mask(window, -1000.0)

    context100 = int(np.sum(window100))
    context1000 = int(np.sum(window1000))

    # Are the same values present at exactly the same timestamps?
    # This counts channels at each sample for each boundary.
    context_sim100 = np.sum(window100, axis=0)
    context_sim1000 = np.sum(window1000, axis=0)

    # Identify contiguous periods where 2+ channels share a boundary.
    sync100_groups = contiguous_groups(
        np.flatnonzero(context_sim100 >= 2)
    )
    sync1000_groups = contiguous_groups(
        np.flatnonzero(context_sim1000 >= 2)
    )

    max_sync100_duration = max(
        [len(group) for group in sync100_groups],
        default=0
    ) / fs

    max_sync1000_duration = max(
        [len(group) for group in sync1000_groups],
        default=0
    ) / fs

    # Determine whether all channels have identical values at a
    # timestamp where at least two channels equal the same boundary.
    exact_vector_matches = 0

    for t in np.flatnonzero(
        (context_sim100 >= 2) | (context_sim1000 >= 2)
    ):
        values = window[:, t]
        matching100 = np.isclose(
            values, -100.0, rtol=0.0, atol=TOL
        )
        matching1000 = np.isclose(
            values, -1000.0, rtol=0.0, atol=TOL
        )

        if np.sum(matching100) >= 2 or np.sum(matching1000) >= 2:
            exact_vector_matches += 1

    # Save waveform plot: each channel has its own vertical scale.
    n_channels = len(channel_names)
    fig, axes = plt.subplots(
        n_channels,
        1,
        figsize=(15, max(18, n_channels * 1.05)),
        sharex=True
    )

    time_axis = (
        np.arange(window_start, window_stop) - event_index
    ) / fs

    for ci, ax in enumerate(axes):
        signal = window[ci]

        ax.plot(
            time_axis,
            signal,
            linewidth=0.65
        )

        ax.axhline(
            -100.0,
            linestyle="--",
            linewidth=0.55
        )
        ax.axhline(
            -1000.0,
            linestyle=":",
            linewidth=0.55
        )

        local100 = np.flatnonzero(
            boundary_mask(signal, -100.0)
        )
        local1000 = np.flatnonzero(
            boundary_mask(signal, -1000.0)
        )

        if local100.size:
            ax.scatter(
                time_axis[local100],
                signal[local100],
                s=8,
                marker="o"
            )

        if local1000.size:
            ax.scatter(
                time_axis[local1000],
                signal[local1000],
                s=10,
                marker="x"
            )

        ax.set_ylabel(
            channel_names[ci],
            rotation=0,
            labelpad=22
        )
        ax.grid(True, alpha=0.2)

    axes[-1].set_xlabel(
        "Time relative to trial marker (seconds)"
    )

    fig.suptitle(
        f"{session} | Run {run_number} | Trial {trial_number}\n"
        f"Label={int(trial['label'])}, "
        f"artifact_flag={int(trial['artifact_flag'])}\n"
        f"Context: {CONTEXT_SECONDS}s before/after boundary span",
        fontsize=12
    )

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    plot_path = (
        PLOT_DIR
        / f"{session}_run{run_number}_trial{trial_number}.png"
    )

    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    summary_rows.append({
        "session": session,
        "run": run_number,
        "trial_within_run": trial_number,
        "label": int(trial["label"]),
        "artifact_flag": int(trial["artifact_flag"]),
        "event_sample_1based": event_sample_1based,
        "source_first_boundary_sample_0based": first_source_index,
        "source_last_boundary_sample_0based": last_source_index,
        "first_boundary_time_after_marker_seconds": float(
            (first_source_index - event_index) / fs
        ),
        "last_boundary_time_after_marker_seconds": float(
            (last_source_index - event_index) / fs
        ),
        "boundary_span_seconds": float(
            (last_source_index - first_source_index) / fs
        ),
        "epoch_minus100_count": int(np.sum(mask100)),
        "epoch_minus1000_count": int(np.sum(mask1000)),
        "epoch_channels_with_minus100": int(
            np.sum(np.sum(mask100, axis=1) > 0)
        ),
        "epoch_channels_with_minus1000": int(
            np.sum(np.sum(mask1000, axis=1) > 0)
        ),
        "epoch_max_simultaneous_minus100_channels": int(
            np.max(sim100)
        ),
        "epoch_max_simultaneous_minus1000_channels": int(
            np.max(sim1000)
        ),
        "epoch_timepoints_with_2plus_minus100": int(
            np.sum(sim100 >= 2)
        ),
        "epoch_timepoints_with_2plus_minus1000": int(
            np.sum(sim1000 >= 2)
        ),
        "context_window_start_sample_0based": window_start,
        "context_window_stop_sample_exclusive": window_stop,
        "context_window_duration_seconds": float(
            (window_stop - window_start) / fs
        ),
        "context_minus100_count": context100,
        "context_minus1000_count": context1000,
        "context_max_simultaneous_minus100_channels": int(
            np.max(context_sim100)
        ),
        "context_max_simultaneous_minus1000_channels": int(
            np.max(context_sim1000)
        ),
        "context_longest_synchronized_minus100_seconds": (
            max_sync100_duration
        ),
        "context_longest_synchronized_minus1000_seconds": (
            max_sync1000_duration
        ),
        "context_synchronized_timestamp_count": int(
            len(any_sync)
        ),
        "context_channel_minimum_range_uV": float(
            np.min(window_min)
        ),
        "context_channel_maximum_range_uV": float(
            np.max(window_max)
        ),
        "plot": str(plot_path.relative_to(ROOT)),
        "channels": ";".join(
            f"{item['channel']}:"
            f"-100={item['minus100_count']},"
            f"-1000={item['minus1000_count']},"
            f"longest100={item['minus100_longest_run']},"
            f"longest1000={item['minus1000_longest_run']}"
            for item in channel_details
        ),
    })

    print(
        f"  boundary span={summary_rows[-1]['boundary_span_seconds']:.3f}s "
        f"context -100={context100} "
        f"context -1000={context1000} "
        f"plot={plot_path.name}"
    )


def write_csv(path, rows):
    if not rows:
        return

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)


write_csv(
    OUT / "continuous_event_summary.csv",
    summary_rows
)

write_csv(
    OUT / "continuous_boundary_timestamps.csv",
    timestamp_rows
)

print("\n" + "=" * 76)
print("CONTINUOUS EVENT INSPECTION COMPLETE")
print("=" * 76)
print("Affected trials:", len(summary_rows))
print("Boundary timestamps:", len(timestamp_rows))
print("Plots:", PLOT_DIR)
print("Summary:", OUT / "continuous_event_summary.csv")
print("Timestamp detail:", OUT / "continuous_boundary_timestamps.csv")
print("Source data modified: no")
print("Trials excluded: no")
