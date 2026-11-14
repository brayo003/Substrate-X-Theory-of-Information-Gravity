# Mathematical Audit of Physical Field Implementation

**Audit Date:** 2026-08-09  
**Purpose:** Reconstruct the exact mathematical implementation and determine why validation experiments failed  
**Scope:** Continuous PDE, discretization, stability, propagation conditions, and parameter relationships

---

## 1. CONTINUOUS EQUATIONS INTENDED

### 1.1 Intended Telegraph Equation

**Target equation (as documented):**
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S(x,t)
```

**Where:**
- s(x,t): Information density field (scalar)
- τ: Relaxation time constant (seconds)
- c: Propagation speed (m/s)
- ∇²: Laplacian operator (1/m²)
- S(x,t): Source term

**Mathematical classification:** Second-order hyperbolic PDE (telegraph equation)

**Physical interpretation:** Damped wave equation exhibiting both wave propagation and exponential relaxation

---

## 2. ACTUAL IMPLEMENTED EQUATIONS

### 2.1 Simplified Validation Script Implementation

**File:** `run_physical_transport_validation.py`, lines 99-120

**Actual discrete update equation:**
```python
# Line 106-110: Laplacian computation
laplacian[1:-1, :, 0] = (s[2:, :, 0] - 2*s[1:-1, :, 0] + s[:-2, :, 0]) / (dx**2)
laplacian[:, 1:-1, 0] = (s[:, 2:, :, 0] - 2*s[:, 1:-1, 0] + s[:, :-2, 0]) / (dy**2)

# Line 116-118: Field update
damping = -0.1  # ARBITRARY CONSTANT
field['field_values'] = field['field_values'] + dt * (c_nominal**2) * laplacian.ravel() / tau_nominal
field['field_values'] = field['field_values'] * (1.0 + damping * dt / tau_nominal)
```

**Mathematical reconstruction:**
```
s(t+Δt) = s(t) + Δt * (c²/τ) * ∇²s(t) * (1 + damping * Δt/τ)
```

**Critical finding:** This is NOT the telegraph equation. This is a first-order diffusion equation with multiplicative damping.

**Classification:** First-order parabolic PDE (diffusion equation) with artificial damping

### 2.2 Official Physical Field Implementation

**File:** `sim_world/domains/physical_field/physical_field_dynamics.py`, lines 128-138

**Actual discrete update equation:**
```python
# Line 134: Acceleration
acceleration = (c**2) * laplacian - v / tau + source / tau

# Line 135: Velocity update
v_new = v + dt * acceleration

# Line 138: Field update
s_new = s + dt * v_new
```

**Mathematical reconstruction:**
```
∂v/∂t = c² ∇²s - v/τ + S/τ
∂s/∂t = v
```

**Substituting v = ∂s/∂t:**
```
∂²s/∂t² = c² ∇²s - (1/τ) ∂s/∂t + S/τ
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S
```

**Critical finding:** This IS the correct telegraph equation (second-order hyperbolic PDE).

**Classification:** Second-order hyperbolic PDE (telegraph equation) ✓

---

## 3. IMPLEMENTATION COMPARISON

### 3.1 Validation Script vs Official Implementation

| Aspect | Validation Script | Official Implementation |
|--------|-------------------|------------------------|
| **Equation type** | First-order diffusion | Second-order telegraph |
| **Wave propagation** | ❌ Impossible | ✅ Possible |
| **Damping mechanism** | Multiplicative factor | First-order derivative term |
| **Damping constant** | `damping = -0.1` (arbitrary) | `1/τ` (physical) |
| **Time integration** | Explicit Euler | Semi-implicit Euler |
| **Velocity field** | ❌ Not tracked | ✅ Tracked separately |
| **Boundary conditions** | Implicit (clamping) | Implicit (clamping) |

### 3.2 Critical Implementation Error

**The validation script used the WRONG equation.**

The simplified script implemented:
```
∂s/∂t = (c²/τ) ∇²s * (1 - 0.1Δt/τ)
```

But should have implemented:
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
```

**Consequence:** The validation script physically cannot exhibit wave propagation because it implemented a diffusion equation, not a wave equation.

---

## 4. CONTINUOUS TELEGRAPH EQUATION ANALYSIS

### 4.1 Canonical Telegraph Equation

