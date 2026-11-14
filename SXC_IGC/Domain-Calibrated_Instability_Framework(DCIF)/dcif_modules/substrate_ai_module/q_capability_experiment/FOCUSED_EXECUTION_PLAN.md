# Q CAPABILITY EXPERIMENT - FOCUSED EXECUTION PLAN

**Analysis Date:** 2026-08-09  
**Status:** PHASE 1 COMPLETE - BACKEND ANALYSIS  
**Next Phase:** EXPERIMENTAL TESTING OF HIGH-PRIORITY CANDIDATES

---

## BACKEND ANALYSIS RESULTS

### Available State Variables

**High Control Potential Candidates:**
1. **T_sys** (SXCOmegaEngine) - Dynamic state variable from V12 ODE system
2. **Q_synthetic** (UnifiedGovernor) - Potential composite variable

**Medium Control Potential Candidates:**
3. **tension** (ProblemAnalyzer) - Heuristic based on keyword detection
4. **regime** (SubstrateDynamics) - Categorical classification on tension

**Low Control Potential Candidates:**
5. **Q_from_QField** - Proven semantic distance (previous audit)

---

## CRITICAL DECISION POINT

Based on the backend analysis, I must make a strategic decision:

**Option A:** Test T_sys (highest priority)
- **Advantage:** Dynamic, temporal, has physical basis from ODE system
- **Disadvantage:** Requires ODE system integration, may be complex

**Option B:** Test tension (medium priority)
- **Advantage:** Simple, already integrated, immediately testable
- **Disadvantage:** Heuristic-based, may lack true state sensitivity

**Option C:** Test Q_synthetic (highest priority)
- **Advantage:** Could leverage multiple information sources
- **Disadvantage:** Must be designed and implemented first

**Option D:** Test all candidates systematically
- **Advantage:** Comprehensive coverage
- **Disadvantage:** Time-intensive, may waste effort on low-potential candidates

---

## DECISION: FOCUSED STRATEGY

**Primary Focus:** T_sys (SXCOmegaEngine)
- **Rationale:** Highest control potential, dynamic/temporal nature, physical basis
- **Strategy:** Test whether T_sys provides the required state, prediction, and control function

**Secondary Focus:** tension (ProblemAnalyzer) 
- **Rationale:** Immediately testable, provides baseline comparison
- **Strategy:** Use as baseline to compare against T_sys

**Tertiary Focus:** Q_synthetic (if T_sys fails)
- **Rationale:** High potential but requires implementation
- **Strategy:** Only pursue if T_sys fails to demonstrate required function

**Explicit Decision:** DO NOT test Q_from_QField
- **Rationale:** Previous audit definitively established it as semantic distance
- **Strategy:** Confirmed low control potential, deprioritize

---

## REFOCUSED EXPERIMENTAL PLAN

### EXPERIMENT 1 — T_sys STATE SENSITIVITY

**Objective:** Test whether T_sys changes when the system's internal state changes.

**Method:**
- Use SXCOmegaEngine to compute T_sys
- Construct controlled state variations (stable, perturbed, unstable)
- Measure T_sys response
- Compare against baseline variables

**Success Criteria:**
- T_sys must show statistically significant differences between states
- Effect size: Cohen's d > 0.5
- Must outperform tension baseline

**Sample Size:** 20 trials per state type (60 total)

---

### EXPERIMENT 2 — T_sys TEMPORAL DYNAMICS

**Objective:** Test whether T_sys tracks state transitions over time.

**Method:**
- Run agent through: stable → perturbation → instability → recovery
- Record T_sys(t) at each timestep
- Analyze transition tracking
- Plot temporal evolution

**Success Criteria:**
- T_sys must show systematic changes during transitions
- ΔT_sys must be statistically significant at transition points
- Must track progression better than tension

**Sample Size:** 10 complete sequences (50-100 timesteps)

---

### EXPERIMENT 3 — T_sys PRECURSOR DETECTION

**Objective:** Test whether T_sys changes before failure.

**Method:**
- Construct tasks with gradually induced failure
- Record T_sys(t), failure(t), correctness(t)
- Analyze lead time: how many timesteps before failure does T_sys change?

**Success Criteria:**
- T_sys must change before failure with statistical significance
- Lead time ≥ 1 timestep
- T_sys(t) must predict failure probability with AUC > 0.7

**Sample Size:** 50 failure-inducing sequences (200-300 timesteps)

---

### EXPERIMENT 4 — T_sys PREDICTIVE POWER

**Objective:** Test whether T_sys(t) predicts future failures at t+1, t+2, t+5, t+10.

**Method:**
- Test T_sys alone vs tension alone vs combined
- Report predictive performance with confidence intervals
- Use ROC-AUC as primary metric

**Success Criteria:**
- T_sys must outperform tension by ΔAUC > 0.05
- Must be statistically significant (p < 0.05)
- Must provide incremental information

**Sample Size:** 200 trials with temporal follow-up

---

### EXPERIMENT 5 — T_sys INTERVENTION TEST

**Objective:** Test whether T_sys-controlled intervention improves outcomes.

**Intervention Policy:**
```
IF T_sys > threshold_high:
    intervene (reconsider, seek info, switch strategy)
IF T_sys < threshold_low:
    conservative strategy
ELSE:
    standard strategy
```

**Comparison Conditions:**
- A. No intervention
- B. Random intervention
- C. Tension-triggered intervention
- D. T_sys-triggered intervention

**Success Criteria:**
- T_sys-triggered intervention must outperform appropriate baselines
- Must reduce failure rate by Δ > 10%
- Must be statistically significant (p < 0.05)

**Sample Size:** 50 trials per condition (200 total)

---

