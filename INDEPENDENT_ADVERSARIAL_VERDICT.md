# INDEPENDENT_ADVERSARIAL_VERDICT.md
## Complete Audit of SXC-IGC/C2 Framework

**Date:** 2026-08-22
**Auditor:** Independent adversarial review
**Scope:** Complete repository audit with no rescue mandate
**Mandate:** Determine whether SXC-IGC/C2 contains genuinely new physical content

---

## 1. What C2 Actually Establishes

### Mathematical Results (Rigorously Established)

**Transport Layer:**
- The Persistent Random Walk (PRW) with constant walker speed v and flip rate λ reduces to the telegrapher equation τ s_tt + s_t = c²τ ∇²s under the continuum limit (Goldstein-Kac theorem, 1951/1974). This is a standard result.
- Parameter identifications: τ = 1/(2λ), c = v, D = c²τ = v²/(2λ). These are definitional relations derived from the PRW balance equations.
- The telegrapher equation is mathematically equivalent to the Maxwell-Cattaneo equation and to Extended Irreversible Thermodynamics (EIT). The full master equation [ME] in C2 is structurally identical to EIT/GENERIC transport theory.

**Spatial Correlations:**
- In 2D, the steady-state spatial correlator of the telegrapher equation is C(r) = K₀(r/ξ_c), where K₀ is the modified Bessel function of the second kind and ξ_c = 2cτ is the correlation length. This is a correct mathematical consequence of the telegrapher Green's function.

**Quantum Channel Structure:**
- Assuming the coupling H_int = g J σ_z, the Born-Markov-Secular derivation yields a Lindblad master equation with L = σ_z. This is standard quantum optics.
- The structural bound T₂ ≤ 2T₁ follows from CPTP map positivity. This is a standard quantum information result.

**Dispersion Relations:**
- The telegrapher dispersion relation is ω(k) = ±√(c²k² − 1/(4τ²)) − i/(2τ). This follows from Fourier analysis of the telegrapher PDE.

### What These Results Represent

All of the above are either:
1. Standard mathematical theorems (Goldstein-Kac, CPTP bounds)
2. Mathematical reformulations of conventional physics (telegrapher ≡ Maxwell-Cattaneo ≡ EIT)
3. Conditional results that depend on independent assumptions (quantum coupling axioms)

None of these results constitute new physical content beyond conventional physics.

---

## 2. What C2 Does Not Establish

### Ontological Derivation

**The substrate is not identified:**
- C2 assumes the existence of an "information substrate" that implements the PRW dynamics.
- No physical realization of this substrate is derived from first principles.
- The FPUT lattice is taken as a microscopic model, but the physical FPUT parameters (mass, spring constant, lattice spacing) are not derived from any known material.
- The identification of the substrate with acoustic phonons (Extension A) or with TLS defects (Extension B) is postulated, not derived.

**Quantum structure is not derived:**
- The quantum Hilbert space ℂ², the Planck constant ℏ, and the Pauli operators σ_z are not derived from the PRW.
- The coupling constant g in H_int = g J σ_z is not derived from the substrate transport theory. It is introduced as a free parameter with dimensions [J·m²·s/info].
- The axioms M1 (matrix fields) and M2 (Moyal deformation) required for quantum reconstruction are independent postulates, not consequences of the transport layer.

**Key missing derivations (from C2_MISSING_PRINCIPLES.md):**
- ℏ is not derived; it enters as an empirical constant.
- Complex Hilbert space structure is not derived from the PRW alone.
- Measurement problem is not solved; decoherence ≠ collapse.
- The coupling constant g remains undetermined.

### Predictive Content

**No forward predictions exist:**
- All C2 "predictions" either (a) fit free parameters to data, (b) state consistency relations between free parameters, or (c) reproduce results already available from conventional models.
- The four free parameters (c, λ, g, S₀) are not independently constrained. None can be predicted before measurement.
- The trilinear prediction Γ_φ = K·r_q²·ω_rot²·τ contains the combination g²S₀ which is not resolvable from decoherence measurements alone.

**Distinction from conventional physics is not established:**
- Lorentzian S(ω) → identical to OU bath
- K₀ spatial correlator → identical to 2D screened diffusion Green's function
- ω_rot² Ramsey scaling → identical to filter function prediction for any Lorentzian bath
- Gaussian non-Markovian onset → universal for any Gaussian bath
- T₂ ≤ 2T₁ → standard CPTP bound
- Telegrapher dispersion → distinguishable from diffusion but not from phonon bath with Debye cutoff

