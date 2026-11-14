# Q LEGACY Q INVENTORY

**Inventory Date:** 2026-08-09  
**Purpose:** Every legacy Q implementation and its disposition  
**Authority:** q_define.txt (theoretical Q = 4c²τ²|∇ln s|² − 1)

---

## LEGACY Q IMPLEMENTATIONS

### Legacy Implementation 1: QField (cosine-based)

**File:** substrate_ai/components/q_field.py

**Current Equation:**
```python
Q = 4c²τ²(cosine_distance)² − 1
```

**Physical Identification (from docstring):**
- s(x,t): Semantic signal vector of current reasoning state
- |∇ln s|²: Cosine distance between consecutive semantic states
- c: Configurable, default 1.0 (dimensionless)
- τ: Configurable, default 0.5 (dimensionless)

**Dependencies:**
- sentence-transformers (if available)
- sklearn TfidfVectorizer (fallback)
- ProblemAnalyzer feature vectors (fallback)

**Relation to Theoretical Q:**
- Mathematical form: IDENTICAL
- Mathematical objects: DIFFERENT
- s(x,t): Semantic embeddings vs information density field
- ∇ln(s): Cosine distance vs spatial gradient
- c, τ: Arbitrary constants vs empirically grounded parameters
- Domain: Embedding space vs physical space

**Status:** **REPLACE**

**Justification:** This is an engineered proxy that does not instantiate the theoretical mathematical objects. Should be replaced only if theoretical Q can be genuinely instantiated.

---

### Legacy Implementation 2: CLIP-based E_t

**File:** substrate_ai/check2.txt

**Current Equation:**
```python
E_t = 1 - cosine_similarity(CLIP_t, CLIP_{t-1})
```

**Physical Identification:**
- E_t: Inter-clip semantic novelty
- Domain: Video frame sequences
- Spatial domain: CLIP embedding space (512-dimensional)
- Temporal evolution: Yes (consecutive frames)

**Relation to Theoretical Q:**
- Used as inspiration for cosine-distance proxy
- Not a Q implementation itself
- Temporal signal, not spatial field

**Status:** **REMOVE**

**Justification:** This is a temporal novelty metric, not a Q implementation. Does not compute Q = 4c²τ²|∇ln s|² − 1.

---

### Legacy Implementation 3: Feature-space Q (Phase Experiments)

**File:** q_capability_experiment/code/phase2_q_calculation.py

**Current Equation:**
```python
Q = 4.0 * (c**2) * (tau**2) * squared_mag - 1.0
```

**Physical Identification:**
- s(x,t): Sum of 5 normalized text features
- Spatial domain: 5 feature dimensions
- c: 1.0 (dimensionless)
- τ: 0.5 (dimensionless)
- squared_mag: |∇ln(s)|² computed from feature gradients

**Dependencies:**
- ProblemAnalyzer feature extraction
- np.gradient for spatial derivatives

**Relation to Theoretical Q:**
- Mathematical form: IDENTICAL
- Mathematical objects: DIFFERENT
- s(x,t): Feature sum vs information density field
- Spatial coordinates: Feature names vs physical coordinates
- c, τ: Arbitrary constants vs empirically grounded parameters

**Status:** **REPLACE**

**Justification:** This is an engineered proxy using feature space instead of physical space. Should be replaced only if theoretical Q can be genuinely instantiated.

---

### Legacy Implementation 4: Semantic Q (Previous Phase 3)

**File:** q_capability_experiment/code/phase3_predictive_capability.py

**Current Equation:**
```python
Q = 4.0 * (c**2) * (tau**2) * squared_mag - 1.0
```

**Physical Identification:**
- Same as Legacy Implementation 3
- Used for temporal prediction experiments
- Not theoretically valid as established in audit

**Relation to Theoretical Q:**
- Same as Legacy Implementation 3
- Invalid for theoretical Q as established in Q_PREDICTIVE_VALIDITY_AUDIT.md

**Status:** **REMOVE**

**Justification:** This experiment was proven invalid as evidence for theoretical Q. Should not be used for theoretical Q validation.

---

## INVENTORY SUMMARY

