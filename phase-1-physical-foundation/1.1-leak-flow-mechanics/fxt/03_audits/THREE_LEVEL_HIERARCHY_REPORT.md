# The Three-Level Equivalence Hierarchy for Classical Stochastic Representations of Quantum Dephasing

**Date:** 2026-10-25
**Status:** COMPLETE
**Author:** Independent mathematical investigation session
**Repository:** `phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt/`
**Verification script:** `04_validations/verify_kolmogorov_hierarchy.py`

---

## 1. Question

Can a quantum dephasing process be reproduced by classical stochastic noise
at every individual time, yet fail to admit a consistent classical stochastic
realization of its full temporal dynamics?

This question separates three levels of equivalence between quantum
dephasing and classical stochastic processes:

1. **Single-time equivalence:** Does a classical model reproduce the quantum
   channel at a given time?
2. **All-time equivalence:** Can one classical stochastic model reproduce
   the family of channels at every time?
3. **Multitime equivalence:** Can it reproduce the statistics of sequences
   of interventions and measurements, not just the state at the end?

---

## 2. Literature

The key results are already established in the literature. This report
does not claim new theorems; it verifies existing ones independently and
applies them to the FXT matrix PRW.

### Level 1: Single-time random-unitary representability

**Landau & Streater (1993):** For a qubit (d=2), a channel is
random-unitary (RU) if and only if it is unital. Since all dephasing
channels are unital, all single-qubit dephasing channels are RU-representable
at any fixed time. This is trivial for qubits.

**Kayser, Luoma & Strunz (2015, PRA 92, 052117):** For d>2, unital is
necessary but not sufficient for RU. Non-RU dephasing channels exist in
higher dimensions. So single-time RU is nontrivial for qudits.

**Crow & Joynt (2014, PRA 89, 042123):** Explicitly constructed the
classical noise functional for any single-qubit dephasing model, proving
that quantum dephasing decoherence can be simulated classically by
random unitary evolution. Applied to spin-boson, central spin, and
quantum impurity models.

### Level 2: All-time classical stochastic process

The Crow-Joynt construction produces a classical noise model that
reproduces the qubit dephasing channel at all times. The construction
uses two noise histories with fixed probabilities (1/2, 1/2) and
time-dependent fields h₁(t), h₂(t) derived from the quantum transfer
matrix. The key structural point: the decomposition into two unitaries
with fixed probabilities works at every time, but the unitaries
themselves are time-dependent and state-dependent.

### Level 3: Multitime classicality (Kolmogorov consistency)

**Smirne et al. (2019, Quantum Sci. Technol. 4, 01LT01):** A Markovian
multitime statistics cannot be traced back to a classical statistics if
and only if the dynamics can generate coherences and subsequently turn
them into populations (the NCGD condition: non-coherence-generating-
and-detecting).

**Milz et al. (2020, PRX 10, 041049):** Full characterization of
classical processes for the non-Markovian case. Non-Markovian processes
exist that are genuinely quantum regardless of measurement scheme.
Classicality is connected to the vanishing of quantum discord between
the system and its environment.

**Lonigro & Chruściński (2022, arXiv:2211.02014):** The complete
framework for dephasing processes. Key results:
- N-classicality defined via Kolmogorov consistency conditions (Eq. 3).
- 2-classicality holds for diagonal initial state + MUB measurement,
  regardless of environment (Prop. 3.1, 3.3).
- Markovian qubit: classicality (all orders) iff dephasing function
  φ(t,s) is real-valued (Prop. 4.1).
- Markovian qudit (d>2): classicality if all off-diagonal dephasing
  factors are equal and real (Prop. 4.2, highly restrictive).
- Non-Markovian: only 2-classicality guaranteed, not full classicality.

---

## 3. Independent Derivations

### 3.1 Level 1: Why single-time RU is trivial for qubits

A single-qubit dephasing channel has the form:

```
Λ(ρ) = |0⟩⟨0|ρ|0⟩⟨0| + |1⟩⟨1|ρ|1⟩⟨1| + φ ρ₀₁ |0⟩⟨1| + φ* ρ₁₀ |1⟩⟨0|
```

where |φ| ≤ 1. In the Bloch vector representation, the transfer matrix is
(Crow-Joynt Eq. 11-12):

