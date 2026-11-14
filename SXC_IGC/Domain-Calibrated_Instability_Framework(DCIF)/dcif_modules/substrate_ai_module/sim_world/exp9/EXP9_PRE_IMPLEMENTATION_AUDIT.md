# EXP9 Pre-Implementation Audit

**Date:** 2026-11-13  
**Mode:** Repository-grounded inspection before any Task 9 implementation.  
**Isolation:** New directory `sim_world/exp9/` only. Task 6–8 source, reports, configs, and result datasets are not modified.  
**Preservation manifests (this session, before any Task 9 code):**

| Manifest | Path | Verified |
|---|---|---|
| Task 6 | `exp9/task6_checksums_before.txt` | 21/21 OK |
| Task 7 | `exp9/task7_checksums_before.txt` | 17/17 OK |
| Task 8 | `exp9/task8_checksums_before.txt` | 22/22 OK |

---

## 1. Actual active `sim_world` source tree

**Root (active):**  
`/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/sim_world`

Relevant subset (verified on disk):

```
sim_world/
  domains/physical_field/
    physical_field_dynamics.py   # evolve_field, evolve_field_nonlinear, apply_perturbation
    physical_field_models.py     # NonlinearReactionParameters, FieldState, …
    physical_field_domain.py
    test_nonlinear_reaction_telegraph.py
  kernel/world_kernel.py         # full sim orchestration — NOT used by Tasks 6–8 offline experiments
  entities/, simulation/         # general agent/entity loop — NOT the Task 6–8 experiment loop
  exp6_corrected/                # IMMUTABLE Task 6 corrective package
  exp7/                          # IMMUTABLE Task 7 package
  exp8/                          # IMMUTABLE Task 8 package
  exp9/                          # NEW (this task) — isolated
  tests/test_exp8_computational_expressivity.py
  EXP{6,7,8}_*.md, exp{6,7,8}_*.json   # milestone reports/results at root
```

There is **no** top-level `agents/` package. Agent behaviour for Tasks 6–8 lives inside experiment packages (`exp6_corrected/experiment_c.py`, `exp7/hazard_behaviour.py`, `exp8/behavioural_bridge.py`) plus `MemoryBackend` interfaces in `exp6_corrected/architectures.py`.

---

## 2. Exact field solver used in Task 8

**Independently verified call chain:**

1. `exp8/field_core.py` → `FieldSim`
2. `initialize_field_state(...)` → `InformationDensityField`
3. `apply_perturbation(field, PhysicalCoordinate, amp, width)` — additive Gaussian deposit
4. `evolve_field_nonlinear(field, prop, relax, react)` — one explicit Euler step per tick  
   Source: `domains/physical_field/physical_field_dynamics.py`  
   MD5: `37b8972777a20a0976e93fa7dfad1b22`
5. Linear / reaction-off: `react` with `r=a=b=0` → `reaction_params.is_linear` → fall-through to `evolve_field`

**Code-implemented update (lines 279–283 of `physical_field_dynamics.py`):**

```
acceleration = ((c**2)*laplacian + reaction + source - v) / tau
v_new = v + dt * acceleration
s_new = s + dt * v_new
```

Equivalent to \(\tau s_{tt}+s_t = c^2\nabla^2 s + rs + as^2 - bs^3 + S\).

**Docstring vs code:** docstring writes \(c^2\tau\nabla^2 s\); code omits the extra \(\tau\) on the Laplacian. At frozen \(\tau=1\) the forms coincide. Task 9 will **not** change the solver equation; \(\tau=1\) remains the confirmatory operating point (same caveat as Task 8).

**Frozen Task 8 / Task 7 bistable set (reuse, do not retune for Task 9 advantage):**

| Symbol | Value |
|---|---|
| \(r,a,b\) | \(-0.5,\ 2,\ 1\) |
| \(\tau,c,\Delta t\) | \(1,\ 1,\ 0.05\) |
| IC | \(s=0\) |
| Grid | \(30\times30\) on \([0,50]^2\) |
| Deposit width | \(2.0\) |
| High-basin decoder \(\theta\) | \(0.85\) (Task 8); Task 7 used \(0.40\) with dual-kind encoding |

