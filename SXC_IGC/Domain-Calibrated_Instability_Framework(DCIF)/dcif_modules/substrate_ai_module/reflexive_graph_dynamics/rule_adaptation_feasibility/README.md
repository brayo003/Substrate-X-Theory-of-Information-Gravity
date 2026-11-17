# Endogenous Rule Adaptation — Feasibility Study

Final verdict: **B — REDUNDANT**. See `FINAL_VERDICT.md`.

## Question

Under changing graph structures, can a system that **creates, modifies, disables,
and deletes its own graph-transformation rules** maintain structural constraints
better or more efficiently than fixed rules, a complete fixed rule library,
adaptive rule selection, or an established graph-rewriting baseline — under an
equal operation budget?

## Answer in one table (held-out, 100 paired cases)

| Model | What it can do | Success | Final violations (total) | Ops per success |
|---|---|---|---|---|
| A | 7 fixed rules | 22% | 355 | 3,761 |
| B | all 68 rules, fixed priority | **96%** | **26** | **798** |
| C | all 68 rules, adaptive selection | 82% | 40 | 950 |
| D | 7 seed rules + create/modify/disable/delete | 68% | 65 | 1,157 |
| Dc | as D, creation only (ablation) | 70% | 64 | 1,104 |
| E1 | programmed rewriting, all 68 rules | **96%** | **26** | 802 |
| E2 | exhaustive best-improvement search | 8% | 289 | 11,429 |

Rule creation improves an incomplete library (A → D) but is dominated by simply
having the complete library (B), by adaptive selection over it (C), and by
programmed rewriting (E1). 73% of rule creations had no observable effect.

## Contents

| File | Contents |
|---|---|
| `RESEARCH_REVIEW.md` | literature review and Gate 1 assessment |
| `CAPABILITY_SPECIFICATION.md` | exact capability definition, rule space, meta-rules, success criteria |
| `BENCHMARK_SPECIFICATION.md` | graphs, constraints, disruptions, budget, metrics, splits |
| `MODEL_DESIGN.md` | Models A–E, ablations, fairness controls |
| `IMPLEMENTATION_REPORT.md` | code, accounting, defects found and fixed, verification |
| `EXPERIMENT_RESULTS.md` | all results and Tests 1–6 |
| `MODEL_COMPARISON.csv` | per-model aggregates with bootstrap CIs |
| `PAIRED_STATISTICS.csv` | 32 paired comparisons, CIs, effect sizes, Holm correction |
| `RULE_EVOLUTION_LOG.csv` | all 609 create/modify/disable/delete events |
| `COMPLEXITY_METRICS.csv` | operation, library, memory, and runtime costs |
| `LIMITATIONS.md` | scope, design, statistical, and measurement limitations |
| `FINAL_VERDICT.md` | the go/no-go decision and its conditions |
| `reproduce.sh` | full reproduction, including a hard check against frozen results |

## Reproduce

```
bash reproduce.sh        # ~50 s, no network, everything inside this directory
```

Source: `src/`, `run_experiment.py`, `analysis.py`.
Frozen configuration: `config/benchmark.json`, `config/models.json`,
`config/SOURCE_HASHES.txt`. Raw per-case data: `results/raw/`.

## Scope note

Synthetic 24-node directed graphs, four constraints, three forced disruptions,
900 operations. This is a feasibility benchmark, not a real-world evaluation.
Only wall-clock columns vary between runs; every behavioural result is
deterministic.
