# DCIF: Gabriel's Horn Substrate
**Core Concept:** Information tension (`T_sys`) coupled to geometric drift (`z`).

## To Reproduce Core Finding:
python3 core/gabriel_horn_instability.py
> Simulation ended at z = 4.19
> Final Tension: 10.12

## To Validate Parameter Sensitivity:
Run each file in `/validation/`. Observe how modifying the geometry-parameter coupling (β, γ) changes the terminal state (z, T_sys).

## Key Interpretation:
Break Test 1: Gamma is the geometric brake.
Break Test 2: Beta must increase with narrowing radius for tension growth.
Break Test 3: Tension must perform work (dz/dt ∝ T_sys) for progression.

## Implied Physics:
The model suggests physical constants may be stationary points in a higher-dimensional information-geometric coupling.
