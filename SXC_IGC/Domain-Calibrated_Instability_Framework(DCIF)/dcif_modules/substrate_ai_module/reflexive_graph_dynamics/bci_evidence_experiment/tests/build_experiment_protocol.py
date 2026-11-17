#!/usr/bin/env python3

from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path.cwd()

FILTERED_DIR = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
TRIAL_MANIFEST = ROOT / "data/processed/bci_iv_2a_epochs_v1/trial_manifest.csv"
QC_REGISTER = ROOT / "bci_evidence_experiment/results/final_qc_register/boundary_contamination_register.csv"

OUT = ROOT / "bci_evidence_experiment/results/experiment_protocol_v1"
SEALED = OUT / "scoring_only_do_not_use_for_model_development"

SUBJECTS = ["A01", "A02", "A03", "A04", "A05", "A08"]
EXPLORATORY_SUBJECTS = ["A06", "A07"]

OUT.mkdir(parents=True, exist_ok=True)
SEALED.mkdir(parents=True, exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

for p in [FILTERED_DIR, TRIAL_MANIFEST.parent]:
    if not p.exists():
        raise FileNotFoundError(p)

for p in [TRIAL_MANIFEST, QC_REGISTER]:
    if not p.exists():
        raise FileNotFoundError(p)

manifest = pd.read_csv(TRIAL_MANIFEST)
qc = pd.read_csv(QC_REGISTER)

required_manifest = {
    "subject", "session", "run", "trial", "label",
    "class_name", "event_sample_1based", "artifact_flag",
    "sampling_rate", "file"
}
required_qc = {
    "session", "run", "trial_within_run", "visual_severity",
    "has_any_boundary", "synchronized_minus100",
    "synchronized_minus1000"
}

if not required_manifest.issubset(manifest.columns):
    raise ValueError(
        f"Manifest missing: {sorted(required_manifest - set(manifest.columns))}"
    )

if not required_qc.issubset(qc.columns):
    raise ValueError(
        f"QC register missing: {sorted(required_qc - set(qc.columns))}"
    )

# Normalize session identity and trial keys.
manifest["subject"] = manifest["subject"].astype(str)
manifest["session"] = manifest["session"].astype(str)
manifest["run"] = manifest["run"].astype(int)
manifest["trial"] = manifest["trial"].astype(int)

qc["session"] = qc["session"].astype(str)
qc["run"] = qc["run"].astype(int)
qc["trial_within_run"] = qc["trial_within_run"].astype(int)

manifest["session_id"] = (
    manifest["subject"] + manifest["session"]
)

# Check manifest uniqueness.
if manifest.duplicated(["session_id", "run", "trial"]).any():
    raise ValueError("Duplicate session/run/trial keys in trial manifest.")

# QC join uses session ID, run and within-run trial.
qc_small = qc[
    [
        "session", "run", "trial_within_run",
        "visual_severity", "has_any_boundary",
        "synchronized_minus100", "synchronized_minus1000"
    ]
].copy()

qc_small = qc_small.rename(columns={
    "trial_within_run": "trial",
})

if qc_small.duplicated(["session", "run", "trial"]).any():
    raise ValueError("Duplicate trial keys in QC register.")

data = manifest.merge(
    qc_small,
    left_on=["session_id", "run", "trial"],
    right_on=["session", "run", "trial"],
    how="left",
    validate="one_to_one",
    suffixes=("", "_qc"),
)

data["has_any_boundary"] = (
    data["has_any_boundary"].fillna(0).astype(int)
)
data["synchronized_minus100"] = (
    data["synchronized_minus100"].fillna(0).astype(int)
)
data["synchronized_minus1000"] = (
    data["synchronized_minus1000"].fillna(0).astype(int)
)
data["visual_severity"] = data["visual_severity"].fillna("None")

# Keep QC categories separate from the original dataset artifact flag.
data["artifact_flag"] = data["artifact_flag"].astype(int)
data["boundary_category"] = data["visual_severity"]

# Primary paired cohort only.
paired = data[data["subject"].isin(SUBJECTS)].copy()

dev = paired[paired["session"] == "T"].copy()
heldout = paired[paired["session"] == "E"].copy()

# Ensure the primary split is exactly the intended 6 x 288 sessions.
expected_sessions = {
    f"{s}{sess}"
    for s in SUBJECTS
    for sess in ["T", "E"]
}

actual_sessions = set(paired["session_id"].unique())
if actual_sessions != expected_sessions:
    raise ValueError(
        f"Paired cohort session mismatch.\n"
        f"Missing: {sorted(expected_sessions - actual_sessions)}\n"
        f"Unexpected: {sorted(actual_sessions - expected_sessions)}"
    )

if len(dev) != 1728 or len(heldout) != 1728:
    raise ValueError(
        f"Unexpected split sizes: T={len(dev)}, E={len(heldout)}"
    )

# Verify NPZ trial metadata and label alignment.
session_checks = []

for session_id in sorted(expected_sessions):
    subject = session_id[:3]
    session = session_id[3]
    npz_path = FILTERED_DIR / f"{session_id}.npz"

    if not npz_path.exists():
        raise FileNotFoundError(npz_path)

    with np.load(npz_path, allow_pickle=True) as z:
        required_npz = {
            "eeg_uV", "labels", "run_ids", "trial_ids",
            "artifact_flags", "event_samples_1based",
            "sampling_rate", "channel_names"
        }
        if not required_npz.issubset(z.files):
            raise ValueError(
                f"{session_id}: missing NPZ keys "
                f"{sorted(required_npz - set(z.files))}"
            )

        X = z["eeg_uV"]
        y = z["labels"]
        runs = z["run_ids"]
        trials = z["trial_ids"]
        flags = z["artifact_flags"]
        events = z["event_samples_1based"]

        if X.shape != (288, 22, 1000):
            raise ValueError(f"{session_id}: unexpected EEG shape {X.shape}")

        if not np.isfinite(X).all():
            raise ValueError(f"{session_id}: non-finite EEG values")

        if not (
            len(y) == len(runs) == len(trials) ==
            len(flags) == len(events) == 288
        ):
            raise ValueError(f"{session_id}: metadata length mismatch")

        expected = manifest[
            manifest["session_id"] == session_id
        ].sort_values(["run", "trial"])

        if len(expected) != 288:
            raise ValueError(
                f"{session_id}: manifest has {len(expected)} rows"
            )

        if not np.array_equal(
            runs.astype(int),
            expected["run"].to_numpy(dtype=int)
        ):
            raise ValueError(f"{session_id}: run IDs disagree with manifest")

        if not np.array_equal(
            trials.astype(int),
            expected["trial"].to_numpy(dtype=int)
        ):
            raise ValueError(
                f"{session_id}: trial IDs disagree with manifest"
            )

        if not np.array_equal(
            y.astype(int),
            expected["label"].to_numpy(dtype=int)
        ):
            raise ValueError(f"{session_id}: labels disagree with manifest")

        if not np.array_equal(
            flags.astype(int),
            expected["artifact_flag"].to_numpy(dtype=int)
        ):
            raise ValueError(
                f"{session_id}: artifact flags disagree with manifest"
            )

        if not np.array_equal(
            events.astype(int),
            expected["event_sample_1based"].to_numpy(dtype=int)
        ):
            raise ValueError(
                f"{session_id}: event samples disagree with manifest"
            )

        class_counts = pd.Series(y).value_counts().to_dict()

        # T labels are development labels. E labels are not used for
        # any model-building or split-selection operation.
        if session == "T" and class_counts != {1: 72, 2: 72, 3: 72, 4: 72}:
            raise ValueError(
                f"{session_id}: unexpected T class counts {class_counts}"
            )

        session_checks.append({
            "session_id": session_id,
            "trials": int(len(y)),
            "eeg_shape": list(X.shape),
            "sampling_rate_hz": int(z["sampling_rate"]),
            "channel_count": int(X.shape[1]),
            "class_counts": class_counts if session == "T" else None,
            "npz_sha256": sha256(npz_path),
        })

# Assign stable row IDs. These refer to trial rows, not new EEG files.
dev = dev.sort_values(
    ["subject", "run", "trial"]
).reset_index(drop=True)

heldout = heldout.sort_values(
    ["subject", "run", "trial"]
).reset_index(drop=True)

dev.insert(0, "trial_row_id", np.arange(len(dev), dtype=int))
heldout.insert(0, "trial_row_id", np.arange(len(heldout), dtype=int))

# Development manifest contains T labels.
dev_columns = [
    "trial_row_id", "subject", "session_id", "run", "trial",
    "label", "class_name", "file", "event_sample_1based",
    "artifact_flag", "has_any_boundary",
    "visual_severity", "boundary_category",
    "synchronized_minus100", "synchronized_minus1000"
]

dev[dev_columns].to_csv(
    OUT / "development_T_labeled.csv", index=False
)

# Held-out manifest intentionally has no labels or class names.
heldout_columns = [
    "trial_row_id", "subject", "session_id", "run", "trial",
    "file", "event_sample_1based", "artifact_flag",
    "has_any_boundary", "visual_severity", "boundary_category",
    "synchronized_minus100", "synchronized_minus1000"
]

heldout[heldout_columns].to_csv(
    OUT / "heldout_E_unlabeled.csv", index=False
)

# E labels are written separately for final scoring only.
# Do not load this file during model development or tuning.
heldout[[
    "trial_row_id", "subject", "session_id", "run", "trial", "label"
]].to_csv(
    SEALED / "heldout_E_labels_for_final_scoring_only.csv",
    index=False
)

# Sensitivity-analysis inclusion masks.
# Primary: all trials retained.
# Sensitivity cohorts are predeclared, not selected using model results.
def add_sensitivity_masks(frame):
    frame = frame.copy()
    frame["primary_all_trials"] = True
    frame["sensitivity_no_dataset_artifact_flag"] = (
        frame["artifact_flag"] == 0
    )
    frame["sensitivity_no_boundary_trials"] = (
        frame["has_any_boundary"] == 0
    )
    frame["sensitivity_exclude_severe"] = (
        frame["visual_severity"] != "Severe"
    )
    frame["sensitivity_exclude_severe_moderate"] = (
        ~frame["visual_severity"].isin(["Severe", "Moderate"])
    )
    frame["sensitivity_sparse_only_excluded"] = (
        frame["visual_severity"] != "Sparse"
    )
    return frame

dev_sens = add_sensitivity_masks(dev)
heldout_sens = add_sensitivity_masks(heldout)

sensitivity_columns = [
    "trial_row_id", "subject", "session_id", "run", "trial",
    "artifact_flag", "has_any_boundary", "visual_severity",
    "primary_all_trials",
    "sensitivity_no_dataset_artifact_flag",
    "sensitivity_no_boundary_trials",
    "sensitivity_exclude_severe",
    "sensitivity_exclude_severe_moderate",
    "sensitivity_sparse_only_excluded"
]

dev_sens[sensitivity_columns].to_csv(
    OUT / "development_sensitivity_masks.csv", index=False
)

heldout_sens[sensitivity_columns].to_csv(
    OUT / "heldout_sensitivity_masks.csv", index=False
)

# Subject-level pairing plan. No trial-level inferential independence.
pairing = pd.DataFrame({
    "subject": SUBJECTS,
    "development_session": [s + "T" for s in SUBJECTS],
    "heldout_session": [s + "E" for s in SUBJECTS],
    "development_trials": [288] * len(SUBJECTS),
    "heldout_trials": [288] * len(SUBJECTS),
})
pairing.to_csv(OUT / "paired_subject_evaluation_plan.csv", index=False)

# Exploratory E-only sessions are listed separately and excluded from
# primary paired inference.
exploratory_rows = []
for subject in EXPLORATORY_SUBJECTS:
    session_id = subject + "E"
    path = FILTERED_DIR / f"{session_id}.npz"
    if path.exists():
        with np.load(path, allow_pickle=True) as z:
            exploratory_rows.append({
                "subject": subject,
                "session_id": session_id,
                "trials": int(len(z["labels"])),
                "status": "Exploratory only; no paired T session",
                "npz_sha256": sha256(path),
            })

pd.DataFrame(exploratory_rows).to_csv(
    OUT / "exploratory_E_only_sessions.csv", index=False
)

# Protocol specification.
protocol = {
    "protocol_id": "SUBSTRATE_AI_BCI_IV2A_PROTOCOL_V1",
    "status": "DATA_SPLIT_AND_QC_PROTOCOL_FROZEN_PENDING_REVIEW",
    "dataset": "BCI Competition IV-2a / BNCI2014-001",
    "preprocessing_dataset": "bci_iv_2a_epochs_8_30hz_v1",
    "input_tensor": {
        "key": "eeg_uV",
        "shape_per_session": [288, 22, 1000],
        "sampling_rate_hz": 250,
        "epoch_seconds": [2, 6],
        "channels": 22,
    },
    "primary_paired_subjects": SUBJECTS,
    "exploratory_E_only_subjects": EXPLORATORY_SUBJECTS,
    "primary_analysis": {
        "development": "T sessions for A01-A05 and A08",
        "heldout_evaluation": "E sessions for A01-A05 and A08",
        "all_eligible_trials_retained": True,
        "development_trials": 1728,
        "heldout_trials": 1728,
    },
    "sensitivity_analysis": {
        "primary_all_trials": "All trials retained",
        "cohort_1": "Exclude original dataset artifact_flag == 1",
        "cohort_2": "Exclude all exact-boundary-affected trials",
        "cohort_3": "Exclude visually Severe trials",
        "cohort_4": "Exclude visually Severe and Moderate trials",
        "cohort_5": "Exclude visually Sparse trials",
        "rule": (
            "Sensitivity masks are predeclared. They do not modify source "
            "or filtered EEG arrays. Report sample counts and subject-level "
            "results for each applicable cohort."
        ),
    },
    "heldout_label_control": {
        "E_labels_in_development_manifest": False,
        "E_labels_in_heldout_manifest": False,
        "E_labels_separate_scoring_file": (
            "scoring_only_do_not_use_for_model_development/"
            "heldout_E_labels_for_final_scoring_only.csv"
        ),
        "restriction": (
            "Do not read E labels for preprocessing decisions, graph "
            "construction, model fitting, threshold selection, hyperparameter "
            "selection, early stopping, or model selection. Load them only "
            "after predictions and model choices are frozen for final scoring."
        ),
    },
    "subject_level_inference": {
        "unit_of_inference": "subject",
        "paired_subjects": SUBJECTS,
        "n_subjects": 6,
        "rule": (
            "Compute each method's metric separately for each held-out "
            "subject, then compare methods using paired subject-level "
            "differences. Do not treat trials as independent subjects."
        ),
        "report": [
            "per-subject metrics",
            "mean and median paired difference",
            "subject-level confidence intervals where appropriate",
            "exact paired permutation or Wilcoxon signed-rank test where justified",
        ],
    },
    "modeling_status": "NOT_STARTED",
    "connectivity_graphs_constructed": False,
    "heldout_E_labels_used_for_modeling": False,
}

(OUT / "experiment_protocol_v1.json").write_text(
    json.dumps(protocol, indent=2) + "\n"
)

# Validation report.
validation = {
    "filtered_sessions_verified": len(session_checks),
    "paired_subjects": SUBJECTS,
    "development_trials": len(dev),
    "heldout_trials": len(heldout),
    "development_labels_present": "label" in pd.read_csv(
        OUT / "development_T_labeled.csv"
    ).columns,
    "heldout_labels_absent": "label" not in pd.read_csv(
        OUT / "heldout_E_unlabeled.csv"
    ).columns,
    "sealed_scoring_labels_rows": len(heldout),
    "qc_boundary_trials_in_primary_cohort": int(
        paired["has_any_boundary"].sum()
    ),
    "primary_development_artifact_flagged": int(
        (dev["artifact_flag"] == 1).sum()
    ),
    "primary_heldout_artifact_flagged": int(
        (heldout["artifact_flag"] == 1).sum()
    ),
    "visual_severity_counts_primary_cohort": {
        str(k): int(v)
        for k, v in paired["visual_severity"].value_counts().items()
    },
    "session_checks": session_checks,
    "validation_passed": True,
}

(OUT / "protocol_validation.json").write_text(
    json.dumps(validation, indent=2) + "\n"
)

print("\nEXPERIMENT PROTOCOL BUILD COMPLETE")
print("=" * 68)
print("Filtered sessions verified:", len(session_checks))
print("Primary paired subjects:", ", ".join(SUBJECTS))
print("T development trials:", len(dev))
print("E held-out trials:", len(heldout))
print("E labels in held-out manifest: NO")
print("E labels stored separately for final scoring: YES")
print("Primary T artifact-flagged trials:", validation["primary_development_artifact_flagged"])
print("Primary E artifact-flagged trials:", validation["primary_heldout_artifact_flagged"])
print("Primary cohort boundary-affected trials:", validation["qc_boundary_trials_in_primary_cohort"])
print("\nOutput directory:")
print(OUT)
print("\nKey files:")
for name in [
    "experiment_protocol_v1.json",
    "protocol_validation.json",
    "development_T_labeled.csv",
    "heldout_E_unlabeled.csv",
    "development_sensitivity_masks.csv",
    "heldout_sensitivity_masks.csv",
    "paired_subject_evaluation_plan.csv",
    "exploratory_E_only_sessions.csv",
    "scoring_only_do_not_use_for_model_development/heldout_E_labels_for_final_scoring_only.csv",
]:
    print(" ", OUT / name)

print("\nIMPORTANT: Model development must not load the scoring-only E-label file.")
print("VALIDATION PASSED")
