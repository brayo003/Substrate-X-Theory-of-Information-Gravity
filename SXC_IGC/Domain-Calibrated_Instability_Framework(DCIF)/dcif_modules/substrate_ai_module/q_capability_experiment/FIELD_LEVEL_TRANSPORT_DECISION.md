# Field-Level Transport Decision

## Executive Summary

**FINAL DECISION: CASE_B - STRUCTURED SPECTRAL OBSERVABLE REQUIRED**

The comprehensive stress testing has determined that while the modal telegraph discriminant is mathematically exact, no single scalar field-level Q can faithfully represent transport classification for general multimode fields. A structured spectral observable is required.

## Experimental Results Summary

### Phase 1: Modal Baseline
- All 7 modal wavenumbers correctly classified
- Critical wavenumber k_c = 0.5000 rad/m verified
- Modal discriminant D(k) = 4c²τ²k² - 1 validated

### Phase 2: Amplitude Invariance
- **PASSED**: Amplitude independence verified
- Spectral discriminant correctly invariant under field amplitude changes
- 42 amplitude tests all consistent

### Phase 3: Two-Mode Mixtures
- **PASSED**: Dominant mode correctly tracks highest-amplitude component
- A1=0.80,A2=0.20: k_dom=0.2467 (overdamped dominant) ✓
- A1=0.20,A2=0.80: k_dom=0.7401 (coherent dominant) ✓
- Power fractions correctly show regime mixture

### Phase 4: Multimode Spectra
- **CRITICAL FINDING**: Dominant mode alone is insufficient
- 5-mode mixture: 81.5% overdamped power, 18.5% propagating power
- Dominant k: 0.9901 (coherent) → D_dominant = 2.92 (positive)
- Weighted D: -0.3246 (negative) → correctly reflects overdamped dominance
- **Single scalar Q fails for multimode fields**

### Phase 5: 2D Generalization
- **PASSED**: 2D wavevector measurement works
- True |k|: 0.3000, Measured |k|: 0.3089 (3% error)
- 2D spectral analysis generalizes correctly

### Phase 6: Noise Robustness
- **PASSED**: Excellent noise robustness
- SNR 40dB → 5dB: k_dominant stable at 0.7491
- Spectral analysis naturally averages noise

### Phase 7: Resolution Convergence
- **PASSED**: Excellent convergence
- k_dominant std: 0.000600 (0.08% relative error)
- Resolution-independent results

### Phase 8: Parameter Sweep
- **PASSED**: Correct boundary tracking across parameter space
- All 9 (c,τ) combinations: k_dominant correctly tracks k_test
- k_c changes correctly identified and followed

## Decision Criteria

All 7 criteria passed:
- amplitude_independence: True ✓
- two_mode_stability: True ✓
- multimode_meaningful: True ✓
- 2d_validity: True ✓
- noise_robustness: True ✓
- resolution_convergence: True ✓
- parameter_validity: True ✓

## Scientific Analysis

### Why Single Scalar Fails

**Multimode Problem**: For fields containing both propagating and overdamped modes, a single scalar cannot represent the coexistence of regimes. The multimode test demonstrated:
- 81.5% of field energy in overdamped regime
- 18.5% of field energy in propagating regime
- Dominant mode indicates coherent (misleading)
- Field is primarily overdamped (correct)

**Power-weighted discriminant**: D_weighted = -0.3246 correctly reflects overdamped dominance, but intermediate values lose explicit regime information.

### Why Structured Spectral Observable Succeeds

The spectral representation provides:
1. **Complete information**: All modes and their transport classifications
2. **Aggregation capability**: Power fractions quantify regime coexistence
3. **Flexibility**: Can be reduced to single-mode case when appropriate
4. **Mathematical exactness**: Direct connection to modal discriminant

## Validated Structured Spectral Observable

### Primary Observables

```python
spectral_transport = {
    'dominant_k': k_dominant,
    'dominant_D': 4c²τ²k_dominant² - 1,
    'propagating_power_fraction': f_prop,
    'overdamped_power_fraction': f_over,
    'critical_power_fraction': f_crit,
    'spectral_entropy': H,
}
```

### Classification Rules

**Single-mode fields** (spectral_entropy < threshold):
- Use dominant_D as single scalar Q
- Equivalent to modal discriminant

**Multimode fields** (spectral_entropy ≥ threshold):
- Use power fractions for regime classification
- Report coexistence when both f_prop and f_over are significant
- Use weighted_D as aggregate indicator

### Mathematical Specification

**Dominant mode:**
```
k_dominant = argmax_k |ŝ(k)|²
D_dominant = 4c²τ²k_dominant² - 1
```

**Power fractions:**
```
f_prop = Σ_{D(k)>0} |ŝ(k)|² / Σ_k |ŝ(k)|²
f_over = Σ_{D(k)<0} |ŝ(k)|² / Σ_k |ŝ(k)|²
```

**Weighted discriminant:**
```
D_weighted = Σ_k |ŝ(k)|² D(k) / Σ_k |ŝ(k)|²
```

**Spectral entropy:**
```
H = -Σ_k p(k) log p(k)
p(k) = |ŝ(k)|² / Σ_k |ŝ(k)|²
```

## Final Scientific Conclusion

### Answer to the Required Question

**"Given the validated telegraph-equation substrate, what is the mathematically and empirically defensible representation of transport regime for an evolving physical field, and is that representation suitable for downstream backend coupling?"**

**Answer:** The mathematically and empirically defensible representation is a **structured spectral observable** containing dominant mode information, power fractions, and spectral entropy. This representation is suitable for backend coupling if the backend can consume structured data rather than requiring a single local scalar.

### Backend Suitability

**Conditionally suitable** - The structured spectral observable is scientifically valid, but backend integration requires:
1. Updating backend data structures to accept spectral observables
2. Modifying agent/environment coupling to use spectral information
3. Ensuring downstream logic can handle regime coexistence
4. Budgeting for FFT computational cost

If the backend architecture strictly requires a single local scalar, this creates an architectural constraint that cannot be satisfied by mathematically correct transport classification.

## Next Steps

### Immediate Actions Required

1. **DO NOT** integrate a single scalar Q into the backend
2. **DO** design backend data structures for spectral observables
3. **DO** update field-entity coupling to use spectral information
4. **DO** test backend with multimode fields
5. **DO** verify artificial-life behavior responds to spectral regime changes

### Prohibited Actions

1. **DO NOT** force a single scalar approximation
2. **DO NOT** modify the telegraph solver
3. **DO NOT** revive Q_old
4. **DO NOT** claim the system is ready for artificial-life coupling
5. **DO NOT** proceed to 50k-tick experiment until spectral observable integration is complete

## Critical Constraint

The scientific gate has determined that **transport classification is fundamentally spectral**. Any attempt to force this into a single local scalar is inherently approximate and must be explicitly treated as such. The validated solution acknowledges this constraint and provides the mathematically correct structured representation.
