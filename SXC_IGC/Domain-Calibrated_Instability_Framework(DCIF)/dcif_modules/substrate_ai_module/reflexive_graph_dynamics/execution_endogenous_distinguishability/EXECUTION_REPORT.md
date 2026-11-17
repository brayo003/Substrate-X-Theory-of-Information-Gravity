# EXECUTION_REPORT

**Task:** execute and evaluate the Endogenous Distinguishability Experiment and the
D-versus-CR graph-dynamics experiment.
**Date of execution:** 2026-11-15 (UTC).
**Workspace:** `/home/lenovo/Projects/GI/execution_endogenous_distinguishability/`
(the original project and the frozen V2 audit archive were not modified).

---

## 1. Source, environment and integrity

| item | value |
|---|---|
| implementation | `one.py`, revision 9 |
| source md5 | `9b73b12efc1c43b1a22c99ec2cfac03d` |
| source sha256 | `3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a` |
| source bytes | 94175 |
| OS | Linux 6.17.4-76061704-generic x86_64 (Pop!_OS, glibc 2.35) |
| Python | 3.10.12 (CPython, GCC 11.4.0) |
| numpy / scipy / networkx | 1.26.4 / 1.15.3 / 3.4.2 |
| PRNG | MT19937 via `random.Random`; streams `s*1e6+1` (init), `+2` (move), `+3` (CR ctrl) |

The workspace copy `one.py` is byte-identical to the archived implementation
(md5 above).  All new code is additive: `controls.py` and `analysis/analyze.py`
import `one.py` and do not edit it.

## 2. What was run

All commands were run from the workspace root unless stated.

| # | command | wall time | exit | output |
|---|---|---|---|---|
| 1 | `cd results/primary && python3 ../../one.py --test` | 1.0 s | 0 | 24/24 tests pass, `test_results.json` |
| 2 | `cd results/primary && python3 ../../one.py --seeds 100` | 32.5 s | 0 | `results/primary/experiment_results/` (9 files) |
| 3 | `python3 controls.py --seeds 100` | 35.0 s | 0 | `results/controls/` (G, H, CS, CT) |
| 4 | `python3 analysis/analyze.py` | 10.2 s | 0 | 3 deliverable CSVs + 11 supporting tables + `stats.json` |

Total compute: about 79 s on one core.

### Configuration (documented defaults, unchanged)

| parameter | value |
|---|---|
| `n_states` | 12 |
| `edge_probability` | 0.25 |
| `initial_blocks` | 3 |
| `steps` | 100 |
| `seeds` | 0–99 (100 paired seeds) |
| `cap_per_source` | `None` (uncapped primary model) |
| `removal_age` | 5 |
| initial state | `z0 = seed % 12` |
| movement variates | one pre-drawn uniform per `(seed, t)`, shared by A/B/C/D/CR |

No parameter was changed.  No model definition in `one.py` was changed.

## 3. Reproduction of the archived run

The primary run regenerated the archived outputs exactly:

| file | md5 of new run | md5 of `experiment_results4` | identical |
|---|---|---|---|
| `per_seed_results.csv` | `56824b121b58aa2d9796afe89ee12d36` | same | yes |
| `summary.csv` | `d290d638e756c86c05aa34c708822d18` | same | yes |
| `paired_differences.csv` | `fd2b2e27ec96842624f1b744a910f9ca` | same | yes |

All 10 diagnostic gates passed, including the five critical gates
(`A1`, `E`, `H`, `I`, `T14`).  The reported values are therefore reproducible
in this environment, not approximate.

Reproduced claims (mean over 100 seeds):

| claim | reported | observed |
|---|---|---|
| D created edges | 612.13 | 612.13 |
| CR created edges | 612.13 | 612.13 |
| D created edges ever traversed | 16.67 | 16.67 |
| CR created edges ever traversed | 35.87 | 35.87 |
| D final edges / CR final edges | 66.76 / 67.45 | 66.76 / 67.45 |
| final graphs differ | 100/100 | 100/100 |
| trajectories differ | 100/100 | 100/100 |
| final partitions equal | 100/100 | 100/100 |
| D partition stable (mean) | 3.24 | 3.24 |
| D graph stable (mean) | 99.99 | 99.99 |

