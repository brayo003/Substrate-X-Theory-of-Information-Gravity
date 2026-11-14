# Field-Level Transport Backend Integration Specification

## Overview

This document specifies the exact backend integration requirements for the validated structured spectral transport observable, following the scientific decision that a single scalar Q is mathematically insufficient for general field-level transport classification.

## Validated Observable Specification

### Mathematical Definition

The validated transport observable is a structured spectral representation:

```python
spectral_transport_observable = {
    # Dominant mode information
    'dominant_k': float,           # Dominant wavenumber magnitude (rad/m)
    'dominant_D': float,           # Dominant discriminant D = 4c²τ²k² - 1
    'dominant_regime': str,        # 'coherent' | 'overdamped' | 'critical'
    
    # Spectral power distribution
    'propagating_power_fraction': float,  # Fraction of energy in propagating modes
    'overdamped_power_fraction': float,   # Fraction of energy in overdamped modes
    'critical_power_fraction': float,    # Fraction of energy at critical boundary
    
    # Aggregate metrics
    'weighted_D': float,           # Power-weighted discriminant
    'spectral_entropy': float,      # Spectral entropy H = -Σ p(k) log p(k)
    
    # Metadata
    'c_nominal': float,            # Propagation speed parameter
    'tau_nominal': float,          # Relaxation time parameter
    'k_critical': float,           # Critical wavenumber k_c = 1/(2cτ)
    'analysis_timestamp': float,    # Time of analysis
}
```

### Units and Dimensions

- k: rad/m (inverse length)
- D: dimensionless
- Power fractions: dimensionless (0 to 1)
- Entropy: dimensionless (nats)
- c: m/s (velocity)
- τ: s (time)

### Frequency Requirements

- **Single-mode fields**: Update every telegraph time step
- **Multimode fields**: Update every N steps (N configurable, suggested N=10-100)
- **Backend coupling**: Update at agent decision frequency (suggested 1-10 Hz)

## Backend Consumer Mapping

### Current Q_old Consumers

Based on the existing codebase, Q_old is consumed by:

1. **Physical field domain** (`physical_field_models.py`)
   - Stores Q as field attribute
   - Used for field state classification

2. **Substrate AI module** (`substrate_ai_module.py`)
   - Uses Q for entity-field coupling decisions
   - May use Q for threshold-based behavior

3. **Entity coupling logic** (domain coupling)
   - Potentially uses Q to determine interaction strength
   - May use Q for regime-dependent parameters

### Required Consumer Updates

#### 1. Physical Field Domain

**Current interface:**
```python
field.q = 4c²τ²|∇ln(s)|² - 1  # Local scalar field
```

**Required interface:**
```python
field.spectral_transport = {
    'dominant_k': k_dominant,
    'dominant_D': D_dominant,
    'propagating_power_fraction': f_prop,
    'overdamped_power_fraction': f_over,
    'weighted_D': D_weighted,
    'spectral_entropy': H,
}
```

**Implementation requirements:**
- Add FFT computation to field state update
- Cache spectral analysis results
- Provide backward compatibility method for old Q interface
- Update frequency: spectral analysis is expensive, cache between updates

#### 2. Substrate AI Module

**Current interface:**
```python
if field.q > 0:
    # Coherent regime behavior
else:
    # Overdamped regime behavior
```

**Required interface:**
```python
# Single-mode case (low entropy)
if field.spectral_transport['spectral_entropy'] < threshold:
    q_scalar = field.spectral_transport['dominant_D']
    if q_scalar > 0:
        # Coherent regime behavior
    else:
        # Overdamped regime behavior

# Multimode case (high entropy)
else:
    f_prop = field.spectral_transport['propagating_power_fraction']
    f_over = field.spectral_transport['overdamped_power_fraction']
    
    if f_prop > 0.7:
        # Primarily propagating
    elif f_over > 0.7:
        # Primarily overdamped
    else:
        # Mixed regime - use both behaviors weighted
```

**Implementation requirements:**
- Add spectral entropy threshold parameter
- Implement regime-coexistence logic
- Weight behavior by power fractions when appropriate

#### 3. Entity Coupling Logic

**Current interface:**
```python
coupling_strength = function_of(Q)
```

**Required interface:**
```python
# Option 1: Use dominant mode
coupling_strength = function_of(field.spectral_transport['dominant_D'])

# Option 2: Use weighted behavior
D_weighted = field.spectral_transport['weighted_D']
coupling_strength = function_of(D_weighted)

# Option 3: Use power fractions
f_prop = field.spectral_transport['propagating_power_fraction']
coupling_strength = f_prop * strong_coupling + (1-f_prop) * weak_coupling
```

**Implementation requirements:**
- Choose coupling strategy based on physical requirements
- Document which strategy is used
- Test that coupling responds to actual spectral changes

## Data Structure Changes

### Field State Update

**Add to FieldState:**
```python
@dataclass
class FieldState:
    # Existing fields...
    
    # New spectral transport data
    spectral_transport: Dict[str, Any] = None
    spectral_transport_cache_timestamp: float = 0.0
    spectral_transport_update_interval: float = 1.0  # seconds
```

### Field Update Frequency

**Spectral analysis computational cost:**
- 1D FFT: O(N log N) per analysis
- 2D FFT: O(N² log N) per analysis
- For 100×100 grid: ~10⁴ operations per analysis

