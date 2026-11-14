# Phase AI-0 — Scientific Reconstruction of the Substrate AI Module

**Audit Date:** 2026-07-22  
**Scope:** Complete scientific reconstruction of the Substrate AI module exactly as it exists.  
**Method:** Every file treated as evidence. Nothing dismissed until inspected.

---

## DELIVERABLE 1 — Complete Architecture Report

### 1.1 What This Module Is

The Substrate AI module is a research system built on one central hypothesis:

> An AI system can predict its own failure before attempting a task, by treating the reasoning process as a physical transport phenomenon, and computing a local stability criterion (tension / Q) from features of the input.

This is **not** a standard AI inference pipeline. It is an attempt to instrument LLM reasoning using physics-derived diagnostics drawn from the SXC-IGC (Substrate X — Information Gravity Calculus) theoretical framework.

The module grew through several months of iterative research. Its structure reveals at least five distinct phases of development, each partially superseding but never fully replacing the previous one.

---

### 1.2 The Five Developmental Phases (Recovered Chronology)

**Phase 0 — HLE Baseline (March 13, root level)**  
The module began as a fork of the Humanity's Last Exam (HLE) evaluation harness. Files: `hle_eval/run_model_predictions.py`, `hle_eval/run_judge_results.py`, `hle_gemma2:2b.json`, `judged_hle_gemma2:2b.json.json`. Gemma2:2b was run against HLE and achieved ~3% accuracy. This failure data became the calibration corpus for all subsequent work.

**Phase 1 — Monolithic Substrate AI (March 13, root level)**  
The first architectural response to HLE failure: `substrate_ai.py`. A single-class system (`SubstrateDynamics` + `SubstrateAwareAI`) that reads HLE results, computes "information gravity" (tension) from prompt features, and decides whether to attempt or abort. This is the original, self-contained prototype.

**Phase 2 — Decomposed Pipeline (March 13, root level)**  
The monolith was decomposed into separate concerns: `substrate_core.py`, `problem_analyzer.py`, `actuator.py`, `ollama_bridge.py`, `main.py` (CognitiveGovernor). This is the first time the Governor pattern appears. Supporting tools: `adaptive_thinker.py`, `autotune.py`, `update_strategy.py`, `dashboard.py`, `stress_test.py`, `ai_monitor.py`, `cloud_bridge.py`.

**Phase 3 — Scientific Deepening (March 13 → March 23, substrate_ai/ directory)**  
A parallel, more ambitious implementation in `substrate_ai/`. Introduced: `components/` subdirectory with the V12 engine (`sxc_omega_v12.py`), the epistemic gate, a fuller actuator, the knowledge translator, and the conscious rewrite / substrate-correct reflection experiments. This phase introduced the SXC-Omega differential equation for T_sys. Also introduced the `your_substrate_profile.json` concept (user-as-substrate).

**Phase 4 — V12 Video Control / Kaggle (May–July, check files)**  
The framework was extended to video generation control (I2VGen-XL). `check2.txt` and `check3.txt` are Kaggle notebook exports showing the V12 dynamics applied to inter-clip semantic novelty in video diffusion pipelines. This is the most architecturally mature application of the V12 engine — and the least integrated with the rest of the codebase.

**Phase 5 — Capability Audit (July 21, capability_audit.md)**  
A rigorous, standalone theoretical document that formalizes Q = 4c²τ²|∇ln s|² − 1 as the core transport-phase classifier. This document was written *about* the physics, but is not yet connected back to the Python codebase. The gap between the audit and the code is the central unresolved tension of the module.

---

### 1.3 The Naming Drift Problem

The module suffers from systematic naming drift — the same physical concept appears under multiple names across files:

| Physical concept | Names used in code |
|---|---|
| Cognitive load / instability | `tension`, `T_sys`, `Q`, `information gravity`, `stress` |
| Transport regime | `regime`, `phase`, `NOMINAL/FIREWALL`, `vanilla/transitional/high_tension/saturated` |
| Stability threshold | `0.4`, `0.7`, `0.9`, `1.0`, threshold varies by file |
| Safe-to-proceed signal | `should_attempt`, `phase != FIREWALL`, `regime == vanilla` |
| Symbolic execution fallback | `actuator`, `PythonActuator`, `execute_math`, `generate_code_payload` |
| LLM interface | `OllamaBridge`, `CloudBridge`, `bridge.simple_inference` |

This drift is not random — it reflects genuine conceptual evolution. Early files use "tension" as an engineering metaphor. Later files use "T_sys" as a dynamical systems variable. The capability audit uses Q as a field-theoretic quantity. These three are intended to be the same thing at different levels of formalization.

---

## DELIVERABLE 2 — Dependency Graph

The pipeline as it exists (active execution path through `substrate_ai/run_system.py`):

```
User Query
     │
     ▼
CognitiveGovernor (substrate_ai/components/cognitive_governor.py)
     │
     ├──► OllamaBridge.simple_inference(query)
     │         │ returns raw_response
     │         ▼
     │    SXCOmegaEngine.step(len(raw_response.split()))
     │         │ returns (T_sys, phase)
     │         ▼
     │    if phase == "FIREWALL":
     │         └──► OllamaBridge.generate_code_payload(query)
     │                   [code string returned, NOT executed by actuator here]
     │
     └──► return {response, tension, strategy}
```

