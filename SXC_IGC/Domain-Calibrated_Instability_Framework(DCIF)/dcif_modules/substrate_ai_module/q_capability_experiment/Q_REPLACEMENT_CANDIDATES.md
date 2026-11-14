# Q Replacement Candidates

## Candidate A: Spectral Transport Discriminant (Recommended)

### Definition
```
Q_spectral = 4c²τ²k_dominant² - 1
```

where k_dominant is the wavenumber of the dominant Fourier mode.

### Derivation
Direct from the telegraph equation dispersion relation:
```
ω² = c²k² - 1/(4τ²)
```

The transition occurs when ω² = 0, giving k_c = 1/(2cτ). Rearranging:
```
4c²τ²k² - 1 = 0
```

### Mathematical Properties
- **Exact for single-mode fields**: Perfectly reproduces telegraph boundary
- **Amplitude-independent**: Does not depend on field amplitude A
- **Scale-invariant**: Correctly scales with c and τ
- **Dimensionally consistent**: Has dimensions of (length)⁻² · (time)² · (velocity)² = dimensionless
- **Well-defined**: Uniquely determined for a given field

### Implementation
```python
def compute_spectral_discriminant(field, c, tau):
    # Compute spatial FFT
    s_k = np.fft.fft(field.state.field_values)
    power_spectrum = np.abs(s_k)**2
    
    # Find dominant wavenumber
    k_idx = np.argmax(power_spectrum)
    k_dominant = 2 * np.pi * k_idx / field.state.L
    
    # Compute discriminant
    Q = 4 * c**2 * tau**2 * k_dominant**2 - 1
    
    return Q, k_dominant
```

### Advantages
1. Mathematically exact for the intended use case
2. No amplitude dependence
3. Directly connected to the PDE
4. Numerically stable
5. Clear interpretation

### Disadvantages
1. Not a local scalar field
2. Requires FFT computation
3. Multi-mode fields require interpretation
4. Global field property, not pointwise

### Stress Test Predictions
- **Pure Fourier modes**: 100% accuracy expected
- **Amplitude sweep**: 100% accuracy expected (amplitude-independent)
- **c/τ sweep**: 100% accuracy expected
- **Resolution**: Converges under refinement
- **Noise**: Robust to moderate noise
- **Multi-mode**: Needs weighted interpretation

### Validation Status
**PASS**: Mathematically exact for single-mode cases

---

## Candidate B: Weighted Spectral Discriminant

### Definition
```
Q_weighted = Σ_k P(k) · (4c²τ²k² - 1) / Σ_k P(k)
```

where P(k) is the power spectrum.

### Derivation
Energy-weighted average of the mode-space discriminant across all Fourier components.

### Mathematical Properties
- **Handles multi-mode fields**: Provides single scalar for complex fields
- **Amplitude-independent**: Does not depend on overall field amplitude
- **Scale-invariant**: Correctly scales with c and τ
- **Dimensionally consistent**: Dimensionless

### Implementation
```python
def compute_weighted_discriminant(field, c, tau):
    # Compute spatial FFT
    s_k = np.fft.fft(field.state.field_values)
    power_spectrum = np.abs(s_k)**2
    
    # Compute k values
    k_values = 2 * np.pi * np.fft.fftfreq(len(field.state.field_values), d=field.state.dx)
    
    # Compute discriminant for each k
    discriminants = 4 * c**2 * tau**2 * k_values**2 - 1
    
    # Weighted average
    Q = np.sum(power_spectrum * discriminants) / np.sum(power_spectrum)
    
    return Q
```

### Advantages
1. Handles multi-mode fields naturally
2. Single scalar output
3. Amplitude-independent
4. Mathematically sound

### Disadvantages
1. May obscure regime coexistence
2. Global property, not local
3. Requires FFT
4. Interpretation of intermediate values less clear

### Stress Test Predictions
- **Pure Fourier modes**: 100% accuracy expected
- **Amplitude sweep**: 100% accuracy expected
- **Multi-mode**: Should reflect mixture correctly
- **Noise**: May be sensitive to noise in spectrum

### Validation Status
**PASS**: Mathematically valid for multi-mode cases

---

