# ARROW_OF_TIME
## Gate 6 — Does the Primitive Generate Temporal Asymmetry?

---

### Status Notice

**TEMPLATE — Gate 5 not yet passed.**

This file records the research hypothesis and what would need to be derived to establish a connection between the primitive and the thermodynamic arrow of time.

---

## Section 1: The Research Hypothesis

From CHARTER.md §8:

> The hypothesis is that the same mechanism that explains the initial-state problem necessarily generates temporal asymmetry.

This is a hypothesis, not an assumption. It is tested here, after a primitive is derived.

**Possible outcomes:**
1. **True:** The primitive selects an initial state that is low-entropy AND generates a direction for entropy increase via its dynamics. One mechanism does both.
2. **False — independent:** The primitive explains the initial state but does not by itself generate time asymmetry. The arrow of time requires additional structure (the Past Hypothesis is still needed).
3. **False — impossible:** The primitive fails to explain the initial state (program killed at Gate 5 or 6).

Outcome 2 is scientifically valid — it just means the two problems require separate treatment.

---

## Section 2: What Would Confirm the Hypothesis

For the primitive P to generate temporal asymmetry, it must:

1. **Select a low-entropy initial state** (this is Gate 6's main task)

2. **Generate a time-asymmetric evolution rule** — the primitive must not be time-symmetric. If P and its derived dynamics are time-symmetric, entropy increase is not guaranteed; the universe could evolve in either time direction symmetrically.

3. **The time asymmetry must not be manually inserted.** If the primitive is symmetric and the evolution equations are time-symmetric, the arrow of time is not explained — only the low initial entropy is.

**The key question:** Is the primitive time-symmetric or time-asymmetric?

- If time-asymmetric: it introduces a preferred direction of time. This is a strong claim that requires justification (why does the primitive break time-symmetry?).
- If time-symmetric: the low-entropy initial state is selected, but the arrow of time requires the Past Hypothesis as usual. The primitive does not explain the arrow — only the initial state.

Either result is valuable. The program does not require the primitive to explain both.

---

## Section 3: The Distinction Between the Two Problems

| | Initial-State Problem | Arrow-of-Time Problem |
|---|---|---|
| What is explained | Why the early universe was in a special state | Why macroscopic processes are irreversible |
| Standard account | Unknown (this is the target) | Past Hypothesis (assumes the above) |
| Can be solved by a time-symmetric primitive? | Yes | No |
| Can be solved by a time-asymmetric primitive? | Yes | Yes (potentially) |

A time-symmetric primitive that selects a low-entropy initial state is already a substantial result. It would explain the initial state but still require the Past Hypothesis as an additional assumption for the arrow. This is acceptable.

---

## Section 4: Connection to the Second Research Branch

The second branch (gravity as information channel) concerns the information-processing properties of gravity. If gravity has a preferred direction for information flow (e.g., information can be extracted from but not injected into spacetime in certain regimes), this might be a physical realization of time asymmetry.

**This connection must not be assumed.** If the derivation of the primitive produces a time-asymmetric evolution rule AND the channel capacity characterization of gravity produces a directionality, AND these can be shown to be the same mathematical structure — then the two branches have connected through derivation.

That would be a significant result. But the connection must come from the mathematics, not from declaring it in advance.

---

## Section 5: Template for Arrow-of-Time Derivation

When a primitive P is cleared and its dynamics derived:

**Step 1 — Check time-symmetry of P:**
```
Is P[h_ij, K_ij] = P[h_ij, -K_ij]?
(Reversing time is equivalent to flipping the sign of extrinsic curvature)
```
If yes: P is time-symmetric. The arrow-of-time hypothesis (this program) is false for this primitive.
If no: P is time-asymmetric. Proceed to Step 2.

**Step 2 — Derive the entropy gradient:**
```
For initial data in Γ_P, show that dS/dt > 0 under the derived evolution,
where S is a specified entropy functional.
```

**Step 3 — Verify universality:**
```
Show that dS/dt > 0 holds for all initial data in Γ_P,
not just for specific fine-tuned trajectories.
```

**Step 4 — Connect to thermodynamic arrow:**
```
Show that the abstract entropy S is related to the thermodynamic entropy
of macroscopic matter distributions in the universe.
```

---

*Document status: TEMPLATE — arrow-of-time analysis deferred until primitive is cleared*
