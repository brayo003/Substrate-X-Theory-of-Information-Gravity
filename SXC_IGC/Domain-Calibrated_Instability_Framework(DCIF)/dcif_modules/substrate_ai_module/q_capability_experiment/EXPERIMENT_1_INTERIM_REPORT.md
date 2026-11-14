# Q CAPABILITY EXPERIMENT - EXPERIMENT 1 INTERIM REPORT

**Experiment ID:** exp1_state_information  
**Date:** 2026-08-09  
**Status:** PARTIALLY COMPLETED  
**Model:** gemma2:2b (primary), qwen2.5-coder:1.5b (initial trials)

---

## EXPERIMENT 1 — STATE INFORMATION TEST

### Hypothesis
Q changes in ways that correspond to meaningful changes in the system's internal state that are not captured by baseline variables.

### Pre-Registered Success Criteria
- Q must show statistically significant differences between conditions that represent different internal states
- These differences must not be explained by baseline variables
- Effect size must be meaningful (Cohen's d > 0.5)

---

## RESULTS

### Data Collection
- **Total trials completed:** 4 successful trials (2 from initial run, 2 from gemma2:2b)
- **Failed trials:** 4 (Ollama timeouts)
- **Models tested:** qwen2.5-coder:1.5b (2 trials), gemma2:2b (4 trials)

### Q Computation Method
Due to TF-IDF backend issues, a simplified Q computation was used:
```
Q = 4c²τ²(1 - Jaccard_similarity) - 1
```
Where Jaccard similarity is computed from word sets.

### Results Summary

**Stable Conditions:**
- math_stable: Q = -0.14 (mean of 2 trials)
- logic_stable: Q = -0.11 (1 trial)

**Unstable Conditions:**
- math_unstable: Q = -0.10 (1 trial)

**Regime Classification:**
- All trials classified as "overdamped" (Q < 0)

### Statistical Analysis

**Insufficient sample size** for proper statistical testing. With only 4 successful trials and 1 unstable trial, we cannot:
- Compute meaningful effect sizes
- Perform statistical significance tests
- Compare to baseline variables effectively

---

## PRELIMINARY FINDINGS

### Q Behavior
1. **Narrow Range:** Q values clustered around -0.10 to -0.14
2. **No Clear Separation:** Stable and unstable conditions produced similar Q values
3. **Consistent Regime:** All trials classified as "overdamped"

### Baseline Variable Comparison
**Response Length:**
- Stable tasks: 33 words (math), 602 words (logic)
- Unstable task: 329 words (math)
- No clear pattern

**Length Ratio (response/prompt):**
- Stable tasks: 0.5 (math), 7.5 (logic)
- Unstable task: 1.74 (math)
- Variable, potentially confounded

---

## INTERPRETATION

### Current Status: INCONCLUSIVE

**Evidence Against Hypothesis:**
- Q values are very similar between stable and unstable conditions
- No clear separation in Q values
- Range is very narrow (-0.10 to -0.14)

**Limitations:**
- Insufficient sample size due to Ollama timeouts
- Simplified Q computation may not capture relevant information
- Limited variety of task conditions tested

**Confounding Factors:**
- Response length varies significantly between conditions
- Different task types (math vs logic) may have different baselines
- Small sample size makes statistical validation impossible

---

## EXPERIMENTAL ISSUES

### Technical Problems
1. **Ollama Timeouts:** High timeout rate (50% failed trials)
2. **TF-IDF Backend Issues:** Original Q computation failed with "empty vocabulary"
3. **Simplified Q Computation:** Had to fall back to Jaccard-based Q

### Methodological Issues
1. **Small Sample Size:** Insufficient for statistical analysis
2. **Task Complexity:** "Unstable" tasks may not actually produce different internal states
3. **Q Computation Validity:** Simplified Q may not capture the intended information

---

## RECOMMENDATIONS

### Immediate Actions
1. **Increase Timeout:** Use longer Ollama timeout (120+ seconds)
2. **Simplify Tasks:** Use faster, simpler tasks to reduce timeout risk
3. **Increase Sample Size:** Target at least 20 trials per condition
4. **Validate Q Computation:** Test if simplified Q captures relevant information

### Alternative Approaches
1. **Use Smaller Model:** deepseek-coder:latest (1B) may be faster
2. **Simplify Prompts:** Remove verbose instructions to speed up inference
3. **Batch Processing:** Process similar tasks together
4. **Mock Ollama:** For initial testing, use simulated responses

### Revised Experimental Design
Given the technical constraints, consider:
- **Experiment 2 (Predictive Power)** may be more feasible with simpler tasks
- **Focus on tasks with known ground truth** for outcome measurement
- **Use pre-computed responses** where possible to avoid Ollama latency

---

## DECISION ON EXPERIMENT 1

**Status:** INCONCLUSIVE - Cannot reject or accept hypothesis due to insufficient data

**Recommended Action:** 
- Continue with Experiment 2 (Predictive Power) using simplified tasks
- Address Ollama timeout issues before retrying Experiment 1
- Consider if simplified Q computation is adequate for capability testing

---

## NEXT STEPS

1. **Proceed to Experiment 2** with simplified, fast tasks
2. **Address Ollama timeout** by using smaller model or longer timeout
3. **Increase sample size** once technical issues resolved
4. **Consider alternative Q computation** if current method proves inadequate

---

**Report Status:** INTERIM  
**Confidence in Findings:** LOW (insufficient data)  
**Next Experiment:** Experiment 2 (Predictive Power)  
**Technical Issues:** Ollama timeouts, Q computation fallback needed
