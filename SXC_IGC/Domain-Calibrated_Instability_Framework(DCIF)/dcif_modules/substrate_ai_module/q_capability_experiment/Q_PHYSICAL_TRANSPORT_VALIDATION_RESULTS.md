# Q Physical Transport Validation Results

**Validation Date:** 2026-08-09

**Theoretical Q:** Q = 4 c² τ² |∇ ln s|² - 1

**PDE Used:** τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s

**Numerical Scheme:** Semi-implicit Euler with velocity tracking

**Final Classification:** D

---

## Executive Summary

Total experiments: 3
Successful experiments: 3
Q/transport agreement: 0/3
Agreement rate: 0.00%

## Configuration

- Grid: 80×80×1 (1.27m spacing)
- Domain: 100m×100m×1m
- Time step: 0.05s
- Boundary conditions: Clamped (implicit)
- Initial conditions: s=1.0, v=0

## Measurement Methods

**Propagation speed:** Center-of-mass tracking of perturbation
**Relaxation time:** Exponential fit to amplitude decay
**Q calculation:** Spatial gradient using physical metric
**Transport regime:** Independent classification based on measurable propagation

## Parameter Sweep Results

**Experiment 1:**
- Grid: 60×60
- c_nominal: 1.0 m/s
- τ_nominal: 1.0 s
- Perturbation width: 8.0 m
- c_measured: 0.0000 ± 0.0000 m/s
- τ_measured: 37.4204 ± 0.0002 s
- Q mean: 1.3495
- Q range: [-1.0000, 30.0803]
- Transport regime: critical
- Q regime: coherent
- Agreement: False

**Experiment 2:**
- Grid: 60×60
- c_nominal: 1.0 m/s
- τ_nominal: 1.0 s
- Perturbation width: 15.0 m
- c_measured: 0.0000 ± 0.0000 m/s
- τ_measured: 120.6635 ± 0.0001 s
- Q mean: 22.9075
- Q range: [-1.0000, 111.3498]
- Transport regime: critical
- Q regime: coherent
- Agreement: False

**Experiment 3:**
- Grid: 60×60
- c_nominal: 1.0 m/s
- τ_nominal: 1.0 s
- Perturbation width: 20.0 m
- c_measured: 0.0000 ± 0.0000 m/s
- τ_measured: 211.1604 ± 0.0000 s
- Q mean: 70.9988
- Q range: [-0.8224, 172.0831]
- Transport regime: critical
- Q regime: coherent
- Agreement: False

## Resolution Convergence

**Resolution 40×40:**
- c_measured: 0.0000 m/s
- τ_measured: 121.5923 s
- Q mean: 23.4588

**Resolution 60×60:**
- c_measured: 0.0000 m/s
- τ_measured: 120.6635 s
- Q mean: 22.9075

Convergence metrics:
- c_std: 0.0000
- τ_std: 0.4644
- Q_std: 0.2756

## Critical Regime Test

**Width 10.05m:**
- Q mean: 4.2218
- Transport regime: critical
- Q regime: coherent
- Agreement: False

**Width 12.57m:**
- Q mean: 11.1215
- Transport regime: critical
- Q regime: coherent
- Agreement: False

**Width 15.08m:**
- Q mean: 23.4431
- Transport regime: critical
- Q regime: coherent
- Agreement: False

## Final Classification

**Classification:** D

**Evidence scores:**
- A: 0

- B: 0

- C: 1

- D: 2

- E: 2

---

## EXPERIMENTAL RESULT

Q does not correspond to independently measured transport regime.

## Q VALIDATION STATUS

INVALIDATED: Q does not predict transport regime.

## PROPAGATION RESULT

FAILURE: No wave propagation detected.

## RELAXATION RESULT

SUCCESS: Relaxation time measured in 3 experiments.

## Q/REGIME CORRESPONDENCE

Agreement rate: 0.00%

## NUMERICAL CONVERGENCE

NOT CONVERGED: Results depend on resolution.

## FALSIFICATION RESULT

PARTIALLY FALSIFIED: Only Q>0 regime observed.

## SCIENTIFIC CLASSIFICATION

D

## REMAINING LIMITATIONS

- Boundary conditions: Clamped (implicit), may cause reflections
- Grid resolution: May not resolve all relevant wavelengths
- Measurement methods: Center-of-mass tracking assumes coherent packets
- Parameter space: Limited subset of full parameter space tested

---

## FINAL ANSWER

**Does the implemented physical field produce independently observable transport dynamics for which the theoretical Q is a valid regime classifier?**

**Answer: NO**

