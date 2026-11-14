# Substrate Transport Derivation
## From Telegrapher Equation to Observable Decoherence

**Status:** Derivation document — no new physics introduced  
**Depends on:** `microscopic_derivation.md`, `UNIFIED_PERTURBATIVE_DERIVATION.md`, `COMPLETE_MASTER_EQUATION.md`  
**Established without re-derivation:** PRW origin, telegrapher equation, τ = 1/(2λ), c = v, D = c²τ

---

## Notation

| Symbol | Units | Meaning |
|--------|-------|---------|
| s | info/m³ | Information density |
| q or **J** | info/(m²·s) | Information flux vector |
| n⁺, n⁻ | info/m³ | Right- and left-moving PRW densities |
| v | m/s | Microscopic PRW particle speed |
| λ | s⁻¹ | Direction-reversal rate |
| τ = 1/(2λ) | s | Mean free time between reversals |
| c = v | m/s | Causal propagation speed |
| D = c²τ | m²/s | Effective diffusivity |
| **v**_sub | m/s | Substrate bulk flow velocity |
| E_sub | J/m³ | Substrate energy density |
| **P** | kg/(m²·s) | Substrate momentum density = ρ **v**_sub |
| ρ | kg/m³ | Effective substrate mass density |
| **Π** | J/m³ | Substrate stress-energy tensor (diagonal = pressure P) |
| ω_mic | rad/s | Angular frequency of spatial oscillation mode k: ω_mic = c·k |
| ω_rot | rad/s | Frame rotation rate (external, kinematic) |
| ω_sub | rad/s | Substrate vorticity: ω_sub = (1/2)|∇×**v**_sub| |
| Γ | s⁻¹ | Observable decoherence rate |
| k_rot | s | Rotation-decoherence coupling constant |
| κ | — | Dimensionless information-quantum coupling |
| ℏ | J·s | Reduced Planck constant |

---

## Part I — What Is Propagating?

### Section 1: The Microscopic State Space and Its Physical Content

**Established result (microscopic_derivation.md, Section 1.2–1.4):**

The PRW has two microscopic fields:

```
n⁺(x,t)  — density of right-moving information quanta    [info/m³]
n⁻(x,t)  — density of left-moving information quanta     [info/m³]
```

These satisfy the exact balance equations:

```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻ + S⁺(x,t)     [M1+]
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻ + S⁻(x,t)     [M1-]
```

**Assumption [PRW-1]:** The propagating quantity is information content. Each microscopic particle carries one information quantum. The density fields n⁺, n⁻ are densities of these quanta. This is a physical interpretation assigned to the mathematical objects of the PRW; it is not derivable from the PRW structure alone, but is the postulate already present in the Substrate-X theory as stated in COMPLETE_MASTER_EQUATION.md.

**Assumption [PRW-2]:** The reversal rate λ is spatially and temporally uniform in the absence of external fields. This is the definition of the homogeneous PRW. Departures from uniformity (directional bias χ, energy coupling α, etc.) are encoded in non-uniform S⁺, S⁻ or position-dependent λ.

**Physical question 1:** *What physical quantity is actually propagating?*

**Answer (derived from the PRW structure):**

The conserved quantity in the source-free, drift-free limit is the total information density:

```
s = n⁺ + n⁻                                        [DEF-s]
```

The corresponding flux is:

```
J = v(n⁺ − n⁻)                                     [DEF-J]
```

Because each quantum travels at speed ±v, the flux J is the net information current: the difference between rightward and leftward flows, scaled by the speed. The pair (s, J) is the complete macroscopic state of the field.

The microscopic quantity that propagates is therefore: **individual information quanta, each carrying one unit of information, moving at speed c = v in one of two directions, reversing direction at mean rate λ.** At the macroscopic level, the propagating fields are the density s and the flux J. Both are real, non-negative-valued (s ≥ 0; J can be signed), and have dimensions of [info/m³] and [info/(m²·s)] respectively.

---

## Part II — From Telegrapher to Substrate Master Equation

### Section 2: The Exact Coupled System and Its Conservation Structure

**Established result (microscopic_derivation.md, Section 1.4):**

The exact macroscopic equations for (s, J) are:

```
∂s/∂t + ∂J/∂x = S_total                            [C-s]
∂J/∂t + c² ∂s/∂x = −(1/τ) J + S_J                 [C-J]
```

where S_total = S⁺ + S⁻ and S_J = v(S⁺ − S⁻).

**Identity [ID-1]:** These two equations together are mathematically equivalent to the telegrapher equation for s. This equivalence is exact; it involves no approximation.

