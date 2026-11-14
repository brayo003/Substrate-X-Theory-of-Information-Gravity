#!/usr/bin/env python3
"""
EXP7 — Nonlinear-specific computational advantage & behavioural utility
======================================================================

Follow-up to Corrective Task 6 (Outcome B, Level 3). Does not modify Task 6 files.

Usage:
  python exp7_nonlinear_specific_advantage.py --pilot
  python exp7_nonlinear_specific_advantage.py
  python exp7_nonlinear_specific_advantage.py --seeds 40
  python exp7_nonlinear_specific_advantage.py --integrity-only
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

from sim_world.exp7.integrity import run_t1_t2
from sim_world.exp7.runner import run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--integrity-only", action="store_true")
    ap.add_argument("--out-dir", default=_HERE)
    args = ap.parse_args()

    if args.integrity_only:
        r = run_t1_t2()
        print(json.dumps({"T1": r["T1"]["pass"], "T2": r["T2"]["pass"]}, indent=2))
        return

    run_pipeline(
        out_dir=args.out_dir,
        pilot_only=args.pilot,
        confirm_n=args.seeds,
        verbose=True,
    )


if __name__ == "__main__":
    main()
