# GATE 0 — Theory Audit: C2 Substrate Project
## Spatiotemporal C2 Decoherence Test

**Date:** 2026-08-20  
**Auditor:** gate0_audit (adversarial session)  
**Working directory:** `fxt/`  
**Status:** ADVERSARIAL — all claims tested against source derivations  

**Label convention:**
- `DERIVED` — proven from stated premises by explicit algebraic or differential steps
- `ASSUMED` — stated without derivation; accepted as axiom or physical postulate
- `FITTED` — parameter adjusted to match empirical data
- `EMPIRICAL` — value read from experiment, no derivation attempted
- `UNKNOWN` — neither derived nor empirically pinned; free parameter

**Source files read for this audit:**
- `01_foundations/C2_FOUNDATIONS.md`
- `01_foundations/C2_FRONTIER_MAP.md`
- `01_foundations/C2_MISSING_PRINCIPLES.md`
- `02_derivations/prw_01_cjj_derivation.py` (full)
- `02_derivations/prw_02_spatial_correlator.py` (full)
- `02_derivations/microscopic_derivation.md` (first 150 lines)
- `02_derivations/substrate_transport_derivation.md` (first 150 lines)
- `02_derivations/decoherence_chain_summary.md` (first 100 lines)
- `02_derivations/interaction_hamiltonian_derivation.md` (first 100 lines)
- `11_v02_extension/NM_PREDICTION_AUDIT.md` (full)
- `11_v02_extension/nm_01_memory_kernel.py` (first 60 lines)
- `03_audits/C2_final_prediction_audit.md` (first 100 lines)
- `10_stress_tests/STRESS_TEST.md` (full)
- `06_datasets/` (directory listing)
- `check` (root file)

**Script run:** `python 02_derivations/prw_01_cjj_derivation.py`  
Output confirmed: Lorentzian spectrum, τ_B = 1/(2λ), two PASS verifications.

---

## SECTION 1 — Equations Actually Derived (With Proof Chain)

Every item here has a complete algebraic chain traceable to explicit steps in the source files.

---

### 1.1 PRW Balance Equations → Telegrapher Equation

**Status: DERIVED**

**Proof chain** (microscopic_derivation.md §1.2–1.5; substrate_transport_derivation.md §2):

1. *Microscopic rules*: discrete lattice, step size h, time step Δt, speed v = h/Δt, reversal rate λ. Exact balance equations:
   ```
   ∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻
   ∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻
   ```

2. *Define macroscopic fields*: s = n⁺ + n⁻, q = v(n⁺ − n⁻). Add and subtract the balance equations:
   ```
   ∂s/∂t = −∂q/∂x                    [C-s]
   ∂q/∂t = −v² ∂s/∂x − 2λ q         [C-q]
   ```
   These are exact; no approximation yet.

3. *Eliminate q*: Differentiate [C-s] in t, substitute [C-q] into ∂q/∂t, use [C-s] to replace ∂q/∂x:
   ```
   ∂²s/∂t² + 2λ ∂s/∂t = v² ∂²s/∂x²
   ```

4. *Parameter identification*: τ = 1/(2λ), c = v, D = c²τ. Rewrite:
   ```
   τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s      [TEL]  ← DERIVED
   ```

**What is established:** The 1D telegrapher equation follows exactly from the PRW balance equations. No approximation is needed. This is the Goldstein-Kac result (1951/1974) [KR].

**What is NOT established:** The 3D generalization; the case of non-uniform λ(x,t).

---

### 1.2 BGK (Diffusion) Limit

**Status: DERIVED** (conditional on τ → 0 with D = c²τ fixed)

From [TEL]: in the limit τ → 0, the term τ ∂²s/∂t² → 0, leaving:
```
∂s/∂t = D ∇²s,    D = c²τ           [DIFF]  ← DERIVED (limit of TEL)
```

**Domain of validity:** τ ≪ timescale of s variation (diffusive regime). Breaks when ωτ ≫ 1.

---

### 1.3 Wave Equation Limit

**Status: DERIVED** (conditional on τ → ∞ with c fixed)

From [TEL]: divide by τ, take τ → ∞:
```
∂²s/∂t² = c² ∇²s                    [WAVE]  ← DERIVED (limit of TEL)
```

---

### 1.4 C_JJ(t) — Local Current-Current Correlation Function

**Status: DERIVED** (from PRW balance equations via Ornstein-Uhlenbeck argument)

**Proof chain** (prw_01_cjj_derivation.py, Steps 1–2; verified symbolically):

1. At k = 0 (spatially uniform mode), the [C-q] system reduces to:
   ```
   dG_q/dt = −2λ G_q,   G_q(0) = 1
   ```
   *Solved exactly*: G_q(k=0, t) = exp(−2λt). Verified by sympy dsolve: ODE residual = 0. **[PASS]**

2. At a fixed point, the current q(t) satisfies an Ornstein-Uhlenbeck equation with decay rate 2λ. The equilibrium variance is ⟨q²⟩ = s₀v²/2 (from PRW equipartition).

3. Wiener-Khinchin theorem applied to the stationary OU process:
   ```
   C_JJ(t) = S₀ · exp(−t/τ_B)
   S₀ = s₀v²/2
   τ_B = 1/(2λ)                      [C_JJ-LOCAL]  ← DERIVED
   ```

4. Fourier transform gives the power spectral density:
   ```
   S_JJ(ω) = 2S₀τ_B / (1 + ω²τ_B²)  [LORENTZIAN]  ← DERIVED
   ```

Script output confirmed: `C_JJ(t) = S0 * exp(-t/tau_B)`, `S_JJ(w) = 2*S0*tau_B / (1 + w^2*tau_B^2)`. **[PASS]**

---

### 1.5 Spatial Correlator S_JJ(Δx, ω=0) = S₀ exp(−|Δx|/ξ_c)

