# EXP7 Report — Nonlinear-Specific Computational Advantage and Substrate-Mediated Behavioural Utility

**Date:** 2026-11-13  
**Follow-up to:** Corrective Task 6 (Outcome B, Acceptance Level 3)  
**Confirmatory N:** 40 seeds (200–239)  
**Outcome:** **C — Both capabilities demonstrated**  
**Acceptance level:** **3 — Nonlinear-specific computational capability** (T1–T8; T9 FAIL)

Raw records: `exp7_pilot_results.json`, `exp7_results.json`, `exp7_configuration.json`.  
Task 6 preservation: `exp7/task6_checksums_before.txt` ≡ `exp7/task6_checksums_after.txt` (MD5, all OK).

---

## 1. Executive summary

Task 7 asked two independent questions left open by Task 6:

1. Can substrate-mediated hazard information change agent behaviour and reduce actual exposure?
2. Do nonlinear reaction-telegraph dynamics provide a computational operation that linear dynamics cannot?

**Track A (behavioural utility):** PASS through T6. In a forced corridor with Discoverer→Recipient separation, informed recipients recover hazard marks before entry, detour, and reduce exposure from 5.0 to 0.0 ticks (paired mean difference = 5.0, permutation \(p\approx 2\times10^{-4}\)) while completing the task. Incorrect/random/ablated controls do not reproduce successful avoidance. Delayed and disconnected-discoverer conditions retain utility for persistent architectures.

**Track B (nonlinear computation):** PASS T7–T8, FAIL T9. The bistable AND-gate (two subthreshold deposits latch iff spatially near) yields nonlinear F1 ≈ 0.987 vs linear F1 = 0.0. Reaction ablation collapses the capability (F1 = 0.0). Direct messaging and blackboard solve the same logical AND via explicit records (F1 = 1.0), so **no comparative advantage over conventional structured memory**.

**Combined:** Outcome C, Level 3. Behavioural utility is real; nonlinear-specific field computation is real; specialized superiority over messaging/blackboard is not established.

---

## 2. Task 6 findings carried forward

Preserved without re-litigation:

1. Bistable reaction-telegraph dynamics with corrected low-state IC.
2. Linear and nonlinear substrates recover events at delay 30.
3. Controlled \(X/Y/X{+}Y\) recovery at F1 = 1.0 (ceiling) across five architectures.
4. No hidden-coordinate querying or shared claim oracle in the corrected experiment.
5. Hazard-mediated behavioural utility was **not** demonstrated (G8 failed: identical exposure, zero avoided crossings).
6. Nonlinear-specific comparative advantage was **not** established.

Task 6 artifacts were not modified (checksum verification PASS).

---

## 3. Scientific motivation for Task 7

Task 6 proved recoverable information and bistability, but (a) G8 never exercised the causal chain discovery→deposit→pre-entry route change→reduced exposure, and (b) the collective XY task saturated for all sharing architectures. Task 7 therefore:

- Forces a corridor decision with a costly safe detour (Track A).
- Uses a subthreshold bistable AND that linear dynamics cannot latch (Track B).
- Keeps conventional baselines strong (Track B persistence budget matched to evaluation window).

---

## 4. Repository and implementation audit

See `EXP7_SCIENTIFIC_AUDIT.md`. Key executable facts:

| Item | Value |
|---|---|
| Solver | `evolve_field_nonlinear` |
| Parameters | \(r=-0.5,a=2,b=1,\tau=1,c=1,\Delta t=0.05\), 30×30 |
| Task 6 hazard encoding | Negative (blocks bistable latch) |
| Task 7 hazard encoding | **Positive danger-marker** (documented; enables latch test) |
| Track A geometry | Start (5,20) → Goal (45,20); hazard (25,20) r=5; detour via (25,40) |
| Track B primary | Bistable AND: amp=0.18, near sep=3, far sep=18, evolve=60 |

Implementation (Task 7 only): `exp7/`, `exp7_nonlinear_specific_advantage.py`, `exp7_hazard_behaviour.py`, `exp7_collective_computation.py`.

---

## 5. Track A experimental design