This confirms the arithmetic and the implementation.  It does **not** by itself
confirm any interpretation; the controls below test the interpretations.

> Note: `results/primary/experiment_results/experiment_report.md` is generated
> by `one.py` and retains that program's built-in verdict wording
> ("Distinguishable from matched control").  It is a raw artifact, not the
> verdict of this execution.  The verdict of this execution is in
> `HYPOTHESIS_RESULTS.md`.

## 4. Additional controls (pre-registered)

The existing four models do not form a complete factorial, and `CR` matches D
on edge count but not on the source of created edges.  Four controls were
defined in `CONTROL_DEFINITIONS.md` **before** execution and added without
touching `one.py`:

| control | definition | isolates |
|---|---|---|
| **G** | gating on, refinement off, graph fixed | the missing 2×2 cell |
| **H** | gating on, refinement on **unrestricted R** | the act of coupling refinement to the gate |
| **CS** | D loop with the same count and the same source `z`, targets random | source-concentration confound in D-vs-CR |
| **CT** | D loop with the same count and the same block-pair multiset | count matching vs true quotient-topology matching |

The 2×2 design has cells A = (refinement off, gating off), B = (on, off),
G = (off, on), C = (on, on).  `H` decomposes C: both mechanisms present but
decoupled.  `CS` and `CT` are exact matching controls: equal per-step creation
counts, enforced, not statistical.

Feasibility of the post-treatment matching controls was lower than the
pre-run argument assumed, because the control's own trajectory diverges from
D's: CS is feasible in 79/100 seeds, CT in 77/100.  Exclusions are recorded
and not patched; completed runs are reported separately.

## 5. Implementation defect found (not blocking, not repaired in `one.py`)

`run_model_d` finalises with the gate computed at the **start** of the final
iteration (from `(R_99, P_99)`, before that step's refinement and creation),
whereas `run_control_random_matched` recomputes the gate from the final
`(R_100, P_100)`.  Consequently the stored `final_gate` of D is stale in
**99/100** seeds (mean stored 63.70 edges vs 64.00 fresh).

Effect on results:

- `final_gate_edges` for D is off by 0.30 edges on average.
- The reported counter `D_gate_reach_differs_from_CR = 0` becomes **1/100**
  when the gate is recomputed correctly from `(final_graph, final_partition)`
  for both models.
- No trajectory, partition, created-edge or stored-graph quantity is affected.

The corrected quantity is used throughout the analysis.  `one.py` was not
edited; the defect is documented here and in `MATHEMATICAL_INTERPRETATION.md`.

## 6. Definitive findings

### 6.1 The three-model experiment

1. **Model 2 (refinement alone) is dynamically identical to Model 1.**
   A and B produce the same trajectory in 100/100 seeds and the same stored
   graph in 100/100 seeds, because B's movement ignores the gate and `R` is
   fixed.  Refinement changes only the partition label.
2. **Gating alone is strongly disruptive.**  G stalls on 51.53 of 100 steps on
   average, visits 6.74 distinct states (vs 9.92), and ends in an absorbing
   stall in 55/100 seeds.
3. **Refinement + gating (C) is not the sum of the two.**  C stalls on 12.63
   steps, visits 9.93 states, ends stalled in 13/100 seeds (12/100 absorbing),
   and the 2×2 interaction is
   `(C−B) − (G−A) = −38.90` stalls (95% CI −48.67 to −28.94, dz −0.78,
   Holm p = 8.0e-8) and `+3.19` distinct states (95% CI 2.51 to 3.89,
   dz +0.90, Holm p = 1.4e-11).
4. **The interaction has no reachability or partition-size signature.**
   Stored reachability DiD = 0 (CI 0 to 0), gate reachability DiD = 0 (CI 0 to 0),
   final blocks DiD = −0.10 (CI −0.16 to −0.05).  B and C have identical final
   gate reachability in 100/100 seeds.
5. **The refinement-to-gate coupling itself is inert.**  H (gating on,
   refinement on `R`) and C differ by 0 in stalls, traversals, distinct states,
   stored reachability and gate reachability.  They differ in final partition
   in 10/100 seeds and by 0.10 blocks on average.  The observable interaction
   is therefore *refinement relaxing the movement gate*, not the gate being
   fed into the refinement operator.

### 6.2 The D-versus-CR experiment

6. **Count matching is by construction, not an empirical result.**  CR
   receives D's per-step creation counts; equality is 100/100 by definition.
7. **Different graphs and trajectories are also guaranteed.**  Two different
   placement rules with equal counts cannot produce the same graph; the
   100/100 graph and trajectory differences carry no evidential weight.
8. **No partition difference.**  Final partitions are identical in 100/100
   seeds.  D's partition stabilises slightly later (3.24 vs 2.36 steps,
   Holm p = 1.6e-3) but to the same partition.
