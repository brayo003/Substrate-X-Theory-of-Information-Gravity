# Mapping Derivation: Substrate X Theory → Superconducting Qubit Observable

**Status:** Theory laboratory — isolated from validated inference pipeline  
**Frozen references:** `COMPLETE_MASTER_EQUATION.md`, `UNIFIED_PERTURBATIVE_DERIVATION.md`  
**Date:** 2026-07-19  
**Rule:** No equation in the frozen documents may be modified. No new constants. No fitting parameters.

---

## Primary Question

The perturbative derivation produces:

```
δJ = s₀ (ω × r)                                    [D2']
```

and ultimately:

```
Γ = Γ₀ + k_rot ω² / (1 + (ω/ω_max)²)              [DCH]
```

where k_rot = 4.5×10⁻⁷ s, ω_max ≈ 10⁶ rad/s.

**Can ω be rigorously identified with a controllable quantity in superconducting-qubit physics via an exact change of variables — with no approximation, no new postulate, no redefinition of ω?**

---

## Mathematical Starting Point (Frozen)

From `UNIFIED_PERTURBATIVE_DERIVATION.md` Section 5.2, the frame-induced current perturbation is:

```
δJ = s₀ (ω × r)                                    [D2']
```

derived from the kinematic identity:

```
v_sub' = v_sub + ω × r                             [RF]
```

where ω is the **physical angular velocity of the laboratory frame** — the rate at which the coordinate axes rotate relative to an inertial frame.

From `COMPLETE_MASTER_EQUATION.md`, the full decoherence prediction including saturation is:

```
Γ = Γ₀ + k_rot ω² / (1 + (ω/ω_max)²)              [DCH]
```

These two equations are the inputs. ω is the same quantity in both.

---

## Acceptance and Rejection Criteria

**Accept** a candidate mapping if and only if there exists an unbroken algebraic chain:

```
Master Equation
    ↓
Perturbative Expansion
    ↓
δJ = s₀(ω × r)
    ↓
Hamiltonian Transformation (exact change of variables)
    ↓
Superconducting Observable
    ↓
Experimental Control Variable
```

with every step explicit and every approximation named and justified.

**Reject immediately** if any step requires:
- Introducing new postulates
- Redefining ω
- Changing the master equation
- Adding phenomenological couplings
- Assuming equivalence without proof
- Appealing to analogy instead of derivation

---

## Candidate A — Rotating-Frame Transformation

### A.1 Setup

A superconducting transmon qubit has the bare Hamiltonian (in the two-level approximation):

```
H₀ = (ℏω_q / 2) σ_z                               [A-H0]
```

where ω_q is the qubit transition frequency (typically 4–8 GHz). Apply a microwave drive at frequency Ω_d:

```
H_drive(t) = ℏ Ω_R cos(Ω_d t) σ_x                 [A-Hd]
```

where Ω_R is the Rabi frequency (drive amplitude). The total lab-frame Hamiltonian is:

```
H_lab(t) = (ℏω_q/2) σ_z + ℏ Ω_R cos(Ω_d t) σ_x   [A-Hlab]
```

### A.2 Rotating-Frame Transformation (Exact)

Define the unitary:

```
U(t) = exp(i Ω_d t σ_z / 2)                        [A-U]
```

The rotating-frame Hamiltonian is:

```
H_rot = U H_lab U† − iℏ U (∂U†/∂t)                [A-trans]
```

Computing each term:

**Term 1:** U H₀ U†

```
U σ_z U† = σ_z   (σ_z commutes with exp(i θ σ_z))

U (ℏω_q/2) σ_z U† = (ℏω_q/2) σ_z
```

**Term 2:** U H_drive U†

Using the identity:
```
U σ_x U† = cos(Ω_d t) σ_x + sin(Ω_d t) σ_y
```

