# FINAL_THEORY_PREDICTIVITY_AUDIT.md
## SXC-IGC/C2 — Adversarial Theory Predictivity Audit

**Date:** 2026-08-22
**Mandate:** Determine whether C2 contains a real, non-circular route to a
  predictive physical theory. Classify as R0/R1/R2/R3.
**Sources:** All prior audit documents, plus direct inspection of:
  C2_FOUNDATIONS.md, C2_FRONTIER_MAP.md, C2_MISSING_PRINCIPLES.md,
  substrate_transport_derivation.md, 00_THEORY_AUDIT.md,
  32_C_FIRST_PRINCIPLES_DERIVATION.md, 32_C_PRW_SPEED_DERIVATION_AUDIT.md,
  33_C_CORRELATION_LENGTH_CONSEQUENCE.md, INVARIANT_AUDIT.md,
  FOUNDATIONAL_ADVERSARIAL_FINAL_AUDIT.md, FOUNDATIONAL_FINAL_VERDICT.md,
  projection_classification_audit.md (via audit chain)

**Label convention:**
THEOREM: proved from stated premises
CONDITIONAL: proved given an identified assumption
IDENTIFICATION: physical argument, not mathematical theorem
NEW AXIOM: not in current C2
CONJECTURE: unproved claim in the theory
TAUTOLOGY: true by definition, zero predictive content
FREE: undetermined by any C2 equation

---

## 1. EXECUTIVE VERDICT

**Classification: R2 — C2 REQUIRES A NEW THEORY EXTENSION**

The existing C2 foundations contain one partially legitimate route to
constraining c — the FPUT/phonon physical identification — but this route
requires a named physical postulate ([PHON]) that is NOT derivable from
the existing C2 axioms. It is an IDENTIFICATION, not a DERIVATION.

Accepting [PHON] with appropriate transparency creates a concrete, testable
extension of C2 with specific numerical predictions. Rejecting [PHON] leaves
the theory at R3. The decision between R2 and R3 therefore turns entirely
on whether [PHON] can be justified as physically necessary rather than merely
compatible — which is the precise question the existing theory cannot answer
from within.

The following sections prove this conclusion through the complete audit.

---

## 2. COMPLETE DEPENDENCY GRAPH

### 2.1 Layer structure

```
LAYER 0: CCA Primitives (Ax1–Ax5)
  Objects O, morphisms M, composition ⊗, causal order ≤, dagger †, weights ε
  ↓ No velocity, no ℏ, no Hilbert space, no mass
  
LAYER 1: SCC (adds M1–M8, compactness AA1, complex vector space M8)
  M8 NOT derivable from M1–M7 [FOUNDATIONAL_ADVERSARIAL_FINAL_AUDIT §4]
  ↓ Still no velocity, no c
  
LAYER 2: FPUT chain + admissibility constraints C1–C6
  FPUT Hamiltonian H = Σ[p²/2m + K(Δq)²/2]  [ASSUMED — substrate model]
  Normal modes ωₖ = 2√(K/m)|sin(πk/N)|  [DERIVED — Fourier diagonalisation]
  Actions nₖ = |Aₖ|²  constant  [DERIVED — harmonic integrability]
  Acoustic speed v_s = a√(K/m)  [DERIVED — k→0 group velocity]
  C3: signal speed ≤ v_s  [DERIVED from C3 + FPUT acoustics — INEQUALITY]
  
LAYER 3: PRW / Telegrapher (P1 projection)
  Unique admissible projection: P1 (right-action phonons)  [DERIVED — FPUT-3]
  Transport equations: ∂ₜn± ± v_PRW ∂ₓn± = ∓γ(n±−n∓)
  v_PRW = ?  ← THIS IS THE GAP
  
LAYER 4: Transport parameters
  τ_B = 1/(2γ)  [DERIVED from P1 reversal rate]
  ξ_c = v_PRW/γ = 2·v_PRW·τ_B  [DERIVED from v_PRW and γ — but v_PRW free]
  D = v_PRW²·τ_B  [DERIVED — ditto]
  
LAYER 5: Quantum coupling
  H_int = g·J·σ_z  [ASSUMED — A-HC5]
  Lindblad: Γ_φ = k_rot·ω_rot²  [DERIVED conditional on ≥10 assumptions]
  g  [FREE — F10]
  
LAYER 6: Observable predictions
  S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)  [DERIVED — does NOT contain v_PRW]
  C_Γ(r) = K₀(r/ξ_c)  [DERIVED — CONTAINS v_PRW through ξ_c]
  Γ_φ = k_rot·ω_rot²  [DERIVED conditional — does NOT contain v_PRW]
```

### 2.2 The gap location

v_PRW appears in ξ_c and nowhere else in observable predictions.
The gap is structural: FPUT-3 derives the FORM of the telegrapher equation
and proves the projection is unique, but does not specify the numerical
value of v_PRW within that telegrapher equation.

### 2.3 Free parameters after complete dependency tracing

| Parameter | Layer | Dependencies | Status |
|-----------|-------|-------------|--------|
| v_PRW | 3 | FPUT Hamiltonian (but see §3.3) | **GAP** |
| γ (= λ) | 3 | None in C2 — relaxation rate free | FREE |
| g | 5 | None in C2 | FREE |
| s₀ | 4 | None in C2 | FREE |
| FPUT parameters (a, K, m) | 2 | Substrate model choice | EMPIRICAL |

