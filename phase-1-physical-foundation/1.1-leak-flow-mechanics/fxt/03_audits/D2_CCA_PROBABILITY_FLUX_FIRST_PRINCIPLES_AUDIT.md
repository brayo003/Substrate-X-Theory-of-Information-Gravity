# D2_CCA_PROBABILITY_FLUX_FIRST_PRINCIPLES_AUDIT.md
## Complete First-Principles Verification: D2 Definition of J_C2

**Date:** 2026-10-10
**Status:** COMPLETE — OUTCOME: PARTIAL ADVANCE WITH MULTIPLE ERRORS CORRECTED
**Validation scripts:**
  `04_validations/d2_first_principles_audit.py` (original 8 tests)
  `04_validations/d2_comprehensive_validation.py` (this session, 12 tests)
**Machine-readable outputs:**
  `04_validations/outputs/d2_first_principles_audit.json`
  `04_validations/outputs/d2_comprehensive_validation.json`
**Prior audit superseded (verdict only):** `03_audits/GAP0_J_C2_OPERATIONAL_DEFINITION.md`
**Prior audits preserved as history:**
  `MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md`
  `ISOTROPY_AND_MULTIBRANCH_AUDIT.md`
  `GMS_ADVERSARIAL_AUDIT.md`
  `C2_ELASTIC_COUPLING_AUDIT.md`
  `SUBSTRATE_SELECTION_BRIDGE_AUDIT.md`

**Label convention:**
- `[T]` Proved theorem (from existing source)
- `[DERIVED]` Follows logically from named premises
- `[COND]` Follows only after named additional assumptions
- `[NV]` Numerically verified for tested inputs
- `[OPEN]` Not yet established
- `[CONTRA]` Incompatible with verified equations or data
- `[OBS]` Proved obstruction / impossibility

---

## 1. Executive Summary

The D2 proposal (`GAP0_J_C2_OPERATIONAL_DEFINITION.md`, 2026-10-10) defines J_C2 as the
CCA probability flux and claims two new structural results: (1) c = a/dt, and (2) g ~ ℏ.
This audit evaluates every claim against the actual repository axioms and the executed
validation outputs.

**What survives scrutiny:**
- T-parity of J (J is T-odd) is conditionally derivable from Ax3. `[COND]`
- The Lorentzian PSD follows from the PRW dynamics. `[DERIVED]` (pre-existing result)
- Multi-branch C2 is algebraically identical to a multi-component Drude bath. `[NV]`
- The orientation experiment is a valid discriminator in principle under stated conditions. `[OPEN]`

**What does not survive scrutiny:**
1. D2 is NOT derivable from Ax1–Ax5. Three additional axioms are required.
   Directly contradicted by CCA-IMP-1 and CCA-IMP-3. `[CONTRA]`
2. c = a/dt is NOT a new structural result. It is the tautological definition of a
   discrete lattice step, present in Goldstein (1951). `[CONTRA]`
3. g ~ ℏ is a DIMENSIONAL ERROR. [g] = J·m²·s; [ℏ] = J·s; g/ℏ has units m². `[CONTRA]`
4. J is NOT uniquely determined by continuity in >1D. Solenoidal ambiguity. `[NV]`
5. Isotropy is NOT derivable from CCA. It is postulate A-PRW1. `[CONTRA]`
6. Multi-branch C2 does NOT restore the P3 discriminator. P3 spread = 65% of mean. `[NV]`
7. The orientation experiment has four major confounders not addressed in the D2 proposal. `[OPEN]`

**Gap statuses after this audit:**
- Gap 0 (operational definition of J_C2): **PARTIALLY OPEN**
  T-parity is conditionally derivable; spatial current requires new axioms.
- Gap 7 (unique propagation speed c): **NOT CLOSED**
  D2 adds no new constraint on c beyond the tautological c = a/dt.
- g (coupling constant): **NOT NUMERICALLY CONSTRAINED**
  The claim g ~ ℏ is a dimensional error; g remains a free parameter.

---

## 2. Repository Sources Inspected

