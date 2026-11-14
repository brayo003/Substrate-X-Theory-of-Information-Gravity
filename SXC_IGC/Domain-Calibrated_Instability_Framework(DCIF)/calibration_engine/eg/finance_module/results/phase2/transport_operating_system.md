# Transport Operating System — Architecture Documentation

## SXC-IGC Q Transport Layer as Market Operating System

**Date:** 2026-07-22
**Version:** Phase 2 Validation

---

## Theoretical Foundation

The Transport OS is grounded in the SXC-IGC transport theory:

  **Telegraph PDE:**  τ ∂²s/∂t² + ∂s/∂t = c²τ ∂²s/∂t²

  **Transport field quantity:**  Q = 4(cτ)² |∇ ln(s)|² − 1

  **Coherence length:**  ξ_c = 2cτ

where:
- s(x,t) = normalised composite market stress field (DCII)
- c = 1.0 (propagation speed, bar units)
- τ = 5.0 (relaxation time, bars = 25 minutes at 5-min bars)
- Q > 0 → COHERENT (wave-like, trends propagate)
- Q < 0 → INCOHERENT (overdamped, signals decay, mean reversion)

**Q is NOT a trading signal. Q is a market state classifier.**

---

## Q Regime Boundaries (from Phase 1 full-dataset statistics)

| Regime | Q Range | Fraction |
| ------ | ------- | -------- |
| Deep_Incoherent  | Q ≤ -0.9980 | ~5% |
| Mod_Incoherent   | -0.9980 < Q < 0 | ~75% |
| Transition       | |Q| < 0.01 | ~0.4% |
| Weak_Coherent    | 0 < Q < 1.7323 | ~15% |
| Strong_Coherent  | Q ≥ 1.7323 | ~5% |

---

## Layer 1 — Strategy Scheduler

Analogous to a CPU process scheduler. Q determines which strategy process
has access to the execution engine.

| Regime | Selected Strategy | No-Trade? |
| ------ | ---------------- | --------- |
| Deep_Incoherent | NO_TRADE | YES |
| Mod_Incoherent | NO_TRADE | YES |
| Transition | NO_TRADE | YES |
| Weak_Coherent | NO_TRADE | YES |
| Strong_Coherent | NY_Continuation | no |


Calibration: composite score (0.4×PF + 0.3×Sharpe + 0.2×WinRate + 0.1×Expectancy)
from Phase 1 performance_by_regime.csv. NO_TRADE if best PF < 0.85.

---

## Layer 2 — Risk Budget Manager

Analogous to memory/resource allocation. Q determines how much capital
the OS allocates to the active strategy.

| Regime | Risk Fraction | Interpretation |
| ------ | ------------- | -------------- |
| Deep_Incoherent | 0.000 | Blocked |
| Mod_Incoherent | 0.000 | Blocked |
| Transition | 0.000 | Blocked |
| Weak_Coherent | 0.000 | Blocked |
| Strong_Coherent | 0.250 | Active |


Calibration: normalised from median regime PF. PF=1.5 → 1.0, PF=0.5 → 0.0.
Floor = 0.25 for any tradeable regime.

---

## Layer 3 — Stop/Target Policy Controller

Analogous to I/O priority scheduling. Q-regime determines execution quality
parameters (stop width, target width, trailing policy).

| Regime | Stop×ATR | Target×ATR | Trailing |
| ------ | -------- | ---------- | -------- |
| Deep_Incoherent | 1.50 | 2.50 | No |
| Mod_Incoherent | 1.50 | 2.50 | No |
| Transition | 1.50 | 2.50 | No |
| Weak_Coherent | 1.50 | 2.50 | No |
| Strong_Coherent | 1.88 | 2.50 | No |


Calibration: stop_freq from Phase 1 (high freq → wider stops). Trailing
enabled when P(stay) > geometric null × 1.5 (persistent regimes).

---

## Execution Rules

1. Q is read at every bar (IMMUTABLE computation)
2. Regime is classified using global quantile thresholds (IMMUTABLE)
3. OS.decide(regime) returns: strategy, risk_fraction, stop/target multipliers
4. Strategy generates entry signal (strategy never sees Q)
5. Position opened with risk-scaled sizing and regime-specific stops
6. Maximum one position at a time (no pyramiding)
7. Exit: stop hit | target hit | max 24-bar hold

## IMMUTABLE Components

- transport_layer.py: telegraph PDE solver
- Q computation: 4(cτ)²|∇ln s|² − 1
- Signal construction (signals.py)
- DCII calibration
- V12 engine (engine_runner.py)
- Regime thresholds (global quantiles from Phase 1)
