# EXP9 Architectural Specification — Substrate–Agent Interface

**Date:** 2026-11-13  
**Depends on:** `EXP9_PRE_IMPLEMENTATION_AUDIT.md`  
**Field equation:** unchanged from Tasks 7–8 (code form at \(\tau=1\)).

---

## 1. Interaction cycle

For each agent \(i\) at tick \(t\):

1. **Observe** only permitted local environment + local field/memory readout.  
2. **Decide deposit** \(D_i(t)\in\{0,1\}\) and location \(\mathbf{x}_i^{\mathrm{dep}}\) (usually own pose or nearest visited landmark).  
3. **Substrate / backend evolves** once per tick after all deposits (matched across architectures).  
4. **Read** permitted local medium value \(r_i(t)=R(\mathrm{medium},\mathbf{x}_i,\rho_{\mathrm{read}})\).  
5. **Interpret** via architecture-specific rule (threshold / max-among-landmarks / message parse).  
6. **Act:** move and optionally **commit** to a landmark \(k\in\{1..K\}\).  
7. **Environment** returns observation noise, travel cost, and (for evaluation only) correctness of commitment.  
8. Outcomes affect subsequent energy/budget and whether further deposits are allowed.

---

## 2. Mathematical / operational definitions

### 2.1 Deposit function

\[
s(\mathbf{x},t^+) = s(\mathbf{x},t) + A\,G(\mathbf{x}-\mathbf{x}^{\mathrm{dep}};w)
\]

- \(G\): Gaussian footprint via existing `apply_perturbation` (width \(w=2.0\)).  
- Amplitude \(A = A_{\mathrm{dep}}\) (frozen; Task 8-scale \(0.50\) for coincidence-class deposits).  
- Conventional backends: analogous write to message/blackboard/pheromone with matched write cost.

### 2.2 Observation radius

Agent \(i\) may sense environmental evidence patches and landmarks within Euclidean radius \(\rho_{\mathrm{obs}}\) of pose \(\mathbf{x}_i\). No global map of undiscovered evidence.

### 2.3 Field readout

\[
R_{\mathrm{field}}(\mathbf{x}) = \max_{\|\mathbf{y}-\mathbf{x}\|\le\rho_{\mathrm{read}}} s(\mathbf{y})
\]

(local max on grid cells; same pattern as Task 8 `local_max`).  
Pheromone: local grid value. Messaging/BB: structured records in range / stale window.

### 2.4 Decision / commitment

Landmark set \(\mathcal{L}=\{L_k\}_{k=1}^K\) is an **environmental feature** (visible posts). Agents know post coordinates as public geometry; they do **not** know which \(k^\*\) is correct.

Commitment rule (substrate / pheromone spatial):

\[
\hat{k} = \arg\max_{k\in\mathcal{V}_i} R(L_k),\quad \text{commit if } R(L_{\hat{k}})\ge\theta_{\mathrm{dec}}
\]

where \(\mathcal{V}_i\) = landmarks agent \(i\) has visited (or is within \(\rho_{\mathrm{obs}}\) of).  
Messaging/BB: commit to majority / strongest evidence record among known reports.  
Independent: commit only from own noisy observations (no shared medium).

\(\theta_{\mathrm{dec}}=0.85\) for high-basin substrate (Task 8); pheromone/messaging use matched decision thresholds on their own scales (documented in config).

### 2.5 Movement policy

Speed \(v_{\max}\). Default policy: explore unvisited landmarks / evidence-bearing regions via greedy + small random exploration; if local readout high, linger/read; after commit, stop or move to committed landmark.

### 2.6 Field evolution interval

One solver step per environment tick (\(\Delta t=0.05\)), same as Tasks 7–8. Ablations may disable evolution (`readout_only`) or set \(c=0\) / reaction off.

### 2.7 Communication restrictions

| Architecture | Cross-agent channel |
|---|---|
| independent | none |
| direct_msg | explicit messages, TTL |
| blackboard | shared records, stale window |
| pheromone | evaporating scalar map |
| linear_sub / nonlinear_sub | physical field only |
| hybrid | field + limited messages (budget-capped) |

No architecture receives GT \(k^\*\) or global field max location unless that location is reached by permitted sensing.

### 2.8 Agent memory restrictions

- Private: pose history, visited landmarks, last local observations, own deposits count.  
- No deposit_log of other agents.  
- No evaluator ground truth.

### 2.9 Costs (accounted every trial)

| Action | Cost unit |
|---|---|
| Deposit / write | 1 write |
| Read / query | 1 read |
| Message send | 1 message + payload bytes |
| Move | \(\Delta\) path length |
| Field step | 1 solver_step (substrate only) |

Resource expenditure = weighted sum (weights in config; reported, not hidden).

---

## 3. Information taxonomy (attribution rules)

| Kind | Example | Attribution |
|---|---|---|
| Stored in medium | Deposit amplitude at site | Channel capacity / memory |
| Transformed by dynamics | Overlap → high-basin latch | **Substrate computation** |
| Extracted by agent | \(R(\mathbf{x})\) | Readout (not computation by itself) |
| Agent policy | Explore, when to deposit, when to commit | **Agent computation** |

Claiming “substrate computed X” requires ablation: remove/alter dynamics → X fails while policy & sensors held fixed.

---

## 4. Privileged-information prohibition

Agents must **not** receive:

1. Identity of correct landmark \(k^\*\).  
2. Other agents’ deposit coordinates except via physical observation of the medium in range.  
3. Precomputed collective answer.  
4. Global \(\arg\max s\).  
5. A readout site that is correct **because** the designer tied it to \(k^\*\) without requiring discovery/visit.

Evaluator may know \(k^\*\) for scoring only.

**Landmark posts are justified** as shared environmental geometry available to **all** architectures (including messaging baselines that name post IDs). They are not oracles of correctness.

---

## 5. Ablation vocabulary (mechanism isolation)

| Ablation | Change |
|---|---|
| `nonlinear_full` | \(r,a,b\) bistable |
| `linear_telegraph` / `reaction_off` | \(r=a=b=0\) |
| `no_propagation` | \(c=0\) |
| `no_inertia` | documented 1st-order step (Task 8) |
| `no_hysteresis` | replace commit with non-persistent threshold on instantaneous deposit sum proxy **or** force linear + high θ (documented) |
| `readout_disabled` | agents cannot query medium |
| `deposit_disabled` | agents cannot write |
| `fixed_random_policy` | ignore readout; random commit |
| `propagation_off` | alias `no_propagation` |

Where an ablation changes multiple mechanisms, claims stay at the joint level.

---

## 6. Reuse boundary

- Solver: import `evolve_field_nonlinear` / `apply_perturbation` — **no edits**.  
- New code: only under `exp9/` and `tests/test_exp9_*.py`.  
- Task 6 `MemoryBackend` imported for conventional baselines; Task 9 substrate wrapper lives in `exp9/` to avoid editing Task 6/7/8.
