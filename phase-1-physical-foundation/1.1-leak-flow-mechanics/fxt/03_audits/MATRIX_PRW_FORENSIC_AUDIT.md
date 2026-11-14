# Matrix PRW Forensic Audit and Next-Stage Direction Selection

**Date:** 2026-10-25
**Status:** COMPLETE
**Auditor:** Independent forensic verification session
**Repository:** `phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt/`
**Artifacts inspected:**
  - `04_validations/matrix_prw_investigation.py` (37,187 bytes, 2026-10-25 21:06)
  - `04_validations/MATRIX_PRW_AUDIT.md` (7,244 bytes, 2026-10-25 21:18)
  - `04_validations/outputs/matrix_prw_investigation.json` (5,978 bytes, 2026-10-25 21:17)
  - `04_validations/outputs/matrix_prw_gate4_comparison.png` (110,470 bytes, 2026-10-25 21:07)
  - `04_validations/outputs/matrix_prw_simulation_verification.png` (120,294 bytes, 2026-10-25 21:17)
  - `04_validations/verify_decay_rate.py` (new verification script, this session)

---

## 1. Executive Verdict

The matrix PRW investigation correctly established that:

1. A matrix-valued persistent random walk is a **classical stochastic process** with
   matrix-valued internal states. The observable algebra is commutative.

2. The matrix structure enriches the correlation function from single-exponential
   to multi-exponential, with decay rates λ(1+r_k) where r_k are eigenvalues of the
   R superoperator R(M) = E[UMU†].

3. A conventional two-bath model reproduces the matrix PRW spectrum exactly
   (max difference = 0.00e+00).

4. CP is always preserved. The RHP non-Markovianity measure is 0.

The investigation's claim that this is a "stronger negative result than the original
FXT" is **partially correct**. It demonstrates that enriching the internal state space
from scalar to matrix does not cross the classical-to-quantum boundary for this
specific model class. However, this result is an **example within a known class**
(Crow & Joynt 2014, Kayser et al. 2015), not a new theorem. The original FXT already
proved the scalar case; this investigation extends the example to the matrix case
without establishing a universal impossibility.

---

## 2. Reproduction Report

### Commands executed

```
cd fxt && python 04_validations/matrix_prw_investigation.py
cd fxt && python 04_validations/verify_decay_rate.py
```

### Numerical results

**Decay rate verification (independent balance equation simulation):**

| r_k | Predicted rate λ(1+r_k) | Measured rate | Relative error |
|-----|------------------------|---------------|----------------|
| 0.0 | 1.0000 | 1.000050 | 5.00×10⁻⁵ |
| 0.5 | 1.5000 | 1.500113 | 7.50×10⁻⁵ |
| 0.9 | 1.9000 | 1.900181 | 9.50×10⁻⁵ |
| 1.0 | 2.0000 | 2.000200 | 1.00×10⁻⁴ |

Errors are consistent with Euler method truncation at dt=10⁻⁴.

**Two-bath equivalence:** Max |S_matrix − S_twobath| = 0.00e+00 (exact analytical match).

**Stochastic simulation:** 200,000 steps, 500 walkers. Max |C_emp − C_single_exp| = 0.0401
(consistent with finite-sample noise at 500 walkers).

**FFT verification:** Wiener-Khinchin transform verified at non-zero frequencies
(max diff at ω=1.0: 0.000000). Large diff near ω=0 is a known FFT wrap-around artifact,
not a mathematical error.

### Dependencies

numpy, scipy, matplotlib. All available in the repository environment.

---

## 3. Mathematical Audit

### 3.1 Balance equations (verified)

For sector k with R-eigenvalue r_k:

```
∂n⁺_k/∂t = -v ∂n⁺_k/∂x - λ n⁺_k + λ r_k n⁻_k
∂n⁻_k/∂t = +v ∂n⁻_k/∂x + λ r_k n⁺_k - λ n⁻_k
```

Current equation derived independently:

```
dq_k/dt = -v² ∂s_k/∂x - λ(1+r_k) q_k
```

**Derivation verified algebraically and numerically.** The key step:

```
-vλ n⁺_k - vλ r_k n⁺_k + vλ r_k n⁻_k + vλ n⁻_k
= -vλ(1+r_k) n⁺_k + vλ(1+r_k) n⁻_k
= -λ(1+r_k) q_k
```

### 3.2 R superoperator eigenvalues (verified)

For n=2, Pauli basis {I, σx, σy, σz}:

