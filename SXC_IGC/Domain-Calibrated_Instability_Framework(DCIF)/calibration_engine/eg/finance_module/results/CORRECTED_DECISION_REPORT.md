# Corrected Decision Report
Generated: 2026-10-11

This document supersedes TRANSPORT_DECISION_REPORT.md and corrects three claims
identified as imprecise or wrong in that report.

---

## Correction 1: Breakeven win-rate calculation

**Prior claim:** "Breakeven WR = 58.8% because ATR×1.5 stop / ATR×2.5 target / 5pip cost."

**Verification method:** Computed directly from the actual trade PnL distribution
in `results/transport_signal_eval/trade_log_all.csv`, gate A_no_gate, N=382.

**Verified numbers:**

| Metric | Value |
|---|---|
| Gross PF (before costs) | **1.036** |
| Net PF (after 5pip RT) | 0.422 |
| Avg net winner | +9.25 pip |
| Avg net loser | −13.41 pip |
| Actual RR ratio (avg_win / avg_loss) | 0.690 |
| Breakeven WR from actual payoffs | **59.2%** |
| ATR-based breakeven WR | 58.8% |
| Difference | 0.4 pp |

The ATR-based number happened to be close to the actual number (0.4pp difference)
because the simulator's ATR-multiple stops and targets were approximately realized
in practice: stops averaged −8.86pip gross (vs 1.5×5.88=8.82pip theoretical) and
targets averaged +14.34pip gross (vs 2.5×5.88=14.7pip theoretical).

**Corrected framing:** The prior report said the problem was "ATR/cost ratio."
The more precise statement is: the entry signal has near-zero gross edge
(Gross PF = 1.036 ≈ 1.0). Any round-trip cost converts a breakeven gross signal
into a net loss. A higher ATR/cost instrument is necessary but not sufficient —
the entry signal must also have positive gross edge on that instrument.

---

## Correction 2: XAUUSD ATR/cost ratio claim

**Prior claim:** "XAUUSD ATR/cost ratio ≈ 20:1."

**Verification method:** Audited `data/XAUUSD/` files directly.

**Verified numbers:**

| Timeframe | ATR | Conservative RT cost | Ratio |
|---|---|---|---|
| 5-min (from M1 resample) | 5.66 USD/oz (mean) | 0.50–1.00 USD/oz | **5.7:1 to 11.3:1** |
| Daily | 65.71 USD/oz (mean) | 0.50–1.00 USD/oz | 66:1 to 131:1 |

The 20:1 claim in the prior report was wrong. At 5-min bars, XAUUSD ATR/cost is
5–11:1, not 20:1. This is better than EURUSD (≈1.2:1) but not by the claimed margin.

**Additional data limitation discovered:** The XAUUSD M1 file covers only
2026-01-01 to 2026-07-22 — the previously examined holdout period. No 2023–2025
intraday data exists for XAUUSD in this dataset. Intraday strategy testing on
XAUUSD with a fresh walk-forward split is not currently possible.

**NAS100:** Only daily bars are available. The NAS100_2025.csv and NAS100_daily.csv
files are corrupted (HTML bot-protection pages). No intraday NAS100 data exists.

---

## Correction 3: The "11 independent configurations" claim

**Prior claim:** "11 configurations were tested."

**Corrected statement:** Two experiments were run containing a total of 11
strategy×gate configurations, but most share the same EURUSD 5-min composite
microstructure input and the same execution framework. They are not 11
independent strategy ideas. The transport-derived gates (Q, v_abs, tension,
v_persist, tsys_dev) all operate on the same underlying composite field.
The second experiment's four strategies use different entries but the same
cost structure on the same dataset.

The evidence is sufficient to conclude that none of the tested configurations
has positive walk-forward expectancy on 5-min EURUSD after 5pip RT costs.
It does not rule out the transport architecture on different instruments or
timeframes where the gross edge structure may differ.

---

## XAUUSD Daily Baseline Results (new, task 4)

Three simple baseline strategies tested on XAUUSD daily bars without any
transport features. This establishes whether a viable baseline exists before
asking whether transport improves it.

