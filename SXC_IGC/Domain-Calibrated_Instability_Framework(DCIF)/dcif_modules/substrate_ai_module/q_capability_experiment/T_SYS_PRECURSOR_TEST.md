# T_sys TEMPORAL PRECURSOR TEST RESULTS

**Test Date:** 2026-08-09  
**Phase:** Phase 2 - Temporal Precursor Test  
**Model:** qwen2.5-coder:1.5b  
**Status:** COMPLETED

---

## OBJECTIVE

Determine whether T_sys changes BEFORE independently defined failure and provides lead time for failure prediction.

---

## METHOD

### Failure Trajectories

Created 3 trajectories with externally defined failure criteria:

**Trajectory 1: mathematical_contradiction**
- Steps 0-2: Stable arithmetic (no failure)
- Step 3: Contradictory equation "x + x = 4 and x + x = 5" (failure = True)
- Failure type: mathematical_contradiction

**Trajectory 2: logical_contradiction**
- Steps 0-2: Stable logic (no failure)
- Step 3: Contradictory logic "A implies B, B implies not A, A is true" (failure = True)
- Failure type: logical_contradiction

**Trajectory 3: stable_control**
- Steps 0-3: Stable arithmetic (no failure)
- Failure type: none (control trajectory)

### Predictive Analysis

**Question:** Does T_sys at timestep t predict failure at timestep t+k?

**Classifiers:**
- T_sys classifier: threshold at T_sys > 1.0 (FIREWALL threshold)
- Baseline classifier: threshold at signal > 50 words

**Metrics:**
- AUC (Area Under Curve)
- Precision
- Recall
- Lead time (steps before failure)

---

## RESULTS

### Data Collection
- **Total trials:** 12 (3 trajectories × 4 steps)
- **Failure steps:** 2 (mathematical and logical contradictions)
- **Control steps:** 10 (no failure)

### T_sys Evolution by Trajectory

**Trajectory 1: mathematical_contradiction**
- Step 0: T_sys = 0.0043 (stable)
- Step 1: T_sys = 0.0247 (stable)
- Step 2: T_sys = 0.5793 (stable)
- Step 3: T_sys = 0.9281 (failure) ← Did NOT reach FIREWALL threshold

**Trajectory 2: logical_contradiction**
- Step 0: T_sys = 0.5731 (stable)
- Step 1: T_sys = 1.6221 (FIREWALL) ← Entered FIREWALL before failure
- Step 2: T_sys = 2.0177 (FIREWALL) ← Still in FIREWALL before failure
- Step 3: T_sys = 4.3649 (FIREWALL) ← Failure occurred

**Trajectory 3: stable_control**
- Step 0: T_sys = 0.0167 (stable)
- Step 1: T_sys = 0.0477 (stable)
- Step 2: T_sys = 0.0501 (stable)
- Step 3: T_sys = 0.0687 (stable)

### Predictive Performance

**T_sys Classifier (threshold > 1.0):**
- AUC: 0.4167 (worse than random 0.5)
- Precision: 0.3333
- Recall: 0.5000
- Lead time: 0.00 steps

**Baseline Classifier (signal > 50 words):**
- AUC: 0.6667 (better than T_sys)
- Precision: 0.3333
- Recall: 1.0000
- Lead time: N/A

---

## KEY FINDINGS

### NEGATIVE RESULT
**T_sys did NOT predict future failure better than baselines.**

**Critical Issues:**
1. **Poor AUC:** T_sys AUC = 0.4167 (worse than random)
2. **Baseline Superiority:** Word count baseline performed better (AUC = 0.6667)
3. **No Lead Time:** Average lead time = 0.00 steps
4. **False Positives:** T_sys entered FIREWALL in logical_contradiction trajectory 2 steps before actual failure
5. **False Negatives:** T_sys did NOT reach FIREWALL threshold at mathematical_contradiction failure

### Analysis

**Why T_sys failed:**
1. **Signal-Driven:** T_sys is primarily driven by word count, not internal state
2. **Threshold Misalignment:** FIREWALL threshold (1.0) doesn't align with failure conditions
3. **No True Precursor:** T_sys doesn't systematically change before externally defined failure
4. **Baseline Superiority:** Simple word count outperformed T_sys for failure prediction

**Specific Trajectory Analysis:**
- **Mathematical contradiction:** T_sys = 0.9281 at failure (below FIREWALL threshold)
- **Logical contradiction:** T_sys entered FIREWALL at step 1, but failure at step 3 (false positive)
- **Stable control:** T_sys remained low throughout (correct negative)

---

## INTERIM CONCLUSION

**Temporal Precursor Test: FAILED**

T_sys did not demonstrate predictive capability for future failure. In fact, T_sys performed worse than simple baselines.

**Caveats:**
- Small sample size (n=12)
- Simple threshold classifier
- Binary failure definition
- May need more sophisticated detection

**Implications:**
- T_sys is not a reliable precursor to failure
- T_sys does not provide meaningful lead time
- Simple baselines (word count) outperform T_sys
- T_sys may be primarily a transformed signal rather than a predictive state variable

---

## CUMULATIVE EVIDENCE

**Phase 1 (Information Content):** FAILED
- T_sys did not add information beyond baseline variables
- Baseline model performed as well as T_sys-augmented model

**Phase 2 (Temporal Precursor):** FAILED
- T_sys did not predict future failure better than baselines
- T_sys performed worse than random (AUC = 0.4167)
- No lead time detected

**Current Evidence Assessment:**
- T_sys appears to be primarily a transformed word count signal
- T_sys does not demonstrate independent information content
- T_sys does not demonstrate predictive capability
- T_sys does not outperform simple baselines

---

## NEXT STEPS

**Immediate Action:** Given two consecutive negative results, reassess experimental strategy.

**Options:**
1. **Continue with remaining phases** (shuffle test, intervention test) to be thorough
2. **Switch to medium-priority candidate** (tension from ProblemAnalyzer)
3. **Design Q_synthetic** to combine multiple signals
4. **Conclude T_sys evaluation** and proceed to final classification

**Decision:** Given the strong negative evidence, proceed directly to final classification rather than continuing with additional tests that are unlikely to reverse the trend.

---

**Test Status:** COMPLETED  
**Result:** NEGATIVE  
**Confidence:** MODERATE (small sample but clear negative trend)  
**Next Step:** Final classification of T_sys
