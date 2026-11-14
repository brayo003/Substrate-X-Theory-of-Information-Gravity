# TASK 9.2 — Source Requirements Audit

**Status:** Read-only dependency audit (no implementation)  
**Date:** 2026-11-13  
**Scope:** Identify exact existing files required to implement and execute Task 9.2 under `dcif_modules/substrate_ai_module/sim_world/`  
**Protocol:** `exp9/TASK92_EXPERIMENTAL_PROTOCOL.md`  
**Constraint:** Existing Task 9 results are **not** Task 9.2 evidence. Frozen field coefficients must not be retuned. \(H=1\) must not be assumed to remove dynamical hysteresis.

---

## Section 1 — Project structure

Relevant tree (paths relative to `sim_world/`):

```
sim_world/
├── exp9/
│   ├── TASK92_EXPERIMENTAL_PROTOCOL.md      # Task 9.2 protocol (authoritative)
│   ├── TASK92_SOURCE_REQUIREMENTS_AUDIT.md  # this document
│   ├── config.py / exp9_configuration.json  # Task 9 freeze (coefficients + agent params)
│   ├── env.py / agents.py / field_backend.py
│   ├── experiments.py / runner.py / statistics.py / numerical.py
│   ├── EXP9_*.md / exp9_*.json              # Task 9 reports/results (context only)
│   └── task{6,7,8}_checksums_*.txt
├── exp8/
│   ├── field_core.py / config.py / experiments.py
│   ├── numerical_validation.py / classify.py / runner.py
│   └── EXP8_* (via parent) + checksums
├── domains/physical_field/
│   ├── physical_field_dynamics.py           # evolve_field_nonlinear, linear fall-through
│   ├── physical_field_models.py             # NonlinearReactionParameters, FieldState, …
│   ├── test_nonlinear_reaction_telegraph.py # includes TestHysteresisVerification
│   ├── test_physical_field.py / test_modal_validation.py
│   └── __init__.py (+ domain side-effect imports)
├── exp6_corrected/statistics.py             # paired t / permutation helpers (optional reuse)
├── tests/test_exp8_*.py / test_exp9_*.py
├── core/contracts.py / core/ids.py          # freeze_value import path
├── exp8_substrate_computational_expressivity.py
├── exp9_autonomous_collective.py
├── EXP8_EXPERIMENTAL_REPORT.md / exp8_results.json / exp8_configuration.json
└── EXP9_EXPERIMENTAL_REPORT.md / exp9_configuration.json / exp9_results.json
```

Import note: `from sim_world.domains.physical_field…` executes `domains/__init__.py` and `physical_field/__init__.py`, pulling additional domain/simulation packages. Those are **runtime import-closure** dependencies, not Task 9.2 scientific surface.

---

## Section 2 — Mandatory source files

Exact relative paths from `sim_world/`, with reason.

### 2.1 Protocol and scientific context

| Path | Role |
|------|------|
| `exp9/TASK92_EXPERIMENTAL_PROTOCOL.md` | Authoritative Task 9.2 design: evidence model, info restrictions, conditions, voting, BA metric, stats, PASS/STOP |
| `exp9/EXP9_EXPERIMENTAL_PROTOCOL.md` | Prior Task 9 protocol (contrast; not 9.2) |
| `exp9/EXP9_EXPERIMENTAL_REPORT.md` | What Task 9 actually measured (landmark \(k^*\) task) |
| `exp9/EXP9_BASELINE_FAIRNESS_AUDIT.md` | Baseline fairness lessons for BB/msg |
| `exp9/EXP9_ARCHITECTURAL_SPECIFICATION.md` | Medium / agent architecture as built |
| `EXP8_EXPERIMENTAL_REPORT.md` | Task 8 latch / coincidence / hysteresis findings |
| `EXP8_THEORETICAL_SPECIFICATION.md` | Field computational claims |
| `NONLINEAR_REACTION_TELEGRAPH_IMPLEMENTATION_REPORT.md` | Solver equation and parameter provenance |