Therefore:
```
U H_drive U† = ℏ Ω_R cos(Ω_d t)[cos(Ω_d t) σ_x + sin(Ω_d t) σ_y]
             = ℏ Ω_R [cos²(Ω_d t) σ_x + cos(Ω_d t)sin(Ω_d t) σ_y]
             = ℏ Ω_R [(1 + cos2Ω_d t)/2 · σ_x + (sin2Ω_d t)/2 · σ_y]
```

**Term 3:** −iℏ U (∂U†/∂t)

```
U† = exp(−i Ω_d t σ_z / 2)
∂U†/∂t = (−i Ω_d σ_z / 2) exp(−i Ω_d t σ_z / 2)
U ∂U†/∂t = (−i Ω_d σ_z / 2)
−iℏ U ∂U†/∂t = −ℏ Ω_d σ_z / 2
```

**Rotating-wave approximation (RWA):** Drop terms oscillating at 2Ω_d t (these average to zero on timescales ≫ 1/Ω_d). This is an approximation — named here as [RWA-A].

After [RWA-A]:

```
H_rot = (ℏ(ω_q − Ω_d)/2) σ_z + (ℏ Ω_R / 2) σ_x   [A-Hrot]
```

Define the detuning: Δ = ω_q − Ω_d. Then:

```
H_rot = (ℏΔ/2) σ_z + (ℏ Ω_R / 2) σ_x              [A-Hrot2]
```

### A.3 Identifying ω

In the rotating frame, the state vector precesses about an effective axis at angular frequency:

```
ω_eff = √(Δ² + Ω_R²)                               [A-weff]
```

**Attempt:** Identify ω_eff with the ω appearing in δJ = s₀(ω × r).

**Algebraic check:** In the substrate derivation, ω is the angular velocity of the physical coordinate frame. In [A-U], Ω_d is the angular velocity of the mathematical transformation applied to the Hilbert space. These live in different spaces:

- Substrate ω: rotation of physical 3D space, units rad/s, acts on position vector r ∈ ℝ³
- Rotating-frame Ω_d: rotation in the 2D Bloch sphere / SU(2), acts on quantum state |ψ⟩ ∈ ℂ²

**The identification requires:** ω × r ↔ Ω_d × ⟨r_qubit⟩. This would need:
1. A mapping from the SU(2) rotation to a physical spatial rotation.
2. An identification of the qubit's effective "position" r with a physical coordinate.

Neither follows from the frozen equations. The substrate derivation uses ω as a rigid-body angular velocity of the laboratory frame. The rotating-frame transformation uses Ω_d as a mathematical device to remove the time dependence of H_lab. These are structurally different operations.

**Furthermore:** The identification δJ = s₀(ω × r) requires ω to multiply the physical position vector r. In [A-Hrot], Ω_d appears only as a frequency shift in σ_z; it does not multiply any position observable.

### A.4 Verdict

**REJECTED.**

The rotating-frame transformation is exact as an algebraic manipulation of the Hamiltonian. However, the Ω_d appearing in the rotating frame is not the same mathematical object as the ω in δJ = s₀(ω × r). The chain breaks at the step:

```
δJ = s₀(ω × r)  →  H_rot contains Ω_d
```

because ω × r is a 3-vector field defined on physical space, while Ω_d is a scalar parameter of a unitary transformation on Hilbert space. No change of variables within the frozen equations can equate them without redefining ω — which is prohibited.

---

## Candidate B — Interaction-Picture Angular Velocity

### B.1 Setup

The interaction picture (Dirac picture) for the qubit Hamiltonian H = H₀ + V(t):

```
H₀ = (ℏω_q / 2) σ_z                               [B-H0]
V(t) = ℏ Ω_R cos(Ω_d t) σ_x                        [B-V]
```

The interaction-picture state is:

```
|ψ_I(t)⟩ = U₀†(t) |ψ_S(t)⟩,   U₀(t) = exp(−iH₀t/ℏ)   [B-IP]
```

