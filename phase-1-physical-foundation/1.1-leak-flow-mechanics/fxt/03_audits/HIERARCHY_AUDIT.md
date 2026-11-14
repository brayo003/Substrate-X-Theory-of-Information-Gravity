# Focused Audit: Theorem-to-Code Correspondence and Claim Scope

**Date:** 2026-10-25
**Status:** COMPLETE
**Auditor:** Focused verification session
**Repository:** `phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt/`
**Reports audited:**
  - `03_audits/THREE_LEVEL_HIERARCHY_REPORT.md`
  - `04_validations/verify_kolmogorov_hierarchy.py`

---

## Executive Summary

The three-level hierarchy report correctly identifies the relevant
literature and verifies a specific calculation. However, four issues
need correction before treating it as a reliable research handoff:

1. The theorem (Lonigro-Chruściński Prop. 4.1) has narrower assumptions
   than the report's shorthand suggests.
2. The script implements the regression formula (Markovian multitime
   statistics) rather than independently testing it. It computes P_n
   under the ASSUMPTION of Markovianity, then checks Kolmogorov
   consistency. It does not verify that the FXT process satisfies the
   regression formula from first principles.
3. The claim about complex dephasing producing quantum statistics needs
   careful wording: a deterministic phase rotation from energy splitting
   is conventional quantum dynamics, not a new prediction.
4. The Markovianity claim conflates three distinct conditions: the
   regression formula (needed by the theorem), CP-divisibility, and RHP
   non-Markovianity. These are not interchangeable.

This document corrects each issue and produces three deliverables:
the classical model class definition, the multitime probability
derivation, and the quantitative discriminator.

---

## Issue 1: Theorem Assumptions

### What the theorem actually says

Lonigro & Chruściński (2022), Proposition 4.1:

> Let dim H_S = 2 and consider a Hamiltonian H = Σ_j |e_j⟩⟨e_j| ⊗ H_j
> such that the corresponding dephasing process is Markovian; consider
> an initial state ρ_{t_0} diagonal in the dephasing basis
> {|e_j⟩}_{j=0,1}, and choose as measurement basis any of the unbiased
> bases {|m_x(φ)⟩}_{x=0,1}. Then the process is classical if and only
> if the dephasing function φ(t,s) is real-valued.

The assumptions are:
1. **System dimension:** d = 2 (qubit only).
2. **Dephasing-type Hamiltonian:** H = Σ_j |e_j⟩⟨e_j| ⊗ H_j
   (block-diagonal in the system basis).
3. **Markovianity:** the regression formula holds (Prop. 2.1, Eq. 14).
4. **Initial state:** diagonal in the dephasing basis.
5. **Measurement basis:** mutually unbiased with the dephasing basis.

### What the report's shorthand suggested

The report's summary section states:

> Markovian qubit: classicality (all orders) iff dephasing function
> φ(t,s) is real (ε=0).

This omits assumptions 2, 4, and 5. The theorem is not a universal
statement about all dephasing processes or all measurement protocols.
It applies specifically to:
- Pure dephasing (not general dissipative dynamics).
- Diagonal initial states (not arbitrary preparations).
- MUB measurements (not arbitrary measurement bases).

### Correction

The report should state all five assumptions whenever invoking the
proposition. The condition "φ is real" is necessary and sufficient for
classicality only within the specified protocol. Other initial states
or measurement bases may yield different classicality conditions.

---

## Issue 2: Theorem-to-Code Correspondence

### What the script computes

The script's `multitime_probability` function implements:

```
P_n(x_n,...,x_1) = Tr[P_{x_n} Λ_{t_n,t_{n-1}} ... P_{x_1} Λ_{t_1,t_0}(ρ_0)]
```

This is the regression formula (Lonigro-Chruściński Eq. 7). It computes
P_n **under the assumption that the process is Markovian** (regression
formula holds). It does NOT independently verify that the FXT process
satisfies the regression formula.

The script then checks the Kolmogorov consistency condition:

```
Σ_{x_2} P_3(x_3,t_3;x_2,t_2;x_1,t_1) = P_2(x_3,t_3;x_1,t_1)
```