### EXPERIMENT 6 — T_sys THRESHOLD ROBUSTNESS

**Objective:** Test whether T_sys regime boundary is stable across conditions.

**Method:**
- Use development set to determine thresholds
- Evaluate on held-out set
- Test stability across tasks, models, perturbations

**Success Criteria:**
- Threshold must remain stable (variation < 20%)
- Must work across multiple task types
- Must work across at least 2 models

**Sample Size:** Development: 100 trials, Held-out: 100 trials per condition

---

### EXPERIMENT 7 — T_sys MODEL INDEPENDENCE

**Objective:** Test whether T_sys is tied to one model's behavior.

**Method:**
- Run key experiments with qwen2.5-coder:1.5b and gemma2:2b
- Compare T_sys behavior across models

**Success Criteria:**
- T_sys must show consistent effects across models
- Effect direction must be consistent
- No significant model × T_sys interaction

**Sample Size:** 50 trials per model per experiment

---

### EXPERIMENT 8 — T_sys INFORMATION GAIN

**Objective:** Calculate whether T_sys adds information beyond existing variables.

**Method:**
- Compare Model 1 (tension) vs Model 2 (tension + T_sys)
- Use likelihood ratio test or AIC/BIC
- Quantify incremental contribution

**Success Criteria:**
- Adding T_sys must improve prediction/control by ΔR² > 0.05
- Must be statistically significant
- Must demonstrate independent information value

**Sample Size:** 200 trials with full variable set, cross-validation

---

## SUCCESS MATRIX FOR T_sys

### For Category 4 Classification
- [ ] State sensitivity demonstrated (Exp 1)
- [ ] Temporal sensitivity demonstrated (Exp 2)
- [ ] Precursor detection demonstrated (Exp 3)
- [ ] Predictive power demonstrated (Exp 4)
- [ ] Intervention value demonstrated (Exp 5)
- [ ] Threshold robustness demonstrated (Exp 6)
- [ ] Model independence demonstrated (Exp 7)
- [ ] Information gain demonstrated (Exp 8)

All must be satisfied for Category 4.

---

## FALLBACK STRATEGY

### If T_sys Fails Category 4 Requirements

**Level 1 Failure (no state sensitivity):**
- Switch to tension testing
- Test whether heuristic provides required function
- If tension fails, proceed to Level 2

**Level 2 Failure (no temporal dynamics):**
- Design and implement Q_synthetic
- Combine T_sys + tension + other signals
- Test composite variable

**Level 3 Failure (no predictive value):**
- Conclude no useful Q-like quantity exists
- Classify as Category 0

---

## EXPERIMENTAL PRIORITY ORDER

1. **EXP 1:** T_sys State Sensitivity (Gatekeeper)
2. **EXP 2:** T_sys Temporal Dynamics (Gatekeeper)
3. **EXP 3:** T_sys Precursor Detection (Gatekeeper)
4. **EXP 4:** T_sys Predictive Power (Gatekeeper)
5. **EXP 5:** T_sys Intervention Test (Critical)
6. **EXP 6:** T_sys Threshold Robustness (Validation)
7. **EXP 7:** T_sys Model Independence (Validation)
8. **EXP 8:** T_sys Information Gain (Validation)

**Gatekeeper Experiments:** If any gatekeeper fails, re-evaluate strategy before proceeding.

---

## STATISTICAL STANDARDS

### Effect Size Requirements
- State sensitivity: Cohen's d > 0.5
- Predictive power: ΔAUC > 0.05
- Intervention: Δ failure rate > 10%

### Significance Thresholds
- Primary tests: α = 0.05
- Multiple comparisons: Bonferroni correction
- Confidence intervals: 95%

### Sample Size Requirements
- Gatekeeper experiments: n ≥ 20 per condition
- Validation experiments: n ≥ 50 per condition
- Information gain: n ≥ 200 for reliable estimation

---

## DELIVERABLES

### For Each Experiment
- Raw data (CSV/JSONL)
- Statistical analysis
- Effect sizes and confidence intervals
- Plots/visualizations
- Pass/fail determination

### Final Deliverables
- RESULTS.md (all experimental results)
- FINAL_Q_CAPABILITY_REPORT.md (final classification 0-4)
- Complete raw data archive
- Analysis code

---

## TIMELINE ESTIMATE

### Phase 1: Backend Analysis (COMPLETE)
- Status: Done
- Output: BACKEND_STATE_ANALYSIS.md

### Phase 2: T_sys Gatekeeper Experiments (NEW FOCUS)
- EXP 1-4: State sensitivity, temporal dynamics, precursor detection, predictive power
- Estimated time: 2-3 hours (including Ollama latency)

### Phase 3: T_sys Intervention Test (CRITICAL)
- EXP 5: Intervention experiment
- Estimated time: 1-2 hours

### Phase 4: T_sys Validation Experiments
- EXP 6-8: Threshold robustness, model independence, information gain
- Estimated time: 2-3 hours

### Phase 5: Final Classification
- Data analysis, report generation
- Estimated time: 1 hour

**Total Estimated Time:** 6-9 hours

---

## CRITICAL SUCCESS FACTORS

1. **Ollama Reliability:** Must handle timeouts gracefully
2. **SXCOmegaEngine Integration:** Must work with experimental harness
3. **Statistical Rigor:** Must meet pre-registered criteria
4. **No Cheating:** Must follow all experimental discipline rules
5. **Clear Decision:** Must classify into exactly one category

---

**Plan Status:** FOCUSED ON T_sys TESTING  
**Next Step:** Build experimental harness for T_sys testing  
**Fallback Strategy:** Tension testing if T_sys fails  
**Final Fallback:** Q_synthetic if T_sys and tension fail