| Document | Location | Content relevant to this audit |
|----------|----------|-------------------------------|
| C2_FOUNDATIONS.md | 01_foundations/ | CCA axioms Ax1–Ax5; CCA-IMP-1, CCA-IMP-3; PRW model; FPUT projection |
| THEORY_CLOSURE_AUDIT.md | fxt/ | 18+ independent assumptions enumerated; GAP-7 confirmed |
| MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md | 03_audits/ | Double obstruction A&B; isotropic limit; 4 elastic candidates tested |
| GAP0_J_C2_OPERATIONAL_DEFINITION.md | 03_audits/ | D2 proposal being evaluated here |
| ISOTROPY_AND_MULTIBRANCH_AUDIT.md | 03_audits/ | Multi-branch = Drude; isotropy not from CCA |
| GMS_ADVERSARIAL_AUDIT.md | 03_audits/ | Elastic speed non-uniqueness in cubic silicon |
| C2_ELASTIC_COUPLING_AUDIT.md | 03_audits/ | Earlier elastic coupling attempt |
| SUBSTRATE_SELECTION_BRIDGE_AUDIT.md | 03_audits/ | Silicon as experimental platform vs substrate |
| GAP7_REDERIVATION.md | fxt/ | 25 routes tested; all failed; structural proof of GAP-7 |
| interaction_hamiltonian_derivation.md | 02_derivations/ | H_int = g·J·σ_z; σ_z selection derivation |
| d2_first_principles_audit.py | 04_validations/ | 8-test validation; run and output read |
| d2_first_principles_audit.json | 04_validations/outputs/ | Results read in full |
| d2_comprehensive_validation.py | 04_validations/ | 12-test validation; created and run this session |
| d2_comprehensive_validation.json | 04_validations/outputs/ | Results produced this session |

---

## 3. Exact Definitions and Axiom Inventory

### 3.1 CCA Axioms (Ax1–Ax5)

Source: C2_FOUNDATIONS.md Subsystem 4.

| Axiom | Statement | Has spatial content? |
|-------|-----------|---------------------|
| Ax1 | Finite set O of objects; morphism set M; symmetric monoidal structure | No |
| Ax2 | Causal partial order ≤ on M (locally finite) | No |
| Ax3 | Dagger involution †: M→M reversing causal order | No |
| Ax4 | Probability weight ε: M→[0,1]; sums to 1 per hom-set | No |
| Ax5 | Composition / probability-simplex structure | No |

None of Ax1–Ax5 contains positions, distances, directions, or speeds. This absence is proved formally:

**[T] CCA-IMP-1** (C2_FOUNDATIONS.md §6): "Ax1–Ax5 generate only a finite discrete structure. A continuous Lorentzian manifold cannot emerge without a limiting procedure."

**[T] CCA-IMP-3** (C2_FOUNDATIONS.md §6): "Finite propagation speed as a physical ratio requires a metric. CCA provides only a counting measure (rank). Numerical value of c is not derivable from Ax1–Ax5."

### 3.2 D2 Definition (from GAP0_J_C2_OPERATIONAL_DEFINITION.md §4)

Given CCA objects at positions {xᵢ} ⊂ ℝ^d with spacing a, and morphisms m: xᵢ→xⱼ with
weights ε(m), the CCA probability flux in direction α is:

```
J_α(x, t) = (1/a^d) Σ_{|xᵢ-x|<a/2} Σ_{j: xⱼ-xᵢ=a ê_α} [ε(m_{ij})(t) - ε(m_{ji})(t)] · (a/dt)
```

In continuum limit (a→0, dt→0 at fixed c = a/dt):

```
J_α(x, t) = c · [n⁺_α(x,t) - n⁻_α(x,t)]
```

### 3.3 Additional Axioms Required by D2 (Not in Ax1–Ax5)

| Axiom | Content | Type |
|-------|---------|------|
| SE1 — Spatial embedding | Map φ: O→ℝ^d assigning positions to CCA objects | **NEW AXIOM** |
| SE2 — Lattice spacing | a = min_{m∈M} \|φ(src(m))−φ(tgt(m))\| | **NEW ASSUMPTION** |
| SE3 — Time step | dt per morphism application | **NEW ASSUMPTION** |
| SE4 — Continuum limit | a→0, dt→0 at fixed c = a/dt | **NEW ASSUMPTION** |
| A-PRW1 (isotropy) | Equal speeds and rates in all directions | **EXISTING POSTULATE** (not derived) |

SE1 is the "additional limiting procedure" whose absence CCA-IMP-1 proves. These are not
minor clarifications — they add metric structure that is provably absent from Ax1–Ax5.

---

## 4. Derivation of D2 — Step-by-Step Classification