---

## 3. GAP-7 REANALYSIS — BEYOND THE PRIOR AUDIT

### 3.1 What the prior audit established

GAP7_REDERIVATION.md: all 25 routes failed or were blocked.
The structural proof: models (v, λ) and (αv, λ) are both valid for any α > 0.

This is confirmed. The prior audit is correct within its scope.

### 3.2 What the prior audit may have underweighted

Document 32 (32_C_FIRST_PRINCIPLES_DERIVATION.md) reaches a conclusion the
prior audit categorised as FAILED (Route 5) but which deserves more precise
classification. The document concludes:

> "c = v_PRW = v_s = a√(K/m) is derived, not postulated, conditional on the
>  standard hydrodynamic coarse-graining limit that defines the PRW from the FPUT chain."

This is stronger than Route 5's conclusion, which treated the identification
as merely compatible with FPUT. Document 32 argues it is the NATURAL identification
that follows from the definition of n± as acoustic phonon densities.

The precise question is: is the identification [PHON] a mathematical theorem
or a physical assumption?

### 3.3 The [PHON] identification — precise status

**What [PHON] asserts:**
The PRW particles in C2 are identified with acoustic phonons of the physical
substrate (chip material). Therefore v_PRW = v_s = a√(K/m).

**What FPUT-3 proves:**
The unique admissible P1 projection produces transport equations where n±
move at speed v_PRW. FPUT-3 does NOT specify what v_PRW is numerically
within those equations. It proves uniqueness of the functional form (PRW),
not uniqueness of the speed parameter.

**What the P1 equations use:**
The P1 governing equations in projection_classification_audit.md write
v_s explicitly in the n± transport. This is because n± are DEFINED as
right/left-moving acoustic phonon action densities. The acoustic phonon speed
IS v_s by definition of the phonon. Therefore within the P1 model as explicitly
stated, v_PRW = v_s.

**The logical structure:**
```
P1 is defined as: n±(x) = Σₖ nₖ w±ₖ(x)
                  where w±ₖ groups modes by sign of ∂ωₖ/∂k
→ by construction, n± move at the GROUP VELOCITY of those modes
→ in the k→0 (acoustic) limit, group velocity = v_s = a√(K/m)
→ therefore v_PRW = v_s IN THE P1 MODEL AS DEFINED
```

**Is this a theorem?**
DERIVATION: v_PRW = v_s follows from the definition of n± via acoustic phonon
group velocity, given the FPUT Hamiltonian. Within the P1 model as stated, it
is not a free parameter — it IS v_s.

But: the statement "the C2 substrate is described by P1 where n± are acoustic
phonon densities of the physical chip material" requires identifying the abstract
mathematical substrate with a specific physical medium. This step is NOT
mathematical — it is an empirical identification.

**Precise classification:**

```
v_PRW = v_s  is:
  - DERIVED within the P1 model as defined [CONDITIONAL DERIVATION]
  - IDENTIFIED by equating P1 phonons with physical chip phonons [IDENTIFICATION]
  - NOT a pure mathematical theorem from C2 axioms alone [NOT THEOREM]
```

The [PHON] identification is the ONLY step that requires external input.
Everything else in the chain from FPUT Hamiltonian → v_s → ξ_c is mathematically
rigorous conditional on [PHON].

### 3.4 Can [PHON] be derived from existing C2?

**Attempt:** Does any C2 axiom or theorem compel the identification of PRW
particles with acoustic phonons rather than with some other physical degree
of freedom?

**Test: Rescaling argument**
Consider the same FPUT chain but define n± differently — as right/left-moving
excitations at some fraction α·v_s (α < 1). Do these still satisfy the C1–C6
admissibility constraints?

- C1 (Locality): n±(x) based on spatial windows at scale ℓ_CG >> a — satisfied for any α
- C2 (Conservation): total action nₖ conserved — satisfied regardless of the speed convention
- C3 (Finite speed ≤ v_s): α·v_s ≤ v_s — satisfied for 0 < α ≤ 1
- C4 (Positivity): densities ≥ 0 — satisfied for any α
- C5 (Closure): ∂_t of the new n± expressible as function of themselves — this is the critical test

For C5 (closure): if n± move at αv_s, the balance equations become:
```
∂_t n⁺ + αv_s ∂_x n⁺ = −γ(n⁺ − n⁻) + [non-closed terms]
```
The "non-closed terms" appear because modes with group velocity ≠ αv_s exist in the
FPUT chain but are not included in the n± definition. For α = 1 (acoustic modes only),
closure holds because long-wavelength acoustic modes form an approximately closed set
under the linear dynamics. For α < 1, closure requires including modes with different
group velocities, which contaminate the n± fields and break C5.

**Conclusion:** C5 (closure) is only satisfied in the acoustic limit α = 1 (v_PRW = v_s).
Any PRW with v_PRW < v_s would have non-closed dynamics — acoustic modes with
group velocity > v_PRW would leak out of the n± description. Therefore C5 forces
v_PRW = v_s if the substrate is the acoustic FPUT chain.

**This is the key finding not previously established in the audit documents.**

