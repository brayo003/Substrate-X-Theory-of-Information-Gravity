# COMPLETE_ONTOLOGY_CONSEQUENCE_AUDIT.md
## Full Consequence Tree: C2 Primitive Ontology → Observables

**Date:** 2026-08-22
**Method:** Trace every chain from the C2 axioms to a measurable quantity.
  Every claim traced to its axiom. Chains broken at assumptions are marked
  NOT A C2 PREDICTION.
**Source:** CURRENT_C2_ONTOLOGY_MAP.md, C2_FOUNDATIONS.md

Legend: [C2] = genuine C2 consequence | [COND] = conditional on extra axioms
        [CONV] = conventional equivalent exists | [BREAK] = chain breaks at assumption
        [FAIL] = chain breaks at proved impossibility

---

## THE CONSEQUENCE TREE

### ROOT: C2 Axioms
A-PRW1 (constant v, λ)
A-PRW2 (continuum limit)
A-PRW3 (Markovian flip)
A-FPUT1 (FPUT substrate — assumed, not derived)

### BRANCH 1: Transport Structure

1.1 PRW balance equations → telegrapher equation [C2, exact]
  → finite signal speed c = v [C2]
  → diffusion limit D = c²τ for τ→0 [C2]
  → wave limit for τ→∞ [C2]
  → τ = correlation time = 1/(2λ) [C2]

All of these are ALSO consequences of the Maxwell-Cattaneo/EIT framework.
[CONV] No C2-unique content.

1.2 Spatial correlator in 2D:
  telegrapher → Green's function G(r,ω) → K₀(r/ξ_c) in steady state [C2, DERIVED]
  BUT: (∇²−ξ_c⁻²)G = −δ(r) → G = K₀(r/ξ_c)/(2π) [also from 2D screened diffusion]
  [CONV] K₀ shape is not unique to telegrapher.

1.3 Causal wavefront:
  telegrapher → C(r,t) = 0 for t < r/c [C2, exact from Goldstein-Kac]
  Diffusion null → C(r,t) > 0 for all t > 0
  Phonon null → C(r,t) = 0 for t < r/v_s
  Under Extension A (c=v_s): C2 wavefront = phonon wavefront [CONV]
  Under Extension B (c≪v_s): wavefront arrives at t = r/c ≫ T₂ [inaccessible]

  This is the ONLY structural consequence that differs from diffusion.
  Assessment: [COND] — discriminates from diffusion only. Not from phonon bath.

1.4 Dispersion relation:
  telegrapher → ω² + iω/τ = c²k² → ω(k) = ick ± √(c²k² − 1/(4τ²)) [C2]
  Compare phonon: ω = c_s k (linear)
  Compare diffusion: ω = −iDk² (purely imaginary)
  [COND] Telegrapher dispersion is distinct from both, but:
    - At k → 0: identical to diffusion (ω ≈ −iDk²)
    - At k → ∞: identical to wave equation (ω ≈ ck)
    - Crossover at k = 1/(2cτ) = 1/ξ_c
  [COND] Crossover scale ξ_c is measurable in principle — but ξ_c itself is free.

1.5 Power spectral density of substrate current:
  telegrapher → S_JJ(ω) = 2S₀τ/(1+ω²τ²) [C2, DERIVED]
  [CONV] Identical to OU bath with same parameters.

---

### BRANCH 2: Temporal Correlations

2.1 Substrate autocorrelation:
  C_JJ(t) = S₀ exp(−|t|/τ) [C2, DERIVED from telegrapher]
  [CONV] Identical to OU process with relaxation time τ.

2.2 Multi-time correlations:
  For Gaussian substrate (linear PRW): all n-point functions factorise by Wick's theorem.
  C_n(t₁,...,tₙ) = Σ products of C_JJ pairs [C2, DERIVED]
  [CONV] Any Gaussian bath has same factorisation.
  Non-Gaussian corrections arise only from nonlinear substrate — [BREAK]:
  the PRW is linear; no nonlinear terms are in the C2 axioms.

2.3 Non-Markovian onset:
  W(t) ≈ exp(−Γt − G t²/2) for t ≪ τ [COND — requires coupling assumptions]
  [CONV] Universal for any Gaussian bath. Not C2-specific.