**Data:** 566 daily bars, 2025-01-01 to 2026-07-21. Bid prices, no spread embedded.
**Cost model:** 0.75 USD/oz RT (conservative mid-range of 0.50–1.00 USD/oz).
**Walk-forward:** IS 2025-01 to 2025-08 | WF1 2025-09 to 2025-12 | WF2 2026-01 to 2026-07.

**WF combined results:**

| Strategy | N | Gross PF | Net PF | exp (USD) | CI 95% | Pass |
|---|---|---|---|---|---|---|
| EMA_Trend | 7 | — | 1.380 | +25.41 | [−83, +137] | NO (N<20) |
| Donchian20 | 21 | 2.062 | 2.042 | +56.53 | [−19, +132] | **YES** |
| RSI_Reversion | 17 | — | 1.586 | +28.59 | [−41, +117] | NO (N<20) |

**Donchian20 detail:**
- Gross PF 2.062 → Net PF 2.042: cost = 0.75 USD vs avg ATR = 73 USD = 1% of ATR.
  Cost is structurally negligible on daily XAUUSD. This is the key contrast with EURUSD.
- Cost sensitivity: PF remains above 1.0 until RT cost exceeds ~55 USD/oz.
  Actual cost is 0.75 USD/oz — 73× below the break-even cost level.
- Long trades (N=14): WR=78.6%, avg=+95 USD. Short trades (N=7): WR=28.6%, avg=−21 USD.
- WF1 (Sep–Dec 2025): PF=5.56. WF2 (Jan–Jul 2026): PF=1.35.

**Critical caveats — do not overstate this result:**

1. N=21 WF trades is too small for reliable inference. Bootstrap 95% CI lower
   bound is −19 USD (below zero). The result is consistent with noise.

2. WF2 (2026-01 to 2026-07) was previously examined in prior experiments.
   It is not a fresh untouched holdout. A true OOS test is not possible with
   the available data.

3. The strong long-side performance (78.6% WR) is consistent with gold's
   documented bull run in 2025. This may be a regime-specific result rather
   than a robust strategy. Short-side performance is poor.

4. The result provides a baseline worth investigating further. It does not
   confirm a reliable edge.

---

## What should happen next

**Immediate:**
- Do not promote Donchian20 as a confirmed strategy. N=21 and WF2 contamination
  prevent that conclusion. Record it as a candidate requiring further validation.
- Do not run transport features on top of this result yet. The baseline itself
  is not confirmed.

**Next experiment (if fresh data is obtained):**
1. Acquire XAUUSD daily bars from 2020–2024 (adds ~5 years, ~1200 bars).
   This enables a proper IS (2020–2023) / WF1 (2024) / WF2 (2025-H1) split
   with N>50 per fold and a genuinely untouched holdout (2025-H2 to 2026).
2. Rerun Donchian20 on that extended history. If it holds up with N>50 and
   fresh OOS, it is a candidate baseline.
3. Only then add transport-derived features and test whether they improve it.

**The transport architecture question remains open** for daily XAUUSD.
The composite field at daily resolution would aggregate over 288 five-minute
bars, potentially producing more persistent transport states than at 5-min.
This hypothesis is testable but requires the extended data first.

---

## Summary of verified decisions

| Item | Decision | Evidence |
|---|---|---|
| Q gate on EURUSD 5-min | Remove | Zero WF edge across 7 gates, 382 trades, 3 time periods |
| NY_Continuation on EURUSD 5-min | Remove | Gross PF=1.036; negative net expectancy every year, fold, direction |
| "20:1 ATR/cost" claim for XAUUSD | Retract | 5-min: 5.7–11.3:1. Daily: 66–131:1 |
| Donchian20 on XAUUSD daily | Candidate only | N=21, CI includes zero, WF2 contaminated |
| Transport on XAUUSD daily | Untested | Requires extended data before testing |
| Transport on EURUSD 5-min | No evidence of value | 11 configs tested, zero positive WF expectancy |
