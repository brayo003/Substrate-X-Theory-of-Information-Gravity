# Interaction Hamiltonian Derivation
## Coupling the Qubit to the Substrate Current: From H_int to Γ ∝ ω_rot²

**Status:** Derivation document — resolves OB-1 from transport_summary.md  
**Depends on:** Layers 1–5 (established), substrate_transport_derivation.md  
**Does not modify:** Any established equation, parameter, or approximation

---

## Notation

All symbols from substrate_transport_derivation.md carry their established meanings.
New symbols introduced here:

| Symbol | Units | Meaning |
|--------|-------|---------|
| H_S | J | Free qubit Hamiltonian |
| H_B | J | Free substrate (bath) Hamiltonian |
| H_int | J | Interaction Hamiltonian |
| g | J·m²·s/info | Coupling constant (dimensions fixed below) |
| A | — | Hermitian qubit operator (to be determined) |
| ρ_S(t) | — | Qubit density matrix |
| ρ_B | — | Substrate bath density matrix (stationary) |
| C_JJ(t) | (info/(m²·s))² | Current–current correlation function |
| S_JJ(ω) | (info/(m²·s))²·s | Current power spectral density |
| Γ_φ | s⁻¹ | Pure dephasing rate |
| Γ_↑, Γ_↓ | s⁻¹ | Excitation and relaxation rates |
| T₁ | s | Longitudinal relaxation time |
| T₂ | s | Transverse (dephasing) time |

---

## Part I — The Interaction Hamiltonian

### Section 1: The Most General Linear Coupling

**Starting point:** The qubit Hilbert space is ℂ² spanned by {|0⟩, |1⟩}. Every Hermitian operator on ℂ² is a linear combination of {I, σ_x, σ_y, σ_z}. The substrate current J(**x**,t) is a real classical field (established in substrate_transport_derivation.md).

**Assumption [A-lin-coupling]:** The coupling between qubit and substrate is linear in J. This is the minimal (lowest-order) coupling. Quadratic couplings J² would produce second-order corrections suppressed by additional powers of g.

**Assumption [A-local]:** The qubit couples to the substrate current at the qubit's location **x**_q. The field J(**x**_q, t) is evaluated at a single point. This is the electric-dipole approximation, standard for small quantum systems embedded in a field.

The most general linear, local, Hermitian interaction Hamiltonian is:

```
H_int = g · J(**x**_q, t) · A                              [H-INT-GEN]
```

where:
- g is a real coupling constant with units to be determined
- J(**x**_q, t) is the classical substrate current at the qubit location (units: info/(m²·s))
- A ∈ {α_x σ_x + α_y σ_y + α_z σ_z} with α_x² + α_y² + α_z² = 1 (unit Hermitian)

**Dimensional requirement:** H_int must have units of energy [J]. Therefore:

```
[g] × [J_field] × [A] = J
[g] × info/(m²·s) × 1 = J
[g] = J·m²·s/info                                          [DIM-g]
```

The coupling constant g has units of energy times area times time per information quantum. This is the unique dimensional choice.

**No further constraint on g comes from the substrate transport theory.** g is the single new parameter introduced by the quantum coupling. It is analogous to the electric charge e in QED — it sets the magnitude of the interaction.

### Section 2: Identifying the Qubit Operator A

The free qubit Hamiltonian (with energy splitting ℏω_q between |0⟩ and |1⟩) is, in the standard basis:

```
H_S = (ℏω_q / 2) σ_z                                       [H-FREE]
```

**Approximation [A-RWA-prep]:** We work in the rotating frame defined by H_S. In the interaction picture, operators evolve as:

```
σ_±(t) = σ_± exp(±i ω_q t)
σ_z(t) = σ_z    (time-independent)
```

where σ_+ = |1⟩⟨0|, σ_- = |0⟩⟨1|.

We now determine which choice of A produces **pure Ramsey dephasing** — that is, decay of the off-diagonal elements ρ_{01} of the qubit density matrix without population transfer between |0⟩ and |1⟩.