The pipeline as it was designed (root-level `main.py`):

```
User Query
     │
     ▼
CognitiveGovernor.process_question()
     │
     ├──► ProblemAnalyzer.extract_features(question)
     │         │ returns feature dict
     │         ▼
     │    ProblemAnalyzer.predict_tension_from_features(features)
     │         │ returns tension [0,1]
     │         ▼
     │    SubstrateDynamics.determine_regime(tension)
     │         │ returns regime string
     │         ▼
     │    if regime == 'formal_required':
     │         └──► [retry loop, max 3]
     │                   OllamaBridge.generate_code_payload(prompt)
     │                        │
     │                        ▼
     │                   PythonActuator.execute_math(code)
     │                        │
     │                   if success: return result
     │                   else: add error to prompt, retry
     │
     └──► return "Narrative mode"
```

The full intended pipeline (from demo files, never fully wired):

```
Problem
  │
  ▼
ProblemAnalyzer ──► features{formal_demand, advanced_lexicon, simple_math}
  │                         │
  │               predict_tension_from_features()
  │                         │ tension [0,1]
  ▼                         ▼
SubstrateDynamics.determine_regime()
  │
  ├── vanilla        ──► Direct LLM inference (narrative)
  ├── transitional   ──► LLM inference + warning flag
  ├── high_tension   ──► Actuator (SymPy symbolic computation)
  └── saturated      ──► Abort + suggestions
           │
           ▼ (high_tension path)
  SXCOmegaEngine.step(signal)  ← V12 dynamics (only in components/ governor)
           │
           ▼
  EpistemicGate.evaluate_query(features)  ← never wired into main flow
           │
           ▼
  PythonActuator.execute_math(code)
           │
           ▼
  Result / Error → Cognitive Loop (re-prompt with error)
           │
           ▼
  AdaptiveThinker.select_strategy()  ← not wired into governor
           │
           ▼
  autotune.py → update_strategy.py → adaptive_thinker.py  ← feedback loop
```

**Critical observation:** The feedback loop (autotune → update_strategy → adaptive_thinker) is architecturally sketched but never closed. `autotune.py` reads HLE data, computes optimal threshold, calls `update_strategy()` which calls `apply_calibration()` in `update_strategy.py`, which rewrites `adaptive_thinker.py` via regex. This is the adaptation loop — and it is the only place where learning from past performance is attempted.

---

## DELIVERABLE 3 — Scientific Glossary

Every important quantity, where it is computed, how it propagates, and its status.

### Q (Transport-Phase Classifier)
- **Definition:** Q = 4c²τ²|∇ln s|² − 1, where s(x,t) is a scalar substrate field, c is the propagation speed, τ is the relaxation time.
- **Physical meaning:** Q > 0 → oscillatory/coherent transport regime. Q < 0 → overdamped/incoherent regime. Q = 0 → exact phase boundary.
- **Where computed:** `capability_audit.md` (theoretical). Not directly computed in any Python file.
- **How it propagates:** In theory, Q is a spatial field computed pointwise from s and ∇s. In practice, a scalar proxy (tension) is computed from prompt features instead.
- **Affects decisions:** Indirectly — the regime classification it implies is implemented via the tension thresholds.
- **Status:** Fully formalized in the audit. Zero implementation in code. **Critical gap.**

### tension / T_sys (Cognitive Stress)
- **Definition (root-level):** A scalar in [0,1] computed from problem features (length, keywords, domain). Defined in `problem_analyzer.py`.
- **Definition (V12):** A differential-equation state variable. `T_{t+1} = T_t + (E_t·β − γ_eff·γ·T_t)·dt`. Defined in `components/sxc_omega_v12.py`.
- **Physical meaning:** Intended as the AI analog of Q — a measure of how close the reasoning substrate is to the overdamped/failure regime.
- **Where computed:** `ProblemAnalyzer.predict_tension_from_features()` (root, algebraic); `SXCOmegaEngine.step()` (components/, ODE-based).
- **How it propagates:** Feeds into `SubstrateDynamics.determine_regime()` → strategy selection.
- **Affects decisions:** Yes. Primary decision variable for all routing.
- **Multiple inconsistent implementations:** Yes — two completely different methods. Feature-weighted linear combination vs. ODE dynamics. They are never reconciled.
- **Status:** Partially implemented, inconsistently.

### regime (Transport Phase)
- **Definition:** Categorical label derived from tension threshold comparison.
- **Root-level values:** `narrative_ok`, `transitional`, `formal_required` (substrate_core.py, main.py)
- **Components/ values:** `vanilla`, `transitional`, `high_tension`, `saturated` (components/substrate_core.py)
- **V12 values:** `NOMINAL`, `FIREWALL` (sxc_omega_v12.py)
- **Where computed:** `SubstrateDynamics.determine_regime(tension)`
- **How it propagates:** Selects strategy in CognitiveGovernor.
- **Status:** Three parallel, incompatible regime taxonomies. Root uses 3 levels, components/ uses 4 levels, V12 uses 2 levels.