### Experimental Discrimination

**No viable discriminative experiment exists:**
- The proposed K₀ spatial correlation test on IBM Brisbane cannot distinguish K₀ from power-law or multi-bath covariance.
- The causal wavefront test (C(r,t) = 0 for t < r/c) requires either c ≪ v_s (no physical substrate identified) or c = v_s (identical to phonon bath).
- No QPU observable has been identified that would rule out the strongest conventional null.

---

## 3. Independent Reconstruction of the Ontology-to-Observable Chain

### Axioms (Primitive Ontology)

**A-PRW1:** Walker speed v and flip rate λ are constant and uniform.
**A-PRW2:** Continuum limit Δx → 0, Δt → 0 at fixed v, λ.
**A-PRW3:** Markovian flip process.
**A-FPUT1:** Harmonic FPUT lattice as microscopic substrate (assumed, not derived).
**A-HC5, A-HC6:** Quantum coupling H_int = g J σ_z (assumed, not derived).
**M1, M2:** Matrix fields and Moyal deformation axioms (independent quantum postulates).

### Derived Equations

**PRW Balance Equations → Telegrapher:**
```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻
```
Under continuum limit: τ s_tt + s_t = c²τ ∇²s, with τ = 1/(2λ), c = v.
**Status:** Correct derivation, but telegrapher ≡ Maxwell-Cattaneo ≡ EIT.

**Telegrapher → Spatial Correlator:**
2D steady-state solution: C(r) = K₀(r/ξ_c), ξ_c = 2cτ.
**Status:** Correct derivation, but K₀ is also the Green's function of 2D screened diffusion: (∇² − ξ_c⁻²)G = −δ(r) → G = K₀(r/ξ_c)/(2π).

**Telegrapher → Temporal Correlator:**
C_JJ(t) = S₀ exp(−|t|/τ) → S_JJ(ω) = 2S₀τ/(1+ω²τ²).
**Status:** Correct derivation, but identical to OU process with single relaxation time.

**Quantum Coupling → Lindblad:**
H_int = g J σ_z + Born-Markov-Secular → Lindblad equation with L = σ_z.
**Status:** Standard quantum optics derivation, but H_int is an independent axiom.

**Lindblad → Decoherence:**
Γ_φ = g² S_JJ(ω_rot) / ℏ² = k_rot · ω_rot², with k_rot = 8g²S₀r_q²τ/(3ℏ²).
**Status:** Correct conditional derivation, but (i) ω_rot² scaling is a filter function consequence for any Lorentzian bath, (ii) k_rot contains free parameters g and S₀.

### Chain Summary

**Complete chain:**
[PRW axioms] → [telegrapher] → [correlators] → [quantum coupling axiom] → [Lindblad] → [decoherence observables]

**Break points:**
- PRW axioms → no physical substrate identified
- Quantum coupling → H_int is an independent axiom with free parameter g
- Decoherence → all observables reproduce conventional model predictions

**No link in this chain produces a prediction that is both (a) distinctive from conventional physics and (b) free of unfitted parameters.**

---

## 4. Parameter Identifiability

### Parameter Vector

θ = (c, λ, g, S₀)

All four are FREE PARAMETERS. None is derivable from C2 axioms without specifying a physical substrate.

- c: substrate propagation speed (free, no derivation)
- λ: substrate flip rate (free, no derivation)
- g: quantum-substrate coupling constant (free, no derivation)
- S₀: substrate noise amplitude (free, no derivation)

### Observable Vector

o = (Γ_φ, τ_B, ξ_c, k_rot)

Relations:
```
τ_B = 1/(2λ)
ξ_c = 2cτ_B = c/λ
k_rot = 8g²S₀r_q²τ_B/(3ℏ²)
Γ_φ = k_rot · ω_rot²
```

### Identifiability Analysis

**Jacobian rank:** ∂o/∂θ has rank 3.
**Null space dimension:** 1.
**Non-identifiable combination:** g²S₀ cannot be resolved into g and S₀ from decoherence measurements alone.

**Forward prediction status:**
- Γ_φ = k_rot·ω_rot²: NO (k_rot contains g·S₀, both free)
- τ_B from Ramsey curvature: NO (measurement, not prediction; λ is free)
- ξ_c from spatial data: NO (measurement, not prediction; c and λ are free)
- c = ξ_c/(2τ_B): NO (tautology; c is defined as this ratio)
- k_rot numerical value: NO (contains g and S₀, both free)

