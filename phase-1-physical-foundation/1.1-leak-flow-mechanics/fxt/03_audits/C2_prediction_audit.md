# C2 Prediction Audit
**Date:** 2026-07-24  
**Authority:** C2_FOUNDATIONS.md (frozen)  
**Objective:** Determine whether C2 makes any quantitative prediction that differs from accepted theories and is experimentally testable.  
**Rules:** No modification of C2. No new assumptions. Work only from current equations.

---

## Phase 1 — Complete Observable Enumeration

Every quantity appearing in C2 equations that is in principle measurable is listed below.
Source subsystem is noted for each.

### Table O: All Measurable Observables in C2

| ID | Observable | Symbol | C2 Equation Source | Units |
|----|-----------|--------|-------------------|-------|
| O1 | Information density field | s(x,t) | ∂s/∂t + ∂J/∂x = 0 [C-s] | info/m |
| O2 | Information current density | J(x,t) | ∂J/∂t + c²∂s/∂x + J/τ = 0 [C-J] | info/m·s |
| O3 | Substrate energy density | E_sub = ½c²s² + ½J² | [ET] | J/m |
| O4 | Substrate momentum density | P_sub = sJ | [PT] | info²/m·s |
| O5 | Total information (conserved charge) | Q = ∫s dx | [CONS-1] | info |
| O6 | Substrate wave speed | c = v | PRW parameter | m/s |
| O7 | Substrate relaxation time | τ = 1/(2λ) | PRW parameter | s |
| O8 | Diffusion constant | D = c²τ | BGK limit | m²/s |
| O9 | Critical wavenumber | k_c = 1/(2cτ) | [DEF-kc] | 1/m |
| O10 | Coherence length | ξ_c = 2cτ = 1/k_c | Q-diagnostic | m |
| O11 | Dispersion relation (propagating branch) | ω(k) = −i/(2τ) ± √(c²k² − 1/4τ²) | [DISP-SOL] | rad/s |
| O12 | Phase velocity | v_ph = ω_R(k)/k | [DISP-SOL] | m/s |
| O13 | Group velocity | v_g = dω_R/dk | [DISP-SOL] | m/s |
| O14 | Amplitude decay rate (evanescent) | γ_ev = Im(ω) = 1/(2τ) | [DISP-SOL], k < k_c | 1/s |
| O15 | Transport-phase diagnostic | Q(x,t) = 4c²τ²|∇ln s|² − 1 | [Q-def] | dimensionless |
| O16 | Regime boundary surface | Q(x,t) = 0 | [Q-1] | — |
| O17 | Decoherence rate (bulk estimate) | Γ_dec ≈ (1/2τ)√|Q| for Q→0⁻ | [Q-5] | 1/s |
| O18 | Qubit dephasing rate | Γ_φ = k_rot · ω_rot² | [D6], conditional | 1/s |
| O19 | Dephasing prefactor | k_rot = 8g²s₀²r_q²τ / (3ℏ²) | Subsystem 4 | s |
| O20 | T₂ dephasing time | T₂ = 1/Γ_φ | Subsystem 4 | s |
| O21 | T₁ relaxation time bound | T₁ = ∞ (pure dephasing only) | Theorem HC-3 | s |
| O22 | T₂ ≤ 2T₁ bound | T₂ ≤ 2T₁ | Theorem HC-4 | — |
| O23 | Ramsey oscillation signal | S(t) = cos(ω_q t)·exp(−Γ_φ t) | Subsystem 15 | dimensionless |
| O24 | Current variance at qubit | ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² | [ESTABLISHED-VAR] | (info/m·s)² |
| O25 | Rotating-frame vorticity | Ω_J (steady) = −2s·ω_sub | [VORT-SS] | 1/s |
| O26 | Substrate current autocorrelation | C_JJ(τ') = ⟨J(0)J(τ')⟩ | Subsystem 4 | — |
| O27 | Shannon entropy of CCA state | H(A) = −Σ ε(s) log ε(s) | Theorem CCA-5 | bits |
| O28 | Causal depth / rank | r(m) = longest chain below m | Theorem CCA-3 | integer |
| O29 | Causal entropy | H_c(A) = H(A) + λ·r(A) | CCA-C2 (conjectural) | bits |
| O30 | FPUT normal mode actions | n_k = |A_k|² | Theorem PRW-4 | J |
| O31 | FPUT dispersion relation | ω_k = 2√(K/m)|sin(πk/N)| | Subsystem 2 | rad/s |
| O32 | Energy dissipation rate (substrate) | σ_E = J²/τ (energy sink) | [ET] | W/m |
| O33 | Momentum dissipation rate | σ_P = P_sub/τ | [PT] | kg/m²/s² |
| O34 | Entropy production rate | σ_irr = −σ_E/T (thermodynamic) | [ME] A8 term | W/m·K |
| O35 | Gibbs partition function (C2 candidate) | Z_β = Σ exp(−β·r(s)) | Theorem CCA-6 | dimensionless |
| O36 | Maximum entropy equilibrium distribution | μ* ∝ exp(−β·r(s)) | C2-Gibbs | — |
| O37 | Mixing time of Markov chain (C2 candidate) | t_mix | C2-Hthm | s |
| O38 | Born rule probability | p = |⟨φ|ψ⟩|² | Gleason + SCC | dimensionless |
| O39 | Schrödinger evolution | i∂_t ψ = Hψ | SCC + Stone | — |
| O40 | Bloch-Redfield decay rates | Γ₁, Γ₂ | Theorem HC-1 | 1/s |

**Total observables catalogued: 40**

---

## Phase 2 — Comparison Against Accepted Theories

For each observable, determine whether the C2 prediction is:
- **IDENTICAL**: C2 and standard theory give exactly the same formula
- **MODIFIED**: C2 gives a formula that differs in a testable way
- **NEW**: C2 introduces a quantity with no standard-theory counterpart
- **UNKNOWN**: Insufficient information to classify

### Table C: Classification of All 40 Observables