#### Case A: A = σ_z (longitudinal coupling)

In the interaction picture:

```
H_int^I = g · J(t) · σ_z                                   [H-INT-Z]
```

σ_z is diagonal: σ_z|0⟩ = −|0⟩, σ_z|1⟩ = +|1⟩. It commutes with H_S. Therefore H_int^I has no time dependence from the free evolution.

**Effect on the qubit:**
- Diagonal elements ρ_{00}, ρ_{11}: driven by ⟨0|σ_z|0⟩² and ⟨1|σ_z|1⟩² — non-zero.
- Off-diagonal elements ρ_{01}: driven by ⟨0|σ_z|1⟩ = 0. Wait — the Born-Markov equation couples ρ_{01} to itself through the commutator. Let us compute:

```
[σ_z, ρ] = [[σ_z, |0⟩⟨0|], ...] 
```

More precisely: the commutator [H_int^I, ρ] contains terms [σ_z, ρ]. For the off-diagonal element:

```
[σ_z, ρ]_{01} = (σ_z)_{00} ρ_{01} − ρ_{01} (σ_z)_{11} = (−1)ρ_{01} − ρ_{01}(+1) = −2ρ_{01}
```

This shows σ_z coupling directly modulates the phase of the off-diagonal element, not its magnitude — at first order. At second order (Born-Markov), the stochastic fluctuations of J destroy the phase coherence, producing pure dephasing with no population transfer.

**Conclusion on A = σ_z:** Longitudinal coupling σ_z produces **pure dephasing** (T₂ decay with T₁ = ∞). This is exactly the signature of Ramsey dephasing. ✓

#### Case B: A = σ_x or A = σ_y (transverse coupling)

In the interaction picture, using σ_x = σ_+ + σ_-:

```
H_int^I = g · J(t) · (σ_+ e^{iω_q t} + σ_- e^{-iω_q t})   [H-INT-X]
```

This contains terms oscillating at ±ω_q. Under the Born-Markov approximation, the rotating-wave approximation (RWA) selects terms at the qubit frequency. The Bloch-Redfield master equation then produces both:
- Population transfer rates Γ_↑ = Γ_- (excitation), Γ_↓ = Γ_+ (relaxation) — driving T₁ decay
- Dephasing from the population decay: Γ_φ = (Γ_↑ + Γ_↓)/2

**Conclusion on A = σ_x or σ_y:** Transverse coupling produces **both relaxation and dephasing** (T₁ decay with T₂ = 2T₁ at most). This does not produce **pure** Ramsey dephasing — it additionally modifies T₁. ✗

#### Case C: Mixed coupling A = α σ_z + β σ_x (β ≠ 0)

The transverse part contributes relaxation. For pure Ramsey dephasing (T₁ → ∞), we need β = 0.

#### Result [R-OPERATOR]: The unique minimal coupling producing pure Ramsey dephasing is:

```
A = σ_z                                                    [R-OPERATOR]
```

The interaction Hamiltonian is:

```
H_int = g · J(**x**_q, t) · σ_z                            [H-INT]
```
*(A-QUANT-9: linear coupling, A = σ_z; A-QUANT-10: local coupling at x_q; Def 2.11: A = σ_z (system operator), B = gJ (bath operator))*

**Physical interpretation:** The substrate current J at the qubit location shifts the qubit energy splitting by ±g·J (+ for |1⟩, − for |0⟩). Fluctuations in J therefore introduce random phase shifts between |0⟩ and |1⟩, destroying coherence without flipping the qubit. This is the canonical dephasing mechanism.

---

## Part II — Born-Markov Master Equation

### Section 3: Setup and Approximations

The full Hamiltonian is:

```
H = H_S + H_B + H_int = (ℏω_q/2)σ_z + H_B + g·J(**x**_q,t)·σ_z
```

