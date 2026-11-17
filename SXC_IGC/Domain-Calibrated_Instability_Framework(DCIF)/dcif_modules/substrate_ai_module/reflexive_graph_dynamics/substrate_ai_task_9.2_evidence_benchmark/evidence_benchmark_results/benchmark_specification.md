# Distributed Evidence Integration Benchmark — Specification (v1)

## Research question

Does Model D’s partition-conditioned edge-placement rule improve distributed
evidence integration relative to a creation-count-matched random control (CR)
and relative to models A, B, C and a conventional majority-vote baseline (MV)?

A negative or inconclusive result is an acceptable scientific outcome.

## Preserved substrate (unchanged)

| Item | Value |
|---|---|
| Source file | `one.py` (not modified by this benchmark) |
| Source SHA-256 | `3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a` |
| Source MD5 | `9b73b12efc1c43b1a22c99ec2cfac03d` |
| Latest graph experiment | `experiment_results4/` (100 seeds, 100 steps, 12 states, cap=None, removal_age=5) |
| Tests | T00–T17, A1–A4 (24/24 PASS) |

This benchmark is a **separate layer**. It imports model runners from `one.py`
and never alters their equations, candidate rules, removal policy, CR sampling,
or random-stream offsets `{init:1, move:2, ctrl:3}`.

## How models connect to the evidence task

1. For each paired seed, generate the same initial `(R0, P0, z0)` via
   `generate_instance` and the same move uniforms via `pre_draw_uniforms`.
2. Run A, B, C, D, and CR exactly as in `one.py`.
3. Extract the directed communication graph sequence
   `G_0 = R0`, `G_{t+1}` = post-step stored graph from each `StepRecord`.
4. Run the evidence-propagation protocol **on top of** that sequence.
   Partition dynamics affect the protocol only insofar as they already shaped
   the graphs (via D/CR creation and C/D/CR gated movement/refinement).
5. MV uses the **same** evidence, budgets, and failure schedule, but always
   communicates on the **bidirected** initial graph (conventional gossip),
   ignoring model dynamics.

No model definition is changed. No new edge-placement rule is injected into D.

## Evidence-generation process

Hidden ground truth `y ∈ {0,1}` is drawn from the evidence stream and is
accessible only to the evaluator.

For each node `i`:

- Draw a local evidence bit `b_i` that equals `y` with reliability `p`
  (Bernoulli noise of rate `1-p`), unless an experimental condition overrides.
- Assign an opaque token `τ_i = SHA256(seed ‖ "ev" ‖ serial)[:16]`. Tokens do
  **not** encode node labels.
- Attach a numeric weight `w_i` (true reliability logit magnitude).

Conditions:

| Factor | Levels | Concrete values | Rationale |
|---|---|---|---|
| Network size | small / medium / large | `n∈{8,12,20}`, `edge_p=0.25`, `blocks=3` | Medium matches the preserved experiment; 8 and 20 probe scale without leaving the sparse directed regime. |
| Reliability | weak / moderate / strong | `p∈{0.55,0.70,0.90}` | Weak is near chance; strong is easy; moderate is the primary operating point. |
| Correlation | independent / correlated | indep: independent flips; corr: one shared error bit applied to a random half of nodes | Separates redundant vs diverse evidence. |
| Distribution | balanced / uneven | balanced: every node has one item at `p`; uneven: 25% of nodes hold all evidence at `p`, others hold none | Tests whether placement helps reach under-informed regions. |
| Budget | low / medium / high | rounds `{5,15,40}` with per-round per-node send cap `{1,2,4}` | Couples to graph_steps=40; low stresses scarcity. |
| Failures | none / controlled | none; or remove 20% of non-R0 dynamic-eligible edges at round `⌊R/2⌋` with a fixed failure stream | Exogenous; identical schedule across models. |
| Adversarial | off / on | off; or 20% of nodes emit flipped bits with high weight | Separate condition, never mixed into ordinary noise. |

**Primary baseline condition (locked before results):**
`n=12, p=0.70, independent, balanced, medium budget, no failures, no adversarial`.

Parameter values are fixed in `configuration.json` before the full run.
Changing them requires a new condition id / version, not silent retuning.

## Message-propagation process

Each node maintains:

- `known`: map `token → (bit, weight)` of unique evidence items (no double count).
- outbound queue of newly acquired tokens.

Each communication round `r = 0 … R-1`:

1. Topology = `G_r` for dynamic models (clamped to last available step);
   for MV, topology = bidirected `R0` (failures applied identically).
