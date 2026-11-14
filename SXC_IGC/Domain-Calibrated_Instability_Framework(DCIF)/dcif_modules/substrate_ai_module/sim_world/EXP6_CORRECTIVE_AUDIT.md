# EXP6 Corrective Audit

**Date:** 2026-11-13  
**Audited artifacts (preserved, not modified):**
- `exp6_nonlinear_advantage.py`
- `exp6_pilot_results.json`
- `exp6_results.json`
- `EXP6_NONLINEAR_ADVANTAGE_REPORT.md`

**Supporting substrate modules inspected:**
- `domains/physical_field/physical_field_dynamics.py`
- `domains/physical_field/physical_field_models.py`
- `domains/physical_field/test_nonlinear_reaction_telegraph.py`
- `NONLINEAR_REACTION_TELEGRAPH_IMPLEMENTATION_REPORT.md`

**Status of original results:** Exploratory / historically informative only.  
They must **not** be merged with corrected confirmatory results.

---

## Summary verdict

The original Task 6 implementation executed and reported statistically significant differences, but it does **not** validly test the stated hypotheses. Multiple information-leakage paths, incorrect bistable initialization, invalid hazard/duplicate metrics, unpaired effect sizes for a paired design, silent solver recovery, and the absence of the controlled collective-processing experiment invalidate confirmatory claims of substrate capability or advantage.

---

## Defect register

### D1 — Nonlinear field initialized above the unstable equilibrium

| Field | Detail |
|---|---|
| **Location** | `exp6_nonlinear_advantage.py` → `_build_substrate_field()`, `initial_value=1.0` (≈ L446) |
| **Constraint** | C6 |
| **Scientific consequence** | For bistable parameters \(r=-0.5,a=2,b=1\), the unstable separatrix is \(s_-\approx 0.292893\). Background \(s=1.0\) already lies in the **high-state basin**. The field will spontaneously evolve toward \(s_+\approx 1.707\) without any agent deposit. Claimed “deposit-triggered persistent memory” is confounded with spontaneous basin attraction. |
| **Additional aggravation** | Same function applies 3 random perturbations of amplitude 0.5–1.5 on top of the 1.0 background (L455–459), further pushing the field into the high basin before any agent acts. |
| **Corrective action** | Initialize background strictly below \(s_-\) (candidate: \(s_0=0\)). Verify undisturbed-field stability over full trial duration (Gate G2 Test 1). Match linear/nonlinear ICs (C8). |

### D2 — Spontaneous global transition without deposits

| Field | Detail |
|---|---|
| **Location** | Consequence of D1; dynamics confirmed by `test_nonlinear_reaction_telegraph.py` Test J (IC=1.0 → \(s_+\)) and implementation report §5 |
| **Constraint** | C6, C7 |
| **Scientific consequence** | Undisturbed nonlinear fields do not remain in the low-state basin under the original IC. Any “persistence” after deposits cannot be attributed to deposit-triggered bistable switching. |
| **Corrective action** | Gate G2 Tests 1–4: undisturbed, subthreshold, superthreshold, deposit-removal. Proceed to agentic experiments only if G1–G2 pass. |

### D3 — Agents query memory at undiscovered resource ground-truth coordinates

| Field | Detail |
|---|---|
| **Location** | `run_trial()` movement block (≈ L683–689): `for r in active_resources: sig = memory.query_resource(r.x, r.y, tick)` |
| **Constraint** | C1, C2, C4, C5 |
| **Scientific consequence** | Movement decisions iterate over **all active resource coordinates** from the environment generator and evaluate the communication medium at those exact points. Agents thereby receive an oracle of undiscovered locations: any nonzero signal at a true resource site steers them there. This is not sensor-limited exploration; it is ground-truth-guided querying. Decision-invariance under relocated hidden resources would fail. |
| **Corrective action** | Agents may only query at their own position (or along locally sensed paths). Movement candidates must come from own sensors, own memory, or architecture-specific messages/records—never from the full resource list. Add Gate G3 decision-invariance tests. |

### D4 — Hazard “avoidance” counted after the agent is already inside the hazard

| Field | Detail |
|---|---|
| **Location** | `run_trial()` hazard block (≈ L640–649): `if in_hz: if knows_hazard: hazard_avoidances += 1` |
| **Constraint** | Gate G8 requirements |
| **Scientific consequence** | An agent already inside a hazard who has a memory signal is scored as having “avoided” it. This inverts the meaning of avoidance and understates true exposure. No pre-entry route diversion is implemented. |
| **Corrective action** | Implement actual avoidance policy that alters route **before** entry. Count: exposure ticks, unique hazard-entry events, avoided crossings (planned path would enter; diverted path does not), false positives, detour cost. Never classify in-hazard presence as avoidance. |

