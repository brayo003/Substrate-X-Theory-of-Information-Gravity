#!/usr/bin/env python3

from pathlib import Path
from collections import Counter, defaultdict
import importlib.util
import csv
import json

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]

SOURCE = (
    ROOT
    / "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
)

OUT = (
    ROOT
    / "bci_evidence_experiment/results/source_boundary_audit"
)
OUT.mkdir(parents=True, exist_ok=True)

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

# Primary paired cohort only.
SUBJECTS = ["A01", "A02", "A03", "A04", "A05", "A08"]
SESSIONS = [
    f"{subject}{session}"
    for subject in SUBJECTS
    for session in ("T", "E")
]

FS = 250
EPOCH_START_SECONDS = 2
EPOCH_STOP_SECONDS = 6

BOUNDARY_VALUES = (-100.0, -1000.0)
BOUNDARY_ATOL = 1e-7
EXTREME_THRESHOLD_UV = 90.0

run_channel_rows = []
trial_rows = []
trial_channel_rows = []

session_summaries = []
other_extreme_counter = Counter()
other_extreme_locations = defaultdict(set)
other_extreme_sessions = defaultdict(set)
other_extreme_channels = defaultdict(set)

cohort = {
    "sessions": 0,
    "runs": 0,
    "trials": 0,
    "source_samples_per_channel": 0,
    "source_boundary_minus100": 0,
    "source_boundary_minus1000": 0,
    "source_samples_abs_ge_90": 0,
    "trials_with_minus100": 0,
    "trials_with_minus1000": 0,
    "trials_with_any_boundary": 0,
    "trials_with_synchronized_minus100": 0,
    "trials_with_synchronized_minus1000": 0,
}

def exact_mask(values, target):
    return np.isclose(
        values,
        target,
        rtol=0.0,
        atol=BOUNDARY_ATOL
    )


def longest_true_run(mask):
    """Length of longest consecutive True sequence."""
    mask = np.asarray(mask, dtype=bool)

    if mask.size == 0 or not np.any(mask):
        return 0

    padded = np.concatenate(([False], mask, [False]))
    changes = np.diff(padded.astype(np.int8))

    starts = np.flatnonzero(changes == 1)
    stops = np.flatnonzero(changes == -1)

    return int(np.max(stops - starts))


def count_true_runs(mask):
    """Number of separate consecutive True sequences."""
    mask = np.asarray(mask, dtype=bool)

    if mask.size == 0:
        return 0

    padded = np.concatenate(([False], mask, [False]))
    changes = np.diff(padded.astype(np.int8))

    return int(np.sum(changes == 1))


def write_csv(path, rows):
    if not rows:
        print("No rows for:", path.name)
        return

    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)


