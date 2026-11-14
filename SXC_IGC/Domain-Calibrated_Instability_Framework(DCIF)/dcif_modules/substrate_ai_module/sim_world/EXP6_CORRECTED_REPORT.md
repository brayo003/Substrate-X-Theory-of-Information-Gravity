# EXP6 Corrected Report — Nonlinear Substrate Capability Protocol

**Date:** 2026-11-13  
**Protocol package:** `exp6_corrected/`  
**Entry point:** `exp6_corrected_nonlinear_advantage.py`  
**Confirmatory N:** 60 paired seeds (100–159), disjoint from pilot seeds 0–11  
**Overall outcome:** **B — Specialized capability** (no comparative advantage on the primary endpoint)  
**Maximum acceptance level supported:** **Level 3** (collective information processing). Level 4 blocked by G8 FAIL.

**Provenance:** Original Task 6 artifacts were preserved and not modified:
`exp6_nonlinear_advantage.py`, `exp6_pilot_results.json`, `exp6_results.json`, `EXP6_NONLINEAR_ADVANTAGE_REPORT.md`.  
Original results are exploratory/historical only and are **not** pooled with these confirmatory results.

---

## 1. Executive summary

Under corrected initialization (low-state basin \(s_0=0\)), the reaction-telegraph field exhibits the specified bistable dynamics (G1–G2). With oracle pathways removed, six architectures were compared on three separate experiments.

- **Experiment A (persistent memory):** Nonlinear and linear substrates retained recoverable event information through delay 30; conventional messaging/pheromone/blackboard degraded with delay (direct messaging only at delay ≤ MSG_TTL). Independent agents recovered nothing shared.
- **Experiment B (collective processing; primary):** Agent C recovered the BOTH_NEAR interaction label with F1 = 1.0 for nonlinear, linear, pheromone, blackboard, and direct messaging. Independent F1 = 0. Spatial near vs far was distinguished. **No nonlinear advantage over matched conventional baselines** (all paired mean differences = 0 on primary F1).
- **Experiment C (agentic utility):** Resource discovery and task allocation ran without a shared claim oracle (G7, G9 PASS). Hazard avoidance produced **zero** pre-entry avoided crossings in all conditions (G8 FAIL); exposure was identical across architectures.

**Conclusion:** Persistent spatial memory and controlled collective interaction recovery are demonstrated for the nonlinear substrate under tested conditions, but they are matched by the linear substrate and by conventional shared-memory / messaging architectures on the primary collective-processing endpoint. Comparative specialized advantage is **not** established. Hazard-mediated behavioural utility is **not** demonstrated.

---

## 2. Original Task 6 defects and corrective actions

Full defect register: `EXP6_CORRECTIVE_AUDIT.md`. Summary:

| ID | Defect | Correction |
|---|---|---|
| D1 | IC = 1.0 above separatrix \(s_-\) | IC = 0.0 (low basin); G2 T1 |
| D2 | Spontaneous high-basin transition | Undisturbed / deposit-gated tests G2 |
| D3 | Movement queried GT resource coords | `choose_movement_target` uses sensors + architecture only; G3 |
| D4 | Post-entry counted as avoidance | Pre-entry diversion metric; exposure separate; G8 |
| D5 | Global `task_claimed` oracle | Architecture-only claims; eval ledger isolated; G9 |
| D6 | Proximity-field “accuracy” | Balanced present/absent probes; precision/recall/F1 |
| D7 | Per-tick observation = duplicate | Unique multi-agent visit events |
| D8 | Unpaired Cohen’s \(d\) on paired design | Paired \(d_z = \bar{d}/s_d\); scipy or numpy t-test |
| D9 | Opaque composite / multiplicity | Primary = Exp B F1; Bonferroni \(m=5\) |
| D10 | Missing \(X,Y,X{+}Y\) experiment | Experiment B with XY_near / XY_far |
| D11 | Silent solver resets | `failed` / `solver_failed` recorded; no silent success |
| D12 | Unmatched info/compute budgets | Documented fairness notes; matched seeds/N/env |

---

