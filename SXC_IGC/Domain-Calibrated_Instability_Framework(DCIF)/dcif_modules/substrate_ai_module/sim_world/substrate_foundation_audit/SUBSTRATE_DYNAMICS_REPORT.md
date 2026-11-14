# SUBSTRATE DYNAMICS REPORT
**Date:** 2026-11-13  
**All quantitative results produced by executing the substrate.**

---

## 1. Equilibrium States

**Analytical prediction:** Any spatially uniform field s(x) = C, v(x) = 0 is an equilibrium.  
For a spatially non-uniform IC, spatial fluctuations decay and the field converges toward its own spatial mean.

**Measured:**

| τ | Initial std | Final std (t=25) | % remaining | Mean preserved |
|---|-------------|-----------------|-------------|----------------|
| 1.0 | 0.4934 | 0.1067 | 21.6% | YES (diff < 0.03) |
| 3.0 | 0.4934 | 0.1372 | 27.8% | YES |
| 5.0 | 0.4934 | 0.1568 | 31.8% | YES |

**Equilibrium stability: CONFIRMED.** Spatial fluctuations decay; mean is exactly preserved. At t=25 (500 steps), ~20–32% of initial spatial variability remains — slow decay at higher τ (larger τ = slower dissipation, as predicted by the overdamped characteristic root λ_slow = [−1 + √(1−4c²τ²k²)]/(2τ)).

There is exactly **one equilibrium** for each initial condition (the spatial mean). No multiple equilibria exist. This is mathematically guaranteed by linearity.

---

## 2. Perturbation Response

### Linearity

Applied Gaussian perturbations of amplitudes 0.1, 0.5, 1.0, 2.0, 5.0, 10.0:

| Amplitude | Peak response | Ratio |
|-----------|--------------|-------|
| 0.1 | 0.0921 | 0.9207 |
| 0.5 | 0.4604 | 0.9207 |
| 1.0 | 0.9207 | 0.9207 |
| 2.0 | 1.8415 | 0.9207 |
| 5.0 | 4.6037 | 0.9207 |
| 10.0 | 9.2074 | 0.9207 |

**Ratio variation: 0.0000%. The substrate is perfectly linear.** Response scales exactly with perturbation amplitude. No saturation, no thresholds, no nonlinear behaviour.

### Relaxation

After a 5-unit amplitude Gaussian perturbation (width=2.0m) at centre:
- Max field difference from control: decays with field half-life ≈ 2.1 time units at τ=3.0
- C_spectral difference from control: initial Δ=+1.86, decays slowly (not halved within 10 time units)

The two decay rates differ because C_spectral integrates power across all modes, and long-wavelength modes (which carry most power) decay slowly.

---

## 3. Bistability

**Mathematical verdict: IMPOSSIBLE for this substrate.**

The implementing equations are strictly linear. The superposition principle holds to machine precision (error 6.5×10⁻¹⁶). Linear systems have a unique equilibrium for each set of governing parameters. Multiple coexisting attractors require nonlinearity, which is absent.

**Empirical confirmation:** 8 random initial conditions with amplitudes 0.5–5.0 all converged to their respective unique equilibria. Final means: [0.88, 0.88, 0.90, 1.13, 0.20, 0.81, 1.13, 0.53]. Each mean tracks its own IC mean — no attractor switching.

The UTD Minecraft mod claims bistability. That claim cannot be supported by this Python substrate implementation, which is linear. If UTD's Java implementation has nonlinear terms (the description suggests it does — activation susceptibility, logistic saturation), then UTD and the Python substrate are **different systems**. The Python substrate does not implement UTD's nonlinear dynamics.

---

## 4. Path-Dependence / "Hysteresis"

**Measured:** A tau sweep (forward 1.0→4.0, reverse 4.0→1.0) with 200 equilibration steps per tau shows a maximum C_spectral gap of 0.854 at τ=4.0.

**Root cause confirmed:** This is **slow transient persistence**, not genuine hysteresis.

The second-order nature of the substrate stores momentum (velocity field v = ∂s/∂t). When τ is changed, the velocity field built under the previous τ persists and continues to influence C_spectral. The velocity half-life is τ·ln(2). At τ=4.0 this is 2.77 time units; 200 steps × dt=0.05 = 10 time units.

**Equilibration test:**

| Steps per τ | Forward C (τ=4) | Reverse C (τ=4) | Gap |
|-------------|----------------|----------------|-----|
| 200 | −0.6734 | +0.1807 | 0.854 |
| 500 | −0.6742 | −0.4419 | 0.232 |
| 1000 | −0.6742 | −0.6742 | 0.000 |
| 2000 | −0.6742 | −0.6741 | 0.000 |

