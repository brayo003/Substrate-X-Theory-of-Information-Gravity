# PROJECT_CONTINUATION_DECISION.md
## SXC-IGC/C2 — Phase I Project Continuation Decision

**Date:** 2026-08-22
**Based strictly on:** THEORY_CLOSURE_AUDIT.md, GAP7_REDERIVATION.md,
  PARAMETER_OBSERVABLE_RANK.md, CONVENTIONAL_EQUIVALENCE_AUDIT.md,
  SURVIVING_THEORY_PREDICTIONS.md, RESCUE_GATE.md, EXPERIMENTAL_RESCUE_AUDIT.md

**This document answers five questions and produces one classification.**

---

## The Five Required Questions

### Q1. Is GAP-7 actually derivable from the existing theory?

**Answer: NO.**

GAP7_REDERIVATION.md tested all 25 independent derivation routes.
Result: 19 FAILED, 5 BLOCKED (unproved prerequisite), 0 succeeded.

The structural proof confirms: models M₁=(v,λ) and M₁'=(αv,λ) are both
valid C2 models for any α > 0, and no C2 equation distinguishes them in the
temporal observable sector. The substrate speed c is not determined by:
- dimensional analysis
- conservation laws
- dispersion relations
- equilibrium conditions
- entropy extremization
- any coupling to quantum or gravitational sectors
- any normalization or boundary condition

GAP-7 is a structural property of the theory, not a derivation gap.
The PRW model describes dynamics for a substrate with speed v without
saying what determines v.

---

### Q2. Does C2 contain at least one parameter-constrained empirical prediction?

**Answer: NO — with one narrow conditional qualification.**

PARAMETER_OBSERVABLE_RANK.md established:
- The prediction map has rank 3 over a 4-dimensional free parameter space
- One null direction exists (g vs s₀ degeneracy)
- No observable is a function of a single independently-constrained parameter

SURVIVING_THEORY_PREDICTIONS.md found: zero predictions pass all four
criteria unconditionally.

The conditional qualification: the P3 consistency relation c = ξ_c/(2τ_B)
is a quantitative constraint (once c is measured from one set of data, all
subsequent measurements must give the same ratio). But:
- c is not predicted by the theory — it must be measured first
- The theory provides no bound on what c should be
- This is a consistency check, not a forward prediction

A consistency check is not a parameter-constrained empirical prediction in
the sense required for a falsifiability test. It can falsify C2 (if the ratio
changes), but it cannot confirm C2 (any constant ratio is consistent with C2
for some value of the free parameter c).

---

### Q3. Does that prediction distinguish SXC-IGC from physically plausible conventional mechanisms?

**Answer: CONDITIONALLY — only if the measured c is anomalous.**

CONVENTIONAL_EQUIVALENCE_AUDIT.md established:
- P1 (Lorentzian PSD): fully equivalent to OU bath
- P2 (ω_rot² scaling): fully equivalent to rotating-frame bath
- P3 (Gaussian NM onset): fully equivalent to any Gaussian bath
- P4 (K₀ spatial shape): shape-degenerate with M7/M9 on current hardware
- P5 (P3 consistency): conditionally non-equivalent

For P5: conventional independent noise sources have no mechanism that forces
ξ_corr/(2τ_corr) = constant velocity. If the measured c is anomalous
(e.g., ~50 m/s, orders of magnitude below any acoustic mode), no conventional
mechanism explains this. But:
- If c ≈ v_sound: consistent with phonon bath — not discriminating
- If c ≈ c_light: consistent with EM coupling — not discriminating
- Only c ≪ v_sound would be genuinely anomalous

The theory provides no prediction for what value c will have, so the
discriminating power of P5 is not guaranteed before the measurement.

---

### Q4. Is there any legitimate theoretical route that can reopen the experimental gate?

**Answer: YES — two routes exist, but both require work outside current C2.**

**Route T1 — Physical substrate identification:**
If C2 is extended by identifying the substrate with a specific physical medium
(e.g., acoustic phonons of a specific polarization, a topological mode, a
novel slow surface excitation), then c = v_medium is determined.

Requirements:
- A physical argument for why that medium IS the C2 substrate
- Independent derivation of v_medium from material properties
- New predictions from the identification (material-dependent c,
  temperature dependence c(T), pressure dependence, etc.)
- These new predictions must be distinct from the conventional phonon bath

This route requires extending C2 — adding new physics, not deriving
from existing axioms. It would constitute a NEW THEORY EXTENSION, not
a derivation within current C2.

**Route T2 — Additional axiom constraining v:**
A new axiom relating v to other C2 quantities (e.g., via ℏ and a mass scale,
or via the CCA causal action conjecture CCA-C3). This would reduce the free
parameter count by 1.

Requirements:
- The new axiom must not be circular
- It must produce a unique, derivable value for v
- It must create new predictions beyond those already in C2
- The axiom must be explicitly documented as NEW AXIOM REQUIRED

Neither T1 nor T2 is a derivation from existing C2. Both require new theoretical
work. Neither is available today.

---

### Q5. If no valid route exists, is the correct conclusion that SXC-IGC has reached a theoretical underdetermination boundary?

**Answer: YES.**

C2 has reached the boundary of what its current axioms can determine.
The theory correctly describes the mathematical consequences of a substrate
with parameters (v, λ, g, s₀) — but none of these parameters are derived
from the axioms. The theory is a consistent mathematical framework that
cannot, in its current form, produce a single parameter-free prediction.