| Step | Claim | Classification | Basis |
|------|-------|---------------|-------|
| Ax4 provides probability weights ε(m) | ε(m) ∈ [0,1] | `[DERIVED]` | Ax4 definition |
| Ax2 provides causal direction | Directed transitions | `[DERIVED]` | Ax2 (conceptual precursor only; no spatial field) |
| Ax3 provides T-parity of J | J† = −J (T-odd) | `[COND]` | Ax3 + D2 interpretation of J |
| Define n⁺_α, n⁻_α as CCA morphism densities in ±α directions | Requires α-direction to exist | **NEEDS SE1** | CCA-IMP-1 |
| Continuum field J(x,t) | Spatial current density | **NEEDS SE1, SE4** | CCA-IMP-1 |
| c = a/dt | Speed equals lattice ratio | **TAUTOLOGICAL** — not new | Goldstein 1951 |
| D2 reduces to PRW in 1D | Exact identity | `[DERIVED]` | Trivially: D2 = PRW by construction |

**Overall derivation verdict: D2 is NOT derivable from Ax1–Ax5.**
Only J's T-parity is conditionally derivable (from Ax3, given the D2 interpretation).
All other steps require new axioms SE1–SE4.

---

## 5. Continuity and Current Uniqueness

### 5.1 The Continuity Equation

```
∂s/∂t + ∇·J_C2 = 0
```

is `[DERIVED]` from PRW balance equations (Goldstein-Kac, 1951). Source: C2_FOUNDATIONS.md
Subsystem 1; substrate_transport_derivation.md.

In 1D:
- s = n⁺ + n⁻ (information density)
- J_C2 = c(n⁺ − n⁻) (net directional flux)
- Adding balance equations gives ∂s/∂t + ∂J/∂x = 0 exactly.

Units are dimensionally consistent: [s] = info·m⁻³, [J] = info·m⁻²·s⁻¹, and both
sides of continuity have units info·m⁻³·s⁻¹. `[NV]` (T1, continuity_residuals test)

Charge conservation Q = ∫s dV verified to numerical precision (Q_error < 10⁻¹⁵). `[NV]`

### 5.2 Continuity Does NOT Uniquely Fix J in >1D

**Proof:** If J satisfies ∂s/∂t + ∇·J = 0, then J' = J + K with ∇·K = 0 also satisfies
∂s/∂t + ∇·J' = ∂s/∂t + ∇·J + ∇·K = 0 + 0 = 0. ✓

The solenoidal ambiguity is confirmed numerically: for explicit K = curl(φ),
max|∇·J − ∇·J'| < 6×10⁻¹⁴. `[NV]` (T2)

**What the GAP0 audit claims incorrectly:** "J is the Noether current of Q = ∫s dV."
Continuity implies Q is conserved, but it does not uniquely identify J among the
infinitely many currents that conserve Q.

**What does fix J (in >1D):** Specifying the PRW propagation directions {ê_b, c_b}. But
these are model inputs, not derived from Ax1–Ax5. `[OPEN]`

**The H_int constraint:** H_int = g·J·σ_z requires J to be a scalar at the qubit location.
In >1D this means B = n̂·J for some projection direction n̂. The direction n̂ is not fixed
by any existing equation. It is a new free parameter. `[OPEN]`

### 5.3 Is J_C2 a Noether Current?

Not in the sense that term usually implies. A Noether current requires:
(a) An action functional S[s, J]
(b) A continuous global symmetry of that action
(c) Application of Noether's first theorem

None of (a)–(c) exists in the C2/PRW framework. The PRW balance equations are not derived
from an action principle. The current J is defined kinematically, not Noether-theoretically.
The term "Noether current" should not be applied to J_C2.

---

## 6. Spatial Embedding Axiom

To construct J(x,t) from CCA morphisms, the theory requires SE1 (spatial embedding):

**SE1:** There exists a map φ: O→ℝ^d assigning positions to CCA objects, with a minimum
spacing a = min\|φ(src(m))−φ(tgt(m))\|, a morphism duration dt, and a continuum limit
a→0, dt→0 at fixed c = a/dt.

**What SE1 adds:**
- Metric structure (absent from Ax1–Ax5 by CCA-IMP-1)
- Lattice spacing a (free parameter)
- Time step dt (free parameter)
- c = a/dt (determined by ratio of two free parameters — still free overall)
- Direction structure enabling the definition of n⁺_α, n⁻_α