The interaction-picture Hamiltonian is:

```
V_I(t) = U₀†(t) V(t) U₀(t)                         [B-VI]
```

### B.2 Explicit Computation

```
U₀†(t) = exp(+iω_q t σ_z / 2)
U₀†(t) σ_x U₀(t) = cos(ω_q t) σ_x + sin(ω_q t) σ_y
```

Therefore:

```
V_I(t) = ℏ Ω_R cos(Ω_d t)[cos(ω_q t) σ_x + sin(ω_q t) σ_y]
```

Expanding with product-to-sum:

```
V_I(t) = (ℏ Ω_R / 2){cos((ω_q − Ω_d)t) σ_x + sin((ω_q − Ω_d)t) σ_y
                     + cos((ω_q + Ω_d)t) σ_x + sin((ω_q + Ω_d)t) σ_y}
```

### B.3 Attempting the Identification

The "interaction-picture angular velocity" candidate proposes that the precession rate of V_I(t) — namely (ω_q − Ω_d) — plays the role of ω.

**Explicit identification attempt:**

The phase factor in V_I rotates the operator at rate Δ = ω_q − Ω_d in the (σ_x, σ_y) plane of operator space. This rotation is:

```
R_I(t) : (σ_x, σ_y) → (cos(Δt) σ_x + sin(Δt) σ_y, ...)
```

This is a rotation in operator space with angular velocity Δ. Compare with [RF]:

```
v_sub' = v_sub + ω × r
```

The substrate frame transformation acts on the velocity field in physical 3D space. The interaction-picture transformation acts on operators in a 2D subspace of the Lie algebra su(2).

These are isomorphic as abstract rotation groups — SO(3) ≅ SU(2)/ℤ₂ — but isomorphism of abstract groups does not constitute an exact identification of physical quantities. For the mapping to be exact, the rotation in operator space would need to be shown to be the same physical object as the rotation of the laboratory frame.

**What would be needed:** A derivation showing that rotating the Hilbert-space frame at rate Δ is physically equivalent to rotating the laboratory at rate ω, in the sense that both produce δJ = s₀(ω × r) with the same ω. This would require a coupling between the qubit's quantum state and the substrate current J, which is precisely what CA-3 (constitutive assumption 3) in UNIFIED_PERTURBATIVE_DERIVATION.md provides — but CA-3 is a postulate, not a derivation. Invoking it here would be circular: using a constitutive assumption to establish the mapping that the mapping derivation is trying to derive.

### B.4 Verdict

**REJECTED.**

The interaction-picture precession rate Δ = ω_q − Ω_d is a rotation in operator space, not in physical space. The chain breaks at:

```
δJ = s₀(ω × r)  →  V_I rotates at Δ in Hilbert space
```

The group-theoretic similarity (both are SO(3) rotations in their respective spaces) does not constitute an exact identification. Establishing the identification requires either invoking CA-3 (circular) or introducing a new coupling postulate (prohibited).

---

## Candidate C — Floquet Effective Hamiltonian

### C.1 Setup

For a periodically driven qubit H(t) = H(t + T), Floquet theory guarantees the existence of an effective (time-independent) Hamiltonian H_F such that the stroboscopic evolution satisfies:

```
U(T, 0) = exp(−i H_F T / ℏ)                        [C-Floquet]
```

where U(T,0) is the one-period propagator. H_F is the Floquet effective Hamiltonian.

For the driven qubit [A-Hlab], the one-period propagator at resonance (Δ = 0) is:

```
U(T, 0) = exp(−i Ω_R T σ_x / 2)                    [C-UT]
```

giving:

```
H_F = (ℏ Ω_R / 2) σ_x                              [C-HF]
```

The Floquet quasi-energies are ±ℏΩ_R/2, and the system precesses about the x-axis of the Bloch sphere at angular frequency Ω_R.

### C.2 Attempting the Identification

