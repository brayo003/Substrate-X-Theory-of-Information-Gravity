# Distributed Evidence Integration Benchmark — Specification (v2)

## Research question

Does Model D’s partition-conditioned edge-placement rule improve distributed
evidence integration relative to a creation-count-matched random control (CR)
and relative to models A, B, C and conventional baselines STATIC, MV_W, MV_U?

A negative or inconclusive result is an acceptable scientific outcome.

## Stage-1 architecture (explicit)

This benchmark is a **first-stage** evaluation:

1. Substrate models A/B/C/D/CR run to completion and produce **precomputed**
   directed graph sequences.
2. An evidence-propagation protocol is then run **on top of** those sequences.
3. Evidence **cannot** alter edge creation, removal, partitions, or movement.

This is **not** evidence-driven graph adaptation. Partition-conditioned
placement is evaluated only by how the resulting stored topology supports
message passing under a fixed protocol.

## Preserved substrate (unchanged)

| Item | Value |
|---|---|
| Source file | `one.py` (not modified) |
| Source SHA-256 | `3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a` |
| Prior graph experiment | `experiment_results4/` |
| Prior evidence v1 results | `evidence_benchmark_results/` (preserved) |
| Corrected evidence output | `evidence_benchmark_results_v2/` |

## Protocol / evaluator separation

- **Protocol** accepts only `NetworkEvidenceView` (local items). It must not
  receive ground truth. It returns decisions, message counts, and delivery events.
- **Evaluator** alone receives ground truth and computes accuracy, agreement
  correctness, and edge attribution.

## Evidence-generation process

Hidden ground truth `y ∈ {0,1}` is evaluator-only.

### Independent model
For each holder i: `P(b_i = y) = p` independently.

### Correlated model (`group_equicorrelated_mixture`)
- Choose random group `G ⊂ H` with `|G| = max(1, ⌊|H|/2⌋)`.
- With probability `ρ = 0.6`, draw shared `S` with `P(S=y)=p` and set
  `b_i = S` for all `i ∈ G`; complement independent.
- Otherwise all holders independent.
- Empirical mean pairwise bit correlation is recorded per condition.
- The decision rule remains a **naive** weighted/unweighted vote that treats
  items as independent (misspecified under dependence by design).

Adversarial sources are a separate condition (flipped bits + weight boost).

## Message-propagation process

Synchronous rounds; token-atomic global budget accounting (label-anonymous):
for each opaque token in sorted order, either send the full planned fanout
or skip the token if it would exceed `max_messages`.

Messages carry `{token, bit, weight}` only (no source id).

## Local decision rules

- **Weighted** (A/B/C/D/CR/STATIC/MV_W):
  `score = Σ (2b−1)·w`; sign → decision; 0 → undecided.
- **Unweighted majority** (MV_U only): majority of known bits; tie → undecided.

Collective / agreement labels: majority among decided nodes; **ties yield no
unique label**, including when undecided nodes remain.

## Baselines

| Id | Topology | Decision |
|---|---|---|
| STATIC | static directed R0 | weighted |
| MV_W | static bidirected R0 | weighted (formerly mislabelled “MV”) |
| MV_U | static bidirected R0 | unweighted majority |
| CR | creation-count-matched random (preserved) | weighted |

## Anonymity

| Kind | Mechanism |
|---|---|
| Node-label | Token-atomic budgets; pending token-sorted; relabel tests under tight budgets, caps, failures, dynamic graphs |
| Provenance | Opaque tokens; no source field |
| GT isolation | Protocol API rejects GT-bearing inputs |

## Pre-registered inference

**Primary condition:** `baseline`.  
**Primary pair:** D − CR.  
**Primary endpoints:** `frac_correct`, `time_to_correct_agreement`,
`messages_per_correct_node`, `evidence_coverage`, `agreement_correct`
(Wilcoxon + Holm–Bonferroni).

**Non-inferiority / equivalence (accuracy):** margin
`δ = 0.05` on mean paired `frac_correct`, locked before v2 analysis.
- NI: H₀ mean(D−CR) ≤ −δ.
- TOST equivalence at ±δ.

A confidence interval containing zero is **not** equivalence.
All non-baseline / non-primary contrasts are **exploratory**.

## Random streams

| Domain | Offset |
|---|---|
| init / move / ctrl | `one.py` 1/2/3 |
| evidence / failure / relabel | 4/5/6 |

Distinctness claimed; independence not claimed.

## Assumptions that cannot be fully justified

1. Stored-graph edges as communication channels.
2. Round index coupled to graph time index.
3. Naive vote under correlated evidence.
4. Contribution-to-evidence edge attribution ≠ causal necessity.
