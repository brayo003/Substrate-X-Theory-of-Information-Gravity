#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "data/processed/bci_iv_2a_epochs_v1"
FILTERED = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
MANIFEST = FILTERED / "preprocessing_manifest.json"
REPORT = ROOT / "bci_evidence_experiment/results/bci_8_30hz_validation.json"

EXACT_KEYS = [
    "labels",
    "run_ids",
    "trial_ids",
    "event_samples_1based",
    "artifact_flags",
    "sampling_rate",
    "epoch_tmin",
    "epoch_tmax",
    "eog_channel_names",
    "class_names",
]

def equal(a, b):
    return np.array_equal(np.asarray(a), np.asarray(b))

def main():
    manifest = json.loads(MANIFEST.read_text())
    baseline_files = sorted(BASELINE.glob("A??[TE]_epochs.npz"))
    filtered_files = sorted(FILTERED.glob("A??[TE].npz"))

    expected = {
        p.name.removesuffix("_epochs.npz"): p for p in baseline_files
    }
    actual = {p.stem: p for p in filtered_files}

    report = {
        "baseline_session_count": len(baseline_files),
        "filtered_session_count": len(filtered_files),
        "missing_filtered_sessions": sorted(set(expected) - set(actual)),
        "unexpected_filtered_sessions": sorted(set(actual) - set(expected)),
        "sessions": [],
        "all_pass": False,
    }

    if set(expected) != set(actual):
        report["error"] = "Session file sets differ."
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\\n")
        raise SystemExit("FAIL: filtered session set does not match baseline.")

    all_pass = True

    for session_id in sorted(expected):
        baseline_path = expected[session_id]
        filtered_path = actual[session_id]
        filename = filtered_path.name

        with np.load(baseline_path, allow_pickle=False) as base, np.load(
            filtered_path, allow_pickle=False
        ) as new:

            checks = {}

            # Baseline and filtered files use different keys for EEG channel names.
            checks["eeg_channel_names_match"] = (
                "eeg_channel_names" in base.files
                and "channel_names" in new.files
                and equal(base["eeg_channel_names"], new["channel_names"])
            )

            for key in EXACT_KEYS:
                checks[key] = (
                    key in base.files
                    and key in new.files
                    and equal(base[key], new[key])
                )

            checks["eog_exact_match"] = (
                "eog_uV" in base.files
                and "eog_uV" in new.files
                and equal(base["eog_uV"], new["eog_uV"])
            )

            eeg = np.asarray(new["eeg_uV"])
            checks["eeg_shape_valid"] = eeg.shape == (288, 22, 1000)
            checks["eeg_finite"] = bool(np.isfinite(eeg).all())
            checks["eeg_dtype_float32"] = eeg.dtype == np.float32

            # This should not be an exact match: an additional filter was applied.
            checks["eeg_changed_by_filter"] = (
                "eeg_uV" in base.files
                and not equal(base["eeg_uV"], new["eeg_uV"])
            )

            session_pass = all(checks.values())
            all_pass &= session_pass

            report["sessions"].append({
                "file": filename,
                "pass": session_pass,
                "checks": checks,
                "eeg_mean_uV": float(np.mean(eeg)),
                "eeg_std_uV": float(np.std(eeg)),
                "artifact_flagged_trials": int(
                    np.sum(new["artifact_flags"] != 0)
                ),
            })

            print(f"{'PASS' if session_pass else 'FAIL'} {filename}")
            for name, passed in checks.items():
                if not passed:
                    print(f"  FAIL: {name}")

    report["manifest_success_count"] = manifest.get("success_count")
    report["manifest_failure_count"] = manifest.get("failure_count")
    report["all_pass"] = bool(all_pass and len(filtered_files) == 14)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print(f"Validation: {'PASS' if report['all_pass'] else 'FAIL'}")
    print(f"Report: {REPORT}")

    if not report["all_pass"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