**Proposal:** ω = Ω_R (Floquet drive rate = substrate angular velocity).

**Algebraic chain check:**

Step 1: From master equation to δs. ✓ (Section 3 of UNIFIED_PERTURBATIVE_DERIVATION.md — exact)

Step 2: From δs to δJ = s₀(ω × r). ✓ (kinematic identity [RF] — exact)

Step 3: From δJ to Γ = Γ₀ + k_rot ω². ✓ (with constitutive assumption CA-3)

Step 4: Claim Ω_R = ω.

**What this identification requires:**

The Floquet Hamiltonian H_F = (ℏΩ_R/2)σ_x generates precession of the Bloch vector at rate Ω_R. The decoherence in the substrate theory is caused by the frame rotation ω generating the current perturbation δJ = s₀(ω × r). For ω = Ω_R to be an exact identification, the physical mechanism must be the same:

"Rotating the qubit drive frame at rate Ω_R must be physically equivalent to rotating the laboratory frame at angular velocity ω = Ω_R."

**Structural check:** In Floquet theory, Ω_R is the amplitude of the oscillating drive — it parameterises the strength of H_drive(t), not the angular velocity of any physical rotation. In the substrate theory, ω is the angular velocity of the rigid laboratory frame, a physical spatial rotation. The Floquet quasi-energy Ω_R has units of rad/s, and so does ω — but matching units is not sufficient for identification.

**The decisive test:** If ω = Ω_R were exact, then the decoherence formula [DCH] would read:

```
Γ = Γ₀ + k_rot Ω_R² / (1 + (Ω_R/ω_max)²)
```

This is a testable prediction: decoherence should increase as Ω_R² at low drive strength and saturate at Ω_R ≈ ω_max. This functional form is experimentally distinguishable.

**However**, the identification step "ω = Ω_R" is not derived from the frozen equations — it is asserted. To derive it, one would need to show that the Floquet drive acts on the substrate current J in the same way as a physical frame rotation, i.e.:

```
J_Floquet = s₀ (Ω_R × r)
```

This would require showing that the time-periodic Hamiltonian H(t) generates a substrate current perturbation of this exact form — which in turn requires a coupling between the qubit Hamiltonian and the substrate field J. That coupling is CA-3, which is a constitutive postulate, not a derivable consequence of [ME].

### C.3 Verdict

**REJECTED** as an exact derivation. **Conditionally useful** as a physical hypothesis.

The Floquet mapping ω ↔ Ω_R is not derivable from the frozen equations without invoking CA-3. The identification is a postulate, not a consequence. However, it generates a sharp, falsifiable prediction:

```
Γ(Ω_R) = Γ₀ + k_rot Ω_R² / (1 + (Ω_R/ω_max)²)
```

This is the best available candidate for an experimental test.

---

## Candidate D — Magnus Expansion

### D.1 Setup

The Magnus expansion expresses the time-evolution operator as:

```
U(t) = exp(Ω_M(t))
```

where Ω_M(t) is given by the Magnus series:

```
Ω_M(t) = Ω₁(t) + Ω₂(t) + Ω₃(t) + ...
```

with:
```
Ω₁(t) = −(i/ℏ) ∫₀ᵗ H(t₁) dt₁

Ω₂(t) = (−i/ℏ)² (1/2) ∫₀ᵗ dt₁ ∫₀ᵗ¹ dt₂ [H(t₁), H(t₂)]
```

For the driven qubit [A-Hlab] with H(t) = (ℏω_q/2)σ_z + ℏΩ_R cos(Ω_d t) σ_x:

### D.2 First Magnus Term

```
Ω₁(T) = −(i/ℏ) ∫₀ᵀ [(ℏω_q/2)σ_z + ℏΩ_R cos(Ω_d t) σ_x] dt
       = −i(ω_q T/2) σ_z − i Ω_R [sin(Ω_d T)/Ω_d] σ_x
```

