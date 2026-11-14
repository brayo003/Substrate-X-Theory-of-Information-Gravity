# SUBSTRATE EQUATION MAP
**Source:** `domains/physical_field/physical_field_dynamics.py`  
**Date:** 2026-11-13  
**Method:** Direct source inspection — equations reconstructed from actual update operations, not documentation.

---

## State Variables

| Variable | Symbol | Shape | Location |
|----------|--------|-------|----------|
| `field_values` | s(x,t) | (nx×ny×nz,) | `FieldState.field_values` |
| `field_velocity` | v(x,t) = ∂s/∂t | (nx×ny×nz,) | `FieldState.field_velocity` |

## Parameters

| Parameter | Symbol | Location |
|-----------|--------|----------|
| `c_nominal` | c | `PropagationParameters.c_nominal` |
| `tau_nominal` | τ | `RelaxationParameters.tau_nominal` |
| `dt` | Δt | `FieldState.dt` |
| `dx`, `dy` | Δx, Δy | `FieldState.dx`, `FieldState.dy` |

---

## Governing Equations

### PDE (continuum form)

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S(x,t)
```

This is the **telegraph equation** (also: damped wave equation).

Equivalent first-order system (as implemented):
```
∂s/∂t = v
∂v/∂t = c² ∇²s  -  v/τ  +  S/τ
```

### Discretisation (`evolve_field`, lines 104–125)

```python
acceleration = (c**2) * laplacian - v / tau + source / tau  # ∂v/∂t
v_new = v + dt * acceleration                                # explicit Euler
s_new = s + dt * v_new                                       # explicit Euler
```

**Scheme:** Explicit forward Euler on both variables. First-order in time, O(Δt).

### Laplacian (`compute_laplacian`, lines 128–148)

```python
# Interior x-nodes (1..nx-2):
d2s_dx2 = (s[2:,:,:] - 2*s[1:-1,:,:] + s[:-2,:,:]) / dx²

# Interior y-nodes (1..ny-2):
d2s_dy2 = (s[:,2:,:] - 2*s[:,1:-1,:] + s[:,:-2,:]) / dy²

# Boundary nodes: Laplacian = 0 (not computed → left at 0)
```

**Spatial order:** Second-order central finite differences on interior nodes.

### Boundary Conditions

**Implicit zero-Laplacian at boundary nodes.** Not explicitly stated in code or documentation. Consequence: boundary nodes experience no spatial coupling; they evolve as `v' = -v/τ` only.

This is not standard Dirichlet (s=0) or Neumann (∂s/∂n = 0). It is a stencil-truncation artifact with the following properties:
- Equivalent to Neumann BC only for modes that have zero gradient at the boundary
- Introduces ~12.9% boundary contamination in the 30×30 EXP3 grid
- Does not cause numerical instability

### Perturbation (`apply_perturbation`)

```
s(x) → s(x) + A · exp(−|x−x₀|²/(2σ²))
```

Applied directly to `field_values` only. Does NOT perturb `field_velocity`.

---

## Spectral Observable (`compute_spectral_transport_observable`)

### Modal discriminant

```
D(k) = 4c²τ²|k|² − 1
```

| D(k) > +ε | propagating mode (damped oscillation) |
| D(k) < −ε | overdamped mode (pure exponential decay) |
| |D(k)| ≤ ε | critical boundary |

### Algorithm

1. Subtract spatial mean: δs = s − ⟨s⟩ (removes DC; prevents it dominating fractions)
2. 2D FFT of δs
3. Compute |k| for each mode; compute D(k)
4. Exclude DC bin (k=0) from power fractions
5. `f_prop` = sum(power where D(k) > ε) / total_AC_power
6. `f_over` = sum(power where D(k) < −ε) / total_AC_power
7. `C_spectral = f_prop − f_over ∈ [−1, +1]`

### Critical wavenumber

```
k_c = 1/(2cτ)       [rad/m]
```

For 30×30 grid, L=50m, c=1, τ=3: k_c = 1/(2·1·3) = 0.167 rad/m.  
Minimum resolved wavenumber: k_min = 2π/50 = 0.126 rad/m.  
Since k_min < k_c at τ=3, lowest modes are overdamped. Transition near τ ≈ 4.

---

## Implementation/Documentation Discrepancies

| Item | Documentation | Implementation |
|------|---------------|----------------|
| Boundary conditions | Not documented | Zero-Laplacian (stencil truncation) |
| `rng_precursor` stream | Declared (seed+5000) | Not instantiated — precursor uses `rng_schedule` |
| `c_measured` usage | "use if >0" | Defaults to `c_nominal=0.0` → uses nominal always in practice |

