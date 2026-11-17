#!/usr/bin/env python3

from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()

INPUT_FILE = (
    ROOT
    / "bci_evidence_experiment/results/source_boundary_audit/"
      "trial_boundary_audit.csv"
)

OUTPUT_DIR = (
    ROOT
    / "bci_evidence_experiment/results/final_qc_register"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(INPUT_FILE)

df = pd.read_csv(INPUT_FILE)

# Actual source CSV schema.
required = [
    "session",
    "global_trial_index",
    "run",
    "trial_within_run",
    "event_sample_1based",
    "label",
    "artifact_flag",
    "epoch_samples",
    "count_exact_minus100_all_channels",
    "count_exact_minus1000_all_channels",
    "count_abs_ge_90_all_channels",
    "channels_with_minus100",
    "channels_with_minus1000",
    "max_simultaneous_minus100_channels",
    "timepoints_with_2plus_minus100_channels",
    "timepoints_with_3plus_minus100_channels",
    "timepoints_with_10plus_minus100_channels",
    "max_simultaneous_minus1000_channels",
    "timepoints_with_2plus_minus1000_channels",
    "has_minus100",
    "has_minus1000",
    "has_any_boundary",
    "synchronized_minus100",
    "synchronized_minus1000",
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

if len(df) != 3456:
    raise ValueError(
        f"Expected 3456 source trials, found {len(df)}. "
        "Check the source audit before proceeding."
    )

# Select only trials with at least one exact boundary occurrence.
df["has_any_boundary"] = pd.to_numeric(
    df["has_any_boundary"], errors="raise"
)

register = df.loc[df["has_any_boundary"] == 1].copy()

# Visual classifications supplied by the user from Gemini.
visual_reviews = {
    ("A01E", 3, 27): "Severe",
    ("A03E", 4, 35): "Severe",
    ("A04T", 4, 36): "Severe",
    ("A04E", 3, 13): "Moderate",
    ("A08T", 2, 34): "Severe",
}

def classify_visual(row):
    key = (
        str(row["session"]),
        int(row["run"]),
        int(row["trial_within_run"]),
    )
    return visual_reviews.get(key, "Pending")

register["visual_severity"] = register.apply(
    classify_visual, axis=1
)

register["visual_review_status"] = register[
    "visual_severity"
].map(
    lambda x: "Reviewed" if x != "Pending" else "Not visually reviewed"
)

register["visual_source"] = register[
    "visual_review_status"
].map(
    lambda x: (
        "Gemini assessment supplied by user"
        if x == "Reviewed"
        else ""
    )
)

# Explicit analysis policy: no automatic exclusion or repair.
register["primary_analysis_status"] = "Retained"
register["exclusion_authorized"] = False
register["signal_repair_performed"] = False

register["qc_category"] = "Boundary occurrence"

register.loc[
    register["synchronized_minus100"] == 1,
    "qc_category",
] = "Synchronized -100 boundary occurrence"

register.loc[
    register["synchronized_minus1000"] == 1,
    "qc_category",
] = "Synchronized -1000 boundary occurrence"

register.loc[
    (register["synchronized_minus100"] == 1)
    & (register["synchronized_minus1000"] == 1),
    "qc_category",
] = "Synchronized -100 and -1000 boundary occurrence"

# Human-readable stable trial identifier.
register.insert(
    0,
    "trial_id",
    register.apply(
        lambda r: (
            f"{r['session']}_run{int(r['run'])}"
            f"_trial{int(r['trial_within_run'])}"
        ),
        axis=1,
    ),
)

register = register.sort_values(
    ["session", "run", "trial_within_run"]
).reset_index(drop=True)

# Save the register.
register_path = OUTPUT_DIR / "boundary_contamination_register.csv"
register.to_csv(register_path, index=False)

reviewed = register["visual_review_status"] == "Reviewed"

summary = {
    "source_file": str(INPUT_FILE.relative_to(ROOT)),
    "source_trial_count": int(len(df)),
    "boundary_affected_trial_count": int(len(register)),
    "visually_reviewed_count": int(reviewed.sum()),
    "visual_review_pending_count": int((~reviewed).sum()),
    "visual_severity_counts": {
        str(k): int(v)
        for k, v in register["visual_severity"].value_counts().items()
    },
    "exact_minus100_total": int(
        register["count_exact_minus100_all_channels"].sum()
    ),
    "exact_minus1000_total": int(
        register["count_exact_minus1000_all_channels"].sum()
    ),
    "trials_with_minus1000": int(
        (register["has_minus1000"] == 1).sum()
    ),
    "trials_with_original_artifact_flag": int(
        (register["artifact_flag"] == 1).sum()
    ),
    "trials_with_synchronized_minus100": int(
        (register["synchronized_minus100"] == 1).sum()
    ),
    "trials_with_synchronized_minus1000": int(
        (register["synchronized_minus1000"] == 1).sum()
    ),
    "primary_analysis_policy": (
        "All trials retained. No exclusion, repair, interpolation, "
        "or replacement is authorized by this register."
    ),
    "evidence_policy": (
        "Numerical measurements, original dataset artifact flags, "
        "and visual assessments are stored separately."
    ),
}

summary_path = (
    OUTPUT_DIR / "boundary_contamination_register_summary.json"
)
summary_path.write_text(json.dumps(summary, indent=2) + "\n")

# Validate the five supplied classifications.
expected_reviews = {
    "A01E_run3_trial27": "Severe",
    "A03E_run4_trial35": "Severe",
    "A04T_run4_trial36": "Severe",
    "A04E_run3_trial13": "Moderate",
    "A08T_run2_trial34": "Severe",
}

actual_reviews = dict(
    zip(
        register.loc[reviewed, "trial_id"],
        register.loc[reviewed, "visual_severity"],
    )
)

if actual_reviews != expected_reviews:
    raise RuntimeError(
        "Visual review mapping validation failed.\n"
        f"Expected: {expected_reviews}\n"
        f"Actual:   {actual_reviews}"
    )

if len(register) != 12:
    raise RuntimeError(
        f"Expected 12 boundary-affected trials, found {len(register)}."
    )

if int(reviewed.sum()) != 5:
    raise RuntimeError(
        f"Expected 5 reviewed trials, found {int(reviewed.sum())}."
    )

print("\nBOUNDARY CONTAMINATION REGISTER")
print("=" * 65)
print(f"Source trials:              {len(df)}")
print(f"Boundary-affected trials:   {len(register)}")
print(f"Visually reviewed:          {int(reviewed.sum())}")
print(f"Visual reviews pending:     {int((~reviewed).sum())}")
print(f"Exact -100 occurrences:     {summary['exact_minus100_total']}")
print(f"Exact -1000 occurrences:    {summary['exact_minus1000_total']}")

print("\nVisual severity counts:")
for severity, count in summary["visual_severity_counts"].items():
    print(f"  {severity}: {count}")

print("\nTrial register:")
print(
    register[
        [
            "trial_id",
            "artifact_flag",
            "count_exact_minus100_all_channels",
            "count_exact_minus1000_all_channels",
            "channels_with_minus100",
            "max_simultaneous_minus100_channels",
            "visual_severity",
            "primary_analysis_status",
        ]
    ].to_string(index=False)
)

print("\nOutput files:")
print(register_path)
print(summary_path)
print("\nVALIDATION PASSED")
