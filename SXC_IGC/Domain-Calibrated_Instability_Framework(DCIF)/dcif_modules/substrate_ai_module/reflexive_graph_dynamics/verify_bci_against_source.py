from pathlib import Path
import numpy as np
import scipy.io

SOURCE = Path(
    "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
)
OUTPUT = Path("data/processed/bci_iv_2a_epochs_v1")

FS = 250
TMIN = 2
TMAX = 6

ORIGINAL_CHANNELS = [
    "C1", "C2", "C3", "C4", "C5", "C6",
    "CP1", "CP2", "CP3", "CP4", "CPz", "Cz",
    "EOG1", "EOG2", "EOG3",
    "FC1", "FC2", "FC3", "FC4", "FCz",
    "Fz", "P1", "P2", "POz", "Pz"
]

EEG_INDICES = [
    i for i, name in enumerate(ORIGINAL_CHANNELS)
    if not name.startswith("EOG")
]

EOG_INDICES = [
    i for i, name in enumerate(ORIGINAL_CHANNELS)
    if name.startswith("EOG")
]

def get_field(entry, name):
    return np.asarray(getattr(entry, name))

def load_entries(path):
    mat = scipy.io.loadmat(
        path,
        squeeze_me=True,
        struct_as_record=False
    )
    return np.atleast_1d(mat["data"]).ravel()

def main():
    session_files = sorted(OUTPUT.glob("*_epochs.npz"))

    total_trials = 0
    total_mismatches = 0
    max_difference = 0.0
    failed = []

    print("=" * 72)
    print("CORRECTED SOURCE-TO-EPOCH VERIFICATION")
    print("=" * 72)
    print("Original EEG indices:", EEG_INDICES)
    print("Original EOG indices:", EOG_INDICES)

    for npz_path in session_files:
        stem = npz_path.name.replace("_epochs.npz", "")
        mat_path = SOURCE / f"{stem}.mat"

        print(f"\n{stem}")

        try:
            entries = load_entries(mat_path)

            annotated = [
                entry for entry in entries
                if get_field(entry, "trial").size > 0
            ]

            reconstructed_eeg = []
            reconstructed_eog = []
            reconstructed_labels = []
            reconstructed_runs = []
            reconstructed_trials = []
            reconstructed_events = []

            for run_id, entry in enumerate(annotated, start=1):
                signal = get_field(entry, "X").astype(np.float32)
                markers = get_field(entry, "trial").ravel().astype(int)
                labels = get_field(entry, "y").ravel().astype(int)

                if signal.shape[1] != 25:
                    raise ValueError(
                        f"Unexpected source shape: {signal.shape}"
                    )

                for trial_id, (marker, label) in enumerate(
                    zip(markers, labels), start=1
                ):
                    event_index = marker - 1
                    start = event_index + TMIN * FS
                    stop = event_index + TMAX * FS

                    epoch = signal[start:stop]

                    if epoch.shape != (1000, 25):
                        raise ValueError(
                            f"Unexpected epoch shape: {epoch.shape}"
                        )

                    reconstructed_eeg.append(
                        epoch[:, EEG_INDICES].T.copy()
                    )
                    reconstructed_eog.append(
                        epoch[:, EOG_INDICES].T.copy()
                    )

                    reconstructed_labels.append(label)
                    reconstructed_runs.append(run_id)
                    reconstructed_trials.append(trial_id)
                    reconstructed_events.append(marker)

            reconstructed_eeg = np.asarray(
                reconstructed_eeg, dtype=np.float32
            )
            reconstructed_eog = np.asarray(
                reconstructed_eog, dtype=np.float32
            )

            with np.load(npz_path, allow_pickle=True) as saved:
                checks = {
                    "EEG": (
                        reconstructed_eeg,
                        saved["eeg_uV"]
                    ),
                    "EOG": (
                        reconstructed_eog,
                        saved["eog_uV"]
                    )
                }

                for name, (source, extracted) in checks.items():
                    if source.shape != extracted.shape:
                        raise ValueError(
                            f"{name} shape mismatch: "
                            f"{source.shape} vs {extracted.shape}"
                        )

                    difference = np.abs(
                        source.astype(np.float64)
                        - extracted.astype(np.float64)
                    )

                    mismatch_count = int(
                        np.count_nonzero(difference)
                    )
                    session_max = float(difference.max())

                    total_mismatches += mismatch_count
                    max_difference = max(
                        max_difference, session_max
                    )

                    print(
                        f"  {name}: mismatches={mismatch_count}, "
                        f"max_difference={session_max:.12g}"
                    )

                metadata_checks = [
                    (
                        "labels",
                        reconstructed_labels,
                        saved["labels"]
                    ),
                    (
                        "run IDs",
                        reconstructed_runs,
                        saved["run_ids"]
                    ),
                    (
                        "trial IDs",
                        reconstructed_trials,
                        saved["trial_ids"]
                    ),
                    (
                        "event markers",
                        reconstructed_events,
                        saved["event_samples_1based"]
                    )
                ]

                for name, source, extracted in metadata_checks:
                    if not np.array_equal(source, extracted):
                        raise ValueError(f"{name} mismatch")

                print("  Metadata: PASS")

            total_trials += len(reconstructed_eeg)

            if (
                np.array_equal(reconstructed_eeg, checks["EEG"][1])
                and np.array_equal(reconstructed_eog, checks["EOG"][1])
            ):
                print("  RESULT: EXACT SOURCE MATCH")
            else:
                print("  RESULT: NUMERIC MISMATCH")

        except Exception as exc:
            print("  RESULT: FAILED")
            print("  Error:", repr(exc))
            failed.append(stem)

    print("\n" + "=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    print("Sessions:", len(session_files))
    print("Trials:", total_trials)
    print("Total sample mismatches:", total_mismatches)
    print("Maximum absolute difference:", max_difference)
    print("Failed sessions:", failed)

    if not failed and total_mismatches == 0:
        print("FINAL RESULT: ALL SESSIONS MATCH SOURCE EXACTLY")
    else:
        print("FINAL RESULT: INVESTIGATION REQUIRED")

if __name__ == "__main__":
    main()