**What SE1 does NOT add:**
- The numerical value of c (a and dt are both free)
- Isotropy (must be separately assumed via A-PRW1)
- Coupling to a physical phonon medium
- The projection direction n̂ for H_int in >1D

**Classification of SE1:** MAJOR NEW AXIOM. Not contradicted by existing axioms. Necessary
but not sufficient for a complete spatial current definition.

---

## 7. Speed Derivation: c = a/dt

### 7.1 The Claim (GAP0 §5)

"This is the first identification of what c is. Previous documents treated c as a
completely free parameter with no structural meaning."

### 7.2 Why This Is Incorrect

c = a/dt is the **definition** of the PRW step velocity. It appears in:
- Goldstein (1951, Proc. Cambridge Phil. Soc.) — original PRW paper, explicitly uses v = a/dt
- Kac (1974, Rocky Mountain J. Math.) — formal treatment
- C2_FOUNDATIONS.md Subsystem 1 — "step size h [m], time step Δt [s], particle speed v = h/Δt"

The relation c = a/dt is a tautology once the discrete step is defined. Calling it "the
first identification of what c is" is incorrect. `[CONTRA]`

### 7.3 What c = a/dt Does and Does Not Establish

| Claim | Status |
|-------|--------|
| c = a/dt holds for 1D PRW | `[DERIVED]` — by definition |
| c = a/dt gives a unique c | FAILS — a and dt are both free; only ratio is specified |
| c = a/dt in multidimensional lattice | Multiple c_b values if a_b varies by direction; `[NV]` (T4) |
| c = a/dt from CCA axioms | `[CONTRA]` — CCA-IMP-3 proves c is not derivable from Ax1–Ax5 |
| c = a/dt is a new result | `[CONTRA]` — known since Goldstein 1951 |
| c is now "not arbitrary" | INCORRECT — a and dt remain arbitrary; c = a/dt is merely a name |

### 7.4 What Genuinely Fixing c Would Require

To fix c's numerical value, the theory would need an independent specification of at least
one of {a, dt}. Candidates:
- Planck length → c = speed of light (incompatible with acoustic c ~ 5000 m/s)
- Phonon wavelength scale → requires identifying CCA with physical phonons (unproved, `[OPEN]`)
- Qubit geometry (r_q ~ 100 nm) → circular (would just set a = r_q, but then dt is free)

None of these is currently justified. GAP-7 remains open. `[OPEN]`

---

## 8. Coupling Scale g

### 8.1 The Claim (GAP0 §5)

"The dimensional analysis forces g to involve ℏ explicitly... g is of order ℏ times a
frequency-related factor. This is the first time the theory's equations require g to
involve ℏ."

### 8.2 Dimensional Analysis — The Error

Starting from H_int = g·J·σ_z:

```
[H_int] = J              (joules)
[J_C2]  = m⁻²·s⁻¹       (when [info] = dimensionless)
[g]     = J / (m⁻²·s⁻¹) = J·m²·s
```

Now compare with ℏ:

```
[ℏ] = J·s
[g/ℏ] = (J·m²·s) / (J·s) = m²
```

g/ℏ has units m², **not dimensionless**. The comparison "g ~ ℏ" is a dimensional error. `[CONTRA]`

This error is confirmed by the validation script: test T6 returns status FAIL with the
explicit message: "DIMENSIONALLY INCORRECT: g/hbar = 4.11e+06 m^2 -- NOT dimensionless".

### 8.3 The Correct Statement About g and ℏ

The dephasing formula from Born-Markov (H_int = g·J·σ_z, secular approximation):

```
Γ_φ = (g²/ℏ²) · 2S₀τ_B
```

where S₀ is the spectral amplitude of J fluctuations, and τ_B = 1/(2λ). `[DERIVED]`

This formula does contain ℏ² in the denominator — but this is a trivial consequence of
Fermi's golden rule applied to any coupling Hamiltonian, not a new result specific to D2.

Solving for g:

```
g = ℏ · sqrt(Γ_φ / (4·n₀·c²·τ_B²))
```

where n₀ is the background information density (a free parameter). This equation requires
knowing n₀ to produce a numerical estimate of g.

**g is NOT numerically constrained.** The claim "g is of order ℏ" requires the right-hand
side to be dimensionless, which it is not. `[CONTRA]`

### 8.4 Corrected Statement

