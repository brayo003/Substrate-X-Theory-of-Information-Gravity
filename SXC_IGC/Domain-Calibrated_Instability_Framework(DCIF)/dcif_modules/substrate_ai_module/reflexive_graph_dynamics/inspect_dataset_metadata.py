from pathlib import Path
import scipy.io
import numpy as np

root = Path("data/nm000139/data.nemar.org/nm000139/v1.0.3")

print("DATASET ROOT:", root.resolve())
print("\nMETADATA FILES:")
for p in root.rglob("*"):
    if p.is_file() and (
        p.name.lower().startswith(("readme", "dataset", "participants", "description"))
        or p.suffix.lower() in (".json", ".tsv", ".txt")
    ):
        print(p.relative_to(root))

print("\nMAT FILE STRUCTURE:")
for p in sorted((root / "sourcedata").glob("A01*.mat")):
    print(f"\nFILE: {p.name}")
    try:
        mat = scipy.io.loadmat(p, squeeze_me=True, struct_as_record=False)
        data = mat["data"]
        entries = np.atleast_1d(data)

        for i, entry in enumerate(entries, start=1):
            x = np.asarray(entry.X)
            trial = np.asarray(entry.trial).reshape(-1)
            y = np.asarray(entry.y).reshape(-1)
            fs = np.asarray(entry.fs).reshape(-1)

            print(
                f"entry={i}, X_shape={x.shape}, "
                f"trial_count={len(trial)}, label_count={len(y)}, "
                f"fs={fs.tolist()}"
            )
            if len(trial):
                print("  first trial positions:", trial[:5].tolist())
                print("  first labels:", y[:5].tolist())
                print("  first channel min/max:", float(np.nanmin(x[:, 0])),
                      float(np.nanmax(x[:, 0])))
    except Exception as e:
        print("READ ERROR:", repr(e))
