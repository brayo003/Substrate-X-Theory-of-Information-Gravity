# Gap 0: Operational Definition of J_C2

**Date:** 2026-10-10
**Status:** PARTIAL ADVANCE — definition partially derivable from CCA; three free parameters remain
**Executable:** `04_validations/j_c2_definition_attempt.py`
**Output:** `04_validations/outputs/j_c2_definition_attempt.json`
**Prior audits:** `MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md`, `ISOTROPY_AND_MULTIBRANCH_AUDIT.md`

---

> **⚠ CORRECTION NOTICE — 2026-10-10**
> This document has been independently audited. Four specific claims in §1 (Executive
> Verdict) and §5 (Structural Results) are **incorrect**. The document is preserved as
> a historical record but its positive claims are superseded by:
>
> **`03_audits/D2_CCA_PROBABILITY_FLUX_FIRST_PRINCIPLES_AUDIT.md`**
>
> Specific corrections:
> 1. **"D2 is partially derivable from Ax2, Ax3, Ax4"** — INCORRECT. Only T-parity
>    (from Ax3) is conditionally derivable. Ax2 and Ax4 provide conceptual motivation only.
> 2. **"c = a/dt is the first identification of what c is"** — INCORRECT. This is the
>    tautological definition of a PRW lattice step, present since Goldstein (1951).
>    It does not fix c's numerical value.
> 3. **"g ~ ℏ"** — DIMENSIONAL ERROR. [g] = J·m²·s; [ℏ] = J·s. g/ℏ has units m²,
>    not dimensionless. This claim should not be relied upon.
> 4. **"Isotropy is a property of the CCA causal structure"** — INCORRECT. Isotropy
>    enters via postulate A-PRW1, not from Ax1–Ax5.
>
> What survives: T-parity of J from Ax3 (conditional); the spatial embedding axiom
> SE1 as a necessary new axiom; the framing of Gap 0b (CCA lattice spacing) as the
> right next question.

---

---

## 1. Executive Verdict

The theory's existing axioms force several properties on J_C2 but do not define
it as a physical observable. Starting strictly from the CCA axioms (Ax1–Ax5) and
the PRW layer, this audit derives the strongest definition that the theory can
support without importing external physics.

The result is candidate **D2: J_C2 as the CCA probability flux.** It is partially
derivable from Ax2 (causal order), Ax3 (time reversal), and Ax4 (probability
weights), given one additional axiom: spatial embedding of CCA objects.

Two structural results follow from D2 that are not in any existing document:

1. **c = a/dt**: the PRW propagation speed equals the CCA lattice spacing divided
   by the CCA time step. This is the first identification of what c *is* — not a
   value, but a quantity.

2. **g ~ ℏ**: dimensional analysis of the dephasing rate constrains the coupling
   energy g to be of order ℏ. This is the first non-trivial constraint on g's scale.

Three parameters remain free after D2: the lattice spacing a, the morphism density
n₀, and the projection direction α. These cannot be fixed without additional physics
input that is not present in the existing theory.

---

## 2. What the Existing Theory Forces on J_C2

The following properties of J_C2 are derived from existing equations, without any
new assumption:

| Property | Source | Status |
|----------|--------|--------|
| J is the Noether current of Q = ∫s dV | Continuity eq [C-s] | **DERIVED** |
| Units: [info/(m²s)] in 3D, [info/(ms)] in 1D | Dimensional analysis from continuity | **DERIVED** |
| J is a vector in d dimensions (d=2 in chip plane) | From continuity in d>1 | **DERIVED** |
| J is odd under T-reversal: J(-t) = -J(t) | PRW balance eqs + Ax3 (dagger) | **DERIVED** |
| PSD is Lorentzian: S_JJ(ω) = 2S₀τ/(1+ω²τ²) | From C-J equation dynamics | **DERIVED** |
| J(x_q,t) enters H_int as a scalar | H_int = g J σ_z requires scalar bath operator | **FORCED BY H_int STRUCTURE** |

The following are **not** forced by any existing equation:

- What physical medium's fluctuations produce J
- The projection direction needed to form a scalar in >1D
- The conversion between [info] and physical units
- The value or scale of g
- The value of c

---

## 3. What the CCA Axioms Provide

Each CCA axiom was checked for content relevant to J_C2:

| Axiom | Content | Contribution to J_C2 |
|-------|---------|----------------------|
| Ax1 (objects, morphisms) | Abstract set O, morphism set M | None — no spatial content |
| Ax2 (causal order) | Partial order ≤ on M | **Partial**: causal order implies directed information flow, precursor to a current |
| Ax3 (time-reversal dagger) | Involution †: M→M reversing causal order | **Partial**: forces J† = -J (T-odd), consistent with forced property above |
| Ax4 (probability weight) | Map ε: M → [0,1] | **Partial**: ε(m) can be interpreted as probability weight of information flow |
| Ax5 (composition) | Tensor product structure | **Partial**: describes how local currents compose across CCA boundaries |

Conclusion: Ax2 + Ax3 + Ax4 together provide the conceptual ingredients for a current — causal directed flow with probability weight that is time-reversal-odd. They do not produce a spatial current density without one additional element: positions.