The correct statement is: g has units [J·m²·s], it appears in any dephasing formula
through the combination g²/ℏ², and its numerical value cannot be estimated without
specifying n₀ (the background information density), which is a free parameter.

---

## 9. Isotropy Conditions

### 9.1 Where Isotropy Enters C2

Isotropy enters via postulate A-PRW1 (C2_FOUNDATIONS.md, Subsystem 1):

> "Walker speed v and flip rate λ are constant (spatially and temporally uniform)."

This is a postulate about the abstract PRW process. It is not derived from Ax1–Ax5 or from
any other existing C2 structure. `[CONTRA]` (the claim that CCA implies isotropy)

### 9.2 Rigorous Conditions for Isotropic Transport

The transport tensor for a PRW with B branches is:

```
D_ij = Σ_b w_b · c_b² · τ_b · ê_{b,i} · ê_{b,j}
```

D_ij ∝ δ_ij (isotropic) if and only if both:
1. All speeds c_b are equal across all propagation directions
2. All reversal times τ_b are equal across all propagation directions
AND
3. The directions {ê_b} form an isotropic distribution in ℝ^d

`[NV]` (T5):
- Cubic lattice, equal c and τ: **isotropic**
- FCC lattice, equal c and τ: **isotropic**
- Anisotropic τ (z-direction different): **NOT isotropic**
- Anisotropic c (z-direction different): **NOT isotropic**

### 9.3 Five Isotropy Levels — None Auto-Derived

| Level | Content | Status |
|-------|---------|--------|
| 1. Abstract CCA | All causal morphisms equal probability in all directions | POSTULATED (not Ax1–Ax5) |
| 2. Spatial embedding | Lattice spacing same in all directions | ADDITIONAL ASSUMPTION |
| 3. Continuum transport | D_ij ∝ δ_ij | `[COND]` — follows if levels 1+2 hold |
| 4. Physical material | Silicon acoustic speeds isotropic | FALSE (Zener ratio = 1.56) |
| 5. Observables | Measured c_eff orientation-independent | `[OPEN]` |

No level is automatically derived. Each requires an independent assumption.

---

## 10. Experimental Discriminator Assessment

### 10.1 Setup

Proposed experiment: measure c_eff = ξ_c/(2τ_B) on silicon qubits with [100], [110], [111]
surface orientations. Predicted LA speed range verified: `[NV]` (T7)

```
v_LA([100] in-plane):  8433 m/s
v_LA([110] in-plane):  9134–9356 m/s
v_LA([111] in-plane):  9134 m/s (isotropic in-plane for [111])
Full directional range: 8435–9355 m/s (ratio 1.109)
```

The cited range 8435–9355 m/s from GAP0 is confirmed. `[NV]`

### 10.2 Predictions Under Each Hypothesis

**Hypothesis A — D2, isotropic CCA (A-PRW1):**
- c_eff = c (constant, free) for all orientations
- Orientation dependence: NONE (postulated, not derived)
- Free parameters: {c, λ, g, n₀}

**Hypothesis B — Conventional silicon phonon bath (LA-mode coupling):**
- c_eff = v_LA(n̂) varies by ~11% across orientations
- Requires directionally resolved qubit-phonon coupling

**Hypothesis C — TLS bath (amorphous oxide):**
- c_eff: isotropic (amorphous → no crystal orientation effect)
- Indistinguishable from Hypothesis A on orientation measurements alone

### 10.3 Four Confounders

1. **Angular averaging:** Transmon qubits couple approximately isotropically to phonons.
   Angular average of v_LA over all directions produces a single effective speed
   independent of wafer orientation. `[NV]` (T12: conventional phonon bath reproduces
   orientation-independent c_eff through angular averaging)

2. **TLS bath dominance:** TLS bath is the dominant decoherence source in state-of-the-art
   superconducting qubits. TLS bath is intrinsically isotropic. A measured
   orientation-independent c_eff cannot distinguish D2 from TLS bath.

3. **ξ_c extraction requires functional form assumption:** Extracting ξ_c from spatial
   correlator data requires fitting C_Γ(r) = K₀(r/ξ_c), which is a theory prediction.
   Power-law and exponential alternatives can fit the same data. ξ_c is not
   model-independently measurable. `[OPEN]`

4. **Precision requirement:** The 11% LA speed variation requires ξ_c measured to
   <3.7% precision for 3σ significance. This demands multi-qubit arrays with
   controlled qubit separations — not standard single-qubit experiments.

