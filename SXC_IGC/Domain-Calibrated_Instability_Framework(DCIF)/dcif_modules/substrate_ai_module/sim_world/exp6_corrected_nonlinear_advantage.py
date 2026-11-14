#!/usr/bin/env python3
"""
EXP6 CORRECTED — Nonlinear Substrate Capability & Advantage Protocol
====================================================================

Corrective re-implementation of Task 6. Original files are preserved:
  exp6_nonlinear_advantage.py, exp6_pilot_results.json, exp6_results.json,
  EXP6_NONLINEAR_ADVANTAGE_REPORT.md

This entry point runs the mandatory gate sequence and experiments A/B/C.

Usage
-----
  python exp6_corrected_nonlinear_advantage.py --pilot
  python exp6_corrected_nonlinear_advantage.py --seeds 30
  python exp6_corrected_nonlinear_advantage.py --gates-only
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in (_PARENT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.exp6_corrected.math_gates import run_math_gates
from sim_world.exp6_corrected.oracle_tests import run_oracle_gates
from sim_world.exp6_corrected.runner import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Corrected Task 6 experiment")
    parser.add_argument("--pilot", action="store_true", help="Pilot only")
    parser.add_argument("--seeds", type=int, default=None,
                        help="Confirmatory N (default: from pilot power estimate)")
    parser.add_argument("--gates-only", action="store_true",
                        help="Run G1–G4 only")
    parser.add_argument("--out-dir", default=_HERE)
    args = parser.parse_args()

    if args.gates_only:
        math = run_math_gates()
        oracle = run_oracle_gates()
        summary = {
            "G1": math["G1"]["pass"],
            "G2": math["G2"]["pass"],
            "G3": oracle["G3"]["pass"],
            "G4": oracle["G4"]["pass"],
            "G1_checks": {k: v.get("pass") for k, v in math["G1"]["checks"].items()},
            "G2_tests": {k: v.get("pass") for k, v in math["G2"]["tests"].items()},
        }
        print(json.dumps(summary, indent=2))
        path = os.path.join(args.out_dir, "exp6_corrected_gate_log.json")
        with open(path, "w") as f:
            json.dump({"math": math, "oracle": oracle}, f, indent=2, default=str)
        print(f"Wrote {path}")
        return

    run_pipeline(
        out_dir=args.out_dir,
        pilot_only=args.pilot,
        confirm_n=args.seeds,
        verbose=True,
    )


if __name__ == "__main__":
    main()
