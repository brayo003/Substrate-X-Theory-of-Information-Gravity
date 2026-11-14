# INTERACTION SPACE AUDIT
## Do Physical Constraints Force Any Specific Energy-Information Feedback?

**Date:** 2026-08-22  
**Method:** Stages A–G. Enumerate all admissible interactions, apply physical constraints, derive macroscopic equations, test equivalence.  
**Governing rule:** A selection principle must be named. Choosing an interaction because it produces interesting dynamics is not a derivation.

---

## 1. The Question

The substrate master equation contains `αE` — an energy-to-information source term. This term was previously phenomenological. The question is:

> Does the PRW microscopic ontology, together with physical constraints, uniquely determine (or meaningfully restrict) the mechanism behind `αE`?

The answer has three possible outcomes:
- (A) Constraints force a unique mechanism → the term is derived
- (B) Constraints allow a family → the family is the result, not a specific member
- (C) Constraints are vacuous → the term is irreducibly phenomenological

---

## 2. Stage A — Microscopic State and Symmetries

**State at each site x:** `(n⁺, n⁻, e⁺, e⁻)` with n±, e± ≥ 0.

| Variable | Units | Meaning |
|----------|-------|---------|
| n⁺, n⁻ | info/m³ | Directional information density |
| e⁺, e⁻ | J/m³ | Directional energy density |

**Three symmetries of the undriven PRW:**

| Symmetry | Action | Implication for C± |
|----------|--------|-------------------|
| S1: Parity x→-x | n⁺↔n⁻, e⁺↔e⁻ | C_total must be even in (n⁺-n⁻, e⁺-e⁻) |
| S2: Time-reversal | n⁺(t)↔n⁻(-t) | Constrains ratio C_forward/C_backward (detailed balance) |
| S3: ±-permutation | (n⁺,e⁺)↔(n⁻,e⁻) | C⁻(n⁺,n⁻,e⁺,e⁻) = C⁺(n⁻,n⁺,e⁻,e⁺) |

**Equilibrium:** n⁺=n⁻=ρ/2, e⁺=e⁻=E/2 (J=0, P=0).

---

## 3. Stage B — Complete Interaction Enumeration

The conversion rate C⁺ must have units [info/(m³·s)]. With coupling α [info/(J·s)], the general form is C⁺ = α × F⁺ where F⁺ has units [J/m³].

**Complete local polynomial basis through degree two** under the following stated assumptions: locality (no gradient terms), algebraic (no memory or history), polynomial form (no saturation, exponential, or threshold functions), degree ≤ 2, no additional internal variables, no external fields, fixed dimensional reference scales n₀ and E₀. Without these restrictions the interaction space is infinite-dimensional. Reference scales n₀, E₀ make quadratic terms dimensionally consistent:

```
C⁺ = α [ a₁e⁺ + a₂e⁻                                      (spontaneous emission)
        + ε₀(b₁n⁺ + b₂n⁻)                                  (stimulated from occupancy)
        + (c₁e⁺n⁺ + c₂e⁺n⁻ + c₃e⁻n⁺ + c₄e⁻n⁻)/n₀        (stimulated conversion)
        + (d₁(e⁺)² + d₂e⁺e⁻ + d₃(e⁻)²)/E₀                (nonlinear energy)
        + ε₀(f₁(n⁺)² + f₂n⁺n⁻ + f₃(n⁻)²)/n₀ ]             (nonlinear occupancy)
```

C⁻ is derived from C⁺ by the ±-swap rule (S3).

**Physical interpretation of each class:**

| Term class | Physical analog | Energy justified? |
|------------|----------------|-------------------|
| a₁e⁺+a₂e⁻ | Spontaneous emission — rate ∝ local energy | Yes |
| ε₀(b₁n⁺+b₂n⁻) | Autocatalytic / stimulated — rate ∝ occupancy | Thermodynamically suspect |
| (cᵢ) cross terms | Stimulated conversion — rate ∝ energy × occupancy | Yes (laser analogy) |
| (dᵢ) quadratic energy | Two-photon absorption | Requires external scale E₀ |
| (fᵢ) quadratic occupancy | Logistic growth — no energy drawn | Violates bookkeeping |

