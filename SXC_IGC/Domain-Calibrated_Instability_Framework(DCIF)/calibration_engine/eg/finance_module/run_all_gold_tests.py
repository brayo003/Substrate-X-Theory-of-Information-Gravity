"""
run_all_gold_tests.py
=====================
Master script that runs the entire Gold Strategy Validation pipeline:
1. Acquires and cleans historical market datasets (acquire_gold_data.py)
2. Runs execution audits, bug ablations, and baseline walk-forward tests (validate_gold_baseline.py)
3. Runs Substrate AI Transport incremental tests (test_gold_transport.py)
4. Runs automated unit and regression tests (tests/test_gold_execution.py)
"""

import sys
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

def run_step(cmd_list, description):
    print("\n" + "=" * 70)
    print(f">> RUNNING: {description}")
    print(f">> COMMAND: {' '.join(cmd_list)}")
    print("=" * 70)
    res = subprocess.run(cmd_list, cwd=str(HERE))
    if res.returncode != 0:
        print(f"[!] FAILED: {description} (exit code {res.returncode})")
        sys.exit(res.returncode)
    print(f"[✓] COMPLETED: {description}")

def main():
    print("Starting Complete Gold Validation Pipeline...")
    python_exe = sys.executable

    # Step 1: Unit Tests
    run_step([python_exe, "tests/test_gold_execution.py"], "Unit & Regression Tests")

    # Step 2: Baseline Validation & Execution Audit
    run_step([python_exe, "validate_gold_baseline.py"], "Baseline Validation & Bug Audit")

    # Step 3: Transport Incremental Value Test
    run_step([python_exe, "test_gold_transport.py"], "Substrate AI Transport Incremental Test")

    print("\n" + "=" * 70)
    print("ALL GOLD STRATEGY VALIDATION TESTS COMPLETED SUCCESSFULLY!")
    print("Reports generated in results/:")
    print("  - results/GOLD_DATA_AUDIT.md")
    print("  - results/GOLD_BASELINE_VALIDATION.md")
    print("  - results/GOLD_TRANSPORT_INCREMENTAL_TEST.md")
    print("  - results/GOLD_STRATEGY_DECISION_REPORT.md")
    print("=" * 70)

if __name__ == "__main__":
    main()
