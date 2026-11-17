# Capability Specification

This document fixes exactly what is being tested. It was written before the
held-out evaluation split was executed.

## 1. System state

```
X_t = (G_t, R_t, H_t)
```

| Component | Definition |
|---|---|
| `G_t` | Directed graph `(V, E_t)` with `V = {0..23}`, designated root `0`, per-case out-degree cap `K ∈ {3,4}`, and a fixed set `R_req` of 6 required edges. |
| `R_t` | Finite set of transformation rules held by the system. Each rule is a pair `(template, parameters)` from the 68-element space defined in §3. Rules may be enabled or disabled. |
| `H_t` | Per-rule statistics: attempts, uses, successes (`delta > 0`), summed gain, last use, origin, modification count; plus the last 10 violation vectors and a stall streak. |

An **operation** on `X_t` is one of:

- **evaluation** — match one rule against `G_t`, simulate the edit, score it (1 op);
- **application** — commit the chosen edit to `G_t` (1 op);
- **meta-action** — create, modify, disable, or delete a rule (1 op; create = 3 ops).

The **budget** is 900 ops per case for every model, including all evaluations,
applications, and meta-actions. There is no free search.

## 2. Rules and the rule space

A rule deterministically maps a graph to at most one edit, or to no edit. The
seven templates are:

| Template | Effect | Violation targeted |
|---|---|---|
| `REACH` | Add `u -> v` where `v` is unreachable from the root and `u` is reachable within `radius` (undirected distance). Optional `avoid_cycle` forbids creating a mutual pair. | C1 |
| `REACH_CAP` | As `REACH`, but only if `outdeg(u) < K`. | C1 |
| `CAP` | Remove one outgoing edge of a maximum out-degree node with `outdeg > K`. | C2 |
| `CAP_SAFE` | As `CAP`, but only removals that preserve root reachability and all required edges. | C2 |
| `CYCLE` | Remove one direction of a mutual pair. Optional `safe` restricts to removals preserving C1 and C4. | C3 |
| `REQ` | Add one missing required edge. | C4 |
| `REWIRE` | Move one outgoing edge of an overfull node to a nearby unused target. Optional `avoid_cycle`. | C2 |

Parameters and cardinalities:

| Template | radius | policy | other | count |
|---|---|---|---|---|
| `REACH` | 1,2,3 | min_out, max_out, min_id | avoid_cycle ∈ {F,T} | 18 |
| `REACH_CAP` | 1,2,3 | min_out, max_out, min_id | avoid_cycle ∈ {F,T} | 18 |
| `CAP` | — | min_out, max_out, min_id | — | 3 |
| `CAP_SAFE` | — | min_out, max_out, min_id | — | 3 |
| `CYCLE` | — | min_id, max_id, non_req | safe ∈ {F,T} | 6 |
| `REQ` | — | — | order ∈ {min_id, max_id} | 2 |
| `REWIRE` | 1,2,3 | min_out, max_out, min_id | avoid_cycle ∈ {F,T} | 18 |

**Total: 68 rules.** The space is enumerated exhaustively and is identical for
every model. No model can invent a rule outside it.

## 3. The capability under test

**Capability C\*:** *a system can change which graph-transformation rules exist
in its library, at run time, in response to its own observed performance, and
those changes measurably alter its subsequent behaviour.*

Four sub-capabilities, tested separately where possible:

| ID | Sub-capability | Tested by |
|---|---|---|
| C1 | **Create** a rule not previously in the library | Models D, Dc |
| C2 | **Modify** an existing rule's parameters | Model D (`modify` events) |
| C3 | **Disable/delete** rules | Model D, Model C (disable only) |
| C4 | **Modify the meta-rules themselves** | **Out of scope** |

A rule modification counts as having an observable consequence only if the rule
is subsequently evaluated on a matching graph and changes `G_t`. Rules that are
created and never used are recorded as `unnecessary = 1` and count against the
mechanism's cost.

## 4. Meta-rules (fixed for the whole study)

Model D's adaptation is governed by five fixed meta-rules. They are part of the
model, not the hypothesis, and were not changed after the evaluation split was
run.

| Meta-rule | Trigger | Action | Cost |
|---|---|---|---|
| M1 create | `stall_streak >= 2` **or** no improvement in total violations over the last 10 decisions | Create the highest-priority absent rule targeting a currently violated constraint (priority: safe variants, then larger radius, then template, then policy) | 3 ops |
| M1 guard | 6 enabled rules for the same constraint type have `attempts >= 6` and `successes == 0` | Do not create | 0 |
| M2 disable | `attempts >= 12` and `successes == 0` | Disable, unless it is the last enabled rule covering some constraint type, or its target type is currently violated | 1 op |
| M3 modify | Oldest disabled rule whose target type is currently violated | Step to the next parameter variant, reset statistics, re-enable | 1 op |
| M4 delete | Library > 18 rules, or > 3 disabled rules | Delete the least useful non-seed rule | 1 op |
| M5 schedule | Every 20 ops | At most one meta-action per check | — |

The meta-rules are bounded: no code execution, no external optimiser, no
unbounded search, and no ability to edit themselves.

## 5. What would count as success

The capability would be **supported** only if, on the held-out evaluation cases:

1. Model D beats Model B on at least one primary metric (final violations,
   recovery time, or success rate) with a Holm-corrected significant paired
   difference and a non-trivial effect size; **and**
2. Model D beats Model C on the same metric; **and**
3. Model D is not worse than Model E1 on that metric; **and**
4. the advantage survives equal-budget accounting (it does by construction, since
   every meta-action is charged); **and**
5. the advantage is not explained by a smaller library alone.

Any other pattern — equivalence, mixed results, or inferiority — counts against
the capability. These criteria were fixed before evaluation.

## 6. Interpretation boundaries

- Rule creation is search in a finite rule space; it is not invention of a new
  representational primitive.
- `(G_t, R_t, H_t)` is a transition system over an enlarged state. Nothing here
  escapes ordinary computation.
- A positive result would demonstrate a *bounded engineering advantage on this
  benchmark*, not a general capability.
- No claim is made about real-world graphs, emergent behaviour, or superiority
  over graph-rewriting systems that were not implemented.