**Identity [ID-2]:** The coupled system [C-s, C-J] is a first-order symmetric hyperbolic system. It is the 1D analogue of Maxwell's equations with damping: [C-s] is the "charge continuity" equation, and [C-J] is the "flux evolution" equation with relaxation term −J/τ.

**Remark on the structure of [C-J]:** The term −(1/τ)J = −2λ J is a linear damping of the flux. It arises from the reversal: when a right-mover becomes a left-mover, it contributes −v to the flux (from +v to −v, a change of −2v per quantum, times the reversal rate λ per quantum). The damping coefficient 1/τ = 2λ is exact.

### Section 3: Conserved Quantities in the Source-Free Limit

**Assumption [A-SF]:** Source-free, drift-free limit: S_total = 0, S_J = 0, v_sub = 0.

In this limit [C-s] and [C-J] become:

```
∂s/∂t = −∂J/∂x                                     [SF-s]
∂J/∂t = −c² ∂s/∂x − (1/τ) J                       [SF-J]
```

**Derivation of conserved quantities:**

**Total information (global conservation):**

Integrate [SF-s] over all space (with periodic or vanishing boundary conditions):

```
d/dt ∫ s dx = −∫ ∂J/∂x dx = 0                      [CONS-1]
```

**Mathematical identity:** ∫ ∂J/∂x dx = 0 for periodic or vanishing boundary conditions. This is exact.

**Result [R-1]:** The total information content Q = ∫ s dx is conserved in the source-free limit.

**Energy-like quantity:**

Multiply [SF-s] by c²s and [SF-J] by J, then add:

```
∂/∂t [(1/2)c²s² + (1/2)J²] = −c²s ∂J/∂x − J(c² ∂s/∂x) − (1/τ)J²
                             = −c² ∂(sJ)/∂x − (1/τ)J²           [E-eq]
```

**Derivation step:** 

```
c²s ∂J/∂x + J c² ∂s/∂x = c² ∂(sJ)/∂x     [algebraic identity]
```

Define the substrate energy density:

```
E_sub ≡ (1/2)c²s² + (1/2)J²               [DEF-Esub]
```

**Assumption [DIM-1]:** The units of E_sub depend on the units assigned to s and J. With s in [info/m³] and J in [info/(m²·s)], E_sub has units [info²/(m⁴)] times factors of c². To convert to physical energy [J/m³] requires a coupling constant (the same α or k that appears in the full theory). The quantity E_sub is dimensionally an energy density only up to such a coupling factor. We use it as a positive-definite Lyapunov functional, not as a physical energy directly.

The evolution of E_sub is:

```
∂E_sub/∂t + ∂(c²sJ)/∂x = −(1/τ) J²                [E-transport]
```

**Result [R-2]:** 
- The energy-like quantity E_sub satisfies a transport equation [E-transport] with:
  - Flux: **F**_E = c²sJ (energy transported by the information current)  
  - Dissipation: −(1/τ)J² ≤ 0 (always non-positive — energy is irreversibly lost to flux damping)
- In the τ → ∞ (no reversal) limit, E_sub is exactly conserved.
- For finite τ, E_sub decreases monotonically in the source-free limit.

**Momentum-like quantity:**

Multiply [SF-s] by J and [SF-J] by s, add:

```
∂(sJ)/∂t = −J ∂J/∂x − c²s ∂s/∂x − (1/τ) sJ
           = −∂/∂x[(1/2)J² + (1/2)c²s²] − (1/τ)sJ
           = −∂E_sub/∂x − (1/τ)sJ                  [P-eq]
```

Define:

```
P_sub ≡ sJ                                          [DEF-Psub]
```

(momentum density of the information field — units [info²/(m⁵·s)])

```
∂P_sub/∂t + ∂E_sub/∂x = −(1/τ) P_sub              [P-transport]
```

**Result [R-3]:** The momentum density P_sub satisfies a damped transport equation. The gradient of the energy density ∂E_sub/∂x acts as the "force" on the momentum. The damping rate is 1/τ.

**Summary of conserved and transported quantities:**

| Quantity | Symbol | Equation | Source-free fate |
|----------|--------|----------|-----------------|
| Total information | Q = ∫s dx | [CONS-1] | Exactly conserved |
| Energy density | E_sub = ½c²s²+½J² | [E-transport] | Transported + dissipated at rate J²/τ |
| Momentum density | P_sub = sJ | [P-transport] | Transported + damped at rate P_sub/τ |

---

## Part III — The Energy Transport Equation

### Section 4: Full Energy Transport with Sources and Drift

