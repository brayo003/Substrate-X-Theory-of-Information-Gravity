from pathlib import Path
import numpy as np

ROOT = Path("data/processed/bci_iv_2a_epochs_v1")

print("=" * 72)
print("EXTREME SAMPLE INVESTIGATION")
print("=" * 72)

for path in sorted(ROOT.glob("*_epochs.npz")):
    with np.load(path, allow_pickle=True) as d:
        eeg = d["eeg_uV"]
        labels = d["labels"]
        flags = d["artifact_flags"]
        runs = d["run_ids"]
        trials = d["trial_ids"]
        channels = d["eeg_channel_names"].tolist()

        # Exact and near-boundary values
        exact_negative = np.argwhere(eeg == -1000.0)
        near_negative = np.argwhere(eeg <= -900.0)
        high_positive = np.argwhere(eeg >= 300.0)

        if not (len(exact_negative) or len(near_negative) or len(high_positive)):
            continue

        print(f"\n{path.name}")
        print("  Exact -1000 uV samples:", len(exact_negative))
        print("  Samples <= -900 uV:", len(near_negative))
        print("  Samples >= 300 uV:", len(high_positive))

        affected = set()

        for indices, description in [
            (exact_negative, "EXACT -1000"),
            (near_negative, "<= -900"),
            (high_positive, ">= 300"),
        ]:
            for trial_idx, channel_idx, sample_idx in indices:
                affected.add(int(trial_idx))

        for trial_idx in sorted(affected):
            signal = eeg[trial_idx]
            peak_idx = np.unravel_index(
                np.argmax(np.abs(signal)), signal.shape
            )
            channel_idx, sample_idx = peak_idx

            print(
                f"  Trial array index={trial_idx + 1}, "
                f"run={runs[trial_idx]}, trial={trials[trial_idx]}, "
                f"class={labels[trial_idx]}, "
                f"artifact={flags[trial_idx]}, "
                f"peak={signal[channel_idx, sample_idx]:.3f} uV, "
                f"channel={channels[channel_idx]}, "
                f"sample_in_epoch={sample_idx}"
            )

print("\n" + "=" * 72)
print("COMPLETED")
print("=" * 72)