---

## 4. Stage C — Physical Constraints Applied

### C1: Positivity (C± ≥ 0 for all n±, e± ≥ 0)
Forces: a₁, a₂, b₁, b₂ ≥ 0. For the quadratic terms, nonnegativity over the nonnegative orthant (n±, e± ≥ 0) is related to copositivity of the coefficient matrix — a condition weaker than positive semi-definiteness. The correct conclusion is: positivity imposes inequalities on the coefficients; it does not uniquely select the linear mechanism.  
**Does not eliminate any term class.**

### C2: Conservation (Q± = ε₀ C±, dQ_total/dt = 0)
Automatic given Q± = ε₀C±. Introduces ε₀ > 0 as a free parameter.  
**Does not restrict C± functional form.**

### C3: ±-Permutation Symmetry
Links C⁻ to C⁺ by swap. Does not eliminate terms — only constrains their relationship.  
**Does not restrict C± functional form.**

### C4: Equilibrium Existence
At equilibrium (n⁺=n⁻=ρ_eq/2, e⁺=e⁻=E_eq/2), net creation must balance σ_irr:
```
C⁺_eq + C⁻_eq = σ_irr
```
This gives **one scalar constraint** on parameter combinations.  
**Does not single out linear vs nonlinear terms.**

### C5: Entropy Production ≥ 0
Requires net conversion to proceed downhill in free energy. State-dependent constraint.  
**Does not uniquely determine C± functional form.**

### C6: Detailed Balance
For forward rate C_forward = αe⁺ and backward rate C_backward:
```
C_forward / C_backward = exp(ΔF/kT)
```
Near equilibrium: introduces a destruction term ∝ n⁺ alongside creation ∝ e⁺.  
Far from equilibrium: constrains the **ratio** of rates but not their individual forms.  
**Does not eliminate nonlinear terms.**

### Summary of Stage C

**The constraints do NOT force linearity.** They allow the multi-parameter family parametrized by (a₁, a₂, b₁, b₂, c₁..c₄, d₁..d₃, f₁..f₃) subject to positivity and detailed-balance inequalities.

> The linear mechanism C± = αe± is the **minimal member** of the admissible family, not the **forced member**.

---

## 5. Stage D — The Surviving Interaction Space

After coarse-graining C± to macroscopic fields using:
```
e⁺ = (E+P/c)/2,  e⁻ = (E-P/c)/2
n⁺ = (ρ+J/c)/2,  n⁻ = (ρ-J/c)/2
```

the cross-terms in C_total (symmetric under ±-swap) reduce to two distinct macroscopic scalar combinations:

```
e⁺n⁺ + e⁻n⁻ = (Eρ + PJ/c²)/2    [co-directional combination]
e⁺n⁻ + e⁻n⁺ = (Eρ - PJ/c²)/2    [cross-directional combination]
```

**The symmetric total-conversion sector** (C_total = C⁺+C⁻) of the degree-2 energy-information cross terms therefore contains exactly two independent scalar combinations:

| Combination | Macroscopic form | Physical meaning |
|-------------|-----------------|-----------------|
| Density coupling | Eρ | Energy density × information density |
| Flux coupling | PJ/c² | Energy flux × information flux |

**The directional difference sector** (C_diff = C⁺−C⁻) generates additional combinations. Specifically:

```
e⁺n⁻ − e⁻n⁺ = (Ps − EJ/c) / (2c)   →  Pρ and EJ contributions in J and P equations
```

The J and P evolution equations therefore also receive `Pρ` and `EJ` nonlinear terms from the cross-interaction sector. These are distinct from Eρ and PJ and must be tracked separately in the full 4-field system.

The two Eρ and PJ combinations are not "the complete nonlinear interaction space" — they are the complete scalar basis of the **symmetric total-rate sector**. The full nonlinear system is larger.

---