**Assumption [A-drift]:** Restore substrate bulk flow **v**_sub (uniform in space, slowly varying in time — consistent with approximation [A1] of UNIFIED_PERTURBATIVE_DERIVATION.md).

In the presence of bulk drift the exact [C-J] equation becomes (from microscopic_derivation.md Section 1.6, 3D generalisation):

```
∂J_i/∂t + c² ∂s/∂x_i = −(1/τ) J_i − (v_sub)_i s/τ + (S_J)_i     [C-J-drift]
```

**Derivation of this term:** The bulk drift advects both n⁺ and n⁻ equally. In the flux equation, the advection of the entire density s at velocity v_sub contributes a term −(v_sub s)/τ to the damped flux evolution. This is exact when v_sub is spatially uniform.

The energy transport equation is derived the same way as in Section 3 but including the drift term. Multiplying [SF-s+drift] by c²s and [C-J-drift] by J:

```
∂E_sub/∂t + ∇·(c²sJ) = −(1/τ)J² − (1/τ)(v_sub · J) s + source terms
```

**Assumption [A-slow-v]:** v_sub varies slowly compared to the local oscillation timescale of the field (same slow-variation condition as [A1]). Then v_sub can be treated as a parameter at each spatial point.

The term −(1/τ)(v_sub · J)s = −(1/τ) v_sub · P_sub is the rate of work done by the substrate flow on the momentum density. It is positive when v_sub is aligned with J (drift reinforces transport), negative when anti-aligned.

**Full energy transport equation:**

```
∂E_sub/∂t + ∇·F_E = −(1/τ)J² − (1/τ)(v_sub · J)s + S_E     [ET]
```

where:
- **F**_E = c²s**J** is the energy flux
- S_E = source contribution from αE, σ_irr etc. (inherited from [ME])

**Result [R-4]:** Three distinct dissipative mechanisms appear in [ET]:
1. **Flux damping:** −(1/τ)J² — always negative, irreversible.
2. **Drift-flux coupling:** −(1/τ)(v_sub·J)s — can be positive or negative.
3. **Irreversible loss:** −σ_irr × (∂E_sub/∂s) — information destruction removes energy.

### Section 5: Spatial Fourier Mode Analysis — First Appearance of ω

**Assumption [A-homog]:** The substrate is spatially homogeneous on scales large compared to 1/k (the inverse wavenumber of the mode being analysed). This is the standard assumption for deriving a dispersion relation.

**Assumption [A-lin]:** Analyse small perturbations around the uniform background:

```
s(x,t) = s̄ + δs(x,t),    J(x,t) = 0 + δJ(x,t)
```

with |δs| ≪ s̄ and |δJ| ≪ c s̄.

Substitute into [SF-s] and [SF-J] and linearise (dropping δs·δJ terms):

```
∂(δs)/∂t = −∂(δJ)/∂x                             [L-s]
∂(δJ)/∂t = −c² ∂(δs)/∂x − (1/τ) δJ              [L-J]
```

Seek plane-wave solutions:

```
δs = ŝ exp(i k x − i ω t)
δJ = Ĵ exp(i k x − i ω t)
```

**Substitution into [L-s]:**

```
−i ω ŝ = −i k Ĵ    →    Ĵ = (ω/k) ŝ             [DISP-1]
```

**Substitution into [L-J]:**

```
−i ω Ĵ = −i c² k ŝ − (1/τ) Ĵ                     [DISP-2]
```

Substitute [DISP-1] into [DISP-2]:

```
−i ω (ω/k) ŝ = −i c² k ŝ − (1/τ)(ω/k) ŝ
```

Divide by ŝ (ŝ ≠ 0):

```
−i ω²/k = −i c² k − ω/τk
```

Multiply both sides by k:

```
−i ω² = −i c² k² − ω/τ
```

Rearrange:

```
ω² + i(1/τ)ω − c²k² = 0                           [DISP-EQ]
```

This is the **dispersion relation** of the telegrapher equation.

**Solving [DISP-EQ]:**

```
ω = (−i/2τ) ± √(c²k² − 1/(4τ²))                  [DISP-SOL]
```

This reveals two regimes:

**Propagating regime** (c k > 1/(2τ), equivalently k > k_c ≡ 1/(2cτ)):

```
ω = −i/(2τ) ± √(c²k² − 1/(4τ²))                  [PROP]
```

The imaginary part −i/(2τ) gives exponential damping with time constant 2τ. The real part gives oscillatory propagation at angular frequency:

```
ω_prop(k) = √(c²k² − 1/(4τ²))                     [DEF-omega-prop]
```

