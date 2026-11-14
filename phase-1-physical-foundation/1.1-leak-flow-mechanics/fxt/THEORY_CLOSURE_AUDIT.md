# THEORY_CLOSURE_AUDIT.md
## C2/SXC-IGC Theory Closure and Falsifiability Audit

**Date:** 2026-08-22
**Status:** COMPLETE — STATE T2 (see Phase H)
**Sources:** C2_FOUNDATIONS.md, C2_FRONTIER_MAP.md, C2_MISSING_PRINCIPLES.md,
  substrate_transport_derivation.md, 00_THEORY_AUDIT.md, GAP7_REDERIVATION.md,
  FOUNDATIONAL_ADVERSARIAL_FINAL_AUDIT.md, 32_C_PRW_SPEED_DERIVATION_AUDIT.md

---

## PHASE A — PRIMITIVE ONTOLOGY

### A.1 What C2 Posits as Primitive

C2 is a multi-layer theory. The layers are listed from most fundamental
to most derived:

**Layer 0 — Causal-Compositional Algebra (CCA):**
Primitive: a tuple (O, M, ⊗, ≤, †, ε) satisfying five axioms (Ax1–Ax5).
- O: finite set of objects
- M: morphisms with source and target in O
- ⊗: composition/parallel combination
- ≤: causal partial order
- †: time-reversal involution
- ε: probability weight map ε: M → [0,1]

Status of CCA: internally consistent mathematical structure. No c, no ℏ,
no Hilbert space at this level. Real-valued probability is primitive.

**Layer 1 — Symmetric Compositional Closure (SCC):**
Derived from CCA + additional physical assumptions M1–M8 (compactness AA1,
complex vector space M8).
Status: M8 (complex structure) is NOT derivable from M1–M7. It is an
independent axiom. (FOUNDATIONAL_ADVERSARIAL_FINAL_AUDIT.md §4.)

**Layer 2 — PRW Transport:**
Primitive: walker state (x, σ) ∈ ℝ × {+1,−1}, speed v, reversal rate λ.
Derived: telegrapher equation, ξ_c = v/λ, τ_B = 1/(2λ).

**Layer 3 — Quantum Coupling:**
Primitive: H_int = g·J(x_q, t)·σ_z (interaction Hamiltonian).
Coupling constant g is free (GAP-7 / F10 in C2_FRONTIER_MAP.md).

**Layer 4 — Observable Predictions:**
Derived (conditionally): Γ_φ = k_rot·ω_rot²,
C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c).

### A.2 Parameter Classification

| Parameter | Symbol | Layer | Type | Status |
|-----------|--------|-------|------|--------|
| PRW particle speed | v = c | 2 | velocity | **D — FREE** |
| PRW reversal rate | λ | 2 | rate | **D — FREE** |
| Bath correlation time | τ_B = 1/(2λ) | 2 | time | B — derived from λ |
| Coherence length | ξ_c = v/λ | 2 | length | B — derived from v,λ |
| Diffusivity | D = c²τ_B | 2 | diffusivity | B — derived from v,λ |
| Coupling constant | g | 3 | coupling | **D — FREE** |
| Substrate density | s₀ | 3 | density | **D — FREE** |
| Planck constant | ℏ | 3 | action | **F — imported** |
| Qubit radius | r_q | 3 | length | **E — empirical** |
| Dephasing rate | Γ_φ | 4 | rate | B — derived (conditional) |
| Spatial scale | k_rot | 4 | coupling | C — constrained by fit |

Parameter type key: A=fundamental+specified, B=derived, C=constrained,
D=free, E=empirical, F=imported from conventional physics.

### A.3 State Variables

Transport layer: s(x,t) [information density], J(x,t) [information flux].
Quantum layer: ρ_S(t) [qubit density matrix].
The substrate state s is classical; ρ_S is quantum. No quantum state for
the substrate itself is defined.

### A.4 Fundamental Postulates

Listed with classification:

1. PRW balance equations [∂n⁺/∂t = −v∂n⁺/∂x − λn⁺ + λn⁻, ...] — ASSUMED (A-PRW1,2,3)
2. Identification s = "information density" — ASSUMED (interpretive)
3. Substrate bulk velocity v_sub given externally — ASSUMED (A3)
4. H_int = g·J·σ_z — ASSUMED (A-HC5, A-HC6)
5. Born-Markov approximations — ASSUMED (A-HC1, A-HC2)
6. Secular approximation — ASSUMED (A-HC3)
7. Stationary substrate — ASSUMED (A-HC4)
8. M1 (matrix fields) — ASSUMED (not derivable from transport layer)
9. M2 (Moyal deformation) — ASSUMED (not derivable from M1 or transport)
10. M8 (complex vector space) — ASSUMED (not derivable from M1–M7)

Total independent assumptions for the main prediction: ≥ 10 (listed above)
plus 8 assumptions A1–A8 in the transport layer = ≥ 18 total.

---

## PHASE B — GAP-7 HOSTILE RE-DERIVATION

Full re-derivation in GAP7_REDERIVATION.md. Summary of findings:

All 25 independent routes were tested. Result: 19 FAILED, 5 BLOCKED, 0 succeeded.

The structural proof (GAP7_REDERIVATION.md §"Structural Proof"):
Consider M₁ = (v, λ) and M₁' = (αv, λ) for any α > 0 (λ held fixed).
Both models have:
- Identical τ_B = 1/(2λ)
- Identical S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)
- Identical Γ_φ = k_rot·ω_rot²
- Different ξ_c: v/λ vs αv/λ

No equation within C2 prevents both from being valid simultaneously.
Therefore no temporal measurement can distinguish them, and c is not
determined by the temporal sector of C2.

**GAP-7 CONFIRMED: c is structurally free.**

---

## PHASE C — PARAMETER REDUNDANCY AND REPARAMETERIZATION

### C.1 Reparameterization Structure

The C2 transport theory depends on v and λ through two combinations:
  - τ_B = 1/(2λ)   [temporal scale, appears in S_JJ(ω)]
  - ξ_c = v/λ      [spatial scale, appears in C_JJ(r)]

These two combinations are independent. Neither alone determines the other.
The theory has effectively two independent observable scales: τ_B (temporal)
and ξ_c (spatial).

The individual parameters v and λ are NOT separately observable from the
combinations τ_B and ξ_c:
  - From τ_B alone: λ = 1/(2τ_B) is determined, but v is free.
  - From ξ_c alone: v/λ = ξ_c is determined, but v and λ individually are free.
  - From both τ_B AND ξ_c: c = ξ_c/(2τ_B) is determined — this is the P3 test.

### C.2 Can c Be Eliminated by Nondimensionalization?

Form dimensionless ratios from C2 observables:
  - r/ξ_c: the argument of K₀ in the spatial prediction
  - t/τ_B: the argument of exp(−t/τ_B) in the temporal decay
  - ω·τ_B: the argument of the Lorentzian rolloff
  - NMP = Γ_φ·τ_B: the non-Markovianity parameter

All dimensionless observables involve ξ_c and τ_B, never v and λ separately.
Therefore c = v appears in observables ONLY through the combination ξ_c = v/λ.

**Consequence:** Measuring ALL C2 observables only determines (τ_B, ξ_c), not
(v, λ) separately. The ratio c = ξ_c/(2τ_B) is measurable from data but
is not theoretically predicted by C2.

### C.3 Theory-Level vs. Observable-Level Parameters

The theory has 2 free parameters at the transport level: {v, λ}.
The observable sector resolves into 2 free scales: {τ_B, ξ_c}.
The map (v, λ) → (τ_B, ξ_c) = (1/(2λ), v/λ) is a bijection (given v,λ > 0).
Therefore there is no parameter redundancy — the two free parameters are
genuine and independently observable in principle.

But both τ_B AND ξ_c must be measured to determine c = ξ_c/(2τ_B).
The theory provides no constraint on their ratio.

---

## PHASE D — PARAMETER-TO-OBSERVABLE RANK ANALYSIS

Full matrix in PARAMETER_OBSERVABLE_RANK.md. Summary:

The C2 prediction map has:
- 5 free parameters: {v, λ, g, s₀, r_q} (r_q is empirical)
- 4 observable types: {Γ_φ(ω_rot), S_JJ(ω), C_Γ(r), NM Ramsey curvature}

