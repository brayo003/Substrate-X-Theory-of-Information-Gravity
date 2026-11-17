from pathlib import Path
import csv
import numpy as np

ROOT = Path("data/processed/bci_iv_2a_epochs_v1")
OUT = ROOT / "signal_quality_audit.csv"

rows = []

print("=" * 72)
print("BCI IV-2a SIGNAL QUALITY AUDIT")
print("=" * 72)

for path in sorted(ROOT.glob("*_epochs.npz")):
    with np.load(path, allow_pickle=True) as d:
        eeg = d["eeg_uV"].astype(np.float64)
        eog = d["eog_uV"].astype(np.float64)
        labels = d["labels"]
        flags = d["artifact_flags"]

        trial_peak = np.max(np.abs(eeg), axis=(1, 2))
        trial_p2p = np.ptp(eeg, axis=2)
        trial_max_channel_p2p = np.max(trial_p2p, axis=1)
        trial_rms = np.sqrt(np.mean(eeg ** 2, axis=(1, 2)))

        eog_peak = np.max(np.abs(eog), axis=(1, 2))

        annotated = flags.astype(bool)
        clean = ~annotated

        print(f"\n{path.name}")
        print(f"  Trials: {len(eeg)}")
        print(f"  Annotated: {annotated.sum()} ({annotated.mean()*100:.2f}%)")
        print(f"  EEG peak |amplitude| median: {np.median(trial_peak):.2f} uV")
        print(f"  EEG peak |amplitude| 95th: {np.percentile(trial_peak, 95):.2f} uV")
        print(f"  EEG peak |amplitude| maximum: {trial_peak.max():.2f} uV")
        print(f"  EEG RMS median: {np.median(trial_rms):.2f} uV")
        print(f"  EEG max-channel peak-to-peak median: {np.median(trial_max_channel_p2p):.2f} uV")
        print(f"  EOG peak |amplitude| 95th: {np.percentile(eog_peak, 95):.2f} uV")
        print(f"  Non-finite EEG values: {np.size(eeg) - np.isfinite(eeg).sum()}")

        for name, mask in [("annotated", annotated), ("unannotated", clean)]:
            if mask.sum() == 0:
                continue

            print(
                f"  {name}: n={mask.sum()}, "
                f"EEG RMS median={np.median(trial_rms[mask]):.2f} uV, "
                f"peak median={np.median(trial_peak[mask]):.2f} uV, "
                f"peak 95th={np.percentile(trial_peak[mask], 95):.2f} uV"
            )

        for i in range(len(eeg)):
            rows.append({
                "file": path.name,
                "trial_index": i + 1,
                "label": int(labels[i]),
                "artifact_flag": int(flags[i]),
                "eeg_peak_abs_uV": float(trial_peak[i]),
                "eeg_rms_uV": float(trial_rms[i]),
                "eeg_max_channel_p2p_uV": float(trial_max_channel_p2p[i]),
                "eog_peak_abs_uV": float(eog_peak[i]),
            })

with OUT.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 72)
print("TOTAL")
print("=" * 72)
print("Trials:", len(rows))
print("Artifact-annotated:", sum(r["artifact_flag"] for r in rows))
print("Artifact rate:", round(
    100 * sum(r["artifact_flag"] for r in rows) / len(rows), 2
), "%")
print("Report:", OUT)
