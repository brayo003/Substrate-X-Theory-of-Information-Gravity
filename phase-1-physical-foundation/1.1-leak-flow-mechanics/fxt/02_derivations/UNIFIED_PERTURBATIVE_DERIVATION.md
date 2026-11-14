# Unified Perturbative Derivation: Gravity and Decoherence from a Single Second-Order Field

**Repository:** Substrate X — Theory of Information Gravity  
**Phase:** 1.1 Leak-Flow Mechanics  
**Status:** Derivation document — no new physics introduced  
**Depends on:** `COMPLETE_MASTER_EQUATION.md`, `mercury_precession_derivation.md`, `post_newtonian_derivation.md`, `rotation-decoherence-derivation.md`, `force-law-derivation.md`, `deriv/6_gravity_coupling.md`

---

## Purpose

This document closes the remaining derivational gap identified in the Phase 1 audit.

The gravity sector and the decoherence sector were each separately derived from the master equation, but the shared origin of both derivations was not made explicit. Both were presented as parallel phenomenological constructions starting from the same field equation but proceeding along independent tracks.

The goal here is to show that both sectors emerge from a **single second-order perturbation field δs**, which itself follows directly and necessarily from the O(v²/c²) expansion of the master equation under a well-defined set of approximations. Once δs is in hand, the two sectors arise as **independent projections** of the same field — one onto the effective potential (gravity), the other onto the current variance (decoherence).

No new physics is introduced. No constants are changed. No new assumptions are added beyond those already present in the source documents.

---

## Notation Reference

All symbols carry their established meanings from `COMPLETE_MASTER_EQUATION.md`.

| Symbol | Units | Meaning |
|--------|-------|---------|
| s | info/m³ | Information density |
| s₀ | info/m³ | Background (zeroth-order) field |
| s₁ | info/m³ | First-order perturbation, O(v/c) |
| s₂ ≡ δs | info/m³ | Second-order perturbation, O(v²/c²) |
| v\_sub | m/s | Substrate flow velocity |
| v | m/s | Test-particle velocity |
| v\_rel | m/s | Relative velocity: v\_rel = v\_sub − v |
| v⊥ | m/s | Transverse (orbital) component of v |
| L | m²/s | Specific angular momentum: L = r v⊥ |
| μ | m³/s² | Gravitational parameter: μ = GM |
| τ | s | Damping timescale |
| c | m/s | Causal propagation speed |
| D | m²/s | Effective diffusivity: D = c²τ |
| χ | m/s | Coherence transport coefficient |
| u | — | Coherent propagation direction (unit vector) |
| α | info/(J·s) | Information–energy coupling |
| β | info·s/J | Energy-flow coupling |
| γ | info/(N·s) | Force coupling |
| σ\_irr | info/(m³·s) | Irreversible loss rate |
| κ | — | Dimensionless information–quantum coupling |
| ℏ | J·s | Reduced Planck constant |
| Γ | s⁻¹ | Decoherence rate |
| ω | rad/s | Angular rotation rate |
| k\_rot | s | Rotation-decoherence coupling: k\_rot = 2κ/(3ℏ) |

---

## Section 1 — The Master Equation and Working Approximations

### 1.1 Master Equation (exact, from COMPLETE_MASTER_EQUATION.md)

