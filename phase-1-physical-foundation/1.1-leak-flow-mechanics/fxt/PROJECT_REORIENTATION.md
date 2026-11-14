# PROJECT REORIENTATION — SXC-IGC

**Date:** 2026-08-22
**Basis:** FINAL_RESCUE_OR_KILL_AUDIT.md (C), EXTENDED_THEORY_VIABILITY_AUDIT.md (B),
SUBSTRATE_CLOSURE_AUDIT.md (B), 30_OBSERVABLE_DISCRIMINATION_AUDIT.md (C/OU failure)
**Purpose:** Establish hard project boundaries, exact surviving predictions,
experimental specification, null models, kill criterion. No redesign.

---

## 1. FROZEN BOUNDARIES (HARD STOP)

The following are permanently frozen. No further work in these directions without
explicit acknowledgment that new physics is being introduced:

```
FROZEN:
  C± = αE as a law derived from the original C2 ontology
  Any derivation of η whose primary purpose is rescuing C±
  Any bath or coupling selected because it reproduces αE
  The claim that SXC-IGC is a closed, unified theory
  Any experimental proposal whose discriminating power depends on C±
```

These are not provisionally frozen pending new ideas. They are structurally
blocked by five independent proved no-go theorems (FINAL_RESCUE_OR_KILL_AUDIT §12).

```
ACTIVE:
  PRW substrate transport dynamics
  Substrate-mediated qubit decoherence: Γ_φ = k_rot · ω_rot²
  Spatial decoherence correlator: C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)
  Experimental discrimination of the decoherence prediction from null models
```

---

## 2. WHAT THE THEORY ACTUALLY PREDICTS

### 2A. Primary Observable

**What is measured:** Ramsey coherence decay of a rotating qubit.

```
W(t) = ρ_{01}(t) / ρ_{01}(0)    [coherence visibility]
```

Under the substrate decoherence model (pure dephasing, Markovian, Born):

```
W(t) = exp(−Γ_φ · t)
```

where Γ_φ is the pure dephasing rate (not T₁; the model predicts T₁ = ∞).

**Exact formula (from decoherence_chain_summary.md, all steps labelled):**

```
Γ_φ = k_rot · ω_rot²

k_rot = 8g²s₀²r_q²τ / (3ℏ²)    [compound parameter — not independently predicted]
```

### 2B. Control Variable and Regime

The control variable is ω_rot [rad/s] — the rotation frequency of the qubit
reference frame (equivalently, the qubit angular velocity in a rotating setup,
or an applied transverse drive frequency that sets the effective rotation rate).

**Validity regime (from derivation assumptions):**

| Assumption | Condition | Source |
|------------|-----------|--------|
| Diffusive (drop s_tt) | ω_rot ≪ 2λ = 1/τ | A-diffusive |
| Born (weak coupling) | g² ≪ ℏ²/τ² | A-BORN |
| Markov | τ ≪ Γ_φ⁻¹ | A-MARKOV (self-consistent: τ·Γ_φ ≈ 0.25 from data) |
| Secular | ω_q ≫ Γ_φ | A-SEC (Ramsey condition) |
| ω_max cutoff | Γ_φ ∝ ω² only for ω ≪ ω_max ≈ 10⁶ rad/s | from COMPLETE_MASTER_EQUATION |

**The ω² scaling is not universal — it holds only within the regime
ω ≪ 1/τ ~ 10⁶ rad/s (for τ ~ 10⁻⁶ s).**

The theory does NOT predict Γ_φ ∝ ω² at all frequencies. High-frequency
rolloff is expected. Claims of ω² scaling outside this regime are not supported.

### 2C. Spatial Prediction

**Observable:** Joint decoherence rate correlation between two qubits i,j
at spatial separation r_ij.

**Derived observable (from 02_2D_CORRELATION_DERIVATION.md, D NEW):**

```
C_Γ(r) = [Γ_φ(r=0) − Γ_φ(r)] / Γ_φ(r=0)    [normalized correlation]

       = K₀(r/ξ_c) / K₀(a/ξ_c)               [substrate prediction]

where:
  ξ_c = 2c·τ_B = 2·v_sub·τ    [substrate coherence length]
  a   = UV cutoff (lattice spacing, ~ qubit size)
  K₀  = modified Bessel function of second kind, order 0
```