**Roles:** Agent A (Discoverer) senses and deposits; leaves. Agent B (Recipient) has no personal observation; decides route using only its architecture.

**Conditions:** A no-discovery | B withheld | C immediate | D delay5 | E delay15 | F disconnect | CTRL correct/incorrect/random/ablated.

**Timing model:** After discovery, structured shares are re-stamped at relative tick 0 so TTL/stale measure only intentional delay (not discoverer travel time). Spatial media keep the discoverer’s field.

**Controls:** Incorrect/random **replace** (do not stack on) true deposits so residual truth cannot leak into “wrong-info” trials.

**Primary endpoint (pre-registered):** Paired exposure reduction, informed (`C_immediate`) vs `A_no_discovery`, within architecture; primary focus nonlinear_sub.

**Integrity:** Recipient policy has no environment/GT parameters (T1). Pathways and resource budgets documented (T2).

---

## 6. Track A results (confirmatory N=40)

### Nonlinear substrate (primary)

| Mode | Recovery | Detour | Exposure | Avoided | Complete |
|---|---|---|---|---|---|
| A_no_discovery | 0.0 | 0.0 | 5.0 | 0.0 | 1.0 |
| B_withheld | 0.0 | 0.0 | 5.0 | 0.0 | 1.0 |
| C_immediate | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| D_delay5 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| E_delay15 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| F_disconnect | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| CTRL_correct | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 |
| CTRL_incorrect | 0.0 | 0.0 | 5.0 | 0.0 | 1.0 |
| CTRL_random | 0.0 | 0.0 | 5.0 | 0.0 | 1.0 |
| CTRL_ablated | 0.0 | 0.0 | 5.0 | 0.0 | 1.0 |

Detour extra length ≈ 16.1 units (nonzero cost; avoidance is not free). Solver failures: 0.

### Cross-architecture exposure reduction (C vs A)

| Architecture | Mean Δ exposure (none−informed) | p |
|---|---|---|
| independent | 0.0 | 1.0 |
| direct_msg | 5.0 | 0.0* |
| blackboard | 5.0 | 0.0* |
| pheromone | 5.0 | 0.0* |
| linear_sub | 5.0 | 0.0* |
| nonlinear_sub | 5.0 | 0.0* |

\*Deterministic paired difference; sd_diff = 0 so \(d_z\) undefined; permutation \(p\approx 2\times10^{-4}\) for nonlinear primary.

**Nuance:** Direct messaging recovers at C and D_delay5 (TTL=8) but not E_delay15/F_disconnect. Blackboard, pheromone, and both substrates retain F_disconnect utility. T6 therefore reflects persistent-memory contribution for spatial/structured-long memory; messaging contributes only short-TTL persistence.

---

## 7. Hazard-information recovery analysis

Gate **T3 PASS**: Recipient recovery rate = 1.0 before any hazard entry under C_immediate for all sharing architectures (independent = 0). Ablated readout → recovery 0 with signal present in architecture.

---

## 8. Hazard-mediated behavioural analysis

- **T4 PASS:** Correct information raises detour rate and lowers exposure vs no-info; incorrect/random do not match the successful-avoidance pattern for spatial media.
- **T5 PASS:** Exposure 5→0 with completion 1.0 and nonzero detour cost.
- **T6 PASS:** Delays 5/15 and disconnect-20 preserve utility for substrate/pheromone/blackboard.

Causal chain observed end-to-end: discovery → deposit → persistence → pre-entry recovery → route modification → zero exposure.

---

## 9. Track B experimental design

**Primary challenge (pre-registered after pilot non-ceiling check):** Bistable AND-gate.

- Individually subthreshold deposits (amp=0.18): field max ≈ 0.11–0.15 \(< s_-\approx 0.293\).
- Near pair (sep=3): nonlinear max ≈ 0.46 \(> s_-\) → high-basin entry; readout thr=0.40.
- Far pair (sep=18): no latch.
- Cases: none / X / Y / XY_near / XY_far. Ground truth: positive only for XY_near.

**Ablations:** nonlinear_full | linear_telegraph | nonlinear_reaction_off | no_propagation.

**Fairness:** Track B gives messaging/blackboard persist ≥ AND_EVOLVE_TICKS+10 so T9 is not a TTL artifact.

