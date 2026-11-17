# Distributed Evidence Integration Benchmark — Experiment Report (v2)

## Research question

Does Model D’s partition-conditioned edge-placement mechanism provide a measurable advantage (or disadvantage) for distributed evidence integration relative to creation-matched random placement (CR), models A/B/C, and conventional baselines STATIC / MV_W / MV_U?

## Exact methods

- **Stage-1 architecture:** substrate dynamics are run first; evidence propagation uses the **precomputed** graph sequence. Evidence does **not** drive edge creation. This is not evidence-driven adaptation.
- Substrate: unchanged `one.py` (SHA-256 `3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a`).
- `one.py` unchanged: **True**.
- Protocol/evaluator split: network sees `NetworkEvidenceView` only; ground truth is evaluator-only.
- Models: A, B, C, D, CR; baselines STATIC (directed R0), MV_W (bidirected R0 + weighted vote), MV_U (bidirected R0 + unweighted majority).
- Primary comparison: paired D − CR on baseline.
- Pre-registered NI margin on `frac_correct`: δ = 0.05 (absolute fraction of nodes).
- Seeds: 100.
- Prior v1 outputs preserved in `evidence_benchmark_results/`.

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

Correctness tests: **21/21 PASS**.

- `E01_no_double_count`: PASS
- `E02_hidden_ground_truth`: PASS
- `E03_no_central_coordinator`: PASS
- `E04_relabelling`: PASS
- `E04b_relabel_budget`: PASS
- `E04c_relabel_fail_dyn`: PASS
- `E05_identical_evidence`: PASS
- `E06_d_cr_creation_match`: PASS
- `E07_message_budgets`: PASS
- `E08_propagation_graph`: PASS
- `E09_disconnected`: PASS
- `E10_consensus_distinction`: PASS
- `E10b_agreement_ties`: PASS
- `E11_stream_isolation`: PASS
- `E12_reproducibility`: PASS
- `E13_one_py_preserved`: PASS
- `E14_edge_attribution`: PASS
- `E15_baselines_mv_u_static`: PASS
- `E16_correlation_quantified`: PASS
- `E17_ni_tost_helpers`: PASS
- `E18_v1_preserved`: PASS

## Main findings (baseline, primary)

### Mean final fraction correct

| model | mean | std | n |
|---|---|---|---|
| A | 0.8717 | 0.3046 | 100 |
| B | 0.8717 | 0.3046 | 100 |
| C | 0.8717 | 0.3046 | 100 |
| D | 0.8900 | 0.3097 | 100 |
| CR | 0.8883 | 0.3141 | 100 |
| STATIC | 0.8717 | 0.3046 | 100 |
| MV_W | 0.8900 | 0.3145 | 100 |
| MV_U | 0.8900 | 0.3145 | 100 |

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

### Primary superiority tests (Wilcoxon + Holm)

| metric | mean diff | p | Holm sig |
|---|---|---|---|
| frac_correct | 0.0017 | nan | False |
| time_to_correct_agreement | 0.0500 | nan | False |
| messages_per_correct_node | -0.6883 | 0.0019 | True |
| evidence_coverage | -0.0015 | 0.9191 | False |
| agreement_correct | 0.0000 | nan | False |

### Non-inferiority / equivalence on accuracy (pre-registered)

- Margin δ = 0.05 on mean paired `frac_correct` (D − CR).
- NI test (H₀: mean ≤ −δ): p = 0.0000; noninferior = **True**.
- TOST equivalence (±δ): p_lower = 0.0000, p_upper = 0.0000; equivalent = **True**.
- A CI that contains zero is **not** treated as proof of equivalence.

## Exploratory: D − CR frac_correct across conditions

*Not primary confirmatory tests.*