The derivation:
```
FPUT chain (ASSUMED: substrate model)
  + admissibility C5 (Closure)
  → v_PRW must equal the acoustic group velocity v_s
  → [PHON] identification is forced by C5, not merely compatible with it
  → v_PRW = v_s = a√(K/m)  [CONDITIONAL DERIVATION given FPUT substrate assumption]
```

**Condition:** This derivation holds IF the C2 substrate is modelled by a harmonic
FPUT chain. The FPUT chain is the substrate model used throughout C2, but it is itself
an ASSUMPTION (A-FPUT1 in C2_FOUNDATIONS.md, "ASSUMED — substrate model").

---

## 4. HIDDEN-CONSTRAINT SEARCH

### 4.1 CCA causal structure

The CCA has a causal partial order (≤). Could this order constrain v?

**Scaling test:** Apply v → αv. The CCA structure involves morphisms M,
composition ⊗, causal order ≤, and probability weights ε. None of these
involve a velocity. The CCA is a discrete/finite structure (Ax1: finite hom-sets).
No velocity appears in Ax1–Ax5.

**Conclusion:** v → αv is a symmetry of the CCA. CCA does not constrain v.

### 4.2 SCC structure

SCC requires a compact symmetry group G acting on state space S. The propagation
speed v is not an element of G or S — it is a property of the dynamical evolution
between states. SCC axioms {C,S,I,N} make no reference to a velocity.

**Scaling test:** v → αv with G fixed. SCC structure unchanged.

**Conclusion:** SCC does not constrain v.

### 4.3 Causal-action principle (CCA-C3)

CCA-C3 (conjecture): physically realised morphisms extremise S_causal = −log ε(m) + r(m).

If proved, this would determine probability weights ε, not the propagation speed v.
The causal action is defined over morphisms; v enters through the evolution equations
that generate morphisms, not through S_causal itself.

**Conclusion:** CCA-C3 (even if proved) does not constrain v. CONJECTURE → INAPPLICABLE.

### 4.4 Conservation laws

Only one exact conservation law: Q = ∫s dx (total information).
This holds for all v > 0. No additional conservation law appears in C2.

**Conclusion:** Conservation laws do not constrain v.

### 4.5 Detailed balance / equilibrium

The PRW equilibrium: n⁺* = n⁻* (equal populations). This holds for any v.

**Conclusion:** Detailed balance does not constrain v.

### 4.6 Information-flow constraints

C2 predicts finite signal speed ≤ v (telegrapher causality cone). The information
flow is bounded by v but does not fix v.

**Conclusion:** Information flow constraints bound v from above (v must be finite),
but provide no lower bound or specific value.

### 4.7 C5 Closure — the ONE non-trivial constraint (new finding)

As derived in §3.4: the C5 admissibility constraint forces v_PRW = v_s IF the
substrate is the FPUT chain. This is not a pure CCA/SCC constraint — it requires
the FPUT substrate assumption. But conditional on that assumption, C5 is NOT a
free-choice constraint — it FORCES v = v_s.

**This is the only constraint on v found in the entire theory.**

### 4.8 Quantum consistency

The quantum coupling H_int = g·J·σ_z. The dephasing rate Γ_φ does not contain v.
Quantum consistency (Born-Markov, secular, stationary) places no constraint on v.

**Conclusion:** Quantum consistency does not constrain v.

### 4.9 Dimensional analysis with all C2 quantities

Full set: {v [m/s], γ [s⁻¹], g [J·m²·s], s₀ [m⁻³], ℏ [J·s], a [m], K [N/m], m [kg]}.

From {a, K, m}: v_s = a√(K/m) [m/s] — this IS a velocity formed from FPUT parameters.

The ratio v/v_s is dimensionless. C5 forces this ratio to equal 1.
No other combination produces a dimensionless number that fixes v independently.

**Conclusion:** The only dimensionless combination involving v that is fixed by the
theory is v/v_s = 1 (conditional on FPUT substrate and C5 closure).

---

## 5. T1 — SUBSTRATE IDENTIFICATION ANALYSIS

### 5.1 The [PHON] candidate

**Candidate:** The C2 substrate corresponds to acoustic phonons of the physical chip material.

**C2 quantity identified with physical degree of freedom:**
n±(x) = right/left-moving acoustic phonon action density in the chip material.

**Why identification is necessary rather than merely compatible:**
From §3.4: C5 (Closure) forces v_PRW = v_s when the substrate is modelled by
the FPUT chain. The FPUT chain itself is the modelling assumption. But if one
accepts the FPUT chain as the substrate model, C5 forces the phonon identification.
This makes the identification FORCED-BY-C5 rather than merely compatible.

However: the FPUT chain is itself an ASSUMPTION (A-FPUT1), not a derived result.
The chain from assumption to forced identification is:

```
[ASSUMPTION A-FPUT1: substrate is FPUT chain]
  + [DERIVED: C5 forces v_PRW = v_s within FPUT]
  → c = v_s = a√(K/m)  [CONDITIONAL DERIVATION]
```

The identification is therefore necessary GIVEN A-FPUT1, but A-FPUT1 itself is
not derived from anything more fundamental in C2.

**Derived propagation velocity:**
c = v_s = a√(K/m)

For Si chip material: a ≈ 5.43 Å (crystal lattice constant), K/m ≈ (v_s/a)²
Using known Si acoustic speed v_s ≈ 6000 m/s:
c = 6000 m/s (Si longitudinal acoustic)