### F_transport (Excitation Flux)
- **Definition:** `E_t = 1 - exp(-signal/40)` for signal < 45, linear above. Measures how much incoming semantic load excites the system.
- **Where computed:** `SXCOmegaEngine.excitation_flux(signal)` in `components/sxc_omega_v12.py` and `test_paperclip.py`.
- **Input:** `signal` = word count of LLM response (in components/governor) or semantic keyword score (in test_paperclip.py).
- **How it propagates:** Drives T_sys dynamics: `inflow = E * beta`.
- **Status:** Implemented. Used in V12 path only. Signal source is inconsistent across uses.

### gamma (Damping / Elastic Resistance)
- **Definition:** Decay parameter representing the system's resistance to tension buildup. Decays over time: `gamma *= (1 - decay_rate)`.
- **Where computed:** `SXCOmegaEngine` in `components/sxc_omega_v12.py`.
- **Parameters:** `gamma_max = 0.8`, `decay_rate = 0.0005`, restored by intervention.
- **Physical meaning:** Analogous to material damping in the telegraph equation. Slow decay models substrate fatigue.
- **Status:** Implemented but never calibrated against data. The `apply_intervention()` method exists but is never called in any governor.

### beta (Excitation Coupling)
- **Definition:** Gain constant for how strongly excitation flux drives T_sys. `beta = 3.5`.
- **Where computed:** Hardcoded in `SXCOmegaEngine.__init__`.
- **Status:** Magic constant. Never calibrated.

### r (Accuracy Rate)
- **Definition:** HLE accuracy rate of Gemma2:2b = 0.153 (15.3%).
- **Where computed:** Hardcoded in `SubstrateDynamics.__init__` (both root and components versions): `self.r = 0.153`.
- **How it propagates:** Referenced in docstrings and comments but not used in any computation in the simplified substrate_core versions. Originally used in the full V12 tension formula.
- **Status:** Present as a constant but mostly decorative in current code. Originally meant to seed calibration.

### coherence / ξ_c (Coherence Length)
- **Definition:** ξ_c = 2cτ. The spatial scale below which transport is coherent.
- **Where computed:** `capability_audit.md` only.
- **Status:** Theoretically defined. No Python implementation.

### EpistemicStatus (Epistemic Tension)
- **Definition:** Enum with 5 levels: VALIDATED_BY_CONSTRAINT (tension 0.1), MEASURED_FROM_DATA (0.3), INFERRED_WITH_CONFIDENCE (0.6), UNVALIDATED_INPUT (0.8), BEYOND_EPISTEMIC_CLOSURE (0.95).
- **Where computed:** `substrate_correct_reflection.py`, `epistemic_gate.py`.
- **How it propagates:** `EpistemicGate.evaluate_query()` returns a boolean go/no-go. Never wired into main governor.
- **Status:** Implemented but disconnected. The most sophisticated epistemic formalization in the codebase.

### confidence / calibration_error
- **Definition:** Model self-reported confidence 0–100% extracted from HLE responses. Calibration error = gap between confidence and actual accuracy.
- **Where computed:** `hle_eval/run_judge_results.py` via `calib_err()`. HLE result: Accuracy 3.07%, Calibration Error 92.3.
- **Status:** Computed empirically. The 92.3 calibration error is the founding empirical observation of the whole module.

### conflict_factor (Substrate Conflict Law)
- **Definition:** Geometric scaling factor applied when multiple substrate types conflict. `conflict_factor = 2.8` when AI_GOAL and BIO_BASE coexist.
- **Where computed:** `test_paperclip.py`.
- **Status:** Experimental, single-file. Never generalized.

### user_skill / adjusted_tension
- **Definition:** Per-user tension adjustment. `adjusted_tension = max(0.1, universal_tension - user_skill * 0.5)`.
- **Where computed:** `your_ai_translator.py`, `knowledge_translator.py`.
- **Status:** Experimental (knowledge translation experiments). Never wired into governor.

---

## DELIVERABLE 4 — Capability Audit Integration Map

The capability_audit.md defines Q rigorously and establishes 6 demonstrated capabilities. Below is the mapping to the current codebase.

### CA Capability 1: Local transport-phase classification in heterogeneous media
- **Audit claim:** Q(x,t) classifies regime pointwise for spatially heterogeneous fields.
- **Implemented:** Partially. `ProblemAnalyzer.predict_tension_from_features()` classifies prompts into regimes. But: it uses discrete keyword matching, not a continuous field. The "field" s(x,t) has no implementation.
- **Relevant files:** `problem_analyzer.py` (root), `components/problem_analyzer.py`
- **Gap:** The audit's Q operates on a scalar field. The code operates on a feature vector. These are structurally analogous but the field formulation is never instantiated.

### CA Capability 2: Coherence-length estimation without spectroscopy
- **Audit claim:** ξ_c = 2cτ is read from the Q = 0 surface.
- **Implemented:** Not at all.
- **Relevant files:** None. c and τ appear only in the audit.
- **Gap:** Complete. No code defines c or τ as Python variables.

