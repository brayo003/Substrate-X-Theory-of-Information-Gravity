# CHARTER
## Information_Selection_Problem Research Program

---

### 1. Identity and Scope

This workspace is an **adversarial research program**, not a theory development program.

Its single initial mission is:

> Perform an adversarial literature-and-theory audit of the cosmological initial-state problem and determine whether a genuine unexplained residual exists after existing physics and existing proposed information-theoretic explanations are accounted for.

The program exists inside `fxt/`, which serves as the **adversarial knowledge base**: the complete record of C2 construction, C2 failure analysis, Giga/TLS escape attempts, conventional-null analyses, mathematical stress tests, substrate candidate searches, experimental discrimination work, previous assumptions and failure modes, and the new external literature target (July 2026 information-saturation paper).

The `Information_Selection_Problem/` directory is the **blank ontology workspace**. It inherits nothing from `fxt/` except:
- Constraints demonstrated to be real
- Failure modes demonstrated to be fatal
- Mathematical tools that are valid independently of the failed theory
- Empirical knowledge that is observation-grounded

It does **not** inherit:
- The C2 ontology
- The substrate concept
- Any information-field or information-flux vocabulary
- Any prior theoretical framework, however reformulated

---

### 2. The Research Target

The first target is stated narrowly and precisely:

**Derive the observed specialness of the early cosmological state.**

This is not equivalent to "explain the arrow of time." That extension is a downstream research hypothesis, not an assumed equivalence.

The early cosmological state exhibits, at minimum, the following empirically or theoretically established features (each treated as an independent datum until proven otherwise):

1. Extremely smooth large-scale geometry
2. Small primordial anisotropies (CMB ~10⁻⁵ level)
3. Thermalized matter/radiation at recombination
4. Suppressed free gravitational degrees of freedom in the early universe
5. Subsequent growth of gravitational structure
6. Macroscopic entropy increase from early to late times

**These are not declared equivalent.** The question of which feature(s) carry the dominant relevant low-entropy content is itself contested in the literature. No shortcut equivalences are permitted.

---

### 3. The Fundamental Asymmetry Between Branches

The parent tree (`fxt/`) and this workspace have an asymmetric relationship:

| What passes from `fxt/` to ISP | What does NOT pass |
|---|---|
| Demonstrated failure modes | C2 ontology |
| Valid mathematical tools | Substrate concept |
| Empirical constraints | Information-field vocabulary |
| Experimental negative results | Any prior theoretical framework |
| Lessons about assumption laundering | Penrose's formulation (treated as a hypothesis, not ground truth) |

The old tree is **extremely valuable** precisely because it contains a catalog of demonstrated failure modes. The purpose of inheriting those failures is prevention, not continuation.

---

### 4. The Research Question (Formal Statement)

Is there an information-theoretic constraint, derived **independently** of FLRW symmetry, homogeneity, isotropy, low Weyl curvature, or a prescribed cosmological boundary condition, that dynamically or structurally restricts the physically realizable early-universe state space to a class whose macroscopic evolution reproduces the observed cosmological arrow of time?

This contains several **independent gates** (see DECISION_RULES.md).

---

### 5. Mission Sequence

The program proceeds in strict gate order:

```
GATE 1: Empirical target — establish what is actually observed vs. inferred
         ↓
GATE 2: Conventional explanation audit — what does existing physics already explain?
         ↓
GATE 3: Residual audit — what genuinely remains unexplained?
         ↓
BINARY DECISION:
  RESIDUAL EXISTS → GATE 4: Ontology necessity proof
  NO RESIDUAL → TERMINATE (cosmological branch killed)
         ↓ (if RESIDUAL EXISTS)
GATE 4: Minimum primitive — what is the smallest structure that closes the gap?
         ↓
GATE 5: Derivation — derive dynamics and predictions from the primitive
         ↓
GATE 6: Discrimination — identify predictions not reproduced by any existing theory
         ↓
GATE 7: Verdict — SURVIVAL or KILL
```

**The program must be able to kill itself before inventing a substrate.**

A verdict of NO RESIDUAL is scientifically correct. It is not a failure. It is the most important possible output of Gate 3.

---

### 6. Prohibited Default Behavior

The agent operating in this workspace is **prohibited** from the following inference chain:

```
interesting phenomenon
    ↓
information sounds relevant
    ↓
invent information primitive
    ↓
derive desired behavior
    ↓
declare mechanism
```

The only permitted inference chain is:

```
real unresolved discrepancy
    ↓
exhaust existing explanations
    ↓
formal residual
    ↓
prove existing ontology insufficient
    ↓
derive minimal missing structure
    ↓
derive dynamics
    ↓
derive prediction
    ↓
attack prediction
```

---

### 7. The External Threat

A paper published July 2026 explicitly proposes an information-saturation interface and claims that, within GR, its constraint selects FLRW geometries and therefore suppresses Weyl curvature. The authors describe it as a structural selection principle, not a fully specified dynamical theory, and leave quantitative cosmological predictions for future work.

This paper is **not** an obstacle. It is a **raised bar**:

- We cannot merely reproduce information → FLRW.
- Any surviving primitive must produce: primitive → state-space restriction → specific cosmological dynamics → observable consequence.
- The observable consequence should ideally fall outside: GR + standard cosmological model.

The July 2026 paper is also a **primary attack target** for the conventional explanation audit. It must be explicitly confronted, not ignored.

---

### 8. The Second Branch (Independent)

A second potential research target exists independently:

> What information-processing capability does gravity physically possess?

This branch (quantum-information/gravity channel problem) is **not merged** with the cosmological branch. They remain independent until a mathematical relation emerges from derivation. Merging them before that point would repeat the C2 error of choosing two phenomena and declaring they must share a hidden substrate.

---

### 9. Governance Documents

| File | Purpose |
|---|---|
| CHARTER.md | This document. Defines scope, mission, and prohibited behaviors. |
| ASSUMPTION_FIREWALL.md | Explicit list of assumptions that must not enter the derivation under any name. |
| ONTOLOGY_PROHIBITION.md | Names and concepts prohibited from the workspace until earned by derivation. |
| DECISION_RULES.md | Formal criteria for each gate decision. |

---

*Document status: ACTIVE GOVERNANCE*
*This document governs all work in `Information_Selection_Problem/` until explicitly superseded.*
