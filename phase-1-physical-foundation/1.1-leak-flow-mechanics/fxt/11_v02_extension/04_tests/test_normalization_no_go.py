"""Executable v02 entry test: verify the frozen normalization obstruction.

This does not derive a bridge.  It guards against accidentally treating a
normalization convention as a prediction.
"""
import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

def main():
    a, g, s0, J, r, tau, hbar, omega = sp.symbols(
        "a g s0 J r tau hbar omega", positive=True
    )
    h_int = g * J
    gamma = 8 * g**2 * s0**2 * r**2 * tau * omega**2 / (3 * hbar**2)
    transformed = {g: g/a, s0: a*s0, J: a*J}
    checks = {
        "interaction_invariant": sp.simplify(h_int.subs(transformed) - h_int) == 0,
        "rate_invariant": sp.simplify(gamma.subs(transformed) - gamma) == 0,
        "g_changes_with_normalization": sp.simplify((g/a) - g) != 0,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "transformation": "s,J,s0 -> a(s,J,s0); g -> g/a",
        "checks": {k: bool(v) for k, v in checks.items()},
        "conclusion": (
            "The frozen equations determine only normalization-invariant products; "
            "they cannot numerically determine g without an additional bridge "
            "or independent calibration."
        ),
    }
    (OUT / "normalization_no_go.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "normalization_no_go.log").write_text("v02 normalization no-go test\nSTATUS: %s\n" % result["status"])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