```
T = [[1, 0,    0,    0],
     [0, c,   -s,    0],
     [0, s,    c,    0],
     [0, 0,    0,    1]]
```

where c = Re(φ)·|φ| (scaled), s = Im(φ)·|φ|, and c² + s² = |φ|² ≤ 1.

The key result (Landau-Streater): for d=2, any unital channel is RU.
Since dephasing channels preserve the identity (unital), they are all RU.
The explicit RU decomposition (Crow-Joynt): write (c,s) as a convex
combination of two unit vectors:

```
(c, s) = ½(c + βs, s - βc) + ½(c - βs, s + βc)
```

where β = √(1-|φ|²)/|φ|. This gives two rotation angles Φ₁, Φ₂ with
probabilities 1/2 each. The channel is reproduced by:

```
Λ(ρ) = ½ U(Φ₁) ρ U(Φ₁)† + ½ U(Φ₂) ρ U(Φ₂)†
```

where U(Φ) = exp(iΦσ_z/2). This construction works at any fixed time t.

**Conclusion:** For d=2, single-time RU representability is trivial.
The theorem "all dephasing channels with positive correlation functions
are RU-representable" is vacuous for qubits — it holds for ALL dephasing
channels regardless of correlation structure.

For d>2, the situation is different: unital does not imply RU, and
non-RU dephasing channels exist (Kayser et al. 2015).

### 3.2 Level 2: All-time classical process

The Crow-Joynt construction produces a classical noise model with two
histories. At each time t, the dephasing factor φ(t) is decomposed into
two rotations with probabilities 1/2 each. The classical fields h₁(t)
and h₂(t) are continuous functions of time derived from the quantum
transfer matrix.

The key question: does this constitute a single consistent classical
stochastic process? The answer is yes — the construction defines a
classical probability space with two noise histories, and the channel
at each time is reproduced. This works because the dephasing channel
is unital at every time, hence RU-representable at every time.

**What this does NOT guarantee:** The Crow-Joynt construction ensures
that the channel Λ_t is reproduced at each time. It does not
automatically guarantee that the multitime statistics (sequences of
measurements) are classical. The distinction is:

- Level 2 asks: does Λ_t^{classical} = Λ_t^{quantum} for all t?
- Level 3 asks: does P_n^{classical}(x_n,t_n;...;x_1,t_1) = P_n^{quantum}
  for all n and all measurement sequences?

Level 2 does not imply Level 3.

### 3.3 Level 3: Multitime classicality — the Kolmogorov condition

Following Lonigro & Chruściński (2022), the multitime statistics of
repeated projective measurements is:

```
P_n(x_n,t_n;...;x_1,t_1) = Tr[P_{x_n} Λ_{t_n,t_{n-1}} ... P_{x_1} Λ_{t_1,t_0}(ρ_0)]
```

The Kolmogorov consistency condition requires:

```
Σ_{x_j} P_n(...;x_j,t_j;...) = P_{n-1}(...; [x_j removed]; ...)
```

This holds iff the statistics can be explained by a classical stochastic
process (Kolmogorov extension theorem).

For a Markovian qubit dephasing process with dephasing function
φ(t,s) = exp(-(γ/2 + iε)(t-s)), the key consistency condition is the
second Chapman-Kolmogorov equation (Prop. 4.1):

```
P_2(x_3,t_3;x_1,t_1) = Σ_{x_2} P_3(x_3,t_3;x_2,t_2;x_1,t_1)
```

The violation is (Lonigro-Chruściński Eq. 57):

```
Δ = P_2(x_3,t_3;x_1,t_1) - Σ_{x_2} P_3(x_3,t_3;x_2,t_2;x_1,t_1)
  = (1/8)(-1)^{x_3-x_1} exp(-γ(t_3-t_1)/2) · sin(ε(t_3-t_2)) · sin(ε(t_2-t_1))
```

This vanishes for all t_1, t_2, t_3 if and only if ε = 0, i.e., φ is
real-valued.

**Physical interpretation:** The parameter ε corresponds to the qubit's
energy splitting (the difference between energy levels). The process
is classical if and only if this splitting vanishes — the dephasing is
pure amplitude damping without any phase rotation.

---

## 4. Theorem

