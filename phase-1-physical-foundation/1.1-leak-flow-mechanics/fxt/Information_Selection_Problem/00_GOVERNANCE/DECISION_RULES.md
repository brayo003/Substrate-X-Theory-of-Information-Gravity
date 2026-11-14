# DECISION_RULES
## Formal Criteria for Gate Decisions

---

### Overview

Every gate in this research program has a binary decision: PASS or FAIL. Gates are sequential. A FAIL at any gate terminates or redirects the program. No gate may be bypassed.

Decisions are logged at the bottom of this document as they occur.

---

## GATE 1 — Empirical Target Establishment

**Question:** Have we established with precision what requires explanation?

**PASS criteria (all must be met):**

1. Each of the six early-universe features listed in CHARTER §2 has been assigned one of three status labels:
   - `OBSERVED`: Directly measured, instrument-independent
   - `THEORETICALLY_INFERRED`: Derived from observed data via a theory (label which theory)
   - `DISPUTED`: Contested in the literature (cite the dispute)

2. For each `THEORETICALLY_INFERRED` item: the inference chain is explicit (data → theory → claim), and the sensitivity to the theory's assumptions has been assessed.

3. For each `DISPUTED` item: the specific nature of the dispute is documented, and the dispute's resolution status is noted.

4. The Weyl curvature formulation of gravitational entropy has been examined as a hypothesis, not a fact. At minimum two published criticisms and/or counterexamples are documented.

5. The scale-factor entropy argument (as an alternative to Weyl-based entropy) is documented and assessed.

**FAIL criteria (any causes failure):**
- Treating theoretical inference as observation
- Treating Penrose's formulation as established fact
- Conflating the six features as equivalent
- Using "low entropy early universe" as a single undifferentiated premise

---

## GATE 2 — Conventional Explanation Audit

**Question:** What does standard physics already explain about the early cosmological state?

**PASS criteria (all must be met):**

1. Each of the following frameworks has been assessed against each of the six target features:

   | Framework | Assessment Required |
   |---|---|
   | ΛCDM | What it predicts, what it assumes |
   | General Relativity (alone) | What geometric structure it provides |
   | Inflation (various models) | What it explains vs. assumes |
   | Reheating | What it explains of thermalization |
   | Baryogenesis | What it explains of matter content |
   | QFT in curved spacetime | What it explains of perturbations |
   | Quantum cosmology (WdW, etc.) | What it proposes for boundary conditions |
   | Gravitational perturbation theory | What it explains of structure growth |
   | Statistical mechanics of gravity | What applies and what breaks down |
   | Known gravitational entropy proposals | What each proposes and what is contested |
   | Boundary condition approaches (Hartle-Hawking, etc.) | What each claims and what is unresolved |
   | Inflationary attractor arguments | Whether they genuinely explain or merely reframe |
   | Alternative initial-condition mechanisms | Pre-big-bang, bouncing cosmologies, etc. |

