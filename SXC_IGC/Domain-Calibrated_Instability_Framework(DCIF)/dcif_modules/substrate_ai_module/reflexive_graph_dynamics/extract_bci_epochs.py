from pathlib import Path
import csv
import json
import numpy as np
import scipy.io

ROOT = Path("data/nm000139/data.nemar.org/nm000139/v1.0.3")
SOURCE = ROOT / "sourcedata"
OUTPUT = Path("data/processed/bci_iv_2a_epochs_v1")

FS_EXPECTED = 250
TMIN = 2
TMAX = 6

CHANNELS = [
    "C1", "C2", "C3", "C4", "C5", "C6",
    "CP1", "CP2", "CP3", "CP4", "CPz", "Cz",
    "EOG1", "EOG2", "EOG3",
    "FC1", "FC2", "FC3", "FC4", "FCz",
    "Fz", "P1", "P2", "POz", "Pz"
]

EEG_INDICES = [
    i for i, name in enumerate(CHANNELS)
    if not name.startswith("EOG")
]

EOG_INDICES = [
    i for i, name in enumerate(CHANNELS)
    if name.startswith("EOG")
]

CLASS_NAMES = {
    1: "left_hand",
    2: "right_hand",
    3: "feet",
    4: "tongue"
}

OUTPUT.mkdir(parents=True, exist_ok=True)

manifest = []
total_trials = 0
successful_sessions = 0
failed_files = []

files = sorted(SOURCE.glob("A??[TE].mat"))

print("BCI IV-2a EPOCH EXTRACTION")
print("=" * 65)
print("Source:", SOURCE.resolve())
print("Output:", OUTPUT.resolve())
print("Epoch:", f"{TMIN}-{TMAX} seconds relative to trial marker")
print("Sampling rate:", FS_EXPECTED)
print("EEG channels:", len(EEG_INDICES))
print("EOG channels:", len(EOG_INDICES))
print()

