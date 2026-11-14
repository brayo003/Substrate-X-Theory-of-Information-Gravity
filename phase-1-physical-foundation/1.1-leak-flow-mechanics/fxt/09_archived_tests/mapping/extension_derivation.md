# Extension Derivation: First-Principles Internal Quantum Coupling

**Status:** Theory laboratory — extension branch  
**Frozen references (immutable):**
- `COMPLETE_MASTER_EQUATION.md`
- `UNIFIED_PERTURBATIVE_DERIVATION.md`
- `mapping/mapping_derivation.md`

**Date:** 2026-07-19  
**Rule:** No equation in the frozen documents may be modified. Every new equation must follow explicitly from the master equation below.

---

## Starting Point (Exact, Frozen)

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u)
                    + αE + β∇·(E v_sub) + γF − σ_irr    [ME]
```

**Symbol table (all meanings fixed by COMPLETE_MASTER_EQUATION.md):**

| Symbol | Units | Meaning |
|--------|-------|---------|
| s | info/m³ | Information density |
| τ | s | Damping time constant |
| c | m/s | Causal propagation speed |
| v_sub | m/s | Substrate flow velocity |
| χ | m/s | Coherence transport coefficient |
| u | — | Coherent propagation direction (unit vector) |
| α | info/(J·s) | Information–energy coupling |
| β | info·s/J | Energy-flow coupling |
| γ | info/(N·s) | Force coupling |
| σ_irr | info/(m³·s) | Irreversible loss rate |

**Established result from mapping audit:**
```
δJ = s₀(ω × r)                                          [D2']
```
is a physical-space current. No mapping from ω to any qubit control parameter exists within the frozen theory. This result is accepted and not challenged.

**Research question:** Does [ME] itself — without modification — admit a more general coupling that acts on internal quantum degrees of freedom?

---

## Candidate A — Higher-Order Perturbation: O(v³/c³) and Beyond

### A.1 Setup

The frozen derivation truncates the perturbation series at O(ε²), ε = v/c, producing δs = −μL²/(c²r³).

Here we carry the expansion one order further to O(ε³) to determine whether new coupling terms appear.

**Approximations carried forward:** [A1] steady state, [A2] source-free, [A3] no coherence transport (χ = 0 for this candidate), [A4] v/c ≪ 1, [A5] incompressible substrate flow.

The working equation (from UNIFIED_PERTURBATIVE_DERIVATION.md eq. [SS']):
```
c²τ ∇²s − ∇·(s v_sub) + v·∇s = 0                      [SS']
```

Write s = s₀ + s₁ + s₂ + s₃ + O(ε⁴).

### A.2 Third-Order Equation

At O(ε³), collecting terms from [SS']:
```
c²τ ∇²s₃ = −v·∇s₂                                      [P3]
```

(The ∇·(s₃ v_sub) term is O(ε⁴) and dropped.)

From the frozen derivation: s₂(r,θ) = f(r) sin²θ with f(r) = −μL²/(c²r³).

Compute ∇s₂:
```
∇s₂ = ∂_r(f sin²θ) r̂ + (1/r) ∂_θ(f sin²θ) θ̂
     = f'(r) sin²θ r̂ + (2f(r)/r) sinθ cosθ θ̂         [GS2]
```

with f'(r) = 3μL²/(c²r⁴).

The particle velocity at O(ε): v = v_r r̂ + v_⊥ θ̂. Therefore:
```
v·∇s₂ = v_r f'(r) sin²θ + v_⊥ (2f/r) sinθ cosθ        [SRC3]
```

Substituting f = −μL²/(c²r³) and f' = 3μL²/(c²r⁴):
```
v·∇s₂ = (3μL²v_r)/(c²r⁴) sin²θ − (2μL²v_⊥)/(c²r⁴) sinθ cosθ
```

### A.3 Angular Structure and Orbit Average

The source [SRC3] contains two angular modes:
- sin²θ (ℓ=2, m=0 in spherical harmonics — already present at O(ε²))
- sinθ cosθ = (1/2)sin(2θ) (ℓ=2, m=0 as well, but with different radial weighting)

Orbit average of the radial term: v_r averages to zero over a full Keplerian orbit (radial velocity is odd under time reversal, same argument as in [A7] of the frozen derivation).

Orbit average of the transverse term: v_⊥ = L/r (constant for circular orbits, non-zero average).

**Surviving third-order field:**
```
c²τ ∇²s₃ = (2μL³)/(c²r⁵) sinθ cosθ                    [P3-L]
```

This has the same ℓ=2 angular structure as s₂ but with a sin(2θ) pattern and radial dependence r⁻⁵. The solution has the form s₃ ∝ r⁻⁴ sinθ cosθ — a pure ℓ=2 field.

### A.4 Physical Content of s₃

The third-order field s₃:
- Is an ℓ=2 (quadrupole) correction in angle.
- Has magnitude δs₃/δs₂ ∼ (v⊥/c) ≲ 10⁻⁴ relative to the second-order field.
- Is still a scalar function on physical space.
- Carries no index structure that could couple to internal degrees of freedom.

**Key observation:** s₃, like s₀, s₁, s₂, is a classical scalar field on ℝ³. Its gradient produces a vector force field. There is no mechanism within a classical scalar field theory to generate a coupling to a two-state internal degree of freedom. The perturbation hierarchy produces increasingly small classical corrections; it does not spontaneously generate operator structure.

### A.5 Verdict on Candidate A

**REJECTED.** Higher-order terms in the v/c expansion produce classical scalar corrections to the information density field. They do not introduce any coupling to internal quantum degrees of freedom. The mathematical structure is the same at every order: s_n is a classical scalar, and the force coupling to matter is through F = k s v_sub (constitutive assumption CA-2 of the frozen theory). No order of the perturbation expansion changes this.

---

## Candidate B — Coherence Transport χsu Retained

### B.1 Setup

The frozen derivation discards the coherence transport term χsu under approximation [A3]:

> "The coherence term χsu is dropped relative to advection s v_sub. Justification: χ/|v_sub| is assumed small in the Newtonian regime."

Here we retain it and determine what new structure emerges.

**Approximations in force:** [A1] steady state, [A2] source-free, [A4] v/c ≪ 1, [A5] incompressible. [A3] is NOT applied.

The steady-state equation becomes:
```
c²τ ∇²s = ∇·(s v_sub + χ s u)                          [SS-B]
```

Expanding the right-hand side:
```
∇·(s v_sub + χ s u) = v_sub·∇s + s ∇·v_sub
                     + χ(u·∇s + s ∇·u)
```

Applying [A5] (∇·v_sub = 0):
```
c²τ ∇²s = v_sub·∇s + χ(u·∇s + s ∇·u)                  [SS-B']
```

### B.2 Perturbation Expansion with χ Retained

Write s = s₀ + s₁ + s₂ as before. At zeroth order, if χ is treated as O(ε⁰) (comparable to v_sub in magnitude), the background equation is:

```
c²τ ∇²s₀ = v_sub·∇s₀ + χ(u·∇s₀ + s₀ ∇·u)             [P0-B]
```

For the background to reduce to the Newtonian s₀ = μ/r, we need the χ term to be negligible at zeroth order. This is consistent with treating χ as O(ε¹) — i.e., χ/c ∼ ε. Under this assignment:

**O(ε⁰):** Recovers [P0] of the frozen derivation. Background field s₀ = μ/r unchanged.

**O(ε¹):**
```
c²τ ∇²s₁ = v·∇s₀ + χ(u·∇s₀ + s₀ ∇·u)                 [P1-B]
```

The new term relative to [P1] is:
```
χ(u·∇s₀ + s₀ ∇·u)                                      [CT1]
```

### B.3 Analysis of the Coherence Transport Term

u is the coherent propagation direction — a unit vector field. In the most general case, u = u(r, t). For the steady-state problem u = u(r).

Term [CT1] contains two parts:

**Part 1:** χ u·∇s₀ = χ u·(−μ/r² r̂) = −χμ/r² (u·r̂)

This is a scalar: it depends on the angle between u and the radial direction. It modifies the effective source for s₁ but remains a scalar field equation.

**Part 2:** χ s₀ ∇·u

This term involves the divergence of u. Since u is a unit vector field, ∇·u measures the spreading or converging of the coherence direction field. For a uniform field u = const, ∇·u = 0 and this term vanishes.

**Can u have internal-DOF structure?**

u is defined in `COMPLETE_MASTER_EQUATION.md` as "coherent propagation direction (unit vector)." It is a classical vector field on physical space — no matrix structure, no operator index. Therefore [CT1] is a classical scalar equation regardless of the spatial dependence of u.

### B.4 Second-Order with χ Retained

At O(ε²):
```
c²τ ∇²s₂ = v·∇s₁ + χ(u·∇s₁ + s₁ ∇·u)                 [P2-B]
```

The additional term relative to [P2] is:
```
χ(u·∇s₁ + s₁ ∇·u)                                      [CT2]
```

From s₁ = (μv/2c²τ) cosθ, the gradient is:
```
∇s₁ = −(μv/2c²τr) sinθ θ̂
```

So:
```
u·∇s₁ = −(μv/2c²τr) sinθ (u·θ̂)
```

This is again a scalar. It adds an angular correction to the source of s₂ that depends on the angle between u and θ̂, but does not change the scalar nature of the equation.

**The coherence transport term modifies the numerical coefficients and angular structure of s₁ and s₂.** It does not introduce any new mathematical object. The field s remains a classical scalar throughout.

### B.5 What χsu Actually Encodes

The term χsu is a directed transport flux — it represents information flowing preferentially in direction u. In the master equation it appears inside a divergence: −∇·(χsu). This is structurally identical to the advection term −∇·(sv_sub), with v_sub replaced by χu.

Both terms move information through space. Neither term generates internal quantum degrees of freedom because the field s has no spinor or operator index. The direction u is external (a classical vector field), not an operator.

### B.6 Verdict on Candidate B

**REJECTED** as a source of internal quantum coupling. The coherence transport term χsu modifies the effective transport velocity of the information field but preserves its classical scalar nature. No internal degrees of freedom emerge from retaining this term.

**Partial result:** If u is allowed to precess (∂u/∂t ≠ 0), removing [A1] as well, a new dynamical equation for u is implied. This is investigated in Candidate C.

---

## Candidate C — Removing the Steady-State Approximation

### C.1 Setup

The frozen derivation applies [A1]: all time derivatives set to zero. Here we retain the full time-dependent equation.

The full master equation [ME] with [A2] (source-free) and [A3] (no coherence for now) applied:
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub)             [ME-C]
```

Write s = s₀ + δs(r,t), where s₀ = μ/r is the static background (satisfying the steady-state equation exactly), and δs is a time-dependent perturbation.

Linearising [ME-C] in δs (treating v·∇δs as small):
```
τ ∂²(δs)/∂t² + ∂(δs)/∂t = c²τ ∇²(δs) − v_sub·∇(δs) − δs ∇·v_sub + source
```

Under [A5] (incompressible, ∇·v_sub = 0):
```
τ ∂²(δs)/∂t² + ∂(δs)/∂t = c²τ ∇²(δs) − v_sub·∇(δs)   [LIN-C]
```

### C.2 Wave-Like Solutions

Seek plane-wave solutions δs ∝ exp(i k·r − i ω_w t):

Substituting into [LIN-C] (ignoring the advection term for the free-field case):
```
−τ ω_w² (δs) − i ω_w (δs) = −c²τ k² (δs)
```

```
τ ω_w² + i ω_w − c²τ k² = 0                             [DISP]
```

This is the dispersion relation. Solving for ω_w:
```
ω_w = [−i ± √(−1 + 4c²τ²k²)] / (2τ)                   [DISP-SOL]
```

For c²τ²k² ≫ 1/4 (short-wavelength, high-k limit):
```
ω_w ≈ ±ck − i/(2τ)                                      [DISP-HI]
```

These are damped propagating waves — the telegrapher modes of the master equation.

For c²τ²k² ≪ 1/4 (long-wavelength, low-k limit):
```
ω_w ≈ −i/τ   or   ω_w ≈ −i c²τ k²                      [DISP-LO]
```

Two purely imaginary roots: one fast decay (rate 1/τ) and one slow diffusion.

### C.3 Quantising the Wave Field

The substrate field s(r,t) satisfies a linear wave equation [LIN-C]. Any classical linear wave field can be formally expanded in normal modes:

```
δs(r,t) = Σ_k [a_k φ_k(r) e^{−iω_k t} + a_k* φ_k*(r) e^{+iω_k* t}]   [EXP-C]
```

where φ_k are the spatial mode functions and a_k are complex amplitudes.

**Formal quantisation step:** Replace classical amplitudes a_k, a_k* with operators â_k, â_k†:
```
δŝ(r,t) = Σ_k [â_k φ_k(r) e^{−iω_k t} + â_k† φ_k*(r) e^{+iω_k* t}]  [QF-C]
```

with commutation relations [â_k, â_k'†] = δ_{kk'}.

This produces an operator-valued field δŝ. Is this derivable from [ME], or does it require a new postulate?

### C.4 The Quantisation Postulate Problem

**Canonical quantisation** of a classical field requires specifying:
1. A Lagrangian density L for the field.
2. The canonical momentum π = ∂L/∂(∂_t s).
3. The equal-time commutation relation [s(r,t), π(r',t)] = iℏ δ(r−r').

**Step 1:** Can a Lagrangian be identified for [ME-C]?

The master equation [ME-C] is a **dissipative** equation (the ∂s/∂t damping term). Dissipative systems do not have a standard Lagrangian formulation because the Euler-Lagrange equations conserve phase-space volume (Liouville's theorem), while dissipative systems contract it.

There exist extended Lagrangian formulations for dissipative systems (Caldirola-Kanai, Bateman doubled-system), but they require introducing auxiliary ("mirror") degrees of freedom that are not present in [ME]. Applying them would add new fields not in the master equation — which is prohibited.

**Conclusion on C.4:** Canonical quantisation of [ME-C] cannot be carried out directly because [ME-C] is dissipative. The quantisation step [QF-C] cannot be derived from [ME] alone. It requires a new postulate (specifying the commutation relations) that has no basis in the original master equation.

### C.5 Time-Dependent δs Without Quantisation

Without quantisation, removing the steady-state approximation generates time-dependent classical perturbations δs(r,t). These propagate as damped telegrapher waves [DISP-HI]. They still couple to matter through the constitutive rules (CA-1, CA-2, CA-3 of the frozen theory).

The time-dependent δs(r,t) would modulate the decoherence rate:
```
Γ(t) = Γ₀ + (κ/ℏ s₀² r²) |δJ(r,t)|²                   [TDCOH]
```

This is a time-varying decoherence rate driven by substrate wave modes — a classical effect, not a quantum coupling to internal degrees of freedom.

### C.6 Verdict on Candidate C

**REJECTED** as a source of internal quantum coupling. Removing the steady-state approximation generates classical wave modes of δs. Quantising these modes requires a new postulate (canonical commutation relations) that cannot be derived from [ME] because [ME] is dissipative and lacks a standard Lagrangian. Without quantisation, all results are classical.

**Partial result:** The telegrapher dispersion relation [DISP] is a genuine derivable consequence of [ME] and may be relevant for non-steady-state experimental regimes.

---

## Candidate D — Operator-Valued Information Density

### D.1 Setup

Here we ask: can s be an operator-valued field without introducing a new postulate?

An operator-valued field ŝ(r,t) takes values in the space of linear operators on some Hilbert space H. For ŝ to be operator-valued, there must be a Hilbert space on which it acts.

**The question is:** Does [ME] itself identify or require such a Hilbert space?

### D.2 What [ME] Specifies

The master equation [ME] specifies:
- The dynamics of s(r,t) in terms of differential operators acting on s.
- Coupling terms αE, βE, γF that are classical field sources.
- A dissipative damping term ∂s/∂t.

[ME] contains no index that ranges over quantum states. It contains no commutator. It contains no ℏ. It does not reference any Hilbert space.

Therefore, the mathematical content of [ME] — taken literally — treats s as a scalar function on ℝ³ × ℝ (space × time). Nothing in [ME] prohibits s from being operator-valued, but nothing in [ME] requires it.

### D.3 Necessary Conditions for Operator-Valued Extension

For an operator extension ŝ to be physically meaningful, the following must hold:

**Condition D-1:** The Hilbert space H must be identified.  
**Condition D-2:** The commutation relations of ŝ(r,t) with itself must be specified.  
**Condition D-3:** The classical limit ℏ → 0 must recover [ME] exactly.  
**Condition D-4:** The extension must be consistent with the dissipative structure of [ME].

**Checking D-1:** The master equation does not identify H. The information density s has units info/m³. For s to act on a quantum system with Hilbert space H_q (e.g., a qubit), there must be a coupling rule specifying how a scalar field acts on H_q. This coupling rule is not in [ME].

**Checking D-2:** Canonical quantisation (Candidate C) fails for dissipative systems. Non-canonical quantisation schemes exist but require specifying a Lindblad structure, which is a new postulate.

**Checking D-3:** If ŝ → s_c (classical) as ℏ → 0, then [ME] is automatically satisfied. This is a consistency condition, not a derivation. It does not determine ŝ from [ME] — it only constrains ŝ to be compatible with [ME].

**Checking D-4:** Operator-valued fields on Hilbert spaces are typically governed by Heisenberg equations of motion, which are unitary (no dissipation). The dissipative ∂s/∂t term in [ME] is incompatible with a unitary Heisenberg equation. A Lindblad master equation can accommodate dissipation, but it requires specifying the Lindblad operators — a new postulate.

### D.4 Formal Substitution Attempt

Formally substitute ŝ = s_c I + δŝ into [ME], where I is the identity on H and δŝ is operator-valued:

```
τ ∂²(s_c I + δŝ)/∂t² + ∂(s_c I + δŝ)/∂t
    = c²τ ∇²(s_c I + δŝ) − ∇·((s_c I + δŝ)v_sub + χ(s_c I + δŝ)u)
    + αE I + β∇·(Ev_sub) I + γF I − σ_irr I               [OP-ME]
```

Since [ME] is linear in s, this splits:

**Classical part (coefficients of I):** recovers [ME] exactly for s_c. ✓

**Operator part:** δŝ satisfies the same equation [ME] with all source terms set to zero (since the sources αE, βE, γF, σ_irr are classical):
```
τ ∂²(δŝ)/∂t² + ∂(δŝ)/∂t = c²τ ∇²(δŝ) − ∇·(δŝ v_sub + χ δŝ u)  [OP-δs]
```

**This is [ME] for the operator perturbation, with no source terms.** It is a linear PDE for δŝ. Its solution is determined by:
1. Initial conditions for δŝ and ∂_t δŝ — which require specifying quantum state preparation. Not in [ME].
2. The operator nature of δŝ — which requires specifying H and the commutation structure. Not in [ME].

[ME] is consistent with an operator-valued extension but does not determine it. The extension requires specifying (at minimum) initial conditions on δŝ as an operator, which is a new postulate.

### D.5 Verdict on Candidate D

**REJECTED** as a derivable consequence of [ME]. The master equation is consistent with an operator-valued extension but does not determine one. Specifying the Hilbert space H and the commutation relations of δŝ are necessary conditions for the extension that cannot be derived from [ME] alone. Any operator-valued extension requires at least one new postulate.

**Important result:** Equation [OP-δs] shows that IF a Hilbert space and commutation structure are specified externally, then the operator perturbation δŝ satisfies a well-defined linear equation derived from [ME]. This is the closest the current theory comes to an internal quantum coupling without a new postulate.

---

## Candidate E — Quantisation of Substrate Perturbations

### E.1 Setup

Rather than quantising s as a whole (Candidate D), here we ask a narrower question: does the second-order perturbation δs = −μL²/(c²r³) acquire operator structure naturally?

The field δs satisfies [OP-δs] (from Candidate D):
```
τ ∂²(δs)/∂t² + ∂(δs)/∂t = c²τ ∇²(δs) − ∇·(δs v_sub)  [OP-δs]
```

(retaining classical notation since operator status is under investigation).

### E.2 Mode Decomposition of δs

From Candidate C, the time-dependent δs decomposes into damped normal modes:
```
δs(r,t) = Σ_k A_k φ_k(r) e^{−iω_k t}                   [MOD-E]
```

where ω_k are the complex frequencies from the dispersion relation [DISP]:
```
τ ω_k² + i ω_k − c²τ k² = 0
```

The amplitude A_k is determined by initial conditions.

### E.3 Energy of a Mode

To quantise, we need the energy of each mode. For a classical field, the energy density is:
```
ε = (1/2)(∂_t s)² + (1/2)(c²τ)(∇s)²  (schematic)
```

However, [ME] is dissipative. The usual energy density for a wave equation is not conserved — the damping term ∂s/∂t drains energy continuously. A conserved "energy" for the telegrapher equation does not exist in closed form without the reservoir that absorbs the dissipated energy.

**Formal consequence:** Without a conserved energy, we cannot define normal-mode energies ℏω_k that would naturally quantise the field. Quantisation requires identifying a Hamiltonian, which requires a conserved energy, which requires a non-dissipative (or explicitly Hamiltonian-plus-bath) formulation.

### E.4 Attempting a Formal Hamiltonian

The telegrapher equation (one-dimensional, for clarity):
```
τ ∂²s/∂t² + ∂s/∂t − c²τ ∂²s/∂x² = 0
```

can be cast as a Hamiltonian system by the Bateman trick: introduce a time-reversed "mirror" field s̃ satisfying:
```
τ ∂²s̃/∂t² − ∂s̃/∂t − c²τ ∂²s̃/∂x² = 0
```

The Lagrangian:
```
L = τ (∂_t s)(∂_t s̃) − c²τ (∂_x s)(∂_x s̃) − (1/2)(s ∂_t s̃ − s̃ ∂_t s)  [BAT-L]
```

gives both equations of motion. The canonical momenta are:
```
π_s  = ∂L/∂(∂_t s)  = τ ∂_t s̃ + (1/2) s̃
π_s̃ = ∂L/∂(∂_t s̃) = τ ∂_t s  − (1/2) s
```

The Hamiltonian is:
```
H_Bat = π_s ∂_t s + π_s̃ ∂_t s̃ − L                     [BAT-H]
```

### E.5 The Mirror Field Problem

The Bateman doubled system introduces s̃ — a field with no counterpart in [ME]. The master equation [ME] contains only s, not s̃. Therefore [BAT-L] and [BAT-H] describe a system larger than [ME]: they describe [ME] plus a mirror copy of [ME] with reversed dissipation.

**This violates the derivation requirement:** The extension must emerge from [ME] alone. The Bateman trick introduces s̃ as a new degree of freedom not implied by [ME]. It is a new postulate.

**Conclusion on E.5:** The Bateman Hamiltonian is a valid mathematical object, but it is not derivable from [ME] — it requires introducing s̃ as a new field. Using it here is prohibited.

### E.6 Are There Non-Bateman Alternatives?

Alternative quantisation schemes for dissipative systems include:
- **Lindblad quantisation:** Specify Lindblad operators L_k that encode dissipation. Requires postulating the form of L_k.
- **Stochastic quantisation:** Add a Langevin noise force to the field equation. Requires postulating the noise statistics.
- **Path integral with complex action:** Requires postulating the measure.

All alternatives require at least one postulate beyond [ME].

### E.7 Verdict on Candidate E

**REJECTED.** The substrate perturbation δs does not naturally acquire operator structure from [ME] alone. Quantising δs requires either a conserved energy (absent due to dissipation) or an auxiliary construction (Bateman, Lindblad, stochastic) that introduces new degrees of freedom not in [ME]. No quantisation scheme for δs is derivable from [ME] without a new postulate.

---

## Candidate F — Interaction Hamiltonian from the Master Equation

### F.1 The Question

Does [ME] imply an interaction Hamiltonian H_int between the substrate field and a quantum system?

A Hamiltonian H_int acts on a Hilbert space and generates unitary evolution. For H_int to arise from [ME], there must be a term in [ME] that, under some change of variables, takes the form of a Hamiltonian density h_int(r) such that:
```
H_int = ∫ h_int(r) d³r                                  [HINT-DEF]
```

### F.2 Identifying Candidate Terms in [ME]

The right-hand side of [ME] contains:

| Term | Structure | Type |
|------|-----------|------|
| c²τ ∇²s | Laplacian of s | Kinetic (diffusion) |
| −∇·(s v_sub) | Divergence of current | Advection |
| −∇·(χ s u) | Divergence of directed current | Coherence transport |
| αE | Energy source | External forcing |
| β∇·(E v_sub) | Energy-flow source | External forcing |
| γF | Force source | External forcing |
| −σ_irr | Sink | Dissipation |

The energy coupling term αE is the most natural candidate for an interaction Hamiltonian, since E is the energy density of matter.

### F.3 The αE Term

The term +αE in [ME] says: energy density E creates information density s at rate α.

If E is the energy density of a quantum system (e.g., a qubit), then E = ⟨H_q⟩/V, where H_q is the qubit Hamiltonian and V is the volume.

**Attempt:** Define the interaction as:
```
∂s/∂t|_{int} = αE = α ⟨H_q⟩/V                         [INT-ATT]
```

For this to be a Hamiltonian coupling H_int, we need [INT-ATT] to be expressible as:
```
i/ℏ [H_int, ρ_q]  for some ρ_q                         [INT-COM]
```

But [INT-ATT] is a scalar rate equation for s — it is the rate of change of the classical field s due to the energy of the quantum system. It is a source term in a classical PDE, not a commutator in a quantum master equation.

**The structural gap:** To go from [INT-ATT] to [INT-COM], one would need to specify how the quantum expectation value ⟨H_q⟩ couples back to the quantum state ρ_q through the substrate field s. This back-action is not in [ME] — [ME] specifies only how E affects s, not how s affects the quantum system. That back-action would require a new coupling equation.

### F.4 The Force Coupling Term γF

The term γF says: force density F generates information. If F is the force on a quantum system, then F = −∇⟨H_q⟩. Using the gradient of the energy:

```
∂s/∂t|_{F} = γF = −γ ∇⟨H_q⟩                          [FC-ATT]
```

This is a gradient of the quantum energy in physical space — again a classical source for s, not a quantum operator equation.

### F.5 The γF → δJ → H_int Chain

Consider the decoherence branch of the frozen theory. The current perturbation δJ = s₀(ω×r) enters the decoherence rate through CA-3:
```
Γ ∝ ⟨(δJ)²⟩
```

CA-3 identifies a rate but not a Hamiltonian. To extract H_int, one would need:
```
Γ = (2/ℏ²) ∫₀^∞ ⟨[H_int(t), H_int(0)]⟩ dt            [FGR]
```

(Fermi's golden rule / Redfield form). For this to be consistent with Γ = k_rot ω², one needs:
```
∫₀^∞ ⟨[H_int(t), H_int(0)]⟩ dt = (ℏ² k_rot / 2) ω²   [FGR-MATCH]
```

**This is a constraint on H_int, not a derivation of H_int.** It says: IF H_int exists, its autocorrelation must satisfy [FGR-MATCH]. But it does not determine H_int uniquely — infinitely many Hamiltonians produce the same autocorrelation.

For example, any H_int of the form:
```
H_int = λ ω σ_z                                         [HI-TRY]
```

with λ chosen so that λ² τ_c = ℏ² k_rot / 2 (where τ_c is the correlation time) would satisfy [FGR-MATCH]. But this requires postulating both the form (σ_z coupling) and the correlation time τ_c — neither follows from [ME].

### F.6 Dimensional Analysis of Possible H_int

From [ME], the available dimensioned quantities that could appear in H_int are:

| Quantity | Units |
|----------|-------|
| s₀ | info/m³ |
| δs | info/m³ |
| α | info/(J·s) |
| γ | info/(N·s) |
| κ (from k_rot = 2κ/3ℏ) | dimensionless |
| ℏ | J·s |

A Hamiltonian has units of J. The only combination from [ME] that gives J is:
```
H ~ δs / α = (info/m³) / (info/(J·s·m³)) = J·s
```

That gives J·s, not J. Alternatively:
```
H ~ (δJ) · r / α ...
```

No combination of the frozen theory's constants naturally produces a Hamiltonian with units J that also depends on internal quantum operators (σ_x, σ_y, σ_z). The dimensional analysis does not yield H_int without introducing an additional coupling constant with units J·m³/info (energy per unit information density), which is not in [ME].

### F.7 Verdict on Candidate F

**REJECTED** as a derivable consequence. An interaction Hamiltonian is not implied by [ME]. The master equation specifies how classical sources (E, F) generate information density s. It does not specify how s acts back on quantum systems. That back-action requires a new coupling constant and a new coupling rule — both postulates.

**Structural conclusion:** [ME] is a one-way equation in the substrate-to-matter direction (matter sources create information; information feeds back through CA-1 and CA-2). An H_int would require two-way coupling with an explicit quantum back-action. [ME] contains only the forward direction.

---

## Candidate G — Mathematically Unavoidable Extensions

### G.1 What Would Be "Unavoidable"

A mathematically unavoidable extension is one where ignoring a term in [ME] requires taking a limit that is not self-consistent. We look for such terms.

### G.2 The σ_irr Term

The irreversible loss term −σ_irr represents entropy production. In quantum mechanics, entropy production is associated with decoherence and environmental coupling. Is σ_irr forced to have quantum content?

From [ME], σ_irr has units info/(m³·s) — identical to ∂s/∂t. It is a sink for information density. It is defined as the irreversible entropy production rate.

In classical thermodynamics, σ_irr = Σ_i J_i X_i where J_i are thermodynamic fluxes and X_i are thermodynamic forces (generalized forces). This is entirely classical.

In quantum thermodynamics, σ_irr can be expressed in terms of the von Neumann entropy: σ_irr = −d/dt Tr(ρ ln ρ) / k_B. But ρ here is the density matrix of the quantum substrate — a new object not in [ME]. Introducing ρ is a new postulate.

**Verdict:** σ_irr is defined classically in [ME] and does not force quantum content.

### G.3 The χsu Term at Zeroth Order

In Candidate B we found that retaining χsu modifies the classical dynamics. Now consider the case χ → ic̃ (imaginary coherence coefficient). The term becomes:

```
−∇·(ic̃ s u) = −ic̃(u·∇s + s ∇·u)
```

An imaginary coefficient in a real PDE would make s complex-valued. A complex scalar field on ℝ³ has two degrees of freedom: |s| and arg(s). The phase arg(s) could in principle be associated with a quantum phase.

**Why this fails:** The master equation [ME] is stated for real-valued s (information density is a non-negative real number). Making χ imaginary would require extending s to complex values — a new postulate about the domain of s. Nothing in [ME] requires s to be complex.

### G.4 The Covariant Form

The frozen document gives the covariant form:
```
τ ∂_μ ∂^μ s + ∂_μ J^μ = S − σ_irr
```

with J^μ = (cs, s v_sub + χ s u) and S = αE + β∇·(E v_sub) + γF.

The current J^μ is a 4-vector on spacetime. Under Lorentz transformations (if the theory is Lorentz covariant), J^μ transforms as a vector. The scalar s transforms as a scalar.

**Spinor extension attempt:** In relativistic field theory, scalars and spinors transform differently. A spinor field ψ satisfies the Dirac equation, not the scalar wave equation. Could s be a component of a spinor?

For s to be a spinor component, the master equation would need to be rewritten as a Dirac equation or its non-relativistic limit (Pauli equation). The master equation has a different structure:
- [ME] has a ∂_t damping term (not in Dirac).
- [ME] is second-order in space (Dirac is first-order).
- [ME] has explicit source terms (Dirac has no external sources in free-field form).

Rewriting [ME] as a Dirac equation would change the equation — which is prohibited.

### G.5 Gauge Structure

The master equation [ME] can be written in conservation-law form:
```
τ ∂_t (∂_t s) + ∂_t s = −∂_i J^i + S − σ_irr           [CONS]
```

In gauge field theories, conservation laws are associated with gauge symmetries via Noether's theorem. Is there a gauge symmetry of [ME]?

**Global symmetry check:** [ME] is not invariant under s → s e^{iθ} because s appears without phase — it is real-valued. There is no global U(1) symmetry.

**Local symmetry check:** A local gauge symmetry s(r,t) → s(r,t) + Λ(r,t) would require adding a gauge field A_μ to compensate — which would change [ME]. This is prohibited.

**Conclusion:** [ME] has no gauge symmetry that would force the introduction of quantum gauge degrees of freedom.

### G.6 The Minimum Coupling Prescription

In electrodynamics, the minimal coupling p → p − qA/c generates an interaction Hamiltonian from the kinetic term. Is there an analogue in [ME]?

The kinetic term in [ME] is c²τ ∇²s. Under the substitution ∇ → ∇ − i A (minimal coupling with vector potential A):
```
∇²s → (∇ − iA)²s = ∇²s − 2iA·∇s − i(∇·A)s − A²s
```

The additional terms −2iA·∇s − i(∇·A)s − A²s would appear in [ME]. These terms:
1. Are complex — making s complex, which is a new postulate.
2. Require introducing A as a new field — which is a new postulate.
3. Would change [ME] — which is prohibited.

Minimal coupling does not apply to [ME] without modification of [ME].

### G.7 Summary of Candidate G

No mathematically unavoidable extension of [ME] was found. Every avenue explored either:
- Preserves the classical scalar nature of s (G.2, G.3 real case), or
- Requires introducing new fields or changing the domain of s (G.3 imaginary case, G.4, G.5, G.6).

The master equation [ME] is a classical scalar PDE. Its mathematical structure — linear, dissipative, real-valued, sourced by classical fields — does not contain any hidden quantum structure that is forced to emerge.

**Verdict on Candidate G: REJECTED.**

---

## Consistency Proofs

### Reduction to Frozen Theory

Every candidate was investigated starting from [ME] with no modification. The frozen results are recovered as follows:

| Frozen result | Recovered by | Approximations |
|--------------|-------------|---------------|
| s₀ = μ/r | Candidate A (zeroth order) | [A1][A2][A3][A4][A5] |
| δs = −μL²/(c²r³) | Candidate A (second order) | [A1]–[A7] |
| δJ = s₀(ω×r) | Not modified | Frame kinematic identity |
| Γ = Γ₀ + k_rot ω² | Not modified | CA-3 + above |
| Perihelion Δφ | Not modified | Gravity branch |

Setting all new coupling terms to zero (χ→0, operator parts→0) returns exactly the frozen equations. ✓

### Dimensional Consistency

All new terms identified in Candidates B–G were dimensionally checked:
- [CT1]: χ u·∇s₀ has units (m/s)(m⁻¹)(info/m³) = info/(m³·s) = same as ∂s/∂t ✓
- [SRC3]: v·∇s₂ has units (m/s)(info/m⁴) = info/(m³·s) ✓
- [OP-δs]: same structure as [ME] ✓

### Contradiction with Mapping Audit

The mapping audit established that ω in δJ = s₀(ω×r) cannot be identified with qubit control parameters. No result in this extension contradicts that. The extension investigation found no interaction Hamiltonian, consistent with the mapping audit finding no mapping. ✓

---

## Final Verdict

```
Result:
No mathematically justified extension exists from the current
master equation alone.

Any internal quantum coupling would require introducing
fundamentally new postulates beyond the existing theory.

Specifically, the minimum set of new postulates required is:

  P1. A Hilbert space H on which the substrate field acts.
  P2. Commutation relations for the operator-valued field δŝ.
  P3. A coupling rule specifying how s acts on quantum states
      (the back-action direction, absent from [ME]).

Without P1–P3, the master equation [ME] is a classical scalar PDE
and admits no internal quantum degree of freedom.

The partial result from Candidate D remains:

  IF P1–P3 are specified externally, then the operator
  perturbation δŝ satisfies [OP-δs] — a well-defined linear
  equation derived from [ME] with no source terms.

  [OP-δs]: τ ∂²δŝ/∂t² + ∂δŝ/∂t = c²τ∇²δŝ − ∇·(δŝ v_sub)

  This is the one genuine constraint that [ME] places on any
  operator extension: the quantum part of s must satisfy the
  homogeneous master equation.
```
