# EXP2 AUDIT REPORT
**Date:** 2026-11-13  
**Scope:** Pre-implementation audit for controlled spectral substrate coordination experiment  
**Auditor:** Kiro (direct code inspection, no reliance on prior reports)

---

## 1. What exists and is correct

### Physical field solver — `domains/physical_field/physical_field_dynamics.py`

The telegraph equation solver is correct and verified:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
```

Explicit Euler integration: `v_new = v + dt*(c²∇²s - v/τ)`, `s_new = s + dt*v_new`.  
Finite difference Laplacian with zero-flux boundary.  
`initialize_field_state`, `evolve_field`, `apply_perturbation` all function correctly.  
**Performance:** 0.6ms/tick for 30×30 grid. `apply_perturbation` takes 3.2ms (Python loop over 900 points — vectorizable but not blocking).

### Spectral observable — `compute_spectral_transport_observable`

Correct. Background subtraction (δs = s − ⟨s⟩), DC exclusion, epsilon-tolerance critical band (|D(k)| ≤ 0.05), C_spectral = f_prop − f_over ∈ [−1,+1] all correctly implemented and verified by 6/6 modal tests.

### SubstrateState — `domains/physical_field/substrate_state.py`

Clean authoritative interface. `from_spectral_observable()`, `to_agent_context()`, `coordination_capacity`, and `decay_timescale` all correct.

### Modal discriminant

`D(k) = 4c²τ²|k|² − 1` correctly implemented. `compute_theoretical_q` is correctly marked DEPRECATED and separated from the spectral observable.

### Existing infrastructure reusable in EXP2

- `initialize_field_state`, `evolve_field`, `compute_spectral_transport_observable`, `apply_perturbation` — use unchanged.
- `SubstrateState.from_spectral_observable()`, `to_agent_context()` — use unchanged.
- Phase 10 `phase10_analysis.py` statistical primitives — reuse for EXP2 analysis.
- Phase 10 `phase10_intervention_tests.py` decision-function tests — extend for EXP2.

---

## 2. The core problem: why Phase 10 found no advantage

This is the most important finding from direct measurement.

**Measured signal dynamics at tau=3.0 (Phase 10 operating point):**

```
C_spectral over 80 ticks: mean=+0.012, std=0.128, min=-0.185, max=+0.207
Trajectory: +0.207 → smoothly decays to -0.185 (monotone drift, not reactive)
```

**At tau=1.5 (transition zone):**

```
C_spectral: mean=-0.724, std=0.149 (similarly monotone drift, all overdamped)
```

The signal is not reactive to coordination events. It reflects the **field's relaxation history** from its initial perturbations. Agents perturbing the field with hunger/stress amplitudes (Phase 10 implementation) produce small perturbations (amplitude ~0.3–0.6) that do not measurably change the spectral regime at the grid scale.

**Root cause: no meaningful bidirectional coupling.**

In Phase 10, agents perturb the field with `amplitude = (hunger+stress)/2 × 1.5`. When an agent cooperates, its stress drops, so its perturbation amplitude drops. But:
1. The perturbation is small relative to the initial bumps (amplitude 2–4).
2. Five agents cannot produce enough field variation to shift C_spectral detectably.
3. The spectral observable is not sensitive to the *type* of action (cooperate vs forage) — only to the total perturbation energy.

**The correct coupling mechanism:**

Agents must perturb the field differently depending on their coordination *state*, and the perturbation must be large enough relative to field noise to produce a detectable spectral signature. Specifically:
- When N≥3 agents coordinate simultaneously on the same location, inject a **coherent** (spatially concentrated, large amplitude) perturbation — this produces high-k coherent modes → C_spectral rises.
- When agents act independently, inject **dispersed** (spread across agent locations) perturbations — these produce low-k or overdamped modes → C_spectral stays low.

This creates genuine temporal structure in C_spectral: it rises during coordination episodes and falls between them.

---

## 3. Missing components for EXP2

### 3.1 — CoordinationTaskEnvironment (not implemented anywhere)

Need: A task environment with:
- Coordination-dependent tasks: appear at scheduled intervals (schedule hidden from agents), require ≥3 agents in same zone within same tick, yield collective reward.
- Independent tasks: always available, yield smaller reward per agent, no cooperation needed.
- The schedule must be generated from an RNG stream **separate** from field and agent RNGs.
- Agents observe task availability (what tasks are open) but NOT the coordination schedule (not how many more will come or when).

### 3.2 — Bidirectional field coupling (not implemented in Phase 10)

Need: When a coordination event succeeds (≥3 agents committed to cooperate in the same tick):
- Apply a **coherent concentrated perturbation** at the coordination zone center with amplitude proportional to participating agent count.
- This pushes high-k fluctuation power → C_spectral rises temporarily.

When no coordination occurs:
- Apply smaller dispersed perturbations from individual agent actions.
- Field relaxes → C_spectral drifts back down.

This is the mechanism by which C_spectral becomes a **record of past coordination** that agents can use to anticipate future coordination opportunities.

### 3.3 — Five experimental conditions (Phase 10 had four, mismatched)

Need:
- **baseline**: no substrate signal; pure need+task-availability decision
- **spectral**: actual field-derived C_spectral
- **time_reversed**: actual spectral series reversed (tick i gets signal from tick n-1-i)
- **shuffled**: spectral series shuffled randomly (same marginal, destroyed timing)
- **constant**: constant signal = mean of spectral series for that trial (no temporal structure, no marginal distribution preserved)

Phase 10 had: baseline, legacy_q, spectral, ablation (time-reversal). Needs restructuring.

### 3.4 — Coordination-dependent task completion as primary metric

Phase 10 measured mean_final_hunger. That is a *needs* metric, not a *task* metric. For this experiment, the primary metric must be **coordination task completion rate**: fraction of coordination task opportunities where ≥3 agents committed to cooperate within the task window.

### 3.5 — Predictive-information analysis

Need: Per-tick records of C_spectral and coordination demand, with lead-lag cross-correlation analysis to test whether C_spectral predicts upcoming task demand.

### 3.6 — Experiment ID system and separated RNG streams

Phase 10 identified trials only by seed. Need a proper experiment ID system: `{run_type}_{scenario}_{condition}_{seed}_{timestamp}`.

---

## 4. Files to create (new)

| File | Purpose |
|------|---------|
| `exp2_environment.py` | CoordinationTaskEnvironment with hidden schedule, task rewards, observation interface |
| `exp2_runner.py` | 5-condition experiment runner, paired seeds, isolated RNGs, per-tick records, experiment IDs |
| `exp2_diagnostics.py` | 12 diagnostic tests |
| `exp2_analysis.py` | Statistical analysis + lead-lag analysis |
| `EXP2_AUDIT.md` | This file |
| `EXP2_RESULTS.md` | Results report (after running) |

## 5. Files to use unchanged

| File | Usage |
|------|-------|
| `domains/physical_field/physical_field_dynamics.py` | All functions |
| `domains/physical_field/physical_field_models.py` | All dataclasses |
| `domains/physical_field/substrate_state.py` | SubstrateState |
| `domains/physical_field/test_modal_validation.py` | Regression suite |
| `phase10_analysis.py` | Statistical primitives (import selectively) |

## 6. Files to leave unmodified

All existing Phase 10 output files, `experiment_runner.py`, and all other sim_world infrastructure. EXP2 is a new self-contained experiment in new files.

---

## 7. Risks to experimental validity

### Risk 1 (Critical): Signal not varying at chosen tau
**Mitigation:** Use tau values in the range 2.0–4.0 and use strong bidirectional coupling. Diagnostic test 7 must verify C_spectral std > 0.05 across a run.

### Risk 2 (Critical): Coordination schedule leaking to agents
**Mitigation:** The environment schedule is generated from a separate RNG, stored internally, never passed to agent context. Diagnostic test 6 verifies this.

### Risk 3 (High): Ablation having wrong marginal distribution
**Mitigation:** Time-reversal uses the same spectral time series from the same trial. Shuffled uses the same values in random order. Constant uses the trial mean. All preserve the value distribution.

### Risk 4 (High): Coherent perturbation introducing information leakage
**Mitigation:** The coherent perturbation is applied AFTER agent decisions in the same tick. Agents cannot observe the resulting field state until the next tick. The field evolves one step between the perturbation and the next observation. This is explicitly verified in diagnostic test 9.

### Risk 5 (Medium): apply_perturbation Python loop performance with 5 agents × N ticks
**Measured:** 3.2ms per call at 30×30 grid. With 5 agents + 1 coordination perturbation = 6 calls per tick × 80 ticks = 480 calls per trial = 1.5s per trial. At 30 trials × 5 conditions = 150 trials: ~225 seconds. Acceptable.

### Risk 6 (Medium): C_spectral may not carry predictive (lead-time) information
This is a research question, not a defect. If C_spectral only tracks contemporaneous coordination (lagging indicator), that is a valid negative result. Distinguish explicitly in reporting.