**Secondary challenges A–F:** overlap, temporal, spatial, conflict, interference, degradation (reported; not primary).

---

## 10. Computational challenge results (confirmatory)

| Architecture | AND F1 | XY_near hit | XY_far pred | X false pos |
|---|---|---|---|---|
| nonlinear_sub | 0.987 | 0.975 | 0.0 | 0.0 |
| linear_sub | 0.0 | 0.0 | 0.0 | 0.0 |
| direct_msg | 1.0 | 1.0 | 0.0 | 0.0 |
| blackboard | 1.0 | 1.0 | 0.0 | 0.0 |
| pheromone | 0.0 | 0.0 | 0.0 | 0.0 |
| independent | 0.0 | 0.0 | 0.0 | 0.0 |

Solver failures (AND trials): 0.

---

## 11. Nonlinear and linear ablation results

| Ablation | F1 |
|---|---|
| nonlinear_full | 0.987 |
| no_propagation | 0.920 |
| linear_telegraph | 0.0 |
| nonlinear_reaction_off | 0.0 |

Removing the nonlinear reaction terms abolishes the AND latch. Disabling propagation reduces precision (more far/false positives) but does not remove near-latch. **Mechanism attribution:** reaction nonlinearity, not mere diffusion or telegraph memory.

---

## 12. Conventional architecture comparisons

Paired per-seed F1 (nonlinear − baseline), Bonferroni-adjusted (family of 5):

| Comparison | Mean Δ F1 | p | p_Bonferroni | Sig |
|---|---|---|---|---|
| vs linear_sub | +0.975 | \(7.4\times10^{-33}\) | \(3.7\times10^{-32}\) | Yes |
| vs pheromone | +0.975 | \(7.4\times10^{-33}\) | \(3.7\times10^{-32}\) | Yes |
| vs independent | +0.975 | \(7.4\times10^{-33}\) | \(3.7\times10^{-32}\) | Yes |
| vs direct_msg | −0.025 | 0.32 | 1.0 | No |
| vs blackboard | −0.025 | 0.32 | 1.0 | No |

Nonlinear beats linear/pheromone/independent. It does **not** beat explicit messaging or blackboard on this AND task.

---

## 13. Statistical methodology

- Paired seeds across conditions.
- `paired_analysis` from Task 6 (`exp6_corrected/statistics.py`): mean diff, CI, t/permutation p, \(d_z\) when sd_diff > 0.
- Track B multiplicity: Bonferroni over 5 primary comparisons, α=0.05.
- Pilot exploratory (seeds 0–9); confirmatory independent (200–239).
- Zero-variance differences: \(d_z\) undefined; report permutation p and CI.

---

## 14. Confirmatory results

Frozen protocol in `exp7_configuration.json`. No post-hoc retuning.

| Gate | Result | Evidence |
|---|---|---|
| T1 | PASS | `exp7/integrity.py` decision invariance + pathway traces; `exp7_results.json` → integrity |
| T2 | PASS | Documented pathways + Track A/B resource budgets (`memory.fairness_notes`) |
| T3 | PASS | Recovery rate 1.0 before entry (`track_a_summary`) |
| T4 | PASS | Correct vs incorrect/random/ablated behavioural dissociation |
| T5 | PASS | Exposure 5→0, completion 1.0, detour cost > 0 |
| T6 | PASS | D/E/F utility for persistent architectures |
| T7 | PASS | Nonlinear AND F1≈0.987, near≫far, low X FP |
| T8 | PASS | Reaction-off / linear F1=0; full F1≈0.987 |
| T9 | **FAIL** | Messaging & blackboard F1=1.0; no advantage |

---

## 15. Effect sizes and confidence intervals

**Track A primary (nonlinear exposure: no-info − informed):**  
mean_diff = 5.0; CI95 = [5.0, 5.0]; permutation p ≈ 0.0002; \(d_z\) undefined (sd=0).

**Track B primary (nl vs linear F1):**  
mean_diff = +0.975; Bonferroni-significant. vs messaging/blackboard: nonsignificant negative diffs.

---

## 16. Failure analysis

