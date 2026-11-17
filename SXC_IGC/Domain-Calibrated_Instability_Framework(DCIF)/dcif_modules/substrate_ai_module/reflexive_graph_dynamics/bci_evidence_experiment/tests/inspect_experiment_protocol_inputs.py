from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path.cwd()

FILTERED_DIR = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
BASELINE_DIR = ROOT / "data/processed/bci_iv_2a_epochs_v1"
QC_FILE = ROOT / "bci_evidence_experiment/results/final_qc_register/boundary_contamination_register.csv"
MANIFEST_CANDIDATES = [
    ROOT / "data/processed/bci_iv_2a_epochs_v1/trial_manifest.csv",
    ROOT / "data/processed/trial_manifest.csv",
    ROOT / "bci_evidence_experiment/results/trial_manifest.csv",
]

print("=" * 72)
print("SUBSTRATE AI — EXPERIMENT PROTOCOL INPUT INSPECTION")
print("=" * 72)

# 1. Filtered NPZ inventory and schemas.
print("\n[1] FILTERED DATASET")
if not FILTERED_DIR.exists():
    raise FileNotFoundError(FILTERED_DIR)

npz_files = sorted(FILTERED_DIR.glob("*.npz"))
print("Directory:", FILTERED_DIR)
print("NPZ files:", len(npz_files))

for path in npz_files:
    print(f"\n{path.name}")
    with np.load(path, allow_pickle=True) as data:
        for key in data.files:
            arr = data[key]
            print(
                f"  {key}: shape={arr.shape}, "
                f"dtype={arr.dtype}"
            )

# 2. Baseline inventory.
print("\n[2] BASELINE DATASET")
baseline_files = sorted(BASELINE_DIR.glob("*.npz"))
print("Directory:", BASELINE_DIR)
print("NPZ files:", len(baseline_files))

if baseline_files:
    with np.load(baseline_files[0], allow_pickle=True) as data:
        print("Example:", baseline_files[0].name)
        for key in data.files:
            arr = data[key]
            print(f"  {key}: shape={arr.shape}, dtype={arr.dtype}")

# 3. Trial manifest discovery.
print("\n[3] TRIAL MANIFEST")
manifest_path = next(
    (p for p in MANIFEST_CANDIDATES if p.exists()),
    None
)

if manifest_path is None:
    print("No manifest found in the expected locations.")
else:
    print("Found:", manifest_path)
    manifest = pd.read_csv(manifest_path)
    print("Rows:", len(manifest))
    print("Columns:", list(manifest.columns))
    print("\nSession counts:")
    if "session" in manifest.columns:
        print(manifest["session"].value_counts().sort_index().to_string())
    print("\nFirst three rows:")
    print(manifest.head(3).to_string(index=False))

# 4. Final QC register.
print("\n[4] FINAL QC REGISTER")
if not QC_FILE.exists():
    raise FileNotFoundError(QC_FILE)

qc = pd.read_csv(QC_FILE)
print("File:", QC_FILE)
print("Rows:", len(qc))
print("Columns:", list(qc.columns))

if "visual_severity" in qc.columns:
    print("\nVisual classifications:")
    print(qc["visual_severity"].value_counts().to_string())

if "trial_id" in qc.columns:
    print("\nAffected trial IDs:")
    print(qc["trial_id"].to_string(index=False))

# 5. Frozen baseline manifest.
print("\n[5] FROZEN BASELINE")
baseline_manifest = ROOT / "bci_dataset_baseline_v1/manifest.json"
if baseline_manifest.exists():
    print("Found:", baseline_manifest)
    obj = json.loads(baseline_manifest.read_text())
    print(json.dumps(obj, indent=2)[:6000])
else:
    print("Baseline manifest not found at expected path.")

print("\nINSPECTION COMPLETE — NO FILES MODIFIED")