This is a SPECIFIC NUMERICAL PREDICTION conditional on [PHON] + [Si chip].

**Additional independent predictions from [PHON]:**

Given c = 6000 m/s and measured τ_B:

1. ξ_c = 2c·τ_B = 2 × 6000 × τ_B [m]
   For τ_B = 1.2 µs: ξ_c = 1.44 cm (Eagle chip scale)
   
2. Temperature dependence: c(T) = v_s(T) which for Si decreases as T increases.
   c(T) ≈ c₀·(1 − α_T·T) where α_T ≈ 6×10⁻⁵ K⁻¹ for Si
   → ξ_c(T) = 2v_s(T)·τ_B(T) with v_s(T) following Si acoustics

3. Material dependence: c differs between chip materials:
   Si: v_s ≈ 6000 m/s
   Al (Josephson junctions): v_s ≈ 6420 m/s  
   Nb (control lines): v_s ≈ 3480 m/s
   → Different chip materials → different ξ_c at same τ_B

4. Isotropy: acoustic phonons in Si are anisotropic (different speeds along [100] vs [110]).
   The substrate model is 1D PRW. In a 2D chip, the relevant speed depends on the phonon
   polarisation and propagation direction. For [110] direction (typical qubit layout):
   v_[110] ≈ 5080 m/s (Rayleigh/surface) to 8400 m/s (bulk longitudinal).

**Are these predictions distinguishable from conventional physics?**

The conventional phonon bath predicts ξ_phonon/(2τ_phonon) ≈ v_s — the same value.
Therefore: IF the substrate is acoustic phonons, the C2 prediction c = v_s is
IDENTICAL to the conventional phonon bath prediction c = v_phonon = v_s.

**This is the critical failure of [PHON]:**
Identifying the C2 substrate with acoustic phonons produces predictions that are
indistinguishable from a conventional phonon bath model. The [PHON] identification
does not add discriminating power — it makes C2 equivalent to the phonon null model.

**Verdict on [PHON]:**
- Logically consistent and partially forced by C5 given A-FPUT1
- Produces specific numerical predictions
- Does NOT distinguish C2 from a conventional phonon bath
- The conventional phonon bath (M7-like, M9-like) is exactly the adversarial null
  that defeats the K₀ spatial test (ADVERSARIAL_NULL_AUDIT.md)

**[PHON] fails Task D:** The identification with acoustic phonons produces predictions
equivalent to the conventional phonon bath and therefore does not provide experimental
discrimination between C2 and conventional physics.

### 5.2 Other candidate substrates

**Candidate: Slow surface modes (Rayleigh phonons, surface acoustic waves)**
v_SAW ≈ 3000–5000 m/s in Si.
Same problem: a conventional SAW bath model produces the same PSD and spatial
covariance. The identification does not add discrimination.

**Candidate: Novel slow substrate (v ≪ v_s)**
For c ~ 50–500 m/s: no conventional mechanism exists. This would be genuinely
discriminating (P3 would be anomalous). But:
- C5 forces v = v_s within the FPUT model — a slow mode violates C5 unless a different
  substrate model is used
- A different substrate model would be a NEW AXIOM (different from A-FPUT1)
- This path requires proposing a non-FPUT substrate — which is an extension of C2

**Candidate: EM modes**
c = c_EM ≈ 2×10⁸ m/s. At τ_B = 5 µs: ξ_c = 2000 m >> chip size.
Completely inaccessible. Also consistent with conventional EM coupling.

**Conclusion on T1:**
No substrate identification produces a prediction that is simultaneously:
(a) forced by existing C2 structure (rather than merely compatible)
(b) numerically specific
(c) distinguishable from conventional mechanisms

The acoustic phonon identification satisfies (a) and (b) but fails (c).
A slow-mode identification would satisfy (b) and (c) but fails (a) — it requires
a new substrate model not in C2.

---

## 6. T2 — NEW AXIOM ANALYSIS

### 6.1 CCA-C3 (causal action conjecture)

**Statement:** Physically realised morphisms extremise S_causal = −log ε(m) + r(m).
**Status:** CONJECTURE — unproved (C2_FRONTIER_MAP.md, F9 classification).

**Can CCA-C3 constrain v?**
If proved, CCA-C3 determines the probability weights ε over morphisms.
The propagation speed v enters through the dynamical content of morphisms
(how far information travels per step), not through ε. The causal action
extremisation selects which physical processes occur, not how fast they propagate.

CCA-C3 does not contain v. Even if proved, it would not constrain v.

**Verdict:** CCA-C3 is inapplicable to GAP-7. Even proved, it leaves v free.

### 6.2 Large-N universality (CCA-MC: OBS-C1 conjecture)

**Statement:** In the N → ∞ limit of a framework satisfying U1–U6, complex phase
coherence (O1) and continuous fields (O2) emerge generically.
**Status:** CONJECTURE — the central unproved question of the entire project.

**Can this constrain v?**
If O2 (continuous fields) emerges in the N→∞ limit, the continuum theory would
have a characteristic propagation speed. Whether that speed is determined by the
discrete structure or is still free depends on the details of the N→∞ limit.

In the known analogues: the causal set continuum limit (Bombelli-Lee-Meyer-Sorkin)
produces Lorentzian geometry up to conformal factor — the conformal factor
(which encodes the metric scale, hence speed) remains a free parameter even in
the large-N limit.

