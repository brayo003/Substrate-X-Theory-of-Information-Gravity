# RESCUE GATE
## SXC-IGC Experimental Program — Final Frozen Decision

**Date:** 2026-08-22
**Gate version:** 1 (frozen — not revisable after this date without cited new evidence)
**Based on:** EXPERIMENTAL_RESCUE_AUDIT.md, DISCRIMINATOR_SEARCH.md,
  GAP7_THEORY_AUDIT.md, FINAL_DESIGN_SEARCH.md, ADVERSARIAL_NULL_AUDIT.md,
  TWO_STAGE_STATISTICS_AUDIT.md, ESTIMATOR_AUDIT_FINAL.md

---

## FINAL DECISION

**NO HARDWARE EXECUTION AUTHORIZED.**

**NO VALID RESCUE DESIGN EXISTS within the current theoretical and hardware constraints.**

The experimental program is classified: **STATE 4 — NOT CURRENTLY RESCUABLE.**

---

## What Was Established

### The original route failed

The IBM Brisbane spatial K₀ correlation experiment (12-qubit linear chain,
Ramsey parity estimator, LLR test) was audited through eight phases.

Four gate conditions failed:

| Gate condition | Requirement | Result |
|---------------|-------------|--------|
| Global FP ≤ 10% | All null models ≤ 10% FP | **FAIL — M7_pow1.0: 19.7%, M9_twobath: 15.3%** |
| Power ≥ 80% | LLR distribution reaches threshold | **FAIL — power = 0% (non-discriminating)** |
| Adversarial search fails | No null model defeats FP control | **FAIL — M7 defeats FP at 19.7%** |
| Held-out validation | Independent validation set passes | **FAIL — power = 0% on validation set** |

The root cause is geometric degeneracy: over r = 200–2200 µm with 11 unique
separation bins, K₀ and power-law covariance are both approximately logarithmic.
Shape distance = 0.073, giving SNR ≈ 2. The test has zero useful discrimination
content regardless of shot count, threshold, or fitter sophistication.

### No rescue discriminator was found

A systematic search through all C2 theory predictions found no observable
satisfying all four required criteria simultaneously:

| Candidate | Derivable from C2? | Survives adversarial nulls? | Executable on current hardware? |
|-----------|-------------------|----------------------------|--------------------------------|
| K₀ spatial shape | Yes | **No** — M7/M9 defeat it | Blocked |
| Temporal ω² scaling | Yes | **No** — any Lorentzian bath matches | — |
| NM Ramsey onset | Yes | **No** — any finite-memory bath matches | — |
| P3: c = ξ_c/(2τ_B) | Yes | Conditional (if c ≪ v_sound) | **No** — NMP = 0.033, needs ≥ 0.1 |
| c(T) = const vs temperature | Yes | Yes | **No** — requires T-variation hardware |
| Lorentzian rolloff | Yes | **No** — identical to OU bath | — |
| Multi-qubit higher-order | Only for Gaussian substrate | **No** — Gaussian bath matches | — |

The P3 self-consistency test (c = ξ_c/(2τ_B)) is the strongest surviving
candidate. It is not executable because:
1. NMP = τ_B · Γ_φ = 0.033 on Brisbane (threshold: 0.1) — τ_B not extractable
2. ξ_c measurement blocked by K₀/power-law degeneracy
3. c is a free parameter of the theory (GAP-7) — no independent prediction exists

### GAP-7 is fundamental

The substrate propagation speed c cannot be derived from C2. It equals the PRW
particle speed v = h/Δt, which is a free parameter with no equation in the theory
that constrains it. This is not a computational gap — it is structural. The
telegrapher equation holds for all v > 0. No equilibrium, thermodynamic, or
dimensional argument selects v.

Without resolving GAP-7, any measurement of ξ_c is a post-hoc measurement,
not a theory test. The theory accommodates any ξ_c.

---

## What Must Change Before Re-opening the Gate

