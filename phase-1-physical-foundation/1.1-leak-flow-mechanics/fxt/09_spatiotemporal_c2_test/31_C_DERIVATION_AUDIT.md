# Document 31 — c Derivation Audit
## Phase 9: Does C2 Independently Predict the Propagation Speed c?

**Date:** 2026-08-21  
**Script:** `scripts/p26_c_derivation_audit.py`  
**Data:** `outputs/data/c_derivation_audit.json`  
**Classification:** **C_PARAMETER_DEPENDENT**

---

## 1. Executive Verdict

The C2/PRW/FPUT theory does **not** derive a unique value of c from first principles.

The theory establishes:

- **(A)** `c = v` (PRW particle speed) — **ASSUMED** in [A-PRW1], not derived
- **(B)** `c ≤ v_s = a√(K/m)` — **DERIVED** from FPUT + admissibility constraint C3 (upper bound only)
- **(C)** `c = v_s` under a saturation postulate — **NOT in current C2 theory files**

The previously assumed value `c = 10⁴ m/s` has no derivation in the theory and **violates C3** (`v_s(Si) = 6000 m/s < 10⁴ m/s`). It was chosen for experimental convenience.

Even under the most natural candidate (`c = v_s ≈ 6000 m/s`), the predicted coherence length `ξ_c = 2cτ_B ≈ 6 cm` vastly exceeds any available chip geometry. The spatial discrimination test remains inaccessible regardless of which physically reasonable c is used.

**Classification: C_PARAMETER_DEPENDENT**

---

## 2. Equations Inspected

Sources read for this audit:

- `00_THEORY_AUDIT.md` — parameter status table, GAP-7
- `01_PREDICTION_DERIVATION.md` — PRW → telegrapher → coherence
- `02_2D_CORRELATION_DERIVATION.md` — 2D K₀ result, ξ_c definition
- `02_derivations/microscopic_derivation.md` — PRW balance equations, FPUT candidates
- `02_derivations/transport_summary.md` — full dependency graph, LAYER 0–5
- `02_derivations/substrate_transport_derivation.md` — variance derivation [ESTABLISHED-VAR]
- `01_foundations/C2_FOUNDATIONS.md` — FPUT Subsystem 2, constraints C1–C6, Theorem FPUT-3

---

## 3. Microscopic PRW/FPUT Definitions

### 3.1 FPUT chain (source: C2_FOUNDATIONS.md SUBSYSTEM 2)

```
H = Σᵢ [ pᵢ²/(2m) + K(qᵢ₊₁−qᵢ)²/2 ]   (harmonic limit β→0)

Normal modes: ωₖ = 2√(K/m) |sin(πk/N)|   [KNOWN RESULT — Goldstein-Kac]

Long-wavelength (k→0): ωₖ ≈ (2πa/N)√(K/m) · k  →  ω = v_s · k

Acoustic speed: v_s = a √(K/m)   [DERIVED from FPUT]
```

For silicon substrate: `m = 4.665×10⁻²⁶ kg`, `a = 5.43×10⁻¹⁰ m`, giving `v_s ≈ 6000 m/s`.

Admissibility constraints for the FPUT → PRW projection (C2_FOUNDATIONS.md):

- **C1 (Locality):** projection depends only on bounded neighborhood
- **C2 (Conservation):** total projected density = total microscopic action
- **C3 (Finite speed):** signal speed ≤ acoustic sound speed v_s  ← KEY CONSTRAINT
- **C4 (Positivity):** projected densities ≥ 0
- **C5 (Closure):** evolution expressible as function of projected state
- **C6 (Thermodynamic consistency):** entropy non-decreasing

**Theorem FPUT-3 (C2_FOUNDATIONS.md, proven):** The unique admissible projection satisfying C1–C6 is the PRW, with coarse-grained density `s(x,t)` whose evolution is the telegrapher equation.

### 3.2 PRW microscopic rules