**Verdict:** The large-N conjecture (if proved) would establish that C2 generates
a continuous theory, but would NOT fix the propagation speed. The conformal
freedom remains. This conjecture is inapplicable to GAP-7.

### 6.3 Microscopic reversibility (PA1)

**Statement:** The dynamical evolution is invertible.
**Status:** OPEN PROBLEM F1 — derivation blocked, requires AA2.

**Can PA1 constrain v?**
PA1 requires the evolution to be a bijection on state space. This is a reversibility
condition, not a speed condition. PA1 holds for any v > 0 (the telegrapher equation
is time-reversible for any v). PA1 does not constrain v.

**Verdict:** PA1 inapplicable to GAP-7.

### 6.4 New axiom that COULD work: FPUT substrate identification

The only structure that constrains v comes from A-FPUT1 + C5 closure (§3.4).
If A-FPUT1 is promoted from a modelling choice to a fundamental axiom of C2:

```
NEW AXIOM [A-FPUT-FUND]:
  "The C2 information substrate is physically realised as the acoustic phonon
   field of the underlying physical medium (chip material, laboratory crystal,
   or gravitational background as appropriate to the scale)."

What C2 does not currently imply:
  A-FPUT1 is currently a modelling assumption within the P1 derivation.
  It is not derived from CCA/SCC axioms or from any informational principle.
  Nothing in C2 requires the substrate to be acoustic rather than optical,
  electromagnetic, gravitational, or novel.

New predictions if adopted:
  1. c = v_s(material) — material-specific, measurable independently
  2. ξ_c = 2v_s(material)·τ_B — numerical prediction given τ_B measurement
  3. c(T) ∝ v_s(T) — follows material acoustics
  4. c differs between chip materials at same τ_B

Degrees of freedom removed: 1 (v from free to fixed by material)
Remaining free parameters: γ (= λ), g, s₀ — still 3 free

Empirical consequences:
  If the substrate is acoustic Si phonons:
    c = 6000 m/s → ξ_c = 1.44 cm at τ_B = 1.2 µs
    This is in principle measurable on an Eagle-scale chip with:
    - τ_B ~ 1.2 µs (not 5 µs — must be confirmed, not chosen)
    - 127 qubits with 14 mm physical span
    - Independent τ_B measurement from Ramsey (NMP ~ 0.37 — accessible)

Problem:
  With c = v_s = 6000 m/s, the C2 substrate is physically equivalent to
  a conventional acoustic phonon bath. The K₀ spatial shape test becomes
  a test of the telegrapher (K₀ shape) vs diffusion (exponential shape) limit
  of phonon-mediated decoherence — a legitimate physics question, but one
  that conventional phonon bath models can also answer. The adversarial null
  (M7 power-law, M9 two-bath) still applies. [PHON] does not remove those nulls.
```

**Verdict:** [A-FPUT-FUND] is the best available new axiom. It is:
- Physically motivated by the FPUT construction
- Forced by C5 once the substrate model is accepted
- Produces specific numerical predictions
- But does NOT produce a prediction distinguishable from conventional phonon bath

---

## 7. FULL-THEORY PREDICTION SEARCH

### 7.1 Search scope

Expanded beyond decoherence and spatial correlations. Searched:
- Q diagnostic and its applications
- CCA entropy structure
- SCC representation theory
- Gravitational sector (none exists)
- Non-Gaussian statistics
- Multi-time correlations
- Relations between decoherence and other observables

### 7.2 Q diagnostic

Q(x,t) = 4c²τ²|∇ ln s|² − 1

This is a local stability classifier. Its only observable consequence for qubits
is the transition between overdamped (Markovian) and oscillatory (non-Markovian)
decoherence, characterised by the ωτ criterion. This is equivalent to the standard
Lorentzian bath crossover, which is conventional. Q provides no new observable
that conventional physics cannot reproduce.

### 7.3 The T₂ ≤ 2T₁ structural bound

Derived from the substrate (C2_FOUNDATIONS.md Theorem HC-4, Q-4).
This is the standard quantum channel bound, derivable from the Lindblad structure
alone without the substrate framework. Zero discriminating content. CONVENTIONAL.

### 7.4 Non-Markovian decay shape

The exact dephasing function Φ(t) = Γ_Markov·τ_B·[t/τ_B − 1 + exp(−t/τ_B)]
is derived [T] from the C_JJ = S₀·exp(−t/τ_B) autocorrelation.

This specific form is also the exact result for ANY OU bath with the same
autocorrelation. The form W(t) = exp(−Φ(t)) is universal for all Gaussian baths
with Lorentzian PSD. Zero discriminating content. CONVENTIONAL.

### 7.5 Multi-qubit correlations (n-point)

C2 substrate is Gaussian (linear coupling H_int = g·J·σ_z, Gaussian PSD).
All n-point substrate correlations factorise into products of two-point correlations.
This is Wick's theorem — identical to any Gaussian bath. Zero discriminating content.

### 7.6 Cross-frequency spatial correlations

C2 predicts C_Γ(r, ω) = K₀(r/ξ_c) × Lorentzian(ω) — separable in r and ω.
This separability holds because the substrate is spatially stationary and the
frequency dependence comes only from the temporal autocorrelation.