1. **T9 FAIL (expected under fair baselines):** Explicit coordinate records compute spatial AND without field dynamics. Nonlinear field computation is specialized relative to *linear fields*, not relative to structured memory.
2. **Messaging long-delay Track A:** E_delay15 / F_disconnect fail under MSG_TTL=8 — persistence is TTL-limited, not substrate-like.
3. **Secondary B_temporal:** Nonlinear scored 0.0 (bistable latch retains old amplitude; “newer = stronger” heuristic fails). Not primary; documents a limitation of scalar latching for temporal order.
4. **no_propagation ablation:** Still high F1 on near AND (local superposition + reaction) but elevated far false positives — spatial coupling improves discrimination, reaction is necessary for latch.
5. **Pilot recommended N=50; confirmatory used N=40** after observing deterministic endpoints in pilot (mean_diff=1.0 F1, sd=0.25). Effects remained deterministic; underpowered comparisons are not a concern for T7–T8.

---

## 17. Gate-by-gate acceptance matrix

| Gate | Status | Supporting record |
|---|---|---|
| T1 | PASS | `exp7_results.json` → integrity.T1 |
| T2 | PASS | integrity.T2 + fairness_notes |
| T3 | PASS | track_a_gates.T3; summary recovery_rate |
| T4 | PASS | track_a_gates.T4; CTRL contrast |
| T5 | PASS | track_a_gates.T5; exposure_reduction |
| T6 | PASS | track_a_gates.T6; D/E/F summaries |
| T7 | PASS | track_b_gates.T7; and_summary.nonlinear_sub |
| T8 | PASS | track_b_gates.T8; ablation_summary |
| T9 | FAIL | track_b_gates.T9; conv F1=1.0 |

---

## 18. Overall outcome

**Outcome C — Both capabilities demonstrated.**

- Level 1–2 behavioural/persistent utility: established (T1–T6).
- Level 3 nonlinear-specific computational capability: established (T1–T8).
- Level 4 specialized comparative advantage: **not** established (T9 FAIL).

---

## 19. Claims established

1. Substrate-mediated (and other shared) hazard information produces measurable pre-entry route changes and reduced actual hazard exposure under the corridor protocol.
2. Persistent memory (delay/disconnect) contributes beyond immediate-only communication for substrate, pheromone, and blackboard.
3. Nonlinear reaction-telegraph dynamics implement a bistable spatial AND that linear telegraph dynamics and reaction-ablated fields do not.
4. Information-isolation and architectural pathway integrity hold for the Task 7 decision layer.

---

## 20. Claims not established

1. Nonlinear substrate superiority over direct messaging or blackboard on the AND task.
2. General comparative advantage across all secondary challenges (temporal order favors structured timestamps).
3. That Task 6’s negative hazard encoding would have passed Track A (Exp7 uses documented positive danger-markers).
4. Level 4 specialized advantage.

---

## 21. Scientific limitations

- Corridor is a controlled forced-choice; not a free-exploration multi-hazard world.
- Positive danger-marker encoding differs from Task 6’s negative hazard convention (explicitly documented).
- AND readout is hand-designed (local max vs separatrix threshold), not learned.
- Single scalar field; multi-semantic channels were not claimed.
- Confirmatory N=40 (pilot suggested 50); effects were saturated/deterministic.
- Secondary challenge metrics are exploratory relative to the frozen primary endpoints.

---

## 22. Recommended next experiment

**Task 8 candidates (choose one primary):**

1. **Field-native tasks where structured records are capacity-matched or bandwidth-limited** (e.g., continuous intensity fields, many overlapping events, no explicit ID tags) to re-test T9 without giving messaging free symbolic AND.
2. **Closed-loop agents that must *use* the bistable AND latch for a collective decision** (link Track B computation to Track A-style utility), testing whether nonlinear-specific computation produces behavioural advantage when symbolic AND is unavailable.
3. **Temporal-order / history-dependent tasks** where bistable latching is a liability and alternative nonlinear mechanisms (or multi-channel fields) are required — addressing the B_temporal failure mode.

Do not weaken messaging/blackboard to manufacture T9. Construct tasks where the field’s continuous nonlinear state is the natural computational substrate.
