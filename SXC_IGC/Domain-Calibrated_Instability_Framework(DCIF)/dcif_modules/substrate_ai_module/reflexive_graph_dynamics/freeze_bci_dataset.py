from pathlib import Path
import hashlib
import json
import numpy as np
from datetime import datetime, timezone

ROOT = Path("data")
SOURCE = ROOT / "nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
PROCESSED = ROOT / "processed/bci_iv_2a_epochs_v1"
OUT = Path("bci_dataset_baseline_v1")

OUT.mkdir(exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

records = []

for path in sorted(SOURCE.glob("A*.mat")):
    record = {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "type": "source_mat",
    }
    records.append(record)

for path in sorted(PROCESSED.glob("*_epochs.npz")):
    with np.load(path, allow_pickle=True) as d:
        record = {
            "file": str(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "type": "processed_epochs",
            "eeg_shape": list(d["eeg_uV"].shape),
            "eog_shape": list(d["eog_uV"].shape),
            "trials": int(len(d["labels"])),
            "class_counts": {
                str(int(k)): int(v)
                for k, v in zip(*np.unique(d["labels"], return_counts=True))
            },
            "sampling_rate_hz": int(np.asarray(d["sampling_rate"]).item()),
        }
    records.append(record)

manifest = {
    "dataset": "BCI Competition IV-2a / BNCI2014-001",
    "baseline_version": "v1",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "verified_source_sessions": 14,
    "failed_source_sessions": ["A09E"],
    "processed_sessions": 14,
    "total_trials": 4032,
    "subjects": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08"],
    "paired_subjects": ["A01", "A02", "A03", "A04", "A05", "A08"],
    "e_only_subjects": ["A06", "A07"],
    "eeg_channels": 22,
    "eog_channels": 3,
    "sampling_rate_hz": 250,
    "epoch_interval_seconds": [2, 6],
    "epoch_samples": 1000,
    "source_to_epoch_sample_mismatches": 0,
    "files": records,
}

manifest_path = OUT / "manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

with (OUT / "SHA256SUMS").open("w") as f:
    for r in records:
        f.write(f'{r["sha256"]}  {r["file"]}\n')

print("Baseline frozen.")
print("Manifest:", manifest_path)
print("Checksum list:", OUT / "SHA256SUMS")
print("Files hashed:", len(records))
print("Source files:", sum(r["type"] == "source_mat" for r in records))
print("Processed files:", sum(r["type"] == "processed_epochs" for r in records))
print("Total processed trials:", sum(
    r.get("trials", 0) for r in records
))
