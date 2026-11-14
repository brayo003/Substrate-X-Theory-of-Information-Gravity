# Q Replacement Derivation

## Step 1: True Transport Condition from Telegraph Equation

### The Telegraph Equation

The physical substrate is governed by the validated telegraph equation:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S
```

Where:
- s(x,t) is the information density field
- c is the propagation speed
- τ is the relaxation time constant
- S is the source term

### Fourier Mode Analysis

For a pure Fourier mode:
```
s(x,t) ~ exp(i(k·x - ωt))
```

Substituting into the homogeneous telegraph equation (S=0):
```
τ(-ω²) + (-iω) = c²τ(-k²)
-τω² - iω = -c²τ k²
τω² + iω - c²τ k² = 0
```

This is a quadratic equation in ω:
```
ω = [-i ± sqrt((-i)² - 4τ(-c²τ k²))] / (2τ)
ω = [-i ± sqrt(-1 + 4c²τ²k²)] / (2τ)
```

### Case Analysis

**Case 1: 4c²τ²k² > 1 (Propagating regime)**
```
sqrt(-1 + 4c²τ²k²) = sqrt(4c²τ²k² - 1) = √D (real)
ω = [-i ± √D] / (2τ)
```

The real part:
```
Re(ω) = ±√D / (2τ) = ±sqrt(c²k² - 1/(4τ²))
```

This gives oscillatory (propagating) solutions with:
```
ω_r = sqrt(c²k² - 1/(4τ²))
```

**Case 2: 4c²τ²k² < 1 (Overdamped regime)**
```
sqrt(-1 + 4c²τ²k²) = i·sqrt(1 - 4c²τ²k²) = i·√D' (imaginary)
ω = [-i ± i√D'] / (2τ) = -i(1 ∓ √D') / (2τ)
```

Both solutions are purely imaginary, giving exponential decay without oscillation.

**Case 3: 4c²τ²k² = 1 (Critical regime)**
```
ω = -i / (2τ)
```

Single purely imaginary solution.

### The Exact Transport Boundary

The transition between propagating and overdamped regimes occurs when:
```
4c²τ²k² = 1
```

Defining the critical wavenumber:
```
k_c = 1/(2cτ)
```

### The Exact Mode-Space Discriminant

Define the mode-space transport discriminant:
```
D_k = 4c²τ²|k|² - 1
```

Transport classification:
- D_k > 0: Propagating (coherent) regime
- D_k = 0: Critical regime  
- D_k < 0: Overdamped regime

### Dispersion Relation

For propagating modes (D_k > 0):
```
ω_r² = c²|k|² - 1/(4τ²)
```

Phase velocity:
```
v_phase = ω_r/|k| = sqrt(c² - 1/(4τ²|k|²))
```

### Key Mathematical Insight

The telegraph transport regime is fundamentally a property of:
- **Spatial frequency k** (spectral property)
- **Physical parameters c and τ**

It is NOT a property of:
- Local field amplitude A
- Local field value s(x,t)
- Local gradient magnitude

This is because the dispersion relation involves k², not local field quantities.

## Step 2: Why Q_old Fails

### The Falsified Formula

```
Q_old = 4c²τ²|∇ln(s)|² - 1
```

### For Finite-Amplitude Sinusoidal Field

Consider:
```
s(x) = s0 + A cos(kx)
```

The gradient:
```
∇s = -Ak sin(kx)
∇ln(s) = ∇s/s = -Ak sin(kx) / [s0 + A cos(kx)]
```

The magnitude:
```
|∇ln(s)|² = A²k² sin²(kx) / [s0 + A cos(kx)]²
```

### The Structural Problem

1. **Amplitude dependence**: Q_old depends on A, but telegraph transport does not
2. **Non-uniform spatial dependence**: Q_old varies with position, but transport is a global property of the mode
3. **Boundary dependence**: Q_old depends on the ratio A/s0, not on k alone

### Maximum Possible Q_old

The maximum of |∇ln(s)| occurs where the denominator is minimized:
```
min[s0 + A cos(kx)] = s0 - A
max|∇ln(s)| = Ak/(s0 - A)
```

Thus:
```
max(Q_old) = 4c²τ²(Ak/(s0 - A))² - 1
```

For Q_old to be positive (predict coherent regime):
```
4c²τ²(Ak/(s0 - A))² > 1
k > (s0 - A)/(2cτA)
```

This boundary depends on A, contradicting the amplitude-independent telegraph boundary k_c = 1/(2cτ).

### Empirical Failure

The amplitude sweep experiment demonstrated:
- Telegraph transport: amplitude-independent ✓
- Q_old classification: amplitude-dependent ✗
- Agreement: 0/42 (0%)

This is a mathematical structural failure, not a numerical artifact.

## Step 3: What the Replacement Must Represent

### Analytical Requirements

The replacement quantity must:

1. **Reproduce the exact telegraph transport boundary**: k_c = 1/(2cτ)
2. **Be amplitude-independent** where the telegraph equation is amplitude-independent
3. **Scale correctly** under field transformations
4. **Be mathematically consistent** with the dispersion relation
5. **Be computable** from the field without a priori spectral decomposition

### Fundamental Constraint

The telegraph transport boundary is fundamentally spectral (depends on k). A local pointwise scalar cannot exactly reproduce a spectral boundary unless:

1. The field is a pure single mode
2. The local quantity estimates k from local field structure
3. Approximations are accepted with clear error bounds

## Step 4: Local Candidate Analysis

### Candidate 1: Local Wavenumber Estimate

For a field s(x), define the local wavenumber as:
```
k_local = |∇φ| / φ_mag
```

where φ is a local phase estimate.

**Problems:**
- Requires phase extraction (Hilbert transform for real fields)
- Phase is ill-defined for multi-mode superposition
- Numerically sensitive to noise
- Resolution-dependent

### Candidate 2: Local Spectral Estimation

Compute local Fourier transform with a window:
```
k_local(x) = argmax_k |FT[s](x, k)|
```

**Problems:**
- Window size parameter dependence
- Computational cost
- Not truly local
- Resolution-dependent

### Candidate 3: Local Dispersion Discriminant

Construct a local quantity from the PDE itself:
```
D_local = 4c²τ²|∇s|²/s² - 1
```

**Problems:**
- This is essentially Q_old
- Still amplitude-dependent
- Fails the same mathematical tests

### Candidate 4: Dimensionless Gradient Ratio

```
D_ratio = (τ|∇s|) / s
```

**Problems:**
- Still amplitude-dependent
- Does not have the correct units
- Does not recover the k_c boundary

## Step 5: Mathematical Conclusion

### The Fundamental Issue

The telegraph equation's transport classification is inherently spectral. The discriminant:
```
D_k = 4c²τ²k² - 1
```

requires knowledge of the spatial frequency k.

For a general field s(x,t) that may contain multiple Fourier components, there is no unique "the transport regime" of the field as a whole. Different components may be in different regimes.

### Local Scalar Impossibility

A local pointwise scalar Q(x,t) cannot simultaneously:
1. Reproduce the exact spectral boundary k_c = 1/(2cτ)
2. Be amplitude-independent
3. Be well-defined for multi-mode fields
4. Be computationally stable

This is a mathematical impossibility, not a numerical limitation.

## Step 6: The Correct Approach

### Spectral Observable

The mathematically correct observable is the **spectral discriminant**:
```
D_k = 4c²τ²k² - 1
```

computed from the spatial Fourier transform of the field.

### Practical Implementation

For each field configuration:
1. Compute spatial Fourier transform: Ŝ(k) = FT[s(x)]
2. Compute power spectrum: P(k) = |Ŝ(k)|²
3. Identify dominant wavenumbers: k_dominant = argmax_k P(k)
4. Compute discriminant: D_k = 4c²τ²k_dominant² - 1
5. Classify transport based on sign of D_k

### For Multi-Mode Fields

For fields with multiple significant modes, report:
- The set of dominant wavenumbers
- Their respective discriminants
- Fraction of field energy in each regime

## Step 7: Proposed Replacement

### Candidate A: Spectral Transport Discriminant

**Definition:**
```
Q_spectral = 4c²τ²k_dominant² - 1
```

**Derivation:** Direct from telegraph dispersion relation

**Properties:**
- Exact for single-mode fields
- Amplitude-independent
- Mathematically consistent with PDE
- Requires spectral analysis

**Limitations:**
- Not local
- Requires FFT
- Multi-mode interpretation needed

### Candidate B: Weighted Spectral Discriminant

**Definition:**
```
Q_weighted = Σ_k P(k) · (4c²τ²k² - 1) / Σ_k P(k)
```

**Derivation:** Energy-weighted average of mode-space discriminants

**Properties:**
- Handles multi-mode fields
- Amplitude-independent
- Single scalar output

**Limitations:**
- Still requires spectral analysis
- May obscure regime coexistence

### Candidate C: Local Phase Gradient Estimate

**Definition:**
```
Q_local(x) = 4c²τ²|∇φ(x)|² - 1
```

where φ(x) is the local phase from Hilbert transform

**Derivation:** Approximation of spectral discriminant via local structure

**Properties:**
- Local scalar field
- Approximates spectral behavior

**Limitations:**
- Approximation error
- Numerically sensitive
- Ill-defined for multi-mode fields

## Conclusion

The mathematical analysis demonstrates that:

1. **The telegraph transport boundary is fundamentally spectral** (depends on k)
2. **Q_old fails structurally** due to amplitude dependence
3. **No exact local scalar exists** that reproduces the spectral boundary
4. **The correct observable is spectral**, not pointwise

The scientifically valid replacement is a **spectral transport discriminant**, not a local scalar field. Any local approximation must explicitly acknowledge its approximate nature and error bounds.
