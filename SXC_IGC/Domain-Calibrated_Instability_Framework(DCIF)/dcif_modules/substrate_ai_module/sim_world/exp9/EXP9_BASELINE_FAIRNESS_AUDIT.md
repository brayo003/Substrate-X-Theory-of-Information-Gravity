# EXP9 Baseline Fairness Audit

**Date:** 2026-11-13  
**Principle:** Do not weaken conventional baselines. Goal is mechanistic attribution and trade-off reporting, not forced substrate superiority.

---

## 1. Matched factors across architectures

| Factor | Matched? | Notes |
|---|---|---|
| Agent population \(N_a\) | Yes | Same per trial seed |
| Initial poses | Yes | Seed-matched |
| Landmark geometry | Yes | Public posts identical |
| Evidence patches & noise draws | Yes | Same RNG stream offsets per seed |
| Observation radius \(\rho_{\mathrm{obs}}\) | Yes | |
| Action opportunities (move/deposit/commit) | Yes | Same tick budget \(T_{\max}\) |
| Write amplitude budget | Yes | Same max deposits per agent |
| GT access | Yes (none) | No architecture sees \(k^\*\) |
| Evaluation metric | Yes | Same correct-commit definition |

---

## 2. Architecture-specific channels (intentional differences)

| Architecture | Channel | Retention | Spatial locality |
|---|---|---|---|
| independent | private obs only | agent memory | N/A |
| direct_msg | peer messages | TTL (matched Task 7 scale) | soft via reported coords |
| blackboard | shared records | stale window | soft |
| pheromone | evaporating grid | \(1-\lambda\) per tick | local |
| linear_sub | telegraph field | linear decay | local + propagation |
| nonlinear_sub | reaction-telegraph | bistable latch | local + reaction |
| hybrid | field + capped msgs | both | both |

Differences are the experimental contrast, not hidden handicaps.

---

## 3. Cost accounting

All architectures log: writes, reads, messages_sent, message_payload_bytes, travel_distance, solver_steps, solver_failures.

Reported resource expenditure uses explicit weights in config. Messaging payload costs are **not** set to zero to flatter the substrate.

---

## 4. Decision-rule fairness

- Spatial media (field/pheromone): threshold on local readout at **visited** landmarks.  
- Field media: sustained hold `COMMIT_HOLD_TICKS=20` (tests bistable persistence).  
- Msg/BB: `MSG_MIN_SUPPORT=2` + shorter hold (parity with multi-deposit coincidence, not a TTL handicap).  
- Pheromone: `PHER_COMMIT_THRESH=0.75` (~2 colocated deposits) + short hold.  
- Independent: ≥`INDEP_MIN_STRONG_OBS` distinct strong patches.  
- No baseline receives a global argmax oracle unavailable to substrate agents.

---

## 5. Expected non-superiority regions (pre-registered)

1. Direct messaging / blackboard may achieve higher correct rates when bandwidth is plentiful — **report as such**.  
2. Linear field may match nonlinear when coincidence is unnecessary (single strong evidence).  
3. Hybrid may dominate both pure substrate and pure messaging.  
4. Task 8 symbolic/messaging ceilings remain relevant: substrate advantage is situational.

---

## 6. Forbidden fairness violations

- Reducing message TTL only for baselines to help substrate.  
- Giving substrate agents larger sensor radius.  
- Planting readout ROI only for substrate.  
- Scoring substrate with a softer metric.  
- Excluding baseline failures while keeping substrate failures.

---

## 7. Audit status

Fairness constraints are encoded in `exp9/env.py` / `exp9/agents.py` / `exp9/config.py`.

**Confirmatory outcome (fairness-relevant):** blackboard (0.417) and direct_msg (0.333) matched or exceeded nonlinear_sub (0.292). Baselines were not artificially weakened; conventional structured memory remains competitive. Pheromone underperformed under evaporative + multi-deposit settings — reported as a trade-off, not hidden by exclusion.