A conventional two-bath model with frequency-independent spatial kernel would
also give separable C_Γ(r,ω). A model with frequency-dependent kernels (different
spatial correlation at different frequencies) would differ. This is potentially
discriminating.

**Test:** Can C2's predicted separability distinguish it from a two-bath model
where each bath has a different spatial correlation length?

C2: C_Γ(r, ω) = A·K₀(r/ξ_c) / (1 + ω²τ_B²)

Two-bath (M9): C_Γ(r, ω) = A₁·exp(−r/ξ₁)·S₁(ω) + A₂·exp(−r/ξ₂)·S₂(ω)

At fixed ω: M9 gives a two-exponential spatial profile; C2 gives K₀.
At fixed r: M9 gives a sum of two Lorentzians; C2 gives a single Lorentzian.

The single-Lorentzian frequency dependence at each spatial location IS a
distinguishing feature: C2 predicts S_JJ(ω) is a single Lorentzian at every
qubit, while M9 predicts a sum of two Lorentzians.

**Is this a new prediction?** Yes — the single-Lorentzian temporal spectrum at
every qubit is a C2 prediction that M9 two-bath cannot reproduce (M9 has two
temporal scales at each qubit).

**But:** A single-bath OU model (M2) produces the same single-Lorentzian.
M9 is distinguishable from C2 by its temporal structure, but M2 is not.
The single-Lorentzian does NOT discriminate C2 from M2 (single OU bath).

**Conclusion:** The cross-frequency analysis reveals a partial discriminator
between C2 and M9 (two-bath): their temporal spectra differ. But C2 is still
not distinguished from a single OU bath (M2). The adversarial null family includes
both M2 and M9; defeating M9 on temporal structure still leaves M2 as an adequate
conventional explanation.

### 7.7 The mean free path relation — INVARIANT_AUDIT result

The INVARIANT_AUDIT (read directly) establishes:

> ξ_c/τ_B = 2c (or ξ_c·γ = c) is a TAUTOLOGY.
> It is the mean free path relation, present in any kinetic theory.
> It has zero predictive content beyond the definitions of c and γ.

The upper bound c ≤ v_s is the only non-tautological content (derived from C3 + FPUT).

**Conclusion:** The P3 consistency test (ξ_c/τ_B = 2c = const) is a tautology of
kinetic theory, not a C2-specific prediction. It holds for ANY kinetic model with
finite propagation speed and reversal rate. What makes it conditionally distinctive
is only the anomalous value of c — which is not predicted by C2.

### 7.8 Result: No new prediction found

The full-theory search finds no observable beyond what was catalogued in
SURVIVING_THEORY_PREDICTIONS.md. The partial M9-discriminator (single vs double
Lorentzian temporal spectrum) is noteworthy but does not survive the full adversarial
null family (M2 single OU bath remains indistinguishable from C2).

---

## 8. ADVERSARIAL SELF-ATTACK

### 8.1 Attack: "C2 is underdetermined and no existing structure rescues it."

**Strongest form of this argument:**

1. The FPUT chain is a modelling assumption (A-FPUT1), not a derivation.
   Nothing in C2 compels the substrate to be an FPUT chain rather than any
   other lattice model or continuous medium.

2. Even accepting A-FPUT1, the identification [PHON] produces c = v_s, which
   makes C2 physically equivalent to a conventional acoustic phonon bath.
   The adversarial null family already includes phonon-like baths (M7, M9).
   Therefore [PHON] does not rescue the predictive status of C2 — it makes
   C2 a specific conventional model.

3. The ξ_c/τ_B = 2c relation is a kinetic-theory tautology that holds for
   any model with finite propagation speed. It is not C2-specific.

4. The K₀ spatial shape is degenerate with power-law covariance over accessible
   hardware geometries. Even with c = v_s fixed, the shape test fails (ADVERSARIAL_NULL_AUDIT.md).

5. The temporal spectrum is a Lorentzian — identical to any OU bath.

6. The ω_rot² scaling follows from any rotating-frame bath with finite PSD.

**Verdict of attack:** This argument is strong. It establishes that C2, as currently
formulated with A-FPUT1 and the phonon identification, is empirically equivalent to
a conventional acoustic phonon bath model. No existing C2 structure produces a
prediction distinguishable from conventional mechanisms. R3 is defensible.

### 8.2 Counter-attack: "There exists a legitimate derivation that makes C2 predictive."

**Strongest form of this argument:**

1. The combination of FPUT-3 (uniqueness of P1 projection) + C5 (closure)
   forces v = v_s within the P1 model. This is not arbitrary.

2. The P3 consistency relation (c = ξ_c/(2τ_B) = const) would be genuinely
   anomalous if c ≪ v_s — which would happen if the substrate is NOT acoustic
   phonons. This creates a falsification route: measuring c from data tests
   whether the FPUT/phonon identification is correct. If c ≠ v_s, A-FPUT1
   is falsified, which tells us the substrate is NOT the phonon field.

3. C2 makes a structural claim: the noise source producing qubit decoherence
   has a SINGLE underlying propagation speed (same c links spatial and temporal
   correlations). Conventional multi-bath models do not have this structure.
   The P3 test (c = ξ_c/(2τ_B) = const across conditions) would be violated
   by any model where different noise sources dominate at different chip separations.

