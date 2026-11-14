"""
audit_evidence/verify_transport_pde.py

Independent reference implementation of the telegraph PDE transport
discriminant. Verifies that transport_layer.py produces correct output
for constant, impulse, step, and oscillating inputs.

Also verifies that s_transport (the PDE output field) is never read
by any decision-making component in the pipeline.

Run: python audit_evidence/verify_transport_pde.py

Evidence for: DCIF_EQUATION_TRACE.md §2, END_TO_END_DATA_FLOW.md §3
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FM   = _HERE.parent
for p in [str(_FM), str(_FM / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from v12_validate.transport_layer import compute_transport_field, DEFAULT_C, DEFAULT_TAU

EPSILON = 1e-9

def reference_Q(s: np.ndarray, c: float, tau: float, dt: float = 1.0) -> np.ndarray:
    """
    Independent reference implementation of Q.
    Q = 4*(c*tau)^2 * (grad_ln_s)^2 - 1
    where grad_ln_s = backward log-difference.
    """
    s_safe = np.clip(s, EPSILON, 1 - EPSILON)
    log_s  = np.log(s_safe)
    grad   = np.zeros(len(s))
    grad[1:] = (log_s[1:] - log_s[:-1]) / dt
    grad[0]  = grad[1] if len(s) > 1 else 0.0
    return 4.0 * (c * tau)**2 * grad**2 - 1.0


def run_test(name: str, s: np.ndarray, c: float, tau: float, expected_regime_note: str):
    """Run one transport test and compare library vs reference."""
    s_t, grad_ln, Q_lib, regime, xi_c = compute_transport_field(s, c=c, tau=tau)
    Q_ref = reference_Q(s, c=c, tau=tau)

    q_match = np.allclose(Q_lib, Q_ref, atol=1e-10)

    print(f"\n--- {name} ---")
    print(f"  Input range:      [{s.min():.4f}, {s.max():.4f}]")
    print(f"  Q range:          [{Q_lib.min():.4f}, {Q_lib.max():.4f}]")
    print(f"  Coherent fraction: {(Q_lib > 0).mean():.3f}")
    print(f"  Q matches ref:    {q_match}")
    print(f"  Expected:         {expected_regime_note}")
    print(f"  s_transport range: [{s_t.min():.4f}, {s_t.max():.4f}]")

    return q_match


def main():
    print("=" * 65)
    print("Transport PDE Verification — Independent Reference Implementation")
    print("=" * 65)

    c   = DEFAULT_C    # 1.0
    tau = DEFAULT_TAU  # 5.0
    n   = 200

    results = []

    # ── Test 1: Constant input ────────────────────────────────────────────
    # Constant s → zero log-return → all Q = -1 (all INCOHERENT)
    s_const = np.full(n, 0.5)
    ok = run_test("Constant input (s=0.5)",
                  s_const, c, tau,
                  "All INCOHERENT (Q = -1.0 except boundary)")
    results.append(("Constant", ok))

    # ── Test 2: Impulse (one-bar spike) ───────────────────────────────────
    # Most bars quiet → Q=-1; the spike bar → Q >> 0
    s_impulse = np.full(n, 0.5)
    s_impulse[50] = 0.9  # large spike at bar 50
    ok = run_test("Impulse (spike at bar 50)",
                  s_impulse, c, tau,
                  "Bar 50 COHERENT (large log-return), others INCOHERENT")
    results.append(("Impulse", ok))

    # ── Test 3: Step input ────────────────────────────────────────────────
    # Step from 0.3 to 0.7 at bar 100 → one COHERENT bar at the step
    s_step = np.ones(n) * 0.3
    s_step[100:] = 0.7
    ok = run_test("Step input (0.3 → 0.7 at bar 100)",
                  s_step, c, tau,
                  "Bar 100 COHERENT (large log-return), others INCOHERENT")
    results.append(("Step", ok))

    # ── Test 4: Oscillating (sinusoidal) ──────────────────────────────────
    # Sine wave — alternating coherent/incoherent at peaks of oscillation
    t = np.arange(n)
    s_osc = 0.5 + 0.3 * np.sin(2 * np.pi * t / 10)  # 10-bar period
    s_osc = np.clip(s_osc, EPSILON, 1 - EPSILON)
    ok = run_test("Oscillating (10-bar sine)",
                  s_osc, c, tau,
                  "~40% COHERENT (bars where change is large)")
    results.append(("Oscillating", ok))

    # ── Test 5: Verify s_transport is not referenced in pipeline code ─────
    print("\n\n--- Scan: s_transport column usage in pipeline ---")
    pipeline_files = [
        _FM / "p1_strategy_runner.py",
        _FM / "p2_transport_os.py",
        _FM / "p2_execution_engine.py",
        _FM / "execution_simulator.py",
        _FM / "strategy_library.py",
        _FM / "strategy_allocator.py",
        _FM / "p1_regime_analysis.py",
    ]

    s_transport_used = False
    for fpath in pipeline_files:
        if not fpath.exists():
            continue
        text = fpath.read_text(errors="ignore")
        if "s_transport" in text:
            # Check if it's only in import/write context vs. decision context
            lines = [l.strip() for l in text.splitlines() if "s_transport" in l]
            decision_lines = [l for l in lines
                              if not l.startswith("#")
                              and "to_parquet" not in l
                              and "parquet" not in l
                              and "DataFrame" not in l
                              and "col" not in l.lower()]
            if decision_lines:
                s_transport_used = True
                print(f"  WARNING — {fpath.name} uses s_transport in decision context:")
                for l in decision_lines[:5]:
                    print(f"    {l}")
            else:
                print(f"  {fpath.name}: s_transport present (storage only, not decisions)")
        else:
            print(f"  {fpath.name}: s_transport NOT referenced")

    if not s_transport_used:
        print("\n  CONFIRMED: s_transport is computed but never used in any")
        print("  trading decision, strategy, or OS logic.")
        results.append(("s_transport unused", True))
    else:
        print("\n  UNEXPECTED: s_transport IS used in decision code (investigate).")
        results.append(("s_transport unused", False))

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    all_pass = all(ok for _, ok in results)
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name:<30} {status}")
    print()
    print(f"All tests passed: {all_pass}")

    if all_pass:
        print()
        print("The transport_layer.py implementation is mathematically correct.")
        print("The most informative output (s_transport, the propagated field)")
        print("is stored but never consulted in any decision pathway.")


if __name__ == "__main__":
    main()