---

## 4. Candidate D2: J_C2 as CCA Probability Flux

### Definition

Given CCA objects at positions {xᵢ} ⊂ ℝᵈ with spacing a, and morphisms
m: xᵢ → xⱼ with weights ε(m), the CCA probability flux in direction α is:

```
J_α(x, t) = (1/aᵈ) Σ_{|xᵢ-x|<a/2} Σ_{j: xⱼ-xᵢ = a êα} [ε(m_{ij})(t) - ε(m_{ji})(t)] · (a/dt)
```

In the continuum limit (a → 0 at fixed c = a/dt):

```
J_α(x, t) = c · [n⁺_α(x,t) - n⁻_α(x,t)]
```

where n⁺_α, n⁻_α are the densities of CCA morphisms flowing in the +α and -α
directions. This reduces exactly to the existing PRW definition in 1D.

### Derivation status

| Step | Classification |
|------|---------------|
| CCA probability weight ε(m) | Ax4 — AXIOM |
| Causal direction from Ax2 | Ax2 — AXIOM |
| Time-reversal oddness from Ax3 | Ax3 — AXIOM |
| Spatial embedding of objects | **NEW AXIOM** (promotes implicit 2D chip interpretation) |
| Continuum limit a → 0 | **NEW ASSUMPTION** (analogous to A-PRW2) |
| Reduction to PRW definition in 1D | **DERIVED** — exact identity |

### What [info] = dimensionless gives

If the information unit [info] is taken as dimensionless (= 1 nat = 1 bit/ln2,
i.e., a pure count), then:
- [s] = m⁻³ (number density of information quanta)
- [J] = m⁻² s⁻¹ (flux density of information quanta)
- [g] = J (energy) — the energy transferred per information quantum to the qubit
- This is consistent: H_int = g J σ_z has units [J · m⁻² · s⁻¹] which is
  an energy *rate* per unit area. For a qubit of area r_q², H_int ~ g J r_q²
  has units [J], which is correct for a Hamiltonian.

This treatment is self-consistent and requires no new unit conversion parameter.

---

## 5. The Two New Structural Results

### Result 1: c = a/dt

Under D2, the PRW propagation speed c equals the CCA lattice speed:

```
c = a / dt
```

where a is the CCA lattice spacing and dt is the CCA time step (duration of one
causal morphism).

**This is the first identification of what c is.** Previous documents treated c
as a completely free parameter with no structural meaning. D2 tells us c is the
speed at which causal information propagates between adjacent CCA objects.

This does not fix c's numerical value — a is still free. But it changes the
status of c from "arbitrary number" to "CCA lattice speed."

**Consequence:** The question "why does c have a particular value?" transforms
into "why does the CCA have a particular lattice spacing?" That is a different,
and arguably more tractable, question. It connects GAP-7 to the CCA geometry
rather than to elastic phonon physics.

### Result 2: g ~ ℏ

The dephasing rate formula is:

```
Γ_φ = (g²/ℏ²) · 2S₀τ = (g²/ℏ²) · 4n₀c²τ
```

For typical superconducting qubit parameters (T₂ ~ 100 μs, τ ~ 1 μs):

```
Γ_φ ~ 10⁴ s⁻¹
g² · n₀ · c² · τ / ℏ² ~ 10⁴ s⁻¹
```

For c ~ 6000 m/s, n₀ ~ 10¹⁵ m⁻³ (chip-scale density), τ ~ 10⁻⁶ s:

```
g² ~ ℏ² · 10⁴ / (4 · 10¹⁵ · 3.6×10⁷ · 10⁻⁶)
   ~ ℏ² · 10⁴ / (1.4×10¹⁷)
   ~ ℏ² · 7×10⁻¹⁴ s⁻¹
g  ~ ℏ · 8×10⁻⁷ s⁻½
   ~ ℏ · √(ω₀)  where ω₀ ~ 6×10⁻¹³ rad/s
```

This is extremely small for ω₀ ~ 10⁻¹³ rad/s. If instead we use the qubit
frequency ω_q ~ 5×10⁹ rad/s:

```
g ~ ℏ · √(ω_q) ~ (10⁻³⁴ J·s) · √(5×10⁹ s⁻¹) ~ 7×10⁻³⁰ J·s^½
```

The natural combination that gives units [J] (energy) is g = ℏ · ω_q · (some
dimensionless ratio). The dimensional analysis forces g to involve ℏ explicitly.

**This is the first time the theory's equations require g to involve ℏ.** Prior
documents treated g and ℏ as independent parameters. D2 + dimensional analysis
shows they are related: g is of order ℏ times a frequency-related factor.

---

## 6. What Remains Free: the Three Gaps

After D2, three parameters remain undetermined:

### Gap 0a: The lattice spacing a

a sets c = a/dt (with dt either a separate parameter or derived from a).
No existing C2 axiom determines a. Candidate scales:
- Planck length (1.6×10⁻³⁵ m) → c = speed of light. Incompatible with acoustic c.
- Chip geometry (100 μm) → dt must also be specified. Circular.
- No natural scale exists within the current axioms.