### D5 — Shared `task_claimed` dictionary bypasses architecture-specific coordination

| Field | Detail |
|---|---|
| **Location** | `run_trial()` (≈ L601, L668–677): global `task_claimed: dict[int, list[int]]` used for all conditions |
| **Constraint** | C3, C11, C12; Gate G9 |
| **Scientific consequence** | Task allocation uses a common oracle invisible in the architecture table. Independent, messaging, pheromone, and substrate conditions become functionally equivalent for conflict avoidance. Architecture differences cannot explain allocation outcomes. |
| **Corrective action** | Remove shared claim state from the decision pathway. Claims must flow only through the assigned memory/comms mechanism. Evaluation may keep a separate scoring ledger inaccessible to agents. |

### D6 — Incorrect / insufficient information-recovery measurements

| Field | Detail |
|---|---|
| **Location** | Resource/hazard recovery (≈ L630–662, L709): smooth proximity ground-truth vs normalized readout; mean absolute error → `info_recovery_acc` |
| **Constraint** | Part VII §16; Claim A/B measurement validity |
| **Scientific consequence** | Most agent–tick locations have no nearby event, so a near-zero readout matches a near-zero proximity target and inflates accuracy. Independent agents score highest with zero readout noise (original report §6 admits this). Metric does not measure event detection, localization, age, strength, or multi-event separation. |
| **Corrective action** | Balanced probe sets (event-present/absent, ages, distances, intensities, simultaneous events). Report precision, recall, F1, FPR, FNR, localization error, etc. Do not treat raw field values as probabilities without calibration. |

### D7 — Duplicate-work metric counts repeated observations as separate events

| Field | Detail |
|---|---|
| **Location** | Resource sensing loop (≈ L623–628): every revisit increments `resources_duped`, including same agent across consecutive ticks |
| **Constraint** | Part VII §17; Gate G7 |
| **Scientific consequence** | Dwell time near a resource inflates duplicate-work. Architectures that attract agents to linger are penalized artifactually. Denominator uses `len(resources_found)`, mixing discovery with revisit intensity. |
| **Corrective action** | Define unique redundant exploration / assignment events. Do not auto-count consecutive same-agent same-resource observations. Report unique duplicate visits, multi-agent independent visits, and an explicit fraction denominator. |

### D8 — Paired effect sizes computed with unpaired pooled SD

| Field | Detail |
|---|---|
| **Location** | `_cohens_d()` (≈ L764–772) uses pooled between-group SD; called on paired seed-matched vectors in `analyze_results()` (≈ L889) |
| **Constraint** | Gate G10; Part VII §19 |
| **Scientific consequence** | Design is paired-by-seed, but effect size is Cohen’s \(d\) (unpaired). Correct paired standardized effect is \(d_z = \bar{d}/s_d\) from within-seed differences. Reported \(d\) values are not the pre-registered paired effect sizes. |
| **Corrective action** | Report raw paired mean difference, CI for paired difference, paired test, \(d_z\), exact \(n\), multiplicity-adjusted \(p\). Prefer validated library (`scipy.stats`) where available. |

### D9 — Composite-score weighting and multiple-comparison misuse

| Field | Detail |
|---|---|
| **Location** | Composite (≈ L735–740); outcome classifier (≈ L920–946); Bonferroni over 5 comparisons vs Independent only |
| **Constraint** | Part VII §18–19; Acceptance Level 5 |
| **Scientific consequence** | Weights (0.35/0.35/0.20/0.10) were not justified as primary endpoints and can mask primary failures. Outcome classification counts Bonferroni-significant metrics vs Independent—explicitly prohibited as grounds for comparative advantage over conventional baselines. Primary collective-processing hypothesis was never tested yet outcome labels include “collective information processing.” |
| **Corrective action** | Pre-register primary hypothesis/endpoint (Experiment B interaction accuracy if that is primary). Composite only secondary, with sensitivity analysis. Compare vs conventional baselines for Level 5. Do not infer Claim C/D from Independent-baseline wins. |

### D10 — Missing controlled collective-information-processing experiment