2. For each node, up to `send_cap` pending tokens are forwarded along each
   outgoing edge as messages `{token, bit, weight}` (no source field).
3. Receiver accepts a token iff not already in `known` (duplicate suppressed).
4. Global message counter increments per send; stop early if `max_messages`
   exhausted or no new deliveries occur for a full round after the first.

Stopping: `min(rounds exhausted, message budget exhausted, quiescence)`.

## Local decision rule

After each round (and at termination), for each node:

```
score = Σ_{(τ,b,w) in known} (2b−1) · w
decision = 1 if score > 0; 0 if score < 0; undecided if score == 0 or known empty
```

Collective decision = majority among decided nodes; undecided if tie or none
decided. Incorrect consensus is recorded separately from correct consensus.

There is **no** central answer generator. The hidden `y` is never passed into
node state, messages, or decision code paths.

## Anonymity definition (exact)

| Kind | Implemented? | Mechanism |
|---|---|---|
| Node-label anonymity | Yes | Protocol logic never branches on numeric labels except as opaque dict keys. Relabelling test: random permutation of node ids on `(R0,P0,evidence assignment)`; paired metrics must match within floating tolerance / identical for discrete counts when streams are correspondingly remapped. |
| Evidence-provenance anonymity | Yes | Messages carry opaque tokens only; no source id field. Duplicate suppression uses tokens, not origins. |
| Evaluator omniscience | Evaluator-only | Ground truth and source maps exist only in evaluator structures, never in node/protocol APIs. |

Claim: integer names alone do **not** constitute anonymity; the relabelling
and token tests do.

## Controls

Paired seeds: all of A, B, C, D, CR, MV share for each seed:

- same `R0`, `P0`, `z0`, move uniforms
- same hidden `y`, local evidence, reliability, correlation structure
- same message/round budgets and failure schedule

D vs CR: exact per-step creation-count match via existing
`run_control_random_matched`; removal counts reported separately; infeasible
CR seeds recorded explicitly and excluded from D−CR paired stats only.

### Random streams (domain-separated)

| Domain | Offset | Used by |
|---|---|---|
| init | `s*1e6+1` | `one.py` instance generation |
| move | `s*1e6+2` | `one.py` movement |
| ctrl | `s*1e6+3` | `one.py` CR sampling |
| evidence | `s*1e6+4` | ground truth, evidence bits, tokens |
| failure | `s*1e6+5` | exogenous edge failures |
| relabel | `s*1e6+6` | anonymity permutation tests |

Independence is **not** claimed; distinctness is.

## Metrics

Accuracy: fraction correct / incorrect / undecided; collective accuracy;
accuracy-over-time.

Communication: messages sent; unique evidence delivered; duplicates prevented;
rounds to decision; messages per correctly informed node.

Agreement: fraction agreeing; correct vs incorrect agreement; time to
agreement; agreement maintained at end.

Robustness: post-failure accuracy; recovery rounds; reach into weak components;
correlated / adversarial performance.

Network: final `|E|`, `|P|`; reachability from evidence sources; created /
removed edges; created edges that carried ≥1 new delivery; created edges that
delivered evidence used in a correct final local decision.

## Primary comparisons

1. D − CR (primary): paired differences on accuracy, time-to-correct-agreement,
   messages-per-correct-node, post-failure accuracy, evidence coverage.
2. D − A, D − B, D − C, D − MV.

Inference: paired mean differences, 95% bootstrap CIs (or normal approx when
n≥100), Wilcoxon signed-rank where applicable. Multiple comparisons across the
five primary D−CR endpoints: Holm–Bonferroni.

Advantage is declared only if effect direction is consistent, CI excludes 0
(or adjusted p < 0.05), and the effect appears in more than one condition—
not merely because one mean is larger.

## Assumptions that cannot be fully justified

1. Stored-graph edges are the right communication channels (gate edges are
   movement-only in the substrate). Alternative: gate-only routing — not used.
2. Coupling communication round `r` to graph time `r` is one of many schedules.
3. Weight-aware signed voting is a conventional aggregator, not claimed optimal.
4. Finite-precision movement selection inherits `one.py`’s approximation note.
5. Stream distinctness ≠ probabilistic independence.

## Deliverables

Separate package `evidence_benchmark/`, output directory
`evidence_benchmark_results/`, plus the files required by the task brief.
Previous `experiment_results4/` outputs remain untouched.