The gate may only be re-opened if at least ONE item from EACH column below
is satisfied and documented with cited evidence:

### Column 1 — Theoretical precondition (one required)

| Item | What is needed |
|------|----------------|
| T1 | GAP-7 resolved: c independently predicted or identified from substrate physics |
| T2 | New C2 prediction derived that is not reproduced by any physically plausible conventional mechanism |
| T3 | Theoretical proof that M7 (power-law) and M9 (two-bath) cannot arise on IBM-class superconducting chips under the proposed experimental conditions |

### Column 2 — Hardware precondition (one required)

| Item | What is needed |
|------|----------------|
| H1 | NMP ≥ 0.1 demonstrated on candidate device (requires τ_B ≥ 15 µs or T₂ ≪ current Brisbane median) |
| H2 | Spatial range spanning 0.1–10 ξ_c with ≥ 20 unique separation bins validated against adversarial null family |
| H3 | Independent physical exclusion of M7 and M9 on the candidate device by non-decoherence measurement (e.g., ZZ coupling spectroscopy, crosstalk characterisation) |
| H4 | Access to controlled temperature variation on a dilution fridge with the candidate device (enables c(T) test) |

**Both a T-item and an H-item are required.** Neither alone is sufficient.

---

## What This Conclusion Does Not Mean

1. It does not mean SXC-IGC is incorrect.
   The theory has not been tested. It has been found not yet testable
   under the specific experimental conditions examined.

2. It does not mean the IBM Brisbane experiment produces evidence against SXC-IGC.
   The experiment cannot produce evidence for or against the theory
   because its discriminating power is zero against the relevant null family.

3. It does not mean decoherence spatial correlations are uninteresting.
   If K₀-shaped spatial correlation were found after independent exclusion
   of M7 and M9, that would be a scientifically significant finding — but
   it would demonstrate that some K₀-correlated process exists, not that
   SXC-IGC is correct.

4. It does not authorize a weakened version of the experiment.
   - Do not lower the FP threshold to pass M7 or M9.
   - Do not remove M7 or M9 from the null family because they make the test harder.
   - Do not redefine the hypothesis to match whatever the data show.
   - Do not claim "evidence for SXC-IGC" from a result that only beats exponential null.

---

## State of Each Deliverable

| Document | Status |
|----------|--------|
| ESTIMATOR_AUDIT_FINAL.md | Complete — estimator bug found and corrected |
| ADVERSARIAL_NULL_AUDIT.md | Complete — M7/M9 defeat FP control |
| TWO_STAGE_STATISTICS_AUDIT.md | Complete — power = 0% at frozen threshold |
| FINAL_DESIGN_SEARCH.md | Complete — no feasible design in searched space |
| HARDWARE_READINESS_AUDIT.md | Complete — hardware moot; statistical gate fails first |
| FINAL_PRE_HARDWARE_GATE.md | Complete — updated to reflect corrected analysis |
| GAP7_THEORY_AUDIT.md | Complete — c is fundamentally free |
| DISCRIMINATOR_SEARCH.md | Complete — no class-A observable executable on current hardware |
| EXPERIMENTAL_RESCUE_AUDIT.md | Complete — Phases A–H; STATE 4 |
| **RESCUE_GATE.md** | **This document — final frozen decision** |

---

## Single-Sentence Verdict

The SXC-IGC spatial K₀ decoherence experiment is not currently viable because
the theory has a free parameter that prevents a parameter-free prediction (GAP-7),
the hardware geometry cannot resolve the K₀/power-law shape degeneracy, and the
non-Markovianity parameter is too small to measure the temporal correlation
length needed for the self-consistency test.

---

*Gate frozen: 2026-08-22 13:16 UTC+3.*
*All criteria established before hardware.*
*Not revisable post-hoc without the cited preconditions above.*
*Do not access IBM QPU. Do not submit any quantum job. Do not claim a positive result.*
