# Q THEORY REQUIREMENTS

**Source:** q_define.txt (authoritative definition)  
**Extraction Date:** 2026-08-09  
**Purpose:** Exact mathematical requirements from authoritative source

---

## EXACT Q DEFINITION

From q_define.txt, line 185:

```
Q = 4c²τ²|∇ln s|² − 1
```

This is stated as an assumption in the capability audit: "The transport PDE and Q = 4c²τ²|∇ln s|² − 1 are mathematically correct."

---

## COMPONENT DEFINITIONS

### s(x,t) - Information Density Field

**Definition from q_define.txt:**
- Line 13: "s: Information density (info/m³)"
- Line 193: "Q takes as input a scalar field s(x,t) and its spatial gradient"
- Line 205: "Q is a local transport-phase classifier that identifies, at every point (x,t), whether the substrate field s is in an oscillatory (coherent) or overdamped (incoherent) dynamical regime"

**Properties:**
- Scalar field (not vector)
- Function of space (x) and time (t)
- Units: info/m³ (information per unit volume)
- Must be positive where ln(s) is evaluated

**Domain Requirements:**
- x: spatial coordinates (physical space)
- t: temporal coordinate
- Field defined over spacetime

**Theoretical Context:**
- Evolves according to master equation: τ∂²s/∂t² + ∂s/∂t = c²τ∇²s − ∇⋅(sv_sub + χsu) + αE + β∇⋅(Ev_sub) + γF − σ_irr
- Describes information density in substrate

### ∇ - Spatial Gradient Operator

**Definition from q_define.txt:**
- Line 193: "spatial gradient"
- Line 386: "|∇ln s|² = g^{ij}(∂_i ln s)(∂_j ln s) where g^{ij} is the metric inverse"

**Properties:**
- Spatial gradient (not temporal)
- Operates on spatial coordinates x
- Coordinate-invariant scalar when squared magnitude is taken
- Metric g^{ij} defines spatial geometry

**Mathematical Form:**
- In Cartesian coordinates: ∇ = (∂/∂x, ∂/∂y, ∂/∂z, ...)
- In general coordinates: ∇ln s is a covector
- |∇ln s|² is scalar contraction: g^{ij}(∂_i ln s)(∂_j ln s)

### ∇ln(s) - Logarithmic Gradient

**Definition from q_define.txt:**
- Implied from Q formula: ∇ln(s) = ∇s / s
- Natural logarithm of information density field
- Spatial gradient of logarithm

**Mathematical Properties:**
- ∇ln(s) = ∇s / s (where s > 0)
- Dimensionless (gradient of log removes units)
- Coordinate-invariant when magnitude is taken

### |∇ln(s)|² - Squared Magnitude

**Definition from q_define.txt:**
- Line 386: "|∇ln s|² = g^{ij}(∂_i ln s)(∂_j ln s)"
- Scalar contraction of gradient covector

**Properties:**
- Scalar (coordinate-invariant)
- Dimensionless
- Always non-negative
- Zero when s is constant in space

### c - Propagation Speed

**Definition from q_define.txt:**
- Line 23: "c: Speed of light (m/s)"
- Line 25: "Information diffuses with effective diffusivity D = c²τ"
- Line 107: "c m/s Causal propagation speed"

**Properties:**
- Units: m/s (meters per second)
- Physical meaning: causal propagation speed
- Same as speed of light in vacuum (or effective speed in medium)
- Constant or field property (not state variable)

### τ - Damping Time Constant

**Definition from q_define.txt:**
- Line 15: "τ: Damping time constant (s)"
- Line 105: "τ s Damping time constant"
- Line 111: "D = c²τ m²/s Effective diffusivity"

**Properties:**
- Units: s (seconds)
- Physical meaning: damping/relaxation time
- Characteristic time for system relaxation
- Constant or field property (not state variable)

### Q - Transport Regime Classifier

**Definition from q_define.txt:**
- Line 185: "Q = 4c²τ²|∇ln s|² − 1"
- Line 193: "returns a signed scalar at every point in space and time"
- Line 197: "transport-phase classifier"
- Line 205: "local transport-phase classifier"

**Regime Interpretation:**
- Q > 0: oscillatory/coherent transport regime
- Q < 0: overdamped/incoherent transport regime  
- Q = 0: critical transport boundary

**Properties:**
- Scalar field over spacetime
- Dimensionless (combination of dimensionless |∇ln s|² and constant -1)
- Local and pointwise (defined at each (x,t))
- Coordinate-invariant

**Secondary Predictions:**
- Coherence length: ξ_c = 2cτ (from Q = 0 surface)
- Decoherence rate: Γ_dec ≤ 1/(2τ) as Q → 0⁻
- Critical slowing: Γ_dec → 0 as Q → 0⁻

---

## MATHEMATICAL RELATIONSHIPS

### Master Equation Context

From q_define.txt, line 5:

