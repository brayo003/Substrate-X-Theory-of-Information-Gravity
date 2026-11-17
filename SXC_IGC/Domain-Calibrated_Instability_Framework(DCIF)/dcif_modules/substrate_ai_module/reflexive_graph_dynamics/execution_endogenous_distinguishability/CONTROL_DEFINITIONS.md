# Additional control definitions (written before execution)

The original `one.py` (revision 9, md5 `9b73b12efc1c43b1a22c99ec2cfac03d`) is
used unchanged.  The controls below are implemented in `controls.py`, which
only calls the public primitives of `one.py` (`generate_instance`,
`pre_draw_uniforms`, `gate_successors`, `apply_movement`, `refine_once`,
`generate_candidates`, `creation_pool`, `gate_partition`,
`consistency_violations`, `edge_affects_refinement`, `run_model_d`).  No model
in `one.py` is modified.

The only reason for these additions is that the four existing models do not
form a complete factorial for the coupling claim, and `CR` matches D on edge
count but not on the *source* of created edges.

## G — gating without adaptive refinement (2x2 factorial cell)

Purpose: supply the missing cell of the 2x2 design

|                | refinement off | refinement on |
|----------------|----------------|---------------|
| gating off     | A              | B             |
| gating on      | G (new)        | C             |

Definition, step for step:

- Same instance `R`, initial partition `P0`, start state `z0`, and the same
  pre-drawn movement uniforms as A/B/C/D for each seed.
- `P_t = P0` for all `t` (no refinement, no splits).
- Movement: `z_{t+1}` is selected from `gate_successors(z_t, R, P0)` by the
  identical uniform rule used in `one.apply_movement`.
- `R` is fixed (no edge creation or removal).
- The gate `gate_partition(R, P0)` is recomputed each step (constant).
- Records have the same schema as A/B/C.

"Gating on" therefore means the gate is applied everywhere the model consults
the relation, exactly as in C (movement and refinement input).  In G only the
refinement is switched off.

## H — both mechanisms present, refinement decoupled from the gate

Purpose: G removes refinement entirely, so G alone cannot tell whether the
*act of coupling* the refinement to the gated relation matters.  H keeps both
mechanisms but removes that coupling: movement is gated, while refinement is
computed on the unrestricted relation `R`, exactly as in B.

Definition, step for step:

- Same instance, `P0`, `z0` and movement uniforms as A/B/C/G/D.
- Movement: `z_{t+1}` selected from `gate_successors(z_t, R, P_t)` by the
  identical uniform rule (gating on).
- Refinement: `P_{t+1} = refine_once(R, P_t)` (unrestricted input; not the
  gate).
- `R` fixed.
- Records have the same schema as A/B/C.

`C` and `H` therefore differ only in whether the refinement sees
`gate_partition(R, P_t)` or `R`.  `C` vs `H` isolates the coupling of
refinement to admissibility; `H` vs `B` isolates the movement gate; `C` vs `B`
is their combination.

## CS — count- and source-matched random control for D

Purpose: `CR` samples uniformly from the *global* creation pool, whereas every
edge D creates originates at the current state `z_t`.  `CS` removes that
confound.  It matches D on (i) the exact per-step number of created edges and
(ii) the source of those edges, but chooses targets uniformly at random among
the eligible cross-block non-edges out of `z_t`.

Definition:

- Exactly the D loop: same instance, `P0`, `z0`, uniforms, movement on
  `gate_successors(z_t, R_t, P_t)`, one round of `refine_once` on the gate,
  the same inactivity removal rule (`removal_age = 5`), and the same
  per-step creation count `n_t = |C_t^D|` taken from the paired D run.
- Creation: draw `n_t` edges uniformly without replacement from
  `pool_z = {(z_t, b) : b != z_t, P_{t+1}(z_t) != P_{t+1}(b), (z_t,b) not in R_t}`.
- Feasibility: `C_t^D` is a subset of `pool_z` by construction of
  `generate_candidates`, so `|pool_z| >= n_t` always holds; no exclusion is
  expected.
- Random stream: `random.Random(seed * 1_000_000 + 11)` (domain-separated
  from init/move/ctrl; independence is not claimed).

## CT — count- and quotient-topology-matched random control for D

Purpose: a genuine topology-matched control, as opposed to the count-only
matching of `CR`.  `CT` reproduces the *multiset of block-level edge types*
created by D at every step and randomises only which concrete state pair
realises each block-level edge.

Definition:

- Same loop and matched per-step count as D/CS.
- For step `t`, take the edges created by the paired D run and map each edge
  `(a,b)` to the block pair `(P_{t+1}.block_of(a), P_{t+1}.block_of(b))`.
- Let `k_{(u,v)}` be the multiplicity of each block pair in that multiset.
  From `creation_pool(R_t, P_{t+1})`, group eligible edges by their block
  pair and draw `k_{(u,v)}` edges uniformly without replacement from each
  group.
- Feasibility: D's own created edges are distinct members of the pool in
  their respective block-pair groups, so each group contains at least
  `k_{(u,v)}` eligible edges; no exclusion is expected.  If this invariant
  ever failed, the seed would be recorded as excluded rather than patched.
- Random stream: `random.Random(seed * 1_000_000 + 12)`.

## What each control can and cannot establish

- `CR` is an exact **edge-count** control only.  It is not a topology
  control, and differences between D and CR may be produced by the
  source-concentration difference alone.
- `CS` isolates the target-selection rule under matched count and matched
  source.  A D-vs-CS difference cannot be attributed to source concentration.
- `CT` isolates concrete target choice under matched count and matched
  quotient-level topology.  A D-vs-CT difference at the quotient level cannot
  be attributed to a different block-level edge-type mix; it can still be
  attributed to finer-grained placement inside blocks.
- None of these controls changes the definitions of A/B/C/D/CR, and none is
  described as a "topology control" unless it actually matches topology.

## Observed feasibility addendum (added after the first control run)

The pre-run feasibility argument for CS/CT considered the paired D state and
graph.  In execution the control's own trajectory can diverge from D's, and
D's per-step count `n_t` is then requested at a different state/graph.  Under
that post-treatment divergence the matched placement can be infeasible:

- CS: 21/100 seeds excluded (source pool at the control's state smaller than
  `n_t`).
- CT: 23/100 seeds excluded (a required block pair has no eligible pool edge
  in the control's graph).

Exclusions are recorded, not patched.  The completed CS/CT runs are reported
separately and are not pooled with D.  No definition above was changed.