**Not one quantity is forward-predicted from independently known inputs.**

### Consistency vs. Prediction

The quantity c = ξ_c/(2τ_B) is often presented as a prediction. It is NOT:
- Step 1: Measure τ_B from Ramsey curvature → get a number
- Step 2: Measure ξ_c from spatial correlation → get a number
- Step 3: Compute c = ξ_c/(2τ_B) → get a number
- Step 4: Claim this c is the substrate propagation speed

This is a CONSISTENCY CHECK and PARAMETER ESTIMATION, not a prediction:
- C2 does not predict what value c will take before measurement
- Any measured value of c is consistent with C2 (c is free)
- The check cannot be falsified by any measured value of c

### Falsifiability vs. Distinctiveness

**Falsifiable statements:**
- Γ_φ ∝ ω_rot²: YES (if n ≠ 2 observed, falsified)
- C(r) has K₀ shape: YES (if clearly non-K₀, falsified)
- Single Lorentzian S(ω): YES (already falsified by IBM 1/f data)

**Falsifiability ≠ distinctiveness:**
- All falsifiable predictions are also produced by conventional models (OU bath, phonon bath, screened diffusion)
- Falsification of C2 would equally falsify those conventional models
- No prediction exists that would isolate C2 as the unique explanation

---

## 5. Conventional Null Coverage

### Observable-by-Observable Null Analysis

**Observable 1: Lorentzian Temporal PSD S(ω) = 2S₀τ/(1+ω²τ²)**
- Strongest null: Ornstein-Uhlenbeck (OU) bath
- OU autocorrelation: C(t) = S₀ exp(−|t|/τ) → S(ω) = 2S₀τ/(1+ω²τ²)
- Structural reason: Any Markovian Gaussian bath with single relaxation time τ gives a Lorentzian PSD (Wiener-Khinchin theorem)
- Verdict: FULLY REPRODUCED. Null is structural, not coincidental.

**Observable 2: K₀(r/ξ_c) Spatial Correlator**
- Strongest null A: 2D acoustic phonon bath with screening
- Strongest null B: 2D screened diffusion equation
- (∇² − ξ_c⁻²)G(r) = −δ(r) → G(r) = K₀(r/ξ_c)/(2π)
- This is a MATHEMATICAL FACT: K₀ is the fundamental solution of the 2D modified Helmholtz equation, shared by diffusion with exponential decay AND telegrapher
- Verdict: FULLY REPRODUCED by 2D screened diffusion. Not unique to telegrapher.

**Observable 3: Gaussian Non-Markovian Onset W(t)≈exp(−Γt−Gt²/2)**
- Strongest null: Kubo cumulant expansion
- For ANY zero-mean Gaussian stochastic process coupled to a qubit: W(t) = exp(−∫₀ᵗ (t−s) C(s) ds)
- Short-time expansion gives exactly exp(−Γt − Gt²/2) with G = C(0)
- This is model-independent — requires only Gaussian statistics and finite C(0)
- Verdict: FULLY REPRODUCED. Universal for any Gaussian bath.

**Observable 4: ω_rot² Ramsey Scaling Γ_φ = k_rot·ω_rot²**
- Strongest null: filter function argument (any bath)
- For a qubit rotating at ω_rot with Lorentzian PSD S(ω): Γ_φ = ∫ S(ω) |F(ω,ω_rot)|² dω
- For S(ω) ≈ const near ω_rot: Γ_φ ∝ S(ω_rot) · ω_rot² (from rotating-frame geometry)
- This holds for ANY bath with finite PSD at ω_rot and the same qubit rotation geometry
- Verdict: FULLY REPRODUCED. Geometric consequence of rotating-frame coupling.

**Observable 5: Causal Wavefront C(r,t)=0 for t < r/c**
- Strongest null A (diffusion): No wavefront. C(r,t) > 0 ∀ t > 0. DOES NOT reproduce.
- Strongest null B (phonon bath): Phonon bath has wavefront at t = r/v_s.
- Under Extension A (c=v_s): FULLY REPRODUCED by phonon bath.
- Under Extension B (c≪v_s): Wavefront at t = r/c ≫ T₂. INACCESSIBLE.
- Verdict: PARTIALLY REPRODUCED. Discriminates vs. diffusion-type models. Does NOT discriminate vs. phonon bath (the dominant physical null).