| Distribution | R(I) | R(σx) | R(σy) | R(σz) | Source |
|-------------|------|-------|-------|-------|--------|
| Haar U(2) | 1 | 0 | 0 | 0 | Schur's lemma |
| {I,σz} | 1 | 0 | 0 | 1 | Direct calculation |
| Partial(p) | 1 | p | p | p | Definition |
| Identity | 1 | 1 | 1 | 1 | Trivial |

These are standard results in quantum information theory. The Haar case
follows from Schur's lemma: the Haar integral E[U†AU] projects onto the
commutant of the full unitary group, which is {αI} for irreducible
representations.

### 3.3 CP claim (verified with caveat)

The dephasing rate γ(t) = Σ_k S_k(1−exp(−rate_k·t))/rate_k.

Since S_k ≥ 0 and rate_k > 0, each term is non-negative. Therefore
γ(t) ≥ 0 for all t ≥ 0. This guarantees CP for a time-local dephasing
channel with diagonal structure in the computational basis.

**Caveat:** The code claims "non-Markovian (time-dependent γ(t))" but then
reports RHP non-Markovianity = 0 and is_markovian = True. These are
inconsistent labels. The correct statement is: the dynamics IS Markovian
in the RHP sense (γ(t) monotonically non-decreasing, no information
backflow). The "non-Markovian" label in the code comment is misleading.
The dynamics has a time-dependent rate but is CP-divisible (Markovian
by RHP definition).

### 3.4 Identified issues

**Issue 1 (minor):** The code comment in Gate 3 says "Non-Markovian
(time-dependent γ(t))" but the RHP measure is 0, meaning the dynamics
IS Markovian. A time-dependent rate does not imply non-Markovianity.
Non-Markovianity requires information backflow (temporarily negative
γ(t)), which does not occur here.

**Issue 2 (cosmetic):** The FFT verification shows large error near ω=0
due to spectral wrap-around. This is a numerical artifact, not a math
error. The analytical equivalence is exact.

**Issue 3 (classification):** The code correctly classifies the model as
classical but does not prove that ALL matrix-valued classical substrates
must be classical. The classification is specific to the defined
observable structure (scalar projections Tr(A·q)).

---

## 4. Theorem Ledger

### Claim A: Scalar PRW + conventional coupling → conventional statistics

**Status: PROVEN** (by the original FXT, C2_FOUNDATIONS.md)

The original FXT proved that the scalar PRW produces a Lorentzian
spectrum reproducible by an OU process, that the master equation is
equivalent to Maxwell-Cattaneo/EIT, and that all derived observables
have conventional null models.

### Claim B: Matrix-valued classical PRW → multi-exponential correlation reproducible by two-bath

**Status: PROVEN** (by this investigation, verified independently)

The R superoperator decomposition shows C_JJ(t) = Σ_k S_k exp(−λ(1+r_k)t).
The two-bath model with τ_k = 1/(λ(1+r_k)) and matching amplitudes
reproduces the spectrum exactly (max diff = 0).

### Claim C: Enriching internal state space does not produce noncommutative observables

**Status: PROVEN for this specific model class**

The model defines observables as O_A = Tr(A·q) for fixed A. These are
scalar random variables. The algebra is commutative by construction.
This is a direct consequence of the observable definition, not a deep
theorem. It does NOT prove that no possible matrix-valued substrate
could produce noncommutative observables — only that this particular
construction (scalar projections of matrix-valued classical states)
does not.

### Claim D: No classical stochastic substrate can produce quantum behavior

**Status: NOT PROVEN**

The literature shows this is false as a universal claim. Crow & Joynt
(2014, PRA 89, 042123) proved that quantum dephasing CAN be simulated
classically via random unitary evolution. Kayser et al. (2015, PRA 92,
052117) showed that SOME decoherence channels CANNOT be represented as
random unitary (classical noise). The distinction is channel-dependent,
not universal.

The FXT results (both scalar and matrix) are examples of the simulable
class. They do not establish that ALL classical substrates fall in this
class.

### Summary table

| Claim | Status | Evidence |
|-------|--------|----------|
| A: Scalar PRW → conventional | PROVEN | C2_FOUNDATIONS.md, CONVENTIONAL_EQUIVALENCE_AUDIT.md |
| B: Matrix PRW → two-bath equivalent | PROVEN | This investigation, verified |
| C: This enrichment → commutative observables | PROVEN (model-specific) | By construction |
| D: All classical substrates → classical | NOT PROVEN | Literature contradicts universality |

