#!/usr/bin/env python3
"""CLI for the distributed evidence integration benchmark."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from evidence_benchmark.analysis import (
    plot_accuracy_over_time,
    plot_agreement_over_time,
    plot_d_vs_cr_paired,
    regenerate_report_from_csvs,
    write_experiment_report,
)
from evidence_benchmark.conditions import build_matrix
from evidence_benchmark.experiment import DEFAULT_OUT, run_full_experiment
from evidence_benchmark.tests import run_all_tests


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Evidence integration benchmark")
    p.add_argument("--test", action="store_true", help="Run correctness tests")
    p.add_argument("--smoke", action="store_true", help="Smoke experiment (5 seeds)")
    p.add_argument("--full", action="store_true", help="Full matrix experiment")
    p.add_argument("--report-only", action="store_true",
                   help="Regenerate report/verdict from saved CSVs (no re-run)")
    p.add_argument("--seeds", type=int, default=100, help="Number of paired seeds")
    p.add_argument("--out", type=str, default=DEFAULT_OUT, help="Output directory")
    p.add_argument("--skip-tests", action="store_true")
    args = p.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)

    # Copy specification into output
    spec_src = os.path.join(os.path.dirname(__file__), "benchmark_specification.md")
    if os.path.isfile(spec_src):
        shutil.copy2(spec_src, os.path.join(args.out, "benchmark_specification.md"))
        # Also place at package-adjacent deliverable path expected by brief
        shutil.copy2(spec_src, os.path.join(_ROOT, "benchmark_specification.md"))

    if args.report_only:
        path = regenerate_report_from_csvs(args.out)
        print(f"Regenerated report: {path}")
        return 0

    test_results = {}
    if args.test or args.smoke or args.full:
        if not args.skip_tests or args.test:
            print("=== Correctness tests ===")
            test_results = run_all_tests()
            with open(os.path.join(args.out, "test_results.json"), "w") as f:
                json.dump(test_results, f, indent=2)
            n_pass = sum(1 for v in test_results.values() if v == "PASS")
            if n_pass != len(test_results):
                print("TESTS FAILED — aborting experiment run")
                return 2
            if args.test and not (args.smoke or args.full):
                return 0

    if args.smoke:
        seeds = list(range(min(5, args.seeds)))
        print(f"=== Smoke experiment ({len(seeds)} seeds) ===")
        result = run_full_experiment(seeds=seeds, out_dir=args.out, smoke=True)
    elif args.full:
        seeds = list(range(args.seeds))
        print(f"=== Full experiment ({len(seeds)} seeds, "
              f"{len(build_matrix())} conditions) ===")
        result = run_full_experiment(seeds=seeds, out_dir=args.out, smoke=False)
    else:
        print("Specify --test, --smoke, --full, and/or --report-only")
        return 1

    # Figures for baseline (or smoke)
    cid = result["conditions"][0].condition_id
    plot_ids = {c.condition_id for c in result["conditions"]}
    for plot_cid in (("baseline",) if "baseline" in plot_ids else (cid,)):
        plot_accuracy_over_time(result["time_rows"], args.out, plot_cid)
        plot_agreement_over_time(result["time_rows"], args.out, plot_cid)
        plot_d_vs_cr_paired(result["analysis"]["paired"], args.out, plot_cid)
    # Also plot a few key conditions if present
    for extra in ("failures", "adversarial", "budget_low", "uneven"):
        if extra in plot_ids:
            plot_accuracy_over_time(result["time_rows"], args.out, extra)

    if not test_results and os.path.isfile(os.path.join(args.out, "test_results.json")):
        test_results = json.load(open(os.path.join(args.out, "test_results.json")))

    write_experiment_report(
        args.out, result["config"], result["analysis"],
        test_results, result["conditions"])
    print(f"\nDone. Results in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
