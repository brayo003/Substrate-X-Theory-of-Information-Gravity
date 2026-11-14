# EXP9 Numerical Validation

**Date:** 2026-11-13
**all_pass:** `True`

Continuous metrics required in addition to binary activation agreement.

## dt_sensitivity

- pass: `True`
- pass_binary: `True`
- pass_continuous: `True`
- note: Binary agreement alone is insufficient; continuous local_max error also required.

## spatial_resolution_sensitivity

- pass: `True`
- pass_binary: `True`
- pass_continuous: `True`
- note: Task 8 binary-only grid check strengthened with continuous local_max error.

## high_deposit_density

- pass: `True`

## seed_reproducibility

- pass: `True`

## agent_decision_default_grid

- pass: `None`
- note: Operational claims use 30×30; continuous field refinement reported separately.

## boundary_condition_note

- pass: `True`
- note: compute_laplacian uses interior-only stencil (Dirichlet-like). Landmarks inset from boundary; BC sensitivity not claimed as varied.

