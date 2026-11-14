# Q CAPABILITY EXPERIMENT - HYPOTHESES PRE-REGISTRATION

**Experiment Date:** 2026-08-09  
**Status:** PRE-EXPERIMENTAL  
**Purpose:** Pre-register hypotheses and success criteria before data collection

---

## OVERVIEW

This document pre-registers all hypotheses, success criteria, and experimental designs for the Q capability experiment. The goal is to determine whether Q provides useful information for autonomous AI control beyond what can be obtained from raw text/LLM outputs.

---

## CENTRAL HYPOTHESIS

**Primary Hypothesis:** Q provides control-relevant information for autonomous AI systems that cannot be obtained from baseline variables (response length, token count, semantic similarity, etc.).

**Null Hypothesis:** Q provides no unique control-relevant information beyond baseline variables.

---

## EXPERIMENT 1 — STATE INFORMATION TEST

### Hypothesis
Q changes in ways that correspond to meaningful changes in the system's internal state that are not captured by baseline variables.

### Success Criteria
- Q must show statistically significant differences between conditions that represent different internal states
- These differences must not be explained by baseline variables (response length, semantic similarity, etc.)
- Effect size must be meaningful (Cohen's d > 0.5)

### Baseline Comparison
Compare Q against:
- Response length
- Token count
- Semantic similarity (cosine distance)
- Model confidence (if available)

### Success Threshold
- Q must outperform at least one baseline variable with statistical significance (p < 0.05)
- Effect size advantage over baseline: Δd > 0.2

### Failure Conditions
- Q shows no significant differences between internal states
- Q differences are fully explained by baseline variables
- Effect sizes are negligible (d < 0.2)

---

## EXPERIMENT 2 — PREDICTIVE POWER TEST

### Hypothesis
Q measured at time t predicts future outcomes at time t+k better than baseline variables.

### Success Criteria
- Q(t) must correlate with outcome(t+k) with r > 0.3
- Correlation must be statistically significant (p < 0.05)
- Q must improve prediction over baseline variables in regression analysis

### Baseline Comparisons
- Response length
- Token count
- Task difficulty rating
- Previous error count
- Random baseline
- Raw embedding similarity

### Success Threshold
- Q must achieve higher ROC-AUC than best baseline by ΔAUC > 0.05
- Or Q must achieve higher correlation by Δr > 0.1
- Must be statistically significant (p < 0.05)

### Failure Conditions
- Q shows no predictive correlation (r < 0.1)
- Q is outperformed by all baseline variables
- No statistical significance

---

## EXPERIMENT 3 — INTERVENTION TEST

### Hypothesis
Intervening based on Q values changes system behavior in a predictable and useful way.

### Success Criteria
- Low-Q condition → different behavior than high-Q condition
- Intervention effect size: Cohen's d > 0.5
- Effect must be statistically significant (p < 0.05)
- Intervention must improve task performance

### Intervention Design
- Low-Q condition: Q < -0.5 → trigger conservative strategy
- Medium-Q condition: -0.5 ≤ Q ≤ 0.5 → trigger standard strategy  
- High-Q condition: Q > 0.5 → trigger aggressive strategy

### Success Threshold
- Intervention must improve completion rate by Δ > 10%
- Or reduce error rate by Δ > 10%
- Must be statistically significant (p < 0.05)

### Failure Conditions
- No behavioral difference between Q conditions
- Intervention worsens performance
- No statistical significance

---

## EXPERIMENT 4 — AUTONOMOUS CONTROL TEST

### Hypothesis
A controller using Q achieves better autonomous performance than baseline controllers.

### Success Criteria
- Q-controller outperforms no-Q controller on task completion
- Q-controller outperforms random-signal controller
- Q-controller outperforms semantic-distance baseline controller

### Comparison Conditions
- A: LLM without Q
- B: LLM + Q controller
- C: LLM + random control signal
- D: LLM + semantic-distance baseline

### Success Threshold
- Q-controller must beat best baseline by Δcompletion > 15%
- Must be statistically significant (p < 0.05)
- Must show improvement in at least 2 of: completion, recovery, stability

### Failure Conditions
- Q-controller performs no better than baselines
- Q-controller performs worse than no-Q controller
- No statistical significance

---

## EXPERIMENT 5 — INFORMATION CONTENT TEST

### Hypothesis
Q contains independent information value beyond baseline variables for predicting future outcomes.

### Success Criteria
- Regression model (baseline + Q) outperforms model (baseline only)
- Improvement in R² by ΔR² > 0.05
- Improvement must be statistically significant (p < 0.05)

### Baseline Variables
- Response length
- Token count
- Semantic similarity
- Task difficulty
- Previous performance

### Success Threshold
- Adding Q must improve prediction by measurable margin
- Cross-validated improvement must be consistent
- Information gain (mutual information) > 0.01 bits

### Failure Conditions
- Adding Q does not improve prediction
- Improvement is not statistically significant
- Q information is redundant with baseline variables

---

## EXPERIMENT 6 — TEMPORAL DYNAMICS TEST

### Hypothesis
Q exhibits meaningful temporal patterns that correspond to system state transitions.

### Success Criteria
- Q shows persistence (autocorrelation > 0.3)
- Q shows meaningful transitions between regimes
- Q precursors predict state changes

### Pattern Detection
- Persistence: autocorrelation at lag 1
- Transitions: threshold crossings
- Recovery signatures: post-error behavior
- Precursor signatures: pre-failure patterns

### Success Threshold
- At least one meaningful temporal pattern with statistical significance
- Pattern must have predictive value (p < 0.05)
- Pattern must not be explainable by baseline variables

### Failure Conditions
- No meaningful temporal patterns detected
- Patterns are explained by baseline variables
- No statistical significance

---

## EXPERIMENT 7 — COUNTERFACTactual TEST

### Hypothesis
Q responds to decision-situation changes rather than semantic variation alone.

### Success Criteria
- Q changes when decision situation changes while semantics are constant
- Q remains stable when semantics change while decision situation is constant
- Effect must be statistically significant (p < 0.05)

### Test Design
- Condition A: Same semantics, different decision situations
- Condition B: Different semantics, same decision situation

### Success Threshold
- Q must discriminate decision situations with d > 0.5
- Must be statistically significant (p < 0.05)
- Effect must survive semantic controls

### Failure Conditions
- Q tracks only semantic variation
- Q does not respond to decision situations
- No statistical significance

---

## EXPERIMENT 8 — TASK GENERALIZATION TEST

### Hypothesis
Q's capability generalizes across multiple task classes.

### Success Criteria
- Q shows consistent predictive/control value across ≥ 3 task classes
- Effect sizes must be consistent (variation < 30%)
- Must be statistically significant in each class (p < 0.05)

### Task Classes
- Reasoning
- Planning
- Error recovery
- Sequential decision making
- Contradiction handling
- Resource/state management

### Success Threshold
- Success in ≥ 3 of 6 task classes
- Consistent effect direction across classes
- Meta-analysis shows overall significance (p < 0.05)

### Failure Conditions
- Success in < 2 task classes
- Inconsistent effects across classes
- No overall statistical significance

---

## EXPERIMENT 9 — MODEL GENERALIZATION TEST

### Hypothesis
Q's capability generalizes across different LLM models.

### Success Criteria
- Q shows consistent effects across ≥ 2 models
- Effect sizes must be reasonably consistent (variation < 50%)
- Must be statistically significant in each model (p < 0.05)

### Models to Test
- qwen2.5-coder:1.5b (primary)
- gemma2:2b (secondary)
- deepseek-coder:latest (tertiary if needed)

### Success Threshold
- Success in ≥ 2 models
- Consistent effect direction
- No model × Q interaction (p > 0.05 for interaction)

### Failure Conditions
- Success in only 1 model
- Inconsistent effects across models
- Significant model × Q interaction

---

## EXPERIMENT 10 — THEORETICAL-Q TEST

### Hypothesis
The theoretical Q (if computable) has better predictive/control properties than the implemented semantic Q.

### Success Criteria
- Theoretical Q must be computable from available substrate state
- Theoretical Q must outperform semantic Q by measurable margin
- Improvement must be statistically significant (p < 0.05)

### Prerequisites
- Required substrate variables must exist in backend
- Must be able to compute ∇ln s from actual state
- Must have physical parameters c and τ

### Success Threshold
- Theoretical Q achieves ΔAUC > 0.1 over semantic Q
- Or theoretical Q achieves Δr > 0.15 over semantic Q
- Must be statistically significant (p < 0.05)

### Failure Conditions
- Theoretical Q cannot be computed from available state
- Theoretical Q performs no better than semantic Q
- No statistical significance

---

## EXPERIMENT 11 — NECESSITY TEST

### Hypothesis
Q is necessary for the autonomous capability it appears to control.

### Success Criteria
- Removing Q causes reproducible loss of capability
- Competing signals cannot reproduce the same effect
- Loss must be statistically significant (p < 0.05)

### Competing Signals
- Random signal
- Semantic-distance signal
- Simple scalar heuristic
- Strongest baseline variable

### Success Threshold
- Capability loss with Q removal: Δ > 20%
- Competing signals cannot recover capability (Δ < 5%)
- Must be statistically significant (p < 0.05)

### Failure Conditions
- Removing Q causes no capability loss
- Competing signals can reproduce the effect
- No statistical significance

---

## EXPERIMENT 12 — SUFFICIENT-CAPABILITY TEST

### Hypothesis
Q alone is sufficient for the specific capability it appears to control.

### Success Criteria
- Q-based controller achieves the capability without additional signals
- Capability is reproducible across trials
- Must be statistically significant (p < 0.05)

### Capability Categories
- State estimation
- Instability detection
- Uncertainty detection
- Regime detection
- Error prediction
- Action selection
- Recovery triggering
- Attention allocation
- Planning modulation
- Persistence control

### Success Threshold
- Q alone achieves the capability with success rate > 70%
- Must be statistically significant (p < 0.05)
- Must be reproducible across trials

### Failure Conditions
- Q alone insufficient for the capability
- Requires additional signals
- No statistical significance

---

## STATISTICAL STANDARDS

### Significance Threshold
- Primary hypothesis tests: α = 0.05
- Multiple comparisons: Bonferroni correction applied
- Effect sizes always reported with p-values

### Effect Size Standards
- Small: d = 0.2, r = 0.1, ΔAUC = 0.02
- Medium: d = 0.5, r = 0.3, ΔAUC = 0.05
- Large: d = 0.8, r = 0.5, ΔAUC = 0.1

### Sample Size Requirements
- Minimum n = 30 per condition for t-tests
- Minimum n = 100 for correlation analysis
- Minimum n = 50 per group for group comparisons
- Power analysis: target power = 0.8

### Multiple Testing Correction
- For k simultaneous tests: α_corrected = α/k
- Or use false discovery rate (FDR) control
- Report both corrected and uncorrected p-values

---

## DECISION FRAMEWORK

### Final Classification Criteria

**NO FUNCTION:**
- Fails all predictive/control tests
- No significant effects in any experiment
- Effect sizes negligible across all tests

**DESCRIPTIVE SIGNAL:**
- Describes system properties but no predictive value
- Significant correlations but no intervention effects
- Fails intervention and control tests

**PREDICTIVE SIGNAL:**
- Predicts future outcomes with statistical significance
- No demonstrated causal control value
- Fails intervention tests

**CONTROL SIGNAL:**
- Intervening through Q changes behavior reliably
- Statistical significance in intervention tests
- May not be necessary (competitors can reproduce)

**NECESSARY CONTROL VARIABLE:**
- Removing Q causes capability loss
- Competitors cannot reproduce effect
- Statistical significance in necessity test

**AUTONOMY-RELEVANT STATE VARIABLE:**
- Succeeds in control tests
- Generalizes across tasks and models
- Survives baseline comparisons
- Demonstrates necessity
- Shows temporal dynamics
- Contains independent information

---

## PRE-REGISTRATION CERTIFICATION

**Hypotheses:** All hypotheses are pre-registered before data collection  
**Success Criteria:** All success criteria are defined in advance  
**Analysis Plan:** Statistical methods are specified before execution  
**Data Collection:** Raw data will be preserved regardless of outcome  
**Interpretation:** Results will be interpreted according to pre-registered criteria

**Deviation Policy:** Any deviation from pre-registered criteria will be documented and justified in the final report.

---

**Registration Date:** 2026-08-09  
**Status:** PRE-EXPERIMENTAL  
**Next Step:** Build experimental harness and begin data collection