**Evanescent regime** (c k < 1/(2τ)):

```
ω = −i [1/(2τ) ± √(1/(4τ²) − c²k²)]              [EVAN]
```

Both roots are purely imaginary (purely damped, no oscillation).

**Critical wavenumber:**

```
k_c = 1/(2cτ) = λ/c = λ/v                          [DEF-kc]
```

**Result [R-5]:** The telegrapher equation supports oscillatory wave propagation only above a critical wavenumber k_c = λ/v. Below k_c, all modes are purely diffusive. This is the fundamental distinction between the telegrapher equation (hyperbolic, wave-like at short scales) and the diffusion equation (parabolic, purely diffusive at all scales).

**Identification [ID-ω-1]:** The quantity ω_prop(k) = √(c²k² − 1/(4τ²)) is the **oscillation frequency of the spatial mode with wavenumber k** in the substrate transport field. It is a derived quantity — determined entirely by k, c, and τ. It is not a free parameter.

**Important note:** ω_prop is the frequency at which the substrate information density oscillates spatially. It is **not** the same as the Ramsey oscillation frequency Ω, which is the oscillation frequency of the quantum coherence under an applied detuning. The connection between ω_prop and any observable ω requires additional physical coupling (see Part V).

---

## Part IV — Rotational Dynamics from the Transport Equation

### Section 6: Angular Momentum and Vorticity of the Substrate Field

**Objective:** Identify which angular quantities emerge naturally from the transport equations, without postulation.

#### 6.1 Vorticity of the Substrate Flow

**Assumption [A-3D]:** Work in 3D. The substrate flow field **v**_sub(**x**,t) is a vector field on physical space.

Define the substrate vorticity (a standard fluid mechanics definition):

```
ω_sub ≡ (1/2) ∇×**v**_sub                           [DEF-omega-sub]
```

This is an angular velocity field with units [rad/s]. It measures the local rotation rate of the substrate flow.

**Derivation:** Take the curl of the flux equation [C-J-drift] in 3D:

```
∂(∇×**J**)/∂t = −c²(∇×∇s) − (1/τ)(∇×**J**) − (1/τ)(∇s × **v**_sub + s ∇×**v**_sub) + ...
```

**Identity:** ∇×∇s = 0 (curl of gradient is identically zero).

```
∂(∇×**J**)/∂t = −(1/τ)(∇×**J**) − (s/τ)(∇×**v**_sub) + ...
```

Define the flux vorticity:

```
Ω_J ≡ ∇×**J**                                       [DEF-OmegaJ]
```

Then:

```
∂Ω_J/∂t = −(1/τ) Ω_J − (2s/τ) ω_sub + ...          [VORT-J]
```

**Result [R-6]:** The vorticity of the information flux Ω_J is driven by the substrate vorticity ω_sub, damped at rate 1/τ. In steady state (∂Ω_J/∂t = 0):

```
Ω_J = −2s ω_sub                                     [VORT-SS]
```

The steady-state flux vorticity is proportional to the product of the local information density and the substrate vorticity. This is a derived result — it follows from the transport equations with no additional assumption.

#### 6.2 Angular Momentum Density of the Information Field

**Assumption [A-angmom]:** Define the orbital angular momentum density of the information field in the standard way:

```
L_sub ≡ **x** × **J**                                [DEF-Lsub]
```

(units: [info·m/(m²·s)] = [info/(m·s)])

Taking the time derivative using [C-s] and [C-J-drift]:

```
∂L_sub/∂t = **x** × ∂**J**/∂t
           = **x** × [−c²∇s − (1/τ)**J** − (s/τ)**v**_sub + **S**_J]
```

Integrate over volume to get total angular momentum L_total:

```
dL_total/dt = −(1/τ) L_total − (1/τ) ∫ **x** × (s **v**_sub) dV + boundary terms + source terms
```

**Assumption [A-symm]:** For a spherically symmetric background s₀ = μ/r, the gradient ∇s₀ is purely radial. Then **x** × ∇s₀ = **x** × (−μ/r² **r̂**) = 0, so the c² term contributes no torque.

The result is:

```
dL_total/dt = −(1/τ) L_total − (1/τ) ∫ **x** × (s **v**_sub) dV    [ANGMOM-EQ]
```

**Result [R-7]:** The angular momentum of the information field decays at rate 1/τ. It is also driven by the cross product **x** × (s **v**_sub), which is the torque exerted by the substrate flow on the information density distribution.

#### 6.3 Three Angular Quantities and Their Physical Roles

Three distinct angular frequency quantities appear in the theory at this stage. They must be clearly distinguished:

**Angular quantity Ω₁: Mode oscillation frequency**

```
Ω₁(k) = ω_prop(k) = √(c²k² − 1/(4τ²))             [AQ-1]
```

Origin: dispersion relation of the telegrapher equation (Section 5).  
Physical role: frequency of oscillation of a substrate mode with wavenumber k.  
Nature: derived from (k, c, τ) — fully determined by microscopic PRW parameters.  
Dependence on external physics: none.  
Connection to decoherence: not yet established (see Part V).

**Angular quantity Ω₂: Substrate vorticity**

```
Ω₂(**x**,t) = ω_sub = (1/2) ∇×**v**_sub(**x**,t)   [AQ-2]
```

Origin: local rotation of the substrate flow field (Section 6.1).  
Physical role: drives the flux vorticity Ω_J and appears in the angular momentum equation.  
Nature: a property of the substrate flow — inherited from the background gravitational or dynamical context.  
Dependence on external physics: depends on what determines **v**_sub (e.g., orbital mechanics, laboratory rotation).  
Connection to decoherence: enters [VORT-SS] and therefore affects the flux pattern experienced by a quantum system.

**Angular quantity Ω₃: Frame rotation rate**

```
Ω₃ = ω_rot    (imposed externally)                  [AQ-3]
```

Origin: kinematic frame transformation (UNIFIED_PERTURBATIVE_DERIVATION.md, Section 5.2).  
Physical role: shifts the substrate velocity in the rotating frame by ω_rot × **r**.  
Nature: external parameter — it is the angular velocity of the laboratory frame or the quantum system's environment.  
Connection to decoherence: this is the ω that enters the established result Γ_rot = k_rot ω² (Section 5.4 of UNIFIED_PERTURBATIVE_DERIVATION.md).

**Critical observation:** Ω₁, Ω₂, and Ω₃ are three physically distinct quantities. The decoherence formula Γ = Γ₀ + k_rot ω² uses Ω₃ (frame rotation). The question is whether Ω₃ can be derived from Ω₁ or Ω₂. This is the central question of Part V.

---

## Part V — The Identification of ω and the Derivational Obstruction

### Section 7: What ω Enters the Decoherence Formula, and Why

**Established result (UNIFIED_PERTURBATIVE_DERIVATION.md, Section 5.2–5.4):**

The decoherence rate is derived from the variance of the information current perturbation in a rotating frame:

```
δ**J** = s₀ (ω_rot × **r**)                         [ESTABLISHED-DJ]
⟨|δ**J**|²⟩ = (2/3) s₀² ω_rot² r²                 [ESTABLISHED-VAR]
Γ_rot = k_rot ω_rot²                                 [ESTABLISHED-GAMMA]
```

The ω that appears in these expressions is **Ω₃ = ω_rot**, the angular velocity of the frame in which the quantum system is embedded.

**Derivation of ω_rot's role (fully microscopically):**

Starting from the information current **J** = s **v**_sub, when the frame rotates at rate ω_rot, the substrate velocity in the lab frame relative to the rotating frame acquires an extra contribution:

**Kinematic identity** (this is a mathematical fact about rotating frames, not a physical assumption):

```
**v**_sub|_rotating = **v**_sub|_lab − ω_rot × **r**
```

Therefore the current perturbation in the rotating frame is:

```
δ**J** = s (ω_rot × **r**)
```

This is exact and requires no physical assumptions beyond the definition of the current and the kinematic frame transformation.

**The coupling constant k_rot:**

From [ESTABLISHED-GAMMA]: k_rot = 2κ/(3ℏ). The parameter κ is a dimensionless coupling between the information current variance and the quantum decoherence rate. Its value sets the magnitude of Γ_rot.

**Assumption [CA-3]** (constitutive, from UNIFIED_PERTURBATIVE_DERIVATION.md Section 7.2):

```
Γ ∝ ⟨(δ**J**)²⟩
```

This is a postulate of the decoherence sector. It is not derived from [ME].

**Given [CA-3] is accepted**, the decoherence formula Γ = Γ₀ + k_rot ω_rot² is fully derived, and ω_rot is microscopically identified as the frame rotation rate.

### Section 8: Can ω_rot Be Derived from Ω₁ or Ω₂?

This section determines whether the decoherence ω has any deeper microscopic expression, or whether it must remain as an external (imposed) parameter.

#### 8.1 Ω₁ (Mode frequency) → ω_rot?

**Attempt:** Can the substrate mode oscillation frequency Ω₁(k) serve as the ω in the decoherence formula?