```
τ∂²s/∂t² + ∂s/∂t = c²τ∇²s − ∇⋅(sv_sub + χsu) + αE + β∇⋅(Ev_sub) + γF − σ_irr
```

Q is derived from the transport dynamics of this equation.

### Diffusivity Relationship

From q_define.txt, line 25:

```
D = c²τ
```

Effective diffusivity relates c and τ.

### Regime Boundary Condition

From q_define.txt, line 436:

```
Q = 0 ⟺ ωτ = 1/2 [at k = k_c]
```

For plane waves, Q = 0 corresponds to the standard telegraph equation crossover.

---

## COORDINATE REQUIREMENTS

### Spatial Coordinates x

**Definition from q_define.txt:**
- Implied: physical spatial coordinates
- Line 386: metric g^{ij} defines spatial geometry
- Must support gradient operation ∇
- Must support metric contraction g^{ij}

**Properties:**
- Physical space (not abstract feature space)
- Has metric structure
- Supports coordinate transformations
- Gradient is coordinate-invariant when contracted

### Temporal Coordinate t

**Definition from q_define.txt:**
- Line 13: time variable in master equation
- Line 193: "at every point in space and time"
- Appears in time derivatives of master equation

**Properties:**
- Physical time
- Independent variable for field evolution
- Not used in Q calculation directly (Q is pointwise in time)

---

## DIMENSIONAL ANALYSIS

### Units from q_define.txt

**s:** info/m³ (information per unit volume)

**c:** m/s (meters per second)

**τ:** s (seconds)

**∇:** 1/m (inverse meters, spatial derivative)

**ln(s):** dimensionless (logarithm removes units)

**∇ln(s):** 1/m (spatial derivative of dimensionless quantity)

**|∇ln(s)|²:** 1/m² (squared inverse meters)

**c²τ²:** (m/s)² × s² = m²

**4c²τ²|∇ln(s)|²:** dimensionless (m² × 1/m² = 1)

**Q:** dimensionless (dimensionless - 1)

### Dimensional Consistency

The equation Q = 4c²τ²|∇ln s|² − 1 is dimensionally consistent:
- 4c²τ²|∇ln s|² is dimensionless
- 1 is dimensionless
- Q is dimensionless

---

## UNDEFINED REQUIREMENTS

### Not Specified in q_define.txt

The following aspects are NOT defined in q_define.txt:

1. **Specific coordinate system:** Cartesian, spherical, etc. (any valid coordinate system allowed)
2. **Boundary conditions:** Not specified (depends on physical system)
3. **Normalization of s:** No normalization specified (s is absolute information density)
4. **Specific values of c and τ:** Must be determined from physical system
5. **Initial conditions:** Not specified (depends on physical system)
6. **Source terms in master equation:** α, β, γ, E, F, etc. are system-specific
7. **Metric g^{ij}:** Depends on physical space geometry (assumed Euclidean unless specified)

### Implementation Flexibility

The definition permits:
- Any valid spatial coordinate system with metric
- Any physically grounded values of c and τ
- Any boundary conditions appropriate to the physical system
- Any method for measuring s(x,t) as long as it represents information density

The definition does NOT permit:
- Replacing s with non-information-density quantities
- Replacing spatial gradient with temporal derivative
- Replacing physical coordinates with abstract feature space without metric justification
- Using arbitrary dimensionless values for c and τ without physical grounding

---

## MATHEMATICAL CONSTRAINTS

### Positivity Constraint

**Requirement:** s(x,t) > 0 wherever ln(s) is evaluated

**Reason:** ln(s) is undefined for s ≤ 0

**Implementation Requirement:** Must ensure s is positive before computing ln(s)

### Gradient Existence

**Requirement:** s must be differentiable in spatial coordinates

**Reason:** ∇s must exist to compute ∇ln(s)

**Implementation Requirement:** s must be smooth enough for gradient computation

### Metric Structure

**Requirement:** Spatial coordinates must have metric g^{ij}

**Reason:** |∇ln s|² = g^{ij}(∂_i ln s)(∂_j ln s) requires metric

**Implementation Requirement:** Must define metric if using non-Cartesian coordinates

---

## THEORETICAL vs IMPLEMENTATION DISTINCTION

### Theoretical Requirements (from q_define.txt)

1. s(x,t) is a scalar information density field (info/m³)
2. x represents physical spatial coordinates with metric
3. t represents physical time
4. ∇ is spatial gradient in physical space
5. c is physical propagation speed (m/s)
6. τ is physical damping time (s)
7. Q is dimensionless transport regime classifier

### Implementation Flexibility

The definition does NOT specify:
- How to measure s(x,t) experimentally
- How to determine c and τ for a specific system
- What coordinate system to use
- What numerical methods to use for gradients
- How to handle boundary conditions

These are implementation choices that must be consistent with the theoretical requirements.

---

**Status:** COMPLETE  
**Authority:** q_define.txt  
**Extraction Method:** Direct quotation and contextual analysis  
**Ambiguities:** None in core definition; implementation details left to specific physical systems