for session in SESSIONS:
    mat_path = SOURCE / f"{session}.mat"

    if not mat_path.exists():
        raise FileNotFoundError(
            f"Required primary-cohort source missing: {mat_path}"
        )

    print(f"\nProcessing {session} ...")

    mat = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False
    )

    entries = builder.get_run_entries(mat)

    if len(entries) != 6:
        raise ValueError(
            f"{session}: expected 6 annotated runs, found {len(entries)}"
        )

    session_totals = {
        "session": session,
        "runs": 0,
        "trials": 0,
        "continuous_samples_per_channel": 0,
        "continuous_minus100": 0,
        "continuous_minus1000": 0,
        "continuous_abs_ge_90": 0,
        "trials_with_minus100": 0,
        "trials_with_minus1000": 0,
        "trials_with_any_boundary": 0,
        "trials_with_synchronized_minus100": 0,
        "trials_with_synchronized_minus1000": 0,
        "max_simultaneous_minus100_channels": 0,
        "max_simultaneous_minus1000_channels": 0,
    }

    global_trial_index = 0

    for run_number, entry in enumerate(entries, start=1):
        x = builder.continuous_samples_by_channels(
            entry.X,
            session,
            run_number
        )

        fs = int(round(float(builder.scalar(entry.fs))))

        if fs != FS:
            raise ValueError(
                f"{session} run {run_number}: unexpected sampling rate {fs}"
            )

        eeg = np.asarray(
            x[:, builder.EEG_INDICES],
            dtype=np.float64
        ).T

        channels = [
            str(name) for name in builder.CHANNEL_NAMES
        ]

        if eeg.shape[0] != len(channels):
            raise ValueError(
                f"{session} run {run_number}: channel count mismatch"
            )

        positions = np.asarray(entry.trial).reshape(-1).astype(int)
        labels = np.asarray(entry.y).reshape(-1).astype(int)

        artifacts_value = getattr(entry, "artifacts", None)

        if artifacts_value is None or np.asarray(artifacts_value).size == 0:
            artifacts = np.zeros(len(positions), dtype=int)
        else:
            artifacts = (
                np.asarray(artifacts_value).reshape(-1).astype(int)
            )

        if not (
            len(positions) == len(labels) == len(artifacts) == 48
        ):
            raise ValueError(
                f"{session} run {run_number}: annotation length mismatch"
            )

        # Audit the entire continuous run.
        run_minus100_masks = exact_mask(eeg, -100.0)
        run_minus1000_masks = exact_mask(eeg, -1000.0)

        run_minus100_count = int(np.sum(run_minus100_masks))
        run_minus1000_count = int(np.sum(run_minus1000_masks))
        run_extreme_count = int(
            np.sum(np.abs(eeg) >= EXTREME_THRESHOLD_UV)
        )

        simultaneous_100 = np.sum(
            run_minus100_masks, axis=0
        )
        simultaneous_1000 = np.sum(
            run_minus1000_masks, axis=0
        )

        run_max_sim_100 = int(np.max(simultaneous_100))
        run_max_sim_1000 = int(np.max(simultaneous_1000))

        run_timepoints_2plus_100 = int(
            np.sum(simultaneous_100 >= 2)
        )
        run_timepoints_3plus_100 = int(
            np.sum(simultaneous_100 >= 3)
        )
        run_timepoints_2plus_1000 = int(
            np.sum(simultaneous_1000 >= 2)
        )

        session_totals["runs"] += 1
        session_totals["continuous_samples_per_channel"] += eeg.shape[1]
        session_totals["continuous_minus100"] += run_minus100_count
        session_totals["continuous_minus1000"] += run_minus1000_count
        session_totals["continuous_abs_ge_90"] += run_extreme_count
        session_totals["max_simultaneous_minus100_channels"] = max(
            session_totals["max_simultaneous_minus100_channels"],
            run_max_sim_100
        )
        session_totals["max_simultaneous_minus1000_channels"] = max(
            session_totals["max_simultaneous_minus1000_channels"],
            run_max_sim_1000
        )

        cohort["runs"] += 1
        cohort["source_samples_per_channel"] += eeg.shape[1]
        cohort["source_boundary_minus100"] += run_minus100_count
        cohort["source_boundary_minus1000"] += run_minus1000_count
        cohort["source_samples_abs_ge_90"] += run_extreme_count

        for ci, channel in enumerate(channels):
            signal = eeg[ci]

            mask100 = run_minus100_masks[ci]
            mask1000 = run_minus1000_masks[ci]

            run_channel_rows.append({
                "session": session,
                "run": run_number,
                "channel": channel,
                "continuous_samples": int(signal.size),
                "minimum_uV": float(np.min(signal)),
                "maximum_uV": float(np.max(signal)),
                "maximum_absolute_uV": float(np.max(np.abs(signal))),
                "count_exact_minus100": int(np.sum(mask100)),
                "count_exact_minus1000": int(np.sum(mask1000)),
                "count_abs_ge_90": int(
                    np.sum(np.abs(signal) >= EXTREME_THRESHOLD_UV)
                ),
                "minus100_consecutive_sequences": count_true_runs(mask100),
                "minus100_longest_sequence": longest_true_run(mask100),
                "minus1000_consecutive_sequences": count_true_runs(mask1000),
                "minus1000_longest_sequence": longest_true_run(mask1000),
            })

        # Record repeated extreme values other than the two target boundaries.
        other_mask = (
            (np.abs(eeg) >= EXTREME_THRESHOLD_UV)
            & (~run_minus100_masks)
            & (~run_minus1000_masks)
        )

        other_values = eeg[other_mask]

        if other_values.size:
            values, counts = np.unique(
                np.round(other_values, 8),
                return_counts=True
            )

            for value, count in zip(values, counts):
                key = float(value)
                other_extreme_counter[key] += int(count)
                other_extreme_sessions[key].add(session)

            for ci, channel in enumerate(channels):
                channel_values = eeg[ci][other_mask[ci]]
                for value in np.unique(np.round(channel_values, 8)):
                    other_extreme_channels[float(value)].add(channel)

        # Audit all 48 epochs in this run.
        for trial_within_run, (position, label, artifact) in enumerate(
            zip(positions, labels, artifacts),
            start=1
        ):
            global_trial_index += 1

            event_index = int(position) - 1
            start = event_index + EPOCH_START_SECONDS * fs
            stop = event_index + EPOCH_STOP_SECONDS * fs

            if start < 0 or stop > eeg.shape[1]:
                raise ValueError(
                    f"{session} run {run_number} trial "
                    f"{trial_within_run}: epoch outside continuous run"
                )

            epoch = eeg[:, start:stop]

            if epoch.shape != (len(channels), 1000):
                raise ValueError(
                    f"{session} run {run_number} trial "
                    f"{trial_within_run}: unexpected epoch shape {epoch.shape}"
                )

            mask100 = exact_mask(epoch, -100.0)
            mask1000 = exact_mask(epoch, -1000.0)

            total100 = int(np.sum(mask100))
            total1000 = int(np.sum(mask1000))

            sim100 = np.sum(mask100, axis=0)
            sim1000 = np.sum(mask1000, axis=0)

            max_sim100 = int(np.max(sim100))
            max_sim1000 = int(np.max(sim1000))

            timepoints_2plus_100 = int(np.sum(sim100 >= 2))
            timepoints_3plus_100 = int(np.sum(sim100 >= 3))
            timepoints_10plus_100 = int(np.sum(sim100 >= 10))

            timepoints_2plus_1000 = int(np.sum(sim1000 >= 2))

            trial_has_100 = total100 > 0
            trial_has_1000 = total1000 > 0
            trial_has_boundary = trial_has_100 or trial_has_1000

            synchronized_100 = timepoints_2plus_100 > 0
            synchronized_1000 = timepoints_2plus_1000 > 0

            if trial_has_100:
                session_totals["trials_with_minus100"] += 1
                cohort["trials_with_minus100"] += 1

            if trial_has_1000:
                session_totals["trials_with_minus1000"] += 1
                cohort["trials_with_minus1000"] += 1

            if trial_has_boundary:
                session_totals["trials_with_any_boundary"] += 1
                cohort["trials_with_any_boundary"] += 1

            if synchronized_100:
                session_totals[
                    "trials_with_synchronized_minus100"
                ] += 1
                cohort["trials_with_synchronized_minus100"] += 1

            if synchronized_1000:
                session_totals[
                    "trials_with_synchronized_minus1000"
                ] += 1
                cohort["trials_with_synchronized_minus1000"] += 1

            session_totals["max_simultaneous_minus100_channels"] = max(
                session_totals["max_simultaneous_minus100_channels"],
                max_sim100
            )
            session_totals["max_simultaneous_minus1000_channels"] = max(
                session_totals["max_simultaneous_minus1000_channels"],
                max_sim1000
            )

            trial_rows.append({
                "session": session,
                "global_trial_index": global_trial_index - 1,
                "run": run_number,
                "trial_within_run": trial_within_run,
                "event_sample_1based": int(position),
                "label": int(label),
                "artifact_flag": int(artifact),
                "epoch_samples": int(epoch.shape[1]),
                "count_exact_minus100_all_channels": total100,
                "count_exact_minus1000_all_channels": total1000,
                "count_abs_ge_90_all_channels": int(
                    np.sum(np.abs(epoch) >= EXTREME_THRESHOLD_UV)
                ),
                "channels_with_minus100": int(
                    np.sum(np.sum(mask100, axis=1) > 0)
                ),
                "channels_with_minus1000": int(
                    np.sum(np.sum(mask1000, axis=1) > 0)
                ),
                "max_simultaneous_minus100_channels": max_sim100,
                "timepoints_with_2plus_minus100_channels": timepoints_2plus_100,
                "timepoints_with_3plus_minus100_channels": timepoints_3plus_100,
                "timepoints_with_10plus_minus100_channels": timepoints_10plus_100,
                "max_simultaneous_minus1000_channels": max_sim1000,
                "timepoints_with_2plus_minus1000_channels": timepoints_2plus_1000,
                "has_minus100": int(trial_has_100),
                "has_minus1000": int(trial_has_1000),
                "has_any_boundary": int(trial_has_boundary),
                "synchronized_minus100": int(synchronized_100),
                "synchronized_minus1000": int(synchronized_1000),
            })

            for ci, channel in enumerate(channels):
                signal = epoch[ci]
                m100 = mask100[ci]
                m1000 = mask1000[ci]

                trial_channel_rows.append({
                    "session": session,
                    "global_trial_index": global_trial_index - 1,
                    "run": run_number,
                    "trial_within_run": trial_within_run,
                    "channel": channel,
                    "artifact_flag": int(artifact),
                    "minimum_uV": float(np.min(signal)),
                    "maximum_uV": float(np.max(signal)),
                    "maximum_absolute_uV": float(
                        np.max(np.abs(signal))
                    ),
                    "count_exact_minus100": int(np.sum(m100)),
                    "count_exact_minus1000": int(np.sum(m1000)),
                    "count_abs_ge_90": int(
                        np.sum(np.abs(signal) >= EXTREME_THRESHOLD_UV)
                    ),
                    "minus100_consecutive_sequences": count_true_runs(m100),
                    "minus100_longest_sequence": longest_true_run(m100),
                    "minus1000_consecutive_sequences": count_true_runs(m1000),
                    "minus1000_longest_sequence": longest_true_run(m1000),
                })

            session_totals["trials"] += 1
            cohort["trials"] += 1

    session_totals["sessions"] = 1
    session_summaries.append(session_totals)

    print(
        f"  runs={session_totals['runs']} "
        f"trials={session_totals['trials']} "
        f"-100={session_totals['continuous_minus100']} "
        f"-1000={session_totals['continuous_minus1000']} "
        f"trials_with_boundary={session_totals['trials_with_any_boundary']}"
    )

    cohort["sessions"] += 1

