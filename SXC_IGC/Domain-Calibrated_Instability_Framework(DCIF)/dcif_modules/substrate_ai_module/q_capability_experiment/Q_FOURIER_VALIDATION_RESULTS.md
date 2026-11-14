# Q Fourier Validation Results

**Validation Date:** 2026-08-09

**Theoretical Q:** Q = 4 c² τ² |∇ln s|² - 1

**PDE:** τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s

**Dispersion Relation:** ω² = c²k² - 1/(4τ²)

**Critical Wavenumber:** k_c = 1/(2cτ)

**Critical Wavelength:** λ_c = 4πcτ

**Final Classification:** A

---

## Executive Summary

Total valid modes: 6
Q/transport agreement: 5/6 (83.3%)

## Configuration

- PDE: Telegraph equation
- Numerical scheme: Semi-implicit Euler
- Mode type: Controlled Fourier modes
- Resolution: 40 cells/wavelength
- Duration: 5.0s
- Time step: 0.01s

## Mode Results

**k = 0.2500 rad/m:**
- Analytical regime: overdamped
- Analytical ω: 0.0000 rad/s
- Measured ω: 0.0000 rad/s
- Measured τ: 9.4713 s
- Q mean: -0.8400
- Q regime: overdamped
- Independent regime: overdamped
- Agreement: True

**k = 0.4000 rad/m:**
- Analytical regime: overdamped
- Analytical ω: 0.0000 rad/s
- Measured ω: 0.0000 rad/s
- Measured τ: 3.5738 s
- Q mean: -0.5904
- Q regime: overdamped
- Independent regime: overdamped
- Agreement: True

**k = 0.5000 rad/m:**
- Analytical regime: critical
- Analytical ω: 0.0000 rad/s
- Measured ω: 0.0000 rad/s
- Measured τ: 2.1896 s
- Q mean: -0.3600
- Q regime: overdamped
- Independent regime: critical
- Agreement: False

**k = 0.7500 rad/m:**
- Analytical regime: coherent
- Analytical ω: 0.5590 rad/s
- Measured ω: 0.4349 rad/s
- Measured τ: 0.8279 s
- Q mean: 0.4400
- Q regime: coherent
- Independent regime: coherent
- Agreement: True

**k = 1.0000 rad/m:**
- Analytical regime: coherent
- Analytical ω: 0.8660 rad/s
- Measured ω: 0.9355 rad/s
- Measured τ: 0.8244 s
- Q mean: 1.5600
- Q regime: coherent
- Independent regime: coherent
- Agreement: True

**k = 1.2566 rad/m:**
- Analytical regime: coherent
- Analytical ω: 1.1528 rad/s
- Measured ω: 1.1817 rad/s
- Measured τ: 0.9446 s
- Q mean: 3.0424
- Q regime: coherent
- Independent regime: coherent
- Agreement: True

## Parameter Recovery

- Recovered c: 1.0828 m/s
- Recovered τ: 0.8622 s
- c error: 8.28%
- τ error: 13.78%

## Q Boundary Analysis

- Theoretical k_c: 0.5355 rad/m
- Q transition at k: 0.6250 rad/m
- Agreement: 16.70%

## Final Classification

**A**

A: Q demonstrates predictive regime validity.

---

## EXPERIMENTAL RESULT

Does the fixed theoretical Q correctly classify analytically known telegraph-equation transport regimes?

**Answer: YES**

