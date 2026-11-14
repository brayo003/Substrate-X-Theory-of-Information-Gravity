#!/usr/bin/env python3
"""
EXP8 — Substrate computational expressivity (Track C)
=====================================================

Follow-up to Task 7 (Outcome C, Level 3). Does not modify Task 6/7 artifacts.

Usage:
  python exp8_substrate_computational_expressivity.py --pilot
  python exp8_substrate_computational_expressivity.py
  python exp8_substrate_computational_expressivity.py --seeds 24
  python exp8_substrate_computational_expressivity.py --numerical-only
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

from sim_world.exp8.numerical_validation import run_numerical_suite
from sim_world.exp8.runner import run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--seeds", type=int, default=None, help="Confirmatory N")
    ap.add_argument("--numerical-only", action="store_true")
    ap.add_argument("--skip-bridge", action="store_true")
    ap.add_argument("--out-dir", default=_HERE)
    args = ap.parse_args()

    if args.numerical_only:
        r = run_numerical_suite()
        print(json.dumps(r, indent=2, default=str))
        return

    run_pipeline(
        out_dir=args.out_dir,
        pilot_only=args.pilot,
        confirm_n=args.seeds,
        verbose=True,
        skip_bridge=args.skip_bridge,
    )


if __name__ == "__main__":
    main()
