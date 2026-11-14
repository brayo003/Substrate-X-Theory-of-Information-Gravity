# 03_KILL_TESTS.md
## Earliest Ways the Hypothesis Can Fail

**Date:** 2026-08-23
**Purpose:** List the earliest ways the SXC-X candidate can fail
**Status:** SYSTEMATIC KILL TEST ANALYSIS

---

## Kill Test 1: Mathematical Inconsistency

### Test Description
Can the primitive constraints be formulated consistently without mathematical contradiction?

### How to Test
Attempt to construct well-posed initial value problem for:
- q̇(x,t) ∈ K_X(q,x,t)
- With K_X defined as subset of tangent space
- With physical constraint P → Ω_X mapping

### Success Condition
Mathematical consistency: No contradictions in definitions, evolution always possible.

### Failure Condition
Mathematical inconsistency: Contradiction in definitions, or evolution becomes impossible at some configuration.

### Current Status
**PASSED**

**Reason:** The proposed mathematical structure (state q, configuration space Ω_X, admissible transitions K_X) is mathematically coherent. No contradictions found in definitions.

---

## Kill Test 2: No Nontrivial Stable Localized Solution

### Test Description
Does a stable localized X configuration exist under the primitive constraints?

### How to Test
Solve for stationary solution q(r) satisfying:
- ∂q/∂t = 0 (stationary)
- q̇ ∈ K_X (continuation)
- Physical constraint from central mass M

### Success Condition
Nontrivial stable localized solution exists (not trivial q = constant).

### Failure Condition
No stable localized solution exists (only trivial solutions like q = constant).

### Current Status
**FAILED**

**Reason:** Stable localized solution exists: q(r) = √[g(M)h(r)] r̂. This is nontrivial (depends on r and M) and satisfies the constraint f(q, M, r) ≤ 0.

---

## Kill Test 3: No Attractive Behavior

### Test Description
Does the X configuration produce any attractive behavior (inward acceleration)?

### How to Test
Compute effective acceleration from radial solution:
- Assume matter responds to X configuration gradient
- Calculate a(r) ∝ -∇|q(r)|
- Check sign (inward vs outward)

### Success Condition
Attractive behavior emerges (a(r) points inward).

### Failure Condition
No attractive behavior emerges (either repulsion or no force).

### Current Status
**FAILED**

**Reason:** Attractive behavior emerges: a(r) ∝ -∇|q(r)| produces inward acceleration proportional to r^{-(α/2+1)}.

---

## Kill Test 4: Attraction Requires Inserted Newtonian Structure

### Test Description
Does attractive behavior emerge without inserting Newton's inverse-square law, or does it require constitutive choices that reproduce it?

### How to Test
Derive radial law from primitive constraints:
- Determine what exponent α emerges naturally
- Determine what g(M) dependence emerges naturally
- Check if result is 1/r² with M dependence

### Success Condition
Inverse-square behavior emerges naturally from primitive constraints without arbitrary choices.

### Failure Condition
Inverse-square behavior requires:
- Assuming α = 2 (not derived)
- Assuming g(M) ∝ M² (not derived)
- Or similar constitutive insertions

### Current Status
**PASSED**

**Reason:** Inverse-square law does NOT emerge from primitive constraints. It requires constitutive choices:
- α = 2 (radial profile exponent)
- g(M) ∝ M² (constraint strength)
Neither is forced by primitive constraints X1-X4.

---

## Kill Test 5: Infinite Arbitrary Constitutive Freedom

### Test Description
Is the model underdetermined, with infinitely many constitutive choices leading to different radial laws?

### How to Test
Count degrees of freedom:
- Number of free parameters/functions in constitutive choices
- Number of distinct radial laws possible

### Success Condition
Model is determined or has limited degrees of freedom (few possible radial laws).

### Failure Condition
Infinite constitutive freedom remains (infinitely many radial laws possible).

### Current Status
**PASSED**

**Reason:** At least 5 free functions/parameters remain:
1. α (radial profile exponent)
2. g(M) (constraint strength function)
3. Constraint form f(q, M, r)
4. Speed function c(q,r)
5. Matter coupling law

General radial law: a(r) ∝ [g(M)]^{1/2} r^{-(α/2+1)}

Infinitely many choices for α and g(M) produce infinitely many radial laws.

---

## Kill Test 6: No Natural Propagation Limit