```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻   [exact]
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻   [exact]
```

Parameters:
- `v` = particle speed [m/s] — **ASSUMED** [A-PRW1]
- `λ` = reversal rate [s⁻¹] — **ASSUMED** [A-PRW1]

**These are inputs to the model, not derived from the FPUT chain.**

Theorem FPUT-3 proves that the projection is of the PRW type, but does not derive the numerical values of v and λ from (m, K, a).

---

## 4. Continuum / Transport Equation

From the PRW balance equations (exact, no approximation):

```
∂s/∂t = −∂J/∂x                          [C-s]   DERIVED
∂J/∂t = −c²∂s/∂x − (1/τ)J              [C-J]   DERIVED

Eliminating J:
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s            [TEL]   DERIVED

Parameter identification:
  τ = 1/(2λ)                             DERIVED from λ
  c = v                                  DERIVED (c equals microscopic speed v)
  D = c²τ = v²/(2λ)                      DERIVED
```

The transport equation has the structure of the telegrapher equation. Its two free inputs are `v` (speed) and `λ` (reversal rate). Both are assumed at the microscopic level.

---

## 5. Linearization

The telegrapher equation is already linear. Plane-wave perturbation `s ~ exp(ikx − iωt)`:

```
−τω² − iω + c²τk² = 0

Dispersion relation [DISP-EQ]:
ω² + (i/τ)ω − c²k² = 0                  DERIVED
```

---

## 6. Dispersion Relation and All Candidate Velocities

Solutions to [DISP-EQ]:

```
ω = −i/(2τ) ± √(c²k² − 1/(4τ²))         DERIVED
```

**Critical wavenumber:** `k_c = 1/(2cτ) = λ/v`

