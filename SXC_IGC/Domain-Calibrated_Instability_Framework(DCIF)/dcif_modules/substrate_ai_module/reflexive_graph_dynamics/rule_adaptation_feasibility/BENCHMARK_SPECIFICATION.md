# Benchmark Specification

## 1. Problem class

Online adaptation of graph-transformation rules under structural change.

A base graph satisfies four structural constraints. Three fixed structural
disruptions are applied at fixed operation counts. After each disruption the
system must restore all four constraints using its rule library, under a fixed
operation budget. The graph is the task; the rule library is the thing being
tested.

**This is a synthetic benchmark.** No claim of real-world validity is made. It
is designed to be objective, exactly reproducible, and to contain a known
complete rule inventory so that a fully informed fixed baseline exists.

## 2. Graph

| Property | Value |
|---|---|
| Nodes | `n = 24`, `V = {0..23}` |
| Root | `0` |
| Out-degree cap | `K = 3` if `case_id` even, `4` if odd |
| Base edges | A Hamiltonian cycle plus random forward edges, target `2n = 48` edges |
| Required edges | 6 randomly chosen non-mutual edges, added to the base graph |
| Case seed | `1000003 + case_id * 7919` |

The base graph is asserted to satisfy all four constraints; construction fails
loudly otherwise.

## 3. Constraints

| ID | Constraint | Violation count `v_i` |
|---|---|---|
| C1 | Root reaches every node | number of unreachable nodes |
| C2 | `outdeg(v) <= K` for all `v` | `sum_v max(0, outdeg(v) - K)` |
| C3 | No mutual pair `(u,v)` and `(v,u)` | number of unordered mutual pairs |
| C4 | All required edges present | number of missing required edges |

**Total violations** `V(G) = v_1 + v_2 + v_3 + v_4`.

The four constraints are deliberately heterogeneous: C1 is a global
reachability property, C2 a degree bound, C3 a local pattern prohibition, C4 a
preservation requirement. Rules that fix one can break another, which is what
makes rule interaction the interesting part of the benchmark.

## 4. Disruptions

| # | Operation | Kind | Parameters | Intent |
|---|---|---|---|---|
| d1 | 250 | edge deletion | 6 edges, required edges protected, no isolated node created | break connectivity locally |
| d2 | 500 | hub overfill + cycle injection | add 5 edges from the max out-degree node; inject 3 mutual pairs | create C2 and C3 violations simultaneously |
| d3 | 750 | edge deletion | 8 edges, required edges may be deleted | create C4 violations plus connectivity damage |

Disruption randomness is seeded independently of the model, so every model sees
byte-identical graphs.

Deletions never remove the last incident edge of a node, because such a node
would be unreachable and unrepairable by any local rule in the space.

## 5. Episode protocol

```
ops = 0
while ops < 900:
    apply any disruption whose op threshold has been reached
    if no violations:  advance clock to next disruption (or stop)
    decision = model.decide(G, ops)
    ops += decision.cost          # evaluations + applications + meta-actions
    if 4 consecutive decisions apply nothing and perform no meta-action: stop
```

Stopping rules, identical for all models:

- budget exhausted (900 ops);
- all constraints satisfied and no disruption remains;
- four consecutive stalled decisions (no applicable rule, no meta-action).

Censored recovery phases are retained and charged the remaining time in that
phase; they are never discarded.

## 6. Metrics

All metrics are computed per (case, model) and defined before the evaluation run.

### Primary

| Metric | Definition |
|---|---|
| `final_violations` | `V(G)` at episode end. Integer, lower is better. |
| `success` | `1` iff `V(G) = 0` at episode end. |
| `recovery_ops` | Mean over the three phases of `ops_at_first_zero_violation - ops_at_disruption`; a censored phase is charged the full remaining phase length. |
| `auc_violations` | `sum_t (ops_t * V(G_t)) / total_ops`; time-weighted violation exposure. |

### Secondary

| Metric | Definition |
|---|---|
| `ops` | Total operations charged. |
| `evals`, `edits`, `mods` | Rule evaluations, applied edits, meta-actions. |
| `library_total`, `library_enabled` | Rule-library size at episode end. |
| `distinct_rules_used` | Rules that produced at least one applied edit. |
| `rule_reuse` | `applications / distinct_rules_used`. |
| `rule_stability` | `mods / edits` (0 for models that cannot modify). |
| `peak_mem_kb` | `tracemalloc` peak during the episode. |
| `runtime_s` | Wall-clock per episode. |
| `n_censored` | Recovery phases not completed within the phase. |
| `ops_per_success` | `mean_ops * n_cases / successful_cases`. |
| `oscillation_steps` | Decisions where `V` repeats the value two steps earlier without reaching zero. |

No composite score is used. Metrics are reported separately so that a model
cannot win on an arbitrary weighting.

## 7. Splits

| Split | Case IDs | Purpose |
|---|---|---|
| Development | 0–39 | Model and meta-rule configuration; pilot debugging |
| Validation | 40–59 | Implementation check; no tuning after this point |
| Held-out evaluation | 60–159 | Final comparison, run once |

Cases differ only by seed and by `K`. The evaluation cases were not inspected
before the frozen run. Source and configuration hashes were recorded in
`config/SOURCE_HASHES.txt` before evaluation and verified afterwards.

## 8. Why this benchmark is representative of the stated problem

The stated problem is: *can a system that edits its own transformation rules
maintain structural constraints under change better than systems that do not?*

The benchmark exercises exactly the required ingredients:

- **Structural change** — three disruptions that damage different constraint
  types.
- **Rule interaction** — a rule that repairs one constraint can violate another
  (e.g. adding a reachability edge can create a 2-cycle).
- **An incomplete starting library** — the seed library lacks safe variants and
  radius > 1, so the full inventory cannot be reached without creation.
- **A known complete inventory** — 68 rules, all reachable by Model D's create
  action, so the fully informed baseline B is well defined and not fabricated
  from evaluation outcomes.

## 9. Threats to validity

- Synthetic graphs only; not representative of real dependency graphs.
- One task family, one time scale, one budget (900 ops).
- The rule space is small (68), which caps the possible benefit of creation.
- Disruptions are fixed rather than adversarial.
- Success is a hard threshold; partial recovery is captured by `auc_violations`.

These are expanded in `LIMITATIONS.md`.