**Observable 6: T₂ ≤ 2T₁ Bound**
- Strongest null: standard quantum channel / Lindblad theory
- T₂ ≤ 2T₁ follows from the positivity of the Lindblad dissipator for any dephasing + relaxation combination
- This is a property of CPTP maps, not of the substrate
- Verdict: FULLY REPRODUCED. Standard quantum information result.

**Observable 7: Telegrapher Dispersion ω(k)**
- Strongest null: phonon bath with Debye cutoff
- Telegrapher: ω(k) = √(c²k²−1/(4τ²)) − i/(2τ)
- Phonon: ω = v_s k (linear); Debye cutoff at high k
- These are structurally different at k ~ 1/ξ_c
- BUT: the crossover scale ξ_c = 2cτ is FREE in C2
- Without a prior prediction of ξ_c (from material parameters), measuring the crossover gives ξ_c but cannot test C2 vs. phonon bath
- Verdict: UNDETERMINED. Would require prior prediction of ξ_c.

**Observable 8: Material Dependence ξ_c ∝ v_s(material) [Extension A]**
- Strongest null: acoustic phonon bath
- A phonon bath with ξ_corr ∝ v_s(material)·τ_B gives the same material scaling
- This is conventional phonon transport
- Verdict: FULLY REPRODUCED by phonon bath.

**Observable 9: Single Lorentzian per Qubit**
- C2 predicts a single Lorentzian (single τ_B) at each qubit
- Null: Standard TLS bath with uniform density → approximately Lorentzian
- Reality: IBM qubit spectra show 1/f component (distribution of τ_B values)
- The single-Lorentzian prediction is SIMPLER than conventional physics (which has multiple TLS with different τ_B) and INCONSISTENT with measured IBM noise
- Verdict: REFUTED by existing data. Not merely reproduced by null — the null (full TLS bath) is MORE accurate.

### Null Coverage Summary

| Observable | Strongest null | Reproduced? |
|-----------|---------------|-------------|
| Lorentzian S(ω) | OU bath | FULLY |
| K₀ spatial | 2D screened diffusion | FULLY |
| Gaussian NM onset | Kubo expansion (any Gaussian bath) | FULLY |
| ω_rot² Ramsey | Filter function (any Lorentzian bath) | FULLY |
| Causal wavefront | Phonon bath | FULLY under Ext A; INACCESSIBLE under Ext B |
| T₂≤2T₁ | Standard CPTP | FULLY |
| Telegrapher dispersion | Phonon + Debye | UNDETERMINED (ξ_c free) |
| Material ξ_c scaling | Phonon bath | FULLY |
| Single Lorentzian | TLS bath (multiple) | REFUTED by IBM data |

**The conventional null coverage is EXHAUSTIVE. No C2 observable escapes.**

---

## 6. QPU Experimental Meaning

### Proposed Experiment: K₀ Spatial Correlation Test

**What is claimed:**
The spatial decoherence correlator follows C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c), distinguishing C2 from conventional exponential correlations.

**What is actually measured:**
C_ij(t) = ⟨σ_{x,i}(t)·σ_{x,j}(t)⟩ / (⟨σ_{x,i}(t)⟩·⟨σ_{x,j}(t)⟩) via parity estimator from simultaneous two-qubit X-basis measurement.

**What the null models are:**
- M0: Independent Markovian
- M2: Single exponential / OU
- M5: EM/circuit crosstalk
- M7_pow0.5: Power-law alpha=0.5
- M7_pow1.0: Power-law alpha=1.0
- M8: Gaussian covariance
- M9: Two-bath exponential
- M10: Stretched exponential
- M11: Matérn (nu=1.5)

**Experimental discrimination analysis:**
- The K₀ shape is distinguishable from exponential (M2) but NOT from power-law (M7) or two-bath (M9) over the accessible spatial range (r = 200–2200 µm)
- LLR distributions: K0 vs M7 separation = 0.42 units, far below noise width
- The test cannot discriminate K0 from M7/M9 at any shot count or ξ_c value

**What parameters are free:**
- ξ_c = 2c·τ_B: FREE — c not predicted by C2
- sub_frac (amplitude): FREE — coupling g unknown
- Neither ξ_c nor the amplitude is independently predicted

**What result would rule out the strongest conventional null?**
**No answer exists.** Even if K₀ is measured, the result is equally consistent with power-law covariance (M7) or multi-bath exponential (M9), both of which are physically motivated for superconducting chips.

