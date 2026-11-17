import inspect
import importlib
import importlib.util
from pathlib import Path

print("=" * 70)
print("MOABB ENVIRONMENT")
print("=" * 70)

try:
    import moabb
    print("MOABB version:", getattr(moabb, "__version__", "unknown"))
    print("MOABB location:", moabb.__file__)
except Exception as e:
    print("MOABB import failed:", repr(e))
    raise SystemExit(1)

print("\n" + "=" * 70)
print("BNCI2014_001 LOADER SOURCE")
print("=" * 70)

modules = [
    "moabb.datasets.bnci",
    "moabb.datasets",
]

found = False

for module_name in modules:
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        print(f"Could not import {module_name}: {e}")
        continue

    cls = getattr(module, "BNCI2014_001", None)
    if cls is None:
        continue

    found = True
    print(f"\nClass found in: {module_name}")
    try:
        print(inspect.getsource(cls))
    except Exception as e:
        print("Could not retrieve class source:", e)

if not found:
    print("BNCI2014_001 class not found through expected imports.")

print("\n" + "=" * 70)
print("RELEVANT SOURCE SEARCH")
print("=" * 70)

spec = importlib.util.find_spec("moabb")
if spec and spec.origin:
    root = Path(spec.origin).parent
    terms = (
        "trial",
        "event",
        "tmin",
        "tmax",
        "loadmat",
        "BNCI2014_001",
        "1:3",
        "1-based",
    )

    for path in root.rglob("*.py"):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except Exception:
            continue

        matches = [
            (i + 1, line.strip())
            for i, line in enumerate(lines)
            if any(term.lower() in line.lower() for term in terms)
        ]

        if matches:
            print(f"\n--- {path} ---")
            for line_no, line in matches[:80]:
                print(f"{line_no}: {line}")

print("\nInspection complete. No files were modified.")