### 10.4 Minimum Improved Protocol

For the experiment to discriminate D2 from all conventional physics:

1. Rule out TLS bath via spin-echo spectroscopy (confirm TLS < 10% of T₂)
2. Use verified single-crystal wafers in [100], [110], [111] orientations
3. Measure ξ_c without assuming K₀ form (model-independent spatial estimators)
4. Verify K₀ vs power-law functional shape at multiple separations
5. Achieve ξ_c precision < 3.7% per orientation
6. Cross-correlate between chips with same T₂ physics but different orientations

**Current feasibility:** LOW. Steps 1, 3, 4 require hardware and analysis not currently
available in this project. `[OPEN]`

---

## 11. Multi-Branch Spectral Density

### 11.1 Algebraic Equivalence

Multi-branch C2 PSD:

```
S_C2(ω) = Σ_b w_b · 2S₀τ_b / (1 + ω²τ_b²)
```

Multi-component Drude bath PSD (conventional phonon bath model):

```
S_Drude(ω) = Σ_b 2η_b τ_b / (1 + ω²τ_b²)    with η_b = S₀ w_b
```

These are algebraically identical. Maximum numerical difference: 0. `[NV]` (T8)

### 11.2 Complete Observational Equivalence

The PRW is a **linear** stochastic process. Linear stochastic processes are Gaussian (by the
central limit theorem for linear dynamical systems). Gaussian processes are fully
characterized by their two-point correlation function. Since the two-point functions of
multi-branch C2 and multi-component Drude bath are algebraically identical, all n-point
functions factorize identically by Wick's theorem.

**Complete observational equivalence for all accessible observables:**
- Dephasing rate Γ_φ: identical ✓
- Ramsey decay shape: identical ✓
- Spatial correlator C_Γ(r): shape differs by <0.15% for equal τ_b — experimentally unresolvable ✓
- Multi-qubit observables: all two-point functions identical ✓ `[NV]`

### 11.3 Multi-Branch Eliminates the P3 Discriminator

The P3 ratio c_eff = ξ_c/(2τ_B) is the only C2 observable that could discriminate the
theory from conventional physics. Under multi-branch coupling:

```
Branch speeds (at [123] direction):
  TA1: 4893 m/s (w=0.5%)
  TA2: 5626 m/s (w=0.2%)
  LA:  9157 m/s (w=99.3%)

P3_spread / P3_mean = (9157-4893)/7225 = 65%
```

A 65% spread in P3 across branches eliminates any unique P3 prediction. `[NV]` (T8)

---

## 12. Validation Test Summary

All results reproducible. Command:

```bash
cd .../fxt
python 04_validations/d2_first_principles_audit.py
python 04_validations/d2_comprehensive_validation.py
```

**Original audit (d2_first_principles_audit.py), Oct 10 2026:**

| Test | Result | Finding |
|------|--------|---------|
| continuity_and_conservation | PASS | Residual O(dx,dt) numerical; Q conserved exactly |
| solenoidal_ambiguity | PASS | J' = J+K satisfies continuity; J NOT unique in >1D |
| d2_vs_cca_axioms | FAIL | D2 not derivable from Ax1–Ax5; CCA-IMP-1,3 contradicted |
| c_equals_a_over_dt | PARTIAL | Tautological; not new; does not fix c value |
| coupling_constant_g | FAIL | g ~ ℏ is dimensional error; g/ℏ = m² not dimensionless |
| isotropy_transport_tensor | PASS | Isotropy requires equal rates; not from CCA |
| experimental_discriminator | PARTIAL | Valid in principle; 4 major confounders |
| multibranch_spectral_density | PASS | C2 = Drude algebraically; P3 spread 65% |

**Comprehensive validation (d2_comprehensive_validation.py), this session:**