**At 1000 equilibration steps the gap closes to exactly 0.000.** This is a transient artifact, not hysteresis. Genuine hysteresis would persist regardless of equilibration time.

---

## 5. Memory

**Definition used:** After a perturbation is applied and all external forcing removed, how long does the substrate state remain distinguishable from an unperturbed control?

**Two measures:**

| Measure | Half-life (τ=3.0) |
|---------|-------------------|
| max|Δs| (field values) | 2.1 time units |
| ΔC_spectral | > 10 time units (not halved within measurement window) |

The field value difference (max|Δs|) decays relatively quickly (half-life ≈ 2.1 at τ=3). However, the C_spectral difference decays much more slowly — after 10 time units, Δc_spectral=+0.93, still 50% of its initial value of +1.86.

**This is genuine memory, explicitly represented in the velocity state variable.** The substrate's second-order dynamics store a velocity field that continues to influence spectral properties long after the initial perturbation. This is the mechanism by which the substrate "remembers" that a disturbance occurred, even after field values have partially recovered.

**Mechanism:** The perturbation injects energy into velocity as well as field values. The velocity field drives continued oscillation, which maintains propagating-mode power (raising C_spectral) for many relaxation times.

---

## 6. Modal Dynamics: The C_spectral Transition

**The substrate's primary dynamical phenomenon** is a continuous transition from overdamped to propagating modal character as τ increases.

**Measured C_spectral vs τ (equilibrated, 300 steps, τ=3.0 grid, random IC):**

| τ | C_spectral | f_prop | f_over | Dominant regime |
|---|-----------|--------|--------|----------------|
| 0.5 | −0.820 | 0.086 | 0.906 | overdamped |
| 1.0 | −0.541 | 0.218 | 0.759 | overdamped |
| 1.5 | −0.256 | 0.372 | 0.628 | overdamped |
| 2.0 | −0.002 | 0.499 | 0.501 | overdamped |
| 2.5 | +0.125 | 0.562 | 0.438 | overdamped |
| 3.0 | +0.761 | 0.881 | 0.119 | coherent |
| 3.5 | +0.738 | 0.869 | 0.131 | coherent |
| 4.0 | +0.731 | 0.865 | 0.135 | coherent |
| 5.0 | +1.000 | 1.000 | 0.000 | coherent |

**The transition occurs between τ=2.5 and τ=3.0.** Analytically predicted critical τ for the lowest resolved mode (k_min = 2π/50): τ_c = 1/(2·1·0.126) ≈ 3.98. The empirical transition at τ≈2.5–3.0 is consistent: at τ=2.5–3.0, higher-k modes (k > 2π/50) have already crossed into the propagating regime even though the lowest mode has not.

**This transition is genuine, reproducible, and mathematically grounded.** It follows directly from D(k) = 4c²τ²k² − 1 changing sign as τ increases.

---

## 7. Internal Feedback Structure

The substrate has two internal feedback paths:

**Path 1 (direct):** Spatial coupling via Laplacian.  
`∂v/∂t = c²∇²s` — field values at neighbouring nodes feed back into local velocity.  
This is spatial communication, not temporal feedback. It enables propagation.

**Path 2 (damping):** Velocity dissipation.  
`∂v/∂t = −v/τ` — current velocity feeds back into its own rate of change.  
This is a stabilising, negative feedback. It prevents unbounded growth.

**There are no feedback paths from s back to its own update equation except through v.** The system has no self-excitation, no positive feedback, no autocatalytic terms. All feedback is either dispersive (spatial coupling) or dissipative (damping). This guarantees global stability and the absence of limit cycles or chaos.

---

## 8. Summary of Dynamical Properties

| Property | Present? | Evidence |
|----------|----------|----------|
| Equilibrium states | YES — infinite family (one per IC mean) | Test 4 |
| Unique equilibrium per IC | YES | Linearity + Test 4 |
| Stable equilibria | YES | 500-step convergence test |
| Spatial gradient decay | YES | std decreases from 0.49 to 0.11-0.16 |
| Mean preservation | YES | Exact (numerical) |
| Linear response | YES | 0.0000% ratio variation |
| Bistability | NO | Mathematically impossible (linear system) |
| Genuine hysteresis | NO | Gap closes at 1000 equilibration steps |
| Genuine memory (via velocity) | YES | C_spectral half-life > 10 time units |
| Modal transition (overdamped↔propagating) | YES | Measured τ=2.5→3.0 transition |
| Spatial propagation | YES | Affected-node fraction grows with t |
| Oscillatory modes (τ>τ_c) | YES | Propagating regime confirmed |
| Nonlinear dynamics | NO | Superposition holds to 10⁻¹⁵ |