2.4 Multi-time correlation function ⟨J(t₁)J(t₂)J(t₃)⟩:
  = 0 for Gaussian PRW (by Wick) [C2, DERIVED]
  [CONV] Same result for any zero-mean Gaussian process.

---

### BRANCH 3: Spatial Correlations

3.1 Two-point: C(r) = K₀(r/ξ_c)/K₀(a/ξ_c) [C2, DERIVED]
  [CONV] Same from 2D screened diffusion. Not distinctive.

3.2 Higher-order spatial correlations:
  For Gaussian PRW: factorise by Wick's theorem [C2, DERIVED]
  [CONV] Same for any Gaussian field.

3.3 Spatial anisotropy:
  The 2D PRW is isotropic (uniform v, λ) → C(r) depends only on |r| [C2, DERIVED]
  Any anisotropy is [BREAK] — not in the axioms.
  [CONV] No unique anisotropy prediction.

3.4 Boundary-condition dependence:
  At a reflecting boundary: n⁺ = n⁻ (no-flux) → modified K₀ profile [C2, DERIVED]
  [CONV] Same boundary effect present in any diffusion/telegrapher equation.

---

### BRANCH 4: Spectral / Frequency Domain

4.1 Lorentzian S(ω) [C2, DERIVED] — [CONV] identical to OU bath.

4.2 Crossover frequency ω_c = 1/τ separating Lorentzian from flat PSD:
  [C2, DERIVED] — [CONV] same crossover in any single-relaxation-time bath.

4.3 S(ω) ∝ ω⁻² for ω ≫ 1/τ:
  [C2, DERIVED] — [CONV] high-frequency Lorentzian tail; universal.

4.4 ω_rot² scaling of Γ_φ:
  [COND — requires coupling H_int = gJσ_z]
  [CONV] filter function argument gives same result for any bath with Lorentzian PSD.

---

### BRANCH 5: Fluctuation Statistics

5.1 Variance: ⟨J²⟩ = S₀ [FREE PARAMETER — not predicted]
5.2 Skewness: ⟨J³⟩ = 0 [C2, DERIVED for Gaussian PRW] — [CONV] same for any Gaussian
5.3 Kurtosis: ⟨J⁴⟩ = 3⟨J²⟩² [C2, DERIVED for Gaussian PRW] — [CONV] same for Gaussian
5.4 Non-Gaussianity: The PRW is exactly Gaussian (linear dynamics) → zero excess kurtosis
    [BREAK] for any non-Gaussian prediction — not in C2 axioms.

---

### BRANCH 6: Response Functions

6.1 Linear response / susceptibility:
  telegrapher → χ(ω) = S₀τ/(1+iωτ) [C2, DERIVED]
  [CONV] identical to OU bath susceptibility.

6.2 Fluctuation-dissipation theorem (FDT):
  C2 substrate satisfies FDT by construction (equilibrium state):
  S(ω) = 2kT Im[χ(ω)]/ω [CONV — standard FDT, nothing new]

6.3 Nonequilibrium response:
  PRW is an equilibrium model (detailed balance satisfied for uniform λ) [C2, DERIVED]
  No nonequilibrium driving is in the C2 axioms [BREAK]
  Any nonequilibrium prediction requires [BREAK].

---

### BRANCH 7: Transport Coefficients

7.1 Diffusion constant D = c²τ [C2, DERIVED] — [CONV] identical structure to EIT
7.2 Thermal conductivity κ = D × (heat capacity): same as EIT [CONV]
7.3 Viscosity: [BREAK] — [ME] cannot derive Navier-Stokes (scalar theory)
7.4 Electrical conductivity: [BREAK] — requires coupling to charge; not in C2 axioms

---

### BRANCH 8: Quantum Channel Structure

8.1 Lindblad operator L = σ_z [COND — requires coupling assumptions] [CONV]
8.2 T₂ ≤ 2T₁ [COND] — [CONV] standard quantum channel bound; not C2-specific
8.3 CPTP map structure [COND] — [CONV] standard

---

### BRANCH 9: Information-Theoretic Consequences