**Boundary:** `compute_laplacian` updates interior only → Dirichlet-like fixed-boundary stencil.

**WorldKernel:** `kernel/world_kernel.py` can construct `NonlinearReactionParameters`, but Tasks 6–8 offline experiments do **not** route field evolution through WorldKernel. Task 9 will likewise use the direct dynamics path unless a documented redesign is required (see §11).

---

## 3. Current agent architecture, observation, action, environment loop

### 3.1 Memory / communication backends (Task 6 corrective — reusable API)

File: `exp6_corrected/architectures.py` (MD5 `f34466945f5a59622dfbeece04e52a62`)

| Backend | Role |
|---|---|
| `IndependentMemory` | Agent-local only |
| `DirectMsgMemory` | Explicit peer messages + TTL |
| `BlackboardMemory` | Shared structured records + stale window |
| `PheromoneMemory` | Scalar evaporating map (conventional) |
| `SubstrateMemory` | Nonlinear/linear field via same dynamics path |

**Agent-facing interface (no GT lists):**

- `deposit(kind, x, y, value, tick, meta=None)`
- `query_at(kind, x, y, tick) → float`
- `list_known(kind, tick) → list[dict]` (empty for spatial-only backends)
- `sample_gradient(...)`, `tick_update(tick)`, `usage()`, `failed()`

Constraints C1–C4 / C3 / C12: backends must not expose undiscovered ground-truth coordinates or a shared task-claim oracle on the decision path.

### 3.2 Task 7 extensions

File: `exp7/memory.py` — reuses Task 6 backends without editing Task 6 files; adds `Exp7SubstrateMemory`, `PositiveHazardBlackboard`, `PositiveHazardDirectMsg` (positive danger-marker encoding for Track A).

### 3.3 Task 8 behavioural bridge (controlled, not autonomous discovery)

File: `exp8/behavioural_bridge.py`

- Two observer deposits at scripted sites; decision agent reads **predefined midpoint** via `activated(sim, *mid)`.
- Modes: `nonlinear_full | linear_telegraph | reaction_off | independent | symbolic`.
- **Privileged relative to Task 9:** readout location is experiment-designed (midpoint of deposit pair), not discovered by agents. Task 9 must **not** reuse this as the primary collective-decision oracle without environmental justification.

### 3.4 Multi-agent environment loops (existing)

| Package | Loop | Observations | Actions |
|---|---|---|---|
| `exp6_corrected/experiment_c.py` | Tick loop; `Agent` pose + energy; private known_* sets | Local sensor radius; memory query at pose | Move toward chosen target; deposit/query via backend |
| `exp7/hazard_behaviour.py` | Corridor hazard Track A | Local hazard discovery; delayed info sharing conditions | Detour / exposure metrics |
| `exp8/behavioural_bridge.py` | Fixed deposits + evolve + one readout | Field local_max at designed ROI | Binary act / no-act |

**General `simulation/` + `entities/`:** present for the broader sim_world, but **not** the path used by Tasks 6–8 computational experiments. Task 9 should build on the offline experiment-agent pattern (MemoryBackend + tick loop), not require WorldKernel, unless §11 redesign is triggered.

---

## 4. Task 8 computational operations and implementation paths

| Op | Path | Mechanism (as reported; not re-run here) |
|---|---|---|
| A Coincidence | `exp8/experiments.py` + `FieldSim` | Overlapping subthreshold Gaussians → bistable high-basin latch; Category 5 |
| B Temporal integration | same | Finite delay window (~5 ticks at amp=0.50, θ=0.85); Category 4 |
| C Spatial (equal mass) | same | Cluster/triangle activate; dispersed/line3 do not; Category 4 |
| D Threshold / hysteresis | same | Forward amp≈0.85; reverse needs ~0.7 neg; Category 5 |
| E Conflict | same | Agree = nonlinear latch; oppose = amplitude cancel (also linear) — Category 2 |
| F Pattern | same | Attractor retention, not multi-feature completion — Category 3 |
| Bridge | `exp8/behavioural_bridge.py` | Causal nl latch vs lin/independent; symbolic still F1=1.0 |

