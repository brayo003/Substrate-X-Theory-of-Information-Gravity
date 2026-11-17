#!/usr/bin/env python3
"""Build an additional 8–30 Hz BCI IV-2a epoch set from continuous source MATs.

The frozen acquisition-filtered baseline is read-only and is never modified.
Filtering is performed on each continuous run before trial epoch extraction.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.io import loadmat
from scipy.signal import butter, sosfiltfilt

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
OUTPUT_DIR = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
LOG_DIR = ROOT / "bci_evidence_experiment/results"
LOG_PATH = LOG_DIR / "bci_8_30hz_preprocessing.log"
MANIFEST_PATH = OUTPUT_DIR / "preprocessing_manifest.json"

FS_EXPECTED = 250
TMIN_SECONDS = 2
TMAX_SECONDS = 6
LOW_HZ = 8.0
HIGH_HZ = 30.0
FILTER_ORDER = 4
EXPECTED_RUNS = 6
EXPECTED_TRIALS_PER_RUN = 48
EXPECTED_CHANNELS = 25
EXPECTED_EEG_CHANNELS = 22
EXPECTED_EOG_CHANNELS = 3
EXPECTED_SAMPLES_PER_EPOCH = (TMAX_SECONDS - TMIN_SECONDS) * FS_EXPECTED

# Source order: C1,C2,C3,C4,C5,C6,CP1,CP2,CP3,CP4,CPz,Cz,
# EOG1,EOG2,EOG3,FC1,FC2,FC3,FC4,FCz,Fz,P1,P2,POz,Pz
EEG_INDICES = np.array(list(range(12)) + list(range(15, 25)), dtype=int)
EOG_INDICES = np.array([12, 13, 14], dtype=int)

CHANNEL_NAMES = np.array([
    "C1", "C2", "C3", "C4", "C5", "C6",
    "CP1", "CP2", "CP3", "CP4", "CPz", "Cz",
    "FC1", "FC2", "FC3", "FC4", "FCz", "Fz",
    "P1", "P2", "POz", "Pz",
])
EOG_NAMES = np.array(["EOG1", "EOG2", "EOG3"])
CLASS_NAMES = np.array(["left_hand", "right_hand", "feet", "tongue"])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scalar(value):
    arr = np.asarray(value).squeeze()
    if arr.size != 1:
        raise ValueError(f"Expected scalar metadata, received shape {np.asarray(value).shape}")
    return arr.item()


def vector(value, name: str) -> np.ndarray:
    arr = np.asarray(value).squeeze()
    if arr.ndim == 0:
        arr = arr.reshape(1)
    return arr.reshape(-1)


def continuous_samples_by_channels(value, session_name: str, run_number: int) -> np.ndarray:
    """Normalize source X to samples × 25 channels; reject ambiguous shapes."""
    x = np.asarray(value)
    if x.ndim != 2:
        raise ValueError(
            f"{session_name} run {run_number}: X must be 2-D; got {x.shape}"
        )

    if x.shape[1] == EXPECTED_CHANNELS:
        pass
    elif x.shape[0] == EXPECTED_CHANNELS:
        x = x.T
    else:
        raise ValueError(
            f"{session_name} run {run_number}: cannot identify 25-channel axis in {x.shape}"
        )

    if x.shape[0] < EXPECTED_SAMPLES_PER_EPOCH + FS_EXPECTED:
        raise ValueError(
            f"{session_name} run {run_number}: implausibly short recording {x.shape}"
        )
    if not np.isfinite(x).all():
        raise ValueError(
            f"{session_name} run {run_number}: source recording contains non-finite values"
        )
    return np.asarray(x, dtype=np.float64)


def get_run_entries(mat: dict):
    if "data" not in mat:
        raise KeyError("MAT file has no 'data' variable")

    entries = np.asarray(mat["data"], dtype=object).reshape(-1)
    annotated = []
    skipped_unannotated = []

    for source_index, entry in enumerate(entries, start=1):
        trial_value = getattr(entry, "trial", None)
        label_value = getattr(entry, "y", None)
        x_value = getattr(entry, "X", None)

        if trial_value is None or label_value is None or x_value is None:
            raise ValueError(
                f"Entry {source_index}: missing X, trial, or y"
            )

        n_trials = np.asarray(trial_value).size
        n_labels = np.asarray(label_value).size

        if n_trials == 0 and n_labels == 0:
            skipped_unannotated.append(source_index)
            continue

        if (
            n_trials != EXPECTED_TRIALS_PER_RUN
            or n_labels != EXPECTED_TRIALS_PER_RUN
        ):
            raise ValueError(
                f"Entry {source_index}: malformed annotations "
                f"(trials={n_trials}, labels={n_labels})"
            )

        annotated.append(entry)

    if len(annotated) != EXPECTED_RUNS:
        raise ValueError(
            f"Expected {EXPECTED_RUNS} annotated runs, found {len(annotated)} "
            f"among {len(entries)} entries"
        )

    logging.info(
        "Selected %d annotated runs; skipped unannotated entries %s",
        len(annotated),
        skipped_unannotated
    )

    return annotated


def process_session(mat_path: Path, sos: np.ndarray) -> dict:
    session_name = mat_path.stem
    mat = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    entries = get_run_entries(mat)

    eeg_epochs = []
    eog_epochs = []
    labels = []
    run_ids = []
    trial_ids = []
    event_samples_1based = []
    artifact_flags = []
    missing_artifact_runs = []

    for run_number, entry in enumerate(entries, start=1):
        fs = int(round(float(scalar(entry.fs))))
        if fs != FS_EXPECTED:
            raise ValueError(
                f"{session_name} run {run_number}: expected {FS_EXPECTED} Hz, got {fs}"
            )

        x = continuous_samples_by_channels(entry.X, session_name, run_number)

        # Filter continuous EEG channels before slicing trials.
        # EOG channels are retained in their original acquisition-filtered form.
        eeg_continuous = sosfiltfilt(sos, x[:, EEG_INDICES], axis=0)
        eog_continuous = x[:, EOG_INDICES]

        positions = vector(entry.trial, "trial")
        run_labels = vector(entry.y, "y").astype(int)

        if len(positions) != EXPECTED_TRIALS_PER_RUN:
            raise ValueError(
                f"{session_name} run {run_number}: expected "
                f"{EXPECTED_TRIALS_PER_RUN} trial positions, got {len(positions)}"
            )
        if len(run_labels) != len(positions):
            raise ValueError(
                f"{session_name} run {run_number}: trial/label count mismatch"
            )

        if hasattr(entry, "artifacts"):
            run_artifacts = vector(entry.artifacts, "artifacts").astype(int)
            if len(run_artifacts) != len(positions):
                raise ValueError(
                    f"{session_name} run {run_number}: artifact/trial count mismatch"
                )
        else:
            run_artifacts = np.zeros(len(positions), dtype=int)
            missing_artifact_runs.append(run_number)

        for trial_index, (position, label, artifact) in enumerate(
            zip(positions, run_labels, run_artifacts), start=1
        ):
            # Source trial positions are MATLAB 1-based sample indices.
            event_index = int(position) - 1
            start = event_index + TMIN_SECONDS * fs
            stop = event_index + TMAX_SECONDS * fs

            if start < 0 or stop > len(x):
                raise ValueError(
                    f"{session_name} run {run_number} trial {trial_index}: "
                    f"epoch [{start}:{stop}] outside recording length {len(x)}"
                )

            eeg_epoch = eeg_continuous[start:stop, :].T
            eog_epoch = eog_continuous[start:stop, :].T

            if eeg_epoch.shape != (EXPECTED_EEG_CHANNELS, EXPECTED_SAMPLES_PER_EPOCH):
                raise ValueError(
                    f"{session_name} run {run_number} trial {trial_index}: "
                    f"unexpected EEG epoch shape {eeg_epoch.shape}"
                )
            if eog_epoch.shape != (EXPECTED_EOG_CHANNELS, EXPECTED_SAMPLES_PER_EPOCH):
                raise ValueError(
                    f"{session_name} run {run_number} trial {trial_index}: "
                    f"unexpected EOG epoch shape {eog_epoch.shape}"
                )
            if int(label) not in (1, 2, 3, 4):
                raise ValueError(
                    f"{session_name} run {run_number} trial {trial_index}: "
                    f"unexpected class label {label}"
                )

            eeg_epochs.append(eeg_epoch.astype(np.float32))
            eog_epochs.append(eog_epoch.astype(np.float32))
            labels.append(int(label))
            run_ids.append(run_number)
            trial_ids.append(trial_index)
            event_samples_1based.append(int(position))
            artifact_flags.append(int(artifact))

    result = {
        "eeg_uV": np.stack(eeg_epochs),
        "eog_uV": np.stack(eog_epochs),
        "labels": np.asarray(labels, dtype=np.int8),
        "run_ids": np.asarray(run_ids, dtype=np.int8),
        "trial_ids": np.asarray(trial_ids, dtype=np.int8),
        "event_samples_1based": np.asarray(event_samples_1based, dtype=np.int64),
        "artifact_flags": np.asarray(artifact_flags, dtype=np.int8),
        "sampling_rate": np.asarray(FS_EXPECTED, dtype=np.int16),
        "epoch_tmin": np.asarray(TMIN_SECONDS, dtype=np.float32),
        "epoch_tmax": np.asarray(TMAX_SECONDS, dtype=np.float32),
        "channel_names": CHANNEL_NAMES,
        "eog_channel_names": EOG_NAMES,
        "class_names": CLASS_NAMES,
        "units": np.asarray("microvolts"),
        "preprocessing_filter": np.asarray("4th-order Butterworth band-pass 8-30 Hz"),
        "filter_application": np.asarray("continuous run, before epoch extraction"),
        "filter_phase": np.asarray("zero-phase forward-backward SOS"),
        "source_mat": np.asarray(mat_path.name),
    }

    if result["eeg_uV"].shape[0] != EXPECTED_RUNS * EXPECTED_TRIALS_PER_RUN:
        raise ValueError(
            f"{session_name}: expected 288 epochs, got {result['eeg_uV'].shape[0]}"
        )

    metadata = {
        "session": session_name,
        "source_file": mat_path.name,
        "source_sha256": sha256(mat_path),
        "output_file": f"{session_name}.npz",
        "trials": int(len(labels)),
        "runs": EXPECTED_RUNS,
        "class_counts": {
            str(k): int(np.sum(result["labels"] == k)) for k in (1, 2, 3, 4)
        },
        "artifact_flagged_trials": int(np.sum(result["artifact_flags"] != 0)),
        "missing_artifact_metadata_runs": missing_artifact_runs,
        "eeg_shape": list(result["eeg_uV"].shape),
        "eog_shape": list(result["eog_uV"].shape),
    }
    return result, metadata


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    if not SOURCE_DIR.is_dir():
        logging.error("Source directory does not exist: %s", SOURCE_DIR)
        return 2

    sos = butter(
        FILTER_ORDER,
        [LOW_HZ, HIGH_HZ],
        btype="bandpass",
        fs=FS_EXPECTED,
        output="sos",
    )

    source_files = sorted(SOURCE_DIR.glob("A??[TE].mat"))
    if not source_files:
        logging.error("No session MAT files found in %s", SOURCE_DIR)
        return 2

    session_records = []
    failures = []

    for mat_path in source_files:
        try:
            logging.info("Processing %s", mat_path.name)
            arrays, record = process_session(mat_path, sos)
            output_path = OUTPUT_DIR / f"{mat_path.stem}.npz"
            np.savez_compressed(output_path, **arrays)
            record["output_sha256"] = sha256(output_path)
            session_records.append(record)
            logging.info(
                "PASS %s: %d trials; EEG %s; artifact flags %d",
                mat_path.stem,
                record["trials"],
                record["eeg_shape"],
                record["artifact_flagged_trials"],
            )
        except Exception as exc:
            failures.append({
                "source_file": mat_path.name,
                "error_type": type(exc).__name__,
                "error": str(exc),
            })
            logging.exception("FAILED %s", mat_path.name)

    manifest = {
        "dataset": "BCI Competition IV-2a / BNCI2014-001",
        "pipeline_version": "bci_8_30hz_continuous_filter_v1",
        "sampling_rate_hz": FS_EXPECTED,
        "epoch_window_seconds_relative_to_source_trial_marker": [
            TMIN_SECONDS, TMAX_SECONDS
        ],
        "filter": {
            "type": "Butterworth band-pass",
            "order": FILTER_ORDER,
            "low_hz": LOW_HZ,
            "high_hz": HIGH_HZ,
            "representation": "second-order sections",
            "application": "continuous recording, independently per annotated run",
            "phase": "zero-phase forward-backward (sosfiltfilt)",
            "filtered_channels": "22 EEG channels only",
            "unfiltered_channels": "3 EOG channels",
        },
        "normalization": "none at this stage",
        "rereferencing": "none at this stage",
        "resampling": "none",
        "artifact_policy": "retain every trial and preserve source artifact flags",
        "source_directory": str(SOURCE_DIR),
        "output_directory": str(OUTPUT_DIR),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "successful_sessions": session_records,
        "failed_sessions": failures,
        "success_count": len(session_records),
        "failure_count": len(failures),
        "expected_readable_sessions": 14,
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    logging.info(
        "Finished: %d successful sessions, %d failed sessions",
        len(session_records), len(failures)
    )
    logging.info("Manifest: %s", MANIFEST_PATH)
    logging.info("Log: %s", LOG_PATH)

    # A failed/corrupt source (known A09E) is recorded, not silently accepted.
    if len(session_records) != 14:
        logging.error("Expected 14 readable sessions; produced %d", len(session_records))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
