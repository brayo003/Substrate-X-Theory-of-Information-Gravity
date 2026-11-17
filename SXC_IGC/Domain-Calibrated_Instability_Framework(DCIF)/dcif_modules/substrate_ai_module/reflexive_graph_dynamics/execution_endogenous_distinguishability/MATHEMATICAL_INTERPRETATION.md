# MATHEMATICAL_INTERPRETATION

This document answers the five formal questions in the directive and compares
the observed behaviour with standard partition-refinement, bisimulation and
graph-dynamics machinery.  No new mathematics is claimed.

## 0. Notation

- `Ω` finite state set (`|Ω| = 12`), `R_t ⊆ Ω × Ω`, `P_t` a partition of `Ω`.
- `a ~_P b` means `a` and `b` are in the same block.
- Gate: `G(R,P) = {(a,b) ∈ R : ¬(a ~_P b)}`.
- Gate successors: `S_g(z,R,P) = {b : (z,b) ∈ R, ¬(z ~_P b)}`.
- `Split(P, Q)` = one Moore round: split each `P`-block by the set of
  `Q`-blocks of its successors.
- `refine_once(R,P) = Split(P, R)`.

## 1. Is the partition update ordinary Moore / strong-bisimulation refinement?

**For Model B: yes.**  `P_{t+1} = Split(P_t, R_t)` is exactly one round of
Moore refinement (the partition-refinement step used to compute the coarsest
bisimulation) on the ambient relation `R_t`.  With `R` fixed, repeated rounds
compute the coarsest stable refinement of the initial partition (the
bisimulation quotient when the initial partition is trivial).

**For Models C, D and CR: not exactly.**  They use

```
P_{t+1} = Split(P_t, G(R_t, P_t)).
```

This is a Moore round on the *gated* relation, i.e. on `R_t` with all
intra-block edges deleted.  It is a refinement operator (it only splits
blocks), but it is not the standard refinement operator of the ambient
transition system, because the relation it reads changes with `P_t`.

Consequences:

1. It is **not** strong-bisimulation refinement of `R_t`.  Intra-block
   transitions are invisible to the signature.  This is the same idea as
   partition refinement with internal/hidden moves made invisible, and it can
   be strictly coarser than Moore refinement on `R_t`.  The experiment
   measures exactly this: C's final partition differs from B's in 10/100
   seeds and is 0.10 blocks coarser on average (C 11.78 vs B 11.88 blocks).
2. Its fixed points are **gate-stable** partitions: no block splits when
   successors are classified only by blocks outside the block itself.  This is
   not, in general, the coarsest bisimulation of `R_t`.
3. In this configuration the difference is small because the partition
   becomes (nearly) discrete within 2–3 rounds: once every block is a
   singleton, `G(R,P) = R \ {(a,a)}` and refinement is vacuous.  D reaches a
   12-block partition in 100/100 seeds; C in 82/100, B in 90/100.

So the answer is: **ordinary Moore refinement only in Model B; a
partition-dependent "gate-relative" refinement in the coupled models, which is
a known composition but not the standard bisimulation operator, and whose
distinction from Moore refinement is measurable but structurally negligible
here.**

## 2. Is the transition gate a fixed function of the current partition and traversal history?

The gate is a **fixed function of `(R_t, P_t)` only**:

```
G_t = {(a,b) ∈ R_t : ¬(a ~_{P_t} b)}.
```

It contains no explicit traversal-history term.  History enters only through
the stored graph `R_t`, which contains edges created at earlier steps, and
through `P_t`, which is a function of earlier relations.  The archived
redundancy argument is correct and was re-verified by test `T00`: every created
edge is cross-block at creation (`C_t` excludes the current block), and
partitions only refine, so a created edge remains cross-block forever.
Therefore

```
G(P_t, H_t) = G(P_t, ∅) = G(R_t, P_t)
```

for every run.  Traversal history adds nothing to the gate beyond its effect
on `R_t`.

This also means the gate does **not** invent, learn or modify its own rule.
It is a fixed two-line predicate evaluated on the current graph and partition.

## 3. Can the complete model be represented as an ordinary transition system over an enlarged state?

**Yes, directly.**  Take

```
X_t = (z_t, P_t, R_t, α_t)
```

where `α_t` assigns each dynamic edge its creation time (or bounded age).  The
update is

```
S_t      = S_g(z_t, R_t, P_t)
z_{t+1}  = Select(u_t, S_t)                       (stall if S_t = ∅)
P_{t+1}  = Split(P_t, G(R_t, P_t))
C_t      = Create(z_t, R_t, P_{t+1})              (D; CR additionally uses v_t)
D_t      = Remove(R_t, α_t, z_t, z_{t+1})
R_{t+1}  = (R_t ∪ C_t) \ D_t
α_{t+1}  = updated ages
```

with `u_t` the pre-drawn movement uniform and `v_t` the CR control stream.
`X_t` ranges over a finite set (finitely many graphs, partitions, ages and
nodes).  Hence the model is an ordinary finite-state randomised transition
system with exogenous inputs.  `run_full` already records the augmented key
`(z, P.signature, R.signature, ages)` and the recurrence diagnostics; test
`T15` checks it.

