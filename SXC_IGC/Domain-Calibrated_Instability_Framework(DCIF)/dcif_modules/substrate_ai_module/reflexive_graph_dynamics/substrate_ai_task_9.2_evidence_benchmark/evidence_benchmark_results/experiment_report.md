# Distributed Evidence Integration Benchmark — Experiment Report

## Research question

Does Model D’s partition-conditioned edge-placement mechanism provide a measurable advantage (or disadvantage) for distributed evidence integration relative to creation-matched random placement (CR), models A/B/C, and a conventional majority-vote gossip baseline (MV)?

## Exact methods

- Substrate: unchanged `one.py` (SHA-256 `3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a`).
- `one.py` unchanged check: **True**.
- Evidence protocol: separate layer (`evidence_benchmark/`); see `benchmark_specification.md`.
- Models: A, B, C, D, CR from substrate; MV = bidirected initial-graph majority-vote message passing.
- Primary comparison: paired D − CR.
- Seeds: 100; streams: init/move/ctrl/evidence/failure/relabel.

## Experimental conditions

| id | n | p | corr | dist | rounds | fail | adv |
|---|---|---|---|---|---|---|---|
| baseline | 12 | 0.7 | independent | balanced | 15 | 0.0 | 0.0 |
| rel_weak | 12 | 0.55 | independent | balanced | 15 | 0.0 | 0.0 |
| rel_strong | 12 | 0.9 | independent | balanced | 15 | 0.0 | 0.0 |
| corr | 12 | 0.7 | correlated | balanced | 15 | 0.0 | 0.0 |
| uneven | 12 | 0.7 | independent | uneven | 15 | 0.0 | 0.0 |
| budget_low | 12 | 0.7 | independent | balanced | 5 | 0.0 | 0.0 |
| budget_high | 12 | 0.7 | independent | balanced | 40 | 0.0 | 0.0 |
| failures | 12 | 0.7 | independent | balanced | 15 | 0.2 | 0.0 |
| adversarial | 12 | 0.7 | independent | balanced | 15 | 0.0 | 0.2 |
| size_small | 8 | 0.7 | independent | balanced | 15 | 0.0 | 0.0 |
| size_large | 20 | 0.7 | independent | balanced | 15 | 0.0 | 0.0 |
| stress_weak_fail | 12 | 0.55 | independent | balanced | 15 | 0.2 | 0.0 |

## Test results

Correctness tests: **13/13 PASS**.

- `E01_no_double_count`: PASS
- `E02_hidden_ground_truth`: PASS
- `E03_no_central_coordinator`: PASS
- `E04_relabelling`: PASS
- `E05_identical_evidence`: PASS
- `E06_d_cr_creation_match`: PASS
- `E07_message_budgets`: PASS
- `E08_propagation_graph`: PASS
- `E09_disconnected`: PASS
- `E10_consensus_distinction`: PASS
- `E11_stream_isolation`: PASS
- `E12_reproducibility`: PASS
- `E13_one_py_preserved`: PASS

## Main findings (baseline condition)

### Mean final fraction correct

| model | mean | std | n |
|---|---|---|---|
| A | 0.8717 | 0.3046 | 100 |
| B | 0.8717 | 0.3046 | 100 |
| C | 0.8717 | 0.3046 | 100 |
| D | 0.8900 | 0.3097 | 100 |
| CR | 0.8883 | 0.3141 | 100 |
| MV | 0.8900 | 0.3145 | 100 |

### Paired D − CR (baseline)

| metric | mean diff | 95% CI | n |
|---|---|---|---|
| frac_correct | 0.0017 | [-0.0023, 0.0057] | 100 |
| agreement_correct | 0.0000 | [0.0000, 0.0000] | 94 |
| time_to_correct_agreement | 0.0500 | [-0.0788, 0.1788] | 100 |
| total_messages | -8.5600 | [-13.7279, -3.3921] | 100 |
| messages_per_correct_node | -0.6883 | [-1.1422, -0.2344] | 100 |
| evidence_coverage | -0.0015 | [-0.0065, 0.0036] | 100 |
| frac_correct_after_failure | 0.0017 | [-0.0023, 0.0057] | 100 |

### Statistical tests (baseline D−CR, Wilcoxon + Holm)

| metric | mean diff | p | Holm sig |
|---|---|---|---|
| frac_correct | 0.0017 | nan | False |
| time_to_correct_agreement | 0.0500 | nan | False |
| messages_per_correct_node | -0.6883 | 0.0019 | True |
| evidence_coverage | -0.0015 | 0.9191 | False |
| agreement_correct | 0.0000 | nan | False |

### D − CR frac_correct across conditions

| condition | mean diff | 95% CI |
|---|---|---|
| baseline | 0.0017 | [-0.0023, 0.0057] |
| rel_weak | -0.0092 | [-0.0264, 0.0080] |
| rel_strong | 0.0000 | [0.0000, 0.0000] |
| corr | 0.0008 | [-0.0008, 0.0025] |
| uneven | 0.0000 | [-0.0046, 0.0046] |
| budget_low | 0.0117 | [-0.0059, 0.0292] |
| budget_high | 0.0008 | [-0.0041, 0.0058] |
| failures | 0.0017 | [-0.0023, 0.0057] |
| adversarial | 0.0025 | [-0.0215, 0.0265] |
| size_small | 0.0125 | [-0.0094, 0.0344] |
| size_large | 0.0005 | [-0.0005, 0.0015] |
| stress_weak_fail | -0.0083 | [-0.0258, 0.0091] |

## Negative findings