---

## 5. Conventional-Equivalence Analysis

### Exact scope of two-bath equivalence

The two-bath model:
```
S(ω) = S₁ · 2τ₁/(1+ω²τ₁²) + S₂ · 2τ₂/(1+ω²τ₂²)
```
with parameters (S₁, τ₁, S₂, τ₂) — 4 free parameters.

The matrix PRW (Haar, n=2):
```
S(ω) = S_I · 2·(2λ)/(ω²+(2λ)²) + S_{tr} · 2·λ/(ω²+λ²)
```
with parameters (S_I, S_{tr}, λ) — 3 free parameters, rate ratio fixed at 2:1.

**The equivalence is exact and analytical.** Setting τ₁=1/(2λ), τ₂=1/λ,
S₁=S_I, S₂=S_{tr} gives identical spectra for all ω. This was verified
at 1000 frequency points with max difference = 0.00e+00.

**What the constraint removes:** One parameter (the ratio τ₂/τ₁ is fixed
at 2 for Haar, or 2/(1+p) for partial depolarizing). However, the
constraint depends on the free parameter p of the U distribution. If p
is allowed to vary, the constraint provides no parameter reduction —
the matrix PRW has the same 4 effective parameters as the two-bath model
(S_I, S_{tr}, λ, p).

**What is NOT proven:** Equivalence to ALL conventional models. The
comparison is specifically against a two-bath Lorentzian model. Other
conventional models (e.g., power-law baths, non-Gaussian noise, quantum
baths with non-flat spectral response) were not tested.

---

## 6. Literature and Novelty Assessment

### Prior results

1. **Crow & Joynt (2014), PRA 89, 042123:** "Classical Simulation of Quantum
   Noise." Proved that dephasing decoherence from a quantum bath can be
   simulated classically by random unitary evolution. Explicitly constructs
   the noise functional. Applied to spin-boson, central spin, and quantum
   impurity models.

2. **Kayser, Luoma & Strunz (2015), PRA 92, 052117:** "Geometric
   Characterization of True Quantum Decoherence." Proved that some
   decoherence channels CANNOT be represented as random unitary (classical
   noise). Provided a geometric measure for distance from the RU set.

3. **Wolf & Cirac (2008):** Characterized divisibility of quantum channels,
   relevant to the CP-divisibility check in Gate 3.

4. **Rivas, Huelga-Plenio (2014):** Defined the RHP non-Markovianity measure
   used in Gate 3 (integral of |dγ/dt| where dγ/dt < 0).

### What is new in the matrix PRW investigation

**The specific application to the PRW substrate model is new** — no one has
previously studied a matrix-valued persistent random walk with unitary
mixing at reversal and analyzed its bath statistics. The multi-exponential
correlation structure derived from the R superoperator eigenvalue spectrum
is a specific result for this model.

**The general principle is NOT new.** The fact that classical noise
(random unitary dynamics) can reproduce dephasing channels was proven by
Crow & Joynt (2014). The fact that multi-exponential correlations are
reproducible by multi-bath models is standard in open quantum systems.
The matrix PRW is a new example within the known class of classically
simulable channels.

### Novelty rating

- **Mathematical novelty:** LOW. The R superoperator decomposition and
  multi-exponential correlation are standard techniques.
- **Physics novelty:** LOW. The result is an example of a known phenomenon
  (classical simulation of dephasing).
- **Contribution:** The specific model (matrix PRW with unitary mixing)
  and its exact two-bath equivalence are a minor original result, but
  not publishable as a standalone theorem.

---

## 7. Research-Direction Comparison

### Direction A: Generalize the classical-equivalence theorem

**Problem addressed:** Prove a general theorem stating under what
conditions a classical stochastic substrate coupled via standard
open-quantum-systems methods cannot produce distinctive quantum behavior.

**Minimum new assumptions:** None — this would be pure mathematics within
existing frameworks.

**What FXT provides:** Two proven examples (scalar and matrix PRW).

**What must be imported:** The Crow-Joynt and Kayser et al. results.
The general theorem would need to characterize the boundary between
classically simulable and genuinely quantum channels.

**Feasibility:** MODERATE. The framework exists (GPT, quantum probability,
channel theory). The theorem would likely take the form: "Any
dephasing channel with positive correlation function is classically
simulable." This is close to existing results.

**Risk:** The result may already be proven in a more general form by
existing literature. Low novelty risk.

**Kill condition:** If the theorem turns out to be equivalent to
Crow-Joynt's result in different notation.