# Write detailed reports.
write_csv(
    OUT / "continuous_run_channel_boundary_audit.csv",
    run_channel_rows
)

write_csv(
    OUT / "trial_boundary_audit.csv",
    trial_rows
)

write_csv(
    OUT / "trial_channel_boundary_audit.csv",
    trial_channel_rows
)

write_csv(
    OUT / "session_boundary_summary.csv",
    session_summaries
)

# Rank repeated non-boundary extreme values.
other_rows = []

for value, count in other_extreme_counter.most_common(200):
    other_rows.append({
        "value_uV": value,
        "total_occurrences": count,
        "number_of_sessions": len(other_extreme_sessions[value]),
        "sessions": ";".join(sorted(other_extreme_sessions[value])),
        "channels": ";".join(sorted(other_extreme_channels[value])),
    })

write_csv(
    OUT / "repeated_other_extreme_values.csv",
    other_rows
)

# Final consistency checks.
expected_trials = 12 * 6 * 48
expected_runs = 12 * 6

if cohort["trials"] != expected_trials:
    raise RuntimeError(
        f"Expected {expected_trials} trials, got {cohort['trials']}"
    )

if cohort["runs"] != expected_runs:
    raise RuntimeError(
        f"Expected {expected_runs} runs, got {cohort['runs']}"
    )