### 2.2 Frozen physical solver

| Path | Role |
|------|------|
| `domains/physical_field/physical_field_dynamics.py` | `initialize_field_state`, `evolve_field`, `evolve_field_nonlinear`, `compute_laplacian`, `apply_perturbation` |
| `domains/physical_field/physical_field_models.py` | `NonlinearReactionParameters`, `PropagationParameters`, `RelaxationParameters`, `InformationDensityField`, `FieldState`, `PhysicalCoordinate` |
| `exp9/config.py` | Frozen coeffs `NL_R/A/B/TAU/C`, `DT`, `DEP_AMP`, `ACTIVATION_THRESH`, `COMMIT_HOLD_TICKS`, grid |
| `exp9/exp9_configuration.json` | Confirmatory freeze record of those coeffs |
| `exp8/config.py` | Independent Task 8 freeze of same \((r,a,b,\tau,c,\Delta t)\) |

### 2.3 Substrate wrappers (linear / nonlinear / deposit / readout)

| Path | Role |
|------|------|
| `exp9/field_backend.py` | `SubstrateMedium`, `DirectMsgMedium`, `BlackboardMedium`, `make_medium`, `UsageStats` |
| `exp8/field_core.py` | `FieldSim` — parallel wrapper; useful for solver-only smoke without agents |

### 2.4 Existing Task 9 agent/env/orchestration (reference + partial reuse)

| Path | Role |
|------|------|
| `exp9/env.py` | `EvidencePatch`, `AgentState`, `World`, `build_world`, `sense_evidence`, `move_toward` |
| `exp9/agents.py` | `agent_step`, `majority_commit`, hold-tick / deposit / msg logic |
| `exp9/experiments.py` | `_run_trial`, Exp A–D, `controlled_coincidence_smoke` |
| `exp9/runner.py` | Pilot/confirm orchestration, JSON artifact writing, acceptance ladder (Task 9 only) |
| `exp9/statistics.py` | `paired_correct_rates`, `bonferroni` |
| `exp9/numerical.py` | dt/grid sensitivity, seed reproducibility, density stability |
| `exp9_autonomous_collective.py` | CLI entry for Task 9 (not 9.2) |

### 2.5 Tests and validation reference

| Path | Role |
|------|------|
| `domains/physical_field/test_nonlinear_reaction_telegraph.py` | Linear limit, bistability, `TestHysteresisVerification`, finite-value protection |
| `domains/physical_field/test_physical_field.py` | Field unit tests |
| `domains/physical_field/test_modal_validation.py` | Modal / telegraph validation |
| `tests/test_exp9_interface.py` | No-\(k^*\)-on-agent, sense API, deposit/read, smoke |
| `tests/test_exp9_ablations.py` | Ablation medium construction / latch smoke |
| `tests/test_exp8_computational_expressivity.py` | Task 8 expressivity tests |
| `exp8/numerical_validation.py` | Task 8 numerical suite |
| `exp8/experiments.py` | `run_D_hysteresis`, amplitude sweeps (field hysteresis proxies) |

### 2.6 Optional shared stats / import-closure

| Path | Role |
|------|------|
| `exp6_corrected/statistics.py` | Paired t-test / SciPy-optional helpers |
| `core/contracts.py`, `core/ids.py` | `freeze_value` import path for models |
| Package inits under `domains/`, `simulation/`, etc. | Required only because of package `__init__` side effects |

---

## Section 3 — Reusable components

**Reusable without modification** (for Task 9.2 implementation that lives in *new* modules, importing these unchanged):