**Approximation [A-BORN]:** Born approximation. The qubit–substrate coupling is weak: g² ≪ ℏ²/τ_B² where τ_B is the substrate correlation time. The total density matrix factorises at all times:

```
ρ_total(t) ≈ ρ_S(t) ⊗ ρ_B                                  [BORN]
```

where ρ_B is the stationary substrate bath state. This means the substrate is not significantly perturbed by the qubit — it remains in its equilibrium state.

**Approximation [A-MARKOV]:** Markov approximation. The substrate correlation time τ_B is short compared to the qubit decoherence time Γ⁻¹:

```
τ_B ≡ τ = 1/(2λ) ≪ Γ⁻¹                                    [MARKOV]
```

This is the substrate mean free time between PRW reversals, which is the natural correlation time of J (established from the transport equations — the flux J decays at rate 1/τ). The condition τ ≪ Γ⁻¹ will be verified self-consistently after computing Γ.

**Approximation [A-SEC]:** Secular approximation (rotating-wave approximation on the master equation level). Terms oscillating at ±2ω_q average to zero over the decoherence timescale.

Under these three approximations, the Bloch-Redfield master equation for the qubit density matrix in the interaction picture takes the standard form (see e.g. Breuer & Petruccione, Chapter 3):

```
dρ_S/dt = −(1/ℏ²) ∫₀^∞ dτ' Tr_B{[H_int(t), [H_int(t−τ'), ρ_S(t)⊗ρ_B]]}   [BR]
```

### Section 4: Evaluating the Double Commutator

With H_int(t) = g·J(t)·σ_z (in the interaction picture, σ_z is time-independent):

```
[H_int(t), [H_int(t−τ), ρ_S⊗ρ_B]]
= g²·J(t)·J(t−τ)·[σ_z, [σ_z, ρ_S⊗ρ_B]]
```

**Algebraic identity [ID-COMM]:** For any density matrix ρ_S:

```
[σ_z, [σ_z, ρ_S]] = 2(ρ_S − σ_z ρ_S σ_z)                  [ID-COMM]
```

**Proof:**
```
[σ_z, [σ_z, ρ_S]] = σ_z²ρ_S − 2σ_z ρ_S σ_z + ρ_S σ_z²
                   = ρ_S − 2σ_z ρ_S σ_z + ρ_S    (since σ_z² = I)
                   = 2ρ_S − 2σ_z ρ_S σ_z
                   = 2(ρ_S − σ_z ρ_S σ_z)   ∎
```

Taking the trace over the bath (Tr_B):

```
Tr_B{J(t)·J(t−τ)·[σ_z,[σ_z,ρ_S⊗ρ_B]]} = C_JJ(τ)·[σ_z,[σ_z,ρ_S]]
```

where the current-current correlation function is defined as:

```
C_JJ(τ) ≡ Tr_B{J(t)·J(t−τ)·ρ_B} = ⟨J(t)·J(t−τ)⟩_B        [DEF-CJJ]
```

**Approximation [A-STAT]:** The substrate is stationary (time-translation invariant): C_JJ(τ) depends only on τ, not on t. This follows from the PRW being a homogeneous, time-translation-invariant process.

Substituting into [BR]:

```
dρ_S/dt = −(g²/ℏ²) · (∫₀^∞ C_JJ(τ') dτ') · [σ_z, [σ_z, ρ_S]]
```

**Using [ID-COMM]:**

```
dρ_S/dt = −(2g²/ℏ²) · (∫₀^∞ C_JJ(τ') dτ') · (ρ_S − σ_z ρ_S σ_z)   [ME-QUBIT]
```

### Section 5: Extracting the Dephasing Rate

Write ρ_S in the {|0⟩, |1⟩} basis:

```
ρ_S = [[ρ_{00}, ρ_{01}],
        [ρ_{10}, ρ_{11}]]
```

**Diagonal elements (populations):**

```
(ρ_S − σ_z ρ_S σ_z)_{00} = ρ_{00} − (σ_z ρ_S σ_z)_{00}
```