4. The K₀ shape is distinguishable from power-law at r > 2ξ_c. The hardware
   limitation is a practical obstacle, not a logical one.

**Assessment of counter-attack:**
Points 2 and 3 are valid. C2 does predict that a SINGLE velocity links spatial
and temporal correlations — which conventional multi-source noise models do not
generically produce. But:
- The prediction "c = ξ_c/(2τ_B) = const" is only distinctive if c is anomalous
- If c = v_s (acoustic phonons), a phonon bath model also predicts a single velocity
- Therefore the counter-attack succeeds only if the substrate speed turns out anomalous

### 8.3 Resolution

Both attacks are partially correct. The correct picture:

C2 currently makes predictions that are:
- Equivalent to conventional mechanisms IF c = v_s (phonon speed)
- Anomalous and potentially discriminating IF c ≪ v_s (novel slow substrate)

The theory cannot predict which of these cases obtains. This is the underdetermination.
But the theory is not completely equivalent to conventional mechanisms — it makes a
testable claim that can falsify it (c violates the FPUT constraint c ≤ v_s, or c
varies across conditions).

**The honest classification:** The theory is at the R2/R3 boundary. R2 is correct
because a concrete extension (accepting A-FPUT1 as fundamental and measuring c)
would make the theory predictive — but only in the trivial phonon sense. R2 with
a genuinely discriminating extension requires a different substrate model than FPUT,
which would be a deeper new axiom.

---

## 9. SURVIVING DERIVATIONS

The following results are established within C2 and remain valid:

| Result | Status | Source |
|--------|--------|--------|
| PRW balance equations → telegrapher (1D) | THEOREM | Goldstein-Kac [KR] |
| C_JJ(t) = S₀·exp(−t/τ_B) | THEOREM | PRW OU argument [T] |
| S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²) | THEOREM | Wiener-Khinchin [T] |
| τ_B = 1/(2λ) | DEFINITION | PRW parameter identification |
| ξ_c = v/λ (1D) | DEFINITION | PRW spatial scale |
| K₀ spatial correlator (2D, ω=0) | CONDITIONAL THEOREM | Analytic gap remains [T partial] |
| C5 forces v = v_s within FPUT P1 model | CONDITIONAL DERIVATION | New finding (§3.4) |
| v_s = a√(K/m) from FPUT dispersion | THEOREM | Given FPUT Hamiltonian |
| c ≤ v_s from C3 + FPUT | THEOREM | Inequality, not equality |
| T₂ ≤ 2T₁ | THEOREM | Structural bound |
| Γ_φ = k_rot·ω_rot² | CONDITIONAL THEOREM | ≥10 assumptions required |
| Q diagnostic properties (T Q-1 through Q-5) | THEOREM | Stability analysis |
| CCA internal structure (entropy, causal depth) | THEOREM | Ax1–Ax5 consequences |

---

## 10. FAILED DERIVATIONS

| Claim | Why it fails | Classification |
|-------|-------------|----------------|
| c = v_s from CCA/SCC axioms | CCA/SCC contains no velocity | FAILED |
| c from dimensional analysis alone | No dimensionless group fixes v without material params | FAILED |
| c from entropy extremisation | CCA-C3 unproved and would not fix v anyway | FAILED |
| c from dispersion relation alone | Any v satisfies the telegrapher dispersion | FAILED |
| [PHON] identification distinguishes C2 from phonon bath | Phonon bath is identical to C2 under [PHON] | FAILED |
| Single Lorentzian as discriminator vs M2 | M2 single OU bath is identical | FAILED |
| K₀ shape distinguishable on current hardware | SNR ≈ 2 after shape degeneracy | FAILED |
| c from continuum limit | Continuum limit takes v as input, not output | FAILED |

---

## 11. LABEL MATRIX

