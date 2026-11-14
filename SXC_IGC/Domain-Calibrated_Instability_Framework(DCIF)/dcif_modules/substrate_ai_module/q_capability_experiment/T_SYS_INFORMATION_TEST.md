# T_sys INFORMATION CONTENT TEST RESULTS

**Test Date:** 2026-08-09  
**Phase:** Phase 1 - Information Content Test  
**Model:** qwen2.5-coder:1.5b  
**Status:** COMPLETED

---

## OBJECTIVE

Determine whether T_sys contains information that is not trivially recoverable from instantaneous input features.

---

## METHOD

### Controlled Input Families

Created 3 families with matched lexical features but different internal trajectories:

**Family 1: stable_vs_contradictory**
- Stable reasoning: "A implies B. A is true. Is B true?" (expected stable)
- Contradictory reasoning: "A implies B. B implies not A. A is true. Is A true?" (expected unstable)

**Family 2: stable_vs_verbose**
- Stable concise: "2 + 2 = ?" (expected stable, low signal)
- Stable verbose: Long prompt asking for detailed explanation (expected stable, high signal)

**Family 3: unstable_vs_concise**
- Unstable contradictory: "A implies B. B implies not A. A is true. Is A true?" (expected unstable, medium signal)
- Unstable concise: "A=1, B=0, A→B, B→¬A. A?" (expected unstable, low signal)

### Predictive Models

**Model A (baseline):**
- Features: response_length, response_word_count, length_ratio, signal
- Target: internal trajectory (stable=0, unstable=1)

**Model B (baseline + T_sys):**
- Features: same as Model A + T_sys
- Target: internal trajectory (stable=0, unstable=1)

### Evaluation
- 3-fold cross-validation
- Accuracy metric
- Paired t-test for significance

---

## RESULTS

### Data Collection
- **Total trials:** 11 (1 timeout, 10 successful)
- **Families tested:** 3
- **Trials per family:** 3-4

### T_sys Results by Family

**Family 1: stable_vs_contradictory**
- Stable reasoning: T_sys = 0.50-1.10 (stable expected)
- Contradictory reasoning: T_sys = 2.30 (unstable expected)
- **Observation:** T_sys discriminates stable vs contradictory

**Family 2: stable_vs_verbose**
- Stable concise: T_sys = 0.0043 (low signal)
- Stable verbose: T_sys = 0.77-1.81 (high signal)
- **Observation:** T_sys tracks signal (word count)

**Family 3: unstable_vs_concise**
- Unstable contradictory: T_sys = 2.12-2.13 (medium signal)
- Unstable concise: T_sys = 1.66-1.68 (low signal)
- **Observation:** T_sys tracks signal (word count)

### Predictive Model Comparison

**Model A (baseline only):**
- Accuracy: 0.8889 (8/9 correct)

**Model B (baseline + T_sys):**
- Accuracy: 0.8889 (8/9 correct)

**Improvement:** 0.0000

**Statistical Test:**
- Paired t-test: t=nan, p=nan (insufficient data for statistical test)

---

## KEY FINDINGS

### NEGATIVE RESULT
**T_sys did NOT add information beyond baseline variables in this test.**

The baseline model (response length, word count, length ratio, signal) achieved the same accuracy as the model with T_sys added.

### Analysis

**Why T_sys didn't add information:**
1. **Signal Dominance:** T_sys is primarily driven by the excitation signal (word count)
2. **Small Sample Size:** Only 11 trials, insufficient for detecting subtle effects
3. **Task Simplicity:** Binary classification (stable/unstable) may be too coarse
4. **Baseline Performance:** Baseline already performed well (0.8889 accuracy)

**T_sys Behavior Observed:**
- T_sys clearly responds to signal (word count)
- T_sys shows some discrimination between stable/unstable
- But discrimination is captured by baseline variables

---

## INTERIM CONCLUSION

**Information Content Test: FAILED**

T_sys did not demonstrate independent information content beyond instantaneous baseline variables in this controlled test.

**Caveats:**
- Small sample size (n=11)
- Simple binary classification task
- Baseline already performed well
- May need more sophisticated test

**Implications:**
- T_sys may be primarily a transformed signal rather than an independent state variable
- Current evidence suggests T_sys tracks word count rather than true internal state
- More sophisticated testing needed to draw definitive conclusions

---

## NEXT STEPS

**Immediate Action:** Proceed to Phase 2 (Temporal Precursor Test) to determine if T_sys has predictive value despite this negative result.

**Reconsideration:** If Phase 2 also fails, reassess whether T_sys is the right candidate or if testing methodology needs revision.

---

**Test Status:** COMPLETED  
**Result:** NEGATIVE  
**Confidence:** LOW (small sample size)  
**Next Phase:** Phase 2 - Temporal Precursor Test
