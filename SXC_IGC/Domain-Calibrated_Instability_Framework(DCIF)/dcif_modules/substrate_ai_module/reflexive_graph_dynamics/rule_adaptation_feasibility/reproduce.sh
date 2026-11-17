#!/usr/bin/env bash
# Reproduce the endogenous rule-adaptation feasibility study end to end.
#
# Usage:  bash reproduce.sh
#
# Everything runs inside this directory. No network, no system temp files.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PYTHON:-python3}"
BUDGET="${BUDGET:-900}"

echo "== 1. Verify frozen source and configuration =="
sha256sum -c config/SOURCE_HASHES.txt

echo
echo "== 2. Environment =="
"$PY" -V
"$PY" - <<'EOF'
import numpy, scipy, pandas
print("numpy", numpy.__version__, "| scipy", scipy.__version__, "| pandas", pandas.__version__)
EOF

echo
echo "== 3. Run splits =="
mkdir -p logs results/raw results/analysis
for split in dev val eval; do
    echo "-- $split"
    "$PY" run_experiment.py --split "$split" --budget "$BUDGET" \
        | tee "logs/run_${split}.log"
done

echo
echo "== 4. Analysis =="
"$PY" analysis.py | tee logs/analysis.log

echo
echo "== 5. Re-verify frozen source (nothing may have changed) =="
sha256sum -c config/SOURCE_HASHES.txt

echo
echo "== 6. Reproducibility check against frozen verdict inputs =="
"$PY" - <<'EOF'
import csv, collections, sys

expected = {"A": 22, "B": 96, "C": 82, "D": 68, "Dc": 70, "E1": 96, "E2": 8}
rows = list(csv.DictReader(open("results/raw/eval_runs.csv")))
counts = collections.Counter()
total_viol = collections.Counter()
for r in rows:
    counts[r["model"]] += int(float(r["success"]))
    total_viol[r["model"]] += int(float(r["final_violations"]))

ok = True
print(f"{'model':5s} {'success':>8s} {'expected':>9s} {'total violations':>18s}")
for m in ["A", "B", "C", "D", "Dc", "E1", "E2"]:
    match = counts[m] == expected[m]
    ok = ok and match
    print(f"{m:5s} {counts[m]:8d} {expected[m]:9d} {total_viol[m]:18d} {'OK' if match else 'MISMATCH'}")

if not ok:
    print("\nREPRODUCTION FAILED: success counts differ from the frozen run.")
    sys.exit(1)
print("\nREPRODUCTION OK: held-out success counts match the frozen run.")
EOF

echo
echo "== 7. Deliverables =="
ls -1 RESEARCH_REVIEW.md CAPABILITY_SPECIFICATION.md BENCHMARK_SPECIFICATION.md \
      MODEL_DESIGN.md IMPLEMENTATION_REPORT.md EXPERIMENT_RESULTS.md \
      MODEL_COMPARISON.csv PAIRED_STATISTICS.csv RULE_EVOLUTION_LOG.csv \
      COMPLEXITY_METRICS.csv LIMITATIONS.md FINAL_VERDICT.md reproduce.sh

echo
echo "Verdict: see FINAL_VERDICT.md (B — REDUNDANT)."
echo "Note: only wall-clock columns (runtime_s) vary between runs; every"
echo "behavioural column and every table entry derived from it is deterministic."