1. **Solver core** — `evolve_field_nonlinear` / `evolve_field` / `apply_perturbation` / `compute_laplacian` / `initialize_field_state` in `physical_field_dynamics.py`; parameter dataclasses in `physical_field_models.py`.
2. **Frozen coefficients** — `NL_R=-0.5`, `NL_A=2.0`, `NL_B=1.0`, `NL_TAU=1.0`, `NL_C=1.0`, `DT=0.05`, grid \(30\times30\) on \([0,50]^2\), `DEPOSIT_WIDTH=2.0`, `READ_RADIUS=5.0`, `ACTIVATION_THRESH=0.85`, `DEP_AMP=0.45`, `COMMIT_HOLD_TICKS=20` from `exp9/config.py` / `exp9_configuration.json` (match Task 8).
3. **Linear substrate** — set `NonlinearReactionParameters(r=0,a=0,b=0)` or `SubstrateMedium("linear_telegraph")` / `FieldSim("linear_telegraph")`.
4. **Deposit/read primitives** — `SubstrateMedium.deposit` / `local_max` / `tick_update` pattern (but see §4–5 for *where* agents read/write).
5. **Paired permutation + Bonferroni** — `exp9/statistics.py::paired_correct_rates`, `bonferroni` (adapt metric from binary `correct` to seed-level BA).
6. **Numerical smoke patterns** — `exp9/numerical.py`, `controlled_coincidence_smoke`, Task 8 `FieldSim` near-pair latch.
7. **RNG** — `numpy.random.default_rng(seed)` as used in `env.build_world` (`seed+17`) and `experiments._run_trial` (`seed+99`).
8. **Checksum discipline** — existing `task*_checksums_*.txt` pattern for preserving Tasks 6–8.

**Reusable with care (API shape only):** `UsageStats`, medium class skeleton, agent tick order comment in `agent_step` (“read/commit before deposit”).

---

## Section 4 — Components requiring modification

Do **not** edit frozen Tasks 6–9 in place for 9.2 confirmatory science unless a deliberate non-destructive extension strategy is chosen. Prefer **new** `exp9` Task-9.2 modules that import the solver. If modifying existing Task 9 files is forced, the following changes would be required:

| File | Required change for Task 9.2 compliance |
|------|----------------------------------------|
| `exp9/env.py` | Replace landmark-\(k^*\) world with unmarked \(\mathcal{R}^*\) disk; GO/N0/N1 fragment schedules; \(\mu_T=0.70\), \(\mu_D=0.55\), \(\sigma=0.25\), \(\rho=3.5\); remove `true_landmark` as agent-relevant geometry; stop attaching `landmark_id` into agent-visible observations as a privileged key |
| `exp9/agents.py` | Remove landmark-indexed commit; implement GO/NO-GO/ABSTAIN; 3-of-4 collective rule; deposit at own pose ± jitter; read at own pose only; restricted scalar msg/BB policies |
| `exp9/field_backend.py` | Restricted msg/BB: scalar-only payloads, **no** `landmark_id`; fix `no_hysteresis` mapping (see §5/§7) |
| `exp9/experiments.py` | Matched seed×10-trial units; primary conditions + ablations; BA metric; remove majority-of-2 early stop |
| `exp9/statistics.py` | Seed-level BA pairing; \(m=4\) contrasts per protocol §7.2 |
| `exp9/config.py` / freeze JSON | New Task 9.2 freeze (evidence params after pilot); **do not** change `NL_*` |
| `exp9/runner.py` | New PASS/STOP criteria (protocol §7.3); no Task 9 acceptance ladder |
| `tests/test_exp9_*.py` | New assertions for anonymity, voting, BB/msg payloads, hysteresis-off definition |

Safer approach: leave Task 9 files immutable; add e.g. `exp9/task92_*.py` that duplicate only what must diverge.

---

## Section 5 — Components requiring replacement

These existing implementations are **protocol-incompatible** if reused as-is:

| File / symbol | Reason |
|---------------|--------|
| `env.build_world` / `World.true_landmark` / `LANDMARKS` | Task 9 is choose-landmark-\(k^*\); Task 9.2 forbids region IDs and uses unmarked \(\mathcal{R}^*\) |
| `sense_evidence` returning `landmark_id` | Exposes keyed post identity to policies |
| `EvidencePatch.landmark_id`, `is_true` on world objects used by agent logic | GT / keyed structure; agents must not use type or \(\mathcal{R}^*\) |
| `DirectMsgMedium.send_message(landmark_id, confidence, …)` | Protocol §3.1: scalar only — no landmark/topic/pose |
| `BlackboardMedium` keyed by `landmark_id` | Protocol §3.2: unordered multiset of scalars, no keys |
| `agents._msg_support` filtering by `landmark_id` | Privileged spatial/topic binding via message keys |
| `agents.majority_commit` | Plurality over landmark IDs; not ≥3 agree GO/NO-GO else UNDECIDED |
| `experiments._run_trial` early stop at majority ≥ \(n/2+1\) | Violates §6 (“No majority-of-2”); allows 3-of-4 only as collective rule after full procedure — early stop on weak majority is non-compliant |
| `make_medium` map `"no_hysteresis" → "linear_telegraph"` | **Critical:** disables reaction (\(r=a=b=0\)), conflating “hysteresis-off” with linear. Protocol wants **full NL reaction** with commit hold \(H=1\) |
| `agents.agent_step` commit to landmark index | Wrong decision alphabet for 9.2 |
| Task 9 primary metric `correct` vs `true_landmark` | Must become balanced accuracy on GO/NO-GO with UNDECIDED=error |
| Task 9 seed schedule `CONFIRM_SEED_START=400` | Protocol suggests e.g. 500–523; new freeze required |

---

## Section 6 — Missing components

Must be newly implemented (do not invent behaviour here — list only):

1. **Task 9.2 trial generator** — \(\mathcal{R}^*\) sampling; true-fragment pairwise distance \(\in[1.5,2.5]\); distractor separation; GO / N0 / N1 schedules; 5+5 trials per seed with N0/N1 parity split.
2. **Anonymous observation API** — local intensity only if fragment in \(\rho\); no type, no region id.
3. **Anonymous deposit policy** — one write/agent at pose ± \(\sigma_d=0.5\); amp `DEP_AMP`.
4. **Own-pose readout + hold** — local max in \(R_{\mathrm{read}}=5\); NL+hyst \(H=20\); hyst-off \(H=1\); linear with \(H=20\).
5. **Restricted messaging channel** — live list of scalars; TTL matched to hold budget; policies use count/sum/max/mean only.
6. **Restricted blackboard** — append-only unordered multiset; stale window matched to msg TTL.
7. **Collective decision** — per-agent \(\{\mathrm{GO},\mathrm{NO\text{-}GO},\mathrm{ABSTAIN}\}\); ≥3 agreement else UNDECIDED; no mean-commit shortcut.
8. **Matched multi-condition runner** — identical trial instances across NL / linear / BB / msg / hyst-off / deposit-disabled.
9. **Seed-level BA statistics** — 24 paired units; four Bonferroni contrasts; best-baseline rule vs \(\max(\mathrm{BA}_{BB},\mathrm{BA}_{msg})\).
10. **Task 9.2 freeze JSON** — evidence parameters after ≤8-seed pilot; stop thresholds locked.
11. **Task 9.2 tests** — anonymity, payload shape, voting, matched seeds, hyst-off ≠ linear.
12. **Plotting / report / checksum scripts** — **no matplotlib/plot utilities exist in exp9**; report generation is markdown/JSON only today. Checksums exist as text manifests, not a shared library.
13. **Stronger hysteresis intervention (optional, protocol note)** — if \(H=1\) judged too weak; must be pre-registered; not implemented.

---

## Section 7 — Numerical and scientific risks