## 6. Stage E+F — Macroscopic PDE and Equivalence Audit

### The nonlinear 4-field system (stimulated cross-conversion, κ ≠ 0)

With the minimal nonlinear extension C⁺ = α(e⁺ + κe⁺n⁻/n₀), the exact coarse-grained system is:

```
∂ₜρ + ∂ₓJ = αE(1 + κρ/(2n₀)) − ακPJ/(2n₀c²)          [ρ]
∂ₜJ + c²∂ₓρ = −(1/τ)J + αP(1 + κρ/(2n₀)) − ακEJ/(2n₀) [J]
∂ₜE + ∂ₓP = −ε₀α·C_total                                [E]
∂ₜP + c²∂ₓE = −ε₀α·c·C_diff − (1/τ)P                  [P]
```

**Key structural change at κ ≠ 0:** The (E,P) block now depends on (ρ,J) through the κ terms. The one-directional block structure from the linear case **breaks**. Genuine two-way coupling:
```
(E,P) ↔ (ρ,J)
```

### Equivalence audit

| Nonlinear coupling | Macroscopic structure | Known system | Status |
|--------------------|-----------------------|-------------|--------|
| Eρ (Es) alone | ∂ₜρ = αEρ/n₀ + transport, ∂ₜE = −ε₀αEρ/n₀ + transport | Hyperbolic Lotka-Volterra (Mendez & Camacho 1997) | [F1] KNOWN |
| PJ alone | ∂ₜρ = −ακPJ/(2n₀c²) + αE + transport | Transport-coupled kinetics — **not standard in LV literature** | [O] OPEN |
| Eρ + PJ together | Mixed system | Unknown if reducible to known class | [O] OPEN |

### The PJ term specifically

The `−ακPJ/(2n₀c²)` term in the ρ equation involves the product of energy flux and information flux. This does not appear in the most familiar reaction-transport systems, which couple densities (Lotka-Volterra, FitzHugh-Nagumo, Gray-Scott).

This does not make it novel. A flux-flux coupling could emerge from known relativistic kinetic, radiative-transfer, hydrodynamic, or moment-closure formulations under a change of variables. The correct scientific status is:

> No equivalence to a known named system has yet been established.

Establishing that would require explicit comparison against wave-wave interaction literature, nonlinear moment hierarchies, and relativistic transport theory. That work has not been done.

---

## 7. The KL Information Variable

### Motivation and dimensional caveat

`s = n⁺ + n⁻` is occupation number with a unit relabeling — it is not Shannon information. A physically motivated alternative is the KL divergence of the local directional state from equilibrium:

```
s_KL = D_KL(p || p_eq) = p⁺ ln(2p⁺) + p⁻ ln(2p⁻)
```

where p⁺ = n⁺/ρ, p⁻ = n⁻/ρ, and p_eq = (1/2, 1/2).

**Critical dimensional difference:** `s_KL` is **dimensionless**. It is not a density. It cannot directly replace the dimensional `s` [info/m³] in the master equation `∂ₜs + ∂ₓJ = αE`, because `αE` has units [info/(m³·s)] under the original convention. A KL-based substrate information variable would require a new dimensional normalization and a redefinition of the corresponding flux and source law. That re-derivation has not been done. What has been derived is narrower:

> Given the source-free PRW equations, the dimensionless directional KL divergence has an exact evolution relation. Whether this KL variable can replace the original substrate's information density while retaining a consistent master equation is an open question.

### Key substitution

Let φ = J/(cρ) ∈ (−1, 1) (normalized directional asymmetry). Then:

```
s_KL(φ) = (1+φ)/2 · ln(1+φ) + (1−φ)/2 · ln(1−φ) = φ²/2 + φ⁴/12 + O(φ⁶)
```

(verified symbolically with SymPy). Near equilibrium: `s_KL ≈ φ²/2`.

**Note:** `s_KL` is even in φ — it does not encode the sign of the flux. A given value of `s_KL` corresponds to two states: φ and −φ. The scalar `s_KL` alone is **not a closed state variable** for the PRW; the sign of φ (or equivalently J) must be tracked separately.

