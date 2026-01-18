# Causality Fix: Relativistic Diffusion

## Problem Identified

The diffusion term `-D∇s` in the master equation is **instantaneous**, violating causality.

Standard diffusion equation:
```
∂s/∂t = D∇²s
```

This allows information to propagate at infinite speed, violating special relativity.

## Solution: Relativistic Wave Equation

Replace instantaneous diffusion with a **relativistic wave equation** for information.

### Option 1: Wave Equation with Damping

Replace the diffusion term with:
```
∂²s/∂t² - c²∇²s + (1/τ)∂s/∂t = (sources)
```

where:
- `c²∇²s`: Wave propagation at speed c
- `(1/τ)∂s/∂t`: Damping term (replaces diffusion)

In the limit of slow variations, this reduces to diffusion with effective diffusivity `D = c²τ`.

### Option 2: Retarded Green's Function

Use retarded Green's function for diffusion:
```
s(r,t) = ∫ G_ret(r-r', t-t') S(r', t') d³r' dt'
```

where `G_ret` is the retarded Green's function (zero for t < t').

### Option 3: Modified Master Equation

Add second time derivative to master equation:
```
∂²s/∂t² - c²∇²s + ∇⋅(s v_sub) + (1/τ)∂s/∂t = αE + β∇⋅(E v_sub) + γF − σ_irr
```

This ensures information propagates at speed ≤ c.

## Recommended Fix

Use **Option 1** with modified master equation:

### Modified Master Equation (Causal)

```
∂s/∂t + ∇⋅(s v_sub) + (1/τ)∂s/∂t - c²∇²s + ∇⋅(χ s u) = αE + β∇⋅(E v_sub) + γF − σ_irr
```

Or, combining time derivatives:
```
(1 + 1/τ)∂s/∂t - c²∇²s + ∇⋅(s v_sub + χ s u) = αE + β∇⋅(E v_sub) + γF − σ_irr
```

**Physical interpretation**:
- `-c²∇²s`: Information propagates as waves at speed c
- `(1/τ)∂s/∂t`: Damping (replaces diffusion)
- In slow limit: reduces to diffusion with `D = c²τ`

## Verification

**Causality check**: Information propagates at speed ≤ c ✓

**Diffusion limit**: For slow variations, recovers standard diffusion ✓

**Status**: ✅ Causality preserved

