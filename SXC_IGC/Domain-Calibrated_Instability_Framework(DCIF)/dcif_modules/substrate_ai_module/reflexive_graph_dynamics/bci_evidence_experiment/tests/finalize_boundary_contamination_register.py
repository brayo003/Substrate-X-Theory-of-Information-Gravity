from pathlib import Path
import json
import pandas as pd

out = Path("bci_evidence_experiment/results/final_qc_register")
csv_path = out / "boundary_contamination_register.csv"
json_path = out / "boundary_contamination_register_summary.json"

df = pd.read_csv(csv_path)

reviews = {
    "A01E_run2_trial21": "Sparse",
    "A01E_run3_trial27": "Severe",
    "A02E_run2_trial2": "Sparse",
    "A02E_run3_trial1": "Sparse",
    "A02E_run3_trial2": "Sparse",
    "A03E_run2_trial8": "Moderate",
    "A03E_run4_trial35": "Severe",
    "A04E_run3_trial13": "Moderate",
    "A04E_run4_trial8": "Sparse",
    "A04T_run4_trial36": "Severe",
    "A08E_run6_trial25": "Sparse",
    "A08T_run2_trial34": "Severe",
}

if len(df) != 12:
    raise ValueError(f"Expected 12 rows; found {len(df)}")

if set(df["trial_id"]) != set(reviews):
    raise ValueError("Trial identifiers do not match the 12 expected reviews.")

df["visual_severity"] = df["trial_id"].map(reviews)
df["visual_review_status"] = "Reviewed"
df["visual_source"] = "Gemini assessment supplied by user"

# Retain the original primary-analysis policy.
df["primary_analysis_status"] = "Retained"
df["exclusion_authorized"] = False
df["signal_repair_performed"] = False

df.to_csv(csv_path, index=False)

counts = df["visual_severity"].value_counts().to_dict()

summary = {
    "source_file": "bci_evidence_experiment/results/source_boundary_audit/trial_boundary_audit.csv",
    "source_trial_count": 3456,
    "boundary_affected_trial_count": len(df),
    "visually_reviewed_count": int(
        (df["visual_review_status"] == "Reviewed").sum()
    ),
    "visual_review_pending_count": int(
        (df["visual_review_status"] != "Reviewed").sum()
    ),
    "visual_severity_counts": {
        k: int(v) for k, v in counts.items()
    },
    "exact_minus100_total": int(
        df["count_exact_minus100_all_channels"].sum()
    ),
    "exact_minus1000_total": int(
        df["count_exact_minus1000_all_channels"].sum()
    ),
    "trials_with_minus1000": int(
        (df["has_minus1000"] == 1).sum()
    ),
    "trials_with_original_artifact_flag": int(
        (df["artifact_flag"] == 1).sum()
    ),
    "trials_with_synchronized_minus100": int(
        (df["synchronized_minus100"] == 1).sum()
    ),
    "trials_with_synchronized_minus1000": int(
        (df["synchronized_minus1000"] == 1).sum()
    ),
    "primary_analysis_policy": (
        "All trials retained. No exclusion, repair, interpolation, "
        "or replacement is authorized by this register."
    ),
    "visual_assessment_source": (
        "Gemini assessments supplied by the user; not independently "
        "verified visual diagnoses by this assistant."
    ),
}

json_path.write_text(json.dumps(summary, indent=2) + "\n")

assert counts == {"Sparse": 6, "Severe": 4, "Moderate": 2}
assert summary["visual_review_pending_count"] == 0
assert (df["primary_analysis_status"] == "Retained").all()

print("\nFINAL QC REGISTER")
print("=" * 55)
print(df[["trial_id", "visual_severity", "primary_analysis_status"]]
      .sort_values("trial_id").to_string(index=False))
print("\nClassification totals:", counts)
print("Reviewed: 12/12")
print("Pending: 0")
print("\nUpdated files:")
print(csv_path)
print(json_path)
print("\nVALIDATION PASSED")
