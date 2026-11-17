from pathlib import Path
import json
import pandas as pd

OUT = Path("bci_evidence_experiment/results/experiment_protocol_v1")

for filename in [
    "development_sensitivity_masks.csv",
    "heldout_sensitivity_masks.csv",
]:
    path = OUT / filename
    df = pd.read_csv(path)

    obsolete = "sensitivity_sparse_only_excluded"
    if obsolete in df.columns:
        df = df.drop(columns=[obsolete])

    df.to_csv(path, index=False)

protocol_path = OUT / "experiment_protocol_v1.json"
protocol = json.loads(protocol_path.read_text())

sensitivity = protocol["sensitivity_analysis"]
sensitivity.pop("cohort_5", None)
sensitivity["cohorts"] = [
    "Primary: retain all eligible trials",
    "Exclude original dataset artifact_flag == 1",
    "Exclude all exact-boundary-affected trials",
    "Exclude visually Severe trials",
    "Exclude visually Severe and Moderate trials",
]
sensitivity["rule"] = (
    "Sensitivity masks are predeclared. The Sparse visual category is "
    "reported descriptively but is not an independent exclusion cohort. "
    "Masks do not modify source or filtered EEG arrays."
)

protocol_path.write_text(json.dumps(protocol, indent=2) + "\n")

# Validate expected mask columns and cohort counts.
expected = {
    "primary_all_trials",
    "sensitivity_no_dataset_artifact_flag",
    "sensitivity_no_boundary_trials",
    "sensitivity_exclude_severe",
    "sensitivity_exclude_severe_moderate",
}

for filename in [
    "development_sensitivity_masks.csv",
    "heldout_sensitivity_masks.csv",
]:
    df = pd.read_csv(OUT / filename)
    actual = set(df.columns)
    if not expected.issubset(actual):
        raise AssertionError(
            f"{filename}: missing {sorted(expected - actual)}"
        )
    if "sensitivity_sparse_only_excluded" in actual:
        raise AssertionError("Obsolete Sparse exclusion mask remains.")

    print(f"\n{filename}: {len(df)} trials")
    for col in sorted(expected):
        print(f"  {col}: {int(df[col].sum())} retained")

print("\nPROTOCOL SENSITIVITY CORRECTION PASSED")