| Test | Status | What it tests |
|------|--------|--------------|
| T1 continuity | PASS | Discrete model residuals; Q conservation |
| T2 solenoidal | PASS | div(K)=0 freedom in 2D |
| T3 PRW 1D limit | PASS | D2 = PRW in 1D (tautological) |
| T4 c=a/dt | PARTIAL | Tautological in 1D; multiple values in anisotropic 3D |
| T5 isotropy | PASS | Lattice geometry isotropy conditions; 4 geometries tested |
| T6 units/g | FAIL | [g]=[J m² s] ≠ [ℏ]=[J s]; dimensional error confirmed |
| T7 discriminator | PARTIAL | LA speed range 8435–9355 verified; 4 confounders enumerated |
| T8 multibranch | PASS | PSD difference = 0; P3 spread = 65% |
| T9 T-parity | PASS | J is T-odd from Ax3 (conditional on D2 interpretation) |
| T10 CCA-IMP | PASS | CCA-IMP-1 and CCA-IMP-3 internally consistent |
| T11 protocol | PASS | Minimum discrimination protocol: 6 steps; precision = 3.7% |
| T12 adversarial | PASS | Conventional phonon bath reproduces orientation-independent c_eff |

---

## 13. Remaining Gaps and Dependencies

### Gap 0 — Operational definition of J_C2

**Status: PARTIALLY OPEN**

| Sub-question | Status |
|-------------|--------|
| Is J T-odd? | `[COND]` from Ax3 + D2 interpretation |
| Is J unique in 1D? | `[DERIVED]` — yes (trivially, by PRW definition) |
| Is J unique in >1D? | `[OPEN]` — requires specifying propagation directions {ê_b} |
| What is the projection direction in H_int (>1D)? | `[OPEN]` — free parameter |
| Does spatial embedding axiom SE1 close Gap 0? | `[OPEN]` — SE1 is necessary but not sufficient |

Minimum additional work to partially close Gap 0:
- Formalize SE1 as an explicit CCA axiom with categorical statement
- Specify the projection direction for H_int in d=2 (the experimental case)
- Derive whether the spatial current reduces to a unique scalar observable at qubit scale

### Gap 7 — Unique propagation speed c

**Status: NOT CLOSED**

25 routes tested in GAP7_REDERIVATION.md (Aug 2026): all failed.
D2 adds c = a/dt (tautological) — no new constraint on c's numerical value.
The double obstruction in silicon remains:
- Obstruction A: Branch coupling non-unique at generic crystal directions
- Obstruction B: LA speed varies by 11% across orientations (8435–9355 m/s)

Minimum closure postulate (from MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md §7):
"The substrate must behave as an isotropic elastic medium at the spatial scale relevant
to the qubit." This postulate is identified but not derivable.

### g — Coupling constant

**Status: NOT NUMERICALLY CONSTRAINED**

The claim g ~ ℏ is a dimensional error. Correct unit: g has units [J·m²·s]. Numerical
estimation requires n₀ (background information density), which is a free parameter. No
existing equation constrains n₀.

---

## 14. Revised Closure Classification

| Claim | Classification | Evidence |
|-------|---------------|---------|
| J satisfies continuity | `[DERIVED]` | PRW balance equations (Goldstein-Kac) |
| J is T-odd | `[COND]` | Ax3 + D2 interpretation (T9) |
| Lorentzian PSD S_JJ(ω) | `[DERIVED]` | C-J equation dynamics (pre-existing) |
| D2 derivable from Ax1–Ax5 | `[CONTRA]` | CCA-IMP-1, CCA-IMP-3 (T10) |
| c = a/dt is a new result | `[CONTRA]` | Goldstein 1951; tautological (T4) |
| g ~ ℏ | `[CONTRA]` | Dimensional error; [g/ℏ] = m² (T6) |
| Isotropy from CCA axioms | `[CONTRA]` | CCA has no spatial structure (T5, T10) |
| J unique from continuity in >1D | `[CONTRA]` | Solenoidal ambiguity (T2) |
| Multi-branch C2 = Drude | `[NV]` | Max PSD difference = 0 (T8) |
| Orientation experiment discriminates now | `[CONTRA]` | 4 confounders; TLS bath is isotropic (T7, T12) |
| Orientation experiment discriminates in principle | `[OPEN]` | Under 6-step protocol (T11) |
| P3 discriminator (single-branch, isotropic) | `[COND]` | Requires A-PRW1 + single-branch coupling |
| P3 discriminator (multi-branch) | `[CONTRA]` | P3 spread 65% (T8) |
| Gap 0 closed | `[CONTRA]` | J has T-parity from Ax3; spatial current requires SE1 |
| Gap 7 closed | `[CONTRA]` | c still free; c = a/dt is tautological |
| g numerically constrained | `[OPEN]` | Requires n₀ (free parameter) |

---

## 15. Adversarial Review