**Continuous form:**
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
```

**Seeking plane-wave solutions:** s(x,t) = A exp(i(kx - ωt))

**Substituting into PDE:**
```
τ (-ω²) + (-iω) = c²τ (-k²)
-τω² - iω = -c²τk²
τω² + iω = c²τk²
```

### 4.2 Dispersion Relation

**Real and imaginary parts:**
```
τω² = c²τk²  →  ω² = c²k²  →  ω = ±ck
ω = 0
```

**Combined solution:**
```
ω = ±√(c²k² - (1/2τ)²) + i/(2τ)
```

**Propagation condition:** c²k² > (1/2τ)²

**Critical wavenumber:** k_c = 1/(2cτ)

**Critical wavelength:** λ_c = 4πcτ

### 4.3 Regime Classification

**Coherent regime (propagating waves):**
```
c²k² > (1/2τ)²  →  k > 1/(2cτ)  →  λ < 4πcτ
Q > 0
```

**Critical regime:**
```
c²k² = (1/2τ)²  →  k = 1/(2cτ)  →  λ = 4πcτ
Q = 0
```

**Overdamped regime (diffusive behavior):**
```
c²k² < (1/2τ)²  →  k < 1/(2cτ)  →  λ > 4πcτ
Q < 0
```

### 4.4 Theoretical Q Derivation

**From Q = 4c²τ²|∇ln s|² - 1:**

For plane waves: s = A exp(i(kx - ωt))
```
∇s = ik s
∇ln s = ik
|∇ln s|² = k²
Q = 4c²τ²k² - 1
```

**Critical condition (Q = 0):**
```
4c²τ²k² - 1 = 0  →  k² = 1/(4c²τ²)  →  k = 1/(2cτ)
```

**Matches dispersion relation critical wavenumber** ✓

---

## 5. DISCRETE IMPLEMENTATION ANALYSIS

### 5.1 Official Implementation Discretization

**Semi-implicit Euler scheme:**
```
v_new = v + Δt * (c² ∇²s - v/τ)
s_new = s + Δt * v_new
```

**Substituting:**
```
s_new = s + Δt * (v + Δt * (c² ∇²s - v/τ))
s_new = s + Δt * v + Δt² * (c² ∇²s - v/τ)
```

**Taylor expansion analysis:**
```
s(t+Δt) = s(t) + Δt * ∂s/∂t + Δt²/2 * ∂²s/∂t² + O(Δt³)
```

**Implementation accuracy:** O(Δt²) in space, O(Δt) in time

### 5.2 Stability Analysis

**CFL condition for wave equation:**
```
c * Δt / Δx < 1
```

**Validation script parameters:**
```
c = 1.0 m/s
Δt = 0.1 s
Δx = 100.0/19 ≈ 5.26 m
CFL = 1.0 * 0.1 / 5.26 ≈ 0.019 < 1 ✓
```

**Stability condition satisfied** for the telegraph equation.

### 5.3 Numerical Dispersion

**Discrete dispersion relation:**
```
sin²(ωΔt/2) = (cΔt/Δx)² sin²(kΔx/2)
```

**For small Δt, Δx:**
```
ω ≈ c * k * [1 - (kΔx)²/24 + (ωΔt)²/24]
```

**Numerical dispersion error:** O(Δx², Δt²)

---

## 6. VALIDATION SCRIPT ANALYSIS

### 6.1 Implemented Equation (Validation Script)

**Actual equation:**
```
∂s/∂t = (c²/τ) ∇²s * (1 - 0.1Δt/τ)
```

**Classification:** Diffusion equation with time-dependent diffusion coefficient

**Propagation speed:** Zero (diffusion has no wave speed)

**Critical finding:** This equation cannot support wave propagation by construction.

### 6.2 Why c Measurement Failed

**Propagation detection logic (lines 162-220):**
```python
threshold = baseline + 0.5 * perturbation_amplitude
# Check if field value exceeds threshold at observer
```

**Why it failed:**
1. The equation is diffusion, not wave equation
2. Diffusion spreads smoothly, no sharp propagation front
3. Threshold detection assumes wave-like arrival
4. No wave front exists to detect

**Mathematical reason:** c_measured = 0 because the implemented equation has c = 0 (diffusion).

### 6.3 Why τ Measurement Succeeded

**Relaxation measurement (lines 222-278):**
```python
ln_amplitudes = np.log(amplitudes[significant_mask])
coeffs = np.polyfit(significant_times, ln_amplitudes, 1)
tau_measured = -1.0 / coeffs[0]
```

**Why it succeeded:**
1. Diffusion equations exhibit exponential decay
2. The multiplicative damping factor creates exponential decay
3. τ ≈ 3.17 s measured from fitted exponential

**Critical question:** Is this τ the same τ as in the theoretical Q?

**Answer:** NO. The measured τ is from the artificial damping factor `damping = -0.1`, not from the telegraph equation's physical damping term.

### 6.4 Why All Q Values Were Negative

**Q computation used:**
```
Q = 4c²τ²|∇ln s|² - 1
```

**With measured parameters:**
```
c = 1.0 m/s (nominal, not measured)
τ = 3.17 s (from artificial damping)
|∇ln s|² ≈ small (diffusion creates smooth gradients)
```

**Why Q < 0:**
1. Diffusion creates small gradients
2. Small |∇ln s|² → 4c²τ²|∇ln s|² < 1
3. Q ≈ -1 for smooth diffused fields

**Critical finding:** The diffusion equation cannot produce Q > 0 because it cannot create large spatial gradients required for coherent transport.

---

## 7. PARAMETER RELATIONSHIP ANALYSIS

### 7.1 τ Confusion

**Three different τ concepts:**

1. **Theoretical τ in telegraph equation:**
   - Physical damping time constant
   - Appears in: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
   - Units: seconds

2. **Measured τ from validation script:**
   - From exponential fit to diffusion decay
   - Related to artificial damping factor: `damping = -0.1`
   - τ_measured ≈ 3.17 s
   - NOT the theoretical τ

3. **Nominal τ in Q calculation:**
   - Parameter values used in sweep: τ = 0.5, 1.0, 2.0 s
   - NOT related to measured τ
   - NOT the theoretical τ

**Critical finding:** None of these τ values are the same physical quantity.

### 7.2 c Confusion

**Two different c concepts:**

1. **Theoretical c in telegraph equation:**
   - Physical wave propagation speed
   - Appears in: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
   - Units: m/s

2. **Nominal c in validation script:**
   - Parameter value: c = 1.0 m/s
   - c_measured = 0 (because equation is diffusion)
   - NOT the theoretical c

**Critical finding:** The validation script cannot measure c because it implemented the wrong equation.

---

## 8. BOUNDARY CONDITION ANALYSIS

### 8.1 Implemented Boundary Conditions

**Laplacian computation (lines 107-110):**
```python
laplacian[1:-1, :, 0] = (s[2:, :, 0] - 2*s[1:-1, :, 0] + s[:-2, :, 0]) / (dx**2)
```

**Boundary handling:** Central differences with implicit clamping (boundary points not updated)

**Classification:** Neumann-like (zero derivative at boundaries)

**Effect on propagation:** Reflects waves back into domain

### 8.2 Initial Conditions

**Initialization (lines 59-76):**
```python
field_values = np.full(nx * ny, initial_value)  # constant = 1.0
```

**Classification:** Uniform initial condition

**Effect on propagation:** No initial waves, only perturbations create dynamics

---

## 9. NUMERICAL INSTABILITY ANALYSIS

### 9.1 Baseline Instability Cause

**Observation:** Stability metric = 0.027324 (unstable)

**Analysis:**
```python
field['field_values'] = field['field_values'] * (1.0 + damping * dt / tau_nominal)
```

**With parameters:**
```
damping = -0.1
dt = 0.1
tau_nominal = 1.0
Factor = 1.0 + (-0.1) * 0.1 / 1.0 = 0.99
```

**Mathematical behavior:** Each step multiplies by 0.99 → exponential decay to zero

**Why called "unstable":** The baseline value of 1.0 decays to 0, not "unstable" in the numerical sense but "unstable" in the physical sense.

### 9.2 Numerical Stability Conditions

**For diffusion equation:**
```
Δt < Δx² / (2D)
where D = c²/τ
```

**Validation script parameters:**
```
D = 1.0² / 1.0 = 1.0
Δx = 5.26 m
Δt = 0.1 s
Condition: 0.1 < 5.26² / (2*1.0) = 13.8 ✓
```

**Numerical stability:** Satisfied

---

## 10. ANALYTICAL CRITICAL CONDITIONS

### 10.1 Critical Wavelength

**From dispersion relation:**
```
λ_c = 4πcτ
```

**With c = 1.0 m/s, τ = 1.0 s:**
```
λ_c = 4π * 1.0 * 1.0 ≈ 12.57 m
```

**Domain size:** 100m × 100m

**Critical wavenumber:**
```
k_c = 1/(2cτ) = 0.5 rad/m
```

### 10.2 Grid Resolution Requirements

**To resolve critical wavelength:**
```
Δx < λ_c / 10 = 1.26 m
```

**Actual grid spacing:**
```
Δx = 100/19 ≈ 5.26 m
```

**Critical finding:** Grid is too coarse to resolve critical wavelength (5.26 m > 1.26 m required)

### 10.3 Minimum Parameters for Q > 0

**To achieve Q > 0:**
```
4c²τ²k² > 1
k > 1/(2cτ)
```

**With current grid:**
```
k_min ≈ π/Δx ≈ π/5.26 ≈ 0.6 rad/m
```

**Required cτ:**
```
k_min > 1/(2cτ)  →  cτ > 1/(2k_min) ≈ 0.83
```

**With c = 1.0 m/s:**
```
τ > 0.83 s
```

**Critical finding:** τ = 1.0 s should be sufficient for Q > 0, but the wrong equation prevents it.

---

## 11. ROOT CAUSE ANALYSIS

### 11.1 Primary Failure: Wrong Equation

**The validation script implemented a diffusion equation instead of the telegraph equation.**

**Evidence:**
1. No second-order time derivative
2. No velocity field tracking
3. Arbitrary damping factor instead of physical damping term
4. Cannot exhibit wave propagation by construction

### 11.2 Secondary Failure: Parameter Confusion

**Three different τ values were conflated:**
1. Theoretical τ in telegraph equation (unused)
2. Measured τ from artificial damping (3.17 s)
3. Nominal τ in parameter sweep (0.5, 1.0, 2.0 s)

**Evidence:** None of these correspond to the same physical quantity.

### 11.3 Tertiary Failure: Grid Resolution

**Grid spacing Δx = 5.26 m is too coarse to resolve critical wavelength λ_c = 12.57 m.**

**Evidence:** Required Δx < 1.26 m, actual Δx = 5.26 m.

---

## 12. MINIMUM CHANGES REQUIRED

### 12.1 Implementation Corrections (Required)

1. **Use the official telegraph equation implementation**
   - File: `sim_world/domains/physical_field/physical_field_dynamics.py`
   - Use `evolve_field()` function, not the simplified version
   - Track velocity field properly

2. **Remove arbitrary damping factor**
   - Replace `damping = -0.1` with physical damping term `v/τ`
   - Use the telegraph equation's intrinsic damping

3. **Use proper initial conditions**
   - Initialize velocity field to zero
   - Use proper boundary conditions for wave equation

### 12.2 Parameter Corrections (Required)

1. **Use consistent τ**
   - τ should be the physical damping time constant
   - Should appear in both PDE and Q calculation
   - Should be measured from telegraph equation dynamics, not diffusion

2. **Use consistent c**
   - c should be the physical wave speed
   - Should be measured from wave propagation, not assumed
   - Should be the same in PDE and Q calculation

### 12.3 Grid Corrections (Required)

1. **Increase grid resolution**
   - Current: 20×20 grid, Δx = 5.26 m
   - Required: Δx < 1.26 m
   - Minimum: 80×80 grid (Δx ≈ 1.27 m)

2. **Adjust time step**
   - Current: Δt = 0.1 s
   - Required: CFL condition with finer grid
   - New: Δt < Δx/c = 1.27/1.0 = 1.27 s

### 12.4 Experimental Corrections (Required)

1. **Use proper perturbation scale**
   - Current: amplitude = 2.0, width = 5.0 m
   - Required: width > λ_c to excite propagating modes
   - New: width ≈ 15-20 m

2. **Use proper propagation detection**
   - Current: threshold detection (assumes wave front)
   - Required: cross-correlation or energy tracking
   - New: track wave packet center of mass

---

## 13. PROPOSED EXPERIMENTAL CONFIGURATION

### 13.1 Corrected Parameters

**Grid:**
- Resolution: 80×80×1
- Domain: 100m × 100m × 1m
- Spacing: Δx = Δy ≈ 1.27 m
- Time step: Δt = 0.05 s

**Physical parameters:**
- c = 1.0 m/s (initial guess)
- τ = 1.0 s (initial guess)
- Critical wavelength: λ_c = 4πcτ ≈ 12.57 m

**Perturbation:**
- Amplitude: 2.0
- Width: 15.0 m (> λ_c)
- Position: (50.0, 50.0, 0.0)

**Evolution:**
- Duration: 20.0 s
- Output: Every 0.5 s

### 13.2 Validation Steps

1. **Baseline stability:** Verify uniform field remains stable
2. **Wave propagation:** Track perturbation center of mass
3. **c measurement:** Measure speed from center-of-mass motion
4. **τ measurement:** Measure decay from amplitude fit
5. **Q calculation:** Use measured c and τ
6. **Regime classification:** Compare Q to wave vs diffusive behavior

### 13.3 Expected Results

**With corrected implementation:**
- Wave propagation should be observable
- c ≈ 1.0 m/s should be measurable
- τ ≈ 1.0 s should be measurable
- Q should vary from negative to positive depending on location
- Q > 0 should correspond to coherent wave behavior
- Q < 0 should correspond to diffusive behavior

---

## 14. IMPLEMENTATION VS THEORETICAL GAP

### 14.1 What Was Actually Implemented

**Validation script:**
- Diffusion equation with artificial damping
- No wave propagation capability
- Arbitrary parameter relationships
- Grid too coarse for critical wavelength

**Official implementation:**
- Correct telegraph equation
- Wave propagation capability
- Proper parameter relationships
- Grid may still be too coarse

### 14.2 What Was Intended

**Theoretical telegraph equation:**
- τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
- Wave propagation with damping
- Coherent/critical/overdamped regimes
- Q = 4c²τ²|∇ln s|² - 1

### 14.3 Gap Analysis

**Gap 1: Equation Implementation**
- Intended: Second-order telegraph equation
- Validation script: First-order diffusion equation
- Status: **FIXED** (use official implementation)

**Gap 2: Parameter Consistency**
- Intended: Same c, τ in PDE and Q
- Validation script: Different c, τ in different places
- Status: **FIXED** (use measured parameters consistently)

**Gap 3: Grid Resolution**
- Intended: Resolve critical wavelength
- Validation script: Too coarse
- Status: **FIXED** (increase resolution to 80×80)

**Gap 4: Boundary Conditions**
- Intended: Proper wave equation BCs
- Validation script: Implicit clamping
- Status: **NEEDS ATTENTION** (use absorbing BCs)

---

## 15. FINAL CLASSIFICATION

### 15.1 Mathematical Status

**Telegraph equation:** ✅ Properly implemented in official code  
**Diffusion equation:** ❌ Wrongly implemented in validation script  
**Parameter relationships:** ❌ Inconsistent across components  
**Grid resolution:** ❌ Insufficient for critical wavelength  
**Boundary conditions:** ⚠️ Suboptimal for wave propagation  

### 15.2 Scientific Status

**Q computation:** ✅ Mathematically correct  
**Physical interpretation:** ❌ Using wrong equation  
**Regime access:** ❌ Cannot access Q > 0 with current setup  
**Measurement validity:** ❌ Measuring wrong physical quantities  

### 15.3 Implementation Status

**Official implementation:** C - Theoretically correct but untested  
**Validation script:** E - Fundamentally wrong equation  
**Overall assessment:** C - Needs implementation corrections

---

## 16. NEXT STEPS

### 16.1 Immediate Actions

1. **Replace validation script with official implementation**
2. **Increase grid resolution to 80×80**
3. **Use consistent parameters throughout**
4. **Implement proper wave propagation detection**

### 16.2 Testing Protocol

1. **Verify wave propagation in corrected implementation**
2. **Measure c from actual wave dynamics**
3. **Measure τ from actual damping dynamics**
4. **Compute Q with measured parameters**
5. **Validate regime classification**

### 16.3 Validation Criteria

**Success criteria:**
- Wave propagation observable
- c ≈ nominal value within uncertainty
- τ ≈ nominal value within uncertainty
- Q varies across regimes
- Q > 0 corresponds to coherent behavior
- Q < 0 corresponds to diffusive behavior

**Failure criteria:**
- No wave propagation after corrections
- c or τ not measurable
- Q stuck in single regime
- Q does not correlate with transport behavior

---

**Audit Complete:** Mathematical reconstruction reveals fundamental implementation errors in validation script.  
**Primary Issue:** Wrong equation (diffusion instead of telegraph)  
**Secondary Issue:** Parameter confusion and grid resolution  
**Resolution:** Use official implementation with corrected parameters and grid.