Now (σ_z ρ_S σ_z)_{00} = ⟨0|σ_z ρ_S σ_z|0⟩ = ⟨0|(-1) ρ_S (-1)|0⟩ = ρ_{00}.

So (ρ_S − σ_z ρ_S σ_z)_{00} = ρ_{00} − ρ_{00} = 0. ✓

Similarly for ρ_{11}. **The populations are not driven by the σ_z coupling.** This confirms pure dephasing — no T₁ process.

**Off-diagonal elements (coherences):**

```
(ρ_S − σ_z ρ_S σ_z)_{01} = ρ_{01} − (σ_z ρ_S σ_z)_{01}
```

(σ_z ρ_S σ_z)_{01} = ⟨0|σ_z ρ_S σ_z|1⟩ = ⟨0|(-1) ρ_S (+1)|1⟩ = −ρ_{01}.

So (ρ_S − σ_z ρ_S σ_z)_{01} = ρ_{01} − (−ρ_{01}) = 2ρ_{01}.

Therefore [ME-QUBIT] for the off-diagonal element gives:

```
dρ_{01}/dt = −(2g²/ℏ²) · (∫₀^∞ C_JJ(τ) dτ) · 2ρ_{01}
           = −Γ_φ · ρ_{01}
```

with the **pure dephasing rate**:

```
Γ_φ = (4g²/ℏ²) ∫₀^∞ C_JJ(τ) dτ                           [DEPH-RATE]
```

**Equivalently, using the one-sided power spectral density at zero frequency:**

```
S_JJ(0) = 2 ∫₀^∞ C_JJ(τ) dτ                               [PSD-DEF]

Γ_φ = (2g²/ℏ²) · S_JJ(0)                                  [DEPH-PSD]
```

**Result [R-GAMMA-GENERAL]:** The dephasing rate is determined by the zero-frequency power spectral density of the substrate current, times the square of the coupling constant. This is exact within the Born-Markov approximation.

---

## Part III — The Substrate Current Correlation Function

### Section 6: C_JJ(τ) from the Transport Equations

The current J satisfies the established transport equation (C-J from substrate_transport_derivation.md):

```
∂J/∂t = −c² ∂s/∂x − (1/τ) J                               [C-J]
```

For the homogeneous, source-free substrate in equilibrium, the current fluctuations δJ around the mean satisfy:

```
∂(δJ)/∂t = −c² ∂(δs)/∂x − (1/τ)(δJ)                       [FLUCT-J]
```

**The current autocorrelation function:**

For a single spatial mode with wavenumber k, the current fluctuation evolves as (from the established dispersion relation [DISP-SOL]):

```
δJ_k(t) = δJ_k(0) · exp(−t/τ_k) · [oscillatory or purely decaying]
```

where the decay envelope is always exp(−t/(2τ)) (from the imaginary part of ω = −i/(2τ) ± ...).

**The simplest case — the zero-frequency (k=0) contribution:**

At k = 0, the dispersion relation gives ω = 0 or ω = −i/τ (two purely imaginary roots). The k=0 mode is purely diffusive. The flux at k=0 is the spatially averaged flux, which satisfies:

```
d⟨J⟩/dt = −(1/τ)⟨J⟩                                       [J-DECAY]
```

This gives an exponentially decaying correlation:

```
C_JJ^{(k=0)}(τ) = ⟨J(t+τ)J(t)⟩ = ⟨J²⟩_0 · exp(−|τ|/τ)  [CJJ-EXP]
```

where ⟨J²⟩_0 is the equilibrium variance of the current.

**General mode sum:**

For a spatially local measurement at the qubit position **x**_q, the correlation function is the sum over all modes k:

```
C_JJ(τ) = ∫ (dk/2π) S_k · exp(−|τ|/τ) · cos(Ω_k τ)        [CJJ-GEN]
```