**Ablation knobs already in `FieldSim`:**  
`nonlinear_full | linear_telegraph | reaction_off | no_propagation | no_inertia | readout_only`

**Decoder rule:** `activated` = `local_max(x,y) ≥ θ` on **field values only** (never `deposit_log`).

**Encoding note:** Task 7 AND dual-kind deposits (effective ~2× amp, θ=0.40). Task 8 single-Gaussian, amp=0.50, θ=0.85. Task 9 will inherit Task 8 encoding unless a labelled protocol change is frozen in `exp9_configuration.json`.

---

## 5. Protected Task 6–8 artifact hashes

Recorded in:

- `exp9/task6_checksums_before.txt`
- `exp9/task7_checksums_before.txt`
- `exp9/task8_checksums_before.txt`

Re-verification this session: **all listed hashes match current files** (0 mismatches, 0 missing).

After Task 9 completes, an `*_checksums_after.txt` set will be generated and compared.

---

## 6. Task 6 checksum-manifest coverage discrepancy — reconciliation

### 6.1 Observed inconsistency across prior manifests

| Manifest | File count | Coverage |
|---|---|---|
| `exp7/task6_checksums_{before,after}.txt` | 22 | Corrective + pre-corrective + `__pycache__/exp6_nonlinear_advantage.cpython-310.pyc` |
| `exp8/task6_checksums_before.txt` | 22 | Same as Task 7 |
| `exp8/task6_checksums_after.txt` | **17** | **Corrective package only** — dropped all 4 pre-corrective artifacts **and** the pycache entry |
| `exp9/task6_checksums_before.txt` | **21** | Corrective + pre-corrective; **excludes** `__pycache__` |

### 6.2 Interpretation

1. **Bytecode inclusion was accidental / non-scientific.** The pycache file still exists (`a83c97742743ce5cc8b90d6509e38ff5`) but is not a research deliverable. Task 9 **excludes** it from the protected source set.
2. **Task 8 “after” under-coverage:** comparing only the corrective 17 files left the historical pre-corrective set (`exp6_nonlinear_advantage.py`, `EXP6_NONLINEAR_ADVANTAGE_REPORT.md`, `exp6_pilot_results.json`, `exp6_results.json`) outside the after-check. Those four files remain on disk and match Task 7 / exp8-before / exp9-before hashes — **no evidence they were modified**; the gap was **manifest coverage**, not proven content drift.
3. **Task 9 policy:**  
   - **Primary immutable set:** Task 6 corrective package (17 files).  
   - **Secondary historical set:** 4 pre-corrective artifacts (labelled separately in the before manifest).  
   - **Excluded:** `__pycache__/**`.  
   - After-run comparison will cover the same 21 paths.

### 6.3 Status

Discrepancy **reconciled as a documentation/coverage bug in prior after-manifests**, not as an integrity failure of Task 6 content. No Task 6 files were rewritten to “fix” the manifests.

---

## 7. Task 8 deliverables referenced by its report — availability

The Task 8 report’s evidence index lists four items that earlier conversation text treated as possibly missing. **On-disk verification (this session):**

| Referenced deliverable | Status | MD5 |
|---|---|---|
| `EXP8_PRE_IMPLEMENTATION_AUDIT.md` | **Present** (root) | `fc3ca5e95a6b50337e45353c056c6ab2` |
| `EXP8_THEORETICAL_SPECIFICATION.md` | **Present** (root) | `c6dfa7cc64c0e2f7a4708b0170352d38` |
| `EXP8_LITERATURE_AND_NOVELTY_REVIEW.md` | **Present** (root) | `7fba47dbff25f8ac6081346e33c3495f` |
| `exp8_configuration.json` | **Present** (root) | `d0b4c172368af05b2a46954e6e5fbe5e` |

**No retrospective reconstruction required.** They are included in `exp9/task8_checksums_before.txt`. Prior “missing” status appears to have been a discovery-order / path-search issue, not absent artifacts.