**Status: DERIVED** (from telegrapher Green's function, with numerical verification; analytic step partially incomplete)

**Proof chain** (prw_02_spatial_correlator.py, Steps 1–2):

1. The k-space Green's function at ω = 0:
   ```
   S_JJ(k, ω=0) = S₀ · 2λ / (v²k²) = S₀ · (2/k²ξ_c²)/ξ_c
   ```
   This has a 1/k² pole at k → 0 (IR divergence — discussed in Section 6).

2. Integration over time using the exact telegrapher current Green's function G_q(Δx, t):
   ```
   ∫₀^∞ G_q(Δx, t) dt = exp(−λ|Δx|/v) = exp(−|Δx|/ξ_c)
   ```
   where ξ_c = v/λ = 2cτ.

3. Therefore:
   ```
   S_JJ(Δx, ω=0) = S₀ · exp(−|Δx|/ξ_c)   ← DERIVED (with caveat below)
   ```

4. **Numerical verification:** prw_02 computed S_JJ numerically via Bessel-function integration. Max deviation from exp(−|Δx|/ξ_c) = reported < 0.05 (**[PASS]**).

**Caveat — analytic step incomplete:** The analytic proof of the identity
`∫_{d/v}^∞ exp(−λt) I₀(λ/v √(v²t²−d²)) dt = (v/λ)exp(−λd/v)`
was NOT completed in prw_02. The Watson/Erdélyi integral identity was attempted but the degenerate case (p = y) was not resolved analytically. The result is supported by numerical verification only. The analytic proof is an open mathematical gap.

---

### 1.6 Dephasing Function Φ(t) — Exact Non-Markovian Form

**Status: DERIVED** (from second-order cumulant expansion; exact for Gaussian noise)

**Proof chain** (nm_01_memory_kernel.py; NM_PREDICTION_AUDIT.md §2):

For Gaussian noise, the second-order cumulant expansion is exact (Kubo 1963). With C_JJ(t) = S₀ exp(−t/τ_B):

```
Φ(t) = (2g²/ℏ²) ∫₀ᵗ dt' (t−t') C_JJ(t')
      = Γ_Markov · τ_B · [t/τ_B − 1 + exp(−t/τ_B)]   [EXACT-PHI]  ← DERIVED
```

where Γ_Markov = 2g²S₀τ_B/ℏ².

Numerically verified: max error = 3.12×10⁻⁶. **[PASS]**

---

### 1.7 Markov Limit of Dephasing Rate

**Status: DERIVED** (as limit of EXACT-PHI; conditional on τ_B → 0)

In the limit t ≫ τ_B:
```
Φ(t) → Γ_Markov · t
ρ₀₁(t) = ρ₀₁(0) · exp(−Γ_Markov · t)
Γ_Markov = 2g²S₀τ_B/ℏ² = (4g²/3ℏ²) · s₀² ω_rot² r_q² · τ_B  ← DERIVED (conditional)
```

---

### 1.8 Γ_φ = k_rot · ω_rot²

**Status: DERIVED** — but conditional on at least 6 independent assumptions (see Section 2)

With S₀ = (2/3)s₀²ω_rot²r_q² (Layer 3 rotational variance, see Section 2) and Γ_Markov above:
```
Γ_φ = k_rot · ω_rot²,   k_rot = 8g²s₀²r_q²τ / (3ℏ²)   [DEPH]  ← DERIVED (conditional)
```

The algebra is correct. The conditionality is the critical point: this is not derived from the PRW alone.

---

### 1.9 Q Diagnostic

**Status: DERIVED** (as algebraic shorthand for telegrapher stability analysis)

The telegrapher dispersion relation ω(k) = −i/(2τ) ± √(c²k² − 1/(4τ²)) transitions from oscillatory to overdamped at k_c = 1/(2cτ). The Q diagnostic:
```
Q(x,t) = 4c²τ²|∇ ln s(x,t)|² − 1   [Q-DEF]  ← DERIVED (algebraic identity)
```
Q > 0 ↔ oscillatory; Q < 0 ↔ overdamped; Q = 0 ↔ critical. This is exactly the stability condition of the telegrapher equation.

---

### 1.10 Lindblad Structure (σ_z Pure Dephasing)

**Status: DERIVED** (conditional on A-lin-coupling + A-local + Born-Markov-secular)

For linear local coupling H_int = g J σ_z, the unique Lindblad operator is A = σ_z. T₁ = ∞ (σ_z commutes with H_S). Derived in interaction_hamiltonian_derivation.md via:
Bloch-Redfield → secular approximation → Lindblad:
```
dρ_S/dt = (Γ_φ/2)(σ_z ρ_S σ_z − ρ_S)   [LIND]  ← DERIVED (conditional)
```

---

## SECTION 2 — Equations Merely Assumed (No Derivation)

These items appear in the theory without derivation from more primitive principles. Each is a genuine axiom or conjecture presented as such or quietly imported.

---

### 2.1 H_int = g J(x_q, t) σ_z

**Status: ASSUMED** [A-lin-coupling + A-local]

The coupling form H_int = g J σ_z is not derived from the substrate transport equations. It is imposed as:
- A-lin-coupling: the coupling is linear in J (minimal coupling assumption — standard but not derived)
- A-local: the coupling is evaluated at a single point x_q (electric-dipole approximation)

**Consequence of this assumption being wrong:** If the coupling were quadratic in J, or if it involved ∇J, or if the operator were σ_x instead of σ_z, the entire dephasing prediction would change. The Lindblad operator uniqueness proof (§1.10) is entirely conditional on this assumption.

---

### 2.2 ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q²

**Status: ASSUMED / PARTIALLY DERIVED** — the rotational variance formula

This is labeled [LAYER4] in the decoherence chain. It claims that the current variance in a rotating frame scales as ω_rot²r_q². This requires:
- Identification of a rotating reference frame (assumed external)
- A specific geometric model of the qubit coupling (r_q is the "effective qubit radius" — UNKNOWN in general)
- The factor 2/3 comes from angular averaging (assumes isotropic rotation)

The source documents do not show a complete derivation of this from the PRW balance equations. The rotational frame is externally imposed; the PRW is defined without rotation.

**This is the load-bearing assumption of the ω_rot² prediction.** Without it, Γ_φ ∝ ω_rot² does not follow.

---

### 2.3 Axioms M1 (Matrix Fields) and M2 (Moyal Deformation)

**Status: ASSUMED** [A-M1, A-M2]

Explicitly labeled in C2_FOUNDATIONS.md as independent axioms not derivable from the transport layer [ME] or the PRW. M1 introduces quantum matrix fields; M2 introduces non-commutative (Moyal) deformation. These are required to connect the PRW substrate to quantum mechanics. Without M1 and M2, the entire quantum dephasing prediction is unsupported.

**Proof of non-derivability:** Theorem PRW-IMP-1 in C2_FOUNDATIONS.md: the PRW observable algebra is commutative (C^∞(ℝ, ℝ²)). No non-commutative structure can emerge without additional axioms. This is proven, not conjectured.

---

### 2.4 Born Approximation (A-HC1)

**Status: ASSUMED**

ρ_total = ρ_S ⊗ ρ_B at all times. Weak coupling. This is the standard Born assumption from open quantum systems theory — imported, not derived from the substrate.

---

### 2.5 Markov Approximation (A-HC2)

**Status: ASSUMED** (and demonstrated to be a domain restriction, not a fundamental property)

τ_B ≪ Γ_φ⁻¹. This is assumed, and STRESS_TEST.md explicitly shows it breaks: at NMP = τ_B·Γ_φ = 1, the Markov model has mismatch 0.339; at NMP = 10, mismatch 0.698. The Markov limit is a regime approximation, not a universal property of the substrate.

---

### 2.6 Secular Approximation (A-HC3)

**Status: ASSUMED**

Required to go from Bloch-Redfield to Lindblad form. Standard in quantum optics; not derived from the substrate.

---

### 2.7 Stationarity of Bath (A-HC4)

**Status: ASSUMED**

C_JJ(t, τ) = C_JJ(τ) — the substrate autocorrelation depends only on time difference, not absolute time. The PRW in equilibrium satisfies this, but the full substrate with v_sub ≠ 0 or time-dependent fields does not.

---

### 2.8 Coupling Constant g is Free

**Status: UNKNOWN**

g [J·m²·s/info] is introduced in §1 of interaction_hamiltonian_derivation.md and explicitly declared: "No further constraint on g comes from the substrate transport theory." This is a permanently free parameter unless an independent principle is found (see C2_MISSING_PRINCIPLES.md Problem on Planck constant — which shows even ℏ cannot currently be derived from within C2).

---

### 2.9 s₀ (Background Information Density)

**Status: ASSUMED / EMPIRICAL**

The equilibrium background density s₀ [info/m³] enters S₀ = s₀v²/2. Its value is not derived; it is a property of the substrate's ground state that must be measured or assumed. The stress test confirms that g and s₀ are non-identifiable separately from Ramsey data alone (Fisher matrix eigenvalue = 0, condition number = infinite — STRESS_TEST.md §04).

---

### 2.10 r_q (Effective Qubit Radius)

**Status: UNKNOWN**

r_q is described as "coupling scale" or "effective qubit radius." It appears in ⟨(δJ)²⟩ and k_rot but is not derived from the PRW or from any geometric property of the qubit. It is a free parameter absorbed into k_rot.

---

### 2.11 PRW Is the Unique Admissible Projection of FPUT (in 1D)

**Status: DERIVED** (established as Theorem FPUT-3 in C2_FOUNDATIONS.md, but only in 1D)

The uniqueness of the PRW as the admissible projection is proved for the 1D harmonic FPUT chain. The 3D generalization is explicitly flagged as open (OP-1).

---

### 2.12 Information Density Interpretation of s

**Status: ASSUMED** [PRW-1 in substrate_transport_derivation.md]

"The propagating quantity is information content. Each microscopic particle carries one information quantum." Explicitly labeled [A] in substrate_transport_derivation.md §1. This is a physical interpretation assigned to the PRW field, not derivable from the PRW mathematics.

---

## SECTION 3 — Approximations

Each approximation is named, its domain of validity stated, and what breaks outside it.

---

### 3.1 Markov Approximation

**Name:** Born-Markov  
**Condition:** τ_B · Γ_φ ≡ NMP ≪ 1  
**What it gives:** Γ_φ = const = Γ_Markov; ρ₀₁(t) = exp(−Γ_Markov t)  
**What breaks outside it:** The exact coherence is ρ₀₁(t) = exp(−Φ(t)) with Gaussian initial decay. At NMP > 0.1, the deviation from exponential is measurable (STRESS_TEST §07: mismatch 0.339 at NMP=1). The entire "flat dephasing rate" prediction collapses in the non-Markovian regime.  
**Domain of validity:** IBM qubit data consistent with NMP ≈ 0.024 (fitted τ_B = 0.75 µs; NM_PREDICTION_AUDIT §6). The gamma_dataset was likely recorded in the Markovian regime; this cannot be verified without full Ramsey time traces.

---

### 3.2 Born (Weak Coupling) Approximation

**Name:** Born factorization  
**Condition:** g² ≪ system energy scales; ρ_total ≈ ρ_S ⊗ ρ_B at all times  
**What it gives:** Second-order perturbation theory for the open system; the substrate is not back-acted upon by the qubit.  
**What breaks outside it:** Strong coupling modifies both the substrate and the qubit states; the product state assumption fails; the Lindblad structure breaks down. No strong-coupling treatment exists in the C2 framework.

---

### 3.3 Secular (Rotating-Wave) Approximation

**Name:** Secular approximation  
**Condition:** |ω_q| τ_B ≫ 1, or equivalently, the qubit oscillation period ≪ τ_B  
**What it gives:** Lindblad form with guaranteed CPTP.  
**What breaks outside it:** Bloch-Redfield equation (not Lindblad); potential positivity violations; coherences couple to populations.

---

### 3.4 Stationary Bath Approximation

**Name:** Stationarity of C_JJ  
**Condition:** The substrate is in thermal equilibrium; v_sub = 0; no external driving of the substrate.  
**What it gives:** C_JJ(t, t') = C_JJ(t − t') — only time differences matter.  
**What breaks outside it:** Non-stationary substrate (driven, flowing, or cooling) introduces time-dependent dephasing rates; the Φ(t) integral is no longer analytically tractable in the same form.

---

### 3.5 Continuum Limit

**Name:** PRW continuum limit  
**Condition:** Δx → 0, Δt → 0 at fixed v = Δx/Δt and λ  
**What it gives:** Telegrapher PDE as a continuous field equation  
**What breaks outside it:** Lattice artifacts appear at scales near the lattice spacing; dispersion relation acquires Brillouin zone cutoffs not present in the PDE.

---

### 3.6 1D Restriction

**Name:** One-dimensional PRW  
**Condition:** All of the above derivations are for 1D only  
**What it gives:** Scalar telegrapher, exponential C_JJ(t), exponential spatial correlator  
**What breaks outside it:** In 3D, the telegrapher generalization is non-trivial (not the direct sum of three 1D equations); the spatial correlator takes a different form; the factor 2/3 in the rotational variance formula assumes 3D isotropy, so there is a dimensional inconsistency — the PRW is derived in 1D but the rotational variance formula uses a 3D geometry.

---

## SECTION 4 — Parameter Definitions and Dimensions

All parameters appearing in the theory, with units, derivation status, and whether they are independently measurable.

| Symbol | Definition | Units | Status | Measurable independently? |
|--------|-----------|-------|--------|--------------------------|
| v | PRW particle speed | m/s | ASSUMED (A-PRW1) | No — absorbed into c |
| λ | Reversal rate | s⁻¹ | ASSUMED (A-PRW1) | No — absorbed into τ |
| τ = 1/(2λ) | PRW relaxation time | s | DERIVED | Yes, from T₂* if τ_B = τ |
| c = v | Substrate wave speed | m/s | DERIVED (= v) | UNKNOWN — not independently measured |
| D = c²τ | Effective diffusivity | m²/s | DERIVED | No — composite parameter |
| τ_B | Bath correlation time | s | ASSUMED = τ (open assumption A-BRIDGE-τ) | Potentially from NM Ramsey trace |
| ξ_c = 2cτ | Coherence length | m | DERIVED | Requires independent measurement of c |
| k_c = 1/(2cτ) | Critical wavenumber | m⁻¹ | DERIVED | As above |
| s₀ | Background information density | info/m³ | ASSUMED | Not measurable without g |
| g | Quantum-classical coupling | J·m²·s/info | UNKNOWN (free parameter) | Not measurable without independent experiment |
| r_q | Effective qubit radius | m | UNKNOWN (free parameter) | Not measurable without g and s₀ |
| S₀ = s₀v²/2 | Equilibrium current variance | (info/(m²·s))² | DERIVED | Not measurable without s₀, v |
| k_rot = 8g²s₀²r_q²τ/(3ℏ²) | Rotation-decoherence coefficient | s | FITTED (from IBM data) | Contains 4 unknowns; composite |
| Γ_φ | Dephasing rate | s⁻¹ | EMPIRICAL | Yes — from 1/T₂* |
| Γ_Markov | Markov limit of Γ_φ | s⁻¹ | DERIVED (conditional) | Yes |
| NMP = Γ_Markov · τ_B | Non-Markovianity parameter | dimensionless | DERIVED | Requires τ_B measured |
| ω_rot | Frame rotation frequency | rad/s | EMPIRICAL | Yes — experimental control parameter |
| Q(x,t) | Coherence regime diagnostic | dimensionless | DERIVED | Yes, if s(x,t) is known |
| ℏ | Reduced Planck constant | J·s | EMPIRICAL | Standard physical constant |

**Critical note on non-identifiability:** The stress test (§04) showed that g and s₀ are structurally non-identifiable from Ramsey data alone. The Fisher information matrix has a zero eigenvalue. Only the composite k_rot = 8g²s₀²r_q²τ/(3ℏ²) is measurable from frequency-vs-rate data. This means the theory has at least three independently unmeasurable parameters (g, s₀, r_q) hidden inside one fitted composite.

---

## SECTION 5 — Validity Domains

The theory is valid (all approximations simultaneously satisfied) only within a specific domain. Outside this domain, one or more approximations fail.

### Domain map (from STRESS_TEST §08)

The stress test maps a 2D proxy grid (Born proxy × NMP = τ_B·Γ_φ) and finds:
- Green (approximations valid): 21.4% of parameter space
- Yellow (marginal): 21.2%
- Red (approximations invalid): 57.4%

**The theory is in the valid regime for only ~21% of the plausible parameter space.**

### Explicit validity conditions

1. **Markov valid:** NMP = τ_B·Γ_φ < 0.01 (green); 0.01–0.1 (yellow); > 0.1 (red)
2. **Born valid:** g²S₀τ_B/ℏ²ω_q² ≪ 1 (no independent constraint from current theory)
3. **Secular valid:** ω_q τ_B ≫ 1
4. **1D PRW:** Only for 1D transport; 3D extension unproved
5. **Stationarity:** Substrate in thermal equilibrium; v_sub = 0
6. **Weak coupling:** g ≪ ℏω_q/(J(x_q)·τ_B)

### Falsification domains

The stress test (§10) ran 100,000 seeded parameter samples and found 17.2% failure rate against combined Markov/finite-memory criteria. **This is labeled FAIL.** The theory cannot make universal claims; it is valid only in the weak-Markov corner of parameter space.

---

## SECTION 6 — Unresolved Mathematical Gaps

Ordered from most critical to least critical.

---

### GAP-1: Analytic proof of ∫G_q dt = exp(−|Δx|/ξ_c) is INCOMPLETE

**Location:** prw_02_spatial_correlator.py, STEP 1 derivation block  
**Nature:** The identity ∫_{d/c}^∞ exp(−λt) I₀(λ/c √(c²t²−d²)) dt = (c/λ) exp(−λd/c) was attempted but the degenerate case p = y in the Watson/Erdélyi formula was not resolved analytically.  
**Current support:** Numerical verification only (max error < 0.05). This is not a proof.  
**Consequence:** The exponential spatial correlator S_JJ(Δx) = S₀ exp(−|Δx|/ξ_c) is numerically supported but not analytically proven from the PRW Green's function.

---

### GAP-2: 1/k² IR Divergence in S_JJ(k, ω=0)

**Location:** prw_02_spatial_correlator.py, STEP 1 k-space result  
**Nature:** The zero-frequency spectral density S_JJ(k, ω=0) = S₀ · 2λ/(v²k²) diverges as k → 0. This is the standard 1D random walk IR divergence.  
**Current resolution:** Regularized by a system-size IR cutoff (k_min ~ 1/L_system). This is a physical cutoff, not a UV renormalization — the divergence is real and indicates that the spatial correlator at k = 0 grows without bound in an infinite system.  
**Consequence:** The prediction C_Γ(d) = exp(−d/ξ_c) is only valid for d ≪ L_system and requires careful definition of the correlation as a ratio.

---

### GAP-3: Identification τ_B = τ (Open Assumption A-BRIDGE-τ)

**Location:** C2_FOUNDATIONS.md, Open Assumptions section  
**Nature:** The PRW transport relaxation time τ = 1/(2λ) and the quantum bath correlation time τ_B are identified as the same parameter. This identification is "used implicitly in Theorem HC-4" but "not yet formally verified." It is explicitly listed as an open assumption, not a theorem.  
**Consequence:** If τ_B ≠ τ, the entire identification between the transport timescale and the quantum dephasing timescale breaks. The prediction τ_B = 1/(2λ) would be wrong. This is the central bridge between the transport and quantum layers; its failure would sever the connection.

---

### GAP-4: 3D Generalization of PRW Uniqueness

**Location:** C2_FOUNDATIONS.md, Subsystem 1 and 2  
**Nature:** The uniqueness of the PRW as the admissible projection of FPUT is proved only in 1D (Theorem FPUT-3). The 3D extension is open problem OP-1.  
**Consequence:** All derived results (telegrapher, C_JJ, spatial correlator) are 1D. The physical prediction for real qubits (3D objects) assumes 3D isotropy and uses a factor 2/3 from the rotational variance, but the underlying 3D PRW derivation does not exist.

---

### GAP-5: Derivation of Rotational Current Variance Formula

**Location:** decoherence_chain_summary.md, LEVEL 4; substrate_transport_derivation.md  
**Nature:** The formula ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² is labeled [A] (assumption) in the decoherence chain document. It is the key formula linking substrate to the predicted ω_rot² scaling. The document does not show its derivation from PRW balance equations.  
**Consequence:** Without this derivation, the ω_rot² prediction has no substrate basis. It is an assumed formula, not a consequence of the PRW dynamics.

---

### GAP-6: Origin of the ω_rot² Scaling

**Location:** C2_final_prediction_audit.md, Layer 3  
**Nature:** The final prediction Γ_φ ∝ ω_rot² depends on S₀ ∝ ω_rot². This S₀ dependence comes from the rotational variance formula (GAP-5). The ω_rot² scaling is not independently derived from any wave equation or transport argument; it is inserted via the variance formula.  
**Consequence:** The signature ω_rot² prediction is not a theorem of the transport layer. It requires external assumptions about rotation that are not part of the PRW.

---

### GAP-7: Non-derivability of g and Physical Interpretation

**Location:** interaction_hamiltonian_derivation.md §1  
**Nature:** g is a free parameter. C2_FRONTIER_MAP.md (F10) confirms: no derivation of g exists from first principles in any framework. C2_MISSING_PRINCIPLES.md shows that even ℏ cannot be derived from the current C2 results.  
**Consequence:** k_rot = 8g²s₀²r_q²τ/(3ℏ²) contains four unmeasurable parameters (g, s₀, r_q, τ if τ ≠ T₂*) compressed into one fitted number. The parameter-free prediction is not achievable within the current framework.

---

### GAP-8: Quantum State Space (M1, M2 not derived)

**Location:** C2_FOUNDATIONS.md, Subsystem 1 (Failed Proofs), Subsystem 4  
**Nature:** The PRW state space is the classical simplex Δ₁ ≅ [0,1], not the Bloch sphere. Quantum state space CP¹ ≅ S² does NOT emerge from the PRW. Theorem PRW-IMP-1 proves this is impossible without additional axioms M1 (matrix fields) and M2 (Moyal deformation), which are logically independent of the transport layer.  
**Consequence:** The C2 transport layer cannot be the substrate of a quantum system without importing quantum mechanics back in through M1 and M2. This is a logical circularity — the framework requires quantum axioms to predict quantum behavior.

---

## SECTION 7 — Previous Mistakes Discovered

### MISTAKE-1: prw_02 Initially Claimed exp(−d/ξ_c) Then Found 1/k² Spectrum

**Location:** prw_02_spatial_correlator.py — The docstring for `compute_S_JJ_vs_dx` and the extensive derivation block in STEP 1.

**What happened:**

The prw_02 script went through two conflicting derivation routes and reached initially contradictory results. This is documented in the script's own derivation docstrings:

**Route A (k-space, attempted first):**
The derivation in the large STEP 1 comment block computes the k-space zero-frequency spectral density:
```
S_JJ(k, ω=0) = S₀ · 2λ / (v²k²)    [S_JJ-K]
```
This gives a **1/k² spectrum** — not an exponential. The inverse Fourier transform of 1/k² is |Δx| (linear growth in 1D), NOT exp(−|Δx|/ξ_c). The k-space route directly contradicts the exponential spatial correlator.

The script explicitly notes the IR divergence: "This integral has an IR divergence at k→0 — the 1/k² pole."

**Route B (real-space Green's function, attempted second):**
The "ALTERNATIVE DERIVATION (cleaner)" block uses the telegrapher Green's function in real space and claims:
```
∫₀^∞ G_q(Δx, t) dt = exp(−λ|Δx|/v) = exp(−|Δx|/ξ_c)
```
This gives the exponential. BUT — the analytic step that bridges these two contradictory results is incomplete. The Watson/Erdélyi integral identity was invoked but found to be in a degenerate case (p = y → p²−y² = 0), and the script explicitly states: "Let me use the numerical approach instead and verify the exponential form numerically."

**The error / logical gap:** The k-space and real-space derivations give contradictory results when taken at face value:
- k-space: S_JJ(Δx) ∝ |Δx| (diverges with separation — does NOT decay)
- Real-space: S_JJ(Δx) = S₀ exp(−|Δx|/ξ_c) (decays exponentially)

These are only reconcilable if the IR divergence in the k-space integral is properly regularized and the regularized inverse transform reproduces the exponential. **This reconciliation was not shown analytically.** The script fell back on numerical verification to confirm the exponential form.

**Additionally — Temperature-dependent correlation note:**
The NM_PREDICTION_AUDIT notes that τ_B controls the Gaussian onset of coherence decay. In the PRW, τ_B = 1/(2λ). If λ has temperature dependence (phonon scattering sets the reversal rate at finite T), then τ_B → τ_B(T) and ξ_c → ξ_c(T). This T-dependence is neither derived nor stated — it is implicitly present but uncontrolled.

**Status:** The exponential spatial correlator exp(−|Δx|/ξ_c) is numerically confirmed but NOT analytically proven from the 1/k² k-space result. The two routes have not been analytically reconciled. **This is an open gap in the derivation chain.**

---

### MISTAKE-2: Previously Assumed Super-Ohmic Spectrum (S_JJ ∝ ω²) Was Not Derived

**Location:** prw_01_cjj_derivation.py — docstring and `write_summary()`

**What was assumed:** S_JJ(ω) ∝ ω² (super-Ohmic spectral density), which would give Γ_φ ∝ ω_rot² as a frequency-dependent dephasing rate.

**What the PRW actually gives:** The PRW produces a **Lorentzian** spectral density:
```
S_JJ(ω) = 2S₀τ_B / (1 + ω²τ_B²)   [LORENTZIAN]
```

The script's own critical finding section states: "The previously used S_JJ(ω) ~ ω² (super-Ohmic assumption) was NOT derived from the PRW. The PRW gives a Lorentzian S_JJ(ω). The ω² assumption was an imported model, not a consequence of the substrate dynamics. This is a significant finding."

**Consequence for the ω_rot² prediction:**
- Super-Ohmic assumption: Γ_φ ∝ ω_rot² (rate *increases* with qubit rotation frequency)
- PRW-derived Lorentzian: Γ_φ = Γ_Markov / (1 + ω_rot²τ_B²) (rate *decreases* at high ω_rot)

The predictions are **qualitatively opposite** at high frequencies. The ω_rot² prediction depends on S₀ = (2/3)s₀²ω_rot²r_q² (the rotational variance formula), NOT on the PRW spectral density. The ω_rot² dependence in Γ_φ enters through the variance formula (Section 2.2), not through S_JJ(ω). But the super-Ohmic assumption was a related error where S_JJ(ω_q) ∝ ω_q² was assumed to explain the frequency scaling — this was wrong.

**The gamma_dataset consistency check:** The script shows the IBM gamma_dataset data is approximately flat across frequencies 0.7–50 MHz. This is consistent with the PRW Lorentzian (low-frequency white noise regime ω_rot ≪ 1/τ_B), NOT with the super-Ohmic ω² assumption (which would show strong growth). The flat data is therefore consistent with the PRW Lorentzian in the limit NMP ≪ 1.

---

### MISTAKE-3: Prediction Γ_φ ∝ ω_rot² Is Not Unique to C2

**Location:** STRESS_TEST.md §03 and §06; C2_final_prediction_audit.md §12

**What was claimed:** The ω_rot² scaling is a distinctive prediction of the C2 substrate.

**What was found:** The stress test shows the effective σ_z Lindblad equation is exactly reproduced by standard Lindblad dynamics. "The target is pure σ_z dephasing with Γ_φ = 0.7. It is exactly reproduced by the corresponding standard Lindblad channel — therefore this coincidence cannot be evidence for the microscopic derivation." The C2_final_prediction_audit explicitly reaches Outcome A: "C2 predicts nothing experimentally unique" (for the frequency-domain ω² scaling).

The ω_rot² scaling is also reproduced by any super-Ohmic bath — it is not a signature unique to the PRW substrate.

---

### MISTAKE-4: The Empirical k_rot Does Not Determine g, s₀, r_q Individually

**Location:** STRESS_TEST.md §04 (Inverse Problem); C2_FOUNDATIONS.md §Subsystem 15

**What was claimed:** k_rot = 4.5×10⁻⁷ s (from IBM Quantum data) validates the substrate prediction.

**What was found:** Fisher information matrix for (log g, log s₀) has eigenvalue = 0. Condition number = infinite. The two columns of the Fisher matrix are identical. "Coherence-only Ramsey data do not identify the microscopic mechanism." The fit determines the composite k_rot = 8g²s₀²r_q²τ/(3ℏ²), but the four individual parameters are not separately identifiable. **The empirical k_rot is a fit to one composite number, not a validation of the microscopic mechanism.**

---

## SECTION 8 — The Exact Prediction to Be Tested

The new experimental test proposed in `09_spatiotemporal_c2_test/` should test the **spatiotemporal** prediction — one that is strictly different from all standard alternatives.

### The Prediction (from NM_PREDICTION_AUDIT + prw_02)

**Prediction P1 (Spatial Correlation):**
```
C_Γ(d) ≡ Cov(Γᵢ, Γⱼ) / Var(Γ) = exp(−d / ξ_c)
ξ_c = 2cτ   (coherence length = 2 × substrate speed × PRW relaxation time)
```

The dephasing rates of qubits separated by distance d are correlated with a pure exponential decay over a characteristic length ξ_c.

**Prediction P2 (Temporal — Non-Markovian Ramsey shape):**
```
ρ₀₁(t) = ρ₀₁(0) · exp(−Φ(t))
Φ(t) = Γ_Markov · τ_B · [t/τ_B − 1 + exp(−t/τ_B)]
```

At early times t ≪ τ_B: Φ(t) ≈ Γ_Markov t²/(2τ_B) → **Gaussian initial decay**
At late times t ≫ τ_B: Φ(t) ≈ Γ_Markov t → **exponential decay**

**Prediction P3 (Consistency check — linking spatial and temporal):**
The SAME τ_B = τ = 1/(2λ) that controls the Gaussian onset (P2) also determines the spatial coherence length ξ_c = 2cτ_B (P1). If c can be independently determined (e.g., from phonon speed or qubit layout geometry), the single parameter τ_B predicts both spatial and temporal observables simultaneously. **This is a non-trivial self-consistency condition** that a phenomenological Lindblad model does not have.

### What Makes These Predictions (Conditionally) Unique

| Prediction | Standard Lindblad | Phonon bath | C2 substrate |
|-----------|------------------|-------------|-------------|
| Ramsey shape at t < τ_B | exp(−Γt) always | exp(−Γt) always | exp(−Γt²/2τ_B) Gaussian |
| Spatial correlation form | none (no spatial model) | exp(−d/ξ_ph) | exp(−d/ξ_c) |
| Link between τ_B and ξ_c | none | none | ξ_c = 2cτ_B (same τ) |

**Caveats:**
- P1 (spatial exponential) has the same *form* as a phonon bath. Discrimination requires showing ξ_c = 2c_substrate·T₂* where c_substrate ≠ v_sound.
- P2 (Gaussian onset) is unique to any non-Markovian bath with exponential correlation. It is not unique to C2 — any bath with C(t) = S₀ exp(−t/τ_B) gives the same Φ(t). The C2 prediction is that the *source* of τ_B is the PRW relaxation.
- P3 (self-consistency link) is the most distinctive prediction but requires independent measurement of c.

---

## SECTION 9 — Quantities That Must Be Measured Independently

For the spatiotemporal test to provide meaningful constraints on C2, the following quantities must be measured independently of the dephasing data.

### 9.1 τ_B — Bath Correlation Time

**What it is:** The timescale of exponential decay of C_JJ(t).
**How to measure:** Full Ramsey time trace (not just 1/e point) with sub-µs resolution. Fit the early-time Gaussian decay: log|C(t)| vs t² should be linear at t < τ_B (NM_PREDICTION_AUDIT §7 discriminator protocol).
**Requirement:** ≥ 1000 shots per time point; time resolution dt ≪ τ_B; range 0 to ~4×T₂*.
**Why needed:** Without τ_B, the NMP cannot be computed and it is unknown whether the system is in the Markovian regime.

### 9.2 ξ_c — Spatial Coherence Length

**What it is:** The decay constant of the inter-qubit dephasing correlation C_Γ(d) = exp(−d/ξ_c).
**How to measure:** Measure Γᵢ = 1/T₂* for pairs of qubits at known separations d on the same chip. Compute Cov(Γᵢ, Γⱼ)/Var(Γ) as a function of d. Fit to exponential; extract ξ_c.
**Requirement:** Multiple qubit pairs spanning at least 3×ξ_c; controlled chip layout (known qubit-qubit distances); identical measurement protocol for all qubits.
**Why needed:** ξ_c is the key spatial observable of P1 and P3.

### 9.3 c — Substrate Wave Speed (or T₂* spatial variation)

**What it is:** The PRW propagation speed, c = v. Not the phonon speed.
**How to measure (indirect):** If τ_B is measured from Ramsey traces (§9.1) and ξ_c is measured from spatial correlations (§9.2), then c = ξ_c / (2τ_B). This extracted c can then be compared to the phonon speed in the chip material (Si: ~6 km/s; Al: ~5 km/s). If c ≪ v_sound, the substrate and phonon interpretations are discriminated.
**Why needed:** The only way to break the degeneracy between C2 substrate and phonon bath models.

### 9.4 k_rot (or Γ_Markov) — At Multiple Rotation Frequencies

**What it is:** The Markov dephasing rate as a function of ω_rot.
**How to measure:** Already done in the gamma_dataset (7 data points). Needs extension to: (a) higher frequencies to test for Lorentzian rolloff (high-frequency prediction: Γ ∝ 1/ω_rot² if ω_rot τ_B ≫ 1), and (b) lower frequencies to establish the flat noise floor.
**Why needed:** The ω_rot² scaling at low frequencies and Lorentzian rolloff at high frequencies are both PRW predictions; only the low-frequency limit has been tested.

### 9.5 Temperature Dependence of ξ_c and τ_B

**What it is:** If λ(T) has a specific T-dependence (e.g., phonon-scattering sets λ ∝ T⁵ at low T), then τ_B(T) = 1/(2λ(T)) and ξ_c(T) = c/λ(T) would have characteristic T-dependences.
**How to measure:** Vary chip temperature (dilution refrigerator base vs warmer temperatures); measure τ_B and ξ_c at each T.
**Why needed:** Temperature dependence discriminates C2 substrate noise from classical electronics noise (temperature-independent) and from phonon bath (known T⁵ or T³ dependence).

### 9.6 Full Ramsey Time Traces (Not Just 1/e Points)

**What is available now:** The gamma_dataset contains only 1/e dephasing times Γ = 1/T₂* — single numbers per qubit per frequency.
**What is needed:** Complete time traces ρ₀₁(t) from t = 0 to t = ~4×T₂* with dt ≪ τ_B.
**Why needed:** The Gaussian onset (P2) is entirely invisible in 1/e time measurements. The NM_PREDICTION_AUDIT (§6) explicitly states: "The gamma_dataset is not the right observable. The right observable is the full time trace."

---

## SECTION 10 — What τ_B Is and How It Differs from T₂

This section directly addresses the conceptual distinction, which is conflated in several source documents.

### 10.1 Definitions

**T₂ (Transverse relaxation time / dephasing time):**
T₂ is the time constant for the decay of qubit coherence ρ₀₁(t). It is defined by the 1/e point of the coherence decay, i.e., |ρ₀₁(T₂)| = |ρ₀₁(0)|/e.

- For Markovian exponential decay: ρ₀₁(t) = exp(−Γt), so T₂ = 1/Γ_φ = 1/Γ_Markov.
- T₂* (free induction decay) includes both intrinsic dephasing and inhomogeneous broadening.
- T₂ (Hahn echo) removes inhomogeneous broadening; T₂ ≥ T₂*.

T₂ is a **property of the qubit coherence dynamics** — it is observable.

**τ_B (Bath correlation time):**
τ_B is the timescale over which the substrate "forgets" its state. It governs how long the noise field J(t) is correlated with its past values:
```
C_JJ(t) = S₀ · exp(−t/τ_B)
```

τ_B is a **property of the bath (substrate)**, not of the qubit. It is not directly observable from a single T₂ measurement.

### 10.2 The Relationship Between τ_B and T₂

They are related through the NMP:
```
NMP = Γ_Markov · τ_B = τ_B / T₂
```

- If NMP ≪ 1 (τ_B ≪ T₂): The bath forgets fast; the qubit sees white noise; the coherence decays exponentially; T₂ = 1/Γ_Markov. In this limit, **τ_B cannot be extracted from T₂ measurements** — it is hidden inside Γ_Markov.

- If NMP ~ 1 (τ_B ~ T₂): The bath memory is long; the coherence has a Gaussian initial decay; the 1/e time shifts to T₂ = f(Γ_Markov, τ_B) (requires solving Φ(t) = 1 numerically). **τ_B is measurable in this regime** from the shape of the Ramsey trace.

- If NMP ≫ 1 (τ_B ≫ T₂): Static noise limit; the noise barely changes during the measurement; coherence decays as a Gaussian exp(−Γ_Markov t²/(2τ_B)); T₂ ~ √(2τ_B/Γ_Markov). This is the inhomogeneous broadening regime.

### 10.3 The Open Assumption A-BRIDGE-τ

The C2 framework makes an implicit identification (Open Assumption A-BRIDGE-τ in C2_FOUNDATIONS.md):
```
τ_B ≡ τ = 1/(2λ)
```

**This has not been proven.** The PRW has one timescale: τ = 1/(2λ). The quantum open systems framework has a bath correlation time τ_B. These are assumed to be the same parameter. If this identification is correct:
- τ_B is determined by the PRW reversal rate λ
- λ is a microscopic substrate property
- τ_B is therefore a derived quantity, not a free parameter

If this identification is wrong:
- τ_B and τ are independent
- The theory has an additional free parameter
- The connection between the transport layer and the quantum layer is broken

### 10.4 The T₂ ≤ 2T₁ Bound

C2_FOUNDATIONS.md (Subsystem 5, Theorem Q-4) derives the standard quantum bound T₂ ≤ 2T₁ from the telegrapher structure Im(ω) = 1/(2τ). This is a structural result: the imaginary part of the dispersion relation (the damping) equals 1/(2τ), which maps to the standard quantum channel bound T₂ ≤ 2T₁. This derivation is correct but the result is identical to the standard quantum mechanics bound — it is not a new prediction.

### 10.5 Summary: τ_B vs T₂

| Property | τ_B | T₂ |
|---------|-----|-----|
| Physical meaning | Bath memory time | Qubit coherence time |
| Measured from | Full Ramsey time trace shape | 1/e point of coherence decay |
| Depends on | Substrate reversal rate λ | Both λ and coupling g, s₀ |
| In Markov limit | Not extractable; absorbed into Γ | T₂ = 1/Γ_Markov |
| Relation to NMP | NMP = τ_B/T₂ | NMP = τ_B/T₂ |
| PRW identification | τ_B = τ = 1/(2λ) [ASSUMED, not proven] | T₂ = 1/Γ_Markov (Markov limit) |
| C2 uniqueness | Could discriminate C2 if τ_B = τ is verified | Standard measurable — no discriminating power alone |

---

## ADVERSARIAL SUMMARY

The C2 substrate theory, as documented in this repository, has the following confirmed properties:

**What is mathematically solid:**
1. The 1D telegrapher equation follows exactly from the PRW balance equations. DERIVED.
2. C_JJ(t) = S₀ exp(−t/τ_B) follows from the PRW via the OU process argument. DERIVED.
3. S_JJ(ω) is Lorentzian, not super-Ohmic. DERIVED. The previous ω² assumption was imported without derivation.
4. The exact non-Markovian dephasing function Φ(t) is derived from the second-order cumulant expansion. DERIVED (for Gaussian noise; uses C_JJ(t) which is DERIVED).
5. The σ_z Lindblad structure is uniquely forced by linear local coupling. DERIVED (conditional on A-lin-coupling + A-local).
6. Q diagnostic is a valid stability classifier for the telegrapher equation. DERIVED.

**What is assumed without derivation:**
1. H_int = g J σ_z. ASSUMED.
2. ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q². ASSUMED (the ω_rot² formula that drives the main prediction).
3. M1 (matrix fields) and M2 (Moyal deformation). ASSUMED. Proven non-derivable from the transport layer.
4. τ_B = τ = 1/(2λ) (A-BRIDGE-τ). ASSUMED. Not proven.
5. Information interpretation of s. ASSUMED.
6. The coupling constant g. UNKNOWN. Free parameter.

**The ω_rot² prediction depends entirely on item 2 above (the rotational variance formula), which is assumed not derived. If that assumption is wrong, the entire main prediction collapses. The PRW derivation of S_JJ(ω) shows the spectrum is Lorentzian — the ω² dependence in Γ_φ does not come from S_JJ(ω_q) but from the assumed variance formula. This distinction is critical.**

**What is not unique:**
The frequency-domain prediction Γ_φ ∝ ω_rot² is reproduced by any model giving ⟨(δJ)²⟩ ∝ ω_rot². The effective σ_z Lindblad equation is exactly reproduced by standard Lindblad dynamics. (STRESS_TEST Outcome: not a unique mechanism.)

**What could be unique (conditionally):**
The spatiotemporal prediction — Gaussian Ramsey onset at t < τ_B AND spatial exponential correlation exp(−d/ξ_c) with the SAME τ_B linking both — is not reproduced by any time-independent Lindblad model. This is the prediction for the `09_spatiotemporal_c2_test/`. Its uniqueness is conditional on NMP > 0.1, which requires τ_B > ~3 µs at the median Gamma of 31.7 kHz.

**Critical blockers for the spatiotemporal test:**
- ξ_c = 2cτ_B requires knowing c independently (currently unmeasured)
- The analytic proof of S_JJ(Δx) = S₀ exp(−|Δx|/ξ_c) is incomplete (numerical only)
- τ_B = τ is assumed, not proven
- The gamma_dataset contains only 1/e dephasing times — full time traces are needed

---

*End of GATE 0 Theory Audit*  
*Date: 2026-08-20*  
*All claims sourced from files read in this session. No new mathematics introduced.*  
*This document records the mathematical and logical state of C2 as found; it does not repair, extend, or endorse the theory.*