### Test Description
Does finite propagation speed emerge from primitive constraints, or must it be inserted as a constitutive choice?

### How to Test
Analyze whether continuation principle q̇ ∈ K_X implies finite speed without assuming c(q,r).

### Success Condition
Finite propagation speed emerges naturally from K_X structure.

### Failure Condition
Finite propagation speed requires inserting speed function c(q,r) as arbitrary choice.

### Current Status
**CANNOT BE TESTED**

**Reason:** Speed function c(q,r) is currently a free function. No mechanism exists to derive it from primitive constraints. Could be tested with specific K_X structure.

---

## Kill Test 7: No Coherent Dimensional-Reduction Mechanism

### Test Description
Is there a coherent mechanism for dimensional reduction (3 → 2 spatial degrees of freedom) that emerges from primitive constraints?

### How to Test
Attempt to derive rank(G): 3 → 2 from primitive constraints without assuming metric degeneracy.

### Success Condition
Dimensional reduction mechanism emerges naturally from constraint structure.

### Failure Condition
Dimensional reduction requires additional assumption of metric degeneracy or other arbitrary choice.

### Current Status
**PASSED**

**Reason:** Dimensional reduction requires assuming metric degeneracy (e.g., G_ij = diag(1,1,1,0)). No mechanism in primitive constraints forces this. Must be inserted as constitutive choice.

---

## Kill Test 8: X Mathematically Redundant with Existing Theory

### Test Description
Is the X construction mathematically equivalent to an existing framework (constrained dynamical systems, nonlinear field theory, etc.)?

### How to Test
Compare mathematical structure with:
- Constrained dynamical systems
- Nonlinear field theory
- Scalar field theory with potential
- Gauge theories
- Information geometry

### Success Condition
X is mathematically distinct from all established frameworks.

### Failure Condition
X is mathematically equivalent to an existing framework (same mathematical structure).

### Current Status
**INCONCLUSIVE**

**Reason:** Similar to constrained dynamical systems and nonlinear field theory, but physical interpretation differs. Requires deeper analysis to determine if mathematical equivalence exists. Not a definitive kill yet.

---

## Kill Test 9: Matter and Gravity Require Unrelated Mechanisms

### Test Description
Do stable localized configurations (matter) and attractive geometry (gravity) require independent constitutive assumptions?

### How to Test
Attempt to derive both from same primitive constraints:
- Derive stable localized solution from primitive constraints
- Derive attractive radial law from primitive constraints
- Check if both come from same mechanism or require different assumptions

### Success Condition
Both matter and gravity emerge from same microscopic mechanism.

### Failure Condition
Matter requires one set of constitutive assumptions, gravity requires another independent set.

### Current Status
**CANNOT BE TESTED**

**Reason:** Matter stability mechanism not yet derived. Both currently require independent constitutive choices. Cannot determine if single mechanism can explain both.

---

## Kill Test 10: Continuation Principle Does Not Actually Constrain Dynamics

### Test Description
Does the continuation principle "X cannot terminate" actually constrain dynamics, or is it trivially satisfied?

### How to Test
Check whether continuation principle q̇ ∈ K_X:
- Is always satisfied for relevant solutions
- Adds nontrivial constraints beyond those in K_X
- Can be violated by physically reasonable states

### Success Condition
Continuation principle adds nontrivial constraints (restricts dynamics beyond K_X alone).

### Failure Condition
Continuation principle is trivially satisfied (zero velocity always admissible, etc.) or adds no constraint.

### Current Status
**PASSED (for stationary case)**

**Reason:** For stationary solution (q̇ = 0), continuation principle is trivially satisfied (0 ∈ K_X always). Does not constrain dynamics in this case. May become nontrivial for time-dependent solutions.

---

## Kill Test Summary

| Test | Status | Reason |
|------|--------|--------|
| 1. Mathematical inconsistency | PASSED | Mathematically coherent |
| 2. No stable localized solution | FAILED | Solution exists |
| 3. No attractive behavior | FAILED | Attraction emerges |
| 4. Attraction requires Newtonian insertion | PASSED | Requires α=2, g(M)∝M² |
| 5. Infinite constitutive freedom | PASSED | 5+ free parameters |
| 6. No natural propagation limit | CANNOT TEST | Speed function free |
| 7. No dimensional-reduction mechanism | PASSED | Requires metric degeneracy |
| 8. X redundant with existing theory | INCONCLUSIVE | Similar to constrained systems |
| 9. Matter/gravity require unrelated mechanisms | CANNOT TEST | Matter stability not derived |
| 10. Continuation principle trivial | PASSED | Trivially satisfied for stationary |

