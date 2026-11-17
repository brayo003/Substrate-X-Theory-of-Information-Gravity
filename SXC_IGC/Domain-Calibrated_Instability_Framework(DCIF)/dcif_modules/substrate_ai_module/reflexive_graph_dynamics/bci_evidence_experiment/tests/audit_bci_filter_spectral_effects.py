import csv
import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfreqz, welch

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "data/processed/bci_iv_2a_epochs_v1"
FILTERED = ROOT / "data/processed/bci_iv_2a_epochs_8_30hz_v1"
MANIFEST = FILTERED / "preprocessing_manifest.json"
OUT = ROOT / "bci_evidence_experiment/results"

FS = 250
ORDER = 4
LOW_HZ = 8.0
HIGH_HZ = 30.0
N_PER_SEG = 500

BANDS = {
    "delta_1_4Hz": (1.0, 4.0),
    "theta_4_8Hz": (4.0, 8.0),
    "mu_8_13Hz": (8.0, 13.0),
    "beta_13_30Hz": (13.0, 30.0),
    "low_stop_1_7Hz": (1.0, 7.0),
    "high_stop_31_45Hz": (31.0, 45.0),
    "broad_1_45Hz": (1.0, 45.0),
}


def band_power(freqs, psd, low, high):
    mask = (freqs >= low) & (freqs <= high)
    if mask.sum() < 2:
        raise ValueError(f"Insufficient PSD bins for {low}-{high} Hz")
    return np.trapz(psd[..., mask], freqs[mask], axis=-1)


def summarize(values):
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {
            "count": 0,
            "median_db": None,
            "p05_db": None,
            "p95_db": None,
        }
    return {
        "count": int(values.size),
        "median_db": float(np.median(values)),
        "p05_db": float(np.percentile(values, 5)),
        "p95_db": float(np.percentile(values, 95)),
    }