## 3. Mathematical model and parameter specification

Equation:

\[
\tau s_{tt}+s_t = c^2\tau\nabla^2 s + r s + a s^2 - b s^3
\]

Parameters (frozen): \(r=-0.5\), \(a=2\), \(b=1\), \(\tau=1\), \(c=1\), \(\Delta t=0.05\), grid \(30\times30\) on \([0,50]^2\).

Initial condition: \(s(\mathbf{x},0)=0\) (below \(s_-\)). No random IC perturbations.

Linear ablation: \(r=a=b=0\) on the same infrastructure.

Configuration freeze: `exp6_corrected/config.py` → `ProtocolFreeze`.

---

## 4. Analytical equilibrium and stability verification

| Equilibrium | Analytical | Role |
|---|---|---|
| \(s_0=0\) | 0 | Stable (low) |
| \(s_-\) | \((2-\sqrt{2})/2\approx0.292893\) | Unstable separatrix |
| \(s_+\) | \((2+\sqrt{2})/2\approx1.707107\) | Stable (high) |

Gate G1 equilibria and linear-stability classification: **PASS** (`exp6_corrected_gate_log.json`, `math_gates.py`).

---

## 5. Numerical solver and convergence verification

G1 checks (all PASS):

1. Equilibria within tolerance  
2. Stability classification  
3. Homogeneous ODE identity vs analytic RHS  
4. Linear limit matches linear telegraph evolution  
5. Timestep convergence  
6. Spatial-resolution convergence  
7. Boundary scheme documented/tested  
8. Numerical validity over Exp-C duration (no NaN/Inf; solver errors logged)

Source: `exp6_corrected/math_gates.py`, results in `exp6_corrected_gate_log.json` and confirmatory `math_gates` block.

---

## 6. Initial-state and deposit-triggered transition results

Gate G2 (all PASS):

| Test | Result |
|---|---|
| T1 Undisturbed | Remains in low basin for full duration |
| T2 Subthreshold deposit | No persistent high transition |
| T3 Superthreshold deposit | Local transition |
| T4 Deposit removal | High state persists after deposit removed |
| T5 Spatial localization | High region quantified (not assumed global) |
| T6 Two deposits | Distinguishable peaks at separated sites |
| T7 Linear ablation | Bistable transition disappears |

Deposit-triggered memory is therefore not confounded with spontaneous basin escape from a high IC.

---

## 7. Information-access and no-oracle audit

Gate G3 **PASS**.

- Decision helper `choose_movement_target` has no environment/resource/hazard parameters.
- Decision-invariance: hidden resource layouts differ; agent-visible state identical → identical decisions.
- Ground truth used only in evaluation ledgers in Experiment C.
- Helper audit: no iteration over undiscovered GT coordinate lists in the decision pathway.

Source: `exp6_corrected/oracle_tests.py`.

---

## 8. Architecture implementation and fairness audit

Gate G4 **PASS**.

| Condition | Pathway |
|---|---|
| Independent | Local only; shared queries return 0 |
| Direct messaging | Explicit messages; TTL = 8 |
| Blackboard | Structured shared records; stale = 20 |
| Digital pheromone | Multi-channel grids; evaporate 0.05/tick |
| Linear substrate | Same field infra, \(r=a=b=0\), IC = 0 |
| Nonlinear substrate | Reaction-telegraph, IC = 0 |

Runtime traces confirmed writes/reads on each pathway. Separate backend instances are isolated (no shared mutable claim oracle). Inherent differences (TTL, evaporation, channel count, PDE cost) are documented in `architecture_fairness_notes()` rather than equated.

---

## 9. Experiment A: persistent spatial memory

**Question:** Can deposited information remain recoverable after the depositor leaves?

**Design:** Deposit → evolve `delay` ∈ {5,15,30} with no refresh → balanced present/absent probes at controlled distances. Metrics: detection correctness, precision/recall/F1, FPR/FNR, localization error.

### Confirmatory results (N=60)