| File | Current Equation | Role | Dependencies | Relation to Theoretical Q | Status |
|------|----------------|------|-------------|------------------------|--------|
| q_field.py | 4c²τ²(cosine_distance)² − 1 | Main Q implementation | sentence-transformers, sklearn, ProblemAnalyzer | Same form, different objects | REPLACE |
| check2.txt | E_t = 1 - cosine_similarity(CLIP_t, CLIP_{t-1}) | Temporal novelty metric | CLIP | Inspiration for proxy, not Q | REMOVE |
| phase2_q_calculation.py | 4c²τ²(feature_gradient)² − 1 | Feature-space Q | ProblemAnalyzer, np.gradient | Same form, different objects | REPLACE |
| phase3_predictive_capability.py | 4c²τ²(feature_gradient)² − 1 | Temporal prediction experiment | ProblemAnalyzer, np.gradient | Same form, different objects | REMOVE |

---

## COMMON LEGACY ISSUES

### Issue 1: Wrong Mathematical Objects

**Pattern:** All legacy implementations replace theoretical objects with proxies

**Theoretical:** s(x,t) = information density field over physical space

**Legacy:** s(x,t) = semantic embeddings, feature sums, etc.

**Impact:** Mathematical form is preserved but physical meaning is lost

### Issue 2: Wrong Spatial Domain

**Pattern:** All legacy implementations use abstract coordinate systems

**Theoretical:** Physical spatial coordinates with metric structure

**Legacy:** Feature space, embedding space, conversation domain

**Impact:** No physical spatial gradient computation

### Issue 3: Arbitrary Parameters

**Pattern:** All legacy implementations use arbitrary dimensionless constants

**Theoretical:** c (m/s) and τ (s) must be empirically grounded

**Legacy:** c = 1.0, τ = 0.5 (dimensionless)

**Impact:** No physical meaning to Q values

### Issue 4: Wrong Gradient Computation

**Pattern:** All legacy implementations use distance as gradient proxy

**Theoretical:** ∇ln(s) = spatial gradient of logarithmic information density

**Legacy:** Cosine distance, feature gradient, L2 distance

**Impact:** Gradient is not spatial gradient of information density

---

## DISPOSITION RECOMMENDATIONS

### For Theoretical Q Validation

**Recommended Action:** REMOVE all legacy implementations from theoretical Q validation

**Reasoning:**
- None instantiate the theoretical mathematical objects
- All are engineered proxies with different physical meaning
- Using them would contaminate theoretical Q validation
- Keep them only for comparison/audit purposes

### For Backend Functionality

**Recommended Action:** RETAIN q_field.py for current functionality

**Reasoning:**
- Provides useful engineered Q for semantic processing
- Current backend functionality depends on it
- Should be clearly labeled as engineered proxy, not theoretical Q
- Can coexist with theoretical Q implementation if/when available

### For Experiments

**Recommended Action:** REMOVE phase experiments from theoretical evidence

**Reasoning:**
- Phase experiments use feature-space Q (invalid for theoretical Q)
- Q_PREDICTIVE_VALIDITY_AUDIT.md established experiments as invalid
- Should not be cited as evidence for or against theoretical Q

---

## CLEANUP REQUIRED

### Documentation Updates Required

1. **q_field.py:** Add disclaimer that this is engineered proxy, not theoretical Q
2. **Experiment docs:** Add disclaimer that feature-space Q is not theoretical Q
3. **Audit docs:** Keep legacy analysis for historical context
4. **Theoretical docs:** Make clear distinction between theoretical and implemented

### Code Cleanup Required

1. **Keep:** q_field.py (with disclaimer)
2. **Archive:** Phase experiment code (with disclaimer)
3. **Document:** Legacy Q inventory (this file)
4. **Separate:** Theoretical Q implementation (if/when available)

---

## CRITICAL DISTINCTION

**THEORETICAL Q:**
- Q = 4c²τ²|∇ln s|² − 1
- s(x,t) = information density field (info/m³) over physical spacetime
- ∇ = spatial gradient in physical coordinates
- c = propagation speed (m/s), empirically grounded
- τ = damping time constant (s), empirically grounded

**LEGACY Q (all implementations):**
- Same mathematical form: Q = 4c²τ²(gradient)² − 1
- Different mathematical objects: embeddings, features, etc.
- Different domain: feature space, embedding space
- Different parameters: arbitrary constants
- **NOT THEORETICAL Q**

---

**Inventory Status:** COMPLETE  
**Legacy Implementations Found:** 4  
**Common Issues:** Wrong mathematical objects, wrong spatial domain, arbitrary parameters  
**Overall Recommendation:** REMOVE from theoretical validation, RETAIN for engineered functionality with clear disclaimers
