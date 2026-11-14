# Q CAPABILITY EXPERIMENT PLAN

**Experiment Date:** 2026-08-09  
**Status:** PLANNING  
**Objective:** Determine what kind of Q-like quantity can provide the state, prediction, and control function required for autonomous AI

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

## EXPERIMENTAL OVERVIEW

### Target Classification

**Category 0:** No useful Q-like quantity identified  
**Category 1:** Q measures real property but has no predictive/control value  
**Category 2:** Q predicts future state/failure but does not improve intervention  
**Category 3:** Q provides independent state information and improves prediction  
**Category 4:** Q provides independent state information, predicts future regime changes, and Q-controlled intervention measurably improves autonomous performance

**Category 4 is the target required for autonomous-life hypothesis.**

---

## EXPERIMENT 1 — STATIC STATE DISCRIMINATION

### Objective
Test whether Q can distinguish states with identical surface language but different underlying informational conditions.

### State Types to Test
1. Internally consistent state
2. Contradictory state
3. Incomplete state
4. Unstable state
5. Noisy state
6. Overloaded state
7. Convergent state
8. Divergent state

### Method
- Construct task prompts that are lexically similar but represent different states
- Measure Q and all control variables
- Test if Q distinguishes states beyond semantic similarity

### Success Criteria
- Q must show statistically significant differences between state types
- Effect size: Cohen's d > 0.5
- Must outperform semantic similarity baseline

### Sample Size
- 20 trials per state type
- Total: 160 trials

---

## EXPERIMENT 2 — TEMPORAL STATE EVOLUTION

### Objective
Test whether Q tracks transitions: stable → perturbation → instability → recovery

### Method
- Run agent through defined state sequence
- Record at every timestep: Q, Q derivative, model output, correctness, latency, planner state
- Plot Q(t) and analyze transition tracking

### Success Criteria
- Q must show systematic changes during state transitions
- ΔQ must be statistically significant at transition points
- Q must track progression better than baseline variables

### Sample Size
- 10 complete state sequences
- ~5-10 timesteps per sequence
- Total: 50-100 timesteps

---

## EXPERIMENT 3 — PERTURBATION RESPONSE

### Objective
Test whether Q responds systematically to perturbation type and magnitude.

### Perturbation Types
- Irrelevant information
- Relevant information
- Contradictory information
- Repeated information
- Missing information
- Noisy information
- Task switching
- Increased complexity
- Misleading instruction
- Recovery information

### Method
- Apply controlled perturbations to stable state
- Measure ΔQ for each perturbation type
- Compare against text similarity response

### Success Criteria
- ΔQ must vary systematically with perturbation type
- Effect must be statistically significant (p < 0.05)
- Must outperform semantic similarity

### Sample Size
- 10 trials per perturbation type
- Total: 100 trials

---

## EXPERIMENT 4 — PRE-FAILURE LEAD TIME

### Objective
Test whether Q changes before failure and how many timesteps in advance.

### Method
- Construct tasks with gradually induced failure
- Record Q(t), failure(t), correctness(t)
- Analyze Q changes before failure events

### Success Criteria
- Q must change before failure with statistical significance
- Lead time must be at least 1 timestep
- Q(t) must predict failure probability with AUC > 0.7

### Sample Size
- 50 failure-inducing sequences
- Multiple timesteps per sequence
- Total: ~200-300 timestep observations

---

## EXPERIMENT 5 — PREDICTIVE TEST

### Objective
Test whether Q(t) predicts future failures at t+1, t+2, t+5, t+10.

### Method
- Train no model initially
- Test Q alone vs baselines (text similarity, latency, token count, planner state)
- Report predictive performance with confidence intervals

### Success Criteria
- Q must outperform best baseline by ΔAUC > 0.05
- Must be statistically significant (p < 0.05)
- Must provide incremental information

### Sample Size
- 200 trials with temporal follow-up
- Multiple prediction horizons

---

## EXPERIMENT 6 — COUNTERFACTactual TEST

### Objective
Test whether Q retains history information when surface text is similar.

### Method
- Construct run pairs with different histories but similar final text
- Compare Q values between runs
- Test if Q retains history information

### Success Criteria
- Q must differ between runs with different histories
- Effect must be statistically significant
- Must demonstrate memory beyond surface text

### Sample Size
- 20 run pairs
- Total: 40 trials

---

## EXPERIMENT 7 — INTERVENTION TEST

### Objective
Test whether Q-controlled intervention improves outcomes.

### Intervention Policy
```
IF Q enters regime R:
    intervene (reconsider, seek info, switch strategy, etc.)
```

### Comparison Conditions
- A. No intervention
- B. Random intervention
- C. Fixed-time intervention
- D. Q-triggered intervention

### Success Criteria
- Q-triggered intervention must outperform appropriate baselines
- Must reduce failure rate by Δ > 10%
- Must be statistically significant (p < 0.05)

### Sample Size
- 50 trials per condition
- Total: 200 trials

---

## EXPERIMENT 8 — THRESHOLD ROBUSTNESS

### Objective
Test whether Q regime boundary is stable across tasks, models, and conditions.

### Method
- Use development set to determine thresholds
- Evaluate on held-out set
- Test stability across tasks, models, perturbations

### Success Criteria
- Threshold must remain stable (variation < 20%)
- Must work across multiple task types
- Must work across at least 2 models