**Strongest positive conclusion:** J's T-parity is conditionally derivable from Ax3.

Challenge: The derivation is conditional on accepting D2 as a definition of J, but D2 itself
requires SE1 (spatial embedding), which is not in Ax1–Ax5. Therefore even the T-parity
result is not purely axiomatic — it requires the D2 interpretation to be adopted, which
already presupposes SE1.

Response: This challenge is valid and partially reduces the strength of the claim. The correct
statement is: "If D2 is adopted as the definition of J (requiring SE1 as a new axiom), then
J's T-parity follows from Ax3." This is a conditional derivation, not an axiomatic theorem.

**Strongest negative conclusion:** c is not derivable from any existing axiom (GAP-7).

Challenge: Perhaps c emerges from a renormalization group fixed point of the CCA algebra, or
from a categorical uniqueness theorem not yet explored.

Response: This is a legitimate open research direction. But CCA-IMP-3 (proved theorem) shows
that extracting a dimensional speed from a purely algebraic structure requires adding a metric.
Any such derivation would constitute SE1 (spatial embedding axiom) by another name. GAP-7
remains open unless a new approach genuinely circumvents CCA-IMP-3 — which would require
disproving an existing proved theorem.

**Potential circularity:** c = a/dt. The D2 proposal claims this is "the first identification
of what c is." In fact, D2 was constructed to match the PRW, and the PRW defines c = a/dt
from the start. The proposed "identification" is circular.

**Value selection check:** The silicon LA speed range 8435–9355 m/s was cited in GAP0.
This audit independently computed it from actual elastic constants (C11=165.7 GPa,
C12=63.9 GPa, C44=79.6 GPa, ρ=2330 kg/m³) over 2000 random directions. Result:
8433–9356 m/s — consistent with the citation. No evidence of cherry-picking. `[NV]`

**What would falsify D2:**
1. A measurement of orientation-dependent c_eff after ruling out TLS bath and angular averaging
2. A proof that no spatial embedding axiom is consistent with the categorical structure of CCA
3. A demonstration that the dimensionless information unit [info] is actually dimensional,
   making the H_int formula unit-inconsistent

---

## 16. Corrections to GAP0_J_C2_OPERATIONAL_DEFINITION.md

The following specific statements in the D2 proposal should be corrected:

| Location | Incorrect statement | Correct statement |
|----------|--------------------|--------------------|
| §4, Derivation status | "D2 is partially derivable from Ax2, Ax3, Ax4" | Only T-parity (from Ax3) is conditionally derivable. Ax2 and Ax4 provide conceptual motivation, not mathematical derivation. |
| §5, Result 1 | "This is the first identification of what c is" | c = a/dt is the defining relation of a discrete PRW step, present since Goldstein (1951). Not a new result. |
| §5, Result 2 | "g is of order ℏ times a frequency-related factor" | Dimensional error. [g] = J·m²·s; [ℏ] = J·s; g/ℏ has units m². The claim g ~ ℏ is dimensionally inconsistent. |
| §5, Result 2 | "This is the first time the theory's equations require g to involve ℏ" | Any coupling Hamiltonian H_int produces ℏ in the dephasing formula via Fermi's golden rule. This is not specific to D2. |
| §2, "J is the Noether current" | Implies Noether's theorem applies | No action functional or Noether symmetry exists in the PRW framework. J is defined kinematically. |

---

## 17. Exact Reproduction Commands

```bash
# Repository root
cd /home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity

# Navigate to the audit directory
cd phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt

# Run original 8-test audit (previously run; results stable)
python 04_validations/d2_first_principles_audit.py
# Output: 04_validations/outputs/d2_first_principles_audit.json

# Run comprehensive 12-test audit (this session)
python 04_validations/d2_comprehensive_validation.py
# Output: 04_validations/outputs/d2_comprehensive_validation.json

# Dependencies: numpy, json, math (all standard)
# Python 3.8+ required
```

---

*This audit is a historical record. The D2 proposal document
(GAP0_J_C2_OPERATIONAL_DEFINITION.md) is preserved unchanged. The verdict of that
document is superseded by this audit on the specific points noted in Section 16.*

*The result is not that the D2 direction is wrong — identifying J as a CCA probability
flux is the most natural structural choice available. The result is that four specific
positive claims in the D2 proposal are incorrect, and the admitted gaps (Gap 0, Gap 7)
remain open with precisely characterized obstructions.*
