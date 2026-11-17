import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "data/processed/bci_iv_2a_epochs_v1"
FILTERED = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
OUT = ROOT / "bci_evidence_experiment/results"

PAIRED = {
    "A01E", "A01T", "A02E", "A02T", "A03E", "A03T",
    "A04E", "A04T", "A05E", "A05T", "A08E", "A08T",
}

ROBUST_THRESHOLDS = (6.0, 10.0)
EPS = 1e-12


def robust_z_by_channel(values):
    """Robust z-scores across trials, independently for each channel."""
    values = np.asarray(values, dtype=np.float64)
    med = np.nanmedian(values, axis=0)
    mad = np.nanmedian(np.abs(values - med[None, :]), axis=0)
    scale = 1.4826 * mad

    result = np.zeros_like(values, dtype=np.float64)
    normal = scale > EPS
    result[:, normal] = (
        values[:, normal] - med[None, normal]
    ) / scale[None, normal]

    zero_scale = ~normal
    if np.any(zero_scale):
        deviations = np.abs(values[:, zero_scale] - med[None, zero_scale])
        result[:, zero_scale] = np.where(deviations > EPS, np.inf, 0.0)

    return result


def compute_metrics(eeg):
    """
    eeg shape: trials x channels x samples.
    Metrics are computed independently for each trial/channel.
    """
    x = np.asarray(eeg, dtype=np.float64)

    finite = np.isfinite(x)
    nonfinite_samples = (~finite).sum(axis=-1)

    # Preserve non-finite counts; use NaN-aware calculations for other metrics.
    clean = np.where(finite, x, np.nan)

    rms = np.sqrt(np.nanmean(clean ** 2, axis=-1))
    peak = np.nanmax(np.abs(clean), axis=-1)
    p2p = np.nanmax(clean, axis=-1) - np.nanmin(clean, axis=-1)
    std = np.nanstd(clean, axis=-1)

    flat = np.sum(finite, axis=-1) > 0
    flat &= np.nan_to_num(p2p, nan=np.inf) <= EPS

    kurt = kurtosis(
        clean, axis=-1, fisher=True, bias=False, nan_policy="omit"
    )

    return {
        "rms": rms,
        "peak_abs": peak,
        "peak_to_peak": p2p,
        "std": std,
        "kurtosis": kurt,
        "nonfinite_samples": nonfinite_samples,
        "flat": flat,
    }


def robust_scores(metrics):
    scores = {}
    for name in ("rms", "peak_abs", "peak_to_peak"):
        values = np.log10(np.maximum(metrics[name], EPS))
        scores[name] = robust_z_by_channel(values)

    scores["kurtosis"] = robust_z_by_channel(metrics["kurtosis"])
    return scores


def safe_max(x):
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    return float(np.max(x)) if x.size else None