**Passed:** 6 (tests that FAILED to kill the theory)
**Failed:** 3 (tests that PASSED, i.e., found fatal flaws)
**Inconclusive:** 1
**Cannot test:** 2

---

## Critical Failure Analysis

### Primary Failure: Constitutive Underdetermination

**Kill Test 5 (Infinite Constitutive Freedom)** is the most critical failure.

**Evidence:**
- General radial law: a(r) ∝ [g(M)]^{1/2} r^{-(α/2+1)}
- Both α and g(M) are free
- Infinitely many radial laws possible
- Newtonian 1/r² is one special case among infinitely many

**Implication:** The model cannot predict gravity without additional assumptions. It can reproduce any radial law by choosing appropriate constitutive functions.

### Secondary Failure: Inserted Newtonian Structure

**Kill Test 4 (Attraction Requires Inserted Newtonian Structure)** is the second most critical failure.

**Evidence:**
- Newtonian behavior requires α = 2 and g(M) ∝ M²
- Neither is derived from primitive constraints X1-X4
- Both are constitutive choices

**Implication:** The model does not derive Newtonian gravity; it reproduces it by choosing appropriate constitutive functions.

### Tertiary Failure: Dimensional Reduction

**Kill Test 7 (No Dimensional-Reduction Mechanism)** is a significant issue.

**Evidence:**
- Dimensional reduction requires metric degeneracy
- No mechanism in primitive constraints forces metric degeneracy
- Must be inserted as additional assumption

**Implication:** The distinctive dimensional-reduction claim is not derived from primitive constraints.

---

## Mathematical vs Physical Failure Distinguishing

### Mathematical Failures (Theory Death)

**None found.** The theory is mathematically coherent.

### Physical Failures (Predictive Death)

**Several found:**
- Constitutive underdetermination (Kill Test 5)
- Inserted Newtonian structure (Kill Test 4)
- Inserted dimensional reduction (Kill Test 7)

### Scientific Assessment

**The theory survives mathematical testing but fails predictive testing.**

It is mathematically coherent but empirically empty as a predictive theory in its current form.

---

## Comparison with C2 Failure Mode

### C2 Failure Mode
- Mathematical equivalence to conventional physics (telegrapher ≡ Maxwell-Cattaneo ≡ EIT)
- Free parameters (c, λ, g, S₀)
- No forward predictions
- Conventionally degenerate

### X Failure Mode  
- Mathematical distinction from conventional physics (two-layer structure)
- Free functions (α, g(M), constraint form, speed function, coupling law)
- No forward predictions
- Constitutively underdetermined

### Similarity
Both require constitutive choices to reproduce known physics.
Both have no genuine predictive power in current form.

### Difference
X has a genuinely different mathematical structure (state + admissible transitions vs scalar field), but this structural difference does not translate into predictive advantage.

---

## Scientific Verdict

### Is the Candidate Worth Continuing?

**Current assessment:** NO, in its current form.

**Reason:**
- The distinctive mathematical structure (two-layer with continuation principle) does not translate into predictive advantage
- Constitutive underdetermination is severe (infinitely many radial laws possible)
- Newtonian gravity requires insertion, not derivation
- Dimensional reduction requires insertion, not derivation

### What Would Be Required to Rescue?

**To rescue as predictive theory, would need:**
1. Mechanism to derive α = 2 from primitive constraints
2. Mechanism to derive g(M) ∝ M² from primitive constraints
3. Mechanism to derive metric degeneracy from primitive constraints
4. Mechanism to derive speed function c(q,r) from primitive constraints
5. Mechanism to derive matter stability from primitive constraints

**Alternatively:**
- Accept that radial law is constitutive and test whether other aspects (dimensional reduction, matter stability) provide distinctive predictions

### Research Status

**Status:** FAILS PREDICTIVE TEST

**Classification:** Mathematically coherent but empirically empty as a predictive theory.

**Next action:** Unless mechanisms to derive constitutive choices from primitive constraints can be found, the candidate cannot proceed as a predictive theory.

---

*End of 03_KILL_TESTS.md*