### Exact evolution (source-free PRW, no interaction)

The normalized flux φ satisfies:
```
∂ₜφ = −(1/τ)φ − c(1−φ²)∂ₓlnρ + (c/2)∂ₓφ²
```

Since `s_KL'(φ) = artanh(φ)`, the exact evolution is:
```
∂ₜs_KL = artanh(φ) · [−(1/τ)φ − c(1−φ²)∂ₓlnρ + (c/2)∂ₓφ²]
```

This is exact but not closed in s_KL alone — it requires knowledge of φ (including its sign).

### Near-equilibrium form (corrected)

To leading order in small φ, using `artanh(φ) ≈ φ`, `φ∂ₓφ ≈ ∂ₓ(φ²/2) = ∂ₓs_KL`, and `φ² ≈ 2s_KL`:

```
∂ₜs_KL ≈ φ · [−(1/τ)φ − c∂ₓlnρ + c∂ₓφ]
         = −(1/τ)φ² − cφ∂ₓlnρ + cφ∂ₓφ
         = −(2/τ)s_KL − cφ · ∂ₓlnρ + c · ∂ₓs_KL
```

Since `φ = ±√(2s_KL)` (sign not determined by s_KL):

```
∂ₜs_KL ≈ −(2/τ)s_KL ∓ c√(2s_KL) · ∂ₓlnρ + c · ∂ₓs_KL
```

The `∓` reflects the sign ambiguity of φ. **The sign of the ∂ₓlnρ coupling depends on the direction of the flux and cannot be dropped.**

The factor on the density-gradient term is `c√(2s_KL)` — not `2c√(2s_KL)` as stated in the previous version.

### What this equation says

- s_KL relaxes at rate 2/τ (twice the flux relaxation rate)
- s_KL is advected at speed c
- s_KL is driven by density gradients with a √s_KL coupling whose sign depends on the branch

### Classification

The `√s_KL · ∂ₓlnρ` structure is not in the standard reaction-telegraph class. It is related to entropy production in kinetic theory and to the Fisher information of the density field. Whether it is equivalent to known kinetic-theory entropy evolution equations (McKean-Vlasov, H-theorem transport) requires explicit comparison that has not been done.

**Status: [O] OPEN** — a nonlinear √s_KL structure arises from the KL definition alone in the source-free case. The branch/sign issue means the scalar s_KL is insufficient as a standalone state variable. The full investigation requires either (a) working with (s_KL, sign(φ)) as the state pair, or (b) keeping φ and treating s_KL as a derived quantity.

---

## 8. What Physical Constraints Force vs What They Don't

| Claim | Verdict | Evidence |
|-------|---------|---------|
| Positivity forces C± = αe± (linear) | FALSE | Quadratic terms also satisfy positivity |
| ±-symmetry forces linear coupling | FALSE | Symmetric quadratic terms exist |
| Equilibrium existence forces linearity | FALSE | One scalar constraint, multi-parameter family |
| Detailed balance forces linearity | FALSE | Only constrains ratio C_forward/C_backward |
| Entropy production ≥ 0 forces linearity | FALSE | State-dependent, not functional-form constraint |
| Conservation alone determines C± | FALSE | Q±=ε₀C± holds for any C± |
| All constraints together force linearity | FALSE | Family parametrized by (a,b,c,d,f) coefficients survives |

**The answer to the central question is (B): the constraints allow a multi-parameter family. They do not force a specific mechanism.**

---

## 9. Honest Classification of Surviving Structures

| Structure | Derived from? | Equiv. to known? | Status |
|-----------|--------------|-----------------|--------|
| Linear 4-field system (κ=0) | Minimal C±=αe± + conservation | Two coupled telegraphers | [F1] conventional |
| Es coupling (hyperbolic LV) | Cross-term c₁,c₄ | Hyperbolic Lotka-Volterra | [F1] known class |
| PJ coupling | Cross-term c₂,c₃ | Not standard — unclassified | [O] open |
| s_KL evolution equation | KL definition + source-free PRW only | Not in reaction-telegraph lit; branch/sign issue means scalar s_KL is not closed | [O] open — partial result only |
| αP in J equation | Minimal conversion + coarse-grain | Absent from original ME — structural correction | [F2] new term, known dynamics |