The following is a restatement of Lonigro & Chruściński (2022),
Proposition 4.1, with explicit assumptions. It is NOT a new theorem;
it is an existing result, independently verified.

**Theorem (Lonigro-Chruściński 2022, Prop. 4.1).**

*Let H = Σ_j |e_j⟩⟨e_j| ⊗ H_j be a dephasing-type Hamiltonian on
H_S ⊗ H_B with dim H_S = 2, such that the corresponding dephasing process
is Markovian (i.e., the regression formula holds). Let the initial state
ρ_{t_0} be diagonal in the dephasing basis {|e_j⟩}_{j=0,1}, and let the
measurement basis be any mutually unbiased basis {|m_x(φ)⟩}_{x=0,1}.*

*Then the process is classical (Kolmogorov-consistent at all orders) if
and only if the dephasing function*

```
φ(t,s) = Tr[U^{0,1}_{t,s}(ϱ_B)]
```

*is real-valued for all t ≥ s ≥ t_0.*

**Assumptions:**
1. The system is a qubit (d = 2).
2. The dephasing process is Markovian (regression formula holds).
3. The initial state is diagonal in the dephasing basis.
4. The measurement basis is mutually unbiased with respect to the
   dephasing basis.

**What the theorem says:** Under these conditions, the full multitime
statistics can be reproduced by a classical stochastic process if and
only if the dephasing function has no imaginary component (no energy
splitting, no phase rotation).

**What the theorem does NOT say:**
- It does not address d > 2 (where the conditions are more restrictive,
  Prop. 4.2).
- It does not address non-Markovian processes (where only
  2-classicality is guaranteed).
- It does not say that the channel cannot be reproduced at individual
  times (Level 1 always holds for qubits).
- It does not say that a classical process cannot reproduce the channel
  at all times (Level 2 always holds for qubits via Crow-Joynt).

---

## 5. Computational Verification

The script `verify_kolmogorov_hierarchy.py` independently verifies the
three levels.

### Test 1: Real dephasing function (ε = 0)

Parameters: γ = 0.5, ε = 0, diagonal initial state (p = 0.3), MUB measurement.

| Condition | Violation | Verdict |
|-----------|----------|---------|
| 2-classicality | 2.22e-16 | PASS (machine epsilon) |
| 3-classicality | 2.50e-16 | PASS (machine epsilon) |
| Analytical | 0.00e+00 | Confirmed |

### Test 2: Complex dephasing function (ε = 1.0)

Parameters: γ = 0.5, ε = 1.0, diagonal initial state (p = 0.3), MUB measurement.

| Condition | Violation | Verdict |
|-----------|----------|---------|
| 2-classicality | 2.22e-16 | PASS (machine epsilon) |
| 3-classicality | 2.92e-01 | FAIL (nonzero) |
| Analytical | 5.37e-02 | Confirmed (per-element) |

The 2-classicality always holds (diagonal state + MUB). The
3-classicality fails when φ is complex. The individual violations
exhibit the expected (-1)^{x_3-x_1} sign pattern.

### Test 3: Matrix PRW (multi-exponential, real)

Parameters: Haar U(2), mixed coupling (S₁ = S₂ = 0.5), rates {λ, 2λ},
multi-exponential real dephasing function.

| Condition | Violation | Verdict |
|-----------|----------|---------|
| 2-classicality | 2.22e-16 | PASS (machine epsilon) |
| 3-classicality | 3.61e-16 | PASS (machine epsilon) |

The matrix PRW has a real dephasing function (the multi-exponential
correlation function produces real φ(t,s) because all decay rates are
real and positive). Therefore it achieves Level 3 classicality.

### Test 4: Systematic scan

A scan over ε ∈ [0, 3] confirms that the 3-classicality violation is
zero at ε = 0 and nonzero for ε ≠ 0, following the predicted
sin(εΔt₁)·sin(εΔt₂) pattern.

---

## 6. Application to the FXT Matrix PRW

The FXT matrix PRW produces a dephasing function of the form:

```
φ(t,s) = exp(-(Γ(t) - Γ(s)))
```

where

```
Γ(t) = Σ_k S_k [t/rate_k - (1 - exp(-rate_k·t))/rate_k²]
```

with real, positive decay rates rate_k = λ(1 + r_k). Since all
parameters are real, φ(t,s) is real-valued. By the theorem (Prop. 4.1),
the matrix PRW is classical at all levels:

- **Level 1:** RU-representable at each fixed time (trivial for qubits).
- **Level 2:** A classical stochastic process reproduces the channel at
  all times (Crow-Joynt construction).
- **Level 3:** The multitime statistics satisfy Kolmogorov consistency
  (φ is real → Prop. 4.1 applies).

The matrix PRW is locked at Level 3 classicality. The multi-exponential
correlation structure does not help — what matters is not the number
of exponentials but whether φ has an imaginary component.

### What would be needed to escape Level 3 classicality

For a Markovian qubit dephasing process, the only escape is a complex
dephasing function (ε ≠ 0), corresponding to a nonzero energy splitting.
The matrix PRW as currently defined does not produce this because:
- The coupling H_int = g·J·σ_z is diagonal in the energy basis.
- The reversal process produces real decay rates.
- There is no mechanism for generating an imaginary phase component in φ.

To produce genuinely quantum multitime statistics, one would need:
1. A complex dephasing function (ε ≠ 0) — requires energy splitting
   in the dephasing dynamics.
2. Higher dimensions (d > 2) — where RU representability is not
   automatic and non-RU channels exist.
3. Non-Markovian dynamics — where 2-classicality does not imply full
   classicality (Milz et al. 2020).

---

## 7. The Gap Between Levels

The central finding is that the three levels are genuinely distinct:

```
Level 1 (single-time RU)      ←  trivial for qubits (always holds)
    ↓ does not imply
Level 2 (all-time classical)  ←  always achievable for qubits (Crow-Joynt)
    ↓ does not imply
Level 3 (multitime classical)  ←  iff φ is real (Lonigro-Chruściński)
```

**Level 1 → Level 2 gap:** A channel that is RU at each fixed time
need not be reproducible by a single classical process across all
times. However, for qubit dephasing, the Crow-Joynt construction closes
this gap.

**Level 2 → Level 3 gap:** A classical process that reproduces the
channel at all times need not reproduce the multitime statistics.
The gap is measured by:

```
Δ ∝ Im(φ_{t_3,t_2}) · Im(φ_{t_2,t_1})
```

This vanishes iff φ is real-valued. For the Markovian qubit case, this
is the complete characterization.

---

## 8. What This Establishes for the FXT

### Proven
- The FXT matrix PRW is classical at all three levels.
- The multi-exponential enrichment does not produce quantum behavior
  because the dephasing function remains real-valued.
- The negative result (no distinctive prediction) is a consequence of
  the model's structure: real dephasing function + qubit dimension +
  Markovian dynamics → Level 3 classicality.

### Not proven
- That NO classical substrate can produce quantum multitime statistics.
  The literature shows this is false: complex dephasing functions (ε ≠ 0)
  produce quantum multitime statistics even for qubits.
- That enriching the state space cannot help in higher dimensions.
  For d > 2, the RU representability question is nontrivial, and
  non-RU dephasing channels exist.

### Stopping condition

The question "can a classical stochastic process reproduce quantum
dephasing?" is already resolved by the existing literature:

- **For qubits at single times:** YES, always (Landau-Streater, Crow-Joynt).
- **For qubits at all times:** YES, always (Crow-Joynt construction).
- **For qubits at all orders (multitime):** YES iff φ is real
  (Lonigro-Chruściński Prop. 4.1).
- **For qudits at single times:** NOT always (Kayser et al.).
- **For non-Markovian processes:** NOT always (Milz et al. 2020).

The FXT's negative results are consistent with the first three points.
The FXT does not need a new theorem; it needs to either (a) use the
existing framework to identify which level it targets, or (b) move
to a regime where the existing results do not apply (d > 2, non-
Markovian, or complex dephasing functions).

---

## 9. Reproducibility

### Command

```bash
cd fxt && python 04_validations/verify_kolmogorov_hierarchy.py
```

### Dependencies

numpy (no scipy or matplotlib needed).

### Key parameters

- γ = 0.5 (dephasing rate)
- ε ∈ {0, 1.0} (imaginary part of dephasing function)
- p = 0.3 (initial state diagonal weight)
- t₁ = 0, t₂ = 1, t₃ = 2 (measurement times)
- Measurement basis: MUB (|+⟩, |−⟩)
- Matrix PRW: λ = 1.0, Haar U(2), S₁ = S₂ = 0.5

