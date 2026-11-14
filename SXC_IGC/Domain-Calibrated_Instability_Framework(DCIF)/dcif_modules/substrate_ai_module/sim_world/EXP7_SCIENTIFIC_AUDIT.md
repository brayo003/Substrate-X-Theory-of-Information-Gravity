# EXP7 Scientific Audit

**Date:** 2026-11-13  
**Scope:** Executable Corrective Task 6 system as the baseline for Task 7.  
**Task 6 artifacts:** Preserved; checksums in `exp7/task6_checksums_before.txt` (verified again after Task 7).

---

## 1. Task 6 findings carried forward (not re-litigated)

1. Bistable reaction-telegraph dynamics with IC \(s=0\) below separatrix \(s_-\).
2. Linear and nonlinear substrates recover events at delay 30 (G5).
3. Controlled \(X/Y/X{+}Y\) collective recovery with F1 = 1.0 for five architectures (G6); ceiling.
4. No GT coordinate querying / no shared claim oracle in corrected pathways (G3–G4).
5. G8 FAIL: zero avoided crossings; identical hazard exposure across conditions.
6. No nonlinear-specific comparative advantage (Outcome B, Level 3).

---

## 2. Executable system inspection

| Component | Location | Finding |
|---|---|---|
| Solver | `domains/physical_field/physical_field_dynamics.py` → `evolve_field_nonlinear` | Implements \(\tau s_{tt}+s_t=c^2\tau\nabla^2s+rs+as^2-bs^3\) |
| Parameters | `exp6_corrected/config.py` | \(r=-0.5,a=2,b=1,\tau=1,c=1,\Delta t=0.05\), grid 30×30 |
| IC | `architectures._build_field` | `initial_value=FIELD_IC=0.0` |
| Encoding | `SubstrateMemory.deposit` | Positive Gaussian for most kinds; **hazard forced negative** |
| Hazard readout | `SubstrateMemory.query_at("hazard")` | `max(0,-mean)` |
| Movement | `oracle_tests.choose_movement_target` | Sensors + `list_known` + local gradient; no GT lists |
| Exp C hazard | `experiment_c._hazard_avoid_target` | Pre-entry diversion exists, but G8 showed **0 avoided crossings** |

---

## 3. Why Task 6 G8 failed (causal diagnosis)

1. **Environment:** Scattered hazards with random agent starts; uninformed agents rarely propose a path that would enter a *known* hazard signal region before first contact.
2. **Policy:** Diversion triggers only when a *proposed* waypoint already looks dangerous via architecture signal or private known hazards. Discoverer and recipient were not separated; no forced decision point.
3. **Encoding:** Substrate hazards are **negative** deposits. Bistable latching into \(s_+\) cannot store hazard marks; persistence relies on slow relaxation of a negative bump — weak vs messaging TTL/blackboard for behavioural timing.
4. **Metric:** Methodology was correct (exposure ≠ avoidance), but the causal chain discovery→deposit→recovery→pre-entry route change never fired.

**Task 7 Track A implication:** Use a forced corridor with a genuine safe alternative; separate Discoverer/Recipient; deposit hazard as a documented **positive danger-marker** for spatial media (so nonlinear latching is testable); measure the full causal chain.

---

## 4. Why Task 6 Exp B cannot establish nonlinear advantage

The XY_near midpoint heuristic saturates for linear, pheromone, blackboard, and messaging alike. Ceiling F1 = 1.0. Repeating with more seeds will not discriminate.

**Task 7 Track B implication:** Use a **bistable AND-gate**: individually subthreshold deposits remain below \(s_-\); spatially overlapping pair crosses separatrix and latches. Linear ablation cannot latch. Ablate reaction terms to isolate nonlinearity.

---

## 5. What Task 7 must not do

- Modify or regenerate Task 6 files.
- Re-run Task 6 endpoints as confirmatory evidence.
- Count post-entry detection as avoidance.
- Claim nonlinear advantage when linear matches.
- Use saturated simple XY tasks as primary endpoints.

---

## 6. Task 7 gate map

| Gate | Track | Maps to |
|---|---|---|
| T1–T2 | Both | Information + fairness integrity |
| T3–T6 | A | Recovery → behaviour → utility → persistence |
| T7–T9 | B | Capability → nonlinear-specific → comparative advantage |

---

## 7. Post-execution verification (2026-11-13)

| Check | Result |
|---|---|
| Task 6 MD5 checksums before ≡ after | **PRESERVED** (`exp7/task6_checksums_*.txt`) |
| Pilot gates | T1–T8 PASS, T9 FAIL |
| Confirmatory (N=40, seeds 200–239) | Same gate pattern; Outcome **C**, Level **3** |
| Track A primary | Exposure 5→0 under informed nonlinear; controls dissociate |
| Track B primary | Nonlinear AND F1≈0.987; linear/reaction-off F1=0; msg/BB F1=1.0 |
| Solver failures | 0 in confirmatory Track A and AND trials |

Full interpretation: `EXP7_REPORT.md`.
