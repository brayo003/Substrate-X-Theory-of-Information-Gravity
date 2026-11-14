# Approximation A Audit: Steady-State Approximation

**Audit objective:** Determine whether discarded dynamical terms ∂s/∂t and ∂²s/∂t² contain implicit quantum couplings.

## A.1 Original Approximation

From UNIFIED_PERTURBATIVE_DERIVATION.md Section 1.2:

**[A1] Steady state.**
All time derivatives are set to zero: ∂s/∂t = 0, ∂²s/∂t² = 0.
Justification: orbital and laboratory timescales are long compared to τ, so the system relaxes to a quasi-static equilibrium at each orbital phase.
Effect: the left-hand side of [ME] vanishes entirely.

## A.2 Complete Master Equation (Frozen)

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr
```

Under [A1], this reduces to:
```
0 = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr
```

## A.3 Audit Question

**What mathematical terms were discarded?**
- Second-order time derivative: τ ∂²s/∂t²
- First-order time derivative: ∂s/∂t

**Can those discarded terms couple to quantum internal degrees of freedom?**

To answer this, I need to:
1. Derive the complete time-dependent theory
2. Examine the structure of the discarded terms
3. Determine if they introduce operator-valued interactions
4. Check if removing the approximation changes the mathematical structure

## A.4 Complete Time-Dependent Derivation

Retaining full time dependence, the master equation is:
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr   [ME-full]
```

