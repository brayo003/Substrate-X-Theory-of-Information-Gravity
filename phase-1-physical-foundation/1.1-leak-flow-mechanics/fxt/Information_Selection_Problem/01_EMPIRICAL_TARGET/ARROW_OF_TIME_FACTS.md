# ARROW_OF_TIME_FACTS
## Gate 1 — The Thermodynamic Arrow of Time

---

### Purpose

This document registers what is known about the thermodynamic arrow of time, separates established facts from theoretical inferences, and documents the relationship (and non-equivalence) between the arrow-of-time problem and the cosmological initial-state problem.

The arrow of time is the **second** research target of this program — downstream of the initial-state problem, not identical to it.

---

## Section 1: The Observed Arrow of Time

### 1.1 What Is Observed
The following macroscopic time asymmetries are robustly observed:

- Heat flows from hot to cold bodies (never spontaneously the reverse)
- Mechanical processes with friction are irreversible
- Biological organisms age
- Information erasure is irreversible (Landauer's principle — experimentally tested)
- Chemical reactions proceed to equilibrium, not away from it (without external driving)
- Electromagnetic radiation propagates outward from sources (retarded, not advanced solutions)
- The universe is expanding, not contracting (currently)

**Status: OBSERVED** — These are macroscopic facts independent of any cosmological model.

### 1.2 What Is Inferred
The **explanation** of why macroscopic time asymmetry exists, given that microscopic physics is (nearly) time-symmetric, is theoretically inferred, not observed.

The standard inference:
```
Microscopic laws are time-symmetric (T-symmetric or CPT-symmetric)
    + Observed macroscopic irreversibility
    → [Statistical mechanics argument]
    → The initial state of the universe was low-entropy
    → Entropy increases because the universe evolved away from its initial state
```

The conclusion (low-entropy initial state) is inferred, not observed. The argument is valid given its premises, but the premises include the low initial entropy claim which is itself the target of explanation.

---

## Section 2: The Standard Account (Boltzmann / Past Hypothesis)

### 2.1 The Argument
David Albert and others have formalized the "Past Hypothesis":
- The fundamental laws of physics are time-symmetric
- The macroscopic arrow of time is explained by a low-entropy initial condition ("the Past Hypothesis")
- Given the Past Hypothesis, statistical mechanics explains entropy increase

### 2.2 What the Past Hypothesis Does and Doesn't Do
**Does:** Explain why entropy increases given that it started low.
**Does not:** Explain why the initial entropy was low in the first place.

The Past Hypothesis is an assumption, not a derivation. Explaining the Past Hypothesis is exactly the cosmological initial-state problem.

### 2.3 Status of the Standard Account
`ESTABLISHED AS A FRAMEWORK` — The Past Hypothesis + statistical mechanics is the standard account. It successfully explains entropy increase given the assumption. The assumption itself is unresolved.

---

## Section 3: Approaches Not Based on the Past Hypothesis

Several research programs attempt to explain or dissolve the arrow-of-time problem without relying on a special initial condition:

### 3.1 Barbour, Koslowski, Mercati (2014) — Shape Dynamics Arrow
In a shape-dynamics formulation, time asymmetry emerges from the structure of the complexity functional on shape space. No special initial condition is required; the arrow emerges from the dynamics itself in both time directions from a central minimum-complexity state.

**Status:** Technically interesting but contested. The framework requires shape dynamics as the correct formulation of gravity, which is not established.

### 3.2 Carroll-Chen (2004) — Eternal Inflation / Baby Universes
The universe is embedded in an eternal, larger structure. The arrow of time emerges locally from the branching of baby universes. No global initial condition is imposed.

**Status:** Speculative. Requires an eternal background structure with no independent support.

### 3.3 Rovelli (various) — Thermal Time
Time itself is a thermodynamic concept — the direction of time is the direction of increasing entropy, which is defined by the reference state. There is no "objective" arrow of time; it is always relative to a statistical state.

**Status:** Conceptually interesting but challenges the question rather than answering it. Does not explain why the reference state has the structure it has.

### 3.4 Penrose — CCC (Conformal Cyclic Cosmology)
The universe undergoes endless aeons. The end of each aeon (conformally rescaled) is the beginning of the next. The arrow of time in each aeon is explained by the low-entropy (conformally smooth) state at the aeon's beginning.

**Status:** Speculative cosmological model. Makes some observational predictions (concentric rings in CMB) that are disputed.

---

## Section 4: The Relationship Between the Two Problems

### 4.1 The Arrow of Time vs. The Initial-State Problem

| | Initial-State Problem | Arrow-of-Time Problem |
|---|---|---|
| Core question | Why was the early universe in a special state? | Why does time have a preferred direction? |
| Standard answer | Unknown | Past Hypothesis (which assumes the above) |
| Relation | Upstream | Downstream |
| Can be solved independently? | In principle yes | Only if Past Hypothesis is abandoned |

### 4.2 The Research Hypothesis (to be tested, not assumed)
The program's hypothesis is:

> The same mechanism that explains the initial-state problem necessarily generates temporal asymmetry.

This is a **hypothesis**, not an assumption. The program tests it only after Gate 3 establishes a residual and Gate 5 produces a primitive. The hypothesis could be:
- **True:** The same mechanism does both. Significant.
- **False — independent:** The mechanism explains initial states but not the arrow. The program continues but the arrow is a separate problem.
- **False — impossible:** The mechanism cannot explain the initial state either (program terminated at Gate 3).

---

## Section 5: What the Arrow-of-Time Problem Requires from a Solution

If the arrow-of-time problem is to be addressed by the same mechanism as the initial-state problem, that mechanism must:

1. Distinguish past from future in a way that is not already present in the microscopic laws
2. Not appeal to the arrow-of-time as a premise (circular)
3. Be consistent with the observed symmetry of microscopic physics (T-symmetry is broken only weakly by CP violation; the thermodynamic arrow is much stronger)
4. Explain why entropy increase is *universal* (all subsystems show it), not just statistical (why doesn't the whole universe fluctuate back to low entropy?)

These are demanding constraints. They are registered here as requirements for any proposed mechanism that claims to address both problems.

---

## Section 6: Known Failure Modes for Arrow-of-Time Arguments

From the predecessor project's catalog and literature:

| Failure Mode | Description |
|---|---|
| Time-asymmetry from time-symmetric dynamics | Any argument purporting to derive an irreversible arrow from perfectly time-symmetric laws, without invoking an initial condition or a coarse-graining convention, is suspicious |
| Coarse-graining dependence | The direction of entropy increase depends on the coarse-graining. Different coarse-grainings can give different arrows or no arrow. A satisfactory explanation should not depend on an arbitrary coarse-graining |
| Invoking decoherence without a past hypothesis | Decoherence explains why quantum superpositions are practically unobservable, not why there is a thermodynamic arrow. Decoherence is symmetric in time without a special initial condition |
| Confusing epistemic and ontic asymmetry | We remember the past and not the future. This epistemic asymmetry does not imply an ontic asymmetry in the laws |

---

*Document status: WORKING — Gate 1 analysis complete for arrow-of-time component*
*Arrow-of-time extension deferred to 06_DERIVATION/ARROW_OF_TIME.md pending Gate 3 result*