where:
- S_k is the mode spectral weight (equilibrium variance of mode k)
- Ω_k = √(c²k² − 1/(4τ²)) for k > k_c (propagating), = 0 for k < k_c (evanescent)
- The exp(−|τ|/τ) decay applies universally to all modes

**Approximation [A-MARKOV-J]:** The correlation time of J is τ (mean reversal time). Under the Markov condition τ ≪ Γ_φ⁻¹, the integral ∫₀^∞ C_JJ(τ) dτ is dominated by the short-τ behaviour. For the rotating-frame perturbation (which is a broad-band, low-frequency disturbance), the relevant quantity is the zero-frequency spectral density:

```
S_JJ(0) = 2 ∫₀^∞ C_JJ(τ) dτ
```

Using [CJJ-EXP] for the dominant (near-DC) contribution:

```
∫₀^∞ C_JJ(τ) dτ ≈ ⟨(δJ)²⟩ · τ                             [INT-CJJ]
```

**Derivation:**

```
∫₀^∞ ⟨(δJ)²⟩ · exp(−τ/τ_sub) dτ = ⟨(δJ)²⟩ · τ_sub = ⟨(δJ)²⟩ · τ
```

where τ_sub = τ = 1/(2λ) is the substrate correlation time. This is exact for a single-exponential correlator.

**Result [R-INTEGRAL]:**

```
∫₀^∞ C_JJ(τ) dτ = ⟨(δJ)²⟩ · τ = ⟨(δJ)²⟩ / (2λ)           [INTEGRAL-RESULT]
```

**Approximation label [A-SINGLE-EXP]:** Approximating the full multi-mode correlator by the dominant near-DC exponential. The error from propagating modes (k > k_c) contributes oscillating terms cos(Ω_k τ) that average to smaller contributions in the integral ∫₀^∞ dτ because:

```
∫₀^∞ e^{-τ/τ} cos(Ω_k τ) dτ = τ / (1 + Ω_k² τ²)
```

This is suppressed by the factor 1/(1 + Ω_k² τ²) relative to the DC contribution. For Ω_k τ ≫ 1 (propagating modes well above the critical frequency), the contribution is negligible. The dominant contribution is from modes near k_c where Ω_k ≈ 0.

---

## Part IV — Substitution of Established Layer-4 Results

### Section 7: Inserting ⟨(δJ)²⟩ ∝ ω_rot²

**Established result (Layer 4, substrate_transport_derivation.md [ESTABLISHED-VAR]):**

For a qubit in a rotating frame with angular velocity ω_rot:

```
⟨(δJ)²⟩ = (2/3) s₀² ω_rot² r_q²                           [LAYER4]
```

