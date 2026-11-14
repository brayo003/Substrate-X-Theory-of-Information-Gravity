# EXP8 Experimental Report — Substrate Computational Expressivity

**Date:** 2026-11-13  
**Project:** SXC-IGC `sim_world`  
**Prior milestone:** Task 7 — Outcome C, Acceptance Level 3 (carried forward as reported findings; not re-verified)  
**Overall acceptance level:** **4 — Behaviourally useful computation**  
**Central answer:** The nonlinear reaction-telegraph substrate can intrinsically perform **high-basin coincidence detection**, **finite-window temporal integration**, **equal-mass spatial arrangement discrimination**, and **threshold/hysteresis switching** via reaction nonlinearity; scalar conflict is amplitude cancel (not semantic); “pattern completion” is attractor retention, not multi-feature reconstruction. Symbolic baselines still solve the same decision tasks.

---

## 1. Executive summary

Task 8 asks what the field **computes** through its own dynamics (Track C), not what it stores or relays.

Under a frozen protocol (\(r=-0.5,a=2,b=1,\tau=1,c=1,\Delta t=0.05\); single-Gaussian encoding; high-basin decoder \(\theta=0.85\)):

| Operation | Category | One-line result |
|---|---|---|
| A Coincidence | **5** | Near/triple latch F1=1.0; linear & readout-only = 0; response surface finite; behavioural bridge causal |
| B Temporal | **4** | Simultaneous latch; fails by delay 15–40; window ~5 ticks at operating point |
| C Spatial (equal mass) | **4** | Cluster/triangle activate; dispersed/line3 do not; linear cluster = 0 |
| D Threshold/hysteresis | **5** | Forward amp≈0.85; reverse drop needs ~0.7 neg; bridge uses same latch |
| E Conflict | **2** | Agree latch nonlinear; oppose cancel also linear — no semantics |
| F Pattern | **3** | Recovery after damage+partial = attractor retention, not true completion |

All gates E1–E10 PASS. Acceptance **Level 4** (not 5: no superiority over symbolic/messaging architectures).

---

## 2. Repository audit

See `EXP8_PRE_IMPLEMENTATION_AUDIT.md`.

**Independently verified:** `evolve_field_nonlinear` path; Laplacian \(\tau\)-factor docstring/code mismatch (cancels at \(\tau=1\)); Dirichlet-like boundaries; explicit Euler; Task 7 dual-kind deposit ambiguity (effective ~2× amp).

**Preservation:** All Task 6 corrective and Task 7 listed checksums OK after implementation (`exp8/task6_checksums_*.txt`, `exp8/task7_checksums_*.txt`).

---

## 3. Mathematical model

Implemented reaction-telegraph (code form at \(\tau=1\)):

\[
\partial_t s=v,\quad
\partial_t v=\frac{c^2\nabla^2 s+rs+as^2-bs^3+S-v}{\tau}
\]

Bistable equilibria \(s=0\), \(s_-\approx0.293\), \(s_+\approx1.707\). Full theory: `EXP8_THEORETICAL_SPECIFICATION.md`.

**Decoder:** \(O=\mathbf{1}[\max_{\mathrm{ROI}} s\ge 0.85]\) on field values only (never deposit log). \(\theta=0.85\) chosen so instantaneous near-pair peak0≈0.71 cannot pass without dynamical growth (pilot confound at \(\theta=0.40\)).

---

## 4. Methodology

| Phase | Seeds | Artifact |
|---|---|---|
| Pilot (exploratory) | 0–7 | `exp8_pilot_results.json` |
| Freeze | — | `exp8_configuration.json` |
| Confirmatory | 300–323 (N=24) | `exp8_results.json` |
| Tests | — | `tests/test_exp8_computational_expressivity.py` (10 OK) |

Primary stats: paired seed-matched comparisons + Bonferroni across 6 slots; permutation p as robustness. Pilot not used for confirmatory inference.

---

## 5. Results A–F (confirmatory N=24)

### A — Coincidence detection

- Nonlinear: near_pair F1=1.0, far_pair accuracy=1.0, single accuracy=1.0, triple_near F1=1.0 (overall F1=1.0, n=96 case-trials under nonlinear ablations in primary metric subset).
- Linear / reaction_off / readout_only near: **p_activate=0**.
- **no_propagation** near: p_activate=1.0 → at sep=3 deposits already overlap; latch is **local reaction on overlap**, not long-range telegraph bridging.
- **no_inertia** near: p_activate=1.0 → inertia not required for this primitive.
- Response surface (amp=0.50): activate at sep∈{2,3}; **fail for sep≥4**. Higher amp widens separation window (failure region documented in `A.response_surface_nl`).
- Paired nl−lin near correctness: mean_diff=1.0, p_perm≈0.0002, Bonferroni-adjusted significant.

### B — Temporal integration

| delay | p_activate (nl) | mean local_max |
|---|---|---|
| 0 | 1.00 | 0.915 |
| 2 | 1.00 | 0.902 |
| 5 | 0.75 | 0.883 |
| 10 | 0.58 | 0.847 |
| 15 | 0.04 | 0.809 |
| 20 | 0.00 | 0.770 |
| 40 | 0.00 | 0.620 |

Finite memory window; delay0−delay40 activation mean_diff=1.0 (significant). **Order discrimination not claimed** (scalar bistability). Soft boundary near delay 5–10.

### C — Spatial discrimination (equal mass M=1.0)

| geometry | nl p_act | lin p_act |
|---|---|---|
| cluster | 0.958 | 0.0 |
| triangle | 0.917 | 0.0 |
| dispersed | 0.0 | 0.0 |
| line3 | 0.0 | 0.0 |

Cluster−dispersed activation mean_diff≈0.958, d_z≈4.69, significant.

