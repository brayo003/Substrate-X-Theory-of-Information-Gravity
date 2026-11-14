# FINITE-SPEED NULL MODELS AND PHONON NULL MODEL
## Competitor Models Producing ξ/τ = 2v Without C2

**Date:** 2026-08-21

---

## Model 1: Generic Symmetric PRW (Not C2)

Parameters: walker speed w (arbitrary), flip rate μ (arbitrary), NO FPUT substrate.

    ∂ₜn⁺ + w∂ₓn⁺ = −μ(n⁺ − n⁻)
    ∂ₜn⁻ − w∂ₓn⁻ = +μ(n⁺ − n⁻)

Results: ξ = w/μ, τ = 1/(2μ), ξ/τ = 2w.

**This model gives ξ/τ = 2w with ZERO connection to FPUT, C2, or any substrate.**

It is a pure random walk model with two free parameters. Fitting w and μ to data
reproduces the C2 prediction exactly with the same functional form.

---

## Model 2: Cattaneo-Vernotte Phonon Heat Transport (Standard Condensed Matter)

The standard model for non-Fourier heat conduction (Cattaneo 1948, Vernotte 1958):

    τ_ph ∂ₜₜT + ∂ₜT = D_th ∇²T

where D_th = α = thermal diffusivity, τ_ph = phonon scattering time.

This is the telegrapher equation with effective wave speed:

    c_ph = √(D_th/τ_ph) = √(κ/(ρ Cᵥ τ_ph))

where κ = thermal conductivity, ρ = density, Cᵥ = heat capacity.

Spatial correlation length: ξ_ph = c_ph/μ where μ = 1/τ_ph is the scattering rate.
Result: ξ_ph = c_ph τ_ph.
With τ ≡ 1/(2μ) = τ_ph/2: ξ_ph/τ = 2c_ph.

For crystalline solids at low temperature: c_ph = phonon group velocity → c_s (acoustic speed).

**Standard condensed-matter phonon transport, no C2:**

    ξ_ph / τ_ph = c_ph ≤ v_acoustic

This is identical to the C2 claim ξ_c/τ_B ≤ v_s.

**Reference:** C.C. Ackerman et al., "Second Sound in Solid Helium," PRL 1966.
G.P. Channell, "Heat Pulses in Crystals," Physical Review 1963.
These experiments MEASURE ξ/τ ~ c_sound in real systems without C2.

---

## Model 3: Telegraph Noise in Electronic Circuits (Random Telegraph Signal)

A random telegraph signal (RTS) switches between ±A at rate γ per direction.

Temporal autocorrelation: C(t) = A² exp(-2γ|t|), so τ_RTS = 1/(2γ).
Spatial autocorrelation (for a driven transmission line of speed v): ξ_RTS = v/γ.
Ratio: ξ_RTS/τ_RTS = 2v.

**Identical to C2. Used in electronic noise modeling since the 1950s.**
**No substrate physics, no FPUT, no information-theoretic content.**

---

## Model 4: Stochastic Wave Equation (Damped)

    ∂ₜₜu + 2γ∂ₜu = c²∂ₓₓu + noise(x,t)

Static correlator: <u(r)u(0)> ∝ exp(-r/ξ) with ξ = c/γ.
Temporal correlator: <u(t)u(0)> ∝ exp(-γ|t|), so τ = 1/γ, or with C2 convention τ = 1/(2γ).
Ratio: ξ/τ = 2c (same convention) or c (other convention).

**Generic stochastic hyperbolic PDE. No substrate specificity.**

---

## What the Null Models Show

Every model with (ballistic propagation at speed v) + (Poisson scattering at rate γ) + (spatial stationarity) gives:

    ξ = v/γ = mean free path
    τ = 1/(2γ) [with C2 convention]
    ξ/τ = 2v

This is the MEAN FREE PATH RELATION from kinetic theory. It is 160 years old
(Maxwell 1860) and applies to:
- Gas molecules (kinetic theory)
- Phonons in crystals
- Photons in scattering media
- Electrons in metals (Drude model)
- Telegraph signals
- PRW walkers
- C2 information quanta

**The C2 claim ξ_c/τ_B = 2c with c ≤ v_s is a statement that the C2 substrate
obeys the kinetic-theory mean free path relation — which is expected of any
ballistic+scattering system, and which has been measured in dozens of physical
systems without any reference to C2.**

---

## Phonon Null Model — The Critical Comparison

Suppose someone builds a standard model:
- Harmonic FPUT chain at temperature T
- Phonon scattering from anharmonic terms (or boundary)
- Phonon mean free time τ_ph
- Phonon group velocity c_ph ~ v_s (at long wavelength)

They measure:
- τ_ph from decay of heat pulse temporal profile
- ξ_ph from spatial decay of heat pulse

They find: ξ_ph = 2c_ph τ_ph, c_ph ≤ v_s.

**This is indistinguishable from the C2 prediction for a qubit dephasing experiment
using the same τ_B and ξ_c.**

The phonon null model is not "generic correlated noise." It is the SAME PHYSICAL
SYSTEM (harmonic FPUT chain) with a STANDARD INTERPRETATION (phonon transport)
producing the SAME PREDICTION without any C2 machinery.

**This is the most dangerous null model: it uses the same microscopic system.**