The rank of the prediction map is 3 (not 4, not 5), because:
- Γ_φ(ω_rot) constrains the product g²s₀²r_q²τ_B/ℏ² (1 combination)
- S_JJ(ω) constrains (S₀, τ_B) = (g²s₀², 1/(2λ)) (2 combinations)
- C_Γ(r) constrains ξ_c = v/λ (1 combination, not independent of τ_B+v)
- NM curvature constrains τ_B (same as above)

There is no observable that independently constrains v without also
knowing λ, i.e., no observable is a function of v alone.
Therefore the prediction map has a null direction: v → αv with λ → λ
changes ξ_c but no other observable in the temporal sector.

**Rank deficiency:** The prediction map has rank < number of free parameters.
At least one free parameter (v, or equivalently ξ_c given τ_B) requires
spatial measurement to constrain, and that spatial measurement is confounded
by the K₀/power-law degeneracy on current hardware.

---

## PHASE E — CONVENTIONAL NULL EQUIVALENCE

Full analysis in CONVENTIONAL_EQUIVALENCE_AUDIT.md. Summary:

For every C2 prediction, a conventional stochastic model producing the
identical observable was identified:

| C2 Prediction | Conventional equivalent |
|---------------|------------------------|
| Lorentzian S_JJ(ω) | Any OU process with same τ_B and amplitude |
| K₀(r/ξ_c) spatial | Power-law r^{−α} + two-bath (M7, M9) — shape-degenerate |
| Γ_φ = k_rot·ω_rot² | Any bath with ⟨(δJ)²⟩ ∝ ω_rot² |
| Gaussian NM onset | Any finite-memory bath with same τ_B |
| P3 ratio c = ξ_c/(2τ_B) | No conventional mechanism produces this specific ratio **if** c ≪ v_sound |

The P3 relation is the only candidate that is NOT trivially reproduced
by conventional physics — but only if the measured c differs anomalously
from known propagation speeds. This is conditional, not guaranteed.

---

## PHASE F — SEARCH FOR A TRUE THEORY-LEVEL SIGNATURE

A theory-level signature must be: a relationship between observables
that is (i) derived from C2, (ii) not a free-parameter fit,
(iii) not reproduced by generic conventional mechanisms.

### F.1 Candidates Examined

**Fixed dimensionless ratios:** None found. All C2 dimensionless ratios
(ω·τ_B, r/ξ_c, NMP) involve free parameters.

**Universal exponents:** The K₀ spatial decay and Lorentzian temporal spectrum
are fixed functional forms — but with free scale parameters. Functional
form ≠ constrained exponent.

**Coupled observables:** The P3 relation ξ_c = 2cτ_B couples spatial and
temporal observables. This IS a theory-derived coupling — but c is free.

**Cross-sector relationships:**
C2 predicts that the SAME substrate produces both τ_B (temporal) and ξ_c
(spatial). Therefore: if both are measured, their ratio c = ξ_c/(2τ_B)
must be constant across experimental conditions (same substrate → same c).
This is the c(T) = const prediction (DISCRIMINATOR_SEARCH.md Candidate 9).

**Conservation-law signatures:** Only one: total information Q = ∫s dx.
Not directly observable in qubit experiments.

**Non-Gaussian statistics:** C2 substrate noise is Gaussian (linear coupling,
Gaussian PSD). No non-Gaussian signature is predicted by existing C2.

**Multi-point constraints:** C2 with Gaussian substrate predicts that all
n-point correlations factorise into products of two-point correlations.
This is identical to any Gaussian bath. Not distinctive.

### F.2 The One Surviving Candidate

The only structural prediction with any discriminating content is:

> **P3 consistency: c = ξ_c/(2τ_B) = const across conditions**

This is derived (ξ_c = v/λ = 2·(v/2)·(1/λ) = 2cτ_B, exact).
It is not a free-parameter fit — once c is measured from one set of
(ξ_c, τ_B), the ratio is fixed.
It would be discriminating IF the measured c ≪ v_sound, because no
conventional mechanism predicts such a ratio.

But it does NOT constitute a parameter-free prediction from the theory.
It requires measuring both ξ_c and τ_B first, then computing c, then
asking whether c is anomalous. The theory does not predict what c is.