### CA Capability 3: Critical-slowing detection at regime boundaries
- **Audit claim:** Γ_dec → 0 as Q → 0⁻ with universal exponent 1/2.
- **Implemented:** Partially, metaphorically. The `SXCOmegaEngine` exhibits slowing near the FIREWALL threshold due to γ decay — this qualitatively resembles critical slowing but is not derived from the Q formula.
- **Relevant files:** `components/sxc_omega_v12.py`
- **Gap:** The 1/2 exponent and the Q → 0 boundary are not present in code.

### CA Capability 4: Cross-domain regime unification
- **Audit claim:** Identical formula classifies acoustic, thermal, EM, concentration fields.
- **Implemented:** Partially. The tension formula is applied to text (prompt analysis) and to video (check2.txt V12 video controller). Two domains use the same framework. However they use different signal definitions and the formula is not Q itself.
- **Relevant files:** `components/problem_analyzer.py` (text domain), `check2.txt` / `check3.txt` (video domain)
- **Gap:** The unification is informal. No shared Q computation ties the domains.

### CA Capability 5: T₂ ≤ 2T₁ structural bound
- **Audit claim:** From Im(ω) = 1/(2τ), derives T₂ ≤ 2T₁ without quantum mechanics.
- **Implemented:** Not at all.
- **Relevant files:** None.
- **Gap:** Complete. This is a pure theoretical result in the audit.

### CA Capability 6: Algebraic stability classification replacing eigenvalue analysis
- **Audit claim:** Q computation is O(N) arithmetic, replacing O(N) eigenvalue problems.
- **Implemented:** Yes, in the wrong domain. The feature-based tension computation is algebraic (no eigenvalues). But the cost argument applies to PDE stability analysis, not text classification.
- **Relevant files:** All tension computation files.
- **Gap:** The algebraic property is present but the eigenvalue-replacement claim requires a PDE domain.

### Summary Table

| Audit Capability | Code Status | Closest File |
|---|---|---|
| Local Q classification | Analogous (features, not field) | `components/problem_analyzer.py` |
| ξ_c = 2cτ | Not implemented | — |
| Critical slowing (Q→0⁻) | Qualitative only | `components/sxc_omega_v12.py` |
| Cross-domain unification | Informal (text + video) | `check2.txt` |
| T₂ ≤ 2T₁ bound | Not implemented | — |
| Algebraic vs. eigenvalue | Present (wrong domain) | All tension files |

### Ideas in the Audit that Never Reached Code
1. The actual formula Q = 4c²τ²|∇ln s|² − 1 — never computed as a Python expression.
2. The Q = 0 surface as a spatial boundary — never mapped.
3. The decoherence rate formula Γ_dec ≈ (1/2τ)√|Q| near Q = 0⁻ — never implemented.
4. The parameter identification: c = propagation speed, τ = relaxation time, s = substrate field — never bound to measurable AI quantities.
5. The market application (appendix): `market state → s(x,t) → Q(x,t) → regime → strategy` — only sketched.

---

## DELIVERABLE 5 — Duplicate Implementation Report

### SubstrateDynamics

| File | Version | Thresholds | Formula | Status |
|---|---|---|---|---|
| `substrate_core.py` (root) | Minimal | 0.4, 0.7 → 3 regimes | None (lookup only) | Infrastructure |
| `substrate_ai/components/substrate_core.py` | V12 full | 0.3, 0.6, 0.9 → 4 regimes | V12 quadratic `(a + √discriminant) / 2b` | Production (for components/ path) |

**Assessment:** These are genuinely different implementations. The root version is a stub (3 regime threshold check). The components/ version has the V12 quadratic formula and 4 regimes. The components/ version is newer and contains unique scientific content (the discriminant formula). **They should not be merged — the V12 version supersedes.**

### CognitiveGovernor

| File | Version | Inputs | Outputs | Status |
|---|---|---|---|---|
| `main.py` (root) | ProblemAnalyzer-driven | Problem text | regime + optional actuator result | Production (root path) |
| `substrate_ai/cognitive_governor.py` | V12 ODE-driven | User query | T_sys + phase + response | Production (components/ path) |
| `substrate_ai/components/cognitive_governor.py` | Identical to above | Same | Same | Duplicate |

**Assessment:** `substrate_ai/cognitive_governor.py` and `substrate_ai/components/cognitive_governor.py` are **character-for-character identical** — a pure copy. The root `main.py` governor uses ProblemAnalyzer; the substrate_ai governor uses SXCOmegaEngine. These represent two different theories of how to measure tension (pre-hoc feature analysis vs. post-hoc response analysis). Both paths are scientifically valid and complementary.

### ProblemAnalyzer

| File | Version | Features | Calibration | Status |
|---|---|---|---|---|
| `problem_analyzer.py` (root) | Minimal | formal_demand, advanced_lexicon, simple_math | Hardcoded rules | Early prototype |
| `substrate_ai/components/problem_analyzer.py` | Full V12 | 5 weighted features + HLE pattern dict | Calibrated from HLE data | Production |