For this identification to be valid, a quantum system in a rotating frame would need to couple to a specific substrate mode k such that ω_rot = Ω₁(k). This would require:

1. A mechanism by which a rotating frame selects a specific wavenumber k.
2. That wavenumber would then fix ω_rot = √(c²k² − 1/(4τ²)).

**Examination of the rotating-frame current [ESTABLISHED-DJ]:**

The current δ**J** = s₀(ω_rot × **r**) is linear in **r**. In a Fourier decomposition:

```
**r** = ∫ **r̂**_k exp(i**k**·**r**) (d³k/(2π)³)
```

The mode structure of δ**J** is not a single wavenumber — it is spread across all k by the **r** factor. There is no natural k selected by the rotation.

**Conclusion:** Ω₁ cannot be identified with ω_rot without an additional physical assumption that specifies which wavenumber couples to the rotating quantum system. **No such assumption is derivable from the transport equations alone.**

#### 8.2 Ω₂ (Substrate vorticity) → ω_rot?

**Attempt:** Can the substrate vorticity ω_sub serve as the ω in the decoherence formula?

From [VORT-SS]: ω_sub = −Ω_J/(2s) in steady state. For a rotating laboratory frame, the substrate flow in the frame has:

```
**v**_sub|_rotating = **v**_sub|_lab − ω_rot × **r**
```

Therefore:

```
ω_sub|_rotating = (1/2)∇ × (**v**_sub|_lab − ω_rot × **r**)
               = ω_sub|_lab − ω_rot
```

**Identity** (vector calculus, exact):

```
(1/2)∇ × (ω_rot × **r**) = ω_rot    (for uniform ω_rot)
```

So:

```
ω_sub|_rotating = ω_sub|_lab − ω_rot                [VORT-FRAME]
```

**Observation:** If ω_sub|_lab = 0 (irrotational background substrate flow — which is the case for the Newtonian background v_sub = −μ/r² r̂, since ∇×(f(r)r̂) = 0), then:

```
ω_sub|_rotating = −ω_rot
```

**Result [R-8]:** In the case of an irrotational background substrate flow, the substrate vorticity in the rotating frame equals −ω_rot (equal magnitude, opposite sign). This means Ω₂ and Ω₃ are equal in magnitude when the background is irrotational.

**Can this be used to replace ω_rot with ω_sub?** Formally yes — in the specific case of an irrotational background:

```
ω_rot = −ω_sub|_rotating    (for irrotational background)    [ID-omega-vorticity]
```

This is a derivable identity, not an independent assumption. It holds whenever:
- The background substrate flow is irrotational (∇×**v**_sub|_lab = 0)
- The frame rotation rate ω_rot is uniform

**However**, this identification does not eliminate ω_rot from the theory — it merely re-expresses it in terms of the substrate vorticity measured in the rotating frame. The physical content is identical: ω is the rotation rate.

#### 8.3 Summary: Which ω Survives to the Macroscopic Theory?

Of the three angular quantities:

| Quantity | Symbol | Survives to Γ formula? | How? |
|----------|--------|------------------------|------|
| Mode frequency | Ω₁(k) | **No** — absent from the decoherence formula | No mode-selection mechanism |
| Substrate vorticity | Ω₂ | **Yes, but equivalent to ω_rot** | By [ID-omega-vorticity] when background is irrotational |
| Frame rotation | Ω₃ = ω_rot | **Yes — this is the ω in Γ** | By kinematic frame transformation |

**The unique surviving ω is the frame rotation rate ω_rot.** This is not an assumption but a derived consequence of the frame transformation and the irrotational background.

---

### Section 9: The Derivational Obstruction — Precise Statement

**Question posed by the task:** Can ω be microscopically defined from the transport equations alone, without reference to an external frame?

**Answer (precise):**

The decoherence formula Γ = Γ₀ + k_rot ω² uses ω = ω_rot, which is the angular velocity of the frame relative to the inertial background substrate. This quantity has the following microscopic status:

**Step 1 (derived):** The information current in a rotating frame is δ**J** = s₀(ω_rot × **r**). This follows from the definition **J** = s **v**_sub and the kinematic frame transformation. It is derived.

**Step 2 (derived):** The current variance ⟨|δ**J**|²⟩ = (2/3)s₀²ω_rot²r² follows from Step 1 by angular averaging. It is derived.

**Step 3 (constitutive assumption [CA-3]):** Γ ∝ ⟨(δ**J**)²⟩. This is NOT derived from [ME]. It is a postulate connecting information-current variance to quantum decoherence.