---

## PHASE G — CLOSING THE THEORY WITHOUT AD HOC PATCHES

### G.1 What Would Close GAP-7 Legitimately

A legitimate closure of GAP-7 requires one of:

**Option G-A (Physical substrate identification):**
Identify the C2 substrate with a known physical medium (phonons, EM field,
topological mode, etc.). Then c = speed of that medium. This is an
EXTENSION of C2, not a derivation. It would require:
- Justification for why that specific medium is the substrate
- New predictions from the identification (e.g., specific c value,
  temperature dependence, material dependence)
- These new predictions must be tested independently

**Option G-B (New axiom constraining v):**
Add an axiom to C2 that relates v to other C2 quantities. The only
dimensionally consistent options involve ℏ (already a free import),
the qubit frequency ω_q (a qubit property, not a substrate property),
or a new mass scale m_eff (not in C2, as noted in C2_MISSING_PRINCIPLES.md).

If such an axiom is added, it must be documented as:

```
NEW AXIOM REQUIRED:
Statement: [the axiom]
Why C2 does not currently imply it: c is free in all 25 routes (GAP7_REDERIVATION.md)
New predictions created: specific value of ξ_c given other substrate parameters
Degrees of freedom removed: 1 (reduces free parameters from 5 to 4)
Empirical consequences: parameter-free ξ_c prediction, testable if NMP ≥ 0.1
```

### G.2 Is Any Axiom Already Implied?

C2_MISSING_PRINCIPLES.md documents that HC-1 and HC-2 (proposed principles
for deriving ℏ) both fail: HC-1 requires a new mass scale, HC-2 requires
the unproved CCA-C3 conjecture. The same applies to any proposed axiom
constraining v.

**No existing C2 axiom, theorem, or conjecture implies a specific value of v.**

The closest candidate is the FPUT derivation: if the substrate is identified
with the acoustic phonons of the chip material, then c = v_s ≈ 5000–8000 m/s.
But this is a NEW PHYSICAL IDENTIFICATION, not a mathematical derivation from
existing C2 axioms.

**2026-10-10 extension note:** `03_audits/SUBSTRATE_SELECTION_BRIDGE_AUDIT.md`
formalizes the narrowest non-ad hoc version of this route as GMS
(Gapless Minimal-Support Selection). GMS does not prove `c = v_s` from existing
C2/Giga axioms; it replaces the implicit `[PHON]` identification with an explicit
candidate selection principle:

```
Existing C2 + Giga:                 c is free
Existing C2 + elastic-carrier bound: 0 < c <= v_max
Existing C2 + Giga + GMS:           c remains branch/direction free
```

The adversarial elastic calculation in `03_audits/GMS_ADVERSARIAL_AUDIT.md`
shows distinct transverse and longitudinal gapless modes with different speeds.
It does not by itself establish GMS coarse-graining or PRW kinetic premises.
The theory status therefore remains T2; any closure requires an independently
derived coupling and kinetic mechanism, not merely a branch-selection rule.

**2026-10-10 coupling audit note:** `03_audits/C2_ELASTIC_COUPLING_AUDIT.md`
finds that existing `H_int = g J sigma_z` does not define a microscopic map from
the C2 current to silicon elastic modes. A conditional scalar-density completion
is longitudinal-dominated but has nonzero transverse coupling at generic cubic
directions. Thus the existing coupling does not supply the missing
branch-selection principle or a unique `c`.

---

## PHASE H — THEORY STATUS CLASSIFICATION

### H.1 Assessment Against Each State

**STATE T0 — THEORY CLOSED AND PARAMETER-PREDICTIVE:**
Requires: C2 fixes at least one quantitative observable relationship not
generically reproduced by conventional mechanisms.

**Assessment: NO.**
All quantitative observable relationships in C2 involve at least one free
parameter. No parameter-free prediction exists. The closest candidate (P3)
requires measuring c from data — it is a consistency check, not a prediction.

**STATE T1 — THEORY PARTIALLY CLOSED:**
Requires: C2 produces nontrivial constrained relationships, but with at
least one free parameter remaining; a concrete closure route exists.