This is the correct test for 3-classicality. But it tests classicality
of the Markovian-approximated process, not of the full FXT dynamics.

### The gap

The FXT dephasing function W(t) = exp(-Φ(t)) is computed from the
two-point correlation function C_JJ(t) alone:

```
Φ(t) = ∫_0^t (t-s) C_JJ(s) ds
```

This is the second-order (Gaussian) cumulant result. For a Gaussian
process, all higher cumulants vanish (Wick's theorem), and the
dephasing tensor factorizes, giving the regression formula.

But the actual PRW substrate is a telegraph process (non-Gaussian).
The current J(t) takes values ±v, not Gaussian-distributed values.
The Gaussian approximation enters when the FXT uses only C_JJ to
compute W(t), which is the standard Born approximation in open quantum
systems.

**Consequence:** The script verifies Kolmogorov consistency for the
Gaussian-approximated FXT model. It does not verify it for the full
PRW dynamics. If higher cumulants of the PRW were included, the
regression formula might not hold, and the multitime statistics would
differ from what the script computes.

### What is proven

- For the Gaussian-approximated FXT model (using C_JJ only), the
  regression formula holds (because Gaussian cumulants factorize).
- Under this approximation, φ(t,s) is real-valued.
- Therefore, by Prop. 4.1, the Gaussian-approximated process is
  classical (Kolmogorov-consistent at all orders) for the specified
  protocol.

### What is NOT proven

- That the full (non-Gaussian) PRW satisfies the regression formula.
- That the full PRW multitime statistics are Kolmogorov-consistent.
- That no modification of the PRW could produce quantum multitime
  statistics (the theorem only applies within its assumptions).

### Correction

The script should document that it uses the regression formula as an
assumption, not as a verified property. The semigroup property
φ(t3,t1) = φ(t3,t2)·φ(t2,t1) (verified numerically to machine epsilon)
is necessary for the regression formula but not sufficient — the full
dephasing tensor must also factorize.

---

## Issue 3: The Complex-Phase Claim

### What the report says

> To produce genuinely quantum multitime statistics, one would need:
> 1. A complex dephasing function (ε ≠ 0) — requires energy splitting
>    in the dephasing dynamics.

### The problem

A complex dephasing function φ(t,s) = exp(-(γ/2 + iε)(t-s)) arises
from a Hamiltonian with energy splitting ε between the dephasing basis
states. This is conventional quantum mechanics — a qubit with a
nonzero energy gap.

Adding ε ≠ 0 to the FXT model would produce Kolmogorov violation
(quantum multitime statistics), but this would not be a new prediction.
It would simply reproduce the well-known fact that a qubit with energy
splitting, measured in an unbiased basis, exhibits quantum measurement
statistics. This is textbook quantum mechanics.

### What would constitute a genuine FXT prediction

For the FXT to make a genuine claim, it would need to:

1. **Derive** the complex phase from the substrate dynamics, not insert
   it as a free parameter ε. The substrate equations must produce a
   nonzero imaginary component in the dephasing function through their
   own dynamics.

2. **Show** that the resulting model predicts something that an
   appropriately specified conventional model does not. Simply having
   ε ≠ 0 is not distinctive — any qubit with an energy gap has this.

3. **Identify** what is different about the substrate-derived phase
   compared to a conventional energy splitting. If there is no
   difference, the result is conventional physics in different notation.

### Correction

The report should replace the claim about "complex dephasing producing
quantum statistics" with the more precise statement:

> Within the assumptions of Prop. 4.1 (Markovian qubit dephasing,
> diagonal initial state, MUB measurement), a complex dephasing
> function produces Kolmogorov violation. However, a complex φ
> corresponds to a conventional energy splitting, which is not a
> distinctive prediction. For the FXT to make a genuine claim, the
> complex phase must be derived from substrate dynamics and must
> produce a prediction that differs from the appropriate conventional
> model.

---

## Issue 4: Markovianity Definitions

### Three distinct conditions

The FXT model and the report use "Markovian" in three different senses
that are not interchangeable:

1. **Regression formula** (Lonigro-Chruściński Prop. 2.1, Eq. 14):
   The dephasing tensor factorizes:
   ```
   Tr[U^{j_n,ℓ_n}_{t_n,t_{n-1}} ... U^{j_1,ℓ_1}_{t_1,t_0}(ϱ_B)]
     = ∏_k Tr[U^{j_k,ℓ_k}_{t_k,t_{k-1}}(ϱ_B)]
   ```
   This is the condition needed by Prop. 4.1. It is a property of the
   full multitime dephasing tensor, not just the two-point function.

2. **CP-divisibility** (Rivas-Huelga-Plenio 2014):
   The intermediate map Λ_{t2,t1} is CPTP for all t2 ≥ t1.
   For dephasing: γ(t) ≥ 0 for all t.
   The FXT code checks this and finds it holds.

3. **RHP non-Markovianity measure**:
   ∫ |dγ/dt| dt where dγ/dt < 0.
   The FXT code computes this and finds it equals 0.
   This is equivalent to CP-divisibility for dephasing channels.

### What the theorem needs vs what the code checks

| Condition | Needed by theorem? | Checked by code? | Holds for FXT? |
|-----------|-------------------|-----------------|----------------|
| Regression formula | YES | NO (assumed) | YES (Gaussian approx.) |
| Semigroup of φ | Necessary | YES (machine eps) | YES |
| CP-divisibility (γ≥0) | NO | YES | YES |
| RHP measure = 0 | NO | YES | YES |

The code checks CP-divisibility and RHP, but the theorem needs the
regression formula. The code's checks are relevant but not the same
condition. The regression formula holds for the FXT because the
Gaussian approximation (using C_JJ only) ensures factorization of the
dephasing tensor — but this is not explicitly verified by the code.

### The semigroup property is necessary but not sufficient

The semigroup property φ(t3,t1) = φ(t3,t2)·φ(t2,t1) (verified to
machine epsilon) is necessary for the regression formula but not
sufficient. The full regression formula requires the n-time dephasing
tensor to factorize, which involves all indices (j_k, ℓ_k), not just
the (0,1) component that defines φ.

For a Gaussian process, the regression formula holds because all
higher cumulants vanish. For a non-Gaussian process (like the actual
PRW telegraph process), the regression formula may fail even if the
semigroup property of φ holds.

### Correction

The report should explicitly state which Markovianity condition is
used and why. The correct statement is:

> The FXT model satisfies the regression formula within the Gaussian
> (Born) approximation, because the dephasing function is computed from
> the two-point correlation function C_JJ alone. This ensures
> factorization of the dephasing tensor for Gaussian statistics. The
> code verifies the semigroup property of φ (necessary condition) to
> machine epsilon. CP-divisibility and RHP non-Markovianity = 0 are
> also verified but are distinct conditions that are not the one
> required by the theorem.

---

## Deliverable 1: Classical Model Class and Operational Test

### The classical model class

The comparison class is the set of classical stochastic processes
{X(t)} that produce dephasing channels on a qubit via the standard
coupling:

```
H_int = g · X(t) · σ_z
```

where X(t) is a classical random process with correlation function
C_X(t) = ⟨X(t)X(0)⟩.

The induced dephasing channel at time t is:

```
Λ_t(ρ) = E[U(t) ρ U(t)†]
```

where U(t) = exp(-i g σ_z ∫_0^t X(s) ds) and E[·] is the classical
expectation.

For Gaussian X(t), the channel is fully determined by C_X(t):

```
Λ_t(ρ) = |0⟩⟨0|ρ|0⟩⟨0| + |1⟩⟨1|ρ|1⟩⟨1| + W(t) ρ₀₁ |0⟩⟨1| + W*(t) ρ₁₀ |1⟩⟨0|
```

where W(t) = exp(-g² Φ(t)) and Φ(t) = ∫_0^t (t-s) C_X(s) ds.

### Operational test for classicality

The operational test is the Kolmogorov consistency condition applied
to multitime measurement statistics:

**Protocol:**
1. Prepare the qubit in a state diagonal in the dephasing basis
   {|e₀⟩, |e₁⟩}: ρ₀ = p|e₀⟩⟨e₀| + (1-p)|e₁⟩⟨e₁|.
2. At times t₁, t₂, ..., t_n, perform projective measurements in a
   basis mutually unbiased with the dephasing basis.
3. Record outcomes x₁, x₂, ..., x_n ∈ {0, 1}.
4. Compute P_n(x_n, t_n; ...; x₁, t₁) using the regression formula
   (assuming Markovianity).
5. Check the Kolmogorov condition:
   ```
   Σ_{x_j} P_n(...; x_j, t_j; ...) = P_{n-1}(...; [x_j removed]; ...)
   ```

**Classicality criterion:** The process is classical (reproducible by
a classical stochastic process) if and only if the Kolmogorov condition
holds for all n.

**For the FXT matrix PRW:** The dephasing function is real-valued
(φ(t,s) = exp(-(Φ(t)-Φ(s))) with Φ real). Under the assumptions of
Prop. 4.1 (Markovian, qubit, diagonal initial state, MUB measurement),
the process is classical at all orders.

### Scope of the comparison class

This comparison class includes:
- Single OU process (scalar PRW): single exponential C_X
- Multi-bath OU process (matrix PRW): multi-exponential C_X
- Any classical Gaussian process with arbitrary C_X

It does NOT include:
- Quantum baths (where the bath has its own quantum dynamics)
- Non-Gaussian classical processes (where higher cumulants contribute)
- Higher-dimensional systems (d > 2)
- Non-Markovian dynamics (where the regression formula fails)

---

## Deliverable 2: Multitime Probabilities from FXT Dynamics

### Setup

The FXT matrix PRW produces a classical current J(t) with correlation:

```
C_JJ(t) = Σ_k S_k exp(-rate_k |t|)
```

where rate_k = λ(1 + r_k) and S_k are the sector weights.

The qubit couples via H_int = g · J(t) · σ_z.

### Dephasing function

Within the Gaussian (Born) approximation, the dephasing function is:

```
W(t) = exp(-g² Φ(t))
```

where

```
Φ(t) = ∫_0^t (t-s) C_JJ(s) ds = Σ_k S_k [t/rate_k - (1-exp(-rate_k t))/rate_k²]
```

This is real-valued because all S_k and rate_k are real and positive.

### Multitime probabilities (regression formula)

Under the Markovian assumption (regression formula holds), the n-time
joint probability for MUB measurements is:

```
P_n(x_n, t_n; ...; x₁, t₁) = Tr[P_{x_n} Λ_{t_n,t_{n-1}} ... P_{x₁} Λ_{t₁,t₀}(ρ₀)]
```

where:
- P_x = |m_x⟩⟨m_x| with |m₀⟩ = (|e₀⟩+|e₁⟩)/√2, |m₁⟩ = (|e₀⟩-|e₁⟩)/√2
- Λ_{t,s}(ρ) applies the dephasing channel with factor φ(t,s) = W(t)/W(s)
- ρ₀ = p|e₀⟩⟨e₀| + (1-p)|e₁⟩⟨e₁| (diagonal in dephasing basis)

### Explicit formulas (qubit, MUB measurement)

For n = 1:
```
P₁(x₁, t₁) = 1/2  (uniform, independent of time)
```

For n = 2:
```
P₂(x₂, t₂; x₁, t₁) = 1/4 [1 + (-1)^{x₂+x₁} φ(t₂,t₁)]
```

For n = 3:
```
P₃(x₃, t₃; x₂, t₂; x₁, t₁) = 1/8 [1 + (-1)^{x₃+x₂} φ(t₃,t₂)
                                     + (-1)^{x₂+x₁} φ(t₂,t₁)
                                     + (-1)^{x₃+x₁} φ(t₃,t₁)]
```

(These match Lonigro-Chruściński Eqs. 58-59 with real φ.)

### Kolmogorov check

The 2-classicality condition:
```
Σ_{x₁} P₂(x₂, t₂; x₁, t₁) = P₁(x₂, t₂)
```

LHS = Σ_{x₁} 1/4 [1 + (-1)^{x₂+x₁} φ(t₂,t₁)] = 1/2 = RHS. ✓

The 3-classicality condition (key test):
```
Σ_{x₂} P₃(x₃, t₃; x₂, t₂; x₁, t₁) = P₂(x₃, t₃; x₁, t₁)
```

LHS = Σ_{x₂} 1/8 [1 + (-1)^{x₃+x₂} φ₃₂ + (-1)^{x₂+x₁} φ₂₁ + (-1)^{x₃+x₁} φ₃₁]
    = 1/4 [1 + (-1)^{x₃+x₁} φ₃₁]
    = P₂(x₃, t₃; x₁, t₁) = RHS. ✓

(Here φ_{ij} = φ(t_i, t_j), and the sum over x₂ kills the cross terms
because Σ_{x₂} (-1)^{x₂} = 0.)

### Assumptions made

1. **Gaussian approximation:** W(t) computed from C_JJ alone (Born
   approximation). Higher cumulants of the PRW are neglected.
2. **Regression formula:** assumed to hold (follows from Gaussian
   approximation via Wick's theorem).
3. **Qubit (d=2):** the formulas are specific to d=2.
4. **Diagonal initial state:** ρ₀ diagonal in dephasing basis.
5. **MUB measurement:** measurement basis mutually unbiased with
   dephasing basis.
6. **Real φ:** the dephasing function is real-valued (no energy
   splitting in the dephasing dynamics).

Under these six assumptions, the FXT matrix PRW produces classical
multitime statistics (Kolmogorov-consistent at all orders).

### What is NOT assumed away

- The multi-exponential structure of C_JJ is fully included.
- The time-dependence of the dephasing rate γ(t) is included.
- The non-semigroup nature of γ(t) (it is not constant) is included.
  (The semigroup property of φ still holds because
  φ(t,s) = exp(-(Φ(t)-Φ(s))) factorizes.)

---

## Deliverable 3: Quantitative Discriminator

### The question

Can the FXT matrix PRW produce a quantitative prediction that
differs from the strongest applicable conventional model?

### The strongest conventional model

The strongest conventional model in the comparison class is a
classical Gaussian process with arbitrary (real) correlation function
C(t), coupled via H_int = g · X(t) · σ_z.

This model includes:
- Single OU (scalar PRW equivalent): C(t) = S exp(-γ|t|)
- Multi-bath OU (matrix PRW equivalent): C(t) = Σ_k S_k exp(-γ_k |t|)
- Any classical Gaussian process with real C(t)

For any such model with real C(t), the dephasing function is real,
and by Prop. 4.1, the multitime statistics are classical (for the
specified protocol).

### The discriminator (and why it fails)

The proposed discriminator would be:

**Hypothesis:** The FXT matrix PRW produces multitime statistics that
differ from any classical Gaussian process.

**Test:** Compute the Kolmogorov violation for the FXT model and
compare to zero.

**Result:** The Kolmogorov violation is zero (to machine epsilon)
for the FXT matrix PRW under the specified protocol.

**Conclusion:** The discriminator fails. The FXT matrix PRW does not
produce multitime statistics that differ from the conventional model
class, because both produce classical statistics.

### What would a successful discriminator require?

A successful discriminator would need to move outside the comparison
class. Three specific routes:

**Route A: Non-Gaussian substrate.**
If the FXT used the full (non-Gaussian) PRW statistics, the dephasing
function would include higher cumulants:

```
W(t) = exp(-g² Φ₂(t) + g⁴ Φ₄(t) - ...)
```

where Φ₂ is the second-order cumulant (Gaussian) and Φ₄ is the
fourth-order cumulant. The fourth-order cumulant is nonzero for the
telegraph process. The regression formula would fail, and the
multitime statistics could differ from the Gaussian prediction.

**Quantitative prediction:** The fourth-order cumulant of the PRW
telegraph process is:
```
⟨J(t₁)J(t₂)J(t₃)J(t₄)⟩_connected ≠ 0
```

This produces a correction to W(t) that is not captured by any
classical Gaussian process. The discriminator would be:

```
Δ = P₃^{FXT,non-Gaussian} - P₃^{Gaussian}
```

If Δ ≠ 0, the FXT (with full statistics) produces different multitime
statistics from any Gaussian model.

**Risk:** The non-Gaussian corrections may be too small to detect
in practice, or they may be reproducible by a non-Gaussian classical
model (which is a larger comparison class).

**Route B: Higher-dimensional system (d > 2).**
For d > 2, single-time RU is not automatic (Kayser et al. 2015).
The FXT could produce a dephasing channel that is not
RU-representable, which would be a genuine quantum signature at
Level 1.

**Quantitative prediction:** Compute the RU distance (Kayser et al.
geometric measure) for the FXT dephasing channel in d = 3.

**Risk:** The specific FXT channel might still be RU-representable
in d = 3. The condition for RU in d > 2 is more restrictive but not
every non-unital channel is non-RU.

**Route C: Derived complex phase.**
If the FXT substrate dynamics produced a complex dephasing function
through its own equations (not inserted as ε), this would produce
Kolmogorov violation.

**Quantitative prediction:** The imaginary part of φ would produce:

```
Δ = (1/8)(-1)^{x₃-x₁} exp(-γ(t₃-t₁)/2) · Im(φ_{t₃,t₂}) · Im(φ_{t₂,t₁})
```

**Risk:** If the imaginary part of φ is just a conventional energy
splitting (Hamiltonian term Bσ_z), this is not a distinctive
prediction. The FXT would need to show that the substrate produces
a phase that cannot be reproduced by adding an energy term to the
conventional model.

### Why the current model cannot produce a discriminator

The FXT matrix PRW, under the Gaussian approximation, produces:

1. A real dephasing function → classical at Level 3 (Prop. 4.1).
2. A multi-exponential correlation → reproducible by multi-bath OU.
3. A time-dependent rate γ(t) → still CP-divisible and Markovian
   (regression formula holds in Gaussian approximation).

No combination of these properties produces a statistic that differs
from the conventional Gaussian model class. The multi-exponential
structure enriches the correlation function but does not change the
level of classicality.

---

## Summary of Corrections

| Report claim | Issue | Correction |
|-------------|-------|-----------|
| "φ real → classical" | Omits assumptions 2,4,5 | State all assumptions of Prop. 4.1 |
| "Script verifies classicality" | Uses regression formula as assumption | Document that Markovianity is assumed, not tested |
| "Complex φ → quantum statistics" | Energy splitting is conventional | Must derive phase from substrate, not insert it |
| "FXT is Markovian" | Conflates three definitions | Regression formula (needed) ≠ CP-divisible ≠ RHP |
| "Need ε≠0 to escape" | Not a distinctive prediction | ε from energy splitting is textbook QM |

---

## What the Report Gets Right

- The three-level hierarchy is correctly identified.
- The relevant literature is correctly cited.
- The computational test correctly implements the Kolmogorov condition.
- The numerical results are correct (verified to machine epsilon).
- The FXT matrix PRW is classical under the specified assumptions.
- The multi-exponential enrichment does not help.

## What Needs Qualification

- The theorem applies only within its stated assumptions (qubit,
  Markovian, diagonal state, MUB measurement).
- The script assumes Markovianity via the regression formula; it does
  not test it from the full PRW dynamics.
- The Gaussian approximation is what guarantees the regression formula;
  the full (non-Gaussian) PRW might behave differently.
- A complex φ from energy splitting is conventional physics, not a
  distinctive FXT prediction.

---

## Reproducibility

### Commands executed

```bash
cd fxt && python 04_validations/verify_kolmogorov_hierarchy.py
cd fxt && python3 -c "<semigroup and CP-divisibility checks>"
```

### Key numerical results

- Semigroup property: φ(t3,t1) = φ(t3,t2)·φ(t2,t1), diff < 1.11e-16
- CP-divisibility: min(dγ/dt) = 2.27e-08 > 0 (Markovian by RHP)
- 3-classicality (real φ): violation = 2.50e-16 (classical)
- 3-classicality (complex φ, ε=1): violation = 0.292 (quantum)
- 3-classicality (matrix PRW): violation = 3.61e-16 (classical)

### Files

- `03_audits/THREE_LEVEL_HIERARCHY_REPORT.md` — original report (audited)
- `03_audits/HIERARCHY_AUDIT.md` — this document (audit and corrections)
- `04_validations/verify_kolmogorov_hierarchy.py` — verification script
- `04_validations/matrix_prw_investigation.py` — FXT matrix PRW code
