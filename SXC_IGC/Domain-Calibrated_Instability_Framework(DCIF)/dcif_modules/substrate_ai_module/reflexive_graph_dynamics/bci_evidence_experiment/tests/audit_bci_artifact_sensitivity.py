import csv
import json
from pathlib import Path

import numpy as np
from scipy.signal import welch

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
OUT = ROOT / "bci_evidence_experiment/results"

FS = 250
N_PER_SEG = 500
BANDS = {
    "mu_8_13Hz": (8, 13),
    "beta_13_30Hz": (13, 30),
}

def power(x, lo, hi):
    f, p = welch(
        x, fs=FS, nperseg=N_PER_SEG, axis=-1,
        detrend="constant", scaling="density"
    )
    mask = (f >= lo) & (f <= hi)
    return np.trapz(p[..., mask], f[mask], axis=-1)

def stats(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if not x.size:
        return {"n": 0, "median": None, "mean": None, "p95": None}
    return {
        "n": int(x.size),
        "median": float(np.median(x)),
        "mean": float(np.mean(x)),
        "p95": float(np.percentile(x, 95)),
    }

def main():
    files = sorted(DATA.glob("A??[TE].npz"))
    if len(files) != 14:
        raise SystemExit(f"Expected 14 sessions, found {len(files)}")

    rows = []
    reports = []

    for path in files:
        with np.load(path, allow_pickle=False) as d:
            eeg = np.asarray(d["eeg_uV"], dtype=np.float64)
            labels = np.asarray(d["labels"])
            flags = np.asarray(d["artifact_flags"]) != 0

            if eeg.shape != (288, 22, 1000):
                raise ValueError(f"{path.name}: invalid EEG shape")
            if labels.shape != (288,) or flags.shape != (288,):
                raise ValueError(f"{path.name}: invalid metadata shape")

            trial_rms = np.sqrt(np.mean(eeg ** 2, axis=(1, 2)))
            trial_peak = np.max(np.abs(eeg), axis=(1, 2))

            session = {
                "session": path.stem,
                "trial_count": 288,
                "flagged_count": int(flags.sum()),
                "clean_count": int((~flags).sum()),
                "flagged_fraction": float(flags.mean()),
                "rms_uV": {
                    "clean": stats(trial_rms[~flags]),
                    "flagged": stats(trial_rms[flags]),
                },
                "peak_abs_uV": {
                    "clean": stats(trial_peak[~flags]),
                    "flagged": stats(trial_peak[flags]),
                },
                "classes": {},
                "band_power": {},
            }

            for label in sorted(np.unique(labels)):
                name = {
                    1: "left_hand", 2: "right_hand",
                    3: "feet", 4: "tongue"
                }[int(label)]
                mask = labels == label
                session["classes"][name] = {
                    "total": int(mask.sum()),
                    "flagged": int((mask & flags).sum()),
                    "clean": int((mask & ~flags).sum()),
                }
                rows.append({
                    "session": path.stem,
                    "class": name,
                    "total": int(mask.sum()),
                    "flagged": int((mask & flags).sum()),
                    "clean": int((mask & ~flags).sum()),
                })

            for band, (lo, hi) in BANDS.items():
                bp = power(eeg, lo, hi)
                session["band_power"][band] = {
                    "clean": stats(np.log10(np.maximum(bp[~flags], 1e-30))),
                    "flagged": stats(np.log10(np.maximum(bp[flags], 1e-30))),
                }

            reports.append(session)
            print(
                f"{path.stem}: flagged={flags.sum()}/288 "
                f"({100*flags.mean():.1f}%), "
                f"RMS clean={np.median(trial_rms[~flags]):.2f} uV, "
                f"flagged={np.median(trial_rms[flags]):.2f} uV"
            )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "bci_artifact_class_counts.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    total_flagged = sum(s["flagged_count"] for s in reports)
    paired_ids = {
        "A01E", "A01T", "A02E", "A02T", "A03E", "A03T",
        "A04E", "A04T", "A05E", "A05T", "A08E", "A08T"
    }
    paired = [s for s in reports if s["session"] in paired_ids]

    report = {
        "sessions": reports,
        "total_sessions": len(reports),
        "total_trials": sum(s["trial_count"] for s in reports),
        "total_flagged": total_flagged,
        "overall_flagged_fraction": total_flagged / 4032,
        "paired_cohort": {
            "sessions": len(paired),
            "trials": sum(s["trial_count"] for s in paired),
            "flagged": sum(s["flagged_count"] for s in paired),
        },
        "class_count_csv": str(csv_path.relative_to(ROOT)),
        "interpretation_limit": (
            "Artifact annotations are not a complete guarantee of signal "
            "quality. Flagged and clean comparisons are descriptive and "
            "must not be used to tune on evaluation-session labels."
        ),
    }

    json_path = OUT / "bci_artifact_sensitivity.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    print("\nARTIFACT SENSITIVITY AUDIT COMPLETE")
    print(f"Flagged: {total_flagged}/4032 ({100*total_flagged/4032:.2f}%)")
    print(
        "Paired cohort flagged:",
        f"{report['paired_cohort']['flagged']}/2880"
    )
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")

if __name__ == "__main__":
    main()
