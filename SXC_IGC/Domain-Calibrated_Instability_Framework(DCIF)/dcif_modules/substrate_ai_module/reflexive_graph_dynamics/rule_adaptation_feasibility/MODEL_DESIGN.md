# Model Design

All models share one graph, one constraint set, one disruption schedule, one
rule-evaluation primitive, one operation budget (900 ops), and one stopping rule.
They differ **only** in their rule library and their decision procedure.

## 0. Common mechanics

### 0.1 The operation

Every model's decision returns a cost in operations:

```
cost = evaluations + applications + meta_actions
```

- one **evaluation**: match a rule against the graph, simulate it, score
  `delta = V(G) - V(G')`  → 1 op
- one **application**: replace `G` by `G'`  → 1 op
- one **meta-action**: create (3 ops), modify / disable / delete (1 op)

Nothing is free. A model that evaluates more candidates per decision takes fewer
decisions. This is the equal-resource control.

### 0.2 Common rule evaluation

For a rule `r` and graph `G`, `evaluate(r, G)` returns:

- the deterministic edit selected by the template and its parameters,
- the resulting graph `G'`,
- `delta = V(G) - V(G')`.

A rule that produces no match returns `None`. Ties inside a template are broken
by fixed policy orders; there is no randomness in any model.

### 0.3 Common anti-repetition rule

No model applies the same edit twice in a row (`last_key` guard). This is a
generic liveness rule, applied identically to all models. It prevents trivial
infinite loops but does not prevent longer oscillations.

### 0.4 No-harm rule (adaptive models only)

Models C, D, Dc, and E2 never apply an edit whose predicted `delta` is negative.
Model B and E1 apply the first applicable rule in a fixed order regardless of
`delta`; that is part of the fixed-priority baseline's definition. Model A does
the same with its 7-rule library.

---

## 1. Model A — Fixed rules (incomplete library)

- **Library**: 7 rules (the seed library).
- **Decision**: scan the library in a fixed priority order, apply the first
  applicable rule that is not the previous edit.
- **No adaptation** of any kind.

Seed library:

```
REQ|order=min_id
CYCLE|policy=min_id,safe=False
CAP|policy=min_out
CAP_SAFE|policy=min_out
REACH|radius=1,policy=min_out,avoid_cycle=False
REACH_CAP|radius=1,policy=min_out,avoid_cycle=False
REWIRE|radius=1,policy=min_out,avoid_cycle=False
```

It is deliberately incomplete: no safe `CYCLE`, no `avoid_cycle=True` variants,
and no radius > 1. Model A is the "fixed rules, no extra inventory" baseline.

## 2. Model B — Complete fixed library

- **Library**: all 68 rules from the start.
- **Decision**: fixed priority, apply first applicable.
- **No adaptation.**

Priority order (safe-first, fixed before evaluation):

```
1. REQ|order=min_id
2. CYCLE|policy=min_id,safe=True
3. CAP_SAFE|policy=min_out
4. for radius r = 1,2,3:
     REACH|radius=r,policy=min_out,avoid_cycle=True
     REACH_CAP|radius=r,policy=min_out,avoid_cycle=True
     REWIRE|radius=r,policy=min_out,avoid_cycle=True
5. CAP|policy=min_out
6. all remaining rules in space order
```

**Why this order.** A naive space order puts unsafe radius-1 `REACH` first,
which oscillates against `CYCLE` on 2-cycles and makes B artificially weak.
The safe-first order was chosen on *development* cases so that B is a strong
fixed baseline. Model B is therefore not a strawman: it has every rule Model D
could ever create, plus a priority tuned on dev cases.

**Leakage control.** B's inventory is the whole enumerated space, generated from
the parameter domains in `CAPABILITY_SPECIFICATION.md §2`. It does not depend on
any evaluation outcome.

## 3. Model C — Adaptive rule selection

- **Library**: all 68 rules.
- **Decision**: UCB-style selection; may disable rules; cannot change a rule's
  definition.

Selection procedure per decision:

1. Partition enabled rules into those targeting currently violated constraint
   types (priority 0) and the rest (priority 1).
2. Sort by `(priority, -UCB score, order index)`.
3. Evaluate up to 10 candidates (soft cap), or up to 30 if fewer than `k = 4`
   applicable rules have been found.
