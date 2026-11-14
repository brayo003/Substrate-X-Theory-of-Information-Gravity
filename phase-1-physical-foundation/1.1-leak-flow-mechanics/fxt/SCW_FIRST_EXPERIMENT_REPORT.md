# Substrate Closure Weave (SCW): First Computational Experiment

## Status

This is an exploratory mathematical prototype, not a physical theory. It defines a deterministic relational rewrite system without using a stochastic process, matrix state, Hamiltonian, or quantum channel as its update rule.

## Primitive

A weave consists of four ports, oriented strands `(source, target, sign)`, and a closure count. The sign is `+1` or `-1`.

The interaction alphabet is `{A, B}`. The current closure parity routes each interaction:

- `A`: add `0 -> 1` if the closure count is even; otherwise add `0 -> 3`.
- `B`: add `1 -> 2` if the closure count is even; otherwise add `1 -> 0`.

When a new strand closes a directed cycle, the shortest return path is selected (ties broken by strand insertion order), all signs on that cycle are inverted, and the closure count increases by one.

This is a stipulated toy rule. It is not derived from Substrate-X principles yet.

## Experiments

### 1. Determinism and state validity

All 511 interaction sequences of lengths 0 through 8 were replayed twice. The resulting complete states matched exactly on every replay. All strand endpoints and orientation signs remained valid.

This establishes only that the implementation follows its own deterministic rules consistently over this finite test set.

### 2. Interaction order matters

From the same initial weave:

- `ABB` ends with closure count 2 and orientation balance -2.
- `BBA` ends with closure count 3 and orientation balance 0.

Both have a path from port 0 to port 3, but their closure structures differ. Thus the order of interactions changes the final internal state and selected structural readouts.

This is a demonstrated property of the stipulated rewrite rule, not yet a physical discovery.

### 3. Same coarse summary, different future

Two initial weaves were selected that have:
- the same strand count,
- the same sorted node-degree summary,
- the same orientation balance,
- the same closure count,
- the same listed structural observation.

Applying the identical sequence `AAAB` produces different final observations:

- Weave 1: closure count 0, orientation balance 7.
- Weave 2: closure count 1, orientation balance 1.

The hidden connectivity affects the response even though the selected coarse summaries initially agree. This is the most useful result of the prototype: a coarse state description can lose structural information needed to predict future evolution.

## What has and has not been achieved

### Achieved
- A fully specified finite rewrite rule.
- An executable reference implementation.
- Deterministic replay tests.
- An explicit order-sensitivity witness.
- An explicit example where two coarse-indistinguishable states respond differently to the same input sequence.

### Not achieved
- No quantum system has been coupled to the weave.
- No observation rule for quantum experiments has been derived.
- No probabilities, Born-rule analogue, interference, entanglement, or Bell-type result has been derived.
- No prediction has been shown to differ from all conventional stochastic or quantum models.
- No claim of mathematical novelty has been established; graph rewriting and relational structures already exist as broad mathematical areas.

## Next decisive step

Do not add more state variables just to make the prototype look richer. First replace the stipulated routing rule with a principled closure/reorganization law derived from explicit Substrate-X commitments. Then define a substrate–system interaction and an observation map from the joint structure to testable outcomes. Only after that can we test whether the primitive has explanatory power beyond an alternative encoding of familiar dynamics.