| Statement | Correct label |
|-----------|--------------|
| "c = v_s" | CONDITIONAL DERIVATION (given A-FPUT1 + C5) |
| "A-FPUT1 is necessary" | IDENTIFICATION / NEW AXIOM |
| "ξ_c/τ_B = 2c" | TAUTOLOGY (kinetic theory mean free path) |
| "K₀ is the spatial shape" | THEOREM (2D telegrapher Green's function) |
| "K₀ is experimentally distinguishable" | CONJECTURE (hardware-blocked) |
| "c ≤ v_s" | THEOREM (C3 + FPUT, inequality) |
| "CCA-C3 constrains v" | CONJECTURE → INAPPLICABLE |
| "g is determined by C2" | FREE (F10) |
| "Γ_φ = k_rot·ω_rot² is unique to C2" | FALSE (conventional baths reproduce it) |
| "P3 consistency is distinctive" | CONDITIONAL (only if c anomalous) |
| "FPUT substrate is the only physical identification" | ASSUMPTION |

---

## 12. FINAL CLASSIFICATION: R2

**C2 REQUIRES A NEW THEORY EXTENSION.**

**Justification:**

Current C2 (without extension):
- Is internally consistent
- Contains rigorous derivations (telegrapher, C_JJ, K₀, Γ_φ)
- Has one genuinely interesting structural coupling (ξ_c = 2cτ_B)
- Cannot determine c from existing axioms (all 25 routes fail)
- Produces observable predictions indistinguishable from conventional baths

Therefore current C2 is NOT R0 (not predictive) and NOT R1 (no complete
derivation exists that has merely not been carried out).

Required extension for R2 → R1 transition:

The FPUT-based route (§3.4) is the most legitimate available: C5 closure
forces v = v_s given A-FPUT1. But this makes C2 physically equivalent to
an acoustic phonon bath. A genuinely distinctive prediction requires either:

**Extension A (Weak — towards R1):**
Formally adopt A-FPUT1 as a fundamental axiom of C2. Then c = v_s is a
theorem. This makes C2 a theory of acoustic-phonon-mediated decoherence
with K₀ spatial correlations. It is physically motivated and produces
specific numerical predictions. But it is NOT distinguishable from a
conventional acoustic phonon bath model using the existing null family.
The experimental gate remains closed unless M7/M9 are independently excluded.

**Extension B (Strong — towards R0):**
Develop a NEW substrate model where C5 closure holds at v ≪ v_s. This
would require identifying a physical degree of freedom that:
- Propagates much more slowly than acoustic phonons
- Exists in superconducting chip substrates
- Couples to qubit dephasing as J·σ_z

No such degree of freedom is currently known or motivated by C2's existing
structure. This is speculative and constitutes a significant theory extension.

**Extension C (Formal — alternative to B):**
Prove CCA-C3 (causal action extremization). If proved and if v enters
the causal action (which it currently does not), this might constrain v.
Currently: CCA-C3 does not contain v and cannot constrain it even if proved.
A modified CCA-C3 that includes v would require changing the causal action
definition — a new axiom.

R2 is the correct classification because:
1. Existing C2 lacks the structure to determine c
2. A concrete extension (A-FPUT1 as axiom) partially closes the gap
3. That extension alone does not produce discriminating predictions
4. A stronger extension (slow substrate) would produce discriminating
   predictions but requires physics not in current C2
5. The path to R0 is clear in structure if not in physics

---

## 13. CONDITIONS FOR CHANGING THE CLASSIFICATION

### R2 → R1 conditions:

One of the following must be demonstrated with explicit derivation:
1. A new axiom or physical identification that constrains c to a SPECIFIC
   value not achievable by conventional mechanisms (e.g., c ~ 50 m/s with
   a physical model for why this slow substrate exists)
2. Proof that existing C2 structure (CCA/SCC) implies a constraint on v
   not found in the 25 routes already tested
3. A new observable derived from C2 that passes all four criteria of
   SURVIVING_THEORY_PREDICTIONS.md without requiring c to be measured first

### R1 → R0 conditions:

The derivation found under R1→R1 conditions must additionally:
4. Produce a prediction that survives the adversarial null family
   (including M7 power-law and M9 two-bath)
5. Be confirmed at NMP ≥ 0.1 on appropriate hardware

### R2 → R3 conditions:

If one can prove that NO possible extension of C2 (without contradicting
its existing structure) can produce a prediction distinguishable from
conventional mechanisms, R3 would be established. This is NOT yet proved —
only 25 specific routes have been tested, and Route 5 (C5 closure) contains
non-trivial structure that partially survives.

---

## 14. STATEMENT ON FURTHER EMPIRICAL WORK

**Is further empirical work justified?**

**No, under current C2 — without theory extension.**
The existing theory cannot produce a parameter-free prediction. Measuring
on hardware before the theory specifies what to measure would be a parameter
fit, not a theory test. No IBM QPU job is authorised.

**Yes, conditionally — after one specific theoretical step:**
If Extension A (A-FPUT1 as fundamental axiom) is formally adopted with a
clear statement that c = v_s = 6000 m/s for Si, and if independent τ_B
measurement from Ramsey shape on Eagle-class hardware gives τ_B ~ 1.2 µs
(NOT chosen to match the prediction), then the K₀ spatial test at d ~ ξ_c
becomes a legitimate experiment. Its discriminating power is limited (M7/M9
still present), but it would test whether:
- The phonon bath model produces K₀ or exponential spatial decay
- The correlation length matches the c = v_s prediction

This would be an informative experiment — but it tests conventional phonon
bath physics, not uniquely SXC-IGC.

For SXC-IGC to be tested as a DISTINCT theory (not merely as a formulation
of phonon-bath decoherence), Extension B is required: a physical argument
for why c ≪ v_s in the actual chip substrate. Until that argument exists,
hardware investment in the spatial correlation test is premature.

---

## 15. MACHINE-READABLE VERDICT

```
THEORY_STATUS: T2_STRUCTURALLY_UNDERDETERMINED
EMPIRICAL_STATUS: PAUSED — no hardware authorized
GAP7_STATUS: FUNDAMENTAL — all 25 routes fail; C5 gives conditional derivation under A-FPUT1
PREDICTIVE_STATUS: ZERO_UNCONDITIONAL — one conditional (P3) requiring anomalous c
REQUIRED_NEXT_STEP: THEORY_EXTENSION — either (A) adopt A-FPUT1 explicitly + test whether c=v_s on Eagle-scale hardware produces anomalous P3, or (B) identify a physical mechanism for c << v_s
HARDWARE_AUTHORIZED: NO
```

---

*Audit completed: 2026-08-22*
*Classification: R2 — C2 REQUIRES A NEW THEORY EXTENSION*
*This document supersedes all prior partial audit conclusions on the predictivity question.*
*Not revisable without a new derivation or physical identification satisfying §13.*