**QPU experimental classification:**
**D — INCONCLUSIVE / NOT IDENTIFIABLE**

The measurement is physically legitimate but the available hardware/noise/geometry cannot distinguish the hypotheses. The proposed experiment would establish that "some spatial correlation exists that is better described by K₀ than by a single exponential." It would NOT establish that "the spatial correlation is inconsistent with conventional physics" or that "SXC-IGC is correct."

**No QPU experiment is justified.**

---

## 7. Evidence For SXC-IGC

**List only evidence that actually supports SXC-IGC as a distinct physical theory.**

**NONE.**

**Mathematical consistency is not evidence of physical truth.**
- The PRW → telegrapher derivation is mathematically correct, but this is a standard result equivalent to conventional physics.
- The telegrapher → K₀ correlator derivation is mathematically correct, but K₀ is also the Green's function of 2D screened diffusion.
- The quantum coupling → Lindblad derivation is mathematically correct, but the coupling itself is an independent axiom.

**Reproduction of known results is not evidence of distinctiveness.**
- Reproducing Mercury precession (via fitting) is not evidence.
- Reproducing ω² decoherence scaling (via filter function geometry) is not evidence.
- Reproducing Lorentzian noise spectra (via OU bath equivalence) is not evidence.

**No evidence exists that SXC-IGC is a distinct physical theory rather than a reformulation of conventional physics with additional free parameters.**

---

## 8. Evidence Against SXC-IGC

### A. Evidence That Falsifies C2

**Single Lorentzian prediction refuted by data:**
- C2 predicts a single Lorentzian (single τ_B) at each qubit
- IBM qubit spectra show 1/f component (distribution of τ_B values)
- The conventional TLS bath model (with multiple τ_B) is MORE accurate than the C2 prediction
- This is direct falsification of a specific C2 claim

### B. Evidence That Shows Underdetermination

**Four free parameters, three independent observables:**
- θ = (c, λ, g, S₀)
- o = (Γ_φ, τ_B, ξ_c, k_rot)
- Jacobian rank = 3, null space dimension = 1
- The combination g²S₀ is not resolvable from decoherence measurements alone
- Structural underdetermination: even with perfect measurements, C2 parameters cannot be uniquely determined

**All observables reproduced by conventional nulls:**
- Lorentzian S(ω) → OU bath
- K₀ spatial → 2D screened diffusion
- ω_rot² scaling → filter function geometry
- Gaussian onset → Kubo expansion
- T₂ ≤ 2T₁ → CPTP positivity
- Material scaling → phonon bath
- Causal wavefront → phonon bath (under Extension A)

**No observable exists that is both distinctive and accessible.**

### C. Evidence That Shows Conventional Equivalence

**Telegrapher ≡ Maxwell-Cattaneo ≡ EIT:**
- The full master equation [ME] is mathematically equivalent to Extended Irreversible Thermodynamics
- No new transport structure is introduced by C2

**K₀ ≡ Screened Diffusion Green's Function:**
- (∇² − ξ_c⁻²)G = −δ(r) → G = K₀(r/ξ_c)/(2π)
- This is a mathematical identity, independent of the underlying dynamics
- The K₀ spatial shape is not unique to telegrapher dynamics

**Quantum coupling ≡ Standard System-Bath Model:**
- H_int = g J σ_z is the standard longitudinal coupling form
- The resulting Lindblad equation is standard quantum optics
- No new quantum mechanism is introduced

**Summary:**
C2 is not falsified as a mathematical framework, but it is empirically equivalent to conventional physics in its present formulation. Every physical prediction is either (a) reproduced by a simpler conventional model or (b) contains free parameters that prevent forward prediction.

---

## 9. What Remains Scientifically Valuable

### Mathematical Results (Independent of Physical Ontology)

**The PRW → Telegrapher Derivation:**
- The Goldstein-Kac theorem derivation from PRW balance equations is correct and pedagogically valuable
- This is a standard result but the presentation in C2 is rigorous and clear

**The Telegrapher Green's Function Analysis:**
- The derivation of the K₀ spatial correlator from the telegrapher equation is correct
- The recognition that K₀ is also the screened diffusion Green's function is an important observation

**Stress-Testing Methodology:**
- The adversarial self-testing approach (12 stress tests, systematic assumption tracking, status classification) is methodologically excellent
- The prediction discovery program (systematic search through 26 candidates, elimination table) is rigorous and honest