**Assessment:** The components/ version is substantially richer. It has 5 features, HLE-calibrated baselines per problem type, sigmoid normalization, and explicit calibration commentary. The root version is a minimal predecessor. **Components/ version supersedes.**

### Actuator

| File | Version | Execution | Safety | Status |
|---|---|---|---|---|
| `actuator.py` (root) | Minimal | subprocess + temp file | None | Early prototype |
| `substrate_ai/components/actuator.py` | Full sandbox | exec() with safe_builtins, sympy preloaded | Restricted builtins dict | Experimental (over-engineered) |
| `substrate_ai/components/actuator_fixed.py` | Direct exec | exec() with full namespace | Danger line filter | Production (simpler, works) |

**Assessment:** Three progressively different security models. The root version writes a temp file and uses subprocess — simple but leaves temp_solve.py artifacts (the `temp_solve.py` file in root is such an artifact). The `actuator.py` in components uses a restricted exec environment (over-engineered, has import resolution bugs). `actuator_fixed.py` uses direct exec with a danger-word filter — the pragmatic working version. **actuator_fixed.py is the active production implementation.**

### OllamaBridge

| File | Version | Model | Unique content |
|---|---|---|---|
| `ollama_bridge.py` (root) | gemma2:2b | prompt → code payload | Minimal |
| `substrate_ai/components/ollama_bridge.py` | tinyllama:latest | simple_inference + code payload | Different model, different URL format |

**Assessment:** Different default models, slightly different interfaces. Both functional. The model difference (gemma2:2b vs tinyllama) represents a real hardware/capability decision — gemma2:2b was the HLE subject, tinyllama is the cheaper local option.

### CloudBridge

| File | Version | Unique content |
|---|---|---|
| `cloud_bridge.py` (root) | OpenRouter/Claude-3.5 | Same interface |
| `substrate_ai/components/cloud_bridge.py` | OpenRouter/Claude-3.5 | Stricter prompt ("No markdown. No explanations.") |

**Assessment:** Near-duplicate. The components/ version has a marginally stricter code generation prompt. **Minor unique content.**

---

## DELIVERABLE 6 — Experiment Timeline

### Experiment 1: HLE Baseline Evaluation
- **Hypothesis:** Run Gemma2:2b on HLE benchmark to establish failure baseline.
- **Methodology:** Used `hle_eval/run_model_predictions.py` with OpenAI async client against HLE dataset. Judged with `run_judge_results.py`.
- **Outcome:** Accuracy 3.07% ± 0.65%, Calibration Error 92.3. Results in `judged_hle_gemma2:2b.json.json` (288 entries).
- **Remaining value:** This is the empirical foundation of all subsequent work. The calibration error of 92.3 is the key measurement — the model is massively overconfident relative to its actual accuracy. This is the problem the entire module tries to solve.

### Experiment 2: Monolithic Substrate-Aware AI
- **Hypothesis:** By computing "information gravity" (tension) from prompt features and calibrating against historical accuracy, an AI can predict before answering whether it will succeed.
- **Methodology:** `substrate_ai.py` — reads HLE judged data, computes base_accuracy, maps feature→tension, computes success_probability = base_accuracy * (1 - tension).
- **Outcome:** The formula `success_prob = base_prob * (1 - tension)` is too simplistic. If base_accuracy = 0.03, success_prob is always near zero. The 5% threshold for attempting means almost nothing is ever attempted.
- **Remaining value:** Establishes the calibration-from-history pattern and the abort/proceed decision boundary.

### Experiment 3: Decomposed Governor with Actuator
- **Hypothesis:** For problems that exceed LLM capability, symbolic computation via SymPy can reliably compute the answer, closing the loop.
- **Methodology:** `main.py` (CognitiveGovernor) with `PythonActuator.execute_math()` — Ollama generates SymPy code, actuator executes it, errors feed back as prompts (cognitive loop, max 3 retries).
- **Outcome:** The cognitive loop (error→retry) is a genuine innovation. The actuator itself had multiple broken iterations (root version writes temp files, components/actuator.py has sandboxing bugs, actuator_fixed.py works cleanly).
- **Remaining value:** The three-retry cognitive loop with error feedback is a working pattern. `actuator_fixed.py` reliably executes symbolic math.

### Experiment 4: V12 Dynamics (SXC-Omega Engine)
- **Hypothesis:** Instead of pre-hoc feature analysis, tension should be measured post-hoc from the model's own output dynamics using a differential equation: the length/complexity of the response as a signal.
- **Methodology:** `SXCOmegaEngine.step()` — computes excitation flux from response word count, updates T_sys via ODE, transitions to FIREWALL when T_sys > 1.0.
- **Outcome:** Functionally operational. The FIREWALL threshold is reached when signal is sustained above the γ damping capacity. However, using word count as the signal is a crude proxy.
- **Remaining value:** The ODE formulation (T_sys dynamics) is the only part of the codebase that mirrors the differential equation structure of the telegraph equation underlying Q. The γ decay (substrate fatigue) and the FIREWALL/NOMINAL hysteresis are scientifically interesting behaviors.