| Condition | Detection mean | F1 | Delay 5 / 15 / 30 |
|---|---:|---:|---|
| Independent | 0.000 | 0.000 | 0 / 0 / 0 |
| Direct msg | 0.333 | 0.500 | 1 / 0 / 0 |
| Blackboard | 0.667 | 0.800 | 1 / 1 / 0 |
| Pheromone | 0.667 | 0.800 | 1 / 1 / 0 |
| Linear sub | 1.000 | 1.000 | 1 / 1 / 1 |
| Nonlinear sub | 1.000 | 1.000 | 1 / 1 / 1 |

Failed trials: 0.

**Gate G5: PASS** — deposited info measurable after leave; recoverable by other probes; delay dependence shown; not attributable to hidden agent GT access; reproducible across seeds; compared to linear and conventional baselines.

**Interpretation:** Both substrates dominate evaporating/TTL media at long delay. **Nonlinear does not outperform linear** on this task under these parameters (both ceiling).

---

## 10. Experiment B: collective information processing

**Primary hypothesis / endpoint:** Per-seed F1 for BOTH_NEAR (`exp_b_interaction_f1`).

**Cases:** none | X | Y | XY_near | XY_far.  
**Label:** 1 iff XY_near (both deposits and separation ≤ 6).  
**Readout:** Architecture-visible features only; fixed documented rule (no GT at inference).  
**Note:** Raw accuracy is exploratory only — always-predict-0 yields ~0.8 accuracy and F1 = 0.

Agent C probe geometry uses controlled sites A/B (deposit *presence* unknown; site coordinates are protocol probes). Scalar substrates multiplex X/Y spatially (not claimed as independent semantic channels).

### Confirmatory results (N=60)

| Condition | F1 | Balanced acc | XY_near hit | XY_far pred | Failed |
|---|---:|---:|---:|---:|---:|
| Independent | 0.000 | 0.500 | 0.000 | 0.000 | 0 |
| Direct msg | 1.000 | 1.000 | 1.000 | 0.000 | 0 |
| Blackboard | 1.000 | 1.000 | 1.000 | 0.000 | 0 |
| Pheromone | 1.000 | 1.000 | 1.000 | 0.000 | 0 |
| Linear sub | 1.000 | 1.000 | 1.000 | 0.000 | 0 |
| Nonlinear sub | 1.000 | 1.000 | 1.000 | 0.000 | 0 |

**Gate G6: PASS** — Agent C recovers combined interaction; distinguished from X-only/Y-only; near ≠ far; rule uses architecture features; compared to conventional baselines. Effect is **not** unique to nonlinear substrate.

Evolve horizon kept < MSG_TTL so messaging is tested on combination, not TTL expiry (persistence is Exp A).

---

## 11. Experiment C: agentic coordination

Three modes run separately with matched environments per seed.

### C1 Resource discovery — G7 PASS

| Condition | Discovery rate | Dup-work fraction |
|---|---:|---:|
| Independent | 0.260 | 0.128 |
| Direct msg | 0.290 | 1.782 |
| Blackboard | 0.252 | 2.515 |
| Pheromone | 0.233 | 0.944 |
| Linear | 0.231 | 0.836 |
| Nonlinear | 0.233 | 0.853 |

Decisions never iterate undiscovered GT coordinates. Duplicate work = multi-agent unique visits (not per-tick dwell).

### C2 Hazard avoidance — G8 FAIL

| Condition | Exposure ticks | Avoided crossings |
|---|---:|---:|
| All six | 17.7 | **0.0** |

Methodology correctly separates exposure from avoidance and only counts pre-entry diversions. Empirically, **no architecture produced a pre-entry avoidance event**. Exposure is identical across conditions. Therefore G8 fails: agents did not demonstrably use hazard information to alter routes before entry under this policy/environment.

### C3 Task allocation — G9 PASS

Claims via architecture only; evaluation ledger isolated. Completions observed in all conditions (rates ~0.19–0.28). No shared `task_claimed` decision oracle.

---

## 12. Statistical methodology

Frozen before confirmatory analysis (`ProtocolFreeze`):