- Graph stability / edge creation volume is **not** treated as success; only evidence-integration metrics are interpretive endpoints.
- In 12 conditions, the D−CR accuracy CI included zero.
- D − MV frac_correct mean diff = -0.0000 (CI [-0.0040, 0.0040]).

## Limitations

- Communication uses stored-graph edges, not gate-only routing.
- Round index coupled to graph time index (one schedule among many).
- Stream distinctness ≠ independence.
- Synthetic binary task; no claim about real-world sensing.
- No claim of intelligence, novelty, or practical AI usefulness.

## Reproducibility

```bash
python3 -m evidence_benchmark.run_benchmark --test
python3 -m evidence_benchmark.run_benchmark --full --seeds 100
```

- Output directory: `/home/lenovo/Projects/GI/evidence_benchmark_results`
- Configuration: `configuration.json`
- Infeasible CR seeds: []
- D/CR match failures: []

## Additional comparisons

### Models A/B/C identity on this task

Under the stored-graph communication layer, A, B, and C share the same static edge set `R0` (A/B never modify edges; C refines partitions and gates movement but does not create edges). Consequently their evidence-integration metrics are identical in every seed. Partition refinement alone does not change this protocol’s message routes.

### Communication efficiency (D − CR messages per correct node)

| condition | mean diff | 95% CI |
|---|---|---|
| baseline | -0.6883 | [-1.1422, -0.2344] |
| rel_weak | 0.3645 | [-11.6089, 12.3379] |
| rel_strong | -0.7133 | [-1.1440, -0.2827] |
| corr | -0.5972 | [-0.9586, -0.2358] |
| uneven | -0.2348 | [-0.4567, -0.0129] |
| budget_low | -2.3459 | [-6.6715, 1.9797] |
| budget_high | -0.9800 | [-1.4312, -0.5288] |
| failures | -0.6924 | [-1.1466, -0.2381] |
| adversarial | -7.1005 | [-14.3142, 0.1132] |
| size_small | -2.0636 | [-3.3445, -0.7827] |
| size_large | -0.3823 | [-0.6162, -0.1483] |
| stress_weak_fail | -0.4227 | [-12.4995, 11.6540] |

Negative differences mean D used fewer messages per correctly informed node than CR. Across conditions, CI entirely below 0 in 8/12, above 0 in 0, overlapping 0 in 4.

This is a **communication-cost** difference, not an accuracy advantage. It does not by itself justify claiming that partition-conditioned placement improves evidence integration quality.

### D versus A and MV (baseline)

| pair | metric | mean diff | 95% CI |
|---|---|---|---|
| D-A | frac_correct | 0.0183 | [0.0078, 0.0289] |
| D-A | messages_per_correct_node | 20.5132 | [19.6807, 21.3456] |
| D-A | evidence_coverage | 0.0559 | [0.0411, 0.0707] |
| D-A | total_messages | 254.4700 | [244.2207, 264.7193] |
| D-MV | frac_correct | -0.0000 | [-0.0040, 0.0040] |
| D-MV | messages_per_correct_node | -6.0076 | [-7.1002, -4.9150] |
| D-MV | evidence_coverage | -0.0181 | [-0.0274, -0.0089] |
| D-MV | total_messages | -72.4500 | [-85.9046, -58.9954] |
| D-C | frac_correct | 0.0183 | [0.0078, 0.0289] |
| D-C | messages_per_correct_node | 20.5132 | [19.6807, 21.3456] |
| D-C | evidence_coverage | 0.0559 | [0.0411, 0.0707] |
| D-C | total_messages | 254.4700 | [244.2207, 264.7193] |

### Possible mechanism notes (non-causal claims)

- Where D uses fewer messages than CR at matched creation counts, a plausible mechanism is that D’s candidates are localized at the mover `z_t` and may form shorter bursty routes near the trajectory, whereas CR samples globally from the cross-block pool, producing more diffuse connectivity and more duplicate/wasted forwards. This remains a hypothesis consistent with the metrics, not a proof.
- Accuracy near ceiling under strong reliability (`rel_strong`) limits discriminability; weak-reliability conditions remain inconclusive on accuracy when CIs include 0.

## Hypothesis assessment

**Verdict: mixed — fails to distinguish on accuracy; supports a small communication-cost advantage.**

| Primary question | Assessment |
|---|---|
| Higher final decision accuracy (D vs CR)? | **No.** Mean paired diff near 0; 95% CI includes 0 (or undefined Wilcoxon). Same pattern in 12/12 conditions with CI overlapping 0. |
| Faster correct agreement? | **No.** CI includes 0 (or undefined). |
| Lower communication cost for equivalent accuracy? | **Yes (narrow).** Baseline messages/correct-node CI entirely below 0; Holm-significant where tested. |
| Better resilience after failures? | **No clear advantage.** Failure-condition accuracy CI includes 0. |
| More reliable evidence coverage? | **No.** CI includes 0. |

On final decision accuracy, correct agreement, evidence coverage, and failure resilience, paired D−CR differences are near zero with CIs that include zero (or are exactly zero under ceiling effects). A Holm-significant reduction in messages_per_correct_node and total_messages indicates a small communication-cost advantage for D versus creation-matched CR under several conditions. This does not establish an accuracy advantage for partition-conditioned placement, nor practical AI usefulness.

Relative to static A/B/C, both D and CR (and MV) improve coverage/accuracy somewhat by adding routes; that effect is about *creating edges*, not D’s specific placement rule. Relative to MV, baseline accuracy is indistinguishable when the D−MV CI includes 0.

This benchmark does not establish intelligence, emergent collective computation, or superiority over established distributed algorithms beyond the specific MV gossip baseline under the stated constraints.