**Step 4 (coupling constant):** k_rot = 2κ/(3ℏ). The value of κ is NOT derived from the transport equations. It is an empirical parameter.

**Obstruction [OB-1]: The constitutive coupling [CA-3]**

The transport equations describe how information density and flux evolve. They do not, by themselves, specify how information-current fluctuations decohere a quantum state. The connection from classical field fluctuations to quantum decoherence requires a coupling postulate. Without [CA-3], the derivation cannot proceed from [ET] to Γ.

**This is a genuine physical gap.** It is not a mathematical gap (the algebra is clear on both sides of [CA-3]). It is the gap between a classical transport theory and a quantum measurement theory. Filling it requires one of:

(a) A derivation of [CA-3] from a quantum master equation (Lindblad form) that itself follows from [ME], or  
(b) An additional postulate identifying the quantum system–substrate coupling Hamiltonian, from which [CA-3] follows by standard open-system quantum mechanics.

Neither (a) nor (b) is present in the existing repository.

**Obstruction [OB-2]: The coupling constant κ**

Even if [CA-3] is accepted, the magnitude k_rot = 2κ/(3ℏ) requires κ to be specified. The transport equations determine the functional form Γ ∝ ω² but not the coefficient. κ cannot be derived from (v, λ, c, τ) alone — it requires additional input about how the information field couples to quantum degrees of freedom.

**What CAN be derived from the transport equations alone:**

1. ω_rot = −ω_sub|_rotating for irrotational backgrounds [ID-omega-vorticity] ✓
2. The functional form of the current variance: ⟨|δ**J**|²⟩ ∝ ω_rot² ✓
3. The dispersion relation Ω₁(k) = √(c²k² − 1/(4τ²)) ✓
4. The conservation laws [CONS-1], [R-2], [R-3] ✓
5. The identification of ω_rot as the relevant ω (via frame kinematics) ✓

**What CANNOT be derived from the transport equations alone:**

1. The coupling [CA-3]: Γ ∝ ⟨(δJ)²⟩ ✗
2. The coefficient κ in k_rot = 2κ/(3ℏ) ✗
3. The saturation term (ω/ω_max)² in the full model Γ = Γ₀ + k_rot ω²/(1+(ω/ω_max)²) ✗

**On the saturation term specifically:**

The full decoherence model in COMPLETE_MASTER_EQUATION.md contains:

```
Γ = Γ₀ + k_rot ω²/(1 + (ω/ω_max)²)
```

The saturation factor 1/(1+(ω/ω_max)²) is a Lorentzian cutoff. From the transport theory, the dispersion relation [DISP-SOL] shows that modes with k > k_c are propagating and modes with k < k_c are evanescent. If ω is identified with Ω₁(k) for some characteristic wavenumber k_char, then:

```
ω = Ω₁(k_char) = √(c²k_char² − 1/(4τ²))
```

and an inverse relation:

```
k_char = √(ω² + 1/(4τ²)) / c
```

The energy density at wavenumber k goes as |ŝ(k)|² which, for a thermal or equilibrium distribution, has a spectral cutoff set by the reversal dynamics. A Lorentzian spectral density:

```
S(k) ∝ 1/(k² + k_c²)
```

