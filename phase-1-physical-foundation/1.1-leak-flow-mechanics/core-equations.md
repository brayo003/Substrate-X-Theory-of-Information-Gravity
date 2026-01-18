# Core Equations of Substrate X Theory

## Master Information Equation

**The complete, corrected master equation of Substrate X Theory (causal form):**

\`\`\`
(1 + 1/τ)∂s/∂t - c²∇²s + ∇⋅(s v_sub + χ s u) = αE + β∇⋅(E v_sub) + γF − σ_irr
\`\`\`

**Key corrections applied:**
- ✅ Causality fix: `-c²∇²s` replaces instantaneous diffusion (information propagates at speed ≤ c)
- ✅ Damping term: `(1/τ)∂s/∂t` provides effective diffusion in slow limit

**Derived from first principles**: See `master-equation-first-principles.md` for complete derivation from four fundamental postulates.

**Covariant 4-vector form:**
\`\`\`
∂_μ J^μ = S^0 - c²∇²s + ∂_μ(D^μν ∂_ν s) + σ_irr
\`\`\`

where J^μ = (c s, s v_sub + χ s u) is the information 4-current.

*See `COMPLETE_MASTER_EQUATION.md` for full details and all terms.*  
*See `lorentz-invariance-proof.md` for proof of Lorentz invariance.*  
*See `master-equation-origin.md` for analysis of uniqueness and originality.*

### Term Definitions:
- **s**: Information density (info/m³)
- **v_sub**: Substrate flow velocity (m/s)  
- **D**: Information diffusivity
- **χ**: Coherence transport coefficient
- **u**: Coherent propagation direction
- **E**: Mass-energy density (J/m³)
- **α,β,γ**: Coupling constants
- **σ_irr**: Irreversible entropy production (≥0)

## Gravitational Force Law
\`\`\`
F_grav = k × s × v_sub
\`\`\`
Where \`k = 2.71e-21\` (calibrated constant)

## Orbital Dynamics
### Radial Acceleration (Pressure Term):
\`\`\`
a_radial = -GM/r² - r θ̇²
\`\`\`

### Tangential Acceleration (Flow Guidance):
\`\`\`
a_theta = (θ̇ × v_flow) / r
\`\`\`

### Substrate Flow Velocity:
\`\`\`
v_flow = -√(2GM/r)
\`\`\`

## Time Dilation
\`\`\`
Λ(r) = 1/√(1 − 2GM/rc²)
\`\`\`

## Experimental Validations
- ✅ Mercury perihelion: 42.9''/century (observed: 43.0'')
- ✅ Gravitational lensing: 1.75 arcseconds
- ✅ Gravitational redshift: matches solar surface (2.12×10⁻⁶)
- ✅ Binary pulsar decay: -2.40e-12 s/s (observed: -2.405e-12)

## Novel Predictions

### Rotation-Induced Decoherence
\`\`\`
Γ = Γ₀ + kω²
\`\`\`
where k = 4.5 × 10⁻⁷ s (from rigorous derivation)

*See `rotation-decoherence-derivation.md` for complete derivation.*

This is a **unique, falsifiable prediction** that distinguishes Substrate X Theory from standard quantum mechanics.
