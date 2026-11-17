from pathlib import Path
import scipy.io
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata"

TARGETS = ["A03E", "A04T", "A08T"]

def describe(value, name, depth=0):
    indent = "  " * depth

    if isinstance(value, np.ndarray):
        print(
            f"{indent}{name}: ndarray "
            f"shape={value.shape}, dtype={value.dtype}"
        )

        if value.dtype == object and depth < 3:
            for i, item in enumerate(value.flat[:8]):
                describe(item, f"{name}[{i}]", depth + 1)

    elif hasattr(value, "_fieldnames"):
        print(f"{indent}{name}: MATLAB struct")
        for field in value._fieldnames:
            describe(getattr(value, field), field, depth + 1)

    else:
        print(f"{indent}{name}: {type(value).__name__} = {str(value)[:160]}")

for session in TARGETS:
    matches = list(SOURCE.rglob(f"{session}.mat"))

    print("\n" + "=" * 80)
    print(f"SESSION: {session}")
    print("MATCHES:", matches)

    if len(matches) != 1:
        print("Expected exactly one source MAT file; skipping.")
        continue

    path = matches[0]
    print("FILE:", path)

    data = scipy.io.loadmat(path, squeeze_me=True, struct_as_record=False)

    for key, value in data.items():
        if key.startswith("__"):
            continue
        describe(value, key)