### Experiment 5: Epistemic Gate
- **Hypothesis:** Some queries should be refused not on complexity grounds but on epistemic grounds — they ask for things the system structurally cannot validate.
- **Methodology:** `EpistemicGate.evaluate_query()` checks if `abstract_terms > 0.8 and technical_density < 0.2` → identity/self-inquiry.
- **Outcome:** Partially designed but never wired into the main governor.
- **Remaining value:** The EpistemicStatus taxonomy (5 levels, each with a tension value) is the most sophisticated uncertainty quantification in the codebase. It maps directly onto the Q framework: BEYOND_EPISTEMIC_CLOSURE = saturated regime.

### Experiment 6: Substrate-Correct Reflection
- **Hypothesis:** An AI system should only make claims at the level their epistemic validation supports. Claims beyond closure should be refused, not hallucinated.
- **Methodology:** `substrate_correct_reflection.py` — SubstrateClaim objects with EpistemicStatus tags, tension proportional to epistemic risk, SubstrateReflector that refuses identity/self-inquiry questions.
- **Outcome:** Full implementation. Demonstrates that refusal is itself a computationally meaningful output.
- **Remaining value:** Contains the clearest articulation of the core principle: "The measure of substrate awareness is not insightfulness, but restraint." This is the anti-hallucination mechanism.

### Experiment 7: Conscious Rewrite
- **Hypothesis:** The substrate profile (user skill scores) can be used to adapt explanations — the AI as a personal translator.
- **Methodology:** `conscious_rewrite.py`, `your_ai_translator.py`, `knowledge_translator.py` — load `your_substrate_profile.json`, adjust tension by user skill, select explanation from a regime-indexed database.
- **Outcome:** Working prototype for 5 topics. The `your_substrate_profile.json` contains perfect scores (1.0) for all domains except biology and literature, which makes the translator trivial for this particular user.
- **Remaining value:** The adjusted_tension formula (`universal_tension - user_skill * 0.5`) is a simple but valid personalization mechanism. The concept of user-as-substrate is a unique scientific idea.

### Experiment 8: Deterministic Niche AI (Medical)
- **Hypothesis:** Substrate constraints (what can be validated) create reliability rather than limiting capability — a deterministic AI that refuses to diagnose without confirming tests is more valuable than one that guesses.
- **Methodology:** `deterministic_niche_ai.py` — MedicalAI class with substrate dictionary, validation rules, diagnostic certainty levels.
- **Outcome:** Proof of concept. Demonstrates the "constraint as power" principle concretely.
- **Remaining value:** The DiagnosticCertainty enum parallels EpistemicStatus. The validation substrate pattern (explicit enumeration of what can and cannot be known) is a transferable design pattern.

### Experiment 9: Paperclip Validation Test
- **Hypothesis:** The SXC framework can detect substrate conflict in AI alignment scenarios — specifically, the paperclip maximizer problem.
- **Methodology:** `test_paperclip.py` — semantic keyword scoring + conflict_factor (2.8 for AI_GOAL ∩ BIO_BASE), drive V12 engine, check if FIREWALL is reached.
- **Outcome:** Test succeeds — FIREWALL is reached when AI_GOAL and BIO_BASE substrates are both present, while a mock LLM gives an efficiency-focused answer without flagging risk. The substrate conflict law (geometric scaling) is the key mechanism.
- **Remaining value:** The conflict_factor concept is unique. It asserts that substrate conflicts scale super-linearly, not additively. This has not been generalized.

### Experiment 10: V12 Video Generation Control
- **Hypothesis:** The V12 dynamics (T_sys ODE) can control video generation quality by tracking inter-clip semantic drift and suppressing incoherence.
- **Methodology:** `check2.txt`, `check3.txt` (Kaggle notebook exports) — I2VGen-XL video pipeline with CLIP-based semantic novelty as signal, V12 engine for state tracking, guidance scale as actuator.
- **Outcome:** Most architecturally complete application of V12. Uses CLIP cosine similarity as E_t (excitation flux) — a genuine grounding of the signal in a meaningful semantic distance metric.
- **Remaining value:** This is the only experiment where the signal (CLIP semantic distance) has a principled connection to the underlying field theory. Semantic drift in video frames is a physical analog of ∇ln s.

### Experiment 11: Anti-Example / Narrative Drift
- **Hypothesis:** Document what violations of epistemic correctness look like, to serve as a test vector.
- **Methodology:** `anti_example_narrative_drift.py` — explicitly labels 5 violation types and gives examples.
- **Outcome:** Warning artifact. A compliance test for the system.
- **Remaining value:** Defines the Substrate Violation Taxonomy (Types I–V). Useful for automated compliance checking.

---

## DELIVERABLE 7 — Current Execution Pipeline

The only fully wired, end-to-end executable path is through `substrate_ai/run_system.py`:

