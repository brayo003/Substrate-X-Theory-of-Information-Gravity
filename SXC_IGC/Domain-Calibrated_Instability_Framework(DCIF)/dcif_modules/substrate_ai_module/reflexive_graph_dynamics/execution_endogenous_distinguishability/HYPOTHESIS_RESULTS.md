# HYPOTHESIS_RESULTS

## 1. Hypotheses as tested

**H1 (coupled):** coupling state-distinguishability refinement to transition
admissibility produces reproducible changes in system dynamics that cannot be
explained merely by partition refinement alone, unrestricted graph evolution,
or the number of created edges.

**H0 (null):** the observed behaviour of the coupled model can be explained by
the independent effects of ordinary partition refinement, transition gating,
graph structure and traversal history; the coupling produces no additional
identifiable dynamical effect under the tested conditions.

H1 is a conjunction.  It is evaluated on three separable clauses:

| clause | operational test |
|---|---|
| **H1a — interaction** | paired 2×2 interaction `(C−B)−(G−A)` on per-seed dynamical and structural metrics, 95% bootstrap CI, Wilcoxon, Holm |
| **H1b — beyond count** | D-vs-CR paired differences on non-tautological observables (partition, stored/gate reachability, topology), plus exact count/source/topology-matched controls |
| **H1c — beyond the formalism** | whether any surviving effect requires a mechanism not already present in the definitions |

Each clause is assessed on its own terms: H1a requires a reproducible
interaction; H1b requires a non-tautological D/CR effect; H1c requires that a
surviving effect not be entailed by the definitions.  H1 as a whole requires
H1a plus H1c (or H1a plus H1b).

## 2. H1a — interaction of refinement and gating

The 2×2 design is A (neither), B (refinement only), G (gating only),
C (both).  All four use the same instances, start states and movement
variates, paired by seed.

| metric | A | B | G | C | DiD `(C−B)−(G−A)` | 95% CI | dz | Holm p |
|---|---|---|---|---|---|---|---|---|
| distinct states | 9.92 | 9.92 | 6.74 | 9.93 | **+3.19** | 2.51 to 3.89 | +0.90 | 1.4e-11 |
| steps traversed | 100.0 | 100.0 | 48.47 | 87.37 | **+38.90** | 29.42 to 48.61 | +0.78 | 8.0e-8 |
| stall steps | 0.0 | 0.0 | 51.53 | 12.63 | **−38.90** | −48.67 to −28.94 | −0.78 | 8.0e-8 |
| final blocks | 3.00 | 11.88 | 3.00 | 11.78 | −0.10 | −0.16 to −0.05 | −0.33 | 7.8e-3 |
| final gate edges | 24.06 | 32.94 | 24.06 | 32.88 | −0.06 | −0.11 to −0.02 | −0.25 | 0.043 |
| stored reach | 10.87 | 10.87 | 10.87 | 10.87 | 0.00 | 0.00 to 0.00 | — | 1.0 |
| gate reach | 8.99 | 10.85 | 8.99 | 10.85 | 0.00 | 0.00 to 0.00 | — | 1.0 |
| total splits | 0.0 | 8.79 | 0.0 | 8.69 | −0.10 | −0.16 to −0.05 | −0.33 | 7.8e-3 |

Interpretation of the decomposition:

- **Refinement alone does nothing dynamical.**  A and B have the same
  trajectory in 100/100 seeds, because B moves on `R`, not on the gate.
  B's only effect is the partition itself.
- **Gating alone is strongly disruptive.**  G stalls on 51.53 steps and is
  trapped forever in 55/100 seeds.
- **The combination is not additive.**  The interaction is large and
  unambiguous on stalls/traversals/distinct states (|dz| ≈ 0.8–0.9), and
  statistically robust after Holm correction.
- **The interaction is nil on reachability.**  Both DiD confidence intervals
  are exactly `[0, 0]`; B and C have identical final gate reachability in
  100/100 seeds.