- **Primary endpoint:** Exp B interaction F1 (BOTH_NEAR)  
- **Comparison family (m=5):** nonlinear vs {linear, direct_msg, blackboard, pheromone, independent}  
- **α = 0.05**, Bonferroni-adjusted  
- **Paired seeds**; effect size \(d_z=\bar d / s_d\) (not unpaired pooled SD)  
- Paired t-test + sign-flip permutation p; bootstrap 95% CI on mean difference  
- **Pilot N=12** → power heuristic recommended N=60 → confirmatory N=60 frozen  
- Pilot not used as confirmatory evidence  
- Minimum meaningful effect: \(|d_z|\ge0.5\)  
- Exclusions: `failed` / `solver_failed` trials (none occurred in confirmatory)

---

## 13. Confirmatory results

- Wall time ≈ 63 s; failed trials = 0; solver resets = 0  
- Outcome classification: `B_SPECIALIZED_CAPABILITY`  
- Max acceptance ladder level: **3** (G8 blocks Level 4)

Primary paired comparisons (nonlinear − baseline) on F1:

| Comparison | Mean diff | \(d_z\) | p | p_Bonferroni | Sig |
|---|---:|---:|---:|---:|---|
| vs linear | 0.000 | 0.0 | 1 | 1 | No |
| vs direct_msg | 0.000 | 0.0 | 1 | 1 | No |
| vs blackboard | 0.000 | 0.0 | 1 | 1 | No |
| vs pheromone | 0.000 | 0.0 | 1 | 1 | No |
| vs independent | 1.000 | — (zero variance) | 0 | 0 | Yes |

Beating independent alone does **not** establish specialized advantage (protocol prohibition 17).

---

## 14. Individual metric comparisons

**Exp A detection (secondary):** Nonlinear equals linear (diff 0). Nonlinear beats direct_msg / blackboard / pheromone / independent on long-delay detection (ceiling vs TTL/evaporation failure). This is a **persistence** specialization of *field* media generally, not a nonlinear-vs-linear advantage.

**Exp B F1 (primary):** Nonlinear tied with all communicating baselines.

**Exp C discovery (secondary):** Nonlinear slightly below direct_msg (mean diff −0.056, p≈0.0015, \(d_z\approx-0.43\)); not a nonlinear advantage. vs linear: negligible.

**Exp C hazard:** No architecture differentiated exposure or avoidance.

**Exp C allocation:** Modest completion rates; no nonlinear advantage claimed.

No composite score was used to override primary failure of comparative advantage.

---

## 15. Failure analysis and limitations

1. **G8 FAIL:** Hazard policy did not produce measurable pre-entry avoidances; identical exposure across conditions. Agentic utility for hazard coordination is unestablished.
2. **Ceiling effects in Exp B:** With known probe sites and strong deposits, F1 saturated at 1.0 for five architectures — low power to detect nonlinear specialization.
3. **Linear = nonlinear on A and B:** Bistable persistence was not necessary for the tested delays/amplitudes; linear telegraph already sufficed for recovery.
4. **Scalar field multiplexing:** X and Y are spatial, not semantic channels; interaction is spatial relationship recovery.
5. **Agent C probe sites known:** Controlled laboratory readout, not blind spatial search.
6. **Exp C discovery rates low (~0.23–0.29):** Sensor-limited random/gradient search; architecture effects modest.
7. **Messaging TTL:** Intentional architectural difference; Exp B horizon kept inside TTL; Exp A shows TTL failure at long delay.
8. **No post-hoc confirmatory retuning** was performed.

---

## 16. Gate-by-gate acceptance matrix

| Gate | Status | Evidence |
|---|---|---|
| G1 Mathematical | **PASS** | `exp6_corrected_gate_log.json` / `math_gates.py` — 8/8 checks |
| G2 Dynamical | **PASS** | Same — T1–T7 all true |
| G3 No-oracle | **PASS** | `oracle_tests.py` decision invariance + inspection |
| G4 Architecture | **PASS** | Pathway traces + isolation + fairness notes |
| G5 Persistent memory | **PASS** | Confirmatory Exp A; nonlinear det=1.0 all delays |
| G6 Collective processing | **PASS** | Confirmatory Exp B; F1=1.0; near>far; vs individuals |
| G7 Resource discovery | **PASS** | Valid metrics; discovery>0; no GT in decisions |
| G8 Hazard avoidance | **FAIL** | avoided_crossings=0 all conditions; exposure identical |
| G9 Task allocation | **PASS** | Architecture claims only; completions observed |
| G10 Statistical integrity | **PASS** | Pre-registered F1 endpoint, paired \(d_z\), Bonferroni, N from pilot |