This is not a failure of the derivation machinery. The derivations themselves
are correct (telegrapher equation, C_JJ, K₀ correlator, Γ_φ). The failure
is at the level of the axiom set: the axioms describe how the substrate works
without specifying what the substrate is or what its parameters are.

This is the underdetermination boundary: the theory is consistent with
infinitely many physical realizations, all giving the same functional forms
but different scales. Without an additional principle that selects among
these realizations, the theory cannot make contact with experiment at the
level of specific predicted values.

---

## Phase I Classification

Based strictly on the audit results, classify the project into exactly one state:

**Available states:**
1. CONTINUE THEORY DEVELOPMENT
2. CONTINUE ONLY AS FORMAL THEORETICAL RESEARCH
3. PAUSE EMPIRICAL PROGRAM
4. TERMINATE SXC-IGC AS A DISTINCT EMPIRICAL THEORY
5. REFORMULATE FROM A NEW AXIOMATIC FOUNDATION

---

### Assessment

**State 1 (CONTINUE THEORY DEVELOPMENT):**
Applies if there is a concrete, well-defined theoretical problem whose
solution would produce a parameter-constrained prediction.

Assessment: YES — the problem is concrete. GAP-7 identifies the missing
element precisely. Routes T1 and T2 above specify exactly what theoretical
work is needed. The problem is hard but not impossible, and the C2 framework
has genuine mathematical content worth developing.

**State 2 (CONTINUE ONLY AS FORMAL THEORETICAL RESEARCH):**
Applies if the theory has mathematical content but no current path to
empirical contact.

Assessment: YES — this describes the current situation accurately.
The CCA/SCC foundational layer, the PRW transport derivations, the
non-Markovian decoherence formalism, and the Q diagnostic all have
mathematical interest independent of the experimental program.

**State 3 (PAUSE EMPIRICAL PROGRAM):**
Applies if the empirical program is blocked by a specific resolvable
condition, and the pause is temporary pending that resolution.

Assessment: YES — RESCUE_GATE.md specifies exactly what must change
before hardware execution is authorized. The pause is not permanent;
it has two specific exit conditions (T-item AND H-item from RESCUE_GATE.md).

**State 4 (TERMINATE SXC-IGC AS A DISTINCT EMPIRICAL THEORY):**
Applies if the theory cannot be distinguished from conventional mechanisms
and no route to distinctiveness exists.

Assessment: NO — P3 provides a conditional discriminator that conventional
physics cannot generically reproduce. The theory is not empirically
equivalent in all cases. Termination is not warranted.

**State 5 (REFORMULATE FROM A NEW AXIOMATIC FOUNDATION):**
Applies if the current axioms are internally inconsistent or systematically
produce the wrong predictions.

Assessment: NO — C2 is internally consistent (STATE T4 was rejected).
The current axioms are correct as far as they go. What is needed is not
a reformulation but an extension (new axiom or physical identification).

---

## Decision

**Primary classification: STATE 3 — PAUSE EMPIRICAL PROGRAM**

The empirical program is paused pending two specific conditions:
1. Theoretical (one of T1 or T2 from RESCUE_GATE.md)
2. Hardware (one of H1–H4 from RESCUE_GATE.md)

**Secondary classification: STATE 2 — CONTINUE AS FORMAL THEORETICAL RESEARCH**

The following theoretical work is independently justified and does not
require resolving GAP-7 first:

Priority 1 (near-term, independent):
- F11: Non-Markovian corrections to Γ_φ (standard techniques available)
- F9: CCA causal entropy non-decrease proof (clear strategy)
- F8: CCA GNS representation theorem (analogy with C*-algebras)

Priority 2 (medium-term, addresses GAP-7):
- Physical substrate identification (Route T1): requires engaging with
  materials science and slow-wave physics to identify candidate media
- New axiom search (Route T2): requires investigating whether CCA-C3
  (causal action conjecture) can be proved and whether it constrains v

Priority 3 (long-term, fundamental):
- F7: Large-N universality forcing O1 and O2 (central open question)
- F1: Microscopic reversibility PA1 (unresolved foundational gap)
- F4: Lorentz group derivation (requires continuum limit tools)

---

## What This Decision Does Not Mean

1. It does not mean C2 is incorrect.
   The theory has not been falsified. It has been found underdetermined.

2. It does not authorize further hardware work.
   RESCUE_GATE.md remains frozen. No IBM QPU jobs until both preconditions
   are satisfied and documented.

3. It does not mean the mathematical work is wasted.
   The PRW derivations, the C_JJ formula, the K₀ spatial correlator, the
   Q diagnostic, and the Lindblad reduction are all correct and useful
   independent of the experimental status.

4. It does not mean the theory is empirically equivalent to conventional models.
   P3 retains conditional discriminating power. If hardware conditions improve
   AND the measured c is anomalous, the program can reopen.

---

## Summary

| Question | Answer |
|----------|--------|
| Q1: Is GAP-7 derivable? | No — 25 routes, all failed |
| Q2: Does C2 have a parameter-constrained prediction? | No — only conditional consistency check |
| Q3: Does it distinguish from conventional physics? | Conditionally — only if c anomalous |
| Q4: Legitimate route to reopening the gate? | Yes — Route T1 or T2, both require new theory |
| Q5: Has the theory reached underdetermination boundary? | Yes |
| Classification | **STATE 3 (Pause) + STATE 2 (Formal theory continues)** |

---

*Decision frozen: 2026-08-22*
*Revisable only with cited new evidence satisfying RESCUE_GATE.md preconditions*
*or with a documented new theoretical derivation resolving GAP-7.*
