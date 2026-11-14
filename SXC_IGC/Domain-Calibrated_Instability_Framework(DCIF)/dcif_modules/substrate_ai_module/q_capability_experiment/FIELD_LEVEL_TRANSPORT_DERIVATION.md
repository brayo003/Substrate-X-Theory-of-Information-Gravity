# Field-Level Transport Derivation

## Mathematical Foundation

### Telegraph Equation and Modal Transport

The physical substrate is governed by the validated telegraph equation:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S(x,t)
```

For a Fourier mode analysis, substitute the plane-wave ansatz:

```
s(x,t) ~ exp(i(k·x - ωt))
```

This yields the characteristic equation:

```
-τω² - iω = -c²τ k²
```

Solving for ω:

```
ω = [-i ± sqrt(-1 + 4c²τ²k²)] / (2τ)
```

### Modal Transport Discriminant

Define the modal discriminant:

```
D(k) = 4c²τ²|k|² - 1
```

Transport classification:
- D(k) > 0: Coherent (propagating) regime
- D(k) = 0: Critical regime  
- D(k) < 0: Overdamped (non-propagating) regime

The critical wavenumber is:

```
k_c = 1/(2cτ)
```

### Dispersion Relation

For propagating modes (D(k) > 0):

```
ω_r = sqrt(c²|k|² - 1/(4τ²))
```

Phase velocity:

```
v_phase = ω_r/|k| = sqrt(c² - 1/(4τ²|k|²))
```

## Field-Level Observables

### Spectral Representation

For a general field s(x,t), the spatial Fourier transform is:

```
ŝ(k) = ∫ s(x,t) exp(-ik·x) dx
```

The power spectrum is:

```
P(k) = |ŝ(k)|²
```

### Candidate Field-Level Observables

#### 1. Dominant-Mode Discriminant

```
D_dom = 4c²τ²|k_dominant|² - 1
```

where k_dominant is the wavenumber at maximum power:

```
k_dominant = argmax_k P(k)
```

**Properties:**
- Exact for single-mode fields
- Amplitude-independent
- Resolution-dependent
- Fails for multimode fields with coexisting regimes

#### 2. Spectral Power Fractions

```
f_prop = Σ_{D(k)>0} P(k) / Σ_k P(k)
f_over = Σ_{D(k)<0} P(k) / Σ_k P(k)
f_crit = Σ_{D(k)=0} P(k) / Σ_k P(k)
```

**Properties:**
- Handles multimode fields naturally
- Provides complete spectral information
- Amplitude-independent
- No single scalar classification

#### 3. Power-Weighted Discriminant

```
D_weighted = Σ_k P(k) D(k) / Σ_k P(k)
```

**Properties:**
- Single scalar output
- Reflects spectral mixture
- Intermediate values indicate regime coexistence
- Loses explicit regime information

#### 4. Spectral Entropy

```
H = -Σ_k p(k) log p(k)
```

where p(k) = P(k)/Σ_k P(k)

**Properties:**
- Measures spectral complexity
- Low entropy = single dominant mode
- High entropy = many modes
- Indirect transport information

## Mathematical Limitations

### Local vs Global Properties

The telegraph transport boundary is fundamentally a property of spatial frequency k, not local field values. This creates a fundamental limitation:

**A local pointwise scalar Q(x,t) cannot exactly reproduce the spectral transport boundary for general fields.**

### Multimode Fields

For fields containing multiple Fourier components, there is no unique "the transport regime" of the field as a whole. Different components may be in different regimes simultaneously.

### 2D Generalization

For 2D fields, the discriminant depends on wavevector magnitude:

```
D(k_vec) = 4c²τ²|k_vec|² - 1
```

where |k_vec| = sqrt(kx² + ky²)

The spectral analysis becomes 2D FFT.

## Key Mathematical Insight

The stress test results demonstrate that:

1. **Single-mode fields**: Dominant-mode discriminant works perfectly
2. **Multimode fields**: Dominant-mode discriminant can be misleading (e.g., 81.5% overdamped power but dominant mode indicates coherent)
3. **Power fractions**: Provide meaningful multimode information
4. **Weighted discriminant**: Can give intermediate values that don't clearly classify

Therefore, a **structured spectral observable** is mathematically required for general field-level transport classification.