- **Final-partition effect is detectable but negligible.**  −0.10 blocks
  (10/100 seeds differ), driven by the gate-relative refinement being slightly
  coarser than Moore refinement on `R`.

The interaction is therefore **real and reproducible on trajectory
statistics, and absent on reachability**.

### 2.1 What causes the interaction

The gate is monotone in the partition: if `P` is refined, fewer state pairs
are equivalent, so more edges are admissible.  Refinement never merges
blocks.  Hence along a run the gate can only grow, and a walk that is trapped
by a coarse partition can be released by later refinement.  This is exactly
what the numbers show:

- G (frozen coarse `P`): gate stays small, 55/100 absorbing stalls.
- C (refining `P`): gate grows toward `R`, 13/100 runs end stalled, 12/100
  absorbing.

The trap condition is exact: `gate_successors(z, R, P)` is empty **iff**
every successor of `z` in `R` is `P`-equivalent to `z`.  At a discrete
partition this reduces to "the only successor is a self-loop".  Of C's 12
absorbing stalls, 9 end at a state whose only successor is itself, and 3 at a
state whose only successor is in its own (still non-singleton) block.
Refinement shrinks the trap set from "all successors in the coarse block" to
"only self/same-block successors".

### 2.2 Is the interaction the coupling of refinement to the gate?

No.  Control H keeps both mechanisms but refines on the unrestricted `R`:

| metric | C | H | C−H | 95% CI |
|---|---|---|---|---|
| distinct states | 9.93 | 9.93 | 0.00 | 0 to 0 |
| steps traversed | 87.37 | 87.37 | 0.00 | 0 to 0 |
| stall steps | 12.63 | 12.63 | 0.00 | 0 to 0 |
| stored reach | 10.87 | 10.87 | 0.00 | 0 to 0 |
| gate reach | 10.85 | 10.85 | 0.00 | 0 to 0 |
| final blocks | 11.78 | 11.88 | −0.10 | −0.16 to −0.04 |

H and B have identical final partitions in 100/100 seeds.  The specific act of
feeding `gate(R,P)` into the refinement operator changes the final partition
in only 10/100 seeds and has **no** trajectory or reachability effect.  The
observable coupling is the shared partition: refinement relaxes the movement
gate.  H1a's empirical criterion is met for that shared-partition mechanism;
the coupling of the refinement operator itself contributes nothing.

## 3. H1b — D versus CR beyond edge count

| observable | result | status |
|---|---|---|
| created edges per seed | equal 100/100 | identity of the design |
| final graph | differs 100/100 | guaranteed by different placement |
| trajectory | differs 100/100 | guaranteed by different graphs |
| final partition | **identical 100/100** | no effect |
| stored reachability | differs 1/100; mean −0.11 states, p = 0.32 | no effect |
| gate reachability (fresh) | differs 1/100; mean −0.11 states, p = 0.32 | no effect |
| created edges ever traversed | 16.67 vs 35.87, diff −19.20 [−20.18, −18.19], dz −3.75 | explained by source concentration |
| removal count | 581.17 vs 580.48, diff +0.69 | downstream of traversed-edges |
| final edges | 66.76 vs 67.45, diff −0.69 | downstream of removal |
| out-degree sd | 4.08 vs 1.61, diff +2.47, dz +5.22 | explained by source concentration |
| max out-degree | 11.67 vs 8.29, diff +3.38 | explained by source concentration |
| clustering | 0.836 vs 0.731, diff +0.105, dz +1.73 | explained by source concentration |
| components / largest WCC / path length | no difference | — |
| consistency violations | 0 in both | — |

Source concentration: **100%** of D's created edges have source `z_t`;
**8.19%** of CR's do.  D creates from the current state to non-successors, so
its new edges are unusable until the walk revisits `z`; CR scatters the same
number of edges over the whole pool, so they are available when the walk
reaches their source.  This single difference accounts for the traversal,
removal, final-size and degree-distribution differences.