2. The July 2026 information-saturation paper has been explicitly analyzed:
   - What it claims to derive
   - What it actually assumes
   - Whether its constraint genuinely selects FLRW independently or assumes it
   - What it leaves unresolved (the authors' own admission: quantitative predictions deferred)

3. A matrix has been produced: `[framework] × [target feature] = [explained / partially explained / not explained / reframed but not explained]`

**FAIL criteria:**
- Missing any framework from the list
- Treating the July 2026 paper as successful without explicit adversarial examination
- Treating "reframed" as equivalent to "explained"

---

## GATE 3 — Residual Identification

**Question:** Does a genuine unexplained residual exist after all of Gate 2 is granted?

**Binary Output: RESIDUAL EXISTS or NO RESIDUAL**

**RESIDUAL EXISTS criteria (all must be met):**

1. There exists at least one feature from Gate 1 that cannot be explained by any combination of Gate 2 frameworks without importing the feature itself as an assumption.

2. This residual is formally characterized: it is stated as a precise mathematical or physical claim that has no known derivation from established physics.

3. The residual is not merely "philosophically unsatisfying" — it must represent an actual gap in the predictive or explanatory power of existing physics.

4. The residual survives an adversarial attempt to close it using known physics (the adversarial attempt must be documented).

**NO RESIDUAL criteria (any one suffices):**

1. All six features are explained (derived from independent inputs) by some combination of existing frameworks.

2. The apparent gap is shown to be a question of interpretation, not of physical content.

3. The apparent gap is shown to be a consequence of an inconsistent framing of the question.

**If NO RESIDUAL:** The cosmological branch is **terminated**. This is recorded as a positive scientific result. The second branch (quantum-information/gravity channel) may continue independently.

---

## GATE 4 — Residual Survives Audited Closure Set

**Question:** Does the residual R survive the complete existing-physics and existing-information-theory closure attempts audited so far?

**What Gate 4 establishes (no more, no less):**

> Existing explanations examined so far do not close the formally defined residual without an additional explanatory ingredient.

**What Gate 4 does NOT establish:**

> New ontology is structurally required.

That stronger claim cannot be made until the closure-exhaustion audit is complete. Treating an unresolved problem as evidence for a preferred ontology is the exact failure mode the firewall was designed to prevent.

**The correct logical sequence:**

```
R ≡ unexplained residual
    ↓
Is R ⊆ E_existing?  →  YES → kill project (existing physics closes it)
    ↓ NO
Is R ⊆ E_information?  →  YES → study that mechanism; do NOT invent a substrate
    ↓ NO
R ⊄ E_existing ∪ E_information
    ↓
ONTOLOGY JUSTIFICATION PENDING
    ↓
(Gate 5 only) → derive minimum missing structure as P_new
```

**PASS criteria (all must be met):**

1. Each closure attempt in 04_RESIDUAL_PROBLEM/NECESSITY_AUDIT.md has been executed and the result recorded.

2. For each candidate closure, the explicit failure mode is documented (not merely "we haven't found a way").

3. The July 2026 information-saturation paper has been subjected to the full adversarial examination in 03_INFORMATION_LITERATURE/INFORMATION_SATURATION.md before Gate 4 is declared passed.

4. The Hartle-Hawking no-boundary proposal status is assessed and recorded.

**FAIL criteria (any causes failure):**
- A known closure successfully resolves R
- The "residual" is shown to be a framing artifact, not a physical gap
- The July 2026 paper is found to close R without assumption laundering

**Status after Gate 4 PASS:**

```
ONTOLOGY JUSTIFICATION PENDING
```

Not: "new ontology required." Gate 5 determines whether an additional primitive is necessary, derivable, and minimal. Gate 4 only certifies that the residual has not yet been closed.

---

## GATE 5 — Primitive Derivation

**Question:** Can the minimum required structure be derived, not postulated?

**PASS criteria (all must be met):**

1. The primitive is derived from permitted inputs (see ASSUMPTION_FIREWALL §E).

2. The derivation does not assume any prohibited structure (see ASSUMPTION_FIREWALL §A–C, ONTOLOGY_PROHIBITION §A–C).

3. The adversarial substitution test passes (ASSUMPTION_FIREWALL §D, Test 2).

4. The primitive receives a provisional name derived from its mathematical properties.

**FAIL criteria:**
- The primitive must be postulated rather than derived
- The primitive fails the adversarial substitution test
- The primitive's derivation imports any assumption from ASSUMPTION_FIREWALL

---

## GATE 6 — Prediction

**Question:** Does the derived primitive generate observational predictions not already reproduced by existing physics?

**PASS criteria (all must be met):**

1. At least one quantitative prediction is derived that is not a consequence of GR + standard cosmological model alone.

2. The prediction is in principle measurable.

3. The prediction has not already been measured with a confirming result (otherwise it is postdiction, not prediction).

**FAIL criteria:**
- All predictions are reproduced by existing physics
- Predictions are qualitative only and not falsifiable
- Predictions are retrospective fits to known data

---

## GATE 7 — Discrimination

**Question:** Can the prediction be used to distinguish this framework from all known alternatives?

**Pass criteria:**
1. A null model set is defined that covers all plausible alternative explanations.
2. A statistical discrimination criterion exists with specified power.
3. A measurement exists or can be designed that achieves the required power.

**Fail criteria:**
- No existing or foreseeable measurement can distinguish this from null models
- The prediction is identical to a prediction of an existing theory

---

## Decision Log

*Decisions are recorded here as they are made.*

| Date | Gate | Decision | Summary | Supporting File |
|---|---|---|---|---|
| (none yet) | — | — | Program initialized. No gate decisions made. | CHARTER.md |

---

*Document status: ACTIVE DECISION REGISTER*
*All gate decisions are logged here with citations to supporting analysis.*