summary = {
    "audit": "BCI IV-2a primary cohort source boundary prevalence",
    "source_data": "Original continuous MAT X arrays",
    "cohort_subjects": SUBJECTS,
    "cohort_sessions": SESSIONS,
    "sessions": cohort["sessions"],
    "annotated_runs": cohort["runs"],
    "trials": cohort["trials"],
    "channels_per_trial": len(builder.CHANNEL_NAMES),
    "sampling_rate_hz": FS,
    "epoch_window_seconds_after_marker": [
        EPOCH_START_SECONDS,
        EPOCH_STOP_SECONDS
    ],
    "extreme_threshold_absolute_uV": EXTREME_THRESHOLD_UV,
    "boundary_match_atol_uV": BOUNDARY_ATOL,
    "cohort_totals": cohort,
    "definitions": {
        "minus100": "Samples numerically equal to -100 uV within stated tolerance",
        "minus1000": "Samples numerically equal to -1000 uV within stated tolerance",
        "synchronized_minus100": "At least two EEG channels equal -100 uV at the same sample",
        "synchronized_minus1000": "At least two EEG channels equal -1000 uV at the same sample",
        "other_extreme_values": "Exact repeated values with absolute amplitude >=90 uV, excluding -100 and -1000 uV",
        "consecutive_sequence": "Adjacent samples in one channel matching the same exact boundary value",
    },
    "files": [
        "continuous_run_channel_boundary_audit.csv",
        "trial_boundary_audit.csv",
        "trial_channel_boundary_audit.csv",
        "session_boundary_summary.csv",
        "repeated_other_extreme_values.csv",
    ],
    "data_mutated": False,
    "trials_excluded": 0,
}

summary_path = OUT / "source_boundary_audit_summary.json"
summary_path.write_text(json.dumps(summary, indent=2) + "\n")

print("\n" + "=" * 78)
print("SOURCE BOUNDARY AUDIT COMPLETE")
print("=" * 78)
print(json.dumps(cohort, indent=2))
print("\nOutput directory:", OUT)
print("Summary:", summary_path)
