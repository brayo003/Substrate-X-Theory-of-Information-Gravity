# Part 3: Global Integral Analysis

**Objective**: Integrate the continuity equation over an arbitrary volume using the divergence theorem to determine whether ∫ s dV is conserved.

## 3.1 Starting Point: Master Equation in Integral Form

Taking the volume integral of the master equation over arbitrary volume V:

```
∫_V [τ ∂²s/∂t² + ∂s/∂t] dV = ∫_V [c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr] dV
```

## 3.2 Left-Hand Side Analysis

**Time derivatives**:
```
∫_V [τ ∂²s/∂t² + ∂s/∂t] dV = τ ∂²/∂t² ∫_V s dV + ∂/∂t ∫_V s dV
```

**Defining total information**: S_total(t) = ∫_V s(r,t) dV

```
∫_V [τ ∂²s/∂t² + ∂s/∂t] dV = τ d²S_total/dt² + dS_total/dt
```

## 3.3 Right-Hand Side Analysis Using Divergence Theorem

### Diffusion Term
```
∫_V c²τ ∇²s dV = ∫_V ∇·(c²τ ∇s) dV = ∫_∂V c²τ (∇s)·n̂ dA
```

Where ∂V is the boundary surface and n̂ is the outward normal.

**Physical interpretation**: Net diffusive flux through boundary.

### Advection Term  
```
∫_V ∇·(s v_sub + χ s u) dV = ∫_∂V (s v_sub + χ s u)·n̂ dA
```

**Physical interpretation**: Net advective + coherent flux through boundary.

### Energy Flow Term
```
∫_V β∇·(E v_sub) dV = β ∫_∂V (E v_sub)·n̂ dA  
```

**Physical interpretation**: Net energy flux through boundary.

### Local Source Terms
```
∫_V [αE + γF − σ_irr] dV = ∫_V αE dV + ∫_V γF dV − ∫_V σ_irr dV
```

**Physical interpretation**: Volume-integrated sources and sinks.

## 3.4 Complete Global Balance Equation

Combining all terms:
```
τ d²S_total/dt² + dS_total/dt = ∫_∂V [c²τ (∇s)·n̂ - (s v_sub + χ s u)·n̂ + β(E v_sub)·n̂] dA + ∫_V [αE + γF − σ_irr] dV
```

**Simplifying notation**:
- **Boundary flux**: Φ_boundary = ∫_∂V [c²τ (∇s)·n̂ - (s v_sub + χ s u)·n̂ + β(E v_sub)·n̂] dA
- **Volume sources**: Q_volume = ∫_V [αE + γF − σ_irr] dV

```
τ d²S_total/dt² + dS_total/dt = Φ_boundary + Q_volume
```

## 3.5 Conservation Analysis

### Case 1: Isolated System (No Boundary Flux)
If Φ_boundary = 0 (either infinite volume or zero flux boundary conditions):

```
τ d²S_total/dt² + dS_total/dt = Q_volume
```

**Conservation analysis**:
- **If Q_volume = 0**: Information is conserved in damped oscillator form
- **If Q_volume > 0**: Total information increases (net creation)  
- **If Q_volume < 0**: Total information decreases (net destruction)

### Case 2: Open System (With Boundary Flux)
If Φ_boundary ≠ 0:

```
τ d²S_total/dt² + dS_total/dt = Φ_boundary + Q_volume
```

**Conservation analysis**: Total information change depends on both boundary flux and volume sources/sinks.

## 3.6 Steady-State Global Analysis

**Steady-state condition**: dS_total/dt = d²S_total/dt² = 0

```
0 = Φ_boundary + Q_volume
```

**Mathematical requirement**: Φ_boundary = -Q_volume

**Physical interpretation**: In steady state, boundary flux exactly balances volume sources.

## 3.7 Irreversible Loss Analysis

The irreversible term contributes:
```
∫_V σ_irr dV ≥ 0
```

Since σ_irr ≥ 0 everywhere by definition.

**Consequence**: Even if all other sources (αE, γF, βE·v_sub) vanish, the system has:
```
τ d²S_total/dt² + dS_total/dt = Φ_boundary - ∫_V σ_irr dV ≤ Φ_boundary
```

**Implication**: Irreversible loss provides a **systematic drain** on total information unless compensated by boundary flux or other sources.

## 3.8 Diffusion Limit Analysis (τ → 0)

In the diffusion limit:
```
dS_total/dt = Φ_boundary + Q_volume
```

This is a **first-order global balance equation**.

**Conservation behavior**:
- **If Φ_boundary + Q_volume = 0**: dS_total/dt = 0 (conserved)
- **If Φ_boundary + Q_volume > 0**: dS_total/dt > 0 (increasing)  
- **If Φ_boundary + Q_volume < 0**: dS_total/dt < 0 (decreasing)

## 3.9 Boundary Condition Effects

### Flux Boundary Conditions
If n̂·J = specified flux at boundary:
```
Φ_boundary = ∫_∂V flux_specified dA
```

**Result**: Boundary flux is externally controlled and can drive information in/out.

### Dirichlet Boundary Conditions  
If s = s_boundary at boundary, then ∇s·n̂ is determined by the field configuration.

**Result**: Boundary flux depends on field gradients, creating feedback between interior and boundary.

### Periodic/Closed Boundaries
If boundary fluxes cancel (e.g., periodic or closed system):
```
Φ_boundary = 0
```

**Result**: Only volume sources Q_volume affect total information.

## 3.10 Mathematical Classification of Global Behavior

Based on the global analysis:

### Information is NOT Globally Conserved
**Mathematical proof**: The global balance equation
```
τ d²S_total/dt² + dS_total/dt = Φ_boundary + Q_volume
```

is NOT of the form dS_total/dt = 0 unless both:
1. Φ_boundary = 0 (no boundary flux)
2. Q_volume = 0 (no volume sources/sinks)

### Information Evolution Depends on:
1. **Boundary flux** Φ_boundary (transport across boundaries)
2. **Volume sources** Q_volume (local creation/destruction)  
3. **Inertial effects** τ d²S_total/dt² (information has "mass-like" behavior)

### Monotonic Behavior Conditions
**Monotonic decrease**: Requires Q_volume < -|Φ_boundary| with dominant σ_irr term

**Monotonic increase**: Requires Q_volume > |Φ_boundary| with dominant creation terms

**Neither guaranteed**: General behavior depends on spatial distribution of sources and boundary conditions.

## 3.11 Specific Analysis for Frozen Theory Parameters

From the frozen documents, the source terms are present:
- αE: Energy creates information  
- β∇·(E v_sub): Energy flow creates information
- γF: Forces create information
- σ_irr: Irreversible loss destroys information

**Mathematical conclusion**: Unless the system is carefully constructed to have Q_volume = Φ_boundary = 0, **information is neither globally conserved nor monotonic**.

## 3.12 Implications for Memory and Back-Action

**Memory implication**: Since total information S_total is not conserved, the substrate does not maintain a **conserved memory** of past interactions.

**Back-action implication**: The global analysis confirms the local finding from Part 2 - sources affect information, but there's no mathematical mechanism for information to affect the sources back through global conservation laws.

**Key mathematical result**: The substrate is a **dissipative system with external driving** - it can gain or lose information depending on external fields and boundary conditions, but it does not conserve information in a way that would enable future back-action through accumulated substrate state.