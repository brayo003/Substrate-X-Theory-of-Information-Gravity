#!/usr/bin/env bash
# Reproduce the Endogenous Distinguishability execution end to end.
#
#   ./reproduce.sh
#
# Writes only inside this workspace.  The original project tree and the frozen
# V2 archive are never touched.  Workspace-local outputs are regenerated in
# place; the archived reference run (../experiment_results4) is read-only.
set -euo pipefail

cd "$(dirname "$0")"
ROOT="$(pwd)"
mkdir -p logs results/primary results/controls results/analysis

echo "== environment =="
python3 - <<'PY'
import platform, sys
try:
    import numpy, scipy, networkx
    extra = f"numpy={numpy.__version__} scipy={scipy.__version__} networkx={networkx.__version__}"
except Exception as exc:  # pragma: no cover
    extra = f"missing analysis dependency: {exc}"
print(platform.platform())
print(sys.version.split()[0], extra)
PY

echo "== source integrity =="
EXPECTED_MD5="9b73b12efc1c43b1a22c99ec2cfac03d"
ACTUAL_MD5="$(md5sum one.py | awk '{print $1}')"
if [ "$ACTUAL_MD5" != "$EXPECTED_MD5" ]; then
  echo "FATAL: one.py md5 $ACTUAL_MD5 != $EXPECTED_MD5" >&2
  exit 1
fi
echo "one.py md5 OK ($ACTUAL_MD5)"

echo "== unit tests and diagnostic gates (24 tests) =="
( cd results/primary && python3 ../../one.py --test ) | tee logs/tests.log

echo "== primary run: A/B/C/D/CR, 100 paired seeds, 100 steps =="
( cd results/primary && time python3 ../../one.py --seeds 100 ) \
  2>&1 | tee logs/primary_run.log

echo "== additional controls: G, H, CS, CT =="
time python3 controls.py --seeds 100 2>&1 | tee logs/controls_run.log

echo "== analysis and deliverable tables =="
time python3 analysis/analyze.py 2>&1 | tee logs/analysis_run.log

echo "== headline verification =="
python3 - <<'PY'
import csv, statistics as st, sys

rows = list(csv.DictReader(open("results/primary/experiment_results/per_seed_results.csv")))
by = {}
for r in rows:
    by.setdefault(r["model"], []).append(r)

def mean(model, key):
    return st.mean(float(r[key]) for r in by[model])

checks = [
    ("D created edges = 612.13", mean("D", "total_created_raw"), 612.13),
    ("CR created edges = 612.13", mean("CR", "total_created_raw"), 612.13),
    ("D traversed created = 16.67", mean("D", "created_ever_effective"), 16.67),
    ("CR traversed created = 35.87", mean("CR", "created_ever_effective"), 35.87),
]
ok = True
for name, got, want in checks:
    good = abs(round(got, 2) - want) < 0.005
    ok &= good
    print(f"  {'PASS' if good else 'FAIL'}  {name}  (observed {got:.2f})")

# exact matching and partition identity
by_seed = {(r["model"], int(r["seed"])): r for r in rows}
created_match = sum(
    by_seed[("D", s)]["total_created_raw"] == by_seed[("CR", s)]["total_created_raw"]
    for s in range(100))
print(f"  {'PASS' if created_match == 100 else 'FAIL'}  D/CR per-seed created counts equal  ({created_match}/100)")

sys.exit(0 if ok else 1)
PY

echo
echo "Done. Deliverables are at the workspace root:"
ls -1 EXECUTION_REPORT.md HYPOTHESIS_RESULTS.md MODEL_COMPARISON.csv D_CR_RESULTS.csv \
      STRUCTURAL_METRICS.csv STATISTICAL_ANALYSIS.md MATHEMATICAL_INTERPRETATION.md reproduce.sh