where r_q is the effective size of the quantum system (the radius at which the substrate current fluctuation is evaluated, set by the qubit's spatial extent or the relevant coupling distance) and s₀ is the background information density.

**Substitution of [LAYER4] into [INTEGRAL-RESULT]:**

```
∫₀^∞ C_JJ(τ) dτ = (2/3) s₀² ω_rot² r_q² · τ              [INT-WITH-ROT]
```

**Substitution into [DEPH-RATE]:**

```
Γ_φ = (4g²/ℏ²) × (2/3) s₀² ω_rot² r_q² × τ
    = (8g²s₀²r_q²τ) / (3ℏ²) × ω_rot²                      [GAMMA-ROT-FULL]
```

Collecting all prefactors into a single coupling coefficient:

```
k_rot ≡ 8g²s₀²r_q²τ / (3ℏ²)                               [DEF-KROT] [KROT-CANONICAL]
```
*(Canonical symbolic definition. Empirical value: k_rot = 4.5 × 10⁻⁷ s, from decoherence_prediction.py / IBM Quantum Ramsey data. Cross-reference: COMPLETE_MASTER_EQUATION.md [empirical value only].)*

**First-principles result:**

```
Γ_φ = k_rot · ω_rot²                                       [MAIN-RESULT]
```

with:

```
k_rot = (8g²s₀²r_q²τ) / (3ℏ²) = (8g²s₀²r_q²) / (6ℏ²λ)   [KROT-EXPLICIT]
```

### Section 8: Verification of the κ Connection

The existing repository (UNIFIED_PERTURBATIVE_DERIVATION.md, Section 5.4) writes k_rot = 2κ/(3ℏ). Comparing with [KROT-EXPLICIT]:

```
2κ/(3ℏ) = 8g²s₀²r_q²τ/(3ℏ²)
```

Solving for κ:

```
κ = 4g²s₀²r_q²τ/ℏ = 4g²s₀²r_q²/(2λℏ)                    [KAPPA-FROM-G]
```

**Result [R-KAPPA]:** The dimensionless coupling κ is expressed in terms of first-principles parameters:

```
κ = 4g²s₀²r_q²τ/ℏ                                          [KAPPA-FROM-G]
```

This resolves OB-2 partially: κ is no longer a free parameter — it is determined by (g, s₀, r_q, τ). The remaining free parameter is g, the quantum-classical coupling constant, which sets the overall scale of the interaction and cannot be derived from the classical transport theory alone (analogous to the electric charge e in QED, which must be measured).

---

## Part V — Complete Derivational Chain for Γ ∝ ω_rot²

### Section 9: Step-by-step accounting

Every step labelled: **[D]** derived, **[A]** assumption, **[I]** identity.

```
[A-lin-coupling]  H_int = g·J·A  (linear coupling, minimal order)
      ↓
[D + I]  Evaluate [σ_z,[σ_z,ρ_S]]:  populations unchanged,
                                     coherences: factor of 2
      ↓
[R-OPERATOR]  A = σ_z is unique for pure Ramsey dephasing
      ↓
[A-BORN]       Born approximation: ρ_total = ρ_S ⊗ ρ_B
[A-MARKOV]     Markov approximation: τ_B = τ ≪ Γ_φ⁻¹
[A-SEC]        Secular approximation: fast oscillations drop out
      ↓
[BR]           Bloch-Redfield master equation
      ↓
[I: algebra]   Extract off-diagonal component
      ↓
[DEPH-RATE]    Γ_φ = (4g²/ℏ²) ∫₀^∞ C_JJ(τ) dτ   ← exact within Born-Markov

      ↓

[A-STAT]       Substrate is stationary
[A-SINGLE-EXP] C_JJ(τ) ≈ ⟨(δJ)²⟩·exp(−τ/τ_sub)  (dominant DC contribution)
      ↓
[INTEGRAL-RESULT]  ∫₀^∞ C_JJ(τ)dτ = ⟨(δJ)²⟩·τ

      ↓

[LAYER4] ← ESTABLISHED Layer 4:  ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q²

      ↓
[I: substitution]
      ↓
[MAIN-RESULT]    Γ_φ = k_rot · ω_rot²

where k_rot = 8g²s₀²r_q²τ/(3ℏ²)     ← first-principles expression
```

### Section 10: What Is Derived vs What Requires Input

| Claim | Status | Requires |
|-------|--------|---------|
| H_int = g·J·σ_z | **Derived** (unique for pure dephasing) | [A-lin-coupling] + operator algebra |
| Born-Markov master equation | **Standard open systems** | [A-BORN]+[A-MARKOV]+[A-SEC] |
| Γ_φ = (4g²/ℏ²)∫C_JJ dτ | **Derived** from master equation | Operator algebra [ID-COMM] |
| ∫C_JJ dτ = ⟨(δJ)²⟩·τ | **Derived** from transport + [A-SINGLE-EXP] | Single-exponential approximation |
| ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² | **Established** (Layer 4) | No new input |
| Γ_φ = k_rot·ω_rot² | **Derived** | All of the above |
| k_rot = 8g²s₀²r_q²τ/(3ℏ²) | **Derived** (first-principles expression) | g = quantum coupling |
| g (coupling constant) | **Not derivable** from classical transport | Must be measured or from QFT |

**The functional form Γ ∝ ω_rot² is fully derived from first principles within Born-Markov.**

**The coefficient k_rot is expressed in terms of one remaining free parameter g.**

**No phenomenological Lorentzian saturation is introduced.**

**No ω_max appears.** The Born-Markov integral ∫₀^∞ C_JJ(τ)dτ converges because C_JJ(τ) decays exponentially at rate 1/τ_sub. The result is finite with no UV cutoff needed.

---

## Part VI — Multiple Interaction Hamiltonians: Complete Comparison

### Section 11: All Four Hermitian Operators

For completeness: all four choices of A and their physical consequences.

| Choice | H_int | T₁ effect | T₂ effect | Pure Ramsey dephasing? |
|--------|-------|-----------|-----------|----------------------|
| A = σ_z | g·J·σ_z | **None** | Yes (Γ_φ = k_rot ω²) | **Yes** ✓ |
| A = σ_x | g·J·σ_x | Yes (Γ_↑+Γ_↓) | Yes (Γ_φ + (Γ_↑+Γ_↓)/2) | No ✗ |
| A = σ_y | g·J·σ_y | Yes | Yes | No ✗ |
| A = σ_z + εσ_x | Mixed | Small (O(ε²)) | Dominant σ_z term | No (unless ε=0) ✗ |

**Unique selection:** Only A = σ_z (or any scalar multiple, absorbed into g) produces pure Ramsey dephasing. The selection criterion is physically motivated: a Ramsey experiment measures the evolution of coherence ρ_{01} without driving population transfer. This singles out σ_z uniquely.

**Why not σ_x or σ_y?** These flip the qubit (σ_x|0⟩ = |1⟩, etc.), which destroys coherence through relaxation rather than dephasing. Relaxation produces Ramsey decay at rate Γ_φ + T₁⁻¹/2, not pure dephasing.

---

## Section 12: Assumptions Summary and Self-Consistency Check

### Assumptions introduced in this document

| Label | Statement | Physical justification |
|-------|-----------|----------------------|
| [A-lin-coupling] | H_int linear in J | Minimal coupling order |
| [A-local] | Coupling at point **x**_q | Qubit size ≪ correlation length of J |
| [A-BORN] | ρ_total = ρ_S ⊗ ρ_B | Weak coupling g² ≪ ℏ²/τ² |
| [A-MARKOV] | τ_B = τ ≪ Γ_φ⁻¹ | Substrate relaxes fast compared to decoherence |
| [A-SEC] | Secular approx | Valid when ω_q ≫ Γ_φ (standard Ramsey condition) |
| [A-STAT] | C_JJ stationary | PRW is time-translation invariant |
| [A-SINGLE-EXP] | DC-dominated correlator | Propagating modes suppressed by 1/(1+Ω_k²τ²) |

### Self-consistency of the Markov condition

From [MAIN-RESULT]: Γ_φ = k_rot ω_rot².

The Markov condition requires τ ≪ Γ_φ⁻¹:

```
τ ≪ 1/Γ_φ = 1/(k_rot ω_rot²) = 3ℏ²/(8g²s₀²r_q²τ·ω_rot²)
```

Rearranging:

```
τ² ≪ 3ℏ²/(8g²s₀²r_q²ω_rot²)
```

This is satisfied when the coupling g is small (weak-coupling regime) or when ω_rot is not too large. This is consistent with the Born approximation [A-BORN] and the expectation that k_rot ω_rot² is small for laboratory rotation rates.

**Numerical check:** Using the empirical k_rot = 4.5×10⁻⁷ s and typical ω_rot ∼ 10⁵ rad/s:

```
Γ_φ ~ 4.5×10⁻⁷ × (10⁵)² = 4.5×10³ s⁻¹
τ_sub = Γ_φ⁻¹ ~ 2.2×10⁻⁴ s
```

For τ ≪ 2.2×10⁻⁴ s, any substrate correlation time τ < 10⁻⁵ s satisfies the Markov condition. This is physically reasonable.