| Field | Detail |
|---|---|
| **Location** | Absent from `exp6_nonlinear_advantage.py`; explicitly admitted in `EXP6_NONLINEAR_ADVANTAGE_REPORT.md` §5 |
| **Constraint** | Claim C; Experiment B; Gate G6; Phase 5 mandatory |
| **Scientific consequence** | Persistence / resource-discovery gains cannot establish collective processing. No \(X\), \(Y\), \(X+Y\) controls; no interaction task distinguishing joint state from independent presence. |
| **Corrective action** | Implement Experiment B with Control 1/2/3 and Test, plus an interaction task; Agent C reads only through assigned architecture; evaluate G6 separately from G5. |

### D11 — Silent solver recovery / undocumented numerical failure handling

| Field | Detail |
|---|---|
| **Location** | `SubstrateMemory.tick_update()` (≈ L536–542): `except ValueError: reset field` using `_build_substrate_field(tick)` |
| **Constraint** | C9, C10, C14 |
| **Scientific consequence** | Trials with numerical blow-up continue as ordinary successes after reset to a fresh (still incorrectly initialized) field. Information deposited before failure is destroyed without exclusion or failure flags in primary analysis. Original report notes instability but still treats trials as confirmatory. |
| **Corrective action** | Record solver errors/resets. Mark trials failed or excluded per pre-registered rule. Never silent-reset into a “successful” trial without logging. Verify equation, dt, BCs, convergence (G1). |

### D12 — Unequal information, observation opportunities, and architectural fairness

| Field | Detail |
|---|---|
| **Location** | Multiple |
| **Constraint** | C13, C14; Gate G4 |
| **Scientific consequence** | (a) Movement oracle (D3) gives all non-independent conditions unequal effective information depending on how their query responds at true resource sites. (b) `PheromoneMemory.query_task` reads grid at `(0,0)` not agent location (≈ L431)—broken pathway. (c) Substrate task query uses global `C_spectral`, not local/slot-specific readout (≈ L527–534)—architecture not comparable to per-slot pheromone/blackboard records. (d) Substrate conditions receive random IC perturbations; others start empty. (e) Hazard policy does not use architecture readout for routing (report §6). (f) Experiments A/B/C collapsed into one concurrent trial—cannot isolate claims. |
| **Corrective action** | Separate Experiments A, B, C. Fix each architecture’s pathway. Document irreducible capacity/cost differences. Match seeds, populations, sensors, durations, and observation opportunities. |

---

## Constraint → defect map

| Constraint / Gate | Defects |
|---|---|
| C1–C5 / G3 | D3, D5, D12 |
| C6–C8 / G1–G2 | D1, D2 |
| C9–C10 / G1 | D11 |
| C11–C13 / G4 | D5, D12 |
| C14 | D9, D11 |
| G5 | D1, D2, D6 |
| G6 | D10 |
| G7 | D3, D7 |
| G8 | D4 |
| G9 | D5 |
| G10 | D8, D9 |

---

## Original report claims vs audit status

| Original claim | Audit status |
|---|---|
| Nonlinear substrate shows specialized spatial-memory advantage | **Not established** — confounded by D1/D2/D3 |
| Bistable persistence explains resource-rate gain | **Not established** — IC already above separatrix |
| Statistically robust advantage vs Independent | Numerically computed but **scientifically non-confirmatory** given leaks and metrics |
| Collective information processing (Outcome 3 label path) | **Not tested** (D10) |
| Comparative advantage over conventional baselines | Original report correctly notes substrate loses on composite; still not a valid negative either under confounds |

---

## Corrective implementation plan (mapped)

1. Preserve originals; new corrected filenames only.  
2. Mathematical gates G1–G2 with IC below separatrix; no silent resets.  
3. Rebuild six architectures with isolated pathways; no ground-truth coordinate querying; no shared claim oracle.  
4. Decision-invariance tests (G3) and architecture integrity (G4).  
5. Experiment A — persistent spatial memory (G5).  
6. Experiment B — controlled \(X/Y/X+Y\) collective processing (G6) — **mandatory primary claim path**.  
7. Experiment C — resource / hazard / allocation separately (G7–G9).  
8. Pilot → freeze analysis → confirmatory; paired \(d_z\); pre-registered primary endpoint (G10).  
9. Report Outcome A/B/C with gate matrix; no over-claim.

---

## Provenance note

Original Task 6 files remain byte-identical relative to this corrective workstream. Corrected code, results, and reports use distinct filenames prefixed with `exp6_corrected` / `EXP6_CORRECTED` / `EXP6_CORRECTIVE`.