### Direction B: Noncommutative physical observable algebra

**Problem addressed:** Define a substrate whose physical observables form
a noncommutative algebra, and determine whether this produces genuinely
new predictions.

**Minimum new assumptions:** A new observable algebra must be defined
where observables are operator-valued and do not commute. The state
space, expectation functional, and dynamics must be specified.

**What FXT provides:** Proof that scalar and matrix-valued classical
state spaces do not produce noncommutative observables. This narrows
the search.

**What must be imported:** Operator algebra theory, quantum probability
(Accardi), GPT reconstruction (Hardy, Chiribella-D'Ariano-Perinotti).

**Feasibility:** LOW. This is the hardest open problem in quantum
foundations. Multiple research programs (Hardy 2001, CDP 2010,
Masanes-Müller 2011) have attempted this from different angles. No
complete derivation of the Hilbert space formalism from pre-quantum
principles exists.

**Risk:** HIGH. The result may simply reproduce standard quantum
mechanics in different notation. The "new" algebra may be equivalent
to an existing framework (von Neumann algebras, C*-algebras).

**Kill condition:** If the proposed noncommutative algebra can be
shown to be equivalent to a standard C*-algebra formulation of quantum
mechanics.

### Direction C: Search for a new operational prediction

**Problem addressed:** Find an observable that distinguishes a
precisely defined substrate model from all conventional models.

**Minimum new assumptions:** A substrate model with at least one
non-free parameter, or a constrained relationship that cannot be
reproduced by conventional models with the same or fewer parameters.

**What FXT provides:** A catalog of failed discriminators
(FINAL_DISTINCTIVENESS_DECISION.md, 12 candidates all RED). The P3
relation c=ξ_c/(2τ_B) as the only candidate that was not trivially
reproduced (but requires anomalous c).

**What must be imported:** Experimental parameters from real hardware
(Brisbane, Kyoto datasets already in the repository).

**Feasibility:** LOW-MODERATE. The FXT already exhausted the
discriminator search for the scalar PRW. The matrix PRW adds one
parameter (p) but this is free. A new discriminator would require a
model where the constraint is both non-trivial and parameter-free.

**Risk:** HIGH. The FXT's experience suggests that most "new"
predictions turn out to be reproducible by conventional models with
more parameters.

**Kill condition:** If the proposed discriminator can be reproduced
by a conventional model with the same or fewer free parameters.

### Comparison table

| Criterion | Direction A | Direction B | Direction C |
|-----------|-------------|-------------|-------------|
| Problem importance | 3/5 | 5/5 | 4/5 |
| Feasibility | 3/5 | 1/5 | 2/5 |
| Novelty risk (reproducing known) | LOW | HIGH | HIGH |
| Mathematical difficulty | 3/5 | 5/5 | 3/5 |
| FXT foundation | Two examples | Two negative results | 12 failed candidates |
| Time to first result | Weeks | Months-Years | Months |
| Publishability of negative result | MODERATE | LOW | HIGH |

---

## 8. Next-Stage Recommendation

### Primary direction: Direction A (Generalize the classical-equivalence theorem)

**Justification:**

1. The FXT has two proven examples (scalar and matrix PRW) that
   produce conventional statistics. The natural mathematical question
   is whether this is a theorem, not just examples.

2. The literature (Crow & Joynt 2014, Kayser et al. 2015) provides
   the framework: some dephasing channels are classically simulable
   (RU-representable), others are not. The FXT examples fall in the
   simulable class. The question is: what is the precise condition
   that determines the class?

3. This direction has the highest feasibility and the lowest novelty
   risk. A negative result (the theorem already exists) is still
   valuable because it would characterize the FXT's results precisely
   within the existing literature.

4. Direction B is too hard (25-year open problem). Direction C has
   high risk of reproducing the FXT's existing negative results.

### First milestone

**Research question:** Is the FXT's conventional-equivalence result
(both scalar and matrix) a consequence of the dephasing channel
structure alone, or does it depend on specific properties of the
PRW substrate?

**Mathematical problem:** Characterize the set of dephasing channels
induced by classical stochastic processes with Gaussian statistics
and exponential correlation functions. Determine whether this set
coincides with the set of classically simulable (RU-representable)
dephasing channels as characterized by Crow & Joynt (2014) and
Kayser et al. (2015).

**Proof obligation:** Prove (or disprove) the following statement:

> Every dephasing channel with a correlation function that is a
> finite sum of exponentials with positive weights is classically
> simulable (admits a random unitary representation).

If true, this subsumes both the scalar PRW (single exponential) and
matrix PRW (multi-exponential) results as special cases.

**Validation procedure:**
1. Derive the theorem from the Crow-Joynt framework.
2. Check that the matrix PRW is a special case.
3. Implement a numerical test: generate random multi-exponential
   correlation functions, construct the dephasing channel, and
   verify RU-representability using the Kayser et al. geometric
   measure.

**Pass criteria:** Theorem proven and verified against both PRW
cases and numerical test.

**Fail criteria:** A counterexample found — a multi-exponential
positive-correlation dephasing channel that is NOT RU-representable.
This would be a genuinely new result pointing toward Direction C.

**What success would establish:** The FXT's conventional-equivalence
results are consequences of a general theorem about classical
stochastic processes and dephasing channels. This characterizes
the FXT's contribution precisely within the existing literature.

**What success would NOT establish:** That no classical substrate can
produce distinctive quantum behavior. The Kayser et al. result shows
that non-RU channels exist. The question of whether a substrate can
produce a non-RU channel remains open.

---

## 9. Reproducibility Record

### Commands

```bash
# Reproduce matrix PRW investigation
cd fxt && python 04_validations/matrix_prw_investigation.py

# Verify decay rate formula independently
cd fxt && python 04_validations/verify_decay_rate.py
```

### Seeds

- matrix_prw_investigation.py: rng = np.random.default_rng(42)
- verify_decay_rate.py: deterministic (Euler method, no RNG)

### Key parameters

- λ = 1.0 (reversal rate, normalized)
- v = 1.0 (walker speed, normalized)
- n = 2 (matrix dimension)
- dt = 0.01 (simulation timestep)
- n_steps = 200,000
- n_walkers = 500

### Output files

- `04_validations/outputs/matrix_prw_investigation.json`
- `04_validations/outputs/matrix_prw_gate4_comparison.png`
- `04_validations/outputs/matrix_prw_simulation_verification.png`

### Environment

- Python 3.10
- numpy, scipy, matplotlib
- Linux (confirmed by system context)

---

## 10. Updated Research Handoff

### Current state

The FXT now has two proven negative results:

1. **Scalar PRW:** Classical substrate with standard coupling produces
   conventional bath statistics (OU-equivalent Lorentzian spectrum).

2. **Matrix PRW:** Matrix-valued classical substrate with standard
   coupling produces conventional bath statistics (two-bath-equivalent
   multi-exponential spectrum).

Both results are examples within the class of classically simulable
dephasing channels (Crow & Joynt 2014).

### Key assumptions that drive the negative results

1. **Observable algebra is commutative** (scalar projections of
   matrix-valued states).

2. **Coupling is linear and fixed** (H_int = g·J·σ_z, constant g).

3. **Born-Markov approximation** (standard open quantum systems).

4. **Gaussian statistics** (linear coupling to Gaussian substrate noise).

### What would need to change for a genuinely new result

Any one of:
- Noncommutative physical observables (not just internal labels)
- Nonlinear or state-dependent coupling
- Non-Born-Markov or non-Gaussian substrate
- A substrate that produces a non-RU-representable channel

### Recommended next step

Prove (or find a counterexample to) the theorem stated in §8. This
would determine whether the FXT's negative results are structural
(consequence of a general theorem) or contingent (specific to the
PRW model). Either outcome is valuable: a proof characterizes the
contribution; a counterexample opens a new research direction.

### Files for the next agent

- `01_foundations/C2_FOUNDATIONS.md` — original theorem ledger
- `FINAL_DISTINCTIVENESS_DECISION.md` — original negative result
- `CONVENTIONAL_EQUIVALENCE_AUDIT.md` — original conventional nulls
- `04_validations/matrix_prw_investigation.py` — matrix PRW code
- `04_validations/MATRIX_PRW_AUDIT.md` — matrix PRW audit
- `04_validations/verify_decay_rate.py` — independent verification
- This document — forensic audit and direction recommendation

### Literature to consult

- Crow & Joynt (2014), PRA 89, 042123 — classical simulation of dephasing
- Kayser, Luoma & Strunz (2015), PRA 92, 052117 — true quantum decoherence
- Rivas, Huelga-Plenio (2014) — RHP non-Markovianity measure
- Hardy (2001) — quantum reconstruction from axioms
- Chiribella, D'Ariano, Perinotti (2010) — purification postulate