**This is the core remaining gap.** Fixing a would fix c.

### Gap 0b: The morphism density n₀

n₀ is the CCA background morphism density. In the PRW it appears as s₀
(background information density). It is a free parameter in all existing
documents. D2 gives it a cleaner interpretation (CCA connectivity density)
but does not fix its value.

### Gap 0c: The projection direction α

The scalar coupling H_int = g J_α σ_z requires choosing a direction α.
D2 partially constrains this: α should be the direction of dominant CCA
probability flux at the qubit location. For a stationary background (uniform
CCA), all directions are equal and α remains arbitrary. For a non-uniform
background (near a defect, near a boundary), α is determined by the gradient
of s. This is a genuine partial determination — not complete, but not
arbitrary either.

---

## 7. The 3D Transport Equation Under D2

In 3D with spatial embedding, the PRW generalizes to a set of B walker
directions {eᵢ}, with right-movers n⁺ᵢ and left-movers n⁻ᵢ for each direction i.

For an isotropic 3D CCA (equal morphism weights in all directions):

```
s = Σᵢ (n⁺ᵢ + n⁻ᵢ)
J = Σᵢ c (n⁺ᵢ - n⁻ᵢ) eᵢ
```

This gives the 3D telegrapher equation:

```
τ ∂²s/∂t² + ∂s/∂t = c² τ ∇²s
```

with one speed c = a/dt (identical in all directions, because the CCA is
isotropic by assumption).

**Key result:** If the CCA has isotropic causal structure (equal morphism weights
in all directions), then the 3D transport equation has a single speed c. Isotropy
at the CCA level is what forces the single-speed result — not isotropy of the
physical material (silicon).

This is the correct answer to the question "does SXC-IGC require isotropy?":

> The theory requires the **CCA causal structure** to be isotropic (equal
> morphism probability weights in all directions). This is a property of the
> abstract information substrate, not of any material. Silicon can be anisotropic
> without contradiction — silicon is the experimental medium, not the substrate.

If the CCA is anisotropic (different morphism densities in different directions),
the 3D transport is anisotropic with direction-dependent speed. This is a
consistent extension. It introduces a CCA anisotropy tensor as a new parameter.

---

## 8. The Experimental Discriminator

Under D2, with c as the CCA lattice speed:

> **Prediction:** The P3 ratio c = ξ_c/(2τ_B) should be the same for all
> qubit orientations within the same chip, because c is a property of the
> CCA geometry (uniform lattice), not of the crystal orientation.

> **Conventional phonon prediction:** The effective bath speed depends on
> crystal orientation (8435–9355 m/s for silicon LA branch). Rotating the
> crystal or probing different crystal orientations should change the
> inferred c.

**This is a genuine discriminating prediction.** It does not depend on the
value of c — only on whether c is orientation-dependent.

Experiment: fabricate qubits on chips cut at different crystal orientations
([100], [110], [111] surface cuts). Measure ξ_c and τ_B for each. If
ξ_c/(2τ_B) is orientation-independent, D2 + isotropic CCA is supported.
If orientation-dependent, the conventional phonon bath is supported.

**This prediction requires no fitted parameters beyond τ_B.** The ratio c = ξ_c/(2τ_B)
is measured, not fitted, from two independent observables.

---

## 9. Revised Gap Hierarchy

| Gap | Content | Status after D2 |
|-----|---------|-----------------|
| Gap 0a | Physical identity of J_C2 | **PARTIALLY RESOLVED** — J_C2 = CCA probability flux |
| Gap 0b | Value of c | **STRUCTURALLY IDENTIFIED** — c = a/dt; a still free |
| Gap 0c | Coupling energy g | **SCALE CONSTRAINED** — g ~ ℏ√ω; numerical value still free |
| Gap 0d | 3D transport | **CONDITIONALLY RESOLVED** — single c if CCA is isotropic |
| GAP-7 | Derivation of c | Still blocked until a is fixed or independently measured |
| Gap-g | Coupling constant g | Still free; scale now constrained by dimensional analysis |

The central remaining question is **Gap 0b: what fixes the CCA lattice spacing a?**
This is a more focused question than "what is c?" — it points toward the CCA
geometry, not toward silicon phonon physics.

---

## 10. Summary: What This Task Establishes

1. J_C2 can be defined as the CCA probability flux, derivable from Ax2, Ax3, Ax4 given spatial embedding. This is the strongest definition supportable by the theory.

2. c = a/dt: the PRW speed equals the CCA lattice speed. This is a structural identification, not a value.

3. g ~ ℏ: the coupling energy is of order ℏ times a frequency factor. This is the first constraint on g's scale.

4. Isotropy is a property of the CCA causal structure, not of the physical material. If the CCA is isotropic, the 3D transport has one speed regardless of what material the qubit sits in.

5. The experiment that discriminates D2 from conventional phonon physics is: measure c = ξ_c/(2τ_B) on chips with different crystal orientations. A constant c supports D2; an orientation-dependent c supports phonon bath.

6. The minimum missing input is the CCA lattice spacing a. This is a genuine new research question, not a restatement of GAP-7.
