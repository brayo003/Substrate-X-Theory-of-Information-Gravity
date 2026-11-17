from pathlib import Path
import numpy as np
from scipy.io import loadmat

SOURCE = Path("data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata")

def get_field(entry, name):
    if hasattr(entry, name):
        return getattr(entry, name)
    if isinstance(entry, dict):
        return entry.get(name)
    return None

for path in sorted(SOURCE.glob("A??[TE].mat")):
    if path.stem == "A09E":
        print(f"\n{path.name}: SKIPPED (known corrupt source)")
        continue

    print(f"\n{'=' * 65}\n{path.name}")
    try:
        mat = loadmat(path, squeeze_me=True, struct_as_record=False)
        data = np.asarray(mat["data"], dtype=object).reshape(-1)
        print(f"Top-level data entries: {len(data)}")

        annotated = 0
        for i, entry in enumerate(data, start=1):
            fields = {}
            for name in ("X", "trial", "y", "fs", "artifacts"):
                value = get_field(entry, name)
                if value is None:
                    fields[name] = "MISSING"
                else:
                    arr = np.asarray(value)
                    fields[name] = {
                        "shape": arr.shape,
                        "size": int(arr.size),
                    }

            trial = get_field(entry, "trial")
            labels = get_field(entry, "y")
            x = get_field(entry, "X")

            n_trials = 0 if trial is None else np.asarray(trial).size
            n_labels = 0 if labels is None else np.asarray(labels).size
            valid = (
                x is not None
                and trial is not None
                and labels is not None
                and n_trials == 48
                and n_labels == 48
            )

            if valid:
                annotated += 1

            print(
                f"  entry {i}: {'ANNOTATED' if valid else 'not annotated'} "
                f"| trials={n_trials} | labels={n_labels} "
                f"| fields={fields}"
            )

        print(f"Annotated 48-trial runs: {annotated}")

    except Exception as exc:
        print(f"READ ERROR: {type(exc).__name__}: {exc}")