def main():
    if not MANIFEST.exists():
        raise SystemExit(f"Missing preprocessing manifest: {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text())
    baseline_files = sorted(BASELINE.glob("A??[TE]_epochs.npz"))
    filtered_files = sorted(FILTERED.glob("A??[TE].npz"))

    baseline = {p.name.removesuffix("_epochs.npz"): p for p in baseline_files}
    filtered = {p.stem: p for p in filtered_files}

    if set(baseline) != set(filtered):
        raise SystemExit(
            "Session mismatch. "
            f"Missing filtered={sorted(set(baseline)-set(filtered))}; "
            f"unexpected filtered={sorted(set(filtered)-set(baseline))}"
        )

    if len(filtered) != 14:
        raise SystemExit(f"Expected 14 filtered sessions; found {len(filtered)}")

    OUT.mkdir(parents=True, exist_ok=True)

    # Reconstruct the documented fourth-order Butterworth SOS design.
    sos = butter(
        ORDER,
        [LOW_HZ, HIGH_HZ],
        btype="bandpass",
        fs=FS,
        output="sos",
    )
    freqs, response = sosfreqz(sos, worN=16384, fs=FS)
    one_pass_db = 20.0 * np.log10(np.maximum(np.abs(response), 1e-15))
    # Forward-backward filtering squares the one-pass amplitude response.
    forward_backward_db = 2.0 * one_pass_db

    response_path = OUT / "bci_filter_frequency_response.csv"
    with response_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "frequency_hz",
            "one_pass_magnitude_db",
            "forward_backward_magnitude_db",
        ])
        writer.writerows(zip(freqs, one_pass_db, forward_backward_db))

    checkpoints = [1, 4, 6, 7, 8, 10, 13, 20, 30, 31, 35, 45, 50, 60, 100]
    response_checkpoints = []
    for hz in checkpoints:
        idx = int(np.argmin(np.abs(freqs - hz)))
        response_checkpoints.append({
            "frequency_hz": hz,
            "one_pass_db": float(one_pass_db[idx]),
            "forward_backward_db": float(forward_backward_db[idx]),
        })

    rows = []
    session_reports = []

    for session_id in sorted(filtered):
        with np.load(baseline[session_id], allow_pickle=False) as base, \
             np.load(filtered[session_id], allow_pickle=False) as new:

            x_base = np.asarray(base["eeg_uV"], dtype=np.float64)
            x_new = np.asarray(new["eeg_uV"], dtype=np.float64)
            flags = np.asarray(new["artifact_flags"]) != 0

            if x_base.shape != (288, 22, 1000):
                raise ValueError(f"{session_id}: unexpected baseline shape {x_base.shape}")
            if x_new.shape != x_base.shape:
                raise ValueError(f"{session_id}: filtered shape mismatch")
            if not np.isfinite(x_base).all() or not np.isfinite(x_new).all():
                raise ValueError(f"{session_id}: non-finite EEG values")
            if flags.shape != (288,):
                raise ValueError(f"{session_id}: invalid artifact flag shape")

            f_base, p_base = welch(
                x_base, fs=FS, nperseg=N_PER_SEG, axis=-1,
                detrend="constant", scaling="density"
            )
            f_new, p_new = welch(
                x_new, fs=FS, nperseg=N_PER_SEG, axis=-1,
                detrend="constant", scaling="density"
            )

            if not np.array_equal(f_base, f_new):
                raise ValueError("Welch frequency grids differ")

            session_band_results = {}
            for band_name, (lo, hi) in BANDS.items():
                bp_base = band_power(f_base, p_base, lo, hi)
                bp_new = band_power(f_new, p_new, lo, hi)

                ratio_db = 10.0 * np.log10(
                    np.maximum(bp_new, 1e-30) /
                    np.maximum(bp_base, 1e-30)
                )

                clean_summary = summarize(ratio_db[~flags, :])
                artifact_summary = summarize(ratio_db[flags, :])
                all_summary = summarize(ratio_db)

                session_band_results[band_name] = {
                    "all_trials": all_summary,
                    "clean_trials": clean_summary,
                    "artifact_flagged_trials": artifact_summary,
                }

                rows.append({
                    "session": session_id,
                    "band": band_name,
                    "low_hz": lo,
                    "high_hz": hi,
                    "all_median_db": all_summary["median_db"],
                    "all_p05_db": all_summary["p05_db"],
                    "all_p95_db": all_summary["p95_db"],
                    "clean_median_db": clean_summary["median_db"],
                    "artifact_median_db": artifact_summary["median_db"],
                    "artifact_trial_count": int(flags.sum()),
                    "clean_trial_count": int((~flags).sum()),
                })

            session_reports.append({
                "session": session_id,
                "trial_count": int(x_base.shape[0]),
                "artifact_flagged_trials": int(flags.sum()),
                "clean_trials": int((~flags).sum()),
                "baseline_eeg_rms_uV": float(np.sqrt(np.mean(x_base ** 2))),
                "filtered_eeg_rms_uV": float(np.sqrt(np.mean(x_new ** 2))),
                "bands": session_band_results,
            })

        print(
            f"Audited {session_id}: "
            f"{int(flags.sum())}/288 artifact-flagged trials"
        )

    csv_path = OUT / "bci_filter_spectral_effects.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "audit": "BCI IV-2a additional 8-30 Hz filter spectral effects",
        "sampling_rate_hz": FS,
        "filter": {
            "design": "Butterworth band-pass",
            "order": ORDER,
            "passband_hz": [LOW_HZ, HIGH_HZ],
            "application": "zero-phase forward-backward SOS",
            "response_note": (
                "Forward-backward magnitude response is the square "
                "of the one-pass magnitude response."
            ),
        },
        "welch": {
            "nperseg": N_PER_SEG,
            "detrend": "constant",
            "scaling": "density",
        },
        "session_count": len(session_reports),
        "total_trials": sum(s["trial_count"] for s in session_reports),
        "total_artifact_flagged_trials": sum(
            s["artifact_flagged_trials"] for s in session_reports
        ),
        "response_checkpoints": response_checkpoints,
        "sessions": session_reports,
        "files": {
            "frequency_response_csv": str(response_path.relative_to(ROOT)),
            "spectral_effects_csv": str(csv_path.relative_to(ROOT)),
        },
        "preprocessing_manifest": manifest,
    }

    json_path = OUT / "bci_filter_spectral_audit.json"
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    print("\nFILTER RESPONSE: forward-backward magnitude")
    for item in response_checkpoints:
        print(
            f"{item['frequency_hz']:>5} Hz: "
            f"{item['forward_backward_db']:>8.2f} dB"
        )

    print("\nSPECTRAL EFFECTS: median filtered/baseline power change")
    for band_name in BANDS:
        vals = [
            s["bands"][band_name]["all_trials"]["median_db"]
            for s in session_reports
        ]
        print(
            f"{band_name:>20}: "
            f"median across sessions={np.median(vals):.2f} dB"
        )

    print("\nAUDIT COMPLETE")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print(f"CSV:  {response_path}")


if __name__ == "__main__":
    main()