### Output

All tests pass. The key numerical results:
- Real φ: 3-classicality violation = 2.50e-16 (machine epsilon)
- Complex φ: 3-classicality violation = 2.92e-01 (nonzero)
- Matrix PRW: 3-classicality violation = 3.61e-16 (machine epsilon)

---

## 10. Literature References

1. **Landau & Streater (1993),** Linear Algebra Appl. 193, 107.
   - d=2: RU iff unital. d>2: unital necessary, not sufficient.

2. **Crow & Joynt (2014),** PRA 89, 042123. arXiv:1309.6383.
   - Classical simulation of single-qubit dephasing via RU evolution.
   - Explicit construction of the noise functional.

3. **Kayser, Luoma & Strunz (2015),** PRA 92, 052117. arXiv:1508.04027.
   - Geometric characterization of "true quantum" decoherence.
   - Non-RU dephasing channels exist for d > 2.

4. **Smirne et al. (2019),** Quantum Sci. Technol. 4, 01LT01.
   arXiv:1709.05267.
   - Markovian classicality iff NCGD condition.

5. **Milz et al. (2020),** PRX 10, 041049. arXiv:1907.05807.
   - Full characterization of classical non-Markovian processes.
   - Non-Markovian genuinely quantum processes exist.

6. **Lonigro & Chruściński (2022),** Front. Quantum Sci. Technol. 1,
   1090022. arXiv:2211.02014.
   - Complete framework for dephasing multitime classicality.
   - Prop. 4.1: Markovian qubit classicality iff φ real.
   - Prop. 4.2: Markovian qudit classicality (restrictive).

7. **Buscemi (2006),** arXiv:quant-ph/0607034.
   - Minimum number of unitaries for RU channels.
   - Confirms: d=2 all unital channels are Pauli channels (RU).

---

## 11. Research Handoff

### Current state

The three-level hierarchy is fully characterized by existing literature.
The FXT matrix PRW sits at Level 3 classicality (the most classical
level) because its dephasing function is real-valued.

### The precise gap

To produce genuinely quantum multitime statistics, the FXT would need to
move to a regime where the existing theorems do not guarantee
classicality:

1. **Complex dephasing function (ε ≠ 0):** Even for Markovian qubits,
   a complex φ produces quantum multitime statistics (Kolmogorov
   violation ≠ 0). This requires energy splitting in the dephasing
   dynamics.

2. **Higher dimensions (d > 2):** Single-time RU is not automatic.
   Non-RU dephasing channels exist (Kayser et al. 2015). The
   multitime classicality conditions are more restrictive (Prop. 4.2).

3. **Non-Markovian dynamics:** 2-classicality does not imply full
   classicality. Genuinely quantum non-Markovian processes exist
   (Milz et al. 2020).

### What a successful result would look like

A substrate model that produces either:
- A complex dephasing function φ(t,s) with nonzero imaginary part, or
- A dephasing channel in d > 2 that is not RU-representable, or
- A non-Markovian process with Kolmogorov violation at order 3 or higher.

Any of these would demonstrate that the substrate produces genuinely
quantum multitime statistics that cannot be reproduced by a classical
stochastic process.

### What would NOT be a successful result

- Adding more exponentials to the correlation function (still real φ).
- Enriching the internal state space while keeping d = 2 (still RU).
- Adding free parameters to the U distribution (doesn't change the
  level of classicality).
- Any modification that keeps φ real and d = 2 and Markovian.

### Files for the next agent

- `03_audits/MATRIX_PRW_FORENSIC_AUDIT.md` — original forensic audit
- `03_audits/THREE_LEVEL_HIERARCHY_REPORT.md` — this document
- `04_validations/verify_kolmogorov_hierarchy.py` — verification script
- `04_validations/matrix_prw_investigation.py` — matrix PRW code
- `04_validations/verify_decay_rate.py` — decay rate verification

### Literature to consult for next steps

- For d > 2: Kayser et al. (2015), Lonigro-Chruściński Prop. 4.2
- For non-Markovian: Milz et al. (2020), PRX 10, 041049
- For NCGD condition: Smirne et al. (2019)
- For quantum process tensors: Pollock et al. (2018), PRL 120, 040405
