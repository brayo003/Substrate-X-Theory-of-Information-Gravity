# Evidence Benchmark v1 — Audit Report

**Date:** 2026-11-14  
**Scope:** `evidence_benchmark/` only. `one.py` and `experiment_results4/` untouched.  
**Prior results:** `evidence_benchmark_results/` preserved as v1 archive.  
**Corrected output target:** `evidence_benchmark_results_v2/`

---

## Defect catalogue

### D1 — Ground truth used inside the protocol layer

| Field | Detail |
|---|---|
| **Location** | `protocol.py` `run_protocol`: `y = bundle.ground_truth` (≈L140); `_agreement_stats(states, y)` called each round (≈L165–223); `edges_helping_correct` uses `st.decision == y` (≈L241–247). `experiment.py` passes full `EvidenceBundle` (including GT) into `run_protocol`. |
| **Why it matters** | Correctness metrics and attribution are computed *inside* the network simulation from the hidden label. The network API therefore receives an object that contains ground truth. Even if nodes do not read `y` for decisions, isolation is incomplete: evaluator and simulator are not separated, and a regression could wire `y` into decisions unnoticed. |
| **Proposed correction** | Split inputs: protocol accepts only a `NetworkEvidenceView` (local items / tokens / bits / weights; no GT). Protocol returns decisions, message counts, deliveries, and raw time-indexed delivery events. A separate `evaluator.py` computes accuracy / agreement-vs-truth / attribution using GT. |
| **Tests** | (a) Protocol callable without GT object. (b) Introspect protocol inputs: no `ground_truth` field reachable. (c) Existing decision-rule signature check retained. |

### D2 — Label-dependent global message-budget truncation

| Field | Detail |
|---|---|
| **Location** | `protocol.py` ≈L186–199: `planned` built by iterating `sorted(send_plan.keys(), key=label)` and `sorted(G.successors(u), key=label)`; budget truncates this ordered list. Relabel test (`tests.py` `test_relabelling_statistical_equivalence`) uses moderate budgets that often do not bind. |
| **Why it matters** | Under a tight `max_messages`, which messages execute depends on numeric labels. Relabelled isomorphic runs can diverge → anonymity / invariance claim is false under realistic constraints. |
| **Proposed correction** | Process sends in **token-atomic** batches ordered by opaque token (label-free). For each token, either deliver the full planned fanout for that token in the round or skip the token if it would exceed remaining budget. Do not truncate mid-fanout by label order. Extend relabel tests to restrictive budgets, send caps, failures, and dynamic graph sequences. |
| **Tests** | Relabel equivalence under: (1) binding `max_messages`, (2) small `send_cap`, (3) edge failures, (4) dynamic D graph sequence. |

### D3 — Agreement / collective tie handling with undecided nodes

| Field | Detail |
|---|---|
| **Location** | `protocol.py` `_agreement_stats` ≈L86–97: on `counts[0]==counts[1]>0`, `agr_label` is cleared **only if** `counts[0]+counts[1]==n` (all nodes decided). With undecided present, `counts[0] >= counts[1]` leaves `agr_label=0`. |
| **Why it matters** | A 3–3 tie with 2 undecided is reported as agreement on class 0. Ties must not yield a unique collective / agreement label. |
| **Proposed correction** | Whenever `counts[0]==counts[1]`, set `agr_label=None` and `collective=None` (collective already handles this ≈L100). Define `agreement_frac` as the tied decided share / n without assigning a label. |
| **Tests** | Explicit tie with undecided; all-decided tie; clear majority with undecided. |

### D4 — Over-broad `edges_helping_correct` attribution

| Field | Detail |
|---|---|
| **Location** | `protocol.py` ≈L241–247: for each correctly deciding node, every edge that ever carried any token in that node’s `known` is credited — including edges that delivered the token to *other* nodes. |
| **Why it matters** | Inflates “helping” edges; confuses “carried this token somewhere” with “delivered evidence into this correct node.” Causal necessity is stronger still and was never measured. |
| **Proposed correction** | Record per-delivery events `(round, u, v, token)` for first deliveries into `v`. Define: (i) `edges_carrying_evidence` = edges with ≥1 first delivery; (ii) `edges_helping_correct` = edges that first-delivered a token *into* a node whose final decision is correct (evaluator-side). Document that this is contribution-to-evidence, not causal necessity. Optionally report `edges_causally_untested` note. |
| **Tests** | Construct a path where token T traverses e1 then e2 into correct node; only the inbound edge to the correct node (and any inbound first-deliveries to that node) count for that node’s help set. Edge that only delivered T to a wrong/undecided node must not count toward a different correct node. |

### D5 — Misdescribed / incomplete baselines