**Recommended update strategy:**
```python
if physical_time - spectral_transport_cache_timestamp > update_interval:
    compute_spectral_transport()
    spectral_transport_cache_timestamp = physical_time
```

**Suggested intervals:**
- 1D fields: every 10 time steps
- 2D fields: every 50 time steps
- Backend coupling: every 1-10 seconds (real time)

## Backward Compatibility

### Transition Strategy

**Phase 1: Add spectral transport alongside Q_old**
- Keep Q_old computation unchanged
- Add spectral_transport as new field attribute
- Both observables available during transition

**Phase 2: Update consumers to use spectral_transport**
- Add new code paths using spectral data
- Keep old Q_old paths as fallback
- Add configuration flag to switch between observables

**Phase 3: Deprecate Q_old**
- Mark Q_old as deprecated
- Add warnings when used
- Remove from new features
- Keep for backward compatibility only

**Phase 4: Remove Q_old**
- Remove Q_old computation
- Remove from codebase
- Use spectral_transport exclusively

### Compatibility Requirements

- Old field configurations must continue to work
- Existing entity behaviors should not break abruptly
- Performance impact must be acceptable
- Memory footprint must be manageable

## Failure Behavior

### Spectral Analysis Failures

**FFT failures:**
- Fall back to local gradient estimate if FFT fails
- Log failure and alert user
- Use last valid spectral data

**Memory failures:**
- Reduce FFT resolution
- Fall back to lower-dimensional analysis
- Alert user of degraded performance

**Numerical failures:**
- Use conservative regime classification
- Fall back to overdamped regime (safe default)
- Log numerical issues

## Validation Requirements

### Unit Tests Required

1. **Spectral analysis correctness**
   - Verify dominant mode detection for known inputs
   - Verify power fraction calculations
   - Verify weighted discriminant accuracy

2. **Single-mode equivalence**
   - Verify spectral_transport reduces to single-mode case
   - Verify D_dominant equals modal discriminant for pure modes

3. **Multimode correctness**
   - Verify power fractions sum to 1.0
   - Verify weighted discriminant reflects mixture
   - Verify entropy calculations

4. **Backend integration**
   - Verify entity coupling responds to spectral changes
   - Verify regime coexistence is handled correctly
   - Verify performance within acceptable bounds

### Regression Tests

1. **Prevent Q_old reintroduction**
   - Fail if Q_old code path is accidentally used
   - Verify spectral_transport is always computed

2. **Ensure spectral analysis frequency**
   - Verify FFT is not called every time step (performance)
   - Verify cache invalidation works correctly

3. **Validate regime coexistence**
   - Test with mixed-propagating/overdamped fields
   - Verify backend handles both regimes simultaneously

## Performance Budget

### Computational Cost Estimates

**For 100×100 2D field:**
- FFT: ~10⁴ operations
- Memory: ~16 KB for complex FFT array
- Time: ~1-10 ms per analysis

**Recommended allocation:**
- Spectral analysis: < 5% of total computation time
- Memory overhead: < 10 MB
- Update frequency: 0.1-1 Hz (real time equivalent)

## Configuration Parameters

### New Parameters to Add

```python
# Spectral analysis configuration
spectral_config = {
    'update_interval': 1.0,              # seconds between analyses
    'fft_resolution': 'auto',            # 'low' | 'medium' | 'high' | 'auto'
    'entropy_threshold': 0.5,           # below this = single-mode
    'power_fraction_threshold': 0.3,    # below this = negligible regime
    'fallback_to_local': False,        # if True, use local estimate on FFT failure
}
```

### Backend Coupling Configuration

```python
# Coupling strategy configuration
coupling_config = {
    'strategy': 'dominant',              # 'dominant' | 'weighted' | 'power_fraction'
    'mixed_regime_behavior': 'weighted',  # 'dominant' | 'weighted' | 'separate'
    'thresholds': {
        'propagating_threshold': 0.7,
        'overdamped_threshold': 0.7,
    }
}
```

## Integration Timeline

### Immediate (Current Session)

1. ✅ Mathematical derivation complete
2. ✅ Stress testing complete
3. ✅ Scientific decision made
4. ⏳ Backend specification (this document)
5. ⏳ Backend integration design

### Short-term (Next Session)

1. Implement spectral analysis in physical field module
2. Add spectral_transport to FieldState
3. Add unit tests for spectral analysis
4. Update one consumer as proof-of-concept

### Medium-term (Following Sessions)

1. Update all consumers to use spectral_transport
2. Add backward compatibility layer
3. Implement configuration system
4. Performance optimization and caching

### Long-term (Future Sessions)

1. Deprecate and remove Q_old
2. Full integration testing
3. Performance benchmarking
4. Documentation updates

## Summary

The backend must be updated to consume a **structured spectral transport observable** instead of a single scalar Q. This is a mathematical requirement, not an architectural preference. The integration must:

1. Accept structured spectral data (not just a scalar)
2. Handle regime coexistence in multimode fields
3. Provide backward compatibility during transition
4. Manage computational cost through caching
5. Validate that backend behavior responds to actual spectral transport changes

The system is **NOT** ready for artificial-life coupling until this spectral observable integration is complete and validated.