**Honest Failure Reporting:**
- The explicit documentation of failed proofs (e.g., quantum state space CP¹ ≅ S² does not emerge from PRW) is scientifically valuable
- The distinction between derived, constitutive, and conjectural results is maintained consistently

### Methodological Value

**Parameter Identifiability Analysis:**
- The systematic construction of the parameter → observable map, rank analysis, and null space identification is rigorous
- The distinction between consistency checks and forward predictions is clearly articulated

**Conventional Null Exhaustion:**
- The systematic construction of the strongest conventional null for every observable is methodologically sound
- The recognition that conventional null coverage is exhaustive is important

**Experimental Design Rigor:**
- The pre-hardware gate analysis (12-condition checklist, power analysis, false positive control) is exemplary
- The honest conclusion that the proposed experiment is non-discriminating despite being implementable is scientifically correct

### What Is Not Valuable As Distinct Physics

**The Physical Ontology:**
- The "information substrate" concept is not identified with any known physical system
- The SXC-IGC interpretation of the substrate is not supported by empirical evidence
- The quantum-gravity unification claims are not substantiated (they involve constitutive assumptions rather than derivation)

**The "Predictions":**
- All claimed predictions are either conventional reformulations or contain free parameters
- No forward-predictive content exists

**The Substrate Identification Routes:**
- FPUT route → conventional phonons (Extension A)
- TLS route → requires new physics assumptions not in C2 (Extension B)
- No physically credible substrate is identified that provides discriminating power

---

## 10. Final Verdict

### PRIMARY QUESTION ANSWERED

**Does the current SXC-IGC/C2 framework contain any physical content that is genuinely new and empirically distinguishable from conventional physics?**

**NO.**

### REASONING

1. **Mathematical Equivalence:** The transport layer (telegrapher equation) is mathematically equivalent to Maxwell-Cattaneo/EIT. No new transport structure is introduced.

2. **Conventional Null Coverage:** Every C2 observable is fully reproduced by a conventional null model (OU bath, phonon bath, screened diffusion, standard quantum channel theory).

3. **Parameter Underdetermination:** Four free parameters (c, λ, g, S₀) with only three independent observable combinations. No forward predictions exist.

4. **No Substrate Identification:** No physical substrate is identified that provides discriminative power. The FPUT route gives conventional phonons; the TLS route requires new physics assumptions.

5. **No Viable Experiment:** The proposed QPU experiment cannot discriminate K₀ from power-law or multi-bath covariance on available hardware.

6. **All "Predictions" Are Either Reformulations or Fittings:**
   - Lorentzian S(ω) → OU bath equivalence
   - K₀ spatial → screened diffusion equivalence
   - ω_rot² scaling → filter function geometry
   - Mercury precession → fitted to known result
   - Gaussian onset → universal for Gaussian baths

7. **Quantum Coupling Is Independent Axiom:** H_int = g J σ_z is assumed, not derived. The coupling constant g is free and undetermined.

8. **No Evidence For Distinctive Ontology:** No evidence exists that SXC-IGC is a distinct physical theory rather than a reformulation of conventional physics with additional free parameters.

### FINAL VERDICT

**C: C2 is mathematically valid but empirically equivalent to conventional physics in its present formulation.**

This conclusion is based on:
- The exhaustive conventional null coverage analysis
- The parameter identifiability analysis showing structural underdetermination
- The absence of any forward-predictive content
- The equivalence of all derived equations to conventional physics
- The failure of the substrate identification routes to provide discriminating power
- The non-discriminating nature of the proposed QPU experiment

The framework is mathematically consistent and methodologically rigorous, but it does not contain genuinely new physical content distinguishable from conventional physics. All physical predictions are either reformulations of known results or contain free parameters that prevent forward prediction.

### IMPLICATIONS

**No QPU experiment is justified.** The proposed spatial correlation test cannot discriminate between C2 and conventional null models on available hardware.

**No theoretical rescue route is justified within existing C2.** The ontology-to-observable chain has been exhaustively audited. Every branch terminates in either conventional equivalence or inaccessible free parameters.

**The repository has value as a research notebook and methodological example, but not as evidence for a distinct physical theory.** The stress-testing methodology, honest failure reporting, and systematic null construction are scientifically valuable even though the physical ontology is not supported.

---

*End of Independent Adversarial Verdict*
*Date: 2026-08-22*
*Classification: C — Mathematically valid but empirically equivalent to conventional physics*
