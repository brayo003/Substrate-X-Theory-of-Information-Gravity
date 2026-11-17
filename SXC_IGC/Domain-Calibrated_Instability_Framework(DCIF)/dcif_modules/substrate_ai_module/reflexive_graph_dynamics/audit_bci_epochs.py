from pathlib import Path
import csv
import numpy as np

ROOT = Path("data/processed/bci_iv_2a_epochs_v1")

print("=" * 65)
print("BCI IV-2a EXTRACTED DATA AUDIT")
print("=" * 65)

files = sorted(ROOT.glob("*_epochs.npz"))
print("Session files:", len(files))

total_trials = 0

for path in files:
    print(f"\n{path.name}")

    with np.load(path, allow_pickle=True) as data:
        print("  Keys:", data.files)

        for key in data.files:
            arr = data[key]

            if arr.dtype.kind in "biuf":
                finite = np.isfinite(arr)
                finite_count = int(finite.sum())

                if finite_count:
                    values = arr[finite]
                    print(
                        f"  {key}: shape={arr.shape}, "
                        f"dtype={arr.dtype}, "
                        f"finite={finite_count}/{arr.size}, "
                        f"min={values.min():.6g}, "
                        f"max={values.max():.6g}, "
                        f"mean={values.mean():.6g}, "
                        f"std={values.std():.6g}"
                    )
                else:
                    print(f"  {key}: no finite values")

        if "eeg" in data:
            eeg = data["eeg"]
        elif "X_eeg" in data:
            eeg = data["X_eeg"]
        else:
            eeg = None

        if "labels" in data:
            labels = data["labels"]
        elif "y" in data:
            labels = data["y"]
        else:
            labels = None

        if eeg is not None:
            print("  EEG shape:", eeg.shape)
            print("  EEG finite:", np.isfinite(eeg).all())

        if labels is not None:
            labels = np.asarray(labels).ravel()
            print("  Labels:", dict(zip(*np.unique(labels, return_counts=True))))
            total_trials += len(labels)

print("\n" + "=" * 65)
print("TRIAL MANIFEST")
print("=" * 65)

manifest = ROOT / "trial_manifest.csv"

if manifest.exists():
    with manifest.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print("Rows:", len(rows))
        print("Columns:", reader.fieldnames)
        for row in rows[:5]:
            print(row)
else:
    print("Manifest missing")

print("\nTotal trials found in recognized label arrays:", total_trials)