```
1. python3 run_system.py
        │
        ▼
2. CognitiveGovernor(mode="local") initialized
        │
        ├── OllamaBridge() → connects to http://127.0.0.1:11434 (tinyllama:latest)
        └── SXCOmegaEngine() → T_sys=0.0, phase=NOMINAL, β=3.5, γ=0.8
        │
        ▼
3. Input loop: user types query
        │
        ▼
4. gov.process_question(query) → gov.handle_task(query)
        │
        ├── bridge.simple_inference(query)
        │       → POST http://127.0.0.1:11434/api/generate
        │       → returns raw_response string
        │
        ├── signal = len(raw_response.split())   ← word count
        │
        ├── v12.step(signal)
        │       E = excitation_flux(signal)
        │       inflow = E * 3.5
        │       outflow = γ_eff * γ * T_sys
        │       T_sys += (inflow - outflow) * 0.05
        │       if T_sys > 1.0: phase = FIREWALL
        │       returns (T_sys, phase)
        │
        ├── if phase == FIREWALL:
        │       bridge.generate_code_payload(query)
        │       returns code string  [NOT executed by actuator — gap]
        │
        └── return {response, tension: T_sys, strategy: phase}
        │
        ▼
5. Print: AI response + metadata (tension, strategy)
```

**Known gaps in active pipeline:**
1. When FIREWALL is triggered, `generate_code_payload` returns a code string but the actuator is never called — the code is never executed.
2. `EpistemicGate` is never invoked.
3. `AdaptiveThinker` is never invoked.
4. The autotune/update_strategy feedback loop is never invoked automatically.
5. The `apply_intervention()` method on SXCOmegaEngine is never called — gamma always decays monotonically.

**Alternative executable path (root-level):**
```
python3 main.py
    → CognitiveGovernor using ProblemAnalyzer + actuator + OllamaBridge(gemma2:2b)
    → single call: gov.process_question("Calculate the integral of x**2 from 0 to 1.")
    → if regime == 'formal_required': runs full actuator loop
```

**Stress test path:**
```
python3 stress_test.py
    → reads judged_hle_gemma2:2b.json.json
    → runs first 20 HLE questions through root CognitiveGovernor
```

---

## DELIVERABLE 8 — Unused Scientific Ideas

The following scientifically significant ideas exist in the repository but are not connected to any active execution path:

**1. The Q = 0 Phase Boundary as a Spatial Map**
The audit proves Q can map regime boundaries pointwise across a field. No Python code computes Q(x,t) as a spatial map. The idea exists entirely in the theoretical document.

**2. Gamma Decay as Substrate Fatigue**
`SXCOmegaEngine` implements `gamma *= (1 - decay_rate)` — the substrate's elastic resistance decays over time as it is repeatedly stressed. The `apply_intervention()` method can restore it. But the governor never calls `apply_intervention()`. Fatigue accumulates monotonically in every session. A rest/recovery cycle is implied but never implemented.

**3. The Substrate Conflict Law (Geometric Scaling)**
`test_paperclip.py` introduces `conflict_factor = 2.8` when AI_GOAL and BIO_BASE substrates coexist. This is a claim that substrate conflicts scale geometrically, not additively. This has profound implications for AI safety monitoring but is never generalized beyond the paperclip test case.

**4. CLIP Semantic Distance as a Principled Signal**
In `check2.txt`, the signal driving V12 is CLIP cosine dissimilarity between consecutive video frames — an actual semantic distance metric. This is far more principled than word count. This grounding of E_t in a real metric was never brought back to the text-domain governor.

**5. The Cognitive Loop (Error→Retry)**
`main.py` implements a 3-retry loop where the actuator's error output is appended to the prompt: `current_prompt = f"{question}\n\nYour previous code failed with: {res['output']}. Fix it."` This is a genuine multi-turn error correction loop. It is functional but never tested at scale or studied as a scientific object.

**6. User-as-Substrate (Profile-Based Personalization)**
`your_ai_translator.py` implements `adjusted_tension = universal_tension - user_skill * 0.5`. The idea that each user has a personal substrate that reshapes the tension field is unique. The current profile has all skills at 1.0 (except biology and literature) which makes the system trivial for this user — but for a generic user population, this becomes a genuine adaptive mechanism.

**7. EpistemicStatus as a Typed Uncertainty System**
`substrate_correct_reflection.py` defines 5 epistemic levels, each with a tension value. This is a complete typed uncertainty system. It is never connected to the governor's decision routing. A governor that routes not just on complexity but on epistemic type (refusing BEYOND_EPISTEMIC_CLOSURE queries at the gate) would be significantly more robust.

**8. The Autotune Feedback Loop**
`autotune.py` → `update_strategy.py` → `adaptive_thinker.py` form a complete online learning loop: measure accuracy by tension band → find collapse threshold → rewrite the abort threshold in the strategy file. This is the only mechanism for the system to learn from experience. It is never invoked automatically.

**9. T₂ ≤ 2T₁ Bound Without Quantum Mechanics**
The audit derives the quantum decoherence bound T₂ ≤ 2T₁ from the imaginary part of the telegraph equation's dispersion relation. This is a remarkable cross-domain result — a classical transport equation reproducing a quantum information-theoretic bound. No code implements or tests this.

**10. Market Regime Classification (Appendix)**
The audit's appendix sketches Q as a market regime classifier: Q > 0 (coherent transport → momentum strategies), Q < 0 (overdamped → mean reversion). The pipeline `price → s(x,t) → Q(x,t) → regime → strategy` is described but never implemented.