**Asymptotics:**
- Short range r ≪ ξ_c: C_Γ(r) ~ const − const·ln(r)   [logarithmic decay]
- Long range r ≫ ξ_c: C_Γ(r) ~ (ξ_c/r)^{1/2} · exp(−r/ξ_c)  [exponential with prefactor]

**The claim is K₀ not exponential. These are distinguishable at intermediate
separations r ~ ξ_c where K₀ and pure exp diverge.**

### 2D. Null Models

The theory must be compared against:

```
H₀ (Markovian/white): Γ_φ(ω) = Γ₀  [constant, no ω dependence]

H₁ (Substrate / OU):  Γ_φ(ω) = Γ₀ + k_rot · ω²  [ω² scaling]

H₂ (1/f noise):       Γ_φ(ω) ~ ω⁻¹  [1/f decoherence, common in SC qubits]

H₃ (Ohmic bath):      Γ_φ(ω) = A·ω  [Ohmic, linear in ω]

H₄ (generic OU bath): Γ_φ = 2σ²τ_c / (1 + (ωτ_c)²)  [Lorentzian rolloff]
```

**CRITICAL FINDING from 30_OBSERVABLE_DISCRIMINATION_AUDIT.md:**

The substrate model (H₁) is mathematically identical to an Ornstein-Uhlenbeck
(OU) colored-noise bath in all Ramsey/CPMG/Ramsey-variant observables. The
two models produce exactly the same Φ(t), the same PSD shape (Lorentzian),
and the same decay envelope. They cannot be discriminated by Ramsey measurements
alone, regardless of hardware quality.

This means:

> **The Ramsey/temporal prediction Γ_φ ∝ ω² is currently NON-FALSIFIABLE as a
> test of the substrate model specifically.** It tests the OU class as a whole,
> not C2.

The spatial K₀ vs exp prediction IS potentially discriminating:
- K₀ ≠ exponential at intermediate r
- OU bath correlation function need not follow K₀ (depends on bath geometry)
- This is the only currently identified discriminator

---

## 3. DISCRIMINABILITY ASSESSMENT

**Temporal channel (Ramsey dephasing):**

| Observable | C2/substrate prediction | OU bath prediction | Discriminating? |
|-----------|------------------------|-------------------|-----------------|
| Γ_φ(ω) | Γ₀ + k_rot·ω² | Γ₀ + A·ω² | NO (same functional form) |
| Ramsey decay shape | exp(−Γ_φ t) | exp(−Γ_φ t) | NO |
| Non-Markovian ratio | ~1 (near-Markovian) | ~1 | NO |
| CPMG filter | Lorentzian PSD | Lorentzian PSD | NO |
| T₁ prediction | T₁ = ∞ (pure dephasing) | T₁ = ∞ (for σ_z bath) | NO |

Conclusion: **Temporal channel alone cannot distinguish C2 from OU.**

**Spatial channel (multi-qubit correlations):**

| Observable | C2 prediction | Exp null model | Discriminating? |
|-----------|--------------|----------------|-----------------|
| C_Γ(r), short range | logarithmic −ln(r) | ~exp(−r/ξ) | YES (at r ≪ ξ_c) |
| C_Γ(r), intermediate | K₀(r/ξ_c) shape | exp(−r/ξ) | YES (shape differs) |
| C_Γ(r), long range | exp(−r/ξ_c)/√r | exp(−r/ξ) | MARGINAL (extra √r) |
| ξ_c = 2cτ joint prediction | one parameter ξ_c | two parameters | STRONGER (parameter reduction) |

**The spatial channel provides the ONLY currently identified discriminator.**
The experiment must be multi-qubit with varied separations, not single-qubit Ramsey.

---

## 4. COMPUTATIONAL REPLICATION FIRST

Before any hardware access, the following must be built and run.

**Step 4.1 — Synthetic data generator**

Generate Γ_φ(ω) and C_Γ(r) from the exact C2 parameters under all models:

```python
# Required outputs for each model:
# Model 0: Markovian    → Γ_φ = Γ₀ (constant), C_Γ = 0
# Model 1: C2/substrate → Γ_φ = Γ₀ + k_rot·ω², C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c)
# Model 2: 1/f noise    → Γ_φ ~ A·ω^{-1} (frequency-inverted)
# Model 3: OU bath      → Γ_φ = 2σ²τ_c / (1+(ωτ_c)²), C_Γ = exp(−r/ℓ)
# Model 4: Ohmic bath   → Γ_φ = π·J(ω)·|filter|²

# Parameters to scan:
# ω_rot: [10², 10³, 10⁴, 10⁵, 10⁶] rad/s
# r: [0, 1, 2, 5, 10, 20, 50] × ξ_c
# T2*: 1/Γ_φ for realistic qubit noise floors
```

**Step 4.2 — Distinguishability test (already exists: p25_discrimination_test.py)**

The existing script 09_spatiotemporal_c2_test/scripts/p25_discrimination_test.py
already performs this test. Its verdict (30_OBSERVABLE_DISCRIMINATION_AUDIT.md §17):

> "C2/OU identifiability failure in temporal channel. Spatial K₀ remains
> conditional discriminator."

This test MUST be re-run with the exact qubit chip geometry (IBM Brisbane/Kyoto
topology from 06_datasets/) to verify whether ξ_c ~ chip size produces
a measurable K₀ vs exp difference given realistic noise floors.

**Step 4.3 — Required input before hardware**

The 30_OBSERVABLE_DISCRIMINATION_AUDIT identified:

> Priority 1: Derive c from C2 first principles (independent of ξ_c measurement).

Until c is independently predicted:
- ξ_c = 2cτ_B has two free parameters (c, τ_B)
- The K₀ fit has one free parameter (ξ_c)
- The exp fit also has one free parameter (ξ)
- A fit of K₀ vs exp with the same number of parameters is a SHAPE test only

The shape test is still scientifically valid — K₀ and exp have different shapes.
But an independent prediction of ξ_c would convert the shape test into a parameter-free test.

**Decision gate:** Run p25_discrimination_test.py with IBM chip geometry. If the
shape difference between K₀ and exp is detectable above measurement noise at
realistic separation scales, proceed to hardware. If not, the experiment is
premature regardless of theory correctness.

---

## 5. EXPERIMENT SPECIFICATION

**Architecture:** N qubits on a 2D processor chip, varied spatial separations.

### 5A. Temporal measurement (per qubit)

Protocol:
1. Prepare qubit i in |+⟩ = (|0⟩+|1⟩)/√2
2. Apply no gate — free evolution for time t
3. Apply π/2 pulse and measure ⟨σ_x⟩
4. Repeat for t = 0, dt, 2dt, ... up to ~ 5·T₂*
5. Fit to W_i(t) = exp(−Γ_φ,i · t)

Vary ω_rot by applying a small, known, controlled transverse drive at frequency
ω_rot. The substrate prediction is:

```
Γ_φ,i(ω_rot) = Γ₀,i + k_rot · ω_rot²
```

Scan ω_rot over [10³, 10⁶] rad/s. Fit k_rot. This tests the functional form only.

### 5B. Spatial measurement (cross-qubit correlation)

Protocol:
1. Simultaneously prepare all qubits in |+⟩
2. Allow joint free evolution for time t
3. Measure ⟨σ_x,i⟩ and ⟨σ_x,j⟩ for all pairs (i,j)
4. Compute normalized correlation:
   ```
   C_ij(t) = ⟨σ_x,i(t)·σ_x,j(t)⟩ / (⟨σ_x,i(t)⟩·⟨σ_x,j(t)⟩)
   ```
5. Average over multiple t values (or fit the t-dependence of correlation)
6. Plot C_ij vs r_ij

**Substrate prediction:**
```
C_ij = K₀(r_ij / ξ_c) / K₀(a / ξ_c)
```

**Null model 1 (independent decoherence):** C_ij = 0 for all r_ij > 0
**Null model 2 (exponential bath):** C_ij = exp(−r_ij / ξ_exp)
**Null model 3 (EM crosstalk):** C_ij = A · exp(−r_ij / ξ_EM) with ξ_EM ~ coupling length

### 5C. Controls required

