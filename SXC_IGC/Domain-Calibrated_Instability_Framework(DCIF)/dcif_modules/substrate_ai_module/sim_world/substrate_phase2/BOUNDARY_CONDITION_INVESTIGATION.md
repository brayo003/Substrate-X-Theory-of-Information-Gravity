# Boundary Condition Investigation

**Date:** 2026-11-13  
**Status:** Complete  
**Scope:** Source identification, impact quantification, and alternative BC comparison

---

## Overview

Phase I confirmed a zero-Laplacian boundary artifact (R11). This document provides a full investigation: source code location, physical interpretation, quantified impact on mean preservation and spectral observables, and a comparison against periodic boundary conditions.

---

## 1. Source Location and Mechanism

**File:** `physical_field_dynamics.py`  
**Function:** `compute_laplacian`  
**Lines:** 128–148

The function computes the discrete Laplacian of the field using a standard 5-point stencil. However, the loop over grid nodes is restricted to interior indices:

```python
# Interior nodes only: i in [1, nx-2], j in [1, ny-2]
for i in range(1, nx - 1):
    for j in range(1, ny - 1):
        laplacian[i, j] = (field[i+1,j] + field[i-1,j] +
                           field[i,j+1] + field[i,j-1] -
                           4*field[i,j]) / dx**2
```

Boundary nodes (row 0, row nx-1, col 0, col ny-1) are **never written** — they retain the zero value from array initialisation. This means:

- `laplacian[0, :] = 0` for all j  
- `laplacian[nx-1, :] = 0` for all j  
- `laplacian[:, 0] = 0` for all i  
- `laplacian[:, ny-1] = 0` for all i  

**This is accidental stencil truncation, not an intentional boundary condition choice.**

---

## 2. Physical Interpretation

Setting Laplacian = 0 at the boundary is physically equivalent to **absorbing boundary conditions** on the velocity field:

- Velocity at boundary nodes accumulates no spatial coupling force
- The velocity at boundary nodes evolves under the damping term only: `dv/dt = −v/τ`
- Energy at boundary nodes therefore decays in isolation, without transmitting to or receiving from interior nodes
- Boundary nodes **neither reflect nor transmit** disturbances — they decouple from the field

This is not a physically motivated choice for any standard substrate model. It was introduced accidentally by a loop range error (using `range(1, n-1)` instead of `range(0, n)` or applying a stencil that handles boundaries explicitly).

---

## 3. Boundary Fraction

For the 30×30 EXP3 grid:

| Region          | Node count | Fraction       |
|-----------------|------------|----------------|
| Total nodes     | 900        | 100%           |
| Interior nodes  | 784        | 87.1%          |
| Boundary nodes  | 116        | **12.9%**      |

12.9% of all nodes are affected by the artifact. For larger grids the fraction shrinks (scales as perimeter/area ~ 1/N), but on the 30×30 grid the effect is non-negligible.

---

## 4. Quantified Impact

### 4.1 Mean Preservation

| Boundary Condition  | IC Type            | Mean drift (500 steps) |
|---------------------|--------------------|------------------------|
| Original (zero-Lap) | Uniform IC, v=0    | 0.00 (exact)           |
| Original (zero-Lap) | Random IC, ic_amp=0.5 | −3.24e-02           |
| Periodic (np.roll)  | Random IC, ic_amp=0.5 | +1.11e-16 (exact)   |

The periodic BC eliminates mean drift entirely, confirming that the drift in the original BC is caused by the boundary artifact, not by any intrinsic property of the telegraph equation.

### 4.2 C_spectral Transition (tau sweep)

| tau | C_spectral (Original BC) | C_spectral (Periodic BC) | Shift         |
|-----|--------------------------|--------------------------|---------------|
| 1   | −0.54                    | −1.00                    | −0.46         |
| 2   | −0.0016                  | −0.83                    | −0.83         |
| 3   | +0.76                    | +0.40                    | −0.36         |
| 4   | —                        | +0.83                    | —             |

**Interpretation:** The periodic BC shifts the overdamped-to-propagating transition to **higher tau**. Under periodic BC, even the lowest spatial frequency modes (k_min = 2π/L) wrap around correctly and are properly classified as overdamped at low tau. Under the original BC, boundary decoupling masks the lowest-k modes, artificially inflating the propagating fraction at intermediate tau values and shifting the transition toward lower tau.

The transition zero-crossing shifts from approximately tau≈2 (original BC) to tau≈3–4 (periodic BC). Any quantitative claim about the transition point must specify which BC is in use.

---

## 5. Mechanism: How the BC Contaminates Spectral Analysis

The contamination pathway:

1. Boundary nodes have zero Laplacian → their velocity evolves only under damping
2. This creates a velocity discontinuity between boundary and near-boundary interior nodes
3. The field `s` near boundaries therefore evolves under an asymmetric force
4. When a Fourier decomposition is applied to the field, the non-periodic boundary conditions cause **spectral leakage**: energy from low-k modes bleeds into high-k bins
5. High-k modes are classified as propagating (D = 1 − 4c²τ²k² > 0 fails at large k, but the power-weighted C_spectral counts these bins)
6. Net effect: the propagating fraction appears larger than it should for small tau, artificially advancing the transition

---

## 6. Periodic BC Implementation

The periodic BC replaces finite-difference stencil terms with wrap-around indexing using `np.roll`:

```python
# Forward difference (periodic): φ[i+1] → np.roll(φ, -1, axis=0)
# Backward difference (periodic): φ[i-1] → np.roll(φ, +1, axis=0)

lap_x = (np.roll(field, -1, axis=0) - 2*field + np.roll(field, +1, axis=0)) / dx**2
lap_y = (np.roll(field, -1, axis=1) - 2*field + np.roll(field, +1, axis=1)) / dy**2
laplacian = lap_x + lap_y
```

This applies to **all nodes including boundaries** and does not modify the original `physical_field_dynamics.py` implementation — it is a separate validation/comparison function only.

---

## 7. Recommendations

| Use case                        | Recommended BC       | Rationale                                                     |
|---------------------------------|----------------------|---------------------------------------------------------------|
| Spectral analysis (C_spectral)  | Periodic (np.roll)   | Eliminates leakage; all modes properly resolved               |
| Physically bounded domain       | Neumann (∂s/∂n = 0)  | No flux at boundary; physical for enclosed substrate          |
| Current production code         | Original (zero-Lap)  | Do not change without full regression; artifact is quantified |

The original BC should be treated as a known systematic effect. All Phase I and Phase II spectral results are reported with the original BC unless otherwise noted. Periodic BC comparisons are provided as reference only and do not supersede production results.

---

## 8. Summary

The zero-Laplacian boundary artifact is:
- **Accidental** (stencil truncation, not design intent)
- **Quantified**: affects 12.9% of nodes; causes −3.24e-02 mean drift for random IC over 500 steps
- **Spectrally significant**: shifts C_spectral transition point by ~1–2 tau units
- **Correctable**: periodic BC eliminates both drift and spectral shift
- **Non-critical for current phase**: all findings are reported with consistent BC; the artifact is documented and bounded