### Sample Size
- Development: 100 trials
- Held-out: 100 trials per condition

---

## EXPERIMENT 9 — MODEL INDEPENDENCE

### Objective
Test whether Q is tied to one model's linguistic behavior.

### Method
- Run key experiments with qwen2.5-coder:1.5b and gemma2:2b
- Compare Q behavior across models

### Success Criteria
- Q must show consistent effects across models
- Effect direction must be consistent
- No significant model × Q interaction

### Sample Size
- Repeat key experiments with both models
- 50 trials per model per experiment

---

## EXPERIMENT 10 — NULL/BASELINE TEST

### Objective
Compare Q against trivial baselines (random, text length, embedding distance, token count, latency).

### Method
- Create identical experimental conditions
- Compare Q performance against baselines
- Use statistical tests to determine superiority

### Success Criteria
- Q must outperform all trivial baselines
- Must be statistically significant
- Must show meaningful effect size

### Sample Size
- 50 trials per baseline condition
- Total: 300 trials

---

## CRITICAL TEST: INFORMATION GAIN

### Objective
Calculate whether Q adds information beyond existing backend variables.

### Method
- Compare Model 1 (baseline variables) vs Model 2 (baseline + Q)
- Use likelihood ratio test or AIC/BIC
- Quantify incremental contribution

### Success Criteria
- Adding Q must improve prediction/control by ΔR² > 0.05
- Must be statistically significant
- Must demonstrate independent information value

### Sample Size
- 200 trials with full variable set
- Cross-validation

---

## STATISTICAL REQUIREMENTS

### Sample Size Guidelines
- Small trials (n < 10): Debugging only
- Medium trials (n = 10-30): Preliminary investigation
- Large trials (n ≥ 30): Acceptable for claims
- For final claims: n ≥ 50 preferred

### Required Reporting
- Exact sample sizes (n)
- Effect sizes (Cohen's d, correlation coefficients)
- Confidence intervals (95%)
- P-values where appropriate
- Failure/timeout rates
- Separation of experimental vs model vs infrastructure failure

### Statistical Methods
- For group comparisons: t-tests, Mann-Whitney U
- For correlations: Pearson, Spearman
- For prediction: ROC-AUC, precision/recall
- For intervention: McNemar, chi-square
- For information gain: likelihood ratio, AIC/BIC

---

## BACKEND INVESTIGATION

### Available Components to Inspect
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

## EXPERIMENTAL PIPELINE

### Phase 1: Backend Analysis
- Inspect existing components for state variables
- Identify candidate Q-like quantities
- Build measurement pipeline

### Phase 2: Experiments 1-3 (State Characterization)
- Static state discrimination
- Temporal evolution
- Perturbation response

### Phase 3: Experiments 4-6 (Prediction & History)
- Pre-failure lead time
- Predictive testing
- Counterfactual testing

### Phase 4: Experiments 7-10 (Control & Validation)
- Intervention testing
- Threshold robustness
- Model independence
- Null/baseline testing

### Phase 5: Information Gain & Final Classification
- Information gain analysis
- Final category classification (0-4)

---

## CANDIDATE Q DEFINITIONS

### Candidate 1: Original Semantic Q
```
Q_semantic = 4c²τ²(cosine_distance)² - 1
```
Based on sentence-transformer embeddings.

### Candidate 2: Text-Based Q
```
Q_text = 4c²τ²(1 - Jaccard_similarity)² - 1
```
Based on word overlap.

### Candidate 3: Structural Q
```
Q_structural = 4c²τ²(structural_complexity)² - 1
```
Based on response structure metrics.

### Candidate 4: Dynamic Q
```
Q_dynamic = 4c²τ²(Δresponse_characteristics)² - 1
```
Based on changes in response characteristics.

### Candidate 5: Composite Q
```
Q_composite = f(Q_semantic, Q_text, Q_structural, Q_dynamic)
```
Combination of multiple signals.

---

## SUCCESS MATRIX

### For Category 4 Classification
- [ ] State sensitivity demonstrated
- [ ] State discrimination demonstrated
- [ ] Temporal sensitivity demonstrated
- [ ] Precursor detection demonstrated
- [ ] Predictive power demonstrated
- [ ] Intervention value demonstrated
- [ ] Hysteresis/memory demonstrated
- [ ] Non-redundancy demonstrated
- [ ] Control utility demonstrated
- [ ] Model independence demonstrated
- [ ] Threshold robustness demonstrated
- [ ] Information gain demonstrated

All must be satisfied for Category 4.

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

## FINAL QUESTIONS TO ANSWER

1. What exactly does the candidate Q measure?
2. What backend variable produces it?
3. Is it independent of semantic similarity?
4. Does it respond to internal state changes?
5. Does it respond before failure?
6. Does it predict future state?
7. Does it contain information not already available elsewhere?
8. Can an autonomous controller use it?
9. Does using it improve outcomes?
10. What physical/informational interpretation is justified?
11. What is the minimum architecture required?
12. What claims must NOT be made?

---

## DELIVERABLES

- README.md (overview)
- EXPERIMENT_PLAN.md (this document)
- RESULTS.md (experimental results)
- FINAL_Q_CAPABILITY_REPORT.md (final classification)
- raw/ (raw experimental data)
- plots/ (visualizations)
- code/ (experimental code)

---

**Plan Status:** COMPLETE  
**Next Step:** Build experimental harness and begin Phase 1 backend analysis