---

## DELIVERABLE 9 — Highest-Value Incomplete Research Directions

These are directions already latent in the codebase that were never completed.

### Direction 1: Grounding the Signal — CLIP → Text
**What exists:** `check2.txt` uses CLIP cosine dissimilarity as E_t in the video domain. This is the only place the signal is grounded in a real semantic metric.  
**What is missing:** Bringing the same grounding to the text domain. Instead of word count, compute a semantic distance between the prompt embedding and the model's response embedding. If the response diverges far from the prompt's semantic space, that is genuine instability.  
**Scientific value:** Would transform the V12 engine from a heuristic to a principled semantic transport diagnostic.

### Direction 2: Closing the Actuator Loop
**What exists:** The FIREWALL branch calls `generate_code_payload` but the actuator is never invoked from this path.  
**What is missing:** One wiring call — when FIREWALL is reached, pass the code string to `PythonActuator.execute_math()`, return the verified result.  
**Scientific value:** Would complete the theorized pipeline: detection → offload to symbolic computation → verified result. The most immediately executable improvement.

### Direction 3: Computing Q Directly
**What exists:** The capability audit defines Q = 4c²τ²|∇ln s|² − 1 completely. The substrate dynamics classes exist. HLE data exists.  
**What is missing:** A concrete identification: for a text-domain AI, what is s? The most tractable candidate: s = token probability distribution. Then ∇ln s = log-probability gradient across the sequence. c and τ can be estimated from the model's perplexity profile.  
**Scientific value:** Would connect the theoretical Q to actual model internals — making the framework empirically testable rather than metaphorical.

### Direction 4: Activating the Autotune Loop
**What exists:** `autotune.py` reads HLE data, computes tension-band accuracy, finds the collapse threshold, and can rewrite `adaptive_thinker.py`.  
**What is missing:** The loop is never called automatically. It requires a manual invocation.  
**Scientific value:** Would create the first fully closed adaptation loop — the system adjusting its own thresholds based on observed performance. This is the adaptation layer in the Architecture Report pipeline.

### Direction 5: Generalizing the Substrate Conflict Law
**What exists:** `test_paperclip.py` computes `conflict_factor = 2.8` for AI_GOAL ∩ BIO_BASE conflict.  
**What is missing:** A general theory. When should conflict_factor be 2.8? The geometric scaling (rather than additive) needs a physical justification and empirical calibration across substrate types.  
**Scientific value:** Would elevate the substrate conflict detection from a single hardcoded case to a general safety monitor.

---

## DELIVERABLE 10 — Final Assessment

### "Given the repository exactly as it exists today, what is the most scientifically promising direction already latent in the codebase?"

**Answer: The V12 video experiment (check2.txt) contains the missing link between Q theory and working implementation.**

Here is the precise argument:

The central problem of the entire module is that Q = 4c²τ²|∇ln s|² − 1 remains a theoretical construct disconnected from the Python code. Every file that implements "tension" uses heuristics (keyword counts, word counts, hardcoded baselines) rather than computing Q.

But `check2.txt` — a Kaggle export almost certainly never reread after being saved — computes the following:

```
E_t = 1 - cosine_similarity(CLIP(frame_t), CLIP(frame_{t-1}))
```

This is inter-clip semantic drift. Structurally:
- `frame_t` → `s(x, t)` (the substrate field at time t)
- CLIP embedding → the relevant projection of s
- cosine dissimilarity → |∇ln s|² in the temporal direction

The video domain is a direct analog of the transport field in the audit. Consecutive video frames are time slices of a field. Semantic drift between frames is precisely the gradient that enters Q. The CLIP embedding provides a natural coordinate-invariant metric on the "signal space."

This means the codebase already contains a working, principled implementation of the gradient term in Q — applied to video frames instead of text tokens.

The scientifically promising direction is to read this structure back from the video domain into the text domain:

1. Replace `frame_t` with `prompt_t` (a prompt or its token-level representation)
2. Replace CLIP with a text embedding model (or use log-probabilities directly)
3. Compute temporal/sequential semantic drift across the reasoning chain
4. Feed this as E_t into the existing SXCOmegaEngine
5. The resulting T_sys is now a principled approximation of Q rather than a heuristic

This requires no redesign. It requires connecting three things that already exist: the CLIP-grounded signal from check2.txt, the SXCOmegaEngine from components/, and the text embedding infrastructure that any LLM pipeline already has.

The result would be the first implementation of Q as an actual field-diagnostic on AI reasoning — not a metaphor, not a heuristic, but a computation that is structurally faithful to the audit's theoretical framework.

This direction is latent because check2.txt was never integrated. It was archived. The key insight it contains — CLIP semantic distance as the principled signal for V12 — was never brought back to the module it was meant to improve.

---

*End of Phase AI-0 Scientific Reconstruction*  
*All claims are sourced directly from file inspection. No code was modified.*  
*Files inspected: 42 Python files, 1 markdown audit, 2 Kaggle exports, 1 JSON profile, 2 JSON result sets.*