---

## 8. Components Task 9 will reuse (exact paths)

| Component | Reuse mode | Path |
|---|---|---|
| Nonlinear / linear solver | Import only; **do not edit** | `domains/physical_field/physical_field_dynamics.py` |
| Parameter / field models | Import only | `domains/physical_field/physical_field_models.py` |
| FieldSim-style ablation wrapper | **Copy/adapt into `exp9/`** (not edit `exp8/`) | Pattern from `exp8/field_core.py` |
| MemoryBackend + conventional baselines | Import from Task 6 package | `exp6_corrected/architectures.py` |
| Task 7 substrate memory pattern | Import or mirror in `exp9/` | `exp7/memory.py` |
| Bistable parameter freeze | Mirror constants in `exp9/config.py` | Same \(r,a,b,\tau,c,\Delta t\) as Tasks 7–8 |
| Coincidence / hysteresis primitives | **Compose via dynamics**, not by hard-coding Task 8 answers | Dynamics + local deposit/read |
| WorldKernel / entities simulation | **Not required** for planned offline Task 9 suite | — |

Task 9 will **not** modify `exp6_corrected/`, `exp7/`, `exp8/`, root `EXP6*`, `EXP7*`, `EXP8*`, or their JSON result files.

---

## 9. Privileged-information risks to eliminate in Task 9 design

Carried forward as design constraints (formal spec is Phase 1):

1. **No GT target coordinates** in agent observation APIs.
2. **No global field summary** unavailable to ordinary agents.
3. **No predefined readout that is the answer** (Task 8 midpoint ROI is a controlled decoder, not an autonomous discovery mechanism).
4. **Deposit logs** may exist for analysis only; agent policies must not read them.
5. **Baselines** (messaging, blackboard, pheromone, independent, linear field) must receive comparable sensors, budgets, and populations — do not weaken them.
6. Attribute only dynamics-mediated computation to the substrate; agent policy / local memory / messaging remain separately scored.

---

## 10. Architectural gap vs Task 9 primary question

**Established (Tasks 6–8):** field dynamics can latch, integrate briefly, discriminate some spatial arrangements, and drive a **scripted** behavioural bridge.

**Not established:** autonomous agents that **discover** where to deposit/read, compose primitives under noise / async / partial observation, and gain collective task utility vs fair conventional architectures **without** experiment-planted ROIs.

**Gap for Task 9:** need a multi-agent environment loop with local observation radii, movement, deposit/read costs, distractors, and baselines — built in `exp9/` on top of the existing solver and MemoryBackend patterns.

---

## 11. Redesign threshold

If the existing MemoryBackend + offline tick loop cannot support Experiments A–D without major redesign, document the limitation **before** introducing WorldKernel or rewriting the field equation. Current assessment: **offline `exp9` package is sufficient**; WorldKernel integration is not required for the specified experiments.

---

## 12. Audit conclusion — implementation gate

| Gate | Status |
|---|---|
| Active source tree identified | PASS |
| Task 8 solver path identified | PASS |
| Agent/observation/action interfaces identified | PASS |
| Task 8 ops + paths identified | PASS |
| Task 6–8 before checksums recorded & verified | PASS |
| Task 6 coverage discrepancy reconciled | PASS (manifest policy; content intact) |
| Task 8 “missing” deliverables status | PASS (all present; not reconstructed) |
| Implementation may begin | **YES** — only under `exp9/` (+ new tests under `tests/test_exp9_*`) |

**Central research question remains open pending experiments:**  
*Can autonomous agents use the substrate to transform distributed, incomplete, noisy observations into persistent collective decisions that improve coordination or task performance?*

---

## 13. Next documents (Phase 1; no experiment runs yet)

1. `exp9/EXP9_ARCHITECTURAL_SPECIFICATION.md`
2. `exp9/EXP9_EXPERIMENTAL_PROTOCOL.md`
3. `exp9/EXP9_BASELINE_FAIRNESS_AUDIT.md`
4. Numerical validation plan (executed later as `EXP9_NUMERICAL_VALIDATION.md`)