appears naturally in diffusion-like processes (it is the Green's function of the Helmholtz equation). When converted to frequency via ω = ck, this gives a spectral density:

```
S(ω) ∝ 1/(ω² + (ck_c)²) = 1/(ω² + 1/(4τ²))
```

This is **not** the same Lorentzian as 1/(1+(ω/ω_max)²). The transport theory produces a spectral cutoff at frequency c·k_c = 1/(2τ), whereas the decoherence model has a cutoff at ω_max = 10⁶ rad/s.

**The identification ω_max ↔ c·k_c = 1/(2τ) = λ** would require:

```
λ = ω_max = 10⁶ rad/s    →    τ = 1/(2×10⁶) = 5×10⁻⁷ s
```

This is a specific numerical value that must be verified or falsified by independent measurement. It is not derivable from the decoherence formula alone.

**Result [R-9] (Obstruction summary):**

The derivation from the telegrapher equation to observable decoherence can proceed through the transport equations to the point:

```
Γ_rot ∝ ω_rot²        [reached by pure derivation from [ME] + kinematics]
```

The chain **stops here** without the constitutive coupling [CA-3]. Once [CA-3] is postulated, the functional form Γ = Γ₀ + k_rot ω_rot² is derived. The coefficient k_rot and the saturation ω_max remain as unresolved quantities requiring either additional microscopic input or experimental calibration.

---

## Part VI — Full Derivational Chain Summary

### Section 10: The Chain as a Sequence of Logical Steps

Each step is labelled as: **D** (derived — follows from previous step), **A** (assumption — new physical input), **I** (mathematical identity — no physical content).

```
[A-PRW-1]  Information quanta carried by PRW particles (physical interpretation)
      ↓
[D]   n⁺, n⁻ exact balance equations [M1+, M1-]
      ↓  (I: add and subtract)
[D]   Exact coupled system (s, J): [C-s, C-J]
      ↓  (I: differentiate, substitute)
[D]   Telegrapher equation: τ s_tt + s_t = c²τ s_xx  [established]
      ↓  (I: dimensional comparison)
[D]   Parameter dictionary: τ = 1/(2λ), c = v, D = c²τ  [established]
      ↓
[D]   Conservation of total information Q = ∫s dx  [CONS-1]
      ↓
[D]   Energy transport equation [ET]:
          ∂E_sub/∂t + ∇·(c²sJ) = −J²/τ − (v_sub·J)s/τ + S_E
      ↓
[D]   Momentum transport equation [P-transport]:
          ∂P_sub/∂t + ∇·E_sub = −P_sub/τ
      ↓  (A: linearise around background, seek plane waves)
[D]   Dispersion relation: ω² + i(1/τ)ω − c²k² = 0  [DISP-EQ]
      ↓  (I: solve quadratic)
[D]   Mode frequency: Ω₁(k) = √(c²k² − 1/(4τ²))  [AQ-1]
      ↓
[D]   Three angular quantities identified: Ω₁, Ω₂ = ω_sub, Ω₃ = ω_rot  [Section 6.3]
      ↓
[D]   Vorticity equation: ∂Ω_J/∂t = −(1/τ)Ω_J − (2s/τ)ω_sub  [VORT-J]
      ↓  (A-symm: irrotational background)
[D]   Identity: ω_rot = −ω_sub|_rotating  [ID-omega-vorticity]
      ↓  (I: kinematic frame transformation)
[D]   Current perturbation: δJ = s₀(ω_rot × r)  [ESTABLISHED-DJ]
      ↓  (I: angular average)
[D]   Current variance: ⟨|δJ|²⟩ = (2/3)s₀²ω_rot²r²  [ESTABLISHED-VAR]
      ↓
      ╔═══════════════════════════════════════════════════╗
      ║  OBSTRUCTION [OB-1]: Constitutive coupling needed ║
      ║  [CA-3]: Γ ∝ ⟨(δJ)²⟩  (not derivable from [ME]) ║
      ╚═══════════════════════════════════════════════════╝
      ↓  (given [CA-3])
[D]   Γ_rot = k_rot ω_rot²  [ESTABLISHED-GAMMA]
      ↓
      ╔═══════════════════════════════════════════════════╗
      ║  OBSTRUCTION [OB-2]: Coupling magnitude needed    ║
      ║  k_rot = 2κ/(3ℏ)  — κ not determined by [ME]    ║
      ╚═══════════════════════════════════════════════════╝
      ↓  (given κ from calibration)
[D]   Γ = Γ₀ + k_rot ω_rot²  [D6]
```

### Section 11: The Microscopic Definition of ω — Final Answer

**ω in the decoherence formula is ω_rot, the angular velocity of the quantum system's frame relative to the inertial substrate.**

Its microscopic meaning, tracing back through the full chain:

1. **ω_rot enters via the kinematic frame transformation** — it is the rate at which the substrate velocity field is shifted by frame rotation.

2. **ω_rot = −ω_sub|_rotating for irrotational backgrounds** — it equals the substrate vorticity measured in the rotating frame, with opposite sign. This is an exact derived identity.

3. **ω_rot is not the mode oscillation frequency Ω₁(k)** — the mode frequency is a property of the substrate field spectrum; the frame rotation rate is a property of the laboratory setup. They are independent unless a specific mode-coupling mechanism is specified (which would be an additional assumption).

4. **ω_rot is not a free parameter of the substrate field** — it is imposed externally by the experimental setup (the rotation rate of the trap, interferometer, or test body). The substrate transport theory predicts how a given ω_rot produces decoherence, but does not predict what ω_rot is.

5. **The connection ω_rot = Ω₁(k) for some k** — this would require a resonance condition between the laboratory rotation and a specific substrate mode. Such a condition might arise in specific physical scenarios (e.g., parametric resonance), but it is not a general consequence of the transport theory.

**The derivation is complete up to the two obstructions [OB-1] and [OB-2].** Both obstruction points are precisely identified, physically motivated, and cannot be crossed without additional input that is not present in the current repository.