def audit_file(path, source_name, output_rows):
    with np.load(path, allow_pickle=False) as d:
        eeg = np.asarray(d["eeg_uV"], dtype=np.float64)
        labels = np.asarray(d["labels"])
        flags = np.asarray(d["artifact_flags"]) != 0

        if eeg.shape != (288, 22, 1000):
            raise ValueError(f"{path}: unexpected EEG shape {eeg.shape}")
        if labels.shape != (288,) or flags.shape != (288,):
            raise ValueError(f"{path}: invalid metadata shape")

        if source_name == "filtered":
            channel_names = [str(x) for x in d["channel_names"]]
        else:
            channel_names = [str(x) for x in d["eeg_channel_names"]]

    if len(channel_names) != 22:
        raise ValueError(f"{path}: expected 22 channel names")

    metrics = compute_metrics(eeg)
    scores = robust_scores(metrics)

    # A channel-trial is an outlier if any metric exceeds the threshold.
    outlier6 = np.zeros((288, 22), dtype=bool)
    outlier10 = np.zeros((288, 22), dtype=bool)

    for score in scores.values():
        outlier6 |= np.abs(score) >= ROBUST_THRESHOLDS[0]
        outlier10 |= np.abs(score) >= ROBUST_THRESHOLDS[1]

    for trial in range(288):
        for channel in range(22):
            output_rows.append({
                "session": path.stem.replace("_epochs", ""),
                "source": source_name,
                "trial_index_0based": trial,
                "channel": channel_names[channel],
                "artifact_flag": int(flags[trial]),
                "rms_uV": metrics["rms"][trial, channel],
                "peak_abs_uV": metrics["peak_abs"][trial, channel],
                "peak_to_peak_uV": metrics["peak_to_peak"][trial, channel],
                "std_uV": metrics["std"][trial, channel],
                "kurtosis": metrics["kurtosis"][trial, channel],
                "nonfinite_samples": int(
                    metrics["nonfinite_samples"][trial, channel]
                ),
                "flat_channel": int(metrics["flat"][trial, channel]),
                "rms_robust_z": scores["rms"][trial, channel],
                "peak_robust_z": scores["peak_abs"][trial, channel],
                "p2p_robust_z": scores["peak_to_peak"][trial, channel],
                "kurtosis_robust_z": scores["kurtosis"][trial, channel],
                "outlier_abs_z_ge_6": int(outlier6[trial, channel]),
                "outlier_abs_z_ge_10": int(outlier10[trial, channel]),
            })

    trial_outlier6 = np.any(outlier6, axis=1)
    trial_outlier10 = np.any(outlier10, axis=1)

    return {
        "session": path.stem.replace("_epochs", ""),
        "source": source_name,
        "trials": int(eeg.shape[0]),
        "channels": int(eeg.shape[1]),
        "samples_per_trial": int(eeg.shape[2]),
        "artifact_flagged_trials": int(flags.sum()),
        "flat_channel_trials": int(metrics["flat"].sum()),
        "nonfinite_channel_trials": int(
            (metrics["nonfinite_samples"] > 0).sum()
        ),
        "channel_trials_outlier_abs_z_ge_6": int(outlier6.sum()),
        "channel_trials_outlier_abs_z_ge_10": int(outlier10.sum()),
        "trials_with_any_outlier_abs_z_ge_6": int(trial_outlier6.sum()),
        "trials_with_any_outlier_abs_z_ge_10": int(trial_outlier10.sum()),
        "max_peak_abs_uV": safe_max(metrics["peak_abs"]),
        "max_peak_to_peak_uV": safe_max(metrics["peak_to_peak"]),
        "max_abs_kurtosis": safe_max(np.abs(metrics["kurtosis"])),
        "channel_names": channel_names,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    filtered_files = sorted(FILTERED.glob("A??[TE].npz"))
    if len(filtered_files) != 14:
        raise SystemExit(
            f"Expected 14 filtered sessions, found {len(filtered_files)}"
        )

    rows = []
    reports = []

    for filtered_path in filtered_files:
        session = filtered_path.stem
        baseline_path = BASELINE / f"{session}_epochs.npz"

        if not baseline_path.exists():
            raise FileNotFoundError(baseline_path)

        # Confirm metadata identity before comparing signal metrics.
        with np.load(baseline_path, allow_pickle=False) as b, \
             np.load(filtered_path, allow_pickle=False) as f:
            for key in ("labels", "run_ids", "trial_ids", "artifact_flags"):
                if not np.array_equal(b[key], f[key]):
                    raise ValueError(
                        f"{session}: baseline/filtered mismatch in {key}"
                    )

        baseline_report = audit_file(
            baseline_path, "baseline", rows
        )
        filtered_report = audit_file(
            filtered_path, "filtered", rows
        )

        if baseline_report["channel_names"] != filtered_report["channel_names"]:
            raise ValueError(f"{session}: channel order mismatch")

        reports.extend([baseline_report, filtered_report])

        print(
            f"{session}: "
            f"baseline outlier trials="
            f"{baseline_report['trials_with_any_outlier_abs_z_ge_6']}/288; "
            f"filtered="
            f"{filtered_report['trials_with_any_outlier_abs_z_ge_6']}/288; "
            f"baseline max peak="
            f"{baseline_report['max_peak_abs_uV']:.2f} uV"
        )

    csv_path = OUT / "bci_channel_trial_quality.csv"
    fields = list(rows[0].keys())

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    def cohort_summary(source, sessions):
        selected = [
            r for r in reports
            if r["source"] == source and r["session"] in sessions
        ]
        return {
            "sessions": len(selected),
            "trials": sum(r["trials"] for r in selected),
            "artifact_flagged_trials": sum(
                r["artifact_flagged_trials"] for r in selected
            ),
            "flat_channel_trials": sum(
                r["flat_channel_trials"] for r in selected
            ),
            "nonfinite_channel_trials": sum(
                r["nonfinite_channel_trials"] for r in selected
            ),
            "channel_trials_outlier_abs_z_ge_6": sum(
                r["channel_trials_outlier_abs_z_ge_6"] for r in selected
            ),
            "channel_trials_outlier_abs_z_ge_10": sum(
                r["channel_trials_outlier_abs_z_ge_10"] for r in selected
            ),
            "trials_with_any_outlier_abs_z_ge_6": sum(
                r["trials_with_any_outlier_abs_z_ge_6"] for r in selected
            ),
            "trials_with_any_outlier_abs_z_ge_10": sum(
                r["trials_with_any_outlier_abs_z_ge_10"] for r in selected
            ),
        }

    all_sessions = {r["session"] for r in reports}

    report = {
        "audit": "BCI IV-2a channel-level signal quality",
        "metrics": [
            "RMS amplitude",
            "peak absolute amplitude",
            "peak-to-peak amplitude",
            "standard deviation",
            "excess kurtosis",
            "non-finite sample count",
            "flat-channel indicator",
        ],
        "robust_outlier_method": (
            "Within each session and channel, calculate median and MAD "
            "across trials. Robust z = deviation / (1.4826 * MAD). "
            "RMS, peak, and peak-to-peak are log10-transformed first."
        ),
        "thresholds": list(ROBUST_THRESHOLDS),
        "threshold_interpretation": (
            "Screening thresholds only. They do not define automatic "
            "trial rejection and are not tuned using evaluation labels."
        ),
        "all_sessions": {
            "baseline": cohort_summary("baseline", all_sessions),
            "filtered": cohort_summary("filtered", all_sessions),
        },
        "paired_cohort_A01_A05_A08": {
            "baseline": cohort_summary("baseline", PAIRED),
            "filtered": cohort_summary("filtered", PAIRED),
        },
        "session_reports": reports,
        "trial_channel_csv": str(csv_path.relative_to(ROOT)),
        "limitations": [
            "Robust outliers are relative to each session/channel and do "
            "not establish physiological abnormality.",
            "The 8-30 Hz filter can suppress some artifact components; "
            "baseline and filtered metrics must therefore be interpreted "
            "separately.",
            "No trials are removed by this audit.",
            "No evaluation-session labels are used for model selection."
        ],
    }

    json_path = OUT / "bci_channel_quality_audit.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    print("\nCHANNEL-QUALITY AUDIT COMPLETE")
    print("Baseline paired cohort:")
    print(json.dumps(
        report["paired_cohort_A01_A05_A08"]["baseline"], indent=2
    ))
    print("Filtered paired cohort:")
    print(json.dumps(
        report["paired_cohort_A01_A05_A08"]["filtered"], indent=2
    ))
    print(f"\nJSON: {json_path}")
    print(f"CSV:  {csv_path}")


if __name__ == "__main__":
    main()