**Assessment: PARTIALLY YES, but insufficient.**
C2 does produce nontrivial constrained relationships:
- The Lorentzian form of S_JJ(ω) is derived (not assumed)
- The K₀ form of C_Γ(r) is derived from the 2D telegrapher Green's function
- The P3 coupling ξ_c = 2cτ_B is derived
- The ω_rot² scaling of Γ_φ is derived (conditional on ≥ 10 assumptions)

But the essential observable scales (c, λ, g) are all free. A closure route
exists in principle (Option G-A or G-B above) but requires either a new
physical identification or a new axiom — neither is present in the theory.

**STATE T2 — THEORY STRUCTURALLY UNDERDETERMINED:**
Requires: C2 has genuine mathematical content and derived dynamics, but
essential observable scales/couplings remain free and cannot be determined
from existing axioms.

**Assessment: YES — this is the correct classification.**

C2 has genuine mathematical content:
- The PRW → telegrapher derivation is rigorous and exact [KR/T]
- The C_JJ(t) = S₀exp(−t/τ_B) derivation is correct [T]
- The K₀ spatial correlator derivation is correct (modulo analytic gap) [T]
- The ξ_c = 2cτ_B coupling is exact [T]
- The Q diagnostic is a proven engineering tool [T]
- The CCA has well-defined categorical structure [T]

But essential observable scales are free and cannot be determined:
- c (= v): free (GAP-7, all 25 routes failed)
- λ: free (sets τ_B)
- g: free (F10 in C2_FRONTIER_MAP.md, listed as open problem)
- s₀: free

**STATE T3 — THEORY EMPIRICALLY EQUIVALENT TO CONVENTIONAL MODELS:**
Requires: All presently derived observables reproducible by conventional
mechanisms with no unique discriminator.

**Assessment: PARTIALLY YES for current observables, but not complete.**
For the observables tested so far (temporal Ramsey, spatial correlation),
conventional mechanisms reproduce all C2 predictions. However, the P3
coupling (c = ξ_c/(2τ_B) = const across conditions) is not trivially
reproduced by independent conventional mechanisms with different ξ and τ.
T3 would be fully correct only if P3 were also shown to be reproducible
by conventional physics — which it would be if the measured c equals v_sound
(phonon bath). If c ≪ v_sound, T3 is incorrect.

**STATE T4 — THEORY INTERNALLY INCONSISTENT:**
**Assessment: NO.** C2 is internally consistent. The telegrapher equation
is self-consistent for all v > 0. The CCA axioms are consistent.
No internal contradiction was found.

### H.2 Final Classification

**STATE T2 — THEORY STRUCTURALLY UNDERDETERMINED**

C2 contains:
- A mathematically rigorous transport layer (PRW → telegrapher → correlators) [PROVED]
- A partially rigorous quantum coupling layer (conditional on ≥ 10 assumptions) [CONDITIONAL]
- A partially developed foundational layer (CCA/SCC, several conjectures open) [PARTIAL]

C2 does NOT contain:
- A derivation of the substrate speed c [CONFIRMED ABSENT — 25 routes]
- A derivation of the coupling constant g [OPEN PROBLEM F10]
- A derivation of the substrate density s₀ [FREE PARAMETER]
- A parameter-free observable prediction [ABSENT]

The theory is not inconsistent, not empirically equivalent to all conventional
models (P3 is conditionally discriminating), and not closed. It is
structurally underdetermined at the level of observable scales.

---

## Summary

| Phase | Finding |
|-------|---------|
| A: Primitive ontology | 18+ independent assumptions; c, λ, g, s₀ are all free |
| B: GAP-7 re-derivation | All 25 routes fail or blocked; c is structurally free |
| C: Reparameterization | v enters observables only through ξ_c; 2 observable free scales |
| D: Rank analysis | Prediction map has rank < parameter count; null direction in v |
| E: Conventional equivalence | All current observables matched by conventional mechanisms |
| F: Theory-level signature | Only P3 (conditional); no parameter-free prediction |
| G: Closure without patches | No existing implication; closure requires new axiom or identification |
| H: Status classification | **STATE T2 — STRUCTURALLY UNDERDETERMINED** |

*Audit completed: 2026-08-22. Not revisable without new theory source evidence.*

---