At resonance Ω_d = ω_q, and for one full drive period T = 2π/Ω_d:

```
sin(Ω_d T)/Ω_d = sin(2π)/Ω_d = 0
```

So at stroboscopic times:

```
Ω₁(nT) = −i(ω_q · nT/2) σ_z                        [D-O1]
```

### D.3 Second Magnus Term

The commutator:

```
[H(t₁), H(t₂)] = [(ℏω_q/2)σ_z + ℏΩ_R cos(Ω_d t₁)σ_x,
                   (ℏω_q/2)σ_z + ℏΩ_R cos(Ω_d t₂)σ_x]
```

Since [σ_z, σ_z] = 0 and [σ_x, σ_x] = 0:

```
[H(t₁), H(t₂)] = (ℏ²ω_q Ω_R/2)[cos(Ω_d t₁) − cos(Ω_d t₂)] [σ_z, σ_x]
               = (ℏ²ω_q Ω_R/2)[cos(Ω_d t₁) − cos(Ω_d t₂)] · 2iσ_y
```

This is non-zero and produces a σ_y term in Ω₂. The full expression is cumbersome but integrable. The key point is:

```
Ω₂(T) ∝ (ω_q Ω_R / Ω_d²) σ_y                       [D-O2]
```

The Magnus effective Hamiltonian to second order is:

```
H_Magnus ≈ H_F + O(Ω_R²/ω_q)                        [D-HM]
```

which reproduces the Floquet result at leading order with corrections of order Ω_R/ω_q ≪ 1.

### D.4 Attempting the Identification

The Magnus expansion produces a time-independent effective Hamiltonian whose terms are proportional to ω_q, Ω_R, and their ratios. None of these terms take the form of an angular velocity acting on a position vector.

**Structural observation:** The Magnus expansion is a method for computing the effective Hamiltonian of a driven quantum system. It does not produce any term of the form ω × r for any ω and r — because the qubit Hilbert space ℂ² has no position observable. The Pauli matrices σ_x, σ_y, σ_z are spin operators, not position operators.

For ω × r to appear, one would need:
1. A position observable r̂ in the qubit system.
2. An angular velocity operator ω̂ that generates rotations of r̂.

A two-level qubit has no position observable in the sense of x, y, z ∈ ℝ³. The Bloch vector ⟨σ⟩ transforms like an angular momentum under SU(2), not like a position vector under SO(3). These are locally isomorphic but not identical.

### D.5 Verdict

**REJECTED.**

The Magnus expansion produces corrections to the Floquet Hamiltonian, all expressed in terms of Pauli operators. No term ω × r appears because the qubit has no position observable. The chain breaks at the same point as Candidate B.

---

## Candidate E — Synthetic Gauge Field

### E.1 Setup

In a driven qubit, a spatially varying drive phase φ(r) can induce an effective vector potential:

```
A_eff = (ℏ/q_eff) ∇φ(r)                            [E-A]
```

This is the synthetic gauge field. The effective magnetic field is:

```
B_eff = ∇ × A_eff                                   [E-B]
```

### E.2 Attempting the Identification

For a transmon qubit, φ(r) is the microwave drive phase at position r. If φ(r) = φ₀ + k·r (plane wave), then ∇φ = k (constant), giving B_eff = 0 — no synthetic magnetic field.

A spatially varying phase requires a structured field, e.g. a twisted wavefront. In that case B_eff ≠ 0 and acts like a magnetic field on the qubit's internal degree of freedom.

**Structural problem:** The substrate current perturbation δJ = s₀(ω × r) is linear in r and has the form of a rigid-body rotation field. A synthetic gauge field B_eff would need to reproduce this exact spatial dependence. For B_eff = const, the vector potential A_eff = (1/2) B_eff × r does produce a term linear in r — exactly the form ω × r if we identify B_eff = 2ω_eff.

**However:** This identification requires:

1. The synthetic gauge field to be physically present (i.e., a spatially structured drive).
2. The qubit to have a spatial degree of freedom r over which B_eff × r is meaningful.

A point-like transmon qubit has no spatial degree of freedom r in the sense required. The "position" in A_eff · r refers to the center-of-mass coordinate of a charged particle, not the internal spin of a two-level system.

The synthetic gauge field construction applies exactly to cold atoms or mechanical resonators with spatial wavefunctions. For a superconducting qubit in the two-level approximation, it does not apply without extending the model.

### E.3 Verdict

**REJECTED** for point-like two-level superconducting qubits. The synthetic gauge field construction requires a spatial degree of freedom that a two-level qubit does not possess.

---

## Candidate F — Dressed-State Angular Momentum

### F.1 Setup

In the strong-drive regime, the qubit-drive system forms dressed states. The dressed-state basis diagonalises H_rot [A-Hrot2]:

```
|+⟩ = cos(θ/2)|↑⟩ + sin(θ/2)|↓⟩
|−⟩ = −sin(θ/2)|↑⟩ + cos(θ/2)|↓⟩
```

where tan θ = Ω_R / Δ. The dressed-state splitting is:

```
ω_dressed = √(Δ² + Ω_R²) = ω_eff                   [F-wd]
```

### F.2 Attempting the Identification

**Proposal:** The dressed states carry "angular momentum" ω_dressed that maps to ω.

The dressed-state splitting ω_dressed is the frequency of Rabi oscillations between |+⟩ and |−⟩. It is the precession rate of the Bloch vector around the effective field axis in H_rot.

**Structural check:** This is identical to the precession frequency ω_eff in Candidate A. It is a frequency in Bloch-sphere space (SU(2)), not an angular velocity in physical 3D space (SO(3)).

The dressed-state "angular momentum" is a metaphor from atomic physics (the Jaynes-Cummings ladder). It refers to the quantum number of the Floquet-Bloch state, not to a physical angular momentum L = r × p with r ∈ ℝ³.

For δJ = s₀(ω × r) to be reproduced, ω must act on r via the cross product — a 3D geometric operation. The dressed-state precession acts on the Bloch vector — a 3D abstract space. These are not the same object.

### F.3 Verdict

**REJECTED.** The dressed-state precession frequency is a Bloch-sphere angular velocity, not a physical-space angular velocity. The identification fails for the same structural reason as Candidates A and B.

---

## Candidate G — Direct Construction from Frozen Equations

### G.1 The Precise Constraint

This candidate asks: is there any mathematical object definable within the frozen equations that maps exactly to the ω in δJ = s₀(ω × r)?

The frozen equations contain the following quantities with units of rad/s or equivalent:

| Quantity | Source | Physical meaning |
|----------|--------|-----------------|
| ω | [RF], [DCH] | Physical frame angular velocity |
| 1/τ | [ME] | Damping rate |
| c/r | [S0],[V0] | Characteristic wave rate |
| Γ₀ | [DCH] | Base decoherence rate |
| ω_max | [DCH] | Saturation frequency |

None of these are controllable in a superconducting qubit experiment except through the physical rotation of the apparatus (literal ω).

### G.2 What "Exact Change of Variables" Requires

An exact change of variables ω → f(Ω_drive) requires:

```
δJ = s₀(ω × r) = s₀(f(Ω_drive) × r)
```

for some function f and for r a physical position vector in 3D space. This means f(Ω_drive) must be a 3-vector with units rad/s, generated by the qubit control parameter Ω_drive, and it must act on the physical position vector r of the qubit within the substrate.

**The position vector problem:** A superconducting qubit is a lumped-circuit element. Its "position" r is fixed — it is the location of the chip on the laboratory table. The substrate theory uses r as the position within the rotating frame. For δJ = s₀(ω × r), the r is the position of the quantum system relative to the rotation axis.

