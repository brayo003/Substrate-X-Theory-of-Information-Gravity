#!/usr/bin/env python3
"""CLI: Task 7 Track A — hazard discoverer→recipient behavioural utility."""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from sim_world.exp7 import config as cfg
from sim_world.exp7.hazard_behaviour import run_track_a
from sim_world.exp7.integrity import run_t1_t2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("-o", "--out", default="exp7_track_a_results.json")
    args = p.parse_args()
    integ = run_t1_t2()
    if not integ["proceed"]:
        print("BLOCKED: T1/T2 failed")
        sys.exit(2)
    seeds = list(range(args.seed_start, args.seed_start + args.seeds))
    result = run_track_a(seeds, verbose=True)
    bundle = {
        "integrity": integ,
        "summary": result["summary"],
        "gates": {k: result[k] for k in ("T3", "T4", "T5", "T6")},
        "gates_by_condition": result["gates_by_condition"],
        "trials": result["trials"],
        "n_seeds": len(seeds),
    }
    with open(args.out, "w") as f:
        json.dump(bundle, f, indent=2, default=str)
    print("Wrote", args.out)
    print("Gates:", {k: result[k]["pass"] for k in ("T3", "T4", "T5", "T6")})


if __name__ == "__main__":
    main()