| Velocity | Formula | k-dependence | Uniquely specifies c? |
|----------|---------|-------------|----------------------|
| Phase velocity | `v_p = Re(ω)/k = √(c²−1/(4τ²k²))` | Yes | No |
| Group velocity | `v_g = dRe(ω)/dk = c²k/Re(ω)` | Yes | No |
| Signal/front velocity | `c` (characteristic of PDE) | **No** | **Yes** |
| Correlation spreading | `c` (wavefront of Green's function) | **No** | **Yes** |

The **only** velocity that uniquely and k-independently characterizes the telegrapher equation is the **front/characteristic velocity `c`**, which equals the PRW particle speed `v` by construction.

`v_p → c` and `v_g → c` as `k → ∞`, confirming that `c` is the high-frequency (ballistic) limit.

The correlation length `ξ_c = v/λ = 2cτ_B` uses this front velocity `c`. This is physically correct: the Green's function of the telegrapher equation has a wavefront that propagates at exactly `±c`.

---

## 7. Dimensional Analysis — All [m/s] Combinations

| Parameter combination | Dimensions | Status | Notes |
|----------------------|-----------|--------|-------|
| `v` | [m/s] | ASSUMED [A-PRW1] | The only input velocity |
| `a√(K/m)` = v_s | [m/s] | DERIVED (FPUT) | Upper bound for c via C3 |
| `√(D/τ)` = `√(c²τ/τ)` = c | [m/s] | TRIVIAL | Reduces to c |
| `λ·ξ_c` = `λ·(v/λ)` = v | [m/s] | TRIVIAL | Reduces to v |
| `√(<J²>)/s₀` = `v/√2` | [m/s] | TRIVIAL | Proportional to v |
| `ξ_c/τ_B` = `2v` | [m/s] | TRIVIAL | Names 2c |
| `ω_q·r_q` | [m/s] | NOT DERIVED | ω_q empirical; r_q FREE |
| `√(Γ_M·r_q²/τ_B)` | [m/s] | CIRCULAR | Requires CA-3 |

**Finding:** Every [m/s] combination either reduces to `v` (trivially), equals `v_s` (FPUT bound), or requires free parameters not derived within the theory. No independent velocity scale exists.

---

## 8. Complete Parameter Dependency Graph for c

```
FPUT inputs (m, K, a)
       │
       │  DERIVED via ωₖ = 2√(K/m)|sin(πk/N)|
       ▼
  v_s = a√(K/m)          [DERIVED — acoustic speed]
       │
       │  C3: signal speed ≤ v_s  [ADMISSIBILITY CONSTRAINT]
       ▼
  c ≤ v_s                [DERIVED — upper bound only]

  PRW inputs (v, λ)      [ASSUMED — A-PRW1]
       │
       ▼
  c = v                  [ASSUMED — c equals PRW input v]
       │
  ┌────┴────┐
  │         │
  τ_B=1/(2λ)  ξ_c = v/λ = 2cτ_B
  [DERIVED]   [DERIVED, given c and τ_B]

  Bridge: c ≤ v_s  (from C3 applied to PRW)
  But: c = v_s requires the saturation postulate:
     "PRW saturates C3" — NOT in current theory
```

**To close the chain and derive c uniquely:**

The missing link is: **Theorem FPUT-3 proves the projection is a PRW; it does not fix v.**

A complete derivation would require: "The PRW speed v equals the FPUT acoustic speed v_s." This is the saturation postulate. It is physically natural (phonons in the acoustic branch travel at v_s) but is currently an assumption, not a theorem in the project files.

---

## 9. CA-3 Dependency Analysis

```
CA-3: Γφ ∝ <(δJ)²>   [ASSUMED — constitutive postulate]
```

| Quantity | Requires CA-3? |
|----------|---------------|
| c = v (PRW speed) | **NO** — defined at microscopic level |
| v_s = a√(K/m) (FPUT speed) | **NO** — classical mechanics only |
| c ≤ v_s (C3 bound) | **NO** — admissibility constraint |
| c = v_s (saturation) | **NO** — postulate at PRW level |
| ξ_c = 2cτ_B | **NO** — purely from PRW dynamics |
| Inferring c from Ramsey data | **YES** — requires CA-3 to connect c to Γφ |
| τ_B from Ramsey trace | **YES** — requires CA-3 for Γφ → τ_B identification |
| c = ξ_c/(2τ_B) from experiment | **YES** — requires both CA-3 and spatial data |

**Critical finding:** c can in principle be derived (or bounded) without CA-3. However, c cannot be *measured* from any quantum decoherence observable without CA-3. CA-3 is the bridge between the classical substrate and the qubit, and without it c is empirically inaccessible even if theoretically bounded.

---

## 10. Variance Analysis

### The formula [ESTABLISHED-VAR]:

```
<|δJ|²> = (2/3)s₀²ω_rot²r²
```

Derivation status: **DERIVED** (kinematic frame transform + angular average)  
Source: substrate_transport_derivation.md, LAYER 4

**Does the variance predict a velocity?**

The variance contains the tangential speed `ω_rot × r`, which is the speed of substrate flow in the rotating frame. This is a velocity:

```
v_tangential = ω_rot × r   [m/s]   OBSERVABLE (given ω_rot, r)
```

But `v_tangential` is NOT the PRW propagation speed c. It is the flow speed of the substrate in a rotating frame, set externally by `ω_rot`.

The PRW equipartition formula gives:

```
<J²> = s₀v²/2   →   v = √(2<J²>/s₀)
```

But this requires `s₀` (a free parameter) to extract `v`. If `s₀` is unknown, v cannot be extracted from `<J²>` measurements alone.

**What the variance CAN be tested for, independently of CA-3:**

- The kinematic identity `δJ = s₀(ω_rot × r)` predicts that the current perturbation scales as `ω_rot × r`. This is a classical mechanics prediction testable by measuring substrate flow patterns.
- The `(2/3)` factor (isotropic average) is testable by measuring current correlations in different directions.

**What requires CA-3:**

- Connecting `<|δJ|²>` to the measured dephasing rate Γφ.
- Inferring s₀ or v from decoherence measurements.

---

## 11. ξ_c Predictions for All Justified c Values

Using τ_B = 5 µs (representative from Ramsey fits), chip max = 632 µm:

| c value | Basis | ξ_c = 2cτ_B | d/ξ_c | Resolvable? |
|---------|-------|------------|-------|------------|
| 6000 m/s = v_s(Si) | FPUT C3 saturation (requires postulate) | 6.0 cm | 0.0105 | NO |
| 10⁴ m/s | Previously assumed | 10.0 cm | 0.0063 | NO — also violates C3 |
| 10³ m/s | Arbitrary | 1.0 cm | 0.063 | NO |
| **100 m/s** | **Required for ξ_c ~ 1 mm** | **1.0 mm** | **0.63** | **Marginal** |
| 10 m/s | Implausibly slow | 0.1 mm | 6.3 | YES |

**Critical result:** For ANY physically reasonable c (> 100 m/s), ξ_c >> chip. The spatial test requires c < 50 m/s. No mechanism in C2 predicts c this small. The test is inaccessible regardless of QPU availability.

---

## 12. The Previously Assumed c = 10⁴ m/s: Internal Inconsistency

The value c = 10⁴ m/s was used in previous simulations. This audits its status:

- **Derivation:** None. Chosen for experimental convenience.
- **C3 consistency:** `10⁴ m/s > v_s(Si) = 6000 m/s`. **VIOLATES C3.**
- **Physical meaning:** No FPUT parameter set gives v_s = 10⁴ m/s for silicon.
- **Status:** EMPIRICAL FIT PARAMETER chosen to make ξ_c ~ cm scale.

This value should not appear in future analyses as a C2 prediction. It is an imposed experimental target, not a theoretical result.

---

## 13. Whether c is Genuinely Predicted

**Answer: No.** The current C2 theory does not predict c.

The theory provides:
- An upper bound: c ≤ v_s (DERIVED, not free)
- A natural candidate: c = v_s (requires saturation postulate, not currently in the theory)
- The PRW definition: c = v (ASSUMED, a free microscopic parameter)

**What would constitute a genuine prediction:**

Adding the postulate "c = v_s" explicitly and justifying it — e.g., by deriving that the PRW particle speed must equal the acoustic speed of the substrate material. This is physically reasonable (the information carriers ride the acoustic phonons) but has not been proved from the C2 axioms.

If this postulate were added:

```
c = v_s = a√(K/m)   [would become DERIVED given the saturation postulate]
```

For Si: c = 6000 m/s, giving ξ_c = 6 cm. Still inaccessible on current chips.

---

## 14. Whether the Spatial C2 Prediction is Genuinely Falsifiable

Under any c > 100 m/s: **No** — ξ_c >> chip for all current QPUs.

Under c = v_s ≈ 6000 m/s (best natural candidate): ξ_c ~ 6 cm. Accessible only on a platform with qubit separations of order centimeters. No such platform currently exists for superconducting qubits.

The K₀ vs. exponential shape discrimination (the only way to distinguish C2 2D from generic OU) requires d/ξ_c ~ 0.1–10, i.e., qubit separations ~ 0.6–60 mm. This is at least 3–100× the maximum available chip dimension.

**The C2 spatial prediction is not falsifiable with current hardware, even with the natural saturation candidate c = v_s.**

---

## 15. Whether QPU Experimentation is Currently Justified

**No.** The chain of reasoning is:

1. c is not independently predicted (C_PARAMETER_DEPENDENT) ✗
2. Therefore ξ_c is not independently predicted ✗
3. Even under the best natural c (= v_s), ξ_c >> chip ✗
4. No QPU on any platform has qubit separations ~ ξ_c ✗
5. All temporal/spectral observables are C2/OU-degenerate (from Doc 30) ✗

A QPU experiment currently adds no information toward discriminating C2 from OU.

---

## 16. What Theoretical Result Would Reopen the Experimental Branch

**Required (in order of priority):**

### Step 1 (essential): Add the saturation postulate explicitly
State as a postulate: "The PRW speed v equals the FPUT acoustic speed v_s = a√(K/m) of the substrate material." This gives c = v_s.

Even this does not immediately reopen experiments (ξ_c ~ 6 cm), but it removes the free-parameter status of c.

### Step 2 (required for experiment): Find a regime where ξ_c ~ chip
Either:
- (a) Identify a substrate material with much lower acoustic speed (v_s << 1000 m/s) and longer τ_B, giving ξ_c < mm. No such material is in the C2 theory.
- (b) Access a platform with cm-scale qubit separations (NV centers, trapped ions with adjustable spacing, or a purpose-built test chip).

### Step 3 (required for discrimination): Derive c from first principles
Beyond the saturation postulate, a full derivation would require:
- Proving from FPUT-3 that the projected PRW speed must be v_s (not just ≤ v_s)
- This is currently an open problem (Theorem FPUT-3 proves projection type, not speed value)

---

## 17. Summary of Derivation Chain (Step-by-Step Labels)

| Step | Statement | Label |
|------|-----------|-------|
| FPUT Hamiltonian | H = Σ[p²/2m + K(Δq)²/2] | ASSUMED (FPUT inputs) |
| FPUT dispersion | ωₖ = 2√(K/m)\|sin(πk/N)\| | DERIVED (classical mechanics) |
| Acoustic speed | v_s = a√(K/m) | DERIVED |
| C3 constraint | c ≤ v_s | DERIVED (C3 + FPUT) |
| PRW speed | c = v | ASSUMED [A-PRW1] |
| PRW → telegrapher | τ∂²s/∂t² + ∂s/∂t = c²τ∇²s | DERIVED (Goldstein-Kac) |
| τ_B = 1/(2λ) | Bath correlation time | DERIVED |
| ξ_c = v/λ = 2cτ_B | Coherence length | DERIVED |
| Dispersion [DISP-EQ] | ω²+(i/τ)ω−c²k²=0 | DERIVED |
| Front velocity = c | Characteristic of telegrapher | DERIVED (trivially = v) |
| Saturation c = v_s | c equals FPUT acoustic speed | NOT IN CURRENT THEORY |
| ξ_c = 2v_s·τ_B | Numerical prediction | UNDERDETERMINED (requires saturation) |
| Spatial test | K₀ vs exp at d/ξ_c ~ 1 | NOT ACCESSIBLE (ξ_c >> chip) |

---

## Final Classification

```
C_PARAMETER_DEPENDENT

c is bounded above: c ≤ v_s = a√(K/m)  [DERIVED from FPUT + C3]
c has a natural candidate: c = v_s       [requires saturation postulate]
c has no unique derivation:              [FPUT-3 proves projection type, not speed]

Under the natural candidate c = v_s ≈ 6000 m/s:
  ξ_c = 6 cm  >>  chip (632 µm)
  Spatial test: NOT ACCESSIBLE on any current QPU platform

Previously assumed c = 10⁴ m/s:
  No derivation; violates C3 (> v_s Si)
  STATUS: EMPIRICAL FIT PARAMETER — should be removed from predictions

Condition to upgrade to C_RANGE_PREDICTED:
  Add saturation postulate c = v_s as an explicit axiom AND
  identify a substrate material with ξ_c < chip_size

Condition to upgrade to C_PREDICTED:
  Prove from FPUT-3 that the projected PRW speed must equal v_s
  (currently an open problem)
```

---

*Script: scripts/p26_c_derivation_audit.py*  
*Data: outputs/data/c_derivation_audit.json*  
*Date: 2026-08-21*  
*This is an audit. No theory modified. No c values chosen for experimental convenience.*