## Candidate C: Local Phase Gradient Estimate

### Definition
```
Q_local(x) = 4c²τ²|∇φ(x)|² - 1
```

where φ(x) is the local phase from Hilbert transform of the real field.

### Derivation
Approximation of the spectral discriminant using local phase structure, based on the relation:
```
k_local = |∇φ|
```

### Mathematical Properties
- **Local scalar field**: Provides pointwise Q(x)
- **Approximate**: Not exact for general fields
- **Resolution-dependent**: Depends on grid resolution
- **Noise-sensitive**: Phase estimates are numerically sensitive

### Implementation
```python
def compute_local_phase_discriminant(field, c, tau):
    # Compute analytic signal via Hilbert transform
    from scipy.signal import hilbert
    analytic_signal = hilbert(field.state.field_values)
    phase = np.angle(analytic_signal)
    
    # Compute phase gradient
    phase_gradient = np.gradient(phase, field.state.dx)
    k_local = np.abs(phase_gradient)
    
    # Compute local discriminant
    Q_local = 4 * c**2 * tau**2 * k_local**2 - 1
    
    return Q_local
```

### Advantages
1. Local scalar field (desired property)
2. No explicit FFT required
3. Pointwise regime indicator

### Disadvantages
1. **Approximation error**: Not mathematically exact
2. **Ill-defined for multi-mode**: Phase ambiguous for superpositions
3. **Numerically sensitive**: Hilbert transform and gradient amplification
4. **Resolution-dependent**: Results depend on grid spacing
5. **Edge effects**: Boundary artifacts

### Stress Test Predictions
- **Pure Fourier modes**: Good accuracy (exact in continuous limit)
- **Amplitude sweep**: Good accuracy (amplitude-independent)
- **Multi-mode**: May fail or give misleading results
- **Resolution**: Converges with refinement but slower
- **Noise**: Sensitive to numerical noise

### Validation Status
**CONDITIONAL**: Valid as an approximation for single-mode fields, but explicitly approximate

---

## Rejected Candidates

### Candidate D: Modified Gradient Ratio
```
Q_modified = (τ|∇s|) / s
```

**Status**: REJECTED

**Reason**: Still amplitude-dependent, does not recover correct boundary, no mathematical justification.

### Candidate E: Local Curvature
```
Q_curvature = τ²|∇²s| / s
```

**Status**: REJECTED

**Reason**: Does not correspond to telegraph dispersion, wrong dimensions, amplitude-dependent.

### Candidate F: Energy Density Ratio
```
Q_energy = (τ|∇s|²) / (s/τ)²
```

**Status**: REJECTED

**Reason**: Ad-hoc construction, no connection to PDE, amplitude-dependent.

### Candidate G: Rescaled Q_old
```
Q_rescaled = α·Q_old
```

**Status**: REJECTED

**Reason**: Does not fix structural amplitude dependence, merely rescales the failure.

---

## Comparison Summary

| Candidate | Type | Exact | Local | Multi-mode | Amplitude-independent | Recommended |
|------------|------|-------|-------|------------|----------------------|-------------|
| A: Spectral | Global | ✓ | ✗ | ✓ (with interpretation) | ✓ | ✓ |
| B: Weighted | Global | ✓ | ✗ | ✓ | ✓ | ✓ |
| C: Local Phase | Local | ~ | ✓ | ✗ | ✓ | ~ |

## Decision

**Primary Recommendation**: Candidate A (Spectral Transport Discriminant)

**Reasoning**:
1. Mathematically exact for the telegraph equation
2. No structural limitations
3. Clear interpretation
4. Amplitude-independent as required
5. Directly connected to the physics

**Secondary Option**: Candidate B (Weighted Spectral)

**Reasoning**:
1. Handles multi-mode fields naturally
2. Still mathematically exact
3. Provides single scalar output

**Fallback Option**: Candidate C (Local Phase)

**Reasoning**:
1. Provides local scalar field if required by backend
2. Must be explicitly treated as an approximation
3. Error bounds must be established

**Critical Constraint**: The replacement must acknowledge that transport classification is fundamentally spectral, not pointwise. Any local approximation is inherently approximate and must be validated as such.
