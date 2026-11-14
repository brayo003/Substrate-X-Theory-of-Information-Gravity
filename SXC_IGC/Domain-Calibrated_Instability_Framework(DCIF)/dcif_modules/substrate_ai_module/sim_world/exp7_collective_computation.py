#!/usr/bin/env python3
"""CLI: Task 7 Track B — nonlinear-specific computational challenges."""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from sim_world.exp7.collective_computation import run_track_b
from sim_world.exp7.integrity import run_t1_t2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("-o", "--out", default="exp7_track_b_results.json")
    args = p.parse_args()
    integ = run_t1_t2()
    if not integ["proceed"]:
        print("BLOCKED: T1/T2 failed")
        sys.exit(2)
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    result = run_track_b(seeds, verbose=True)
    bundle = {
        "integrity": integ,
        "and_summary": result["and_summary"],
        "ablation_summary": result["ablation_summary"],
        "secondary_summary": result["secondary_summary"],
        "gates": {k: result[k] for k in ("T7", "T8", "T9")},
        "and_trials": result["and_trials"],
        "ablation_trials": result["ablation_trials"],
        "n_seeds": len(seeds),
        "encoding_note": result["encoding_note"],
    }
    with open(args.out, "w") as f:
        json.dump(bundle, f, indent=2, default=str)
    print("Wrote", args.out)
    print("Gates:", {k: result[k]["pass"] for k in ("T7", "T8", "T9")})


if __name__ == "__main__":
    main()