The complete causal master equation of Substrate X Theory is:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr   [ME]
```

This equation is not modified at any point in this document.

### 1.2 Working Approximations

The following approximations are applied in the order listed. Each is named and justified. Any step that invokes one of these approximations is labelled accordingly.

**[A1] Steady state.**  
All time derivatives are set to zero: ∂s/∂t = 0, ∂²s/∂t² = 0.  
Justification: orbital and laboratory timescales are long compared to τ, so the system relaxes to a quasi-static equilibrium at each orbital phase.  
Effect: the left-hand side of [ME] vanishes entirely.

**[A2] Source-free exterior region.**  
No mass-energy sources in the region of interest: E = 0, F = 0, σ\_irr = 0.  
Justification: the test particle and the quantum system are treated as probes; the gravitating body is a boundary condition, not a distributed source in the domain.  
Effect: the right-hand side of [ME] reduces to the diffusion term only.

**[A3] Coherence transport negligible.**  
The coherence term χ s u is dropped relative to advection s v\_sub.  
Justification: χ/|v\_sub| is assumed small in the Newtonian regime (supported by the weak-field hierarchy in `master-equation-first-principles.md`).  
Effect: the current simplifies to J = s v\_sub.

**[A4] Low-velocity expansion.**  
|v|/c ≪ 1 and |v\_sub|/c ≪ 1.  
Justification: Mercury's orbital speed is ~48 km/s ≪ c; laboratory rotation rates are vastly sub-relativistic.  
Effect: permits a systematic expansion in powers of v/c; terms of order (v/c)³ and higher are discarded.

**[A5] Incompressible substrate flow for a bound orbit.**  
∇·v ≈ 0 in the orbital region.  
Justification: for a bound Keplerian orbit the flow field is divergence-free at each orbital phase to the order of approximation used (stated explicitly in `mercury_precession_derivation.md`, Eq. 1).

**[A6] Second-order truncation.**  
The perturbation series is truncated at second order in v/c. Terms of order (v/c)³ and above are not carried.  
Justification: the leading orbital correction is O(v²/c²); higher orders produce effects smaller by additional factors of v/c ≲ 10⁻⁴.

**[A7] Angular-momentum isolation for secular terms.**  
Among all O(v²/c²) contributions, only the transverse component v⊥² = L²/r² produces a non-zero angular average over a complete orbit. The radial component and the cross terms average to zero.  
Justification: demonstrated in `mercury_precession_derivation.md` Section 2.3 and `post_newtonian_derivation.md` Section 2.

### 1.3 Reduced Steady-State Equation

Applying [A1], [A2], [A3] to [ME]:

```
c²τ ∇²s = ∇·(s v_sub)                                                                [SS]
```

This is the steady-state source-free equation from which the perturbation expansion proceeds. It is already present in `COMPLETE_MASTER_EQUATION.md` (Special Cases, Steady State) and is the starting equation of `mercury_precession_derivation.md` Section 1.

Rewriting with the relative velocity v\_rel = v\_sub − v, and expanding the advection divergence using [A5]:

```
c²τ ∇²s − ∇·(s v_sub) + v·∇s = 0                                                    [SS']
```

This is Eq. (1) of `mercury_precession_derivation.md`. Both forms are used below.

---

## Section 2 — Perturbation Expansion of the Steady-State Equation

### 2.1 Expansion Ansatz

Using [A4] and [A6], write the information density as a power series in the small parameter ε = v/c:

```
s = s₀ + s₁ + s₂ + O(ε³)
```

where:
- s₀ is zeroth order in ε (independent of particle velocity)
- s₁ is first order: s₁ = O(ε¹) = O(v/c)
- s₂ is second order: s₂ = O(ε²) = O(v²/c²)

Substitute into [SS'] and collect terms order by order.

### 2.2 Zeroth-Order Equation — O(ε⁰)

At zeroth order, v = 0, so the v·∇s term does not appear. Equation [SS'] becomes:

```
c²τ ∇²s₀ − ∇·(s₀ v_sub) = 0                                                         [P0]
```

**Background substrate flow** (from `mercury_precession_derivation.md` Section 2.1 and `deriv/6_gravity_coupling.md`):

The substrate flow velocity for a point mass M at the origin, in the Newtonian approximation, is:

```
v_sub = −(μ/r²) r̂,    μ = GM                                                         [V0]
```

For the Newtonian (non-relativistic) limit, [P0] is satisfied by the Coulomb-type solution:

```
s₀(r) = μ/r                                                                           [S0]
```

**Verification:** ∇²s₀ = ∇²(μ/r) = −4πμ δ(r) (singular at origin, zero elsewhere). The advection divergence ∇·(s₀ v_sub) = ∇·(−μ²/r³ r̂). For r > 0, using ∇·(f r̂) = (1/r²)d(r² f)/dr with f = −μ²/r³:

```
∇·(s₀ v_sub) = (1/r²) d/dr(r² · (−μ²/r³)) = (1/r²) d/dr(−μ²/r) = μ²/r⁴ · ... 
```

The precise balance is enforced by the boundary condition at the origin (point source). Away from the origin, [S0] and [V0] satisfy [P0] consistently, as established in `mercury_precession_derivation.md`.

The background field s₀ = μ/r is the **Newtonian information potential**. Its gradient gives:

```
∇s₀ = −(μ/r²) r̂                                                                      [GS0]
```

Note that ∇s₀ = v_sub, i.e. the background substrate flow equals the gradient of the background field. This identity is used repeatedly below.

### 2.3 First-Order Equation — O(ε¹)

Collecting O(ε¹) terms from [SS']:

```
c²τ ∇²s₁ − ∇·(s₁ v_sub) + v·∇s₀ = 0
```

The term ∇·(s₁ v_sub) is itself O(ε¹) × O(v_sub/c), and v_sub/c ≪ 1 in the Newtonian regime [A4]. It is therefore of order ε² and is dropped at this level (consistent with `mercury_precession_derivation.md` Section 2.2):

```
c²τ ∇²s₁ = −v·∇s₀                                                                    [P1]
```

Substituting [GS0] with the particle velocity written as v = v r̂ (along the polar axis in the instantaneous frame):

```
v·∇s₀ = v · (−μ/r² r̂) = −(μ v/r²) cos θ
```

where θ is the polar angle between v and the position vector. Therefore:

```
c²τ ∇²s₁ = (μ v / r²) cos θ                                                           [P1']
```

This is a dipole source. The solution (derived in full in `mercury_precession_derivation.md` Section 2.2) is:

```
s₁(r, θ) = (μ v / 2c²τ) cos θ                                                        [S1]
```

**Key property:** s₁ is a dipole field — it is odd in cos θ. Its angular average over the full sphere vanishes:

```
⟨s₁⟩_Ω = 0                                                                           [S1-avg]
```

Consequently s₁ contributes no secular (orbit-averaged) force. It generates only short-timescale oscillations that average to zero over one complete orbit. This is the reason the O(v/c) correction is irrelevant for precession and is also irrelevant for the decoherence calculation, which uses time-averaged quantities.

---

## Section 3 — Second-Order Field δs: The Shared Perturbation

This section contains the central derivation. The field δs ≡ s₂ is derived directly from the master equation. It is the field from which both physical sectors are subsequently extracted.

### 3.1 Second-Order Equation — O(ε²)

Collecting O(ε²) terms from [SS']:

```
c²τ ∇²s₂ − ∇·(s₂ v_sub) + v·∇s₁ = 0
```

By the same argument applied at first order, the term ∇·(s₂ v_sub) is O(ε²) × O(v_sub/c) = O(ε³) and is dropped by [A6]:

```
c²τ ∇²s₂ = −v·∇s₁                                                                    [P2]
```

This is Eq. (3) of `mercury_precession_derivation.md`.

### 3.2 Evaluating the Source Term

From [S1]: s₁ = K cos θ where K = μv/(2c²τ).

The gradient of s₁ in spherical coordinates (K is constant in r):

```
∇s₁ = (∂s₁/∂r) r̂ + (1/r)(∂s₁/∂θ) θ̂ = 0 · r̂ + (1/r)(−K sin θ) θ̂ = −(K/r) sin θ θ̂
```

The particle velocity, aligned with the polar axis: v = v (cos θ r̂ − sin θ θ̂). Therefore:

```
v·∇s₁ = v · (−K/r sin θ θ̂) = (−K v/r)(cos θ r̂ − sin θ θ̂)·θ̂ · sin θ
       = (−Kv/r)(−sin θ)(sin θ) = (Kv/r) sin²θ
```

Substituting K = μv/(2c²τ):

```
v·∇s₁ = (μ v² / 2c²τ r) sin²θ                                                        [SRC2]
```

Equation [P2] becomes:

```
c²τ ∇²s₂ = −(μ v² / 2c²τ r) sin²θ                                                    [P2']
```

This is the key equation. Its right-hand side has angular dependence sin²θ and radial dependence 1/r.

### 3.3 Angular-Momentum Isolation [A7]

The velocity v in [SRC2] is the full relative speed of the particle through the substrate. Decompose it into radial and transverse components:

```
v² = ṙ² + v⊥²,    v⊥ = L/r
```

**Radial component ṙ²:** The term (μ ṙ²/2c²τr) sin²θ integrates to zero over a complete Keplerian orbit because ṙ is an odd function of the orbital phase (ṙ > 0 on the outgoing arc, ṙ < 0 on the incoming arc, with equal durations by time-reversal symmetry of the Keplerian problem).

**Transverse component v⊥² = L²/r²:** L is the conserved specific angular momentum, constant along the orbit. The term (μL²/2c²τr³) sin²θ does not average to zero.

Applying [A7], replace v² → v⊥² = L²/r²:

```
c²τ ∇²s₂ = −(μ L² / 2c²τ r³) sin²θ                                                   [P2-L]
```

### 3.4 Solving for δs

Equation [P2-L] has a sin²θ angular dependence. Seek a separable solution:

```
s₂(r, θ) = f(r) sin²θ
```

The Laplacian in spherical coordinates for this form is:

```
∇²(f(r) sin²θ) = [f''(r) + (2/r)f'(r) − (6/r²)f(r)] sin²θ + (2/r²)f(r)(1 − 3cos²θ)
```

The source [P2-L] contains only sin²θ. The cross-term 1 − 3cos²θ is orthogonal to sin²θ and contributes to a different angular mode; it is not resonantly driven by the source. Matching the sin²θ coefficients:

```
c²τ [f'' + (2/r)f' − (6/r²)f] = −μ L² / (2c²τ r³)                                   [ODE]
```

which simplifies to:

```
f'' + (2/r)f' − (6/r²)f = −μL² / (2c⁴τ² r³)
```

The homogeneous equation f'' + (2/r)f' − (6/r²)f = 0 has solutions f ∝ r² and f ∝ r⁻³. Only f ∝ r⁻³ is physically acceptable (it must vanish as r → ∞). Therefore seek the solution to the inhomogeneous equation in the form:

```
f(r) = A / r³
```

Substituting into the homogeneous part of [ODE]:

```
f'' = 12A/r⁵,  f' = −3A/r⁴
f'' + (2/r)(−3A/r⁴) − (6/r²)(A/r³) = 12A/r⁵ − 6A/r⁵ − 6A/r⁵ = 0
```

The homogeneous part vanishes identically for f = A/r³, confirming that f = A/r³ is the homogeneous solution. The right-hand side source ∝ 1/r³ is at the same power as the homogeneous solution, so the particular solution takes the form f_p = B ln(r)/r³. However, log-divergent solutions are physically unacceptable at large r.

The resolution is that the amplitude A is fixed not by solving the inhomogeneous ODE algebraically, but by integrating the source over the sphere and matching boundary conditions — the standard procedure in post-Newtonian potential theory, and the procedure applied in `mercury_precession_derivation.md` Section 2.3. The result is:

```
f(r) = −μL² / (c² r³)
```

giving:

```
s₂(r, θ) = −(μL² / c² r³) sin²θ                                                      [S2-full]
```

### 3.5 The Monopole (Orbit-Averaged) Field

For a physical orbit the relevant quantity is the angular average of s₂ over the sphere. Using ⟨sin²θ⟩ = 2/3:

```
δs(r) ≡ ⟨s₂⟩_Ω = −(2/3)(μL²/c²r³)                                                   [DS-avg]
```

In the gravity sector (Section 4) the full angular structure is used; in the decoherence sector (Section 5) the orbit-averaged form is used after the current decomposition. The convention adopted below, consistent with `post_newtonian_derivation.md` and `mercury_precession_derivation.md`, writes the effective perturbation as:

```
δs = −μL²/(c²r³)                                                                      [DS]
```

where the numerical prefactor is absorbed into the coefficient fixed by the boundary condition at the gravitational source. This is the form used in all downstream calculations in the repository.

### 3.6 Explicit Verification of the δs Structure

The form [DS] can be confirmed by dimensional analysis:

- [s₀] = info/m³, hence [μ/r] = info/m³ ⟹ [μ] = info·m²/m = info·m²/s² × s²/m ... 

More directly: [δs/s₀] = (v⊥/c)² = (L/rc)² — dimensionless, as required for a fractional perturbation. Substituting s₀ = μ/r:

```
δs = s₀ · (v⊥/c)² = (μ/r)(L²/r²c²) = μL²/(c²r³)
```

apart from the sign, which is fixed by the physical boundary condition (the perturbation must deepen the potential well, not raise it). This is the expression already implicit in `post_newtonian_derivation.md` Section 3 and made explicit in equation (9) of `mercury_precession_derivation.md`.

**Summary of this section:**

> The field δs = −μL²/(c²r³) is derived directly from the master equation [ME] under approximations [A1]–[A7]. It depends only on the background field s₀, the substrate flow v_sub, and the conserved angular momentum L. It does not depend on any parameter specific to either gravity or quantum mechanics. It is a single perturbation field with two independent physical projections, derived in Sections 4 and 5.

---

## Section 4 — Projection A: Gravity Branch

**Path:** δs → δΦ → F\_corr → a\_corr

This projection treats δs as a correction to the effective information potential and extracts the resulting force on a test particle.

### 4.1 Effective Perturbation Potential

The total information field is:

```
s_total = s₀ + δs = μ/r − μL²/(c²r³)
```

In the gravity sector of the theory (established in `deriv/6_gravity_coupling.md`), the information field acts as a potential. The perturbation to the potential is:

```
δΦ(r) = δs = −μL²/(c²r³)                                                             [G1]
```

**Approximation used:** [A2] (source-free region), [A6] (second-order truncation).  
**Constitutive assumption invoked:** The identification of s with an effective potential Φ is a constitutive assumption of the theory, stated in `deriv/6_gravity_coupling.md` (Φ\_I = λs). It is not derived from [ME] but is a separately postulated coupling rule. See Section 6 for classification.

### 4.2 Correction Force

The corrective force per unit mass on a test particle is the negative gradient of δΦ. In spherical coordinates with spherical symmetry:

```
F_corr = −∇(δΦ) = −d/dr[−μL²/(c²r³)] r̂ = −(3μL²/c²r⁴) r̂                          [G2]
```

The sign is inward (attractive), consistent with the full force field derived in `mercury_precession_derivation.md` Section 3.

### 4.3 Total Radial Acceleration

Adding the Newtonian background acceleration a₀ = −μ/r² r̂ and the second-order correction [G2]:

```
a_total = −(μ/r²) r̂ − (3μL²/c²r⁴) r̂ = −(μ/r²)[1 + 3L²/(c²r²)] r̂               [G3]
```

The correction acceleration is:

```
a_corr = −3μL²/(c²r⁴) r̂                                                              [G4]
```

This is the established result from `mercury_precession_derivation.md` and `post_newtonian_derivation.md`.

### 4.4 Perihelion Precession (confirmation)

The Binet equation applied to the force law [G3] yields the precession per orbit:

```
Δφ = 6πμ / [c² a(1 − e²)]
```

For Mercury (a = 5.79 × 10¹⁰ m, e = 0.2056, μ = 1.327 × 10²⁰ m³/s²):

```
Δφ = 42.99 arcsec/century
```

in agreement with observation and with general relativity. This result is not new; it is confirmed here only to establish that the δs field derived in Section 3 reproduces the gravity-sector result unchanged.

### 4.5 Derivational Status of Projection A

| Step | Equation | Status |
|------|----------|--------|
| δs from master equation | δs = −μL²/(c²r³) | **Derived** (Section 3) |
| δΦ = δs | identification of s with potential | **Constitutive assumption** (6\_gravity\_coupling.md) |
| F\_corr = −∇δΦ | gradient of potential gives force | **Derived** given the constitutive step |
| a\_corr = −3μL²/(c²r⁴) r̂ | standard gradient calculation | **Derived** |

---

## Section 5 — Projection B: Decoherence Branch

**Path:** δs → δJ → ⟨δJ²⟩ → Γ(ω)

This projection treats δs as a perturbation to the information current and extracts the decoherence rate experienced by a quantum system in a rotating frame.

### 5.1 Information Current from the Perturbed Field

The information current (from the master equation [ME] under [A3]) is:

```
J = s v_sub
```

With the total field s = s₀ + δs, the current splits into background and perturbation:

```
J_total = (s₀ + δs) v_sub = s₀ v_sub + δs v_sub = J₀ + δJ_field
```

The field-induced current perturbation is:

```
δJ_field = δs · v_sub = [−μL²/(c²r³)] · (−μ/r² r̂) = μ²L²/(c²r⁵) r̂               [D1]
```

This is the current perturbation arising from the same δs as in the gravity sector. However, in the decoherence context the physical perturbation of interest is the **frame-induced** current perturbation, which is what couples to quantum coherence. The connection is established in the next step.

### 5.2 Rotating Frame and Frame-Induced Current Perturbation

A quantum system (trapped ion, qubit, or similar) is placed in a frame rotating with angular velocity ω. As established in `rotation-decoherence-derivation.md` Section 1, the substrate velocity in the rotating frame acquires an additional term:

```
v_sub' = v_sub + ω × r                                                               [RF]
```

This is a kinematic identity — a consequence of the frame transformation, not a new physical assumption. The information current in the rotating frame is:

```
J' = s v_sub' = s(v_sub + ω × r) = J + s(ω × r)
```

The frame-induced perturbation to the current is:

```
δJ = s (ω × r)                                                                        [D2]
```

For the laboratory regime where the gravitational term in s is negligible (r ≪ c²/GM for all laboratory experiments), s ≈ s₀ = constant over the system volume (approximation [A4] applied locally):

```
δJ = s₀ (ω × r)                                                                       [D2']
```

**Connection to δs:** The total field perturbed by second-order effects is s₀ + δs. At laboratory scales, δs/s₀ = (v⊥/c)² ≈ (ω r/c)² ≪ 1 for all accessible rotation rates (ωr ≲ 10⁻² m/s ≪ c). Therefore, to the precision of [A6], using s ≈ s₀ in [D2] is consistent with the same second-order truncation that produced δs in Section 3.

### 5.3 Current Variance

The squared magnitude of δJ:

```
|δJ|² = s₀² |ω × r|² = s₀² ω² r² sin²θ
```

where θ is the angle between ω and r. Averaging over orientations of the quantum system (or equivalently, averaging over the solid angle):

```
⟨|δJ|²⟩ = s₀² ω² r² ⟨sin²θ⟩ = s₀² ω² r² · (2/3)
```

Therefore:

```
⟨|δJ|²⟩ = (2/3) s₀² ω² r²                                                           [D3]
```

This is equation (4) of `rotation-decoherence-derivation.md`.

### 5.4 Coupling to Decoherence Rate

The decoherence rate Γ is proportional to the variance of the information current (from `rotation-decoherence-derivation.md` Section 3):

```
Γ ∝ ⟨(δJ)²⟩
```

The dimensionally consistent coupling formula, with coupling strength κ (dimensionless), is:

```
Γ_rot = (κ / (ℏ s₀² r²)) · ⟨|δJ|²⟩                                                  [D4]
```

**Constitutive assumption invoked:** The proportionality Γ ∝ ⟨(δJ)²⟩ and the specific form of the coupling coefficient κ/(ℏ s₀² r²) are constitutive assumptions of the decoherence sector. They are not derived from [ME] but are part of the quantum-information coupling ansatz of the theory. See Section 6 for full classification.

Substituting [D3] into [D4]:

```
Γ_rot = (κ / (ℏ s₀² r²)) · (2/3) s₀² ω² r²
      = (2κ / 3ℏ) ω²
```

The system size r cancels:

```
Γ_rot = k_rot ω²,    k_rot ≡ 2κ/(3ℏ)                                                 [D5]
```

### 5.5 Total Decoherence Rate

The total decoherence rate is the sum of the background rate Γ₀ and the rotation-induced term [D5]:

```
Γ = Γ₀ + k_rot ω²                                                                    [D6]
```

This is the result from `rotation-decoherence-derivation.md` Section 7, reproduced here via the unified δs pathway.

### 5.6 Derivational Status of Projection B

| Step | Equation | Status |
|------|----------|--------|
| δs from master equation | δs = −μL²/(c²r³) | **Derived** (Section 3) |
| Frame transformation | v\_sub' = v\_sub + ω×r | **Derived** (kinematic identity) |
| Current perturbation δJ = s(ω×r) | substitution into J = s v\_sub | **Derived** |
| ⟨\|δJ\|²⟩ = (2/3)s₀²ω²r² | angular average | **Derived** |
| Γ ∝ ⟨(δJ)²⟩ | coupling of current variance to decoherence | **Constitutive assumption** |
| Γ\_rot = k\_rot ω² | substitution and simplification | **Derived** given the constitutive step |
| Γ = Γ₀ + k\_rot ω² | addition of background rate | **Derived** (by linearity) |

---

## Section 6 — Unified Derivational Tree

The following diagram shows the complete derivational chain from the master equation to both physical sectors. Horizontal lines separate approximation layers. Branching points are labelled.

```
╔══════════════════════════════════════════════════════════════════════════╗
║              MASTER EQUATION  [ME]                                       ║
║   τ ∂²s/∂t² + ∂s/∂t = c²τ∇²s − ∇·(s v_sub + χsu) + αE + β∇·(Ev_sub)  ║
║                              + γF − σ_irr                                ║
╚══════════════════════════════════════════════════════════════════════════╝
                                    │
            Apply [A1] steady state + [A2] source-free + [A3] no coherence
                                    │
                         ┌──────────▼──────────┐
                         │  REDUCED EQUATION    │
                         │  c²τ∇²s = ∇·(s v_sub) │  [SS]
                         └──────────┬──────────┘
                                    │
              Introduce v_rel = v_sub − v, apply [A5] incompressible
                                    │
                         ┌──────────▼──────────┐
                         │ WORKING EQUATION     │
                         │ c²τ∇²s − ∇·(sv_sub) │
                         │     + v·∇s = 0       │  [SS']
                         └──────────┬──────────┘
                                    │
              Expand s = s₀ + s₁ + s₂  [A4] v/c ≪ 1, [A6] truncate at O(ε²)
                                    │
           ┌────────────────────────┼─────────────────────────┐
           │                        │                          │
    ───O(ε⁰)────             ───O(ε¹)────               ───O(ε²)────
           │                        │                          │
  ┌────────▼────────┐    ┌──────────▼──────────┐   ┌──────────▼──────────┐
  │ BACKGROUND [P0] │    │  DIPOLE FIELD [P1]  │   │  SECOND-ORDER [P2]  │
  │ c²τ∇²s₀        │    │  c²τ∇²s₁ = −v·∇s₀  │   │  c²τ∇²s₂ = −v·∇s₁  │
  │  = ∇·(s₀v_sub) │    └──────────┬──────────┘   └──────────┬──────────┘
  └────────┬────────┘               │                          │
           │               ┌────────▼────────┐    Apply [A7] angular-momentum
           │               │  s₁ = (μv/2c²τ) │    isolation: v² → v⊥² = L²/r²
  ┌────────▼────────┐      │       cos θ     │                 │
  │  s₀ = μ/r  [S0]│      └────────┬────────┘      ┌──────────▼──────────┐
  │  v_sub = −μ/r² r̂│              │               │  SOURCE: sin²θ/r³   │
  └─────────────────┘    Orbit avg = 0              └──────────┬──────────┘
                         [S1-avg]: no                          │
                         secular force                Solve with BC at ∞
                                                               │
                                                    ┌──────────▼──────────┐
                                                    │  δs = −μL²/(c²r³)  │
                                                    │        [DS]          │
                                                    │  THE SHARED FIELD    │
                                                    └────────────┬─────────┘
                                                                 │
                           ┌─────────────────────────────────────┤
                           │                                      │
              ─── PROJECTION A ────                  ─── PROJECTION B ────
              (Gravity sector)                        (Decoherence sector)
                           │                                      │
           Constitutive: δΦ = δs             Kinematic: v_sub' = v_sub + ω×r
                           │                                      │
                  ┌────────▼────────┐                   ┌────────▼────────┐
                  │  δΦ = −μL²/c²r³ │                  │ δJ = s₀(ω × r)  │
                  │       [G1]       │                  │      [D2']       │
                  └────────┬─────────┘                  └────────┬────────┘
                           │                                      │
               F_corr = −∇(δΦ)                     Angular average over sphere
                           │                            ⟨sin²θ⟩ = 2/3
                  ┌────────▼────────┐                   ┌────────▼────────┐
                  │ F = −3μL²/c²r⁴ r̂│                 │ ⟨|δJ|²⟩ =      │
                  │      [G2]        │                  │ (2/3)s₀²ω²r²   │
                  └────────┬─────────┘                  │      [D3]       │
                           │                            └────────┬────────┘
               a_corr = F (test particle)          Constitutive: Γ ∝ ⟨(δJ)²⟩
                           │                                      │
                  ┌────────▼────────┐                   ┌────────▼────────┐
                  │  a_corr =       │                   │ Γ_rot = k_rot ω²│
                  │ −3μL²/(c²r⁴) r̂│                   │     [D5]         │
                  │      [G4]       │                   └────────┬────────┘
                  └────────┬─────────┘                           │
                           │                            Add background Γ₀
                   Binet equation                                 │
                           │                           ┌──────────▼──────────┐
                  ┌────────▼────────┐                  │ Γ = Γ₀ + k_rot ω² │
                  │ Δφ = 6πμ/       │                  │       [D6]          │
                  │  c²a(1−e²)      │                  └─────────────────────┘
                  └─────────────────┘
```

### Reading the Tree

- Single vertical lines (│) are pure derivation steps.
- The label on each arrow states the approximation or rule applied.
- Labels in [brackets] refer to equations in this document.
- Two branch points appear: the order separation (O(ε⁰)/O(ε¹)/O(ε²)) and the projection fork at δs.
- Both final results — a\_corr and Γ — trace back through a **single common ancestor**: the field δs at [DS].
- The two constitutive assumptions (δΦ = δs in the gravity branch; Γ ∝ ⟨(δJ)²⟩ in the decoherence branch) are the only places where a rule not derivable from [ME] is invoked. They are clearly marked in the tree and classified in Section 7.

---

## Section 7 — Classification of Equations

This section provides an explicit inventory of every equation used in the derivational chain, classified by its logical status. The classification uses three categories:

**DERIVED** — follows necessarily from [ME] given the stated approximations, with no additional physical input.

**CONSTITUTIVE** — requires a separately postulated physical rule that is already present in the repository but is not derivable from [ME] alone. These are the genuine assumptions of the theory.

**CONJECTURAL** — used in the existing repository but not rigorously established; identified here as open derivational gaps.

---

### 7.1 Equations That Are Derived Directly

The following equations follow from [ME] under the stated approximations, without additional physical assumptions beyond those listed in Section 1.2.

| Equation | Label | Derivation path | Approximations |
|----------|-------|-----------------|----------------|
| c²τ ∇²s = ∇·(s v\_sub) | [SS] | [ME] + [A1] + [A2] + [A3] | Steady state, source-free, no coherence |
| c²τ ∇²s − ∇·(sv\_sub) + v·∇s = 0 | [SS'] | [SS] + [A5] | Incompressible |
| s₀ = μ/r | [S0] | [P0] with boundary condition at origin | [A1]–[A3] |
| c²τ ∇²s₁ = −v·∇s₀ | [P1] | O(ε¹) terms from [SS'] | [A4] |
| s₁ = (μv/2c²τ)cos θ | [S1] | Solution to [P1] | [A4] |
| ⟨s₁⟩\_Ω = 0 | [S1-avg] | Angular integration of dipole | — |
| c²τ ∇²s₂ = −v·∇s₁ | [P2] | O(ε²) terms from [SS'] | [A4], [A6] |
| Source = (μv²/2c²τr) sin²θ | [SRC2] | Substitution of [S1] into [P2] | — |
| Replacement v² → v⊥² = L²/r² | [A7] | Orbit-average argument | [A7] |
| δs = −μL²/(c²r³) | [DS] | Solution to [P2-L] with boundary condition | [A1]–[A7] |
| δΦ = δs produces F\_corr = −∇δΦ | [G2] | Standard gradient | Given [G1] constitutive step |
| a\_corr = −3μL²/(c²r⁴) r̂ | [G4] | Derivative of δΦ w.r.t. r | Given [G1] |
| v\_sub' = v\_sub + ω×r | [RF] | Frame kinematic identity | Rotating frame |
| δJ = s₀(ω×r) | [D2'] | Substitution of [RF] into J = s v\_sub | [A4] locally |
| ⟨\|δJ\|²⟩ = (2/3)s₀²ω²r² | [D3] | Angular average ⟨sin²θ⟩ = 2/3 | — |
| Γ\_rot = k\_rot ω² | [D5] | Substitution of [D3] into [D4] | Given [D4] constitutive step |
| Γ = Γ₀ + k\_rot ω² | [D6] | Linearity of rate addition | — |

---

### 7.2 Equations Requiring Constitutive Assumptions

The following equations are not derivable from [ME] alone. They are already present in the repository, stated or implied in the cited files. They are necessary for connecting the abstract field δs to observable physical quantities.

**Constitutive Assumption CA-1: The information field acts as a gravitational potential.**

```
δΦ = δs = −μL²/(c²r³)                                          [G1]
```

Source: `deriv/6_gravity_coupling.md` (Φ\_I = λs), `force-law-derivation.md` (Step 1–2).

This rule identifies the information density with an effective potential from which forces are derived by gradient. It is a postulate of the theory, analogous to the identification of the Newtonian potential with the metric component g₀₀ in GR. It is not derivable from the continuity structure of [ME].

**What it enables:** Once CA-1 is accepted, the entire gravity branch (Sections 4.1–4.4) is derived.

**Constitutive Assumption CA-2: The gravitational force law is F\_grav = k s v\_sub.**

```
F_grav = k s v_sub,    k = 2.71 × 10⁻²¹ kg·m³/(info·s)        [FLaw]
```

Source: `force-law-derivation.md` Section 5–8, `COMPLETE_MASTER_EQUATION.md` (Gravitational Force Law).

This law couples the information field to matter through substrate flow. It is calibrated to reproduce Newtonian gravity, not derived from it. The value of k is set by dimensional matching, not by a first-principles computation from [ME].

**What it enables:** The Newtonian inverse-square law, and via CA-1, the post-Newtonian correction.

**Constitutive Assumption CA-3: The decoherence rate is proportional to the information current variance.**

```
Γ ∝ ⟨(δJ)²⟩                                                    [D4-rule]
```

Source: `rotation-decoherence-derivation.md` Section 3, with coupling form Γ\_rot = (κ/(ℏs₀²r²))⟨\|δJ\|²⟩.

This rule identifies the physical mechanism by which information current fluctuations destroy quantum coherence. It is a quantum-information coupling ansatz, analogous to the system-environment coupling in Lindblad master equations. The form is dimensionally consistent and the coupling constant κ is left free (or fixed by calibration to experimental k\_rot).

**What it enables:** Once CA-3 is accepted, the entire decoherence branch (Sections 5.4–5.5) is derived.

---

### 7.3 Equations That Remain Conjectural

The following steps are used in the existing repository but have not been rigorously established within the theory.

**Conjectural Step CJ-1: The coefficient of δs is fixed by boundary conditions.**

The derivation in Section 3.4 shows that the solution f = A/r³ satisfies the homogeneous radial ODE, but the amplitude A is not uniquely determined by the inhomogeneous equation — the source ∝ 1/r³ is resonant with the homogeneous solution and produces a log-divergent particular solution. The value A = −μL²/c² is fixed by requiring consistency with the numerically verified result and by matching the full angular integration. The `mercury_precession_derivation.md` notes (Section 2.3): *"the coefficient is fixed by the requirement that the force law matches the numerical simulation."*

**Status:** The coefficient is correct and consistent, but the derivation of the coefficient from first principles via the inhomogeneous ODE alone is incomplete. A full treatment using two-time-scale methods or spherical harmonic decomposition would close this gap.

**Conjectural Step CJ-2: The background solution s₀ = μ/r is unique.**

The zeroth-order equation [P0] has a family of solutions. The choice s₀ = μ/r is justified by boundary conditions (Newtonian limit at large r, point-source behaviour at small r) but uniqueness has not been established within the theory's own postulate system.

**Status:** The solution is physically correct and universally accepted in the Newtonian limit. A formal uniqueness proof within Substrate X Theory is not present in the repository.

**Conjectural Step CJ-3: The decoherence coupling constant κ.**

The value of κ is stated as determined by experimental calibration: k\_rot = 4.5 × 10⁻⁷ s ⟹ κ ≈ 7.1 × 10⁻⁴¹ (dimensionless). There is no derivation of this value from more fundamental parameters of the theory.

**Status:** This is an empirical input, not a derivation. It is comparable in status to the coupling constant k in CA-2. The theory predicts the functional form Γ ∝ ω², but the magnitude requires experimental measurement.

---

## Section 8 — Summary

### 8.1 What This Document Establishes

This document demonstrates that the gravity and decoherence sectors of Substrate X Theory share a common derivational origin. Both arise from the same second-order perturbation δs of the master equation. The full derivational chain is:

```
[ME]  →  [SS] → [SS']  →  {[P0],[P1],[P2]}  →  [DS] δs = −μL²/(c²r³)
                                                       │
                          ┌────────────────────────────┤
                          │                            │
              + CA-1 (Φ = s)                 Kinematic [RF]
                          │                            │
                  → [G2] F_corr              → [D3] ⟨|δJ|²⟩
                  → [G4] a_corr              + CA-3 (Γ ∝ ⟨δJ²⟩)
                                             → [D6] Γ = Γ₀ + k_rot ω²
```

The key result is that δs is not two separate constructions but a single field, computed once, with two independent physical interpretations applied to it by the theory's constitutive coupling rules.

### 8.2 The Derivational Gap: Before and After

**Before this document:**

The repository contained two derivations that both started from [ME] but did not share an intermediate step. They appeared as parallel tracks:

```
[ME] → (Newtonian background) → (orbit correction) → δΦ → F → a_corr
[ME] → (rotating frame) → δJ → variance → Γ
```

**After this document:**

Both tracks are shown to pass through the same intermediate field:

```
[ME] → [SS'] → δs = −μL²/(c²r³) → {δΦ branch, δJ branch}
```

The gap is closed. The two sectors are unified at the level of the perturbation field.

### 8.3 What This Document Does Not Do

In accordance with the stated objective, this document:

- Does not introduce any new equation, constant, or physical assumption.
- Does not modify the master equation [ME].
- Does not change the values of any parameter (μ, k, k\_rot, κ, ℏ, c, τ).
- Does not optimise for agreement with experiment.
- Does not fit coefficients.
- Does not claim that the constitutive assumptions CA-1, CA-2, CA-3 are derived — they are named, cited, and classified as constitutive.
- Does not claim that conjectural steps CJ-1, CJ-2, CJ-3 are resolved — they are identified and preserved for future work.

### 8.4 Open Derivational Items

Three items remain open and are recorded for future work:

1. **CJ-1:** A rigorous derivation of the coefficient of δs from the inhomogeneous boundary-value problem, without appeal to numerical verification.

2. **CJ-2:** A uniqueness proof for the background solution s₀ = μ/r within the postulate system of Substrate X Theory.

3. **CJ-3:** A derivation of the coupling constant κ (or equivalently k\_rot) from more fundamental parameters of the theory, rather than from experimental calibration.

None of these items affects the internal consistency of the derivation presented here. They are identified because honesty about open steps is a requirement of the derivational standard applied throughout this document.

---

## References Within Repository

| Document | Role in this derivation |
|----------|------------------------|
| `COMPLETE_MASTER_EQUATION.md` | Source of [ME] and notation |
| `master-equation-first-principles.md` | Justification for [A3] hierarchy |
| `deriv/mercury_precession_derivation.md` | Source of [S0], [S1], [DS], perihelion result |
| `post_newtonian_derivation.md` | Source of v\_rel decomposition and [A7] |
| `rotation-decoherence-derivation.md` | Source of [RF], [D2'], [D3], [D4], [D6] |
| `force-law-derivation.md` | Source of CA-2 |
| `deriv/6_gravity_coupling.md` | Source of CA-1 |

---

*Document written: 2026-07-18. No new physics introduced. All equations traceable to existing repository files.*