for file_path in files:
    print(f"Processing {file_path.name} ...")

    try:
        mat = scipy.io.loadmat(
            file_path,
            squeeze_me=True,
            struct_as_record=False
        )

        entries = np.atleast_1d(mat["data"])

        eeg_epochs = []
        eog_epochs = []
        labels = []
        run_ids = []
        trial_ids = []
        event_samples = []
        artifact_flags = []

        annotated_run_number = 0

        for entry in entries:
            trial_positions = np.asarray(
                entry.trial
            ).reshape(-1)

            run_labels = np.asarray(
                entry.y
            ).reshape(-1).astype(np.int64)

            if len(trial_positions) == 0:
                continue

            annotated_run_number += 1

            signal = np.asarray(entry.X, dtype=np.float32)
            fs = int(np.asarray(entry.fs).reshape(-1)[0])

            if fs != FS_EXPECTED:
                raise ValueError(
                    f"Unexpected sampling rate: {fs}"
                )

            if signal.ndim != 2 or signal.shape[1] != 25:
                raise ValueError(
                    f"Unexpected signal shape: {signal.shape}"
                )

            if len(trial_positions) != len(run_labels):
                raise ValueError("Trial/label count mismatch")

            if len(trial_positions) != 48:
                raise ValueError(
                    f"Expected 48 trials, found {len(trial_positions)}"
                )

            if set(np.unique(run_labels)) != {1, 2, 3, 4}:
                raise ValueError("Unexpected class labels")

            counts = np.bincount(run_labels, minlength=5)[1:5]

            if not np.all(counts == 12):
                raise ValueError(
                    f"Unexpected class distribution: {counts}"
                )

            if np.any(np.diff(trial_positions) <= 0):
                raise ValueError("Trial positions are not increasing")

            artifacts = np.asarray(
                getattr(entry, "artifacts", []),
            ).reshape(-1)

            if len(artifacts) == 0:
                artifacts = np.full(48, -1, dtype=np.int8)
            elif len(artifacts) != 48:
                raise ValueError("Artifact flag count mismatch")

            start_offset = TMIN * fs
            stop_offset = TMAX * fs

            for trial_index, (position, label) in enumerate(
                zip(trial_positions, run_labels),
                start=1
            ):
                # MATLAB 1-based sample position -> Python 0-based.
                event_index = int(position) - 1

                start = event_index + start_offset
                stop = event_index + stop_offset

                if start < 0 or stop > len(signal):
                    raise ValueError(
                        f"Epoch outside signal: {start}:{stop}"
                    )

                epoch = signal[start:stop, :]

                if epoch.shape != (1000, 25):
                    raise ValueError(
                        f"Unexpected epoch shape: {epoch.shape}"
                    )

                if not np.isfinite(epoch).all():
                    raise ValueError("Non-finite EEG values")

                eeg_epochs.append(
                    epoch[:, EEG_INDICES].T.copy()
                )

                eog_epochs.append(
                    epoch[:, EOG_INDICES].T.copy()
                )

                labels.append(int(label))
                run_ids.append(annotated_run_number)
                trial_ids.append(trial_index)
                event_samples.append(int(position))
                artifact_flags.append(int(artifacts[trial_index - 1]))

        if annotated_run_number != 6:
            raise ValueError(
                f"Expected 6 annotated runs, found {annotated_run_number}"
            )

        eeg_array = np.asarray(eeg_epochs, dtype=np.float32)
        eog_array = np.asarray(eog_epochs, dtype=np.float32)
        label_array = np.asarray(labels, dtype=np.int8)

        if eeg_array.shape != (288, 22, 1000):
            raise ValueError(
                f"Unexpected EEG output shape: {eeg_array.shape}"
            )

        if eog_array.shape != (288, 3, 1000):
            raise ValueError(
                f"Unexpected EOG output shape: {eog_array.shape}"
            )

        session_output = OUTPUT / f"{file_path.stem}_epochs.npz"

        np.savez_compressed(
            session_output,
            eeg_uV=eeg_array,
            eog_uV=eog_array,
            labels=label_array,
            run_ids=np.asarray(run_ids, dtype=np.int8),
            trial_ids=np.asarray(trial_ids, dtype=np.int8),
            event_samples_1based=np.asarray(
                event_samples, dtype=np.int32
            ),
            artifact_flags=np.asarray(
                artifact_flags, dtype=np.int8
            ),
            sampling_rate=np.int16(FS_EXPECTED),
            epoch_tmin=np.float32(TMIN),
            epoch_tmax=np.float32(TMAX),
            eeg_channel_names=np.asarray(
                [CHANNELS[i] for i in EEG_INDICES]
            ),
            eog_channel_names=np.asarray(
                [CHANNELS[i] for i in EOG_INDICES]
            ),
            class_names=np.asarray([
                CLASS_NAMES[i] for i in range(1, 5)
            ])
        )

        subject = file_path.stem[:3]
        session = file_path.stem[-1]

        for i in range(288):
            manifest.append({
                "subject": subject,
                "session": session,
                "run": int(run_ids[i]),
                "trial": int(trial_ids[i]),
                "label": int(label_array[i]),
                "class_name": CLASS_NAMES[int(label_array[i])],
                "event_sample_1based": int(event_samples[i]),
                "artifact_flag": int(artifact_flags[i]),
                "epoch_tmin": TMIN,
                "epoch_tmax": TMAX,
                "sampling_rate": FS_EXPECTED,
                "units": "microvolts",
                "file": session_output.name
            })

        total_trials += len(label_array)
        successful_sessions += 1

        print("  PASS")
        print("  Runs:", annotated_run_number)
        print("  Trials:", len(label_array))
        print("  EEG:", eeg_array.shape)
        print("  EOG:", eog_array.shape)
        print("  Saved:", session_output.name)

    except Exception as error:
        failed_files.append((file_path.name, str(error)))
        print("  EXCLUDED:", repr(error))

manifest_path = OUTPUT / "trial_manifest.csv"

if manifest:
    with open(manifest_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(manifest[0].keys())
        )
        writer.writeheader()
        writer.writerows(manifest)

summary = {
    "dataset": "BNCI2014-001 / BCI Competition IV-2a",
    "successful_sessions": successful_sessions,
    "total_trials": total_trials,
    "sampling_rate_hz": FS_EXPECTED,
    "epoch_interval_seconds": [TMIN, TMAX],
    "epoch_samples": (TMAX - TMIN) * FS_EXPECTED,
    "eeg_channels": 22,
    "eog_channels": 3,
    "signal_units": "microvolts",
    "class_mapping": CLASS_NAMES,
    "failed_files": [
        {"file": name, "error": error}
        for name, error in failed_files
    ]
}

with open(OUTPUT / "extraction_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 65)
print("EXTRACTION SUMMARY")
print("=" * 65)
print(json.dumps(summary, indent=2))
print("\nManifest:", manifest_path.resolve())
print("Output directory:", OUTPUT.resolve())
