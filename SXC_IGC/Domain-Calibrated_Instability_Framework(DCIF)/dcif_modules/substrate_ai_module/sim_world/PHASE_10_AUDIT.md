# PHASE 10 AUDIT
**Project:** SXC-IGC sim_world  
**Scope:** Spectral substrate advantage experiment — pre-implementation audit  
**Date:** 2026-11-13  

---

## 1. What Phase 9 Established Correctly

Before listing defects, it is important to record what the Phase 9 implementation
got right, so these components are not revisited unnecessarily.

- `compute_spectral_transport_observable` now correctly subtracts the spatial mean
  (`δs = s − ⟨s⟩`) before the FFT, eliminating DC-component domination.
- The critical-band uses an epsilon tolerance (0.05) rather than exact float equality.
- `C_spectral = f_prop − f_over ∈ [−1, +1]` is computed and exposed on
  `SpectralTransportObservable`.
- `SubstrateState` dataclass exists with `from_spectral_observable()`,
  `to_agent_context()`, `coordination_capacity`, and `memory_persistence_factor`.
- `context_builder.py` constructs a full `SubstrateState` from the observable and
  passes `coordination_capacity` and `memory_persistence_factor` into `EntityContext`.
- Modal validation tests pass 6/6: overdamped decay, propagating frequency (3.2%
  error), propagating decay (9.6% error), spectral fractions, near-critical mode,
  mixed-mode field.
- Modal discriminant `D(k) = 4c²τ²|k|² − 1` is correctly separated from the
  local gradient quantity `Q_local = 4c²τ²|∇ln s|² − 1`.

---

## 2. Audit Findings

### Finding 1 — Baseline Is Not a Genuine No-Substrate Control
**Severity: Critical**

**Problem:** The baseline condition sets `signal = 0.0` and passes it to
`Agent.decide(signal)`, which computes `coordination_capacity = 0.5*(1+0.0) = 0.5`.
For a low-stress agent (`stress < 0.6`), the cooperation threshold is
`0.3 + 0.4*(hunger+stress)/2`. With hunger=0.3 and stress=0.2, threshold ≈ 0.40.
`coordination_capacity=0.5 > 0.40`, so baseline agents **cooperate frequently**.

Baseline is not a no-substrate condition. It is a moderate-substrate condition
(equivalent to a substrate with C_spectral=0 exactly). The comparison spectral-vs-
baseline therefore does not test "substrate vs no substrate"; it tests "high-C vs
neutral-C", which is a weaker claim.

**Fix Required:** Baseline agents must use a completely separate decision function
that does not compute `coordination_capacity` at all. Pure need-based rule:
forage if hungry, rest if tired, else explore. No cooperation, no building.

---

### Finding 2 — Ablation Has Incorrect Marginal Distribution
**Severity: Critical**

**Problem:** The ablation pre-runs a *different* field with only 1 agent (not 5),
collects C_spectral values from that trajectory, then shuffles them. This means:
(a) The ablation signals come from a different field history than the spectral
    condition, so their magnitudes and ranges differ.
(b) Using 1 agent instead of 5 produces different perturbation levels and therefore
    different field evolution, further corrupting the marginal distribution.
(c) The random shuffle does not guarantee any particular marginal match.

A valid ablation must preserve the **exact same marginal distribution** as the
spectral condition for that trial while destroying the temporal structure.

**Fix Required:** Pre-compute the spectral signals by running the **same field**
(same seed, same agents) forward, collecting C_spectral at each tick. Then apply
a time-reversal (tick i receives signal from tick n−1−i). This preserves the
exact sequence of values while destroying their temporal relationship to agent state.

---

### Finding 3 — Legacy-Q Normalisation Is Arbitrary
**Severity: High**

**Problem:** `signal = max(-1.0, min(1.0, q_value / 20.0))`. The divisor 20.0
has no principled basis. For the Gaussian-bump field at tick 0 with τ=10,
`q_value ≈ 15`, giving `signal = 0.75`. With τ=0.5, `q_value ≈ −1.0`,
giving `signal = −0.05`. The range is inconsistent across different tau values,
meaning the legacy-Q condition behaves differently not just because of Q but
because of the arbitrary scaling.

**Fix Required:** Use sigmoid normalisation:
`signal = 2.0 / (1.0 + exp(−q_value / 5.0)) − 1.0`
This maps any real Q value to (−1, +1) monotonically and is bounded regardless
of field magnitude.

---

### Finding 4 — No Paired-Seed Mechanism
**Severity: Critical**

