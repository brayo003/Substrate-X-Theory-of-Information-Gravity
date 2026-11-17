from pathlib import Path
import numpy as np
import scipy.io

SOURCE = Path(
    "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"
)
OUTPUT = Path("data/processed/bci_iv_2a_epochs_v1")

def get_entries(path):
    mat = scipy.io.loadmat(
        path,
        squeeze_me=True,
        struct_as_record=False
    )
    return np.atleast_1d(mat["data"]).ravel()

def get_field(entry, name):
    return np.asarray(getattr(entry, name))

def main(stem="A01E"):
    source_path = SOURCE / f"{stem}.mat"
    output_path = OUTPUT / f"{stem}_epochs.npz"

    entries = get_entries(source_path)

    annotated = [
        e for e in entries
        if get_field(e, "trial").size > 0
    ]

    entry = annotated[0]
    signal = get_field(entry, "X").astype(np.float32)
    marker = int(get_field(entry, "trial").ravel()[0])
    event_index = marker - 1

    start = event_index + 500
    stop = event_index + 1500

    raw_epoch = signal[start:stop].T

    with np.load(output_path, allow_pickle=True) as saved:
        saved_epoch = saved["eeg_uV"][0]
        saved_names = saved["eeg_channel_names"].tolist()

    print("=" * 72)
    print("CHANNEL MAPPING DIAGNOSTIC:", stem)
    print("=" * 72)

    print("Original signal shape:", signal.shape)
    print("Original epoch shape:", raw_epoch.shape)
    print("Saved epoch shape:", saved_epoch.shape)

    print("\nSaved EEG channel order:")
    for i, name in enumerate(saved_names):
        print(f"  {i:2d}: {name}")

    print("\nDirect comparison by channel position:")
    for i, name in enumerate(saved_names):
        diff = np.max(np.abs(raw_epoch[i] - saved_epoch[i]))
        print(f"  {name:5s}: max difference={diff:.6f}")

    print("\nBest original channel for each saved channel:")
    for i, name in enumerate(saved_names):
        errors = np.max(
            np.abs(raw_epoch - saved_epoch[i][None, :]),
            axis=1
        )
        best = int(np.argmin(errors))
        print(
            f"  saved {name:5s} -> original column {best:2d}; "
            f"minimum max-error={errors[best]:.6f}"
        )

    print("\nOriginal raw signal statistics:")
    print("  min:", float(signal.min()))
    print("  max:", float(signal.max()))
    print("  mean:", float(signal.mean()))
    print("  std:", float(signal.std()))

    print("\nSaved epoch statistics:")
    print("  min:", float(saved_epoch.min()))
    print("  max:", float(saved_epoch.max()))
    print("  mean:", float(saved_epoch.mean()))
    print("  std:", float(saved_epoch.std()))

    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()