The exact matching controls confirm this:

- **CS** (same count, same source) is feasible in 79/100 seeds and produces
  the **same final graph as D in 79/79**; every topology difference is exactly
  zero.
- **CT** (same count, same quotient block-pair multiset) is feasible in
  77/100 seeds and produces the **same final graph as D in 77/77**.
- D's candidate set equals the source cross-block pool on **98.96%** of steps;
  the mean number of extra pool edges is **0.0164**.  The partition-conditioned
  target filter is active on about 1% of steps.

H1b is **not supported**: after count and source (or count and quotient
topology) are matched, D's partition-conditioned placement has no remaining
freedom to express.  The only surviving D-vs-CR differences are identities of
the design or consequences of source concentration.

## 4. H1c — beyond the existing formalism

Every observed effect is derivable from the update rules without a new
principle:

1. Refinement is one Moore round per step (on `R` in B, on the gated relation
   in C/D/CR), and always refines.
2. The gate is a fixed function of `(R_t, P_t)`.  For fixed `R` (C/G/H) it is
   monotone increasing under refinement; with edge churn (D/CR) it also tracks
   `R_t`.  In the fixed-`R` case this entails the stall interaction.
3. The complete state `(z_t, P_t, R_t, edge ages)` is a finite augmented
   state; the model is an ordinary randomised transition system on it.
4. At the discrete partition the gate equals `R` minus self-loops
   (100/100 D and CR runs), so admissibility becomes ordinary graph
   reachability and the coupling is vacuous.
5. Once the partition is discrete, D's placement rule is partition-independent
   ("all non-successor edges out of `z`").

No invariant or dynamical property was found that requires machinery beyond
partition refinement, bisimulation, graph reachability, or finite-state
Markov dynamics.  H1c is **not supported**.

## 5. Evaluation against H0

| H0 component | verdict |
|---|---|
| refinement alone explains the dynamics | no — refinement alone is trajectory-identical to no refinement |
| gating alone explains the dynamics | no — gating alone stalls 51.5/100 steps; coupling reduces this to 12.6/100 but does not remove it |
| unrestricted graph evolution explains the dynamics | the three-model experiment has no graph evolution; the D/CR branch is answered in §3 |
| edge count explains the D/CR differences | no — counts are exactly matched; source concentration explains them |
| coupling produces no additional identifiable dynamical effect | rejected for stalls/traversals/distinct states; not rejected for reachability or partition structure |

H0 is partially rejected: a non-additive dynamical interaction is present, but
it is entailed by the definitions and has no reachability or persistent
structural signature.  H0 is not rejected for the D/CR branch.

## 6. Verdict

**PARTIALLY SUPPORTED**

Reason: the coupled model produces a reproducible, large, non-additive effect
on traversal and stalling that neither refinement alone nor gating alone
produces, so the narrow H1a clause holds.  But the effect is fully explained by
monotone gate relaxation under refinement (H1c fails), disappears from
reachability and nearly from the final partition, the gate-fed refinement is
dynamically inert (C ≈ H), and the D/CR experiment yields no effect beyond
count and source concentration (H1b fails).  The central claim of an effect
not already contained in the formalism is therefore unresolved/unsupported.
That combination is the partial-support case: some effects are
reproducible, but the central coupling claim remains unresolved.

### What did the system actually demonstrate that we did not already know from the control models?

It demonstrated one quantitative fact the controls alone do not give: gating
alone strands the walk for about half the run (51.5 stall steps, 55/100
absorbing traps), while gating plus refinement strands it for about an eighth
(12.6 stall steps, 13/100 end stalled, 12/100 permanently trapped).
Refinement monotonically re-admits edges that the coarse gate removed, so the
two mechanisms interact strongly in the trajectory.  It did **not** demonstrate
a new reachability relation, a persistent structural effect of the coupling, or
any D/CR distinction that survives matching on edge count and source.  The
practical reading is: the coupling changes *how often the system moves*, not
*where it can go*.