### D — Threshold / hysteresis

- Mean forward activation amp (single deposit → high basin): **0.85** (n=24).
- After strong deposit, state retained; reverse drop requires neg amp ≈ **0.70**.
- Linear does not high-basin latch under the same forward sweep protocol.

### E — Conflict / interference

- Agree (near positives): nl accuracy 1.0; linear 0.0 (nonlinear latch).
- Oppose (same-site ±): both architectures cancel → accuracy 1.0 for “no activate” — **Category 2 superposition**, not semantic conflict resolution.
- Limitation: scalar polarity ≠ multi-semantic channels.

### F — Pattern / degradation

- completion_lift_nl = 1.0 (partial_after_template activates; partial_only does not).
- Linear never recovers high basin after template protocol.
- **Interpretation:** bistable attractor retention / re-excitation — **not** multi-feature pattern completion. Category 3 ceiling appropriate.

---

## 6. Mechanistic ablations (summary)

| Ablation | A near latch |
|---|---|
| nonlinear_full | yes |
| linear_telegraph | no |
| reaction_off | no |
| readout_only | no |
| no_propagation | yes (overlap already present) |
| no_inertia | yes |

**Mechanism for A/C/D at near separations:** cubic reaction bistability acting on spatially overlapping deposits. Propagation expands operating envelope at higher amps but is not necessary when Gaussians already overlap. Inertia not essential for the tested latch.

---

## 7. Numerical validation

`numerical.all_pass=True`:

- dt∈{0.05,0.025,0.0125} agree on activation=1  
- 30×30 vs 40×40 agree on activation=1  
- single deposit no spurious high-basin  
- boundedness under amp=2  
- nl latch vs linear decay on matched deposits  

No confirmatory claim treated as numerically unresolved.

---

## 8. Baselines and fairness

| Baseline | Result |
|---|---|
| Symbolic distance AND | accuracy 1.0 |
| Linear telegraph | fails high-basin coincidence |
| Independent agents | bridge F1=0 |
| Task 7 messaging/BB | F1=1.0 on AND (carried forward; not re-litigated) |

Fairness notes in `exp8_results.json` → `fairness`. **Task 8 does not claim nonlinear superiority over symbolic systems.**

---

## 9. Behavioural bridge

Justified by Category≥4 primitives. Two observers deposit; decision agent reads field only.

| mode | F1 |
|---|---|
| nonlinear_full | 1.0 |
| linear_telegraph | 0.0 |
| reaction_off | 0.0 |
| independent | 0.0 |
| symbolic | 1.0 |

`causal_pass=True` (E10). Symbolic still perfect — expected.

---

## 10. Classification and gates

| Gate | Status |
|---|---|
| E1 Audit | PASS |
| E2 Spec | PASS |
| E3 ≥1 operation | PASS |
| E4 Numerical | PASS |
| E5 Ablations | PASS |
| E6 Parameter/noise ranges | PASS (response surface + temporal/spatial sweeps) |
| E7 Confirmatory | PASS |
| E8 Failure regions | PASS |
| E9 Baselines | PASS |
| E10 Behavioural | PASS |

**Acceptance Level 4.** Level 5 withheld (no distinctive advantage vs matched symbolic architectures).

---

## 11. Failure analysis and limitations

1. Instantaneous overlap can exceed separatrix thresholds — mitigated by \(\theta=0.85\).  
2. At operating amp, sep≥4 fails coincidence — finite spatial window.  
3. Temporal soft edge at delay≈5–10.  
4. Scalar field cannot host multi-semantic conflict.  
5. Pattern “completion” ≠ associative multi-bit reconstruction.  
6. Solver Laplacian \(\tau\) factor ambiguity for \(\tau\neq1\).  
7. Ceiling risk on schedule-labelled A cases (F1=1.0) — surface still shows failures outside window.

---

## 12. Literature / novelty

See `EXP8_LITERATURE_AND_NOVELTY_REVIEW.md`. Contribution = characterized operating regime + ablations in this stack; not a claim of unprecedented field computing.

---

## 13. What can this substrate compute?

**Because of nonlinear spatiotemporal (primarily reaction) dynamics:**

1. **Coincidence / multi-source threshold latch** into a high basin when subthreshold deposits overlap in space (and, within a short window, in time).  
2. **Arrangement-sensitive collective switching** under equal total mass.  
3. **Hysteretic state retention** usable by downstream agents as a distributed decision bit.

**Not demonstrated as intrinsic computation here:** semantic conflict resolution; true pattern completion; temporal order logic; superiority over explicit messaging/blackboard/symbolic distance.

---

## 14. Recommended next research direction

1. Multi-flavor / multi-channel fields for semantic interference.  
2. Systematic comparison to FitzHugh–Nagumo / BZ gate libraries on identical batteries.  
3. Tasks where **propagation delay and spatial continuum** matter (beyond deposit-overlap AND).  
4. Reservoir-style learned readouts vs fixed thresholds.  
5. Leave \(\tau\neq1\) only after resolving Laplacian factor ambiguity in the solver docstring vs code.

---

## 15. Evidence index

| Deliverable | Path |
|---|---|
| Audit | `EXP8_PRE_IMPLEMENTATION_AUDIT.md` |
| Theory | `EXP8_THEORETICAL_SPECIFICATION.md` |
| Literature | `EXP8_LITERATURE_AND_NOVELTY_REVIEW.md` |
| Code | `exp8/`, `exp8_substrate_computational_expressivity.py` |
| Config freeze | `exp8_configuration.json` |
| Pilot | `exp8_pilot_results.json` |
| Confirmatory | `exp8_results.json` |
| Tests | `tests/test_exp8_computational_expressivity.py` |
| Checksums | `exp8/task{6,7}_checksums_{before,after}.txt` |
