# CANDIDATE_KILL_TESTS
## Gate 5 — Adversarial Tests for Each Candidate Primitive

---

### Purpose

Apply the formal kill tests from ASSUMPTION_FIREWALL.md and DECISION_RULES.md to each candidate primitive in CANDIDATE_GENERATION.md. Record which candidates survive and which are killed.

This document is the adversarial firewall between candidate generation and the derivation phase. No candidate proceeds to 06_DERIVATION/ without passing all tests here.

---

## Test Battery (from ASSUMPTION_FIREWALL.md §D)

**Test 1 — Provenance check:** Every input to the primitive's definition must have a non-circular justification.

**Test 2 — Adversarial substitution:** Replace the smooth FLRW state with a maximally pathological alternative. Does the primitive still select the smooth state, or does it also permit the pathological one?

**Test 3 — Name independence:** Does the derivation work with abstract symbols, or does it require the reader to interpret the symbols as "information" to follow the reasoning?

**Test 4 — Competitor universality:** Does the primitive apply outside cosmology? If it is a general principle, it should have non-cosmological consequences.

**Test 5 — Minimality:** Is this the smallest structure that closes R1, or is it larger than necessary?

---

## Section 1: Candidate A (D-constraint) Kill Tests

**Test 1 — Provenance:** What determines which low-dimensional subspace is selected? If the subspace is defined by "the FLRW subspace," the constraint is circular. The constraint must specify the subspace by independent mathematical criteria.
- **Status: UNRESOLVED — requires specification of the subspace**

**Test 2 — Adversarial substitution:** Can a highly inhomogeneous state lie in the selected subspace?
- If the subspace is defined by low Kolmogorov complexity: possibly, since some inhomogeneous states could be algorithmically simple (e.g., a regular fractal)
- **Status: POTENTIAL KILL — needs careful definition to survive**

**Test 3 — Name independence:** Does the argument work without calling the subspace "information space"?
- In principle yes — it is purely about dimensionality of configuration space
- **Status: PASSES**

**Test 4 — Competitor universality:** Does a dimensionality constraint apply elsewhere in physics?
- Yes — renormalization group flows reduce the effective dimension of physical parameter space. This is a genuine analogy.
- **Status: PASSES**

**Overall status for A:** CONDITIONAL — survives tests 3 and 4; fails tests 1 and 2 as currently stated. Needs precise definition of the subspace.

---

## Section 2: Candidate B (Q-bound) Kill Tests

**Test 1 — Provenance:** What probability distribution is Fisher information computed over?
- If over "possible cosmological initial states," this requires a measure — which is part of the problem (R2)
- If over "measurement outcomes given a fixed state," it is standard quantum Fisher information — well-defined but applies to a specific measurement context
- **Status: UNRESOLVED — depends on which interpretation**

**Test 2 — Adversarial substitution:** Does a wildly inhomogeneous state have high Fisher information?
- For a fixed measurement protocol, an inhomogeneous state could in principle have lower Fisher information than a smooth state (depending on what is being measured)
- **Status: UNCLEAR — requires definition of the measurement context**

**Test 3 — Name independence:** Fisher information is a mathematical object independent of "information" interpretation. The bound is purely geometric.
- **Status: PASSES**

**Test 4 — Competitor universality:** Fisher information bounds appear in quantum metrology, parameter estimation, quantum thermodynamics.
- **Status: PASSES**

**Overall status for B:** CONDITIONAL — mathematically rigorous but the application to cosmological initial states requires specifying the probability distribution and measurement context, neither of which is obvious.

---

## Section 3: Candidate C (R-condition) Kill Tests

**Test 1 — Provenance:** What is the quantum gravity wave function? No established theory exists.
- The R-condition is underspecified until a theory of quantum gravity is specified
- **Status: FAILS (in current form) — underspecified**

**Test 2 — Adversarial substitution:** The no-boundary proposal (the closest realization) is claimed by Penrose to predict high-entropy initial states. If the R-condition inherits this problem, it is killed.
- **Status: FAILS if derived from Hartle-Hawking; requires independent formulation**

**Overall status for C:** KILLED in current form — requires a theory of quantum gravity that is not the no-boundary proposal and not yet specified.

---

## Section 4: Candidate D (C-constraint, channel capacity) Kill Tests

**Test 1 — Provenance:** Channel capacity requires a quantum channel. What defines the gravitational channel in the early universe?
- For the Newtonian or post-Newtonian regime this is relatively well-defined
- For the early universe (near Planck scale) this requires quantum gravity
- **Status: PARTIALLY RESOLVED for post-inflation; UNRESOLVED for pre-inflation**

**Test 2 — Adversarial substitution:** Does a high-Weyl spacetime violate the channel capacity constraint?
- This requires computing the gravitational channel capacity as a function of spacetime geometry — not done
- **Status: UNRESOLVED**

**Test 3 — Name independence:** Channel capacity is a purely information-theoretic concept with precise mathematical definition.
- **Status: PASSES**

**Test 4 — Competitor universality:** Channel capacity is a central concept in quantum information theory. It applies to all physical channels.
- **Status: PASSES**

**Overall status for D:** SPECULATIVE but not killed — the connection between channel capacity and geometric complexity is not established but is in principle derivable. Active candidate for further development.

---

## Section 5: Candidate E (B-condition, covariant entropy bound) Kill Tests

**Test 1 — Provenance:** The Bousso bound is an established result, derivable from black hole thermodynamics and the generalized second law.
- **Status: PASSES**

**Test 2 — Adversarial substitution:** Does a wildly inhomogeneous early-universe state violate the Bousso bound?
- The Bousso bound limits entropy on null surfaces. A highly inhomogeneous state can concentrate entropy differently, but the total bound is geometric (area-dependent).
- In the very early universe, the horizon area is small — this constrains the total entropy on null surfaces but is not a selection of specific geometries.
- **Status: PARTIAL — the bound constrains total entropy but does not select smooth over inhomogeneous geometry**

**Test 2 further:** The Bousso bound, applied to the initial state, would rule out states with entropy exceeding A/4G on any null surface. A highly inhomogeneous state does NOT necessarily violate this — it just distributes entropy differently.
- **Status: FAILS as a selection principle — the bound permits inhomogeneous states**

**Overall status for E:** KILLED as a selection principle — the Bousso bound is a necessary condition but not sufficient to select smooth initial states. It can be used as a constraint within a larger argument but cannot stand alone.

---

## Section 6: Summary of Kill Test Results

| Candidate | Kill status | Reason |
|---|---|---|
| A (D-constraint) | CONDITIONAL | Fails provenance and adversarial test as stated; survives with precise subspace definition |
| B (Q-bound) | CONDITIONAL | Passes mathematical tests; application to cosmology requires specifying probability distribution |
| C (R-condition) | KILLED | Underspecified; degenerates to no-boundary problem |
| D (C-constraint) | ACTIVE CANDIDATE | Speculative but not killed; requires deriving channel capacity in geometric terms |
| E (B-condition) | KILLED as standalone | Bousso bound permits inhomogeneous states; can serve as constraint within larger argument |

---

## Section 7: Path Forward

Surviving active candidates: **A (conditional), B (conditional), D (active)**

These feed into SURVIVING_PRIMITIVE.md after further development. The next step is:
- For A: specify which mathematical criterion defines the low-dimensional subspace without encoding smoothness
- For B: specify the probability distribution / measurement context for Fisher information in the cosmological setting
- For D: derive channel capacity as a function of spacetime geometry in the pre-inflationary regime

---

*Document status: WORKING — kill tests applied; candidates A, B, D survive conditionally*
