# audit_evidence/

This directory contains reproducible scripts that verify the core findings
of the forensic audit. Each script produces console output that constitutes
evidence for the findings stated in the deliverable documents.

**Audit date:** 2026-10-17  
**Git commit:** `6738ed05`

---

## Scripts

### verify_q_reduction.py

**What it proves:**  
Q = 4(cτ)²|∇ln(s)|² − 1 with default parameters (c=1, τ=5) reduces to
Q = 100×(log-return of composite)² − 1. The Q>0 threshold is algebraically
identical to |log-return of composite| > 0.1. Q adds no information beyond
the absolute one-bar log-change of the composite stress field.

**How to run:**
```bash
cd calibration_engine/eg/finance_module
python audit_evidence/verify_q_reduction.py
```

**Expected output:**  
- Library Q and reduced formula Q match to 10 decimal places for all tested inputs  
- Q=0 boundary confirmed at |log-return| = 0.1000  
- Q>0 and |grad|>0.1 agree on 100% of bars (bar 0 excluded due to boundary condition)

**Evidence for:** `FORENSIC_AUDIT_FINAL.md` §4 Finding 3, `DCIF_EQUATION_TRACE.md` §3

---

### verify_strategy_independence.py

**What it proves:**  
All 28 strategies in `strategy_library.py` produce identical signals regardless
of whether Q, T_sys, phase, or tr_regime columns are present in the DataFrame.
The DCIF/Substrate calculations have zero causal effect on Phase 1 trading signals.

**How to run:**
```bash
cd calibration_engine/eg/finance_module
python audit_evidence/verify_strategy_independence.py
```

**Expected output:**  
- 28/28 strategies: PASS  
- Confirmed: identical signals with and without DCIF columns

**Evidence for:** `FORENSIC_AUDIT_FINAL.md` §5 "Disconnected", `END_TO_END_DATA_FLOW.md` §3

---

### verify_transport_pde.py

**What it proves:**  
1. The transport_layer.py implementation is mathematically correct: Q values from the library match an independently written reference implementation for constant, impulse, step, and oscillating inputs.  
2. The PDE output field `s_transport` is stored in parquet files but is not referenced in any trading decision code (p1_strategy_runner.py, p2_transport_os.py, execution_simulator.py, strategy_library.py, strategy_allocator.py).

**How to run:**
```bash
cd calibration_engine/eg/finance_module
python audit_evidence/verify_transport_pde.py
```

**Expected output:**  
- All Q vs reference comparisons: match  
- s_transport: "NOT referenced" for all decision-making files  
- All tests: PASS

**Evidence for:** `DCIF_EQUATION_TRACE.md` §2 (transport faithful), `END_TO_END_DATA_FLOW.md` §2.3 (s_transport unused)

---

## Key Audit Facts (Non-scriptable)

These findings were established by reading source code and result files.
They cannot be further distilled into scripts without re-running multi-hour
backtests, but they are verifiable from the existing output files.

### Strategy mismatch (bounded_validation.py)

Evidence file: `results/bounded_validation_corrected/CORRECTED_BOUNDED_VERDICT.md`  
Evidence file: `results/bounded_validation_corrected/corrected_audit_results.json`

The original 76-trade backtest used a custom RSI+MACD+ADX signal (lines visible
in `bounded_validation.py`). The actual `NY_Continuation` from `strategy_library.py`
is an EMA(9)/EMA(21) crossover filtered to hour 13 UTC only (lines 471–485 of
`strategy_library.py`). These are different strategies. When the correct strategy
is used, the 2026 OOS result is 7 trades, all losing.

### Phase 1 matrix: all strategies negative

Evidence file: `results/phase1/phase1_strategy_matrix.csv`

Open this file. Sort by profit_factor descending. The best cell across all
28 strategies and 5 regimes has PF=0.61. There is no profitable cell under
the execution model (3-pip RT cost, ATR 1.5×stop / 2.5×target).

### T_sys not used in decisions

Search for `T_sys` in the active pipeline files:
```bash
grep -n "T_sys" p2_transport_os.py p1_strategy_runner.py execution_simulator.py strategy_library.py
```
T_sys appears in column names stored to parquet, not in any conditional logic,
position sizing, entry/exit, or OS decision.

---

## Hashes of Key Result Files

These SHA-256 hashes identify the exact versions of key outputs audited.

| File | SHA-256 |
|---|---|
| results/bounded_validation_corrected/corrected_audit_results.json | `b92cdb19e23eb9488356425f4385cc714953f4ed67ae2f82d4e353ca72975bb6` |
| results/phase1/phase1_strategy_matrix.csv | `5afda2f89631f8576566a97a26f027f008d488a62fff8b7c8c98169118ab51b1` |
| checkpoints/checkpoint_manifest.json | `74c0babe95790693dbd0d64ebde5cc3e5b19b8e8232cf977d896e0808024d7c9` |

These hashes were computed at audit date 2026-10-17 on git commit `6738ed05`.

## Confirmed Script Results (2026-10-17)

**verify_q_reduction.py:** All Q values match reference formula. Q>0 and |grad|>0.1 agree on 10000/10000 bars. Boundary confirmed at |log-return| = 0.1000.

**verify_strategy_independence.py:** All 29 strategies PASS. Removing Q/T_sys columns produces identical signals for every strategy.

**verify_transport_pde.py:** Constant/Impulse/Step/Oscillating inputs all match reference. s_transport column not referenced in any of: p1_strategy_runner.py, p2_transport_os.py, p2_execution_engine.py, execution_simulator.py, strategy_library.py, strategy_allocator.py, p1_regime_analysis.py.
