"""Run the feasibility experiment.

Usage:
  python3 run_experiment.py --split dev
  python3 run_experiment.py --split eval --budget 900
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from src.bench import BUDGET_OPS, annotate_effects, run_episode  # noqa: E402
from src.graph import make_case  # noqa: E402
from src.models import build_models  # noqa: E402

SPLITS = {
    "dev": list(range(0, 40)),
    "val": list(range(40, 60)),
    "eval": list(range(60, 160)),
}


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: str, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=sorted(SPLITS))
    ap.add_argument("--cases", type=int, default=None)
    ap.add_argument("--budget", type=int, default=BUDGET_OPS)
    ap.add_argument("--models", default="A,B,C,D,Dc,E1,E2")
    ap.add_argument("--out-dir", default=os.path.join(HERE, "results", "raw"))
    args = ap.parse_args(argv)

    ids = SPLITS[args.split]
    if args.cases is not None:
        ids = ids[:args.cases]
    wanted = [m.strip() for m in args.models.split(",") if m.strip()]

    os.makedirs(args.out_dir, exist_ok=True)
    runs, events, decisions = [], [], []
    cases = []
    t0 = time.perf_counter()

    for cid in ids:
        case = make_case(cid)
        cases.append(case.to_json())
        for name in wanted:
            models = build_models()
            model = models[name]
            ep = run_episode(case, model, budget_ops=args.budget)
            annotate_effects(ep.events, model.applied_log)
            runs.append(ep.metrics)
            events.extend(ep.events)
            decisions.extend(ep.decisions)

    elapsed = time.perf_counter() - t0
    write_csv(os.path.join(args.out_dir, f"{args.split}_runs.csv"), runs)
    write_csv(os.path.join(args.out_dir, f"{args.split}_events.csv"), events)
    write_csv(os.path.join(args.out_dir, f"{args.split}_decisions.csv"), decisions)
    with open(os.path.join(args.out_dir, f"{args.split}_cases.json"), "w",
              encoding="utf-8") as f:
        json.dump(cases, f, indent=1)

    manifest = dict(
        split=args.split, case_ids=ids, budget=args.budget, models=wanted,
        elapsed_s=round(elapsed, 3),
        python=sys.version, platform=platform.platform(),
        files={os.path.relpath(p, HERE): md5(p) for p in [
            os.path.join(HERE, "src", "graph.py"),
            os.path.join(HERE, "src", "rules.py"),
            os.path.join(HERE, "src", "models.py"),
            os.path.join(HERE, "src", "bench.py"),
            os.path.join(HERE, "run_experiment.py"),
        ]},
    )
    with open(os.path.join(args.out_dir, f"{args.split}_manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"{args.split}: {len(ids)} cases x {len(wanted)} models in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