If r is fixed (as it is for a chip-based qubit), then δJ = s₀(ω × r) is a fixed vector for given ω. There is no qubit control parameter that can substitute for ω in this expression without also varying r — and r is not controllable in a fixed chip.

**Exception:** If the qubit is physically rotated (e.g., mounted on a spinning platform), then ω is literally the angular velocity of the platform. In that case, ω is directly controllable and no mapping is needed — the substrate prediction applies directly.

### G.3 The Lorentz Analogy (and why it fails)

One might attempt: the driven qubit precesses at ω_eff = √(Δ² + Ω_R²) in the Bloch sphere. Define the "effective position" r_eff = ⟨σ⟩/|⟨σ⟩| (unit Bloch vector). Then:

```
ω_eff × r_eff  ≡  Bloch-sphere analogue of ω × r
```

**Why this fails:** The Bloch vector ⟨σ⟩ is not a position vector in physical space. It is a vector in the abstract space of expectation values of spin operators. The substrate field s₀ is defined over physical space ℝ³, not over the Bloch sphere. The current J = s v_sub is a physical current density (info/m²/s) in 3D space. Substituting the Bloch vector for r conflates two unrelated spaces and constitutes a redefinition of the physical variables — which is prohibited.

### G.4 Verdict

**REJECTED.** No mathematical object in the frozen equations admits an exact change of variables to a superconducting qubit control parameter. Every candidate either requires redefining ω (prohibited), invokes constitutive assumption CA-3 (circular), or relies on a structural analogy rather than a derivation.

---

## Summary Table

| Candidate | Mechanism | Break point | Verdict |
|-----------|-----------|------------|---------|
| A | Rotating-frame transformation | ω×r ≠ Ω_d in Hilbert space | REJECTED |
| B | Interaction-picture angular velocity | Bloch rotation ≠ physical rotation | REJECTED |
| C | Floquet effective Hamiltonian | ω=Ω_R requires CA-3 (postulate) | REJECTED (exact); falsifiable hypothesis |
| D | Magnus expansion | No ω×r term possible without position observable | REJECTED |
| E | Synthetic gauge field | Requires spatial d.o.f. absent in two-level qubit | REJECTED |
| F | Dressed-state angular momentum | Bloch-sphere angular velocity ≠ physical angular velocity | REJECTED |
| G | Direct construction | No control parameter substitutes for ω×r exactly | REJECTED |

---

## Root Cause of All Rejections

All seven candidates fail at the same structural point. The substrate derivation produces:

```
δJ = s₀ (ω × r)
```

where:
- s₀ is a scalar field over physical 3D space
- ω is an angular velocity vector in physical 3D space
- r is a position vector in physical 3D space
- × is the 3D cross product

This expression is a **physical-space vector field**. Every candidate from superconducting-qubit physics produces a **Hilbert-space operator**. The mapping between these two objects is not an algebraic change of variables — it is a physical coupling between the quantum system and the substrate field. That coupling is constitutive assumption CA-3 in UNIFIED_PERTURBATIVE_DERIVATION.md.

CA-3 is a postulate, not a derivation. Using it to establish the mapping is circular: the mapping would be assuming the thing it is trying to prove.

The only path that avoids this circularity is literal physical rotation: mount the qubit on a rotating platform, so that ω is the actual angular velocity of the apparatus. In that case δJ = s₀(ω × r) applies directly, with ω experimentally controlled by the rotation rate of the platform.

---

## Final Verdict

```
Result:
The existing theory does NOT imply an experimentally controllable
observable via any of the candidate mappings A–G.

A genuine theoretical extension would be required to identify ω
with any superconducting-qubit control parameter (drive frequency,
Rabi frequency, detuning, or dressed-state splitting).

The only path consistent with the frozen equations is:
  ω = physical angular velocity of the rotating apparatus.
This is directly controllable but requires physical rotation of
the qubit, not a change of drive parameters.
```