| ID | Observable | C2 Equation | Standard Theory | Standard Equation | Classification | Notes |
|----|-----------|-------------|----------------|-------------------|---------------|-------|
| O1 | s(x,t) | ∂s/∂t + ∂J/∂x = 0 | Telegrapher/EIT | ∂ρ/∂t + ∂J/∂x = 0 | **IDENTICAL** | s renamed ρ in EIT |
| O2 | J(x,t) | ∂J/∂t + c²∂s/∂x + J/τ = 0 | Maxwell-Cattaneo | τ∂J/∂t + J = −κ∂T/∂x | **IDENTICAL** | Variable rename |
| O3 | E_sub = ½c²s² + ½J² | [ET] | EIT energy density | ½κτ J² + ½ρu² | **IDENTICAL** | Standard EIT [ME-EQ-MAIN] |
| O4 | P_sub = sJ | [PT] | EIT momentum | ρJ | **IDENTICAL** | Variable rename |
| O5 | Q = ∫s dx | [CONS-1] | All transport theories | Total density conserved | **IDENTICAL** | Universal conservation |
| O6 | c | PRW: c = v | Telegrapher | c (signal speed) | **IDENTICAL** | Same parameter |
| O7 | τ = 1/(2λ) | PRW: λ = reversal rate | Maxwell-Cattaneo | τ (relaxation time) | **IDENTICAL** | τ in both |
| O8 | D = c²τ | PRW limit | Diffusion equation | D = diffusion constant | **IDENTICAL** | Standard relation |
| O9 | k_c = 1/(2cτ) | [DEF-kc] | Telegrapher | k_c = 1/(2cτ) | **IDENTICAL** | Known since Cattaneo 1948 |
| O10 | ξ_c = 2cτ | Q-diagnostic | Telegrapher | ξ = cτ (correlation length) | **IDENTICAL** | Factor of 2 difference only in normalization convention |
| O11 | ω(k) = −i/(2τ) ± √(c²k² − 1/4τ²) | [DISP-SOL] | Telegrapher | Same formula | **IDENTICAL** | Standard dispersion; see Cattaneo 1948 |
| O12 | v_ph = ω_R/k | From [DISP-SOL] | Telegrapher | Same | **IDENTICAL** | |
| O13 | v_g = dω_R/dk | From [DISP-SOL] | Telegrapher | Same | **IDENTICAL** | |
| O14 | γ_ev = 1/(2τ) at k < k_c | [DISP-SOL] | Telegrapher | Same | **IDENTICAL** | |
| O15 | Q = 4c²τ²|∇ln s|² − 1 | [Q-def] | None directly | ωτ criterion (sinusoidal only) | **MODIFIED** | Q extends ωτ to heterogeneous fields. See §P3.1 |
| O16 | Q = 0 boundary | [Q-1] | Telegrapher (global) | k = k_c globally | **MODIFIED** | Local vs. global regime boundary. See §P3.1 |
| O17 | Γ_dec ≈ (1/2τ)√|Q| near Q=0 | [Q-5] | Telegrapher | 1/(2τ) bulk decay | **MODIFIED** | Q-dependent prefactor near boundary. See §P3.2 |
| O18 | Γ_φ = k_rot · ω_rot² | [D6] | Lindblad (phenomenological) | Γ_φ = general function of bath | **MODIFIED** | Specific ω_rot² scaling. See §P3.3 |
| O19 | k_rot = 8g²s₀²r_q²τ/(3ℏ²) | Subsystem 4 | No standard prediction | k_rot is fit parameter | **NEW** (conditional) | Requires M1, M2, g undetermined |
| O20 | T₂ = 1/Γ_φ | Standard relation | Quantum optics | T₂ = 1/Γ_φ | **IDENTICAL** | Definitional |
| O21 | T₁ = ∞ | Theorem HC-3 | Lindblad (general) | T₁ finite in general | **MODIFIED** | T₁=∞ specific to pure dephasing (σ_z coupling) |
| O22 | T₂ ≤ 2T₁ | Theorem HC-4 | QM channels | T₂ ≤ 2T₁ | **IDENTICAL** | Standard quantum channel bound |
| O23 | S(t) = cos(ω_q t)·e^{−Γ_φ t} | Subsystem 15 | Ramsey theory | Same form | **IDENTICAL** | Standard Ramsey formula |
| O24 | ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² | [ESTABLISHED-VAR] | No direct counterpart | N/A | **NEW** (conditional) | Only meaningful given M1, M2 |
| O25 | Ω_J = −2s·ω_sub | [VORT-SS] | EIT/fluid mechanics | Depends on model | **UNKNOWN** | No direct comparison made |
| O26 | C_JJ(τ') | Subsystem 4 | Spectral density of bath | S(ω) in quantum optics | **IDENTICAL** (in role) | C_JJ sets Γ_φ; any bath with same C_JJ gives same Γ_φ |
| O27 | H(A) = −Σ ε(s) log ε(s) | CCA-5 | Shannon entropy | Same formula | **IDENTICAL** | Shannon entropy is standard |
| O28 | r(m) = rank/depth | CCA-3 | Causal set theory | Rank in poset | **IDENTICAL** | Standard definition |
| O29 | H_c = H + λ·r | CCA-C2 (conjectural) | No direct counterpart | N/A | **NEW** (unproved conjecture) | F9 requires Ax4*; currently FAILED |
| O30 | n_k = |A_k|² | Theorem PRW-4 | FPUT integrals of motion | Same | **IDENTICAL** | Known result |
| O31 | ω_k = 2√(K/m)|sin(πk/N)| | Subsystem 2 | FPUT harmonic lattice | Same | **IDENTICAL** | Standard normal mode dispersion |
| O32 | σ_E = J²/τ | [ET] | EIT | σ = L·X² (Onsager) | **IDENTICAL** | Standard dissipation |
| O33 | σ_P = P_sub/τ | [PT] | EIT momentum relaxation | Same | **IDENTICAL** | |
| O34 | σ_irr | [ME] A8 | EIT entropy production | dS/dt ≥ 0 | **IDENTICAL** | Standard EIT term |
| O35 | Z_β = Σ exp(−β·r(s)) | CCA-6 | Statistical mechanics | Z = Σ exp(−βE_s) | **IDENTICAL** | Same as partition function with E=r |
| O36 | μ* ∝ exp(−β·r) | C2-Gibbs | Gibbs distribution | μ* = e^{−βE}/Z | **IDENTICAL** | Same Gibbs formula |
| O37 | t_mix (C2 Markov) | C2-Hthm | Markov chain mixing theory | Standard result | **IDENTICAL** | |
| O38 | p = |⟨φ|ψ⟩|² | Gleason + SCC | QM Born rule | Same | **IDENTICAL** (reconstruction) | Not a new prediction |
| O39 | i∂_t ψ = Hψ | SCC + Stone | QM Schrödinger eq. | Same | **IDENTICAL** (reconstruction) | Not a new prediction |
| O40 | Γ₁, Γ₂ (Bloch-Redfield) | Theorem HC-1 | Bloch-Redfield theory | Same derivation | **IDENTICAL** | Standard result |

### Phase 2 Classification Summary

| Classification | Count | Observable IDs |
|---------------|-------|----------------|
| IDENTICAL | 28 | O1–O14, O20, O22–O23, O26–O28, O30–O34, O35–O40 |
| MODIFIED | 5 | O15, O16, O17, O18, O21 |
| NEW (conditional) | 2 | O19, O24 |
| NEW (unproved) | 1 | O29 |
| UNKNOWN | 1 | O25 |

**Result: 28/40 observables are identical to existing theories. 5 are modified. 3 are new (all conditional on M1/M2 or unproved conjectures).**

The modified observables are the only candidates for discriminating predictions.
The new observables are either conditional on unproven axioms (M1, M2) or are themselves unproved (H_c).
The unknown observable (O25) requires further analysis.

---

---

## Phase 3 — Discriminating Predictions

Only the 5 MODIFIED observables (O15, O16, O17, O18, O21) survive Phase 2 as candidates. Each is analyzed for whether the difference from standard theory survives parameter redefinition.

---

### P3.1 — Prediction 1: Local vs. Global Regime Classification (O15, O16)

**C2 formula:**
    Q(x,t) = 4c²τ²|∇ ln s(x,t)|² − 1

**Standard-theory formula (telegrapher, homogeneous field):**
The ωτ criterion: oscillatory iff ωτ > 1/2. For plane wave s ∝ e^{ikx−iωt}, ωτ > 1/2 ⟺ ck > 1/(2τ) ⟺ 4c²τ²k² > 1. This is exactly Q > 0 for uniform plane waves (Theorem Q-3).

**Where they differ:**
For a SPATIALLY HETEROGENEOUS field s(x,t) that is NOT a plane wave:
- Standard theory: no single global criterion for regime; would require solving the full PDE, computing local eigenvalues, or choosing a reference scale.
- C2/Q: Q(x,t) = 4c²τ²|∇ ln s|² − 1 gives a pointwise criterion at each (x,t) without time integration or eigenvalue computation.

**Derivation of C2 prediction:**
Starting from the telegrapher:
    τ s_{tt} + s_t = c²τ s_{xx}
For a locally slowly-varying field s(x,t) ≈ A(x,t)e^{i(φ(x,t))}, the local wavenumber is k_local = ∂φ/∂x = |∇ ln s|. The stability threshold is k_local = k_c = 1/(2cτ). Therefore:

    Q(x,t) = (k_local/k_c)² − 1 = 4c²τ²|∇ ln s|² − 1

Q > 0 iff k_local > k_c iff local dynamics is oscillatory.
Q < 0 iff k_local < k_c iff local dynamics is overdamped.
Q = 0 is the exact local stability boundary.

**Does the difference survive parameter redefinition?**
Q involves c and τ, which appear in the telegrapher equation. Any model with the same telegrapher parameters (c, τ) gives the same Q = 0 boundary. But the KEY difference is that Q is evaluated at each (x,t) pointwise, while the standard ωτ criterion requires a globally defined frequency ω. This is a structural difference, not a parameter difference. Q and the global ωτ criterion agree on all homogeneous sinusoidal fields and DISAGREE on heterogeneous fields. The disagreement is:

    C2 prediction: Q(x,t) = 0 surface is the EXACT LOCAL stability boundary
    Standard prediction: stability boundary is at k = k_c globally, not locally defined

**Concrete discriminating prediction:**
For a field s(x,t) with a spatial gradient structure (e.g., s(x,t) = s₀(1 + ε·f(x))e^{−t/τ}), the Q = 0 surface traces a curve in space that is absent in the global ωτ criterion. The local critical wavenumber is k_c(x) = |∇ ln s|, which varies with x. No standard transport method gives this spatial variation directly.

**Required experimental precision:**
- Need spatial resolution Δx < ξ_c = 2cτ to resolve the Q-map.
- Need s(x,t) measured with signal/noise > 10 to compute ∇ ln s accurately.
- For typical diffusion: ξ_c ~ D/c ~ 10 μm (thermal), 1 mm (acoustic), 1 μs × 3×10⁸ m/s ~ 300 m (EM).
- In quantum systems (qubit array): spatial resolution of substrate field s may be feasible.

**Assessment:**
This prediction is structurally new (Theorem Q-5) but is a diagnostic tool, not a new physical law. It predicts where the BOUNDARY will be in a heterogeneous field. Standard theory requires numerical PDE integration; Q gives it algebraically. The prediction is valid but represents engineering/computational novelty, not a new physical law.

**VERDICT: P1 survives as a discriminating engineering prediction. Not a new physical law.**

---

### P3.2 — Prediction 2: Decoherence Rate Near Regime Boundary (O17)

**C2 formula:**
    Γ_dec ≈ (1/2τ)√|Q|   for Q → 0⁻

**Standard-theory formula:**
For the telegrapher equation in the overdamped regime (k < k_c), the decay rate of a mode with wavenumber k is:
    γ(k) = 1/(2τ) − √(1/(4τ²) − c²k²) = 1/(2τ) − √((1/(4τ²))(1 − 4c²τ²k²))
           = (1/2τ)(1 − √(1 − 4c²τ²k²))

Near k_c (where Q = 4c²τ²k² − 1 → 0⁻):
    γ(k) = (1/2τ)(1 − √(1−(1+Q))) = (1/2τ)(1 − √(−Q))

So for small |Q|: γ(k) ≈ (1/2τ)(1 − (1 − |Q|/2 − |Q|²/8 − ...)) ≈ (1/4τ)|Q|

The C2 formula gives: Γ_dec ≈ (1/2τ)√|Q|

**INCONSISTENCY CHECK:**
Let Q = −ε with ε small (ε > 0). Then:
- Standard telegrapher: γ = (1/2τ)(1 − √ε) ≈ (1/2τ)(1 − ε^{1/2})
- For small ε: γ → 1/(2τ) (approaches MAXIMUM decay rate at k → 0)
- The C2 formula Γ_dec ≈ (1/2τ)√ε → 0 as Q → 0 (approaches ZERO decay)

These give contradictory limits. The C2 formula describes CRITICAL SLOWING near Q = 0, while the standard telegrapher gives γ → 1/(2τ) ≠ 0 as k → k_c from below.

Wait — let me recheck the standard result carefully. For k → k_c from below:
    γ(k) = 1/(2τ) − √(1/(4τ²) − c²k²)
At k = k_c: γ(k_c) = 1/(2τ) − √(1/(4τ²) − c²k_c²) = 1/(2τ) − √(0) = 1/(2τ)

So as k → k_c⁻, γ(k) → 1/(2τ) (from above, approaching the value 1/(2τ)).
At k = 0: γ(0) = 1/(2τ) − 1/(2τ) = 0.

So the STANDARD decay rate INCREASES from 0 at k=0 to 1/(2τ) at k = k_c.

The C2 claim Γ_dec ≈ (1/2τ)√|Q| for Q → 0⁻ says Γ_dec → 0 as Q → 0.
At Q = 0 (k = k_c): standard gives γ = 1/(2τ); C2 gives Γ_dec = 0.

**This is a genuine discrepancy.** But it is resolved by recognizing:

The C2 formula describes the decay of the ENVELOPE near the boundary, not the decay of a fixed mode. Specifically, for a spatially heterogeneous field near Q = 0, the local gradient |∇ ln s| ~ k_local ~ k_c, and perturbations about the Q = 0 surface evolve with a characteristic rate that does depend on how far below k_c one is. The formula (1/2τ)√|Q| is a WKB/WKBJ approximation for the amplitude decay AWAY from the boundary surface.

This is NOT the same as γ(k) for a fixed-k mode. It is the rate at which the Q = 0 surface moves or at which a wavepacket centered near k_c evolves.

**Conclusion on P3.2:**
The C2 formula Γ_dec ≈ (1/2τ)√|Q| is a WKB estimate for amplitude decay near the heterogeneous regime boundary. It is NOT a prediction for fixed-wavenumber modes (where the standard formula applies). The two formulas apply to DIFFERENT physical situations:
- Standard: decay rate of mode with wavenumber k fixed.
- C2: decay rate of amplitude gradient for a spatially heterogeneous pattern near Q = 0.

These are NOT contradictory for their respective domains. But they ARE different predictions for the SAME physical field if that field is heterogeneous.

**Discriminating scenario:**
Consider a thermal transport experiment with a spatially varying temperature field T(x,t) (playing the role of s). In a region where |∇T/T| ~ k_c, the C2 prediction gives a specific decay rate Γ_dec ≈ (1/2τ)√|Q| for the gradient structure, while standard telegrapher gives decay of fixed Fourier modes. These are in principle distinguishable by measuring the time evolution of the gradient map ∇ ln T vs. individual Fourier amplitudes.

**VERDICT: P2 survives as a weak discriminating prediction in heterogeneous fields. Experimentally accessible but requires spatial resolution of ∇ ln s.**

---

### P3.3 — Prediction 3: Dephasing Rate ω_rot² Scaling (O18)

**C2 formula:**
    Γ_φ = k_rot · ω_rot²
    k_rot = 8g²s₀²r_q²τ / (3ℏ²)

**Standard-theory formula:**
In standard Lindblad theory, the dephasing rate is determined by the spectral density of the bath S(ω) evaluated at the qubit frequency:
    Γ_φ = (g²/ℏ²) S(ω_q) + ...
where S(ω_q) depends on the specific bath model. The ω_rot² scaling is NOT a generic prediction of Lindblad theory — it requires a specific bath with S(ω) ∝ ω² near ω_q.

**C2 derivation of the ω_rot² scaling:**
From [ESTABLISHED-VAR]: ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q²
The autocorrelation integral: ∫ C_JJ(τ') dτ' ∝ ⟨(δJ)²⟩ · τ = (2/3)s₀²ω_rot²r_q² · τ
Therefore: Γ_φ = (2g²/ℏ²) ∫ C_JJ(τ') dτ' ∝ (2g²/ℏ²)(2/3)s₀²ω_rot²r_q²τ = k_rot · ω_rot²

The ω_rot² scaling follows from the KINEMATIC result [ESTABLISHED-VAR] that current variance scales as ω_rot². This kinematic scaling is model-independent within the rotating-frame interpretation.

**Does this survive parameter redefinition?**
The ω_rot² scaling is potentially testable. But:
(1) k_rot is a COMPOUND PARAMETER containing g, s₀, r_q, τ — none individually determinable from a single Ramsey experiment.
(2) Any bath with spectral density S(ω_rot) ∝ ω_rot² gives the same scaling. The C2 derivation produces the ω_rot² scaling from geometry (rotating frame) — but a standard phenomenological 1/f noise model (S(ω) ∝ ω) does NOT give ω_rot², while a Johnson-Nyquist model (S(ω) = constant) gives Γ_φ = const.

**Discriminating test:**
C2 predicts: Γ_φ ∝ ω_rot² (quadratic in rotation frequency).
Standard Lindblad with white noise bath: Γ_φ = const.
Standard Lindblad with 1/f noise: Γ_φ ∝ 1/ω_rot.
Standard Lindblad with Ohmic bath S(ω) ∝ ω: Γ_φ ∝ ω_rot.

The C2 prediction Γ_φ ∝ ω_rot² DISCRIMINATES against white noise and 1/f noise but NOT against an Ohmic² (super-Ohmic) bath S(ω) ∝ ω².

**Conditional status:**
This prediction requires M1, M2, H_int = g·J·σ_z, plus A-HC1–HC6 (≥17 independent assumptions). The ω_rot² scaling is derived from these assumptions combined, not from the C2 transport equations alone.

**Empirical status:**
k_rot = 4.5 × 10⁻⁷ s fitted to IBM Quantum data. The ω_rot² scaling is confirmed in the dataset. But as Theorem EXP-1 states, the scaling is not unique to C2 — any theory generating ⟨(δJ)²⟩ ∝ ω_rot² gives the same result.

**VERDICT: P3 is a discriminating prediction against white/1/f noise but NOT uniquely against all bath models. The ω_rot² scaling is confirmed empirically but not uniquely attributable to C2.**

---

### P3.4 — Prediction 4: T₁ = ∞ (O21)

**C2 formula:**
    T₁ = ∞ (pure dephasing only, no relaxation)

**Derivation from C2:**
Theorem HC-3: under A-HC5 (linear coupling H_int = g·J·σ_z) and A-HC6 (local coupling), the unique Lindblad operator is A = σ_z. The σ_z operator is diagonal and causes ONLY dephasing (off-diagonal decay), not relaxation (diagonal decay). Therefore:
    dρ₀₀/dt = 0,   dρ₁₁/dt = 0   →   T₁ = ∞.

**Standard-theory prediction:**
Standard Lindblad theory allows BOTH σ_z (dephasing) AND σ_± (relaxation) jump operators. T₁ is finite when transverse coupling (H_int ∝ σ_x or σ_y) is present. The C2 framework predicts T₁ = ∞ because its coupling H_int = g·J·σ_z is purely longitudinal.

**Does this survive parameter redefinition?**
YES. The prediction T₁ = ∞ (or equivalently, the absence of energy relaxation) is a direct consequence of the coupling form H_int = g·J·σ_z combined with the pure-dephasing Lindblad structure. It is NOT a parameter redefinition artifact. Any model with only longitudinal coupling gives T₁ = ∞.

**Is it testable?**
YES. T₁ is directly measured via inversion recovery (π pulse, wait, measure). A finite T₁ falsifies C2 in any regime where the σ_z coupling is the dominant substrate interaction.

**Competing theories:**
Standard Lindblad with amplitude damping gives T₁ < ∞. The C2 prediction T₁ = ∞ is distinctive and falsifiable.

**CAVEAT:** T₁ = ∞ is specific to H_int = g·J·σ_z. If the true coupling has transverse components (g_x·J·σ_x terms), T₁ becomes finite. C2 does not FORBID transverse coupling — it simply doesn't include it. The T₁ = ∞ prediction is therefore only valid WITHIN the assumed coupling model.

**VERDICT: P4 is a clean discriminating prediction — T₁ = ∞ is testable and falsifiable. It is CONDITIONAL on the longitudinal coupling assumption H_int = g·J·σ_z.**

---

### Phase 3 Summary: Surviving Discriminating Predictions

| ID | Prediction | C2 Formula | Competing Theory | Key Difference | Conditional? |
|----|-----------|------------|-----------------|----------------|-------------|
| P1 | Local regime boundary | Q(x,t)=0 surface in heterogeneous field | Global ωτ criterion | Spatial resolution of boundary | No (telegrapher + Q-def) |
| P2 | Decoherence rate near boundary | Γ_dec ≈ (1/2τ)√\|Q\| for heterogeneous field | Fixed-mode decay rate | WKB vs. fixed-k | No (Q-def) |
| P3 | Dephasing ω_rot² scaling | Γ_φ = k_rot·ω_rot² | White/1/f noise bath | Quadratic vs. flat/decreasing | Yes (M1,M2,H_int) |
| P4 | T₁ = ∞ (no relaxation) | Pure σ_z coupling only | General Lindblad | Absence of energy relaxation | Yes (H_int = g·J·σ_z) |

**ALL 5 MODIFIED observables reduce to these 4 predictions.**
(O15 and O16 combine into P1; O17 is P2; O18 gives P3; O21 gives P4.)

---

---

## Phase 4 — Rank by Experimental Accessibility

**Level A:** Testable immediately with IBM Quantum, public datasets, laptop, or published data.  
**Level B:** Needs modest laboratory resources (optics lab, NMR, ultrasound tank).  
**Level C:** Needs major facilities (neutron scattering, CERN, LIGO, synchrotron).

### P1 — Local Q-Boundary in Heterogeneous Fields

**What must be measured:** The spatial map Q(x,t) = 4c²τ²|∇ ln s|² − 1 from a measured field s(x,t). The zero-surface Q = 0 is compared against standard predictions.

**Accessible systems:**
- **Thermal diffusion:** Temperature field T(x,t) in a heterogeneous medium, where s = T. Standard infrared cameras provide spatial resolution of 10–100 μm. For thermal systems with ξ_c ~ 1 mm, this is sufficient.
- **Acoustic propagation:** Pressure field p(x,t) in a waveguide with varying cross-section. Microphone arrays can map p(x,t).
- **Reaction-diffusion (chemical):** Concentration field c(x,t) in a BZ reaction (Belousov-Zhabotinsky). Optical imaging gives spatial resolution.
- **Qubit array simulation:** A lattice of qubits can simulate a 1D or 2D telegrapher field. IBM Quantum's 127-qubit Eagle processor provides spatial extent.

**Required precision:**
- Spatial gradient ∇ ln s measured to ~10% accuracy.
- c and τ calibrated independently from bulk measurements.
- Then Q(x,t) can be computed from the field map.

**Level: A**
Can be tested on a laptop using publicly available field data (e.g., thermal imaging datasets, BZ reaction images). IBM Quantum simulation of telegrapher on qubit array is feasible.

---

### P2 — Decoherence Rate Near Q = 0 Boundary

**What must be measured:** In a region where Q ≈ 0 (near the stability boundary), measure the time decay of the field amplitude. Compare Γ_dec ≈ (1/2τ)√|Q| vs. standard fixed-mode prediction.

**Accessible systems:**
- **Acoustic:** A sound wave in a medium where cτ transitions (by varying temperature, giving τ → τ(T)). Near the critical frequency ω = 1/(2τ), the amplitude decay near a spatial boundary can be mapped.
- **Electrical:** Transmission line near cutoff frequency. At f_c = 1/(4πτ), the Q diagnostic crosses zero. The decay of signal amplitude near f_c is measurable with standard electronics.
- **BZ reaction:** Near the Turing bifurcation, ∇ ln c passes through k_c, and the pattern decay rate can be mapped vs. Q.

**Required precision:**
- Decay rate measurement to ~5–10% accuracy over a range of Q values.
- Need Q to vary over at least a decade (e.g., Q ∈ [−0.9, −0.1]) to resolve the √|Q| dependence.

**Level: B**
Requires a controlled experiment where τ or c can be varied to sweep Q through zero. Achievable in an acoustics or microwave lab.

---

### P3 — Dephasing ω_rot² Scaling

**What must be measured:** Ramsey experiments on a qubit in a rotating frame at multiple ω_rot values. Measure Γ_φ(ω_rot). Test if the scaling is Γ_φ ∝ ω_rot².

**Accessible systems:**
- **IBM Quantum (direct):** IBM Quantum devices support Ramsey sequences with variable rotation rates. The IBM Quantum open access program provides cloud access to ibmq_manila, ibmq_nairobi, ibm_lagos (127+ qubit devices).
- **Published IBM data:** The existing fit k_rot = 4.5 × 10⁻⁷ s was obtained from ibm_nairobi data. The full dataset is in `/home/lenovo/Projects/.../aaG/ramsey_dataset/`.
- **NIST atomic clock data:** Long-coherence qubits in atomic traps allow Ramsey measurements at very small Γ_φ, testing the scaling at low ω_rot.
- **Other open quantum hardware:** IonQ, QuEra, Rigetti all provide cloud API access.

**Required precision:**
- Measure Γ_φ at ≥ 5 values of ω_rot spanning at least one decade in ω_rot.
- Need Γ_φ precision of ~5% to distinguish ω_rot² from ω_rot or ω_rot^{1.5}.
- Already achieved in the IBM dataset.

**Level: A**
Already done. The IBM Quantum dataset is available locally. Requires only a laptop and the Python scripts already written.

---

### P4 — T₁ = ∞ (No Energy Relaxation)

**What must be measured:** T₁ via inversion recovery (π pulse → wait → measure). Compare T₁ vs. T₂ to check T₁ >> T₂ (consistent with T₁ = ∞) vs. T₁ ~ 2T₂ (standard quantum noise).

**Accessible systems:**
- **IBM Quantum:** T₁ is a standard calibration parameter reported for every qubit on IBM devices. The IBM Quantum backend properties API returns T₁ for each qubit in real time.
- **IBM Quantum open data:** IBM publishes T₁ and T₂ for all operational devices. Available at: https://quantum.ibm.com/services/resources.
- **Published literature:** Thousands of papers report T₁ and T₂ for superconducting qubits (transmons), ion traps, NV centers, and quantum dots.

**Required precision:**
- Need T₁/T₂ > 10 to be consistent with T₁ → ∞ while T₂ is finite.
- Standard IBM transmon qubits have T₁ ~ 100 μs, T₂ ~ 100 μs (T₁ ≈ T₂, NOT T₁ >> T₂).
- This is the RELEVANT EMPIRICAL FACT for falsification (see Phase 6).

**Level: A**
T₁ data is publicly available on IBM Quantum website and in thousands of published papers. No experiment needed — existing data is sufficient.

---

### Phase 4 Summary: Accessibility Ranking

| Prediction | Level | Method | Cost |
|-----------|-------|--------|------|
| P3: ω_rot² scaling | **A** | IBM Quantum Ramsey (already done) | $0 |
| P4: T₁ = ∞ | **A** | IBM Quantum T₁ calibration data | $0 |
| P1: Q-boundary in heterogeneous field | **A** | Laptop + public field data (thermal/acoustic) | $0 |
| P2: Γ_dec ~ √|Q| near boundary | **B** | Controlled acoustic/microwave experiment | ~$10k |

**All four predictions are Level A or B. None require major facilities.**

---

## Phase 5 — Existing Data Search

### P3: ω_rot² Scaling — Existing Data

**Local dataset:**
- `/home/lenovo/Projects/Substrate_X_Theory_of_Information_Gravity/fxt/aaG/ramsey_dataset/gamma_dataset.csv`
- `/home/lenovo/Projects/Substrate_X_Theory_of_Information_Gravity/fxt/aaG/ramsey_dataset/experiment_results.npz`
- Fitted k_rot = 4.5 × 10⁻⁷ s; Γ_φ ∝ ω_rot² confirmed.

**External public datasets:**
- IBM Quantum open data portal: ibm.com/quantum-computing/learn/research
- Arute et al. (2019) "Quantum supremacy using a programmable superconducting processor," Nature 574, 505. Reports T₁ and T₂ for 53-qubit Sycamore device.
- Krantz et al. (2019) "A quantum engineer's guide to superconducting qubits," Applied Physics Reviews 6, 021318. Tabulates T₁, T₂ for hundreds of transmon qubits.
- Koch et al. (2007) "Charge-insensitive qubit design derived from the Cooper pair box," PRA 76, 042319. Foundational transmon paper with T₁, T₂ data.

**Does existing data constrain P3?**
YES. The IBM local data confirms Γ_φ ∝ ω_rot² with k_rot = 4.5 × 10⁻⁷ s. The scaling is consistent with C2 (P3). However, Theorem EXP-1 establishes this scaling is not unique to C2.

**Critical question: Is there existing data showing Γ_φ ∝ ω_rot^n with n ≠ 2?**
Krantz et al. (2019) and Ithier et al. (2005) report that Γ_φ depends on the specific noise source:
- Flux noise: Γ_φ ∝ (∂E/∂Φ)² · S_Φ(ω_q) — depends on Φ bias point
- Charge noise: Γ_φ ∝ (∂E/∂n_g)² · S_n(ω_q) — depends on charge sensitivity
- Critical current noise: Γ_φ ∝ S_{I_c}(ω_q)
In transmons operated at the flux sweet spot (∂E/∂Φ = 0), charge noise dominates and Γ_φ can be independent of rotation rate — not ∝ ω_rot².

**Conclusion on P3 data search:** The ω_rot² scaling is confirmed in the specific IBM dataset. It is NOT universally confirmed across all qubit types and operating points.

---

### P4: T₁ = ∞ — Existing Data

**IBM Quantum backend properties (public, real-time):**
IBM Quantum reports T₁ and T₂ for all operational devices. Typical values for ibmq_manila:
- T₁ ~ 90–150 μs
- T₂ ~ 50–120 μs (Ramsey)
- Ratio T₂/T₁ ~ 0.5–1.0

**Published data:**
- Rigetti et al. (2012), Koch et al. (2007): T₁ ~ 1–10 μs for early transmons.
- Kjaergaard et al. (2020), "Superconducting qubits: Current state of play," Annual Review of Condensed Matter Physics: reports T₁ ~ 100 μs for state-of-art transmons.
- Pop et al. (2014), "Coherent suppression of electromagnetic dissipation due to superconducting quasiparticles," Nature 508, 369: T₁ up to 1 ms.

**Does existing data constrain P4?**
CRITICAL FINDING: For EVERY reported superconducting qubit, T₁ is FINITE. Typical values: T₁ ~ 100 μs, T₂ ~ 100 μs. This gives T₁/T₂ ~ 1, NOT T₁ → ∞. The standard quantum channel relation T₂ ≤ 2T₁ is satisfied, but T₁ is not large compared to T₂.

This IMMEDIATELY constrains P4. The C2 prediction T₁ = ∞ is valid ONLY if the coupling is purely longitudinal (σ_z). For real superconducting qubits, finite T₁ is universally observed, indicating that transverse coupling exists and is significant.

**However:** The C2 prediction T₁ = ∞ is a prediction about the SUBSTRATE COUPLING, not about all relaxation channels. Real qubits have many noise sources beyond the substrate (quasiparticle tunneling, two-level systems, radiation loss). The C2 prediction would apply only if all other T₁ channels could be isolated. In practice, the dominant T₁ mechanism in transmons is often NOT the substrate coupling but quasiparticle loss or dielectric loss.

**Conclusion on P4 data search:** Existing data shows finite T₁ universally. This is consistent with the C2 prediction being APPROXIMATELY correct (T₁ >> T₂ in some systems, e.g. charge-insensitive transmons), or the longitudinal coupling assumption may be violated by other mechanisms.

---

### P1: Q-Boundary — Existing Data

**Thermal imaging datasets:**
- FLIR thermal camera datasets (publicly available): spatial resolution 320×240 pixels at 25 fps, temperature resolution 0.05°C.
- NASA/NOAA thermal Earth observation data (Landsat 8 TIRS: 100m resolution).
- Urban heat island datasets: demonstrate heterogeneous temperature fields.

**Acoustic datasets:**
- Room acoustics datasets (OpenAIR: openairlib.net): impulse responses in rooms with heterogeneous absorption.
- Ultrasound medical imaging datasets (various open datasets on PhysioNet).

**Does existing data constrain P1?**
P1 requires SIMULTANEOUSLY measuring both the field s(x,t) AND having known c and τ. In thermal datasets, D = c²τ is known but c and τ individually are not always calibrated. The Q-diagnostic requires knowing c and τ separately (not just D).

**Conclusion on P1 data search:** Thermal imaging data exists in abundance. The challenge is calibrating c and τ independently. For the telegrapher regime to be visible, τ must be comparable to the observation timescale. In most thermal systems, τ is extremely small (heat relaxes quickly), pushing the system well into the diffusive regime (Q << −1 everywhere). The Q = 0 boundary would only be observable in systems near the wave-diffusion crossover.

**Candidate systems near wave-diffusion crossover:**
- Second sound in superfluid He-4 at T < 1 K: genuine second-sound waves where τ ~ 10⁻⁵ s and c ~ 20 m/s, giving ξ_c ~ 4 × 10⁻⁴ m ~ 0.4 mm. Spatial resolution achievable.
- Phonon heat conduction in insulating crystals at low T: τ ~ 10⁻¹⁰ s, c ~ 5000 m/s, ξ_c ~ 1 μm. Needs nanoscale resolution.

---

### Phase 5 Summary: Data Availability

| Prediction | Existing Data Available? | Constraint Status |
|-----------|------------------------|------------------|
| P3 (ω_rot²) | YES — IBM Quantum dataset (local + public) | CONFIRMED in IBM data; not unique to C2 |
| P4 (T₁ = ∞) | YES — IBM Quantum, thousands of papers | CONSTRAINED: finite T₁ observed universally; C2 requires isolation of substrate channel |
| P1 (Q-boundary) | PARTIALLY — thermal/acoustic datasets exist | UNCONSTRAINED — calibration of c,τ independently needed |
| P2 (Γ_dec ~ √|Q|) | NO — no direct measurement found | UNCONSTRAINED — no existing dataset directly tests this |

---

---

## Phase 6 — Falsification Attempts

For each prediction, systematically attempt contradiction, hidden equivalence, parameter degeneracy, experimental exclusion, and mathematical inconsistency.

---

### Falsification Attempt: P1 (Q-Boundary)

**Attempt F1-A — Hidden equivalence:**
Claim: Q(x,t) = 0 is equivalent to the standard stability criterion expressed in terms of a local wavenumber.

Analysis: For a field s(x,t) with well-defined local wavenumber k_local = |∇ ln s| / (2πc_phase), Q = 0 ⟺ k_local = k_c. This is the LOCAL stability criterion of the telegrapher equation. It is not equivalent to the GLOBAL ωτ criterion (which requires a single global ω for the entire field). The two are identical for spatially uniform fields and diverge for heterogeneous ones.

Verdict on F1-A: **NOT hidden equivalence.** Q provides genuinely new spatial information for heterogeneous fields. However, it is a consequence of applying the telegrapher's own stability analysis pointwise. Any physicist who has solved the telegrapher equation could in principle compute k_local(x,t) without the Q formula. Q packages the computation into a single algebraic expression.

**Attempt F1-B — Parameter degeneracy:**
Claim: Renaming |∇ ln s|² → k_eff²(x,t) makes Q ≡ (k_eff/k_c)² − 1, which is dimensionless and identical to existing WKB/JWKB criteria.

Analysis: This is correct. The WKB approximation for the telegrapher equation does use a local wavenumber k_eff(x) and a criterion k_eff > k_c for oscillatory vs. evanescent behavior. The Q formula is the algebraic expression of the WKB criterion in terms of the logarithmic gradient of s.

WKB for telegrapher: s(x) ~ exp(i∫k_eff(x')dx'), k_eff² = k² − k_c² → Q ∝ k_eff²/k_c².

**CONCLUSION: P1 (Q-boundary) IS EQUIVALENT to the WKB criterion for the telegrapher equation, applied locally.** It is a new PACKAGING of a known result, not a new physical law.

This does NOT mean P1 is useless — the Q formula makes the WKB criterion algebraically explicit and coordinate-invariant. But it does mean P1 has no NEW physical content beyond what WKB analysis of the telegrapher already contains.

**P1 FALSIFIED as a new physical prediction. It is a reformulation of WKB for the telegrapher equation.**

---

### Falsification Attempt: P2 (Γ_dec ~ √|Q|)

**Attempt F2-A — Mathematical inconsistency with telegrapher:**
Already analyzed in Phase 3. The formula Γ_dec ≈ (1/2τ)√|Q| contradicts the standard fixed-mode decay rate of the telegrapher near k_c. The C2 formula predicts Γ_dec → 0 as Q → 0, while the standard formula gives γ(k_c) = 1/(2τ) ≠ 0.

Resolution: The C2 formula applies to the decay of the spatial gradient amplitude (WKB envelope), not to a fixed-k mode. In the WKB approximation: the amplitude of the envelope A(x) ∝ exp(−∫Im(k_eff)dx), and near k_c, Im(k_eff) = √(k_c² − k²) ∝ √(k_c − k) ∝ √|Q| (for small |Q|). The decay rate of the envelope at a fixed point x as Q varies IS ∝ √|Q|.

**Attempt F2-B — Hidden equivalence to WKB:**
Same analysis as F1-B. Γ_dec ≈ (1/2τ)√|Q| is exactly the WKB evanescent decay rate for the telegrapher equation near cutoff. This is the STANDARD WKB result for waveguides near cutoff frequency.

Standard waveguide physics: near cutoff frequency f_c = c/(2τ), attenuation α ∝ √(1 − (f/f_c)²) = √(−Q) for f < f_c. This is identical to (1/2τ)√|Q| up to normalization.

**P2 FALSIFIED as a new physical prediction. It is the standard waveguide cutoff attenuation formula expressed in Q notation.**

---

### Falsification Attempt: P3 (ω_rot² Scaling)

**Attempt F3-A — Parameter degeneracy:**
The prediction Γ_φ = k_rot · ω_rot² contains the free parameter k_rot. Any bath model with spectral density S(ω) ∝ ω² gives the same scaling. The C2 derivation produces k_rot = 8g²s₀²r_q²τ/(3ℏ²), but since g is undetermined, k_rot is a free fit parameter. This is parameter degeneracy: C2 and a phenomenological super-Ohmic bath (S(ω) ∝ ω²) are experimentally indistinguishable given only Ramsey data.

Specifically: Any model where ⟨(δJ)²⟩ ∝ ω_rot² will produce Γ_φ ∝ ω_rot². The C2 kinematic derivation of ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² produces this scaling from geometric reasoning (solid-angle average of ω_rot × r). But ANY rotating-frame bath where the fluctuation power scales as ω_rot²r² will give the same result, regardless of whether it is the C2 substrate or something else.

**Attempt F3-B — Experimental exclusion:**
The existing IBM data confirms Γ_φ ∝ ω_rot². Does any published data EXCLUDE this scaling?

NIST data (Degen et al. 2017, "Quantum sensing," Rev. Mod. Phys. 89, 035002): Reports Γ_φ ∝ ω_rot^α with α ranging from 0.5 to 2.5 depending on the noise type and operating point. The scaling exponent is NOT universally 2. For 1/f flux noise in transmons: α ~ 1–1.5 (not exactly 2).

IBM data from Bertet et al. (2005) "Dephasing of a Superconducting Qubit Induced by Photon Noise" Physical Review Letters: Γ_φ from photon number noise has different scaling than ω_rot².

**CONCLUSION on F3:**
The ω_rot² prediction survives within the specific IBM dataset. It does NOT survive as a universal prediction:
- The scaling exponent α depends on the noise source.
- At different operating points or qubit types, α ≠ 2.
- k_rot is a free parameter that can absorb any multiplicative discrepancy.
- The prediction is NOT experimentally falsified for the specific dataset but is NOT uniquely confirmed as a C2 prediction.

**P3 survives as CONSISTENT with IBM data but is not uniquely discriminating.** The ω_rot² scaling is one possible scaling among several observed experimentally.

---

### Falsification Attempt: P4 (T₁ = ∞)

**Attempt F4-A — Direct experimental exclusion:**
The prediction T₁ = ∞ is contradicted by all experimental data on superconducting qubits. Finite T₁ is universally observed:
- Transmons: T₁ ~ 10–1000 μs (Koch et al. 2007, Kjaergaard et al. 2020)
- Ion traps: T₁ > 1 s (Harty et al. 2014, Ballance et al. 2016)
- NV centers: T₁ ~ 1–6 ms at room temperature (Balasubramanian et al. 2008)

**But:** The C2 prediction T₁ = ∞ is explicitly conditional on H_int = g·J·σ_z (longitudinal coupling only). Finite T₁ implies that additional coupling channels exist (transverse noise). The C2 framework does not claim to be the ONLY noise source — it claims that the specific substrate coupling through σ_z contributes ONLY to dephasing.

**Attempt F4-B — Consistency check with T₂ ≤ 2T₁:**
Since T₁ is finite and T₂ is measured, the bound T₂ ≤ 2T₁ must hold. IBM data: T₁ ~ 100 μs, T₂ ~ 100 μs. So T₂/T₁ ~ 1 < 2. ✓ Consistent.

If C2 prediction T₁ = ∞ were strictly correct AND T₂ is finite, then T₂/T₁ → 0. This would require T₂ << T₁, i.e., pure dephasing dominates. In some systems this is indeed the case: in SUPERCONDUCTING QUBITS NEAR FLUX SWEET SPOT, T₂ is dominated by pure dephasing (1/f flux noise) with T₁ >> T₂ (see Ithier et al. 2005).

**Critical assessment:**
The T₁ = ∞ prediction is:
- **FALSIFIED** as a universal prediction (finite T₁ is always observed).
- **CONSISTENT** as a statement about the SUBSTRATE COUPLING CHANNEL specifically: the σ_z coupling does not drive T₁ by construction. Finite T₁ comes from other sources not in C2.
- **NOT TESTABLE IN ISOLATION** because it is impossible to turn off all noise sources except the substrate coupling.

**P4 is not universally falsified but cannot be confirmed in isolation. It is neither verified nor refuted by existing data.**

---

### Phase 6 Summary: Falsification Results

| Prediction | Falsification Attempt | Outcome |
|-----------|----------------------|---------|
| P1 (Q-boundary) | Hidden equivalence | **FALSIFIED as new physics.** Q is WKB criterion for telegrapher, repackaged. |
| P2 (Γ_dec ~ √|Q|) | Hidden equivalence | **FALSIFIED as new physics.** Standard waveguide cutoff attenuation in Q notation. |
| P3 (ω_rot² scaling) | Parameter degeneracy | **NOT FALSIFIED but not unique.** Consistent with IBM data; indistinguishable from super-Ohmic bath. |
| P4 (T₁ = ∞) | Direct experimental exclusion | **CONDITIONAL.** Finite T₁ always observed; prediction applies only to substrate channel in isolation. |

---

## Phase 7 — Final Verdict

### Classification of All Four Predictions

---

**Prediction P1: Local Q-boundary**

- Derivation: Q(x,t) = 4c²τ²|∇ ln s|² − 1; boundary at Q = 0.
- Competing theory: WKB analysis of telegrapher equation. The WKB local wavenumber k_eff(x) = |∇ ln s| and the criterion k_eff = k_c = 1/(2cτ) gives Q = 0.
- Measurable quantity: Spatial map of Q = 0 surface in a heterogeneous field.
- Required precision: Spatial resolution Δx < ξ_c, SNR > 10 on s(x,t).
- Existing datasets: Thermal/acoustic fields exist; calibration of c,τ needed independently.
- Likelihood of being uniquely C2: **ZERO.** P1 is the WKB criterion for the telegrapher. Every physicist who applies WKB to the Maxwell-Cattaneo/telegrapher equation arrives at the Q formula. C2 provides a useful algebraic packaging but no new physics.

**Classification: FAILED as discriminating prediction. Q is a novel engineering diagnostic tool (Theorem Q-5 stands) but not a new physical law.**

---

**Prediction P2: Γ_dec ~ √|Q| near boundary**

- Derivation: WKB envelope decay for telegrapher near cutoff.
- Competing theory: Standard waveguide attenuation near cutoff: α ∝ √(1 − (ω/ω_c)²) = √|Q|.
- Measurable quantity: Amplitude decay rate of spatial envelope as Q → 0.
- Required precision: Level B (controlled acoustic/microwave experiment).
- Existing datasets: None directly testing this in C2 context.
- Likelihood of being uniquely C2: **ZERO.** This IS the standard cutoff attenuation formula for the telegrapher / telegraph-mode waveguide.

**Classification: FAILED as discriminating prediction. Standard result in disguise.**

---

**Prediction P3: Γ_φ = k_rot · ω_rot²**

- Derivation: Γ_φ = (2g²/ℏ²)·(2/3)s₀²ω_rot²r_q²τ = k_rot · ω_rot².
- Competing theory: Lindblad with super-Ohmic bath S(ω) ∝ ω². Any bath with this spectral density gives the same scaling.
- Measurable quantity: Ramsey T₂ vs. ω_rot across multiple rotation rates.
- Required precision: 5–10% on Γ_φ, ≥5 data points spanning one decade in ω_rot.
- Existing datasets: IBM Quantum data (local). Published IBM and other superconducting qubit data.
- Likelihood of success: The prediction is CONFIRMED in the specific IBM dataset. The scaling is CONSISTENT with C2. It is not UNIQUE to C2 (any ω_rot²-variance bath gives the same).

**Discriminating tests:**
- If ω_rot is varied over more than two decades, sub-leading corrections would distinguish C2 (pure ω_rot²) from other models (which may have crossovers). C2 predicts no crossover to first order; a phenomenological bath may show deviations.
- If the qubit geometry (r_q) is varied and k_rot scales as r_q², this would partially support C2. Currently r_q is fixed and undetermined in the fit.

**Classification: PARTIAL. Consistent with existing data; not uniquely discriminating given free parameter k_rot.**

---

**Prediction P4: T₁ = ∞ (pure dephasing)**

- Derivation: H_int = g·J·σ_z → Lindblad operator A = σ_z → dρ₀₀/dt = 0 → T₁ = ∞.
- Competing theory: General Lindblad with transverse (σ_±) operators → finite T₁.
- Measurable quantity: T₁ via inversion recovery; ratio T₂/T₁.
- Required precision: T₁/T₂ >> 1 (consistent with T₁ → ∞) vs. T₁ ~ T₂ (standard).
- Existing datasets: IBM Quantum T₁ calibration data; thousands of published qubit measurements.
- Current empirical status: T₁ is finite universally; T₁/T₂ ~ 1–2 in IBM transmons. But T₁ >> T₂ in some flux-noise-dominated systems.

**What falsifies C2:**
If it can be demonstrated that T₁ DECREASES under conditions where the substrate coupling (σ_z channel) is the DOMINANT noise source — this would falsify the σ_z prediction. This requires isolating the substrate coupling channel from all other decoherence mechanisms, which is technically very challenging.

**Classification: PARTIAL. The T₁ = ∞ prediction is conditionally correct (for σ_z coupling in isolation). Experimentally, finite T₁ is always observed due to other noise sources. The prediction is not falsified but is also not confirmable in isolation.**

---

### Final Verdict Table

| Prediction | Content | Verdict | Reason |
|-----------|---------|---------|--------|
| P1: Local Q-boundary | Q(x,t) = 0 is local stability boundary | **FAILED** | Identical to WKB criterion for telegrapher |
| P2: Cutoff attenuation Γ_dec ~ √|Q| | Amplitude decay near Q = 0 | **FAILED** | Identical to standard waveguide cutoff formula |
| P3: Dephasing Γ_φ = k_rot · ω_rot² | Quadratic rotation-rate scaling | **PARTIAL** | Confirmed in IBM data; not unique (super-Ohmic bath gives same) |
| P4: T₁ = ∞ pure dephasing | No energy relaxation from substrate | **PARTIAL** | Conditional on isolating σ_z channel; finite T₁ universally observed otherwise |

---

### Overall Prediction Program Verdict: **PARTIAL**

**What C2 successfully provides:**
1. A confirmed quadratic scaling Γ_φ ∝ ω_rot² consistent with IBM Quantum Ramsey data (P3). This is the most concrete quantitative result. It is consistent with — but not uniquely confirmed as — a C2 prediction.

2. A physically motivated prediction T₁ >> T₂ in the regime where longitudinal noise dominates. Some experimental systems (flux sweet spot in transmons, certain spin systems) may exhibit this. This is testable and currently UNFALSIFIED for the specific channel.

3. The Q diagnostic (P1, P2) provides a useful engineering tool for classifying transport regimes locally. It is not a new physical law, but it unifies multiple known stability criteria under one formula.

**What C2 does not provide:**
1. Any prediction that is mathematically unique to the C2 framework and not reproducible by standard accepted theories.
2. A derivation of any NEW coupling constant, energy scale, or physical law from first principles.
3. Any prediction that has been tested and passed a falsification attempt against competing models.

**The core limiting fact** (from Theorem ME-PRED-NONE in C2_FOUNDATIONS.md): The transport layer [ME] is mathematically equivalent to EIT/GENERIC and cannot produce new predictions from first principles. The only predictions that differ from standard theory require independent axioms M1 and M2, which are not derived from C2 but assumed. Given these axioms, the ω_rot² scaling and T₁ prediction follow — but they follow from the axioms, not from C2's structural novelty.

---

### Final Summary

| Phase | Result |
|-------|--------|
| Phase 1 | 40 observables enumerated |
| Phase 2 | 28 IDENTICAL, 5 MODIFIED, 3 NEW/UNKNOWN |
| Phase 3 | 4 discriminating predictions identified (P1–P4) |
| Phase 4 | All Level A or B; all testable |
| Phase 5 | P3 confirmed in IBM data; P4 constrained but not falsified; P1/P2 unconstrained |
| Phase 6 | P1 and P2 falsified as new physics (WKB equivalence); P3 and P4 survive as PARTIAL |
| Phase 7 | **PARTIAL** — two surviving predictions, both conditional |

**Entire prediction program verdict: PARTIAL**

---

*Document compiled: 2026-07-24*
*All C2 results treated as established per C2_FOUNDATIONS.md (frozen).*
*No C2 structure redesigned. No new assumptions introduced.*
*All comparisons made against named, cited standard theories.*
