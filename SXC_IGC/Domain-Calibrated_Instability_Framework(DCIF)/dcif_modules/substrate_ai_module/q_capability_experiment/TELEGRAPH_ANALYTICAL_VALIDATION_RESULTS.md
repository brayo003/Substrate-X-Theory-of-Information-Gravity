# Telegraph Equation Analytical Validation Results

**Validation Date:** 2026-08-09

**PDE:** τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s

**Numerical Scheme:** Semi-implicit Euler: v_new = v + dt*(c²∇²s - v/τ), s_new = s + dt*v_new

**Final Classification:** A

---

## Test Parameters

- c: 1.0 m/s
- τ: 1.0 s
- Wavelength: 5.0 m
- Amplitude: 0.5
- Baseline: 1.0
- Resolution factor: 40 cells/wavelength
- Duration: 5.0 s
- Time step: 0.01 s

## Analytical Solution

- k: 1.2566 rad/m
- ω: 1.1529 rad/s
- Critical wavelength: 12.5664 m
- Phase velocity: 0.9174 m/s
- Propagating: True

## Numerical Results

- Measured damping rate γ: 0.5194 s⁻¹
- Measured τ: 0.9626 s
- Measured ω: 1.2255 rad/s
- Measured phase velocity: 0.9752 m/s
- Recovered c: 1.0592 m/s
- Max L2 error: 0.113205
- Mean L2 error: 0.077871
- Final L2 error: 0.098661

## Comparison with Theory

- τ error: 3.74%
- ω error: 6.30%
- c error: 5.92%
- γ error: 3.89%

## Classification

**A**

CASE A: Numerical solution propagates and matches analytical solution within expected numerical error.

## Refinement Test

Converges: True

- Resolution 10: L2 error = 0.102161
- Resolution 20: L2 error = 0.099755
- Resolution 40: L2 error = 0.098661