## 4. Is the observed effect simply a consequence of that enlarged state?

**Yes.**  Every measured quantity — stall counts, distinct states, traversals,
partition size, reachability, degree distribution — is a function of the
trajectory `X_0, X_1, …`.  The 2×2 interaction is a property of the transition
map `F`, not of a new state variable or a new interaction term.  No hidden
variable, field, memory or collective property is needed to reproduce any of
the numbers.  In particular:

- The stall interaction follows from the identity
  `S_g(z,R,P) = ∅ ⇔ R.successors(z) ⊆ [z]_P`
  and from the fact that refinement shrinks `[z]_P`.  G has a frozen coarse
  `P`, so its trap set is large (55/100 absorbing traps); C refines `P`, so its
  trap set shrinks to self/same-block successors (12/100 absorbing traps).
- The D-vs-CR traversal difference follows from the source distribution of
  created edges: D always creates from `z_t`, CR scatters over the pool.
- The degree/clustering difference follows from the same source concentration:
  a source always equal to the current node produces a heavy-tailed out-degree
  profile, a uniform global sampler does not.

## 5. Is anything left unexplained by the existing formalism?

No unexplained invariant or dynamical property was found.  The experiment
does, however, establish several precise structural facts that are worth
stating because they bound the claim:

**(i) Gate monotonicity under refinement (fixed `R`).**
If `P` is finer than `Q`, then `G(R,P) ⊇ G(R,Q)`.  Along any run of C/G/H
(where `R` is fixed) the gate therefore grows monotonically.  This is the
mechanism of the measured interaction, and it predicts its sign: refinement
can only release stalls, never create them relative to a fixed coarse
partition.  (Trajectories can still differ, so the per-seed inequality
`stalls(C) ≤ stalls(G)` is not strict in every seed; it holds on average by a
wide margin.)

**(ii) Terminal vacuity.**
If `P` is discrete, then `G(R,P) = R \ {(a,a)}`.  Self-loops are never
traversable (a move requires a different block), so gate reachability equals
ordinary graph reachability.  This holds in **100/100** D and CR runs at the
final step, and in 88–94/100 B/C/H runs.  Consequently the coupling has no
reachability signature at the endpoint, matching the zero interaction CI for
stored and gate reachability.

**(iii) Partition-conditioned placement is a transient.**
D's candidate rule is

```
C_t = {(z,b) : b ≠ z, b ∉ [z]_{P_{t+1}}, b ∉ S_R(z),
              P_{t+1}(b) ∉ B_out(z)}.
```

When `P_{t+1}` is discrete, `[z] = {z}`, so `b ∉ [z]_{P_{t+1}}` already
implies `b ≠ z`; and `B_out(z)` is the set of successor blocks, so
`P_{t+1}(b) ∉ B_out(z)` is implied by `b ∉ S_R(z)`.  Hence
`C_t = {(z,b) : b ≠ z, b ∉ S_R(z)}`, which contains no partition information.
The partition is discrete on **97.76%** of D steps,
and `C_t` equals the source cross-block pool on **98.96%** of steps (mean
extra pool edges 0.0164).  The "endogenous distinguishability" part of the
placement rule is therefore active for roughly the first one or two steps of
each 100-step run.

**(iv) The gate-relative refinement is not the bisimulation quotient.**
As noted in §1, C and B final partitions differ in 10/100 seeds, always with C
coarser by exactly one block.  This is a real but tiny departure from ordinary
Moore refinement, with no reachability consequence.

These four facts are compositions of standard notions: partition refinement,
bisimulation with internal moves, the duality between partition refinement and
relation inclusion, and finite-state random walks on churning graphs.  None
requires a new mathematical object.

## 6. Comparison with established machinery

| element of the model | standard counterpart |
|---|---|
| `Split(P,R)` | one round of Moore's partition-refinement algorithm for bisimulation |
| `Split(P,G(R,P))` | refinement with intra-block moves treated as invisible (internal/hidden transitions) |
| `S_g` and `G` | admissible-action filter induced by an equivalence relation; a quotient-level transition guard |
| `(z_t,P_t,R_t,α_t)` | finite-state controller with endogenous graph and memory; an ordinary augmented Markov chain |
| D creation rule | deterministic local completion of the current node's out-neighbourhood |
| CR | uniform random sampling from a feasibility pool with matched cardinality |
| degree/clustering differences | source-concentration effect familiar from graph growth models |

The D-versus-CR contrast is a comparison between a deterministic local
completion rule and a uniform global sampler with the same budget.  It is not
a comparison between "structured" and "unstructured" graphs: matching the
source (CS) or the quotient-level edge multiset (CT) reproduces D exactly.

## 7. Bottom line

Formally, the coupled system is an ordinary finite-state transition system with
a partition-dependent guard.  For fixed `R` the guard is monotone in the
partition and becomes vacuous at the discrete partition.  The measured
interaction is a correct consequence of that monotonicity, not evidence of a
new mechanism.  The
only precise departures from the standard formalism are negative: the
gate-relative refinement is not Moore refinement on `R` (10/100 partitions
differ), and the partition-conditioned placement rule is asymptotically
partition-independent (98.96% of steps).  Both reduce, rather than increase,
the scope of the original claim.