### 7.1 Solver stability
- Equation: \(\tau\partial_t^2 s+\partial_t s=c^2\tau\nabla^2 s+rs+as^2-bs^3\) via `evolve_field_nonlinear` (explicit two-stage Euler).
- Documented operating point: \(r=-0.5,a=2,b=1\), \(dt\le0.05\); equilibria \(0\), \(\approx0.293\), \(\approx1.707\).
- Non-finite → `ValueError`; `SubstrateMedium` marks `_failed`.
- Laplacian: interior stencil (Dirichlet-like); BC sensitivity not varied (`numerical.py` note).
- **Tests exist** in `test_nonlinear_reaction_telegraph.py` (including `TestHysteresisVerification`). **This audit did not execute them** → status UNVERIFIED here.

### 7.2 Hysteresis isolation (critical)
- Protocol “NL, hysteresis disabled” = **same reaction**, \(\theta=0.85\), **\(H=1\)**.
- Existing Task 9 `ABLATIONS_B` / `make_medium`: `"no_hysteresis"` → **`linear_telegraph`** (zeros reaction). That is **not** a valid 9.2 hyst-off arm.
- Separately, `agent_step(..., no_hysteresis=True)` sets `hold_need=1` while medium may already be linear — double confound.
- Task 8 `run_D_hysteresis` measures **field** forward/reverse amp proxies, not agent commit-hold \(H\).
- **Do not claim \(H=1\) removes dynamical bistability**; protocol itself warns a stronger intervention may be needed and must be pre-registered.

### 7.3 Geometry / information leakage
- Task 9 landmarks are public posts; correct index withheld but **landmark IDs key messages, deposits, commits, and observations**.
- `sense_evidence` omits `is_true` (good) but includes `landmark_id` (bad for 9.2).
- Agent code uses `p.is_true` for `useful_deposits` accounting (evaluator-side leak into agent object stats).
- Spawn-at-landmarks + explore-by-landmark-index encodes a discrete spatial codebook absent from 9.2.
- Task 9.2 \(\mathcal{R}^*\) must never appear in agent observations.

### 7.4 Decision / early-stopping contamination
- `majority_commit` + early break when committed count ≥ majority violates “no majority-of-2” and 3-of-4 GO/NO-GO rule.
- Commit alphabet is landmark id, not GO/NO-GO/ABSTAIN.
- Msg/BB commit uses `MSG_MIN_SUPPORT=2` on **keyed** landmark channels — not anonymous scalar aggregation.

### 7.5 Evidence / metric non-transfer
- Task 9 intensities (\(\mu_T=1.0\), \(\mu_D=0.40\), \(\sigma=0.30\)) ≠ Task 9.2 (\(0.70/0.55/0.25\)).
- Task 9 `correct` ≠ Task 9.2 balanced accuracy with UNDECIDED=error.
- Existing `exp9_results.json` must not be cited as 9.2 support.

---

## Section 8 — Dependency inventory

### External packages
| Package | Role | Declared in project? | Local venv observation |
|---------|------|----------------------|------------------------|
| `numpy` | RNG, grids, stats | No `sim_world/requirements.txt` / `pyproject.toml` | Installed (e.g. 1.26.x observed in environment) |
| `scipy` | Optional in `exp6_corrected/statistics.py` | Not declared under `sim_world/` | May be present; code has ImportError fallback |
| stdlib | `json`, `math`, `dataclasses`, `unittest`, … | — | Assumed |

Historical declarations exist only under `substrate_ai_module/_archive/` (not Task 9.2-specific).

### Execution requirements
- Python ≥3.10 recommended (Task 8/9 developed on 3.10).
- `PYTHONPATH` = parent of `sim_world` package (as in `exp9_autonomous_collective.py`).
- No Minecraft / interactive client required.
- Plotting: **missing** unless newly added (`matplotlib` not used by exp9).