Apply approximations [A2] (source-free) and [A3] (no coherence transport):
E = 0, F = 0, σ_irr = 0, χ = 0

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub)   [ME-reduced]
```

## A.5 Analysis Framework

The discarded terms are:
1. **Inertial term**: τ ∂²s/∂t² - represents "information inertia"
2. **Damping term**: ∂s/∂t - represents relaxation to equilibrium

### A.5.1 Mathematical Structure Analysis

Both discarded terms are **scalar operations** on the scalar field s(r,t):
- τ ∂²s/∂t² takes a scalar function and returns a scalar function
- ∂s/∂t takes a scalar function and returns a scalar function

Neither term contains:
- Matrix structure that could act on quantum states
- Operator indices that could couple to internal degrees of freedom  
- Complex conjugation or commutator structure
- Coupling to Hilbert space operators

### A.5.2 Physical Interpretation

The τ ∂²s/∂t² term gives the master equation "telegrapher" character - it supports propagating wave solutions rather than pure diffusion.

The ∂s/∂t term represents damping/relaxation toward equilibrium.

## A.6 Time-Dependent Perturbation Analysis

Following the perturbation structure from UNIFIED_PERTURBATIVE_DERIVATION.md, but retaining time dependence:

Write s = s₀(r) + s₁(r,t) + s₂(r,t) + ...

### A.6.1 Zeroth Order (Background)

If the background s₀ is time-independent (which is physically reasonable for the gravitational field of a massive body), then:
```
∂s₀/∂t = ∂²s₀/∂t² = 0
```

The background equation reduces to the same steady-state form:
```
c²τ ∇²s₀ = ∇·(s₀ v_sub)
```

This gives s₀ = μ/r as before. **The background is unchanged.**

### A.6.2 First Order with Time Dependence

For s₁(r,t):
```
τ ∂²s₁/∂t² + ∂s₁/∂t = c²τ ∇²s₁ − ∇·(s₁ v_sub) + v·∇s₀
```

In the frozen derivation, s₁ was found to be a dipole field s₁ ∝ cos θ that averages to zero over orbital motion. With time dependence, s₁(r,t) can have temporal oscillations.

**Key question**: Do the time-derivative terms τ ∂²s₁/∂t² + ∂s₁/∂t introduce any coupling to quantum degrees of freedom?

**Analysis**: These are still scalar differential operations on the scalar field s₁. They describe the temporal evolution of the information density field but do not introduce:
- Coupling between different internal quantum states
- Matrix elements between quantum levels
- Operator structure acting on Hilbert space

### A.6.3 Second Order with Time Dependence

For s₂(r,t) (the δs field):
```
τ ∂²s₂/∂t² + ∂s₂/∂t = c²τ ∇²s₂ − ∇·(s₂ v_sub) + v·∇s₁(r,t)
```

The frozen derivation found δs = s₂ = −μL²/(c²r³) in steady state. With time dependence, s₂ could have temporal variations.

**Critical Analysis**: Even if s₂(r,t) has time dependence, the equation structure remains:
- Left side: scalar temporal derivatives of scalar field
- Right side: spatial derivatives of scalar field plus sources

No operator or matrix structure emerges from including time dependence.

## A.7 Dispersion Relation Analysis

The time-dependent master equation [ME-reduced] supports wave solutions. Taking a plane wave ansatz s ∝ e^(ikr - iωt):

```
τ(-iω)² + (-iω) = c²τ(-ik)² - ik·v_sub
```

Simplifying:
```
-τω² - iω = -c²τk² - ik·v_sub
```

This gives the dispersion relation:
```
τω² + iω - c²τk² - ik·v_sub = 0
```

For the homogeneous case (v_sub = 0):
```
τω² + iω - c²τk² = 0
```

Solutions:
```
ω = [-i ± √(-1 + 4c²τ²k²)] / (2τ)
```

### A.7.1 Physical Content of Wave Solutions

For short wavelengths (c²τ²k² >> 1/4):
```
ω ≈ ±ck - i/(2τ)
```

These are **damped propagating waves** - the telegrapher modes.

For long wavelengths (c²τ²k² << 1/4):
```
ω ≈ -i/τ  or  ω ≈ -ic²τk²
```

Pure exponential decay modes.

**Key Finding**: The wave solutions are classical field modes. They describe propagation and damping of the information density field s(r,t) but contain no quantum operator structure.

## A.8 Coupling to Matter Analysis

From the frozen theory, the coupling to matter occurs through:
1. **Gravity branch**: F_grav = k s v_sub (force law)
2. **Decoherence branch**: Γ ∝ ⟨|δJ|²⟩ where δJ = s(ω × r)

Both couplings act on the field s, not on its time derivatives.

### A.8.1 Time-Dependent Coupling

If s(r,t) has time dependence, then:
- Force becomes: F_grav(t) = k s(r,t) v_sub
- Current becomes: δJ(r,t) = s(r,t)(ω × r)

**Analysis**: These are still classical couplings. The time dependence makes the force and current time-dependent but does not introduce quantum internal coupling.

The time derivatives ∂s/∂t and ∂²s/∂t² do not appear directly in either coupling mechanism.

## A.9 Dimensional and Structural Analysis

### A.9.1 Units Check
- ∂s/∂t has units: (info/m³)/s = info/(m³·s)
- ∂²s/∂t² has units: (info/m³)/s² = info/(m³·s²)
- These match the units on the right side of the master equation

### A.9.2 Mathematical Structure Check
The complete master equation [ME-full] is:
- **Linear** in s and its derivatives
- **Real-valued** (no complex structure)
- **Scalar equation** (no matrix/tensor indices)
- **Classical PDE** (no ℏ, no commutators, no operators)

Including the time derivatives does not change these fundamental properties.

## A.10 Quantum Coupling Requirements

For the discarded terms to contain "implicit quantum couplings," they would need to:

1. **Introduce operator structure**: ∂s/∂t or ∂²s/∂t² would need to become operators on a Hilbert space
2. **Couple to internal degrees of freedom**: The terms would need to act differently on different quantum states
3. **Generate non-commuting objects**: The field s would need matrix character

**None of these occur** by simply retaining the time derivatives in a classical scalar PDE.

## A.11 Conclusion for Approximation A

**Why was the steady-state approximation introduced?**
To eliminate fast relaxation dynamics on timescale τ, focusing on the quasi-static limit relevant for orbital motion.

**What mathematical terms were discarded?**
- Inertial term: τ ∂²s/∂t²  
- Damping term: ∂s/∂t

**Can those discarded terms couple to quantum internal degrees of freedom?**
**NO.** Both terms are scalar differential operations on a scalar field. They introduce temporal dynamics but no quantum operator structure.

**Does removing the approximation change the mathematical structure?**
**NO.** The equation remains a linear, real-valued, classical scalar PDE. Time dependence adds wave solutions but preserves the classical character.

**Does it generate an operator-valued interaction?**
**NO.** All terms remain scalar-valued.

**Does it introduce a Hamiltonian naturally?**
**NO.** The master equation is dissipative (contains ∂s/∂t damping), not Hamiltonian. A Hamiltonian structure would require auxiliary fields (like the Bateman doubling), which is not present in the original equation.

**Does it produce an experimentally controllable observable?**
**NO.** The time-dependent solutions are classical field modes. They could modulate the existing observables (gravitational force, decoherence rate) in time, but do not create fundamentally new observables with quantum internal coupling.

## A.12 Verdict

**APPROXIMATION A DOES NOT DISCARD IMPLICIT QUANTUM COUPLINGS**

The steady-state approximation removes classical temporal dynamics from a classical scalar field equation. No quantum internal coupling was present in the discarded terms.