| condition | mean diff | 95% CI |
|---|---|---|
| baseline | 0.0017 | [-0.0023, 0.0057] |
| rel_weak | -0.0133 | [-0.0302, 0.0035] |
| rel_strong | 0.0000 | [0.0000, 0.0000] |
| corr | -0.0067 | [-0.0232, 0.0099] |
| uneven | 0.0000 | [-0.0046, 0.0046] |
| budget_low | 0.0117 | [-0.0059, 0.0292] |
| budget_high | 0.0008 | [-0.0041, 0.0058] |
| failures | 0.0017 | [-0.0023, 0.0057] |
| adversarial | 0.0025 | [-0.0215, 0.0265] |
| size_small | 0.0125 | [-0.0094, 0.0344] |
| size_large | 0.0005 | [-0.0005, 0.0015] |
| stress_weak_fail | -0.0125 | [-0.0293, 0.0043] |

## Exploratory: communication cost (D − CR messages/correct)

| condition | mean diff | 95% CI |
|---|---|---|
| baseline | -0.6883 | [-1.1422, -0.2344] |
| rel_weak | 9.0330 | [-9.9327, 27.9986] |
| rel_strong | -0.7133 | [-1.1440, -0.2827] |
| corr | -1.9650 | [-4.4413, 0.5113] |
| uneven | -0.2348 | [-0.4567, -0.0129] |
| budget_low | -2.3459 | [-6.6715, 1.9797] |
| budget_high | -0.9800 | [-1.4312, -0.5288] |
| failures | -0.6924 | [-1.1466, -0.2381] |
| adversarial | -7.1005 | [-14.3142, 0.1132] |
| size_small | -2.0636 | [-3.3445, -0.7827] |
| size_large | -0.3823 | [-0.6162, -0.1483] |
| stress_weak_fail | 8.5269 | [-10.3556, 27.4093] |

## Evidence correlation diagnostics

| condition | setting | empirical mean pairwise bit corr |
|---|---|---|
| baseline | independent | -0.0909 |
| rel_weak | independent | -0.0909 |
| rel_strong | independent | 0.1818 |
| corr | correlated | -0.0255 |
| uneven | independent | 0.0550 |
| budget_low | independent | -0.0909 |
| budget_high | independent | -0.0909 |
| failures | independent | -0.0909 |
| adversarial | independent | -0.0909 |
| size_small | independent | -0.0514 |
| size_large | independent | -0.0526 |
| stress_weak_fail | independent | -0.0909 |

The decision rule remains a naive weighted/unweighted vote that treats items as independent; correlated conditions probe robustness to that misspecification.

## Hypothesis assessment (demonstrated vs not demonstrated)

| Question | Assessment |
|---|---|
| Better decision accuracy (D vs CR)? | **Non-inferior at δ** (not superior). |
| Equivalence of accuracy at ±δ? | **Yes (TOST).** |
| Faster correct agreement? | **Not demonstrated** on primary test. |
| Lower communication cost? | **Supported (primary Holm; lower messages/correct).** |
| Better evidence coverage? | **Not demonstrated** on primary test. |
| Greater resilience to failures? | **Not demonstrated** (exploratory failures contrast). |

**Verdict: non-inferior on accuracy; supports lower communication cost.**

### Separated claims

**Demonstrated (primary analysis):** see table above.

**Hypotheses / exploratory only:** mechanism stories about localized vs diffuse edge placement; condition-level patterns outside baseline primary tests; any reading of CI∋0 as “equal performance.”

## Limitations

- Stage-1 only: precomputed graphs, not online evidence-driven rewiring.
- Communication uses stored-graph edges, not gate-only routing.
- Naive vote ignores dependence under correlated evidence.
- Stream distinctness ≠ independence.
- No claim of intelligence, novelty, or practical AI usefulness.

## Reproducibility

```bash
python3 -m evidence_benchmark --test
python3 -m evidence_benchmark --full --seeds 100
```

- Output: `/home/lenovo/Projects/GI/evidence_benchmark_results_v2`
- Audit: `evidence_benchmark/AUDIT_REPORT.md`
- Infeasible CR: []
- D/CR match failures: []