---

## 10. What Would Constitute a Genuine Selection Principle

None of the standard constraints (positivity, conservation, symmetry, equilibrium, entropy) select a unique nonlinear form. A genuine selection principle would be one of:

1. **A specified Hamiltonian / transition matrix** — if the conversion process is given a Hamiltonian `H_conv`, detailed balance uniquely determines C±(e,n) up to the temperature T. Different H_conv choices give different C±. The project does not specify H_conv.

2. **Irreversibility structure** — if the conversion is strictly irreversible (no backward process), detailed balance does not apply and C± is unconstrained beyond positivity. This opens the full family.

3. **A physical process** — if there is a specific microscopic scattering model (e.g., phonon-quasiparticle scattering), the rates follow from Fermi's golden rule applied to that model. This would be a genuine derivation, not a dimensional choice.

Without one of these, the interaction space remains multi-dimensional and the nonlinear terms remain free parameters with physical interpretations but no unique selection.

---

## 11. The Corrected Research Program

The previous program: `PDE → interpretation → simulation`

The corrected program:

```
1. SPECIFY microscopic ontology: (n⁺, n⁻, e⁺, e⁻)
2. CHOOSE information variable: s = n⁺+n⁻ (linear) or s_KL = D_KL(p||p_eq) (nonlinear)
3. ENUMERATE admissible C±(e,n) — degree by degree
4. APPLY constraints: positivity, ±-symmetry, conservation, equilibrium, detailed balance
5. IDENTIFY surviving family — do NOT select a specific member without a selection principle
6. DERIVE macroscopic equations for the full surviving family
7. TEST equivalence to known systems for each member
8. ANALYZE dynamics only for members not equivalent to known systems
```

**The two genuinely open directions from this audit:**

**Direction 1 — PJ coupling:**
The `−ακPJ/(2n₀c²)` term (flux-flux product) is not standard in reaction-transport systems. Its dynamics under hyperbolic transport have not been classified. This requires derivation of the linearized dispersion and explicit comparison against wave-wave interaction literature.

**Direction 2 — KL information variable:**
The equation `∂ₜs_KL = artanh(φ)·[...]` with √s_KL nonlinearity is derived from the PRW definition alone. Its equivalence to known kinetic-theory entropy equations has not been established. This requires comparison against McKean-Vlasov, Boltzmann H-theorem transport, and nonlinear diffusion literature.

Both are genuine open questions. Neither is a result yet.

---

## 12. Central Conclusion

The audit has established the following:

> **PRW ontology + standard physical constraints do not entail C± = αe±.**
> Therefore αE is not derived from the existing substrate ontology.
> C± = αe± is a minimal phenomenological closure that produces a mathematically consistent extended system. It is a model choice, not a first-principles consequence.

This is an improvement over the previous state of the project: the substrate no longer falsely claims to derive physics it has merely stipulated.

The remaining scientific question is not "can we manipulate the equations to produce interesting behavior?" It is:

> **What microscopic principle, if any, selects the interaction law?**

If no such principle can be produced — from a specified Hamiltonian, a physical scattering process, or a derived irreversibility structure — then the theory remains an underdetermined phenomenological framework. That is the correct scientific position at this stage.

The two open directions (PJ flux-flux coupling; KL-variable evolution) are genuine questions. Neither has yet been shown to reduce to a known system, and neither has yet been shown to be genuinely novel. Establishing which requires:
1. For PJ: explicit linearized dispersion analysis and comparison against wave-wave interaction literature.
2. For KL: working with the full state (ρ, φ) rather than the scalar s_KL, and comparing the resulting system against McKean-Vlasov and Boltzmann entropy-transport literature.