### Missing dependencies
- Project-local dependency lockfile for sim_world.
- Plotting stack (if reports require figures).
- Wilcoxon signed-rank: protocol allows it; `exp9/statistics.py` implements sign-permutation + sign counts, **not** SciPy Wilcoxon. Either reuse permutation or add SciPy Wilcoxon explicitly.

---

## Section 9 — Minimal source bundle

Smallest complete set another researcher needs to **implement and reproduce** Task 9.2 (import solver + read protocol; not a runnable 9.2 experiment today):

### Essential
```
exp9/TASK92_EXPERIMENTAL_PROTOCOL.md
exp9/config.py
exp9/exp9_configuration.json
exp9/field_backend.py
exp9/env.py
exp9/agents.py
exp9/experiments.py
exp9/statistics.py
exp9/numerical.py
exp9/runner.py
exp9/__init__.py
domains/physical_field/physical_field_dynamics.py
domains/physical_field/physical_field_models.py
domains/physical_field/__init__.py
domains/physical_field/test_nonlinear_reaction_telegraph.py
exp8/config.py
exp8/field_core.py
exp8/experiments.py          # run_D_hysteresis reference only
EXP8_EXPERIMENTAL_REPORT.md
EXP8_THEORETICAL_SPECIFICATION.md
exp8_configuration.json
NONLINEAR_REACTION_TELEGRAPH_IMPLEMENTATION_REPORT.md
exp9/EXP9_EXPERIMENTAL_REPORT.md
exp9/EXP9_BASELINE_FAIRNESS_AUDIT.md
tests/test_exp9_interface.py
tests/test_exp9_ablations.py
core/contracts.py
core/ids.py
```

### Strongly recommended (import-closure + preservation)
```
domains/__init__.py and packages imported by it (or a documented slim package layout)
simulation/* required by physical_field_domain import chain
exp9/task8_checksums_before.txt (and Task 6/7 manifests if preserving lineage)
exp9_autonomous_collective.py
exp8_substrate_computational_expressivity.py
```

### Explicitly not required as 9.2 evidence
```
exp9/exp9_results.json, exp9_raw_per_seed.json, exp9_pilot_results.json
exp8_results.json (context only)
pheromone / hybrid Task 9 architectures (not in 9.2 primary conditions)
```

---

## Section 10 — Execution readiness

| Requirement | Classification | Notes |
|-------------|----------------|-------|
| 1. Understand Task 9.2 protocol | **READY** | `TASK92_EXPERIMENTAL_PROTOCOL.md` complete |
| 2. Reuse frozen NL field solver | **READY** | `evolve_field_nonlinear` + frozen coeffs in `exp9/config.py` / JSON |
| 3. Understand linear substrate | **READY** | `r=a=b=0` via `linear_telegraph` / `is_linear` fall-through |
| 4. Scientifically valid hysteresis-off | **READY WITH MODIFICATIONS** | Need \(H=1\) **with full NL reaction**; current `no_hysteresis`→linear is wrong; \(H=1\) ≠ removing bistability |
| 5. Spatially clustered/dispersed evidence | **MISSING** | Need new \(\mathcal{R}^*\) / GO/N0/N1 generator; Task 9 `dispersed_evidence` is landmark-relative, not 9.2 |
| 6. Anonymous obs + deposits | **READY WITH MODIFICATIONS** | Deposit/read primitives exist; observation/deposit **policies and geometry** must be replaced |
| 7. Restricted anonymous messaging | **MISSING** | Current msgs carry `landmark_id` |
| 8. Restricted anonymous blackboard | **MISSING** | Current BB keyed; not scalar multiset |
| 9. Collective 3-of-4 voting | **MISSING** | `majority_commit` is landmark plurality; early-stop non-compliant |
| 10. Matched trials across conditions | **READY WITH MODIFICATIONS** | Seed looping exists; need shared trial instances ×10 / condition set |
| 11. Seed-level statistical analysis | **READY WITH MODIFICATIONS** | Permutation + Bonferroni exist; need BA metric, \(m=4\), best-baseline rule |
| 12. Numerical stability / reproducibility tests | **UNVERIFIED** | Suites exist (`numerical.py`, telegraph tests); **not re-run in this audit** |
| 13. Plots, reports, checksums | **READY WITH MODIFICATIONS** / **MISSING** for plots | JSON/MD + checksum text patterns exist; **no plotting utilities** |

