# Q CAPABILITY EXPERIMENT

**Experiment Date:** 2026-08-09  
**Status:** IN PROGRESS  
**Objective:** Determine what kind of Q-like quantity can provide the state, prediction, and control function required for autonomous AI

---

## OVERVIEW

This experiment aims to determine, experimentally and definitively, what a Q-like state quantity can actually do for the proposed autonomous-AI backend.

**CORE QUESTION:** What kind of Q-like quantity, if any, can actually provide the function required for autonomous AI?

---

## BACKGROUND

The previous work established:
1. The theoretical framework contains a mathematical quantity: Q = 4c²τ²|∇ln s|² - 1
2. The old backend quantity called Q was embedding-derived semantic distance
3. Experiments demonstrated the old implementation was mathematically tied to semantic-distance construction

**That issue is CLOSED for this experiment.**

**Current Question:** What kind of Q-like quantity can actually provide the required autonomous control function?

---

## EXPERIMENTAL STRUCTURE

```
q_capability_experiment/
├── README.md (this file)
├── EXPERIMENT_PLAN.md (detailed experimental plan)
├── RESULTS.md (experimental results)
├── FINAL_Q_CAPABILITY_REPORT.md (final classification)
├── raw/ (raw experimental data)
├── plots/ (visualizations)
└── code/ (experimental code)
```

---

## CORE HYPOTHESIS

For autonomous-AI to be meaningful, the backend needs a measurable state quantity capable of detecting changes in the system's internal informational/dynamical condition.

**We test whether a candidate Q can provide:**
- A. State Sensitivity
- B. State Discrimination
- C. Temporal Sensitivity
- D. Precursor Detection
- E. Predictive Power
- F. Intervention Value
- G. Hysteresis/Memory
- H. Non-Redundancy
- I. Control Utility

---

## TARGET CLASSIFICATION

**Category 0:** No useful Q-like quantity identified  
**Category 1:** Q measures real property but has no predictive/control value  
**Category 2:** Q predicts future state/failure but does not improve intervention  
**Category 3:** Q provides independent state information and improves prediction  
**Category 4:** Q provides independent state information, predicts future regime changes, and Q-controlled intervention measurably improves autonomous performance

**Category 4 is the target required for autonomous-life hypothesis.**

---

## EXPERIMENTS

See EXPERIMENT_PLAN.md for detailed experimental designs:
- Experiment 1: Static State Discrimination
- Experiment 2: Temporal State Evolution
- Experiment 3: Perturbation Response
- Experiment 4: Pre-Failure Lead Time
- Experiment 5: Predictive Test
- Experiment 6: Counterfactual Test
- Experiment 7: Intervention Test
- Experiment 8: Threshold Robustness
- Experiment 9: Model Independence
- Experiment 10: Null/Baseline Test
- Critical Test: Information Gain

---

## AVAILABLE RESOURCES

### Backend Components
- actuator.py
- adaptive_thinker.py
- ai_monitor.py
- autotune.py
- cognitive_governor.py
- cognitive_governor_final.py
- main.py
- ollama_bridge.py
- problem_analyzer.py
- substrate_core.py
- substrate_ai.py
- substrate_ai/components/
- sim_world/
- benchmark_runner.py
- benchmark_scorer.py

### Ollama Models
- qwen2.5-coder:1.5b (primary, smallest)
- gemma2:2b (secondary)
- gemma2:latest (tertiary, largest)
- deepseek-coder:latest (alternative small model)

---

## PROGRESS

- [x] Experimental plan created
- [ ] Backend analysis (Phase 1)
- [ ] Experiments 1-3 (State Characterization)
- [ ] Experiments 4-6 (Prediction & History)
- [ ] Experiments 7-10 (Control & Validation)
- [ ] Information gain analysis
- [ ] Final classification

---

## NO CHEATING RULES

- Do not alter Q after observing results
- Do not tune Q to test set
- Do not define success after results are known
- Do not replace failed trials
- Do not discard inconvenient results
- Do not redefine "state" after observing output
- Do not call semantic similarity "substrate state"
- Do not claim substrate grounding without measurable variables

---

## FINAL OUTPUT

The experiment will produce:
- RESULTS.md (experimental results)
- FINAL_Q_CAPABILITY_REPORT.md (final classification 0-4)
- Raw data in raw/
- Visualizations in plots/
- Experimental code in code/

---

**Status:** PHASE 1 - BACKEND ANALYSIS  
**Next Step:** Inspect existing backend components to identify available state variables and candidate Q-like quantities