## Addendum: 2026-10-10 Microscopic Coupling Derivation

**Added:** 2026-10-10. Does not revise any prior finding.

`03_audits/MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md` records the results
of attempting to derive a microscopic map from `J_C2` to silicon elastic degrees
of freedom. Four candidate observables (M1–M4) were derived and their Christoffel
mode-coupling matrix elements were calculated explicitly.

**New findings:**

1. The obstruction to closure is **double**: (A) multi-branch coupling from silicon
   anisotropy (Zener ratio = 1.564), and (B) direction-dependent LA speed
   (range 8435–9355 m/s, factor 1.109). Branch selection alone is insufficient.

2. The **minimum closure postulate** is identified: the substrate must behave as an
   isotropic elastic medium at the relevant scale. In the isotropic limit
   (`C44 = (C11-C12)/2`), M1 gives `w_TA = 0` exactly at all directions and a
   unique direction-independent LA speed. This removes both obstructions simultaneously.

3. The kinetic reduction from Christoffel eigenmodes to PRW equations requires six
   steps. Steps 3–5 (coarse-graining, 1D projection, scattering mechanism) are
   each additional physics not present in C2.

4. The four candidates at generic `[1,2,3]` direction:
   - M1 (scalar dilatation): LA=0.993, TA=0.007
   - M2 (energy flux): LA=0.9998, TA=0.0002
   - M3 (momentum density): LA=0.998, TA=0.002
   - M4 (acoustic intensity): LA=0.928, TA=0.072

**GAP-7 status:** Still NOT CLOSED. Theory state remains **T2**.

**Advance:** The obstruction is now characterized at the level of specific equations
and material constants, not just a general underdetermination statement.

---

## Addendum: 2026-10-10 D2 First-Principles Audit

**Added:** 2026-10-10. Does not revise any prior finding. Theory state remains T2.

`03_audits/D2_CCA_PROBABILITY_FLUX_FIRST_PRINCIPLES_AUDIT.md` records the complete
first-principles evaluation of the D2 proposal from `GAP0_J_C2_OPERATIONAL_DEFINITION.md`.

**Key results:**

1. **D2 is NOT derivable from Ax1–Ax5.** Only J's T-parity is conditionally derivable
   from Ax3. All other steps (spatial positions, direction decomposition, continuum limit,
   c = a/dt) require new axioms directly contradicted by the proved theorems CCA-IMP-1
   and CCA-IMP-3.

2. **c = a/dt is tautological.** It is the definition of a PRW lattice step, present since
   Goldstein (1951). It does not fix c's numerical value (a and dt are both free).
   Not a new structural result.

3. **g ~ ℏ is a dimensional error.** [g] = J·m²·s; [ℏ] = J·s; g/ℏ has units m².
   The coupling g is NOT numerically constrained without the background information
   density n₀, which is a free parameter.

4. **Isotropy is postulate A-PRW1, not a theorem.** CCA Ax1–Ax5 have no spatial structure.
   Isotropic transport requires both an isotropic spatial embedding AND equal transition
   rates in all directions — neither of which follows from the axioms.

5. **Multi-branch C2 = multi-component Drude bath.** Maximum PSD difference = 0
   (algebraically proved, numerically confirmed). Complete observational equivalence
   for all two-point observables. P3 spread = 65% of mean — discriminator eliminated.

6. **Orientation experiment has four major confounders.** TLS bath dominates and is
   isotropic. Angular averaging reduces phonon anisotropy. ξ_c extraction requires
   assuming K₀ functional form. Required precision < 3.7%.

**What D2 does contribute:**
- T-parity of J (conditionally from Ax3) — the first property of J_C2 genuinely
  traceable to a CCA axiom
- The spatial embedding axiom SE1 as a clearly-stated necessary new axiom
- Gap 0b (CCA lattice spacing) as the correct residual question

**Validation:** 12 numerical tests in `04_validations/d2_comprehensive_validation.py`.
All results reproducible. Output in `04_validations/outputs/d2_comprehensive_validation.json`.

**GAP-0 status:** PARTIALLY OPEN (T-parity derived; spatial current requires SE1).
**GAP-7 status:** NOT CLOSED. Theory state remains **T2**.