9.1 Shannon entropy of substrate: H[s] = −∫ s ln s dx [C2, DERIVED from definition]
  [CONV] standard entropy functional
9.2 Entropy production rate: σ = J²/(DS) ≥ 0 [C2, DERIVED] — [CONV] standard EIT
9.3 Second law (entropy non-decreasing): [C2, DERIVED] — [CONV] standard thermodynamics
9.4 Information capacity: not a C2 prediction — no channel capacity formula derived

---

### BRANCH 10: Scaling / Universality

10.1 Scaling exponents near ξ_c:
  At r = ξ_c: K₀(1) ≈ 0.42 (a fixed numerical value) [C2, DERIVED]
  But ξ_c is FREE — so scaling with ξ_c is a tautology.

10.2 Dynamic scaling:
  C(r,t) for telegrapher scales as C(r,t) = f(r/ξ_c, t/τ) [C2, DERIVED]
  [CONV] same scaling form for any single-scale bath.

10.3 Critical exponents:
  Near the wavefront r = ct: C_Γ has a sharp onset [C2, DERIVED]
  [COND] vs. phonon bath this is identical under Extension A.

---

### BRANCH 11: Causality / Light-Cone Structure

11.1 Strict causality: C(r,t) = 0 for t < r/c [C2, DERIVED exactly from telegrapher]
  This is the STRONGEST purely mathematical consequence of C2.
  It distinguishes C2 from diffusion-type models.
  Assessment: GENUINE C2 CONSEQUENCE.
  But:
  - Under Extension A (c=v_s): phonon bath gives same causal structure [CONV]
  - Under Extension B (c≪v_s): inaccessible within T₂

---

### BRANCH 12: Geometry / Dimensionality

12.1 The 2D correlator K₀(r/ξ_c) depends on dimension [C2, DERIVED]
  In 1D: C(r) ∝ exp(−r/ξ_c)
  In 2D: C(r) ∝ K₀(r/ξ_c)
  In 3D: C(r) ∝ exp(−r/ξ_c)/r
  [C2, DERIVED] These are different shapes — but:
  - 1D and 3D forms are ALSO standard screened diffusion Green's functions
  - K₀ in 2D is ALSO the screened diffusion Green's function (shown in TLS_CONVENTIONAL_NULL_AUDIT.md)
  [CONV] No geometry is distinctive.

---

## SUMMARY OF CONSEQUENCE TREE

| Branch | Representative observable | C2 axiom chain? | Conventional null? | Distinctive? |
|--------|--------------------------|-----------------|-------------------|-------------|
| 1 Transport | Telegrapher PDE | YES (complete) | EIT/Maxwell-Cattaneo | NO |
| 1.1 Speed | Finite signal speed c | YES | Phonon bath, EM | NO |
| 1.3 Wavefront | C(r,t)=0 for t<r/c | YES | Phonon bath same | COND vs diffusion |
| 1.4 Dispersion | ω(k) crossover at ξ_c | YES | Free (ξ_c free) | NO |
| 2 Temporal | Lorentzian C_JJ(t) | YES | OU bath identical | NO |
| 3 Spatial | K₀ shape | YES | Screened diffusion identical | NO |
| 4 Spectral | Lorentzian S(ω) | YES | OU bath identical | NO |
| 5 Statistics | Gaussian | YES | Any Gaussian bath | NO |
| 6 Response | FDT satisfied | YES | Standard equilibrium | NO |
| 7 Transport | D = c²τ | YES | EIT identical | NO |
| 8 Quantum | Lindblad, T₂≤2T₁ | COND | Standard QC bound | NO |
| 9 Info-thy | Entropy production | YES | Standard thermo | NO |
| 10 Scaling | K₀ scaling at ξ_c | YES | Free parameter | NO |
| 11 Causality | Strict causal front | YES | Phonon bath same | COND vs diffusion only |
| 12 Geometry | K₀ in 2D | YES | Screened diffusion identical | NO |

**Genuinely distinctive consequences: ZERO unconditionally.**
**Conditionally distinctive: causal wavefront vs. diffusion-type baths only.**
  (Phonon bath, the dominant conventional null, also has a causal front.)