**Problem:** All conditions use the same hardcoded 4-bump field at positions
(12,12), (38,12), (12,38), (38,38) with amplitude 3.0 and width 3.0. There is
no per-trial variation. Running 30 "trials" with this setup produces 30 identical
results — the variance across trials is exactly zero. Repeated-trial statistics
are therefore meaningless (you cannot compute a standard deviation on a constant).

**Fix Required:** Each trial must be identified by an integer seed. The seed
controls bump positions, bump amplitudes, and initial agent states via
`numpy.random.default_rng(seed)`. Seeds are `base_seed + trial_index`.
All four conditions within a trial use the **same seed** (same field, same agents)
so that paired statistics are valid.

---

### Finding 5 — Agents Are Fully Deterministic Without Seed Variation
**Severity: Critical** (consequence of Finding 4)

**Problem:** `_make_agents(n)` always produces agents with fixed
`hunger = 0.3 + i*0.05`, `energy = 0.8 − i*0.04`, `stress = 0.2 + i*0.03`.
Without seed variation there is no between-trial variance. This is the same
problem as Finding 4 but specific to agent initial state.

**Fix Required:** Agent initial states must vary per trial, generated from the
trial seed using small uniform noise around the defaults.

---

### Finding 6 — Task Success Metric Is Too Sensitive
**Severity: High**

**Problem:** `task_success` = fraction of agents with `hunger_spike_count == 0`
(hunger never reached 0.75 during the run). Agents receive +0.02 hunger per tick.
Over 50 ticks that is +1.0 baseline hunger accumulation before foraging. Any agent
starting at hunger ≥ 0.25 and doing anything other than active foraging will cross
0.75. At tau=3.0, spectral agents spend ~60% of time cooperating and ~17% foraging,
so almost all cross 0.75, giving task_success ≈ 0% for spectral. At tau=0.3,
agents spend 100% foraging/exploring, giving task_success ≈ 100%.

This metric conflates "agent cooperated" with "agent failed", making it
systematically favour overdamped/baseline conditions regardless of whether agents
are actually performing better.

**Fix Required:** Primary metric must be `mean_final_hunger` (continuous, lower
is better). `task_success` should be retained as a secondary metric but interpreted
as "agents that never needed emergency foraging", not as overall performance.

---

### Finding 7 — Environmental Scenarios Not Implemented
**Severity: High**

**Problem:** Only one fixed field setup exists. The Phase 10 specification requires
three scenarios: stable, dynamic (disturbances), and disrupted (coordination
blocked + field reset). Without multiple scenarios, we cannot determine whether
any substrate advantage is scenario-specific.

**Fix Required:** Implement the three scenarios as separate run modes within the
experiment runner.

---

### Finding 8 — No Statistical Analysis Module
**Severity: High**

**Problem:** No paired-statistics, confidence intervals, effect sizes, or
significance tests exist. Phase 9 reported single-run point estimates only.

**Fix Required:** Implement `phase10_analysis.py`.

---

### Finding 9 — Condition Field Isolation Is Correct But Undocumented
**Severity: Medium (design decision)**

**Note:** Each condition runs its own field, which evolves differently because
agents in different conditions take different actions. This means conditions see
different environmental histories. This is **intentional** — it is part of the
experiment (the substrate couples back to agent behaviour). However, it must be
explicitly documented as a design choice so reviewers do not mistake it for a
confound. The comparison is between "spectral guidance + spectral field evolution"
vs "no guidance + baseline field evolution". This is the correct test.

**Action Required:** Document in protocol. No code change needed.

---

### Finding 10 — No Substrate Intervention Tests
**Severity: Medium**

**Problem:** There is no test that verifies agents actually change their decisions
in response to substrate changes. The existence of a signal path does not prove
it is used.

**Fix Required:** Implement `phase10_intervention_tests.py`.

---

## 3. Summary

| # | Finding | Severity | Required Fix |
|---|---------|----------|-------------|
| 1 | Baseline is moderate-substrate, not no-substrate | Critical | Separate decision function |
| 2 | Ablation has wrong marginal distribution | Critical | Time-reversal of same field signals |
| 3 | Legacy-Q normalisation is arbitrary | High | Sigmoid normalisation |
| 4 | No paired-seed mechanism | Critical | Seeded bump positions + agent states |
| 5 | Agents fully deterministic without seeds | Critical | Seed-derived initial states |
| 6 | Task success metric systematically biased | High | Use mean_final_hunger as primary |
| 7 | Environmental scenarios not implemented | High | Implement 3 scenarios |
| 8 | No statistical analysis | High | Implement phase10_analysis.py |
| 9 | Condition field divergence undocumented | Medium | Document as design choice |
| 10 | No intervention tests | Medium | Implement phase10_intervention_tests.py |

All Critical and High items are corrected before the Phase 10 experiment runs.
