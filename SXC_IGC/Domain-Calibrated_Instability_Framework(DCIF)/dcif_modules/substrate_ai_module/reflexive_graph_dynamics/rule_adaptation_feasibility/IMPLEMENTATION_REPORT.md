# Implementation Report

## 1. Location and isolation

Everything lives in `/home/lenovo/Projects/GI/rule_adaptation_feasibility/`.
The completed `execution_endogenous_distinguishability/` experiment and every
other project directory were read-only during this work; no file outside the new
experiment directory was created or modified.

No reusable graph-rewriting engine was found in the project. The prior
experiments (`one.py` and the evidence-benchmark series) implement topology and
evidence propagation, not rule rewriting. This study therefore ships a
self-contained implementation.

## 2. Files

| Path | Role |
|---|---|
| `src/graph.py` | graph state, constraints, disruption operators, case generation |
| `src/rules.py` | 68-rule space, matching, evaluation, edit application |
| `src/models.py` | Models A, B, C, D, Dc, E1, E2 and meta-rules |
| `src/bench.py` | episode runner, op accounting, metrics, event annotation |
| `run_experiment.py` | CLI, splits, CSV/JSON/manifest output |
| `analysis.py` | paired statistics, bootstrap CIs, Holm correction, CSV tables |
| `config/benchmark.json` | frozen benchmark parameters |
| `config/models.json` | frozen model and meta-rule parameters |
| `config/SOURCE_HASHES.txt` | SHA-256 of source and config at freeze time |
| `config/ENVIRONMENT.txt` | Python, platform, library versions |
| `results/raw/` | per-split runs, events, decisions, cases, manifests |
| `results/analysis/` | stability metrics and analysis summary |
| `logs/` | stdout of each run |

## 3. Determinism

- All randomness is `random.Random(seed)` with fixed seeds derived from case id.
- No wall-clock, network, GPU, or thread scheduling affects results.
- `tracemalloc` and `time.perf_counter` are recorded but never used in decisions.
- The analysis bootstrap uses `numpy.random.default_rng(20261115)`.

Verification: the evaluation split was executed twice. All 700 run rows were
identical in every behavioural column, and `eval_events.csv` was byte-identical.
The only differing column was `runtime_s` (wall-clock timing), as expected.

## 4. Operation accounting

The central implementation detail is that `Model.decide()` returns the exact
cost of its decision:

| Action | Cost |
|---|---|
| `evaluate(rule, G)` | 1 |
| apply the chosen edit | 1 |
| create a rule | 3 |
| modify / disable / delete a rule | 1 |
| meta-check with no action | 0 |

The runner adds `decision.cost` to the episode clock. A model that evaluates 30
candidates to make one edit pays 31 ops; a model that finds an applicable rule
on the first scan pays 2. Nothing is hidden from the budget.

## 5. Defects found and fixed during development

Development cases 0–39 were used for these fixes. No evaluation case was
inspected before the frozen run. Each defect and fix is recorded here so the
development history is auditable.

| # | Symptom (dev cases) | Diagnosis | Fix |
|---|---|---|---|
| 1 | All models stopped at op 0 on satisfied graphs | runner treated "nothing to do" as termination | detect satisfaction, advance clock to next disruption |
| 2 | A and D oscillated forever on a single 2-cycle | `REACH` adds an edge, `CYCLE` removes it, repeat | added `avoid_cycle` and `safe` parameters to the rule space (benchmark revision R2) |
| 3 | C and D often found no applicable rule | top-10 UCB slice missed the violated constraint type | prioritise rules targeting currently violated types; soft cap 10, hard cap 30 |
| 4 | D never created the rule it needed | create trigger required a persistence count that oscillation never met | trigger on `stall_streak >= 2` **or** no improvement over 10 decisions |
| 5 | D created rules late, after budget exhaustion | meta-check every 40 ops | every 20 ops |
| 6 | D disabled its only `REQ` rule, then failed C4 | disable ignored coverage | never disable the last rule covering a type, or while that type is violated |
| 7 | D created 10 variants of one template in a row | create priority exhausted a template family | priority orders by radius before template; creation stops after 6 failed variants for a type |
| 8 | Adaptive models applied edits that lost 22 violations | best-delta selection with no floor | no-harm rule: never apply a negative-delta edit |
| 9 | `CYCLE` removals disconnected the graph | `CYCLE` had no safety variant | added `safe` parameter (benchmark revision R2) |
| 10 | D's `modify` churned rules with no violated target | modify fired unconditionally | modify only rules whose target type is currently violated |

**Benchmark revision note.** Revision R1 had 65 rules and no `safe`/`avoid_cycle`
variants. Pilot runs on dev case 0 showed that this made the benchmark measure a
known-bad edit operator rather than adaptation, because no model could avoid the
add/remove oscillation. Revision R2 (68 rules) was frozen before validation and
before any evaluation case was generated. The revision is a benchmark design
decision made on dev data, not a response to evaluation results.

## 6. Verification performed

1. **Constraint correctness** — `make_base_graph` asserts `V(G) = 0` for every
   generated case. All 160 cases (dev + validation + eval) pass.
2. **Disruption legality** — deletions never remove the last incident edge of a
   node; required-edge deletion is permitted only at d3.
3. **Determinism** — evaluation re-run produced identical values in every
   behavioural column of `eval_runs.csv` (700/700 rows) and a byte-identical
   `eval_events.csv`; only `runtime_s` varied.
4. **Freeze integrity** — `sha256sum -c config/SOURCE_HASHES.txt` passes after
   the evaluation run, proving no source or configuration changed.
5. **Budget honesty** — every model's recorded `ops` equals
   `evals + edits + meta costs` to within the final decision's overshoot; no
   model can spend unrecorded operations.
6. **Event annotation** — each create/modify event is checked against the
   application log for the following 50 ops; `effect_observed`,
   `effect_improved`, and `unnecessary` are filled mechanically.
7. **Paired data completeness** — 100 evaluation cases × 7 models = 700 rows,
   no missing pairs in any comparison.

## 7. Statistical implementation

- Paired differences are computed case-by-case on identical seeds.
- 95% CIs are percentile bootstrap with 10,000 resamples.
- Continuous metrics use the two-sided Wilcoxon signed-rank test; the effect
  size is the rank-biserial correlation of the paired differences.
- Binary success uses the exact McNemar test; the effect size is the risk
  difference.
- Multiplicity is controlled with Holm–Bonferroni within each metric family
  (8 comparisons per metric).
- Censored recovery phases are charged their full remaining length and are never
  dropped.

## 8. Reproduction

```
cd /home/lenovo/Projects/GI/rule_adaptation_feasibility
bash reproduce.sh
```

The script re-runs all splits, re-derives every table, verifies source hashes,
and prints the verdict inputs. Expected runtime on the reference machine:
about 45 seconds.

## 9. Environment

Python 3.10.12, numpy 1.26.4, scipy 1.15.3, pandas 2.3.3, Linux x86_64.
Full details in `config/ENVIRONMENT.txt`.