---

## 17. Overall outcome: B

**Outcome B — Specialized capability.**

Persistent memory (Claim B / Level 2) and controlled collective interaction recovery (Claim C / Level 3) are demonstrated for the nonlinear substrate under the tested conditions. Conventional architectures (and the linear substrate) match or equal the nonlinear substrate on the primary collective-processing endpoint. Comparative specialized advantage (Outcome C / Level 5) is **not** established. Hazard agentic utility (part of Level 4) fails G8.

---

## 18. Exact scientific claims supported by the evidence

1. With IC \(s=0\) and parameters \((r,a,b)=(-0.5,2,1)\), the implemented solver exhibits the specified bistable reaction-telegraph dynamics (G1–G2).
2. Undisturbed fields remain in the low basin; superthreshold deposits can trigger persistent local high states that survive deposit removal.
3. Under no-oracle constraints, the nonlinear substrate retains recoverable spatial event information after the depositor leaves, including at delay 30 (G5).
4. Independently deposited X and Y, when near, produce a recoverable interaction state (BOTH_NEAR) that Agent C distinguishes from X-only, Y-only, and XY_far via the assigned architecture (G6).
5. Resource discovery and task allocation can proceed without a shared claim oracle or GT coordinate querying (G7, G9).

---

## 19. Claims that remain unestablished

1. Nonlinear substrate **advantage** over linear substrate on persistence or collective processing (equal performance).
2. Nonlinear substrate **advantage** over direct messaging, blackboard, or pheromone on primary Exp B F1 (tied at ceiling).
3. Hazard avoidance utility / Level 4 agentic utility (G8 FAIL).
4. Level 5 comparative specialized advantage.
5. Semantic multi-channel encoding in a single scalar field.
6. Blind search recovery without protocol-known probe sites.
7. Any claim that the broader theory of information gravity is “proven” by this simulation.

Original Task 6’s reported nonlinear advantage is **not** confirmed under corrected validity constraints.

---

## 20. Recommended next experiment

**Justify from findings:** Exp B saturated (ceiling) and linear matched nonlinear; G8 failed functionally.

**Next protocol (new confirmatory ID, do not retune this one):**

1. **Harder collective-processing task** without known probe coordinates: Agent C must locate and classify interaction structure by scanning; include overlapping deposits, amplitude coding, and adversarial XY_far geometries that break simple midpoint heuristics.  
2. **Stress persistence where linear fails:** Longer delays, stronger diffusion, weaker deposits near threshold — to test whether bistability yields recoverable memory after linear signals fall below readout.  
3. **Hazard redesign for G8:** Forced paths that would enter known hazards unless diverted; verify nonzero avoided crossings and architecture-dependent exposure before claiming agentic utility.

Until (1)–(2) show nonlinear > linear and > best conventional on a non-ceiling primary endpoint with paired \(d_z\) and multiplicity control, Outcome C remains unsupported.

---

## Deliverables

| File | Role |
|---|---|
| `EXP6_CORRECTIVE_AUDIT.md` | Defect audit (Phase 1) |
| `exp6_corrected/` | Corrective package |
| `exp6_corrected_nonlinear_advantage.py` | Entry point |
| `exp6_corrected_gate_log.json` | G1–G4 detailed log |
| `exp6_corrected_pilot_results.json` | Pilot (exploratory) |
| `exp6_corrected_results.json` | Confirmatory + analysis |
| `exp6_corrected_run.log` | Run transcript |
| `EXP6_CORRECTED_REPORT.md` | This report |

Original files untouched (checksums recorded at run time in session log).