### Critical questions (explicit answers)

**A. Physical solver**  
- **Exact solver:** `domains/physical_field/physical_field_dynamics.py::evolve_field_nonlinear` (linear limit → `evolve_field`).  
- **Coefficients:** `exp9/config.py` (`NL_R/A/B/TAU/C`, `DT`) and `exp9/exp9_configuration.json`; mirrored in `exp8/config.py`. Instantiated as `NonlinearReactionParameters` / `PropagationParameters` / `RelaxationParameters` in `exp9/field_backend.py::SubstrateMedium` and `exp8/field_core.py::FieldSim`.  
- **Existing numerical tests:** `test_nonlinear_reaction_telegraph.py` (incl. `TestHysteresisVerification`), `exp9/numerical.py`, `exp8/numerical_validation.py`. Execution status: **UNVERIFIED** in this audit.  
- **Hysteresis-off support:** Solver can run full NL while agents use \(H=1\); **no separate “hysteresis-off” PDE switch**. Current Task 9 ablation incorrectly zeros reaction.  
- **Modifications:** None to frozen PDE coeffs. New commit-hold ablation wiring required; do not map hyst-off to linear.

**B. Geometry**  
- **Defined in:** `exp9/config.py` (`LANDMARKS`, `SENSOR_RADIUS`, …), `exp9/env.py` (`build_world`, `EvidencePatch`, `sense_evidence`, `move_toward`), deposit jitter in `agents.agent_step`.  
- **Reuse without hidden spatial info?** **No** — landmark IDs and keyed channels leak structure.  
- **Replace:** `build_world` / evidence model / landmark-centric navigation and commit targets. Keep arena scale \(L=50\) and field grid.

**C. Experimental infrastructure**  
- **RNG:** `numpy.random.default_rng` with deterministic offsets (`seed+17`, `seed+99`).  
- **Stats reusable:** `paired_correct_rates`, `bonferroni`; optionally `exp6_corrected/statistics.py` paired t.  
- **Paired trials / reproducibility:** Same-seed loops in `experiments.py`; `numerical.seed_reproducibility`. Need new seed×trial pairing for 9.2 conditions.

**D. Contamination**  
- Hidden/privileged: `World.true_landmark`, `EvidencePatch.is_true`, `landmark_id` in sense/msg/BB/commit, landmark explore targets, `useful_deposits` GT check.  
- Voting/early-stop violations: `majority_commit`; `_run_trial` break on majority ≥ \(n/2+1\); keyed `MSG_MIN_SUPPORT=2`.

**E. Dependencies**  
- Required: `numpy` (+ optional `scipy`).  
- Declared under `sim_world/`: **none**.  
- Missing: sim_world requirements lock; plotting library if figures required; explicit Wilcoxon if chosen over permutation.

---

## Bottom line

Task 9.2 can reuse the **frozen nonlinear/linear field solver and numerical validation corpus** without coefficient changes. It **cannot** reuse Task 9’s landmark world, keyed messaging/blackboard, landmark voting, or `no_hysteresis→linear` ablation without violating the protocol. Implementation should add new modules (or a carefully isolated fork) rather than silently mutating Task 9 artifacts; preserve Tasks 6–9 checksums and treat all existing Task 9 result JSON as non-transferable.

**Overall readiness:** solver/coefficients **READY**; agent–environment–decision stack **MISSING** or **READY WITH MODIFICATIONS**; hyst-off scientific validity **READY WITH MODIFICATIONS** (and must not be over-claimed); plots **MISSING**; test passage **UNVERIFIED**.