| Control | Purpose |
|---------|---------|
| Vary qubit-qubit distance geometrically (use chip topology) | Isolate spatial dependence |
| Measure T₁ independently | Confirm pure dephasing (T₁ >> T₂) |
| Repeat without rotation drive (ω_rot = 0) | Measure Γ₀,i baseline |
| Characterize EM coupling independently | Separate circuit crosstalk from substrate signal |
| Vary temperature | Expected: Γ_φ(T) changes but K₀ shape should not if signal is substrate-mediated |
| Compare on-chip qubits at same distance, different orientation | Test for chip-layout artifacts |

### 5D. Parameter independence requirement

The test of functional FORM (ω² scaling, K₀ shape) tests one aspect of the theory.
The test of the COEFFICIENT k_rot tests a stronger aspect — but k_rot = 8g²s₀²r_q²τ/3ℏ²
contains the undetermined g. Therefore:

**Weak test (currently feasible):** Confirm ω² functional form AND K₀ spatial shape.
This is a test of the model *class* (OU + substrate-correlated bath).

**Strong test (requires g to be independently determined):** Predict k_rot without
fitting. Currently blocked. Would require deriving g, which FINAL_RESCUE_OR_KILL_AUDIT
classified as requiring new physics (addition of η).

The experiment should explicitly label which test is being conducted.

---

## 6. PRE-EXPERIMENT KILL CRITERION

**This criterion is written before any data is collected.**

The substrate hypothesis is considered **unsupported** if ANY of the following:

1. After subtraction of independently characterized conventional noise (EM crosstalk,
   1/f, thermal), the residual Γ_φ(ω) is statistically inconsistent with ω² scaling
   over the range ω ∈ [10³, 10⁶] rad/s.

2. The measured spatial correlation C_ij(r) is statistically inconsistent with the
   K₀(r/ξ_c) functional form — i.e., a pure exponential provides a statistically
   superior fit with the same number of free parameters (ξ_c = ξ, same DoF).

3. The ξ_c fitted from temporal data (via τ_B and c separately) and the ξ_c
   fitted from spatial data disagree by more than a factor of 3.

4. The T₁/T₂ ratio is < 10 for the qubits used, indicating substantial transverse
   relaxation that violates the pure-dephasing assumption of the model.

**The substrate hypothesis becomes interesting only if ALL of the following:**

1. Γ_φ ∝ ω² is confirmed over at least a decade in ω.
2. The spatial K₀ shape provides a statistically better fit than exp(−r/ξ) over
   a range of separations spanning at least 0.2 ξ_c to 5 ξ_c.
3. The above results survive at least one independent control variation
   (e.g., same result on two different chip geometries, or same result at two temperatures).
4. A conventional OU bath model with the same number of parameters cannot fit both
   the temporal and spatial data simultaneously with the same ξ_c.

**These criteria are not to be revised after data collection.**

---

## 7. WORKFLOW

```
ORIGINAL SXC-IGC
       |
  C2 closure → FAILED / FROZEN (FINAL_RESCUE_OR_KILL_AUDIT: C)
       |
       v
SURVIVING LAYER A
  PRW dynamics + decoherence prediction
       |
       v
STEP 1 — EXACT PREDICTION AUDIT (this document §2)
  Define observables, regimes, null models precisely
       |
       v
STEP 2 — RUN p25_discrimination_test.py WITH IBM CHIP GEOMETRY
  Question: Is K₀ vs exp shape distinguishable above noise floor?
       |
   +---+---+
   |       |
  NO      YES
   |       |
  STOP  STEP 3 — DESIGN REAL EXPERIMENT (§5)
           |
           v
       Run experiment with pre-registered kill criterion (§6)
           |
       +---+---+
       |       |
    FAILED   PASSES
       |       |
      STOP   INDEPENDENT REPLICATION (different chip, different lab)
               |
               v
           If replicated: PUBLISH and reconsider deeper theory (η question)
           If not replicated: STOP
```

**Current position in the workflow: Between Step 1 and Step 2.**

Step 1 is complete (this document). Step 2 requires running p25_discrimination_test.py
with the actual IBM chip topology from 06_datasets/conf_brisbane.json and
conf_kyoto.json and realistic noise parameters from props_*.json.

---

*End of PROJECT_REORIENTATION.md*
*Date: 2026-08-22*
*All experimental specifications derived from the project's own equations.*
*No new theory introduced. No goalposts moved.*