| Field | Detail |
|---|---|
| **Location** | `graph_bridge.make_mv_timeline`: static **bidirected** R0. Protocol still uses **weighted** `decide_from_known`. Spec/report call this “majority-vote gossip.” Model A already is static directed R0 but is not named as a conventional baseline. |
| **Why it matters** | Readers infer unweighted majority vote and/or a directed static control that was not actually isolated as such. |
| **Proposed correction** | Rename/document existing MV as **bidirected weighted gossip** (`MV_W`). Add **`MV_U`**: same bidirected topology, unweighted majority of known bits (ties → undecided). Add **`STATIC`**: static **directed** R0 + same weighted protocol as A–CR (explicit conventional baseline; may numerically match A). Keep CR creation-count match unchanged. |
| **Tests** | MV_U ignores weights (adversarial heavy wrong bit loses if outnumbered). STATIC graph sequence constant and equals R0. Spec text matches implementation. |

### D6 — Statistical overclaim from “CI contains 0”

| Field | Detail |
|---|---|
| **Location** | `analysis.py` / `experiment_report.md` / `verdict.json`: language equates CI∋0 with “no difference” / “equivalent accuracy.” No pre-registered non-inferiority (NI) or equivalence margin. Condition-level tables treated like primary tests. |
| **Why it matters** | Failure to reject H₀≠0 is not equivalence. Communication-cost “advantage” may be fine as an exploratory or secondary endpoint if clearly labelled; accuracy needs NI/equivalence framing. |
| **Proposed correction** | Pre-register primary baseline D−CR tests. Fix NI margin **before** analysis: δ_acc = 0.05 on `frac_correct` (absolute fraction of nodes). Report: (1) superiority Wilcoxon + Holm on primary list; (2) one-sided NI test for D vs CR on accuracy (H₀: mean(D−CR) ≤ −δ); (3) optional two one-sided tests (TOST) for equivalence at ±δ. Label all non-baseline / non-primary contrasts **exploratory**. Rewrite report language: “inconclusive for superiority,” “non-inferior at δ,” or “not shown non-inferior,” never “equivalent” from CI∋0 alone. |
| **Tests** | Unit test of NI/TOST helpers on synthetic paired diffs. Report contains margin and primary vs exploratory sections. |

### D7 — Correlated evidence poorly defined; treated as independent in the decision rule

| Field | Detail |
|---|---|
| **Location** | `evidence.py` ≈L105–117: after independent Bernoulli draws, a shared-error flag may overwrite a random half of holders to all-wrong or all-correct. Spec says “one shared error bit.” Decision rule (`decide_from_known`) sums weights as if independent. No quantified pairwise correlation. |
| **Why it matters** | Dependence structure is ambiguous (mixture of independent pre-draws and block overwrite). Weighted log-odds rule is misspecified under dependence; reporting “correlated condition” without this caveat overstates interpretability. |
| **Proposed correction** | Replace generator with an explicit model, e.g. **equicorrelated latent**: draw `Z ~ Bernoulli(p)` shared; with probability ρ use `b_i=Z` for all holders in a designated group, else independent `Bernoulli(p)` (document exact generative steps). Or simpler locked model: **single shared bit for group G, independent for complement**. Compute and record empirical mean pairwise correlation of bits across seeds in config/analysis. Spec: decision rule remains intentionally **naive weighted vote** (does not whitening / pool dependent evidence); correlated condition tests robustness to that misspecification. |
| **Tests** | Empirical correlation under `correlation="independent"` near 0; under `correlated` significantly higher. Spec formula present. |

### D8 — Architecture wording risks implying evidence-driven adaptation

| Field | Detail |
|---|---|
| **Location** | Spec §“How models connect”; report methods. Implementation already runs substrate first, then protocol on stored graphs (`experiment.py` `_run_one_seed`). |
| **Why it matters** | Saying models “integrate evidence” via partition-conditioned placement can be read as online evidence-driven rewiring. This benchmark is **stage-1: evidence on precomputed topologies**. |
| **Proposed correction** | Explicit “Stage-1 architecture” section: graphs are precomputed; evidence cannot alter edge creation; D’s placement is evaluated only by how the resulting sequence supports message passing. Preserve as valid first-stage design. |
| **Tests** | Documentation review checklist in tests or spec hash note; no behavioural change required beyond docs. |

---

## Non-defects / retained design

- Domain-separated PRNG offsets 4/5/6 vs `one.py` 1/2/3 — OK.
- D/CR creation-count matching via `run_control_random_matched` — preserve.
- Synchronous send snapshot (partial anonymity fix) — keep; extend with D2.
- Double-count prevention via token-keyed `known` — OK.
- v1 results directory — do not overwrite; v2 is additive.

---

## Implementation order (post-audit)

1. Protocol / evaluator split (D1) + agreement fix (D3) + budget ordering (D2) + attribution (D4).  
2. Evidence correlation model (D7).  
3. Baselines MV_W / MV_U / STATIC (D5).  
4. Stats NI/TOST + report language (D6).  
5. Spec architecture (D8).  
6. Expanded tests → smoke → full 100-seed → `evidence_benchmark_results_v2/`.

**Parameter lock:** Same condition matrix and δ_acc=0.05 chosen in this audit *before* v2 analysis. No retuning after seeing v2 results.