9. **No reachability difference.**  Stored reachability differs in 1/100
   seeds; corrected gate reachability differs in 1/100 seeds (reported 0/100
   before the final-gate correction).  Paired mean difference −0.11 states,
   p = 0.32.
10. **The traversed-created difference is a source-concentration artefact.**
    D creates 100% of its edges from the current state `z`; CR creates 8.19%.
    D's created edges point to non-successors of `z`, so they cannot be used
    until the walk revisits `z`; CR scatters edges globally, so they are
    available when the walk reaches their source.  Result: 16.67 vs 35.87
    created edges ever traversed.
11. **The topology difference is the same artefact.**  D's out-degree is much
    more concentrated (sd 4.08 vs 1.61, dz 5.22; max 11.67 vs 8.29) and its
    clustering is higher (0.836 vs 0.731, dz 1.73).  Connectivity, largest
    component, path length and consistency violations do not differ.
    Source-matched (CS) and quotient-topology-matched (CT) controls reproduce
    D **exactly** (all topology differences 0 on feasible seeds; final graphs
    identical in 79/79 and 77/77).
12. **D's creation rule is nearly deterministic and asymptotically
    partition-independent.**  The partition is discrete on 97.76% of D steps;
    the candidate set equals the source cross-block pool on 98.96% of steps
    (mean extra pool edges 0.0164).  Once the partition is discrete, the
    partition-dependent exclusions are redundant and D's rule reduces to
    "add every non-successor edge out of `z`".

### 6.3 Stabilisation and censoring

- Partition stabilisation: mean 2.30 (C), 2.36 (CR), 3.24 (D); maximum 34 (D).
  It occurs within 4 steps in 87/100 D runs, 98/100 CR runs.
- Graph stabilisation: **not observed**.  The graph changes at the final
  recorded step in 99/100 D runs and 96/100 CR runs.  `graph_stable_at = 100`
  is a censoring boundary, not a stabilisation time.
- The claim "early partition stabilisation relative to graph stabilisation"
  is therefore supported only in the weak form: partitions stabilise early,
  while graph stabilisation is censored at the 100-step horizon.

## 7. Output map

| deliverable | path |
|---|---|
| `EXECUTION_REPORT.md` | workspace root |
| `HYPOTHESIS_RESULTS.md` | workspace root |
| `MODEL_COMPARISON.csv` | workspace root |
| `D_CR_RESULTS.csv` | workspace root |
| `STRUCTURAL_METRICS.csv` | workspace root |
| `STATISTICAL_ANALYSIS.md` | workspace root |
| `MATHEMATICAL_INTERPRETATION.md` | workspace root |
| `reproduce.sh` | workspace root |
| primary raw outputs | `results/primary/experiment_results/` |
| control raw outputs | `results/controls/` |
| supporting tables / `stats.json` | `results/analysis/` |
| run logs | `logs/` |

Verdict: see the end of `HYPOTHESIS_RESULTS.md`.