4. Apply the applicable candidate with the highest `(delta, priority)`.
5. Never apply a negative-delta edit; report a stall instead.

UCB score for rule `r`:

```
score(r) = gain(r)/attempts(r) + 0.7 * sqrt(ln(1 + total_attempts) / attempts(r))
```

Untried rules receive score `1e9 - order_index`, so every rule is tried at least
once before exploitation begins.

Deactivation: a rule with `attempts >= 15` and `successes == 0` is disabled if
another enabled rule targets the same constraint type and its own target type is
not currently violated. Disabled rules are re-enabled after 50 ops.

## 4. Model D — Endogenous rule modification

- **Library**: 7 seed rules.
- **Decision**: identical selection machinery to Model C (`k = 4`, `ucb_c = 0.7`,
  soft cap 10, hard cap 30, no-harm rule).
- **Additional**: the five bounded meta-rules M1–M5 from
  `CAPABILITY_SPECIFICATION.md §4`, running at most once every 20 ops.

Meta-action ordering within one check:

1. **Create** — if stalled twice in a row, or no improvement over the last 10
   decisions. Choose the highest-priority absent rule for a currently violated
   type.
2. **Disable** — if a rule has `attempts >= 12`, `successes == 0`, is redundant,
   and its type is not currently violated.
3. **Modify** — take the oldest disabled rule whose type is currently violated,
   step it to the next parameter variant, reset its statistics, re-enable it.
4. **Delete** — if the library exceeds 18 rules or has more than 3 disabled
   rules, delete the least useful non-seed rule.

At most one of these happens per check.

**Boundedness.** The meta-rules are a fixed program. They cannot execute
arbitrary code, call an optimiser, inspect evaluation cases, or modify
themselves. Every action is written to `RULE_EVOLUTION_LOG.csv`.

## 5. Model Dc — Creation-only ablation

Identical to D except that M2–M4 (disable, modify, delete) are disabled and only
M1 (create) is active.

Purpose: separate the effect of *adding* rules from the effect of *pruning*
them. Without this ablation, a D−C difference could be caused by destructive
pruning rather than by creation.

## 6. Model E1 — Programmed rewriting (established baseline)

- **Library**: all 68 rules.
- **Decision**: the same fixed safe-first priority as B, but up to 6
  applications per control step (macro-rewriting), stopping early if the graph
  is satisfied or no rule applies.
- **No adaptation.**

This is the operational form of a programmed graph-replacement system: a fixed
rule set, a fixed control order, and batched application. It produces the same
edit sequence as B, but reaches it in fewer control steps.

## 7. Model E2 — Best-improvement repair search

- **Library**: all 68 rules.
- **Decision**: evaluate every enabled rule at every step; apply the edit with
  the highest `delta`; stop if the best `delta` is negative.
- **No meta-adaptation.**

This is the expensive "obvious" baseline: exhaustive one-step lookahead. Under
an equal operation budget it can afford far fewer decisions than the other
models, which is a real cost and is counted.

---

## 8. Fairness controls

| Control | Implementation |
|---|---|
| Same initial graph | Case generated once, shared by all models |
| Same disruptions | Seeded independently of the model |
| Same budget | 900 ops, all evaluations and meta-actions charged |
| Same stopping rule | Budget, satisfaction, or 4 stalled decisions |
| Complete baseline | B and C receive all 68 rules from the start |
| No outcome leakage | B's inventory is the enumerated parameter space, not derived from results |
| Counted meta-costs | create = 3 ops, other actions = 1 op |
| Seed library is genuinely weaker | A and D start with 7 rules that cannot match the full inventory |
| E baselines use the same rules | E1 and E2 operate on the same 68-rule space |
| Destructive pruning isolated | Dc ablation |

## 9. Known asymmetries (reported, not hidden)

- Model B has a hand-tuned safe-first priority; D does not. This favours B and
  makes any D advantage harder to obtain.
- Models C/D evaluate at most 10–30 candidates per decision; B/E1 stop at the
  first applicable rule. B/E1 therefore get more decisions per budget. This is
  the price of selection and is charged consistently.
- Model D pays 3 ops per creation; B pays nothing for the same rule. This is the
  intended cost of endogenous modification.
- E2 is dominated by its own evaluation cost. It is retained as a baseline but
  is not the primary established comparison.
