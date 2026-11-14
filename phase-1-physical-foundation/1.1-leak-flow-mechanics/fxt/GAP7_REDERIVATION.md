# GAP7_REDERIVATION.md
## Independent Re-derivation of GAP-7: All 25 Routes Tested

**Date:** 2026-08-22
**Method:** Exhaustive derivation attempt starting from C2 source equations
**Sources:** C2_FOUNDATIONS.md, C2_FRONTIER_MAP.md, C2_MISSING_PRINCIPLES.md,
  substrate_transport_derivation.md, 00_THEORY_AUDIT.md, 32_C_PRW_SPEED_DERIVATION_AUDIT.md
**Label convention:** DERIVED | FAILED | BLOCKED | ASSUMED | FREE

---

## Statement Being Tested

GAP-7 claims: the substrate propagation speed c (= PRW particle speed v) is
a free parameter not constrained by any equation within C2.

This document independently tests that claim by attempting every legitimate
derivation route. A route succeeds only if it produces a unique numerical
value (or bounded range) for c from other C2 quantities without circular
dependence on c itself.

---

## Background: Where c Appears in C2

The C2 transport layer is built from a PRW with:
  - step size h [m]
  - time step Δt [s]
  - particle speed v = h/Δt [m/s]   ← this is c
  - reversal rate λ [s⁻¹]

Derived quantities that depend on c:
  - τ_B = 1/(2λ)   [free: λ is free]
  - ξ_c = v/λ = 2cτ_B   [depends on c]
  - D = c²τ_B   [depends on c]
  - S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)   [does NOT depend on c directly]
  - C_JJ(r) = S₀ exp(−r/ξ_c)   [depends on c through ξ_c]
  - K₀ spatial covariance: same ξ_c = 2cτ_B

The decoherence rate Γ_φ = k_rot·ω_rot² depends on:
  k_rot = 8g²S₀r_q²τ_B / (3ℏ²)
This does NOT contain c explicitly. c enters only through ξ_c.

---

## Route 1: Dimensional Analysis

**Premise:** C2 has dimensional parameters v [m/s], λ [s⁻¹], g [J·m²·s],
S₀ [info²/(m³·s)], ℏ [J·s].

**Attempt:** Form a dimensionless group that fixes v.

**Algebra:**
  v has dimensions [m/s].
  λ has dimensions [s⁻¹].
  Their ratio v/λ = ξ_c has dimensions [m] — a length scale, not dimensionless.
  No combination of {v, λ, g, S₀, ℏ} produces a dimensionless group that
  uniquely determines v unless an independent length or mass scale is provided.

  Adding ℏ: [ℏ] = J·s = kg·m²/s.
  Combining v and ℏ: ℏ/v has dimensions [kg·m], which is momentum — not useful.
  No combination constrains v to a specific value.

**Result: FAILED.** Dimensional analysis cannot determine v. The theory has
three independent dimensional scales (v, λ, g) with no redundancy.

---

## Route 2: Normalization of s

**Premise:** The total information density ∫s dx = const (conserved, from
C2_FOUNDATIONS.md Theorem PRW-1, Result R-1).

**Attempt:** Does normalizing s fix v?

**Algebra:**
  The conservation law ∫s dx = Q is exact for any v > 0. The value Q is
  an initial condition, not a constraint on v. Changing v while keeping λ
  fixed changes ξ_c but not the conservation law itself.

**Result: FAILED.** Normalization conserves total information but does not
select a value for v.

---

## Route 3: Conservation Laws

**Premise:** C2 has one exact conservation law: total information Q = ∫s dx.

**Attempt:** Does any derived conservation law (momentum, energy-like) fix v?

**Algebra:**
  The substrate energy density E_sub = (1/2)c²s² + (1/2)J²
  satisfies ∂E_sub/∂t + ∂(c²sJ)/∂x = −(1/τ)J² (substrate_transport_derivation.md §3).
  This is a local balance law, not a global conservation: the right-hand side
  −(1/τ)J² is a dissipation term. Energy is not conserved — it is dissipated.
  The dissipation rate depends on J and τ but not in a way that fixes v.

**Result: FAILED.** No conservation law constrains v.

---

## Route 4: Equilibrium Condition

**Premise:** The PRW reaches a spatially uniform stationary state
s*(x) = const when all gradients vanish.

**Attempt:** Does the equilibrium condition s* = const fix v?

**Algebra:**
  Setting ∂s/∂t = 0 and ∂J/∂t = 0 in the transport equations [C-s, C-J]:
    0 = −∂J/∂x → J = const
    0 = −c²∂s/∂x − J/τ
  For spatially uniform s: ∂s/∂x = 0 → J = 0 → trivial equilibrium.
  This holds for any v > 0.

**Result: FAILED.** Equilibrium is v-independent.

---

## Route 5: Thermodynamic Limit

**Premise:** N → ∞ particles on the FPUT chain. Does the thermodynamic
limit select c?

**Algebra:**
  The thermodynamic limit takes N → ∞ with fixed lattice constant a and
  fixed spring constant K/m. The acoustic speed is v_s = a√(K/m).
  The P1 projection (FPUT-3, 32_C_PRW_SPEED_DERIVATION_AUDIT.md) constructs
  n±(x) as phonon action densities. The transport speed in the P1 model is
  v_s by DEFINITION: n± are defined as right/left-moving phonon densities,
  and phonons travel at v_s.

  CRITICAL FINDING (32_C_PRW_SPEED_DERIVATION_AUDIT.md §2):
  "The appearance of v_s in those equations reflects the DEFINITION of n±
  as acoustic phonon densities — particles whose characteristic speed [is v_s]."
  "Within the existing project files, no derivation is given that takes
  ṅₖ = 0 as input and derives the P1 transport PDEs as output. The transport
  equations are CONSTRUCTED as the natural phonon-gas drift equations."

  Therefore: if c is identified with v_s (acoustic speed), this identification
  is a CONSTRUCTION/DEFINITION, not a derivation. It imports v_s from the
  physics of the FPUT chain. But the C2 theory makes no claim that the
  substrate is a phonon gas — the FPUT chain is a mathematical model for
  the projection uniqueness argument, not a physical identification of the
  substrate.

**Result: FAILED as derivation; BLOCKED as identification.**
c = v_s would require asserting that the C2 substrate IS the phonon gas of
an FPUT chain in the material under study. This is an additional physical
identification not present in C2.

---

## Route 6: Dispersion Relation

**Premise:** The telegrapher equation has dispersion relation
ω(k) = −iλ ± √(v²k² − λ²).

**Attempt:** Does imposing a physical condition on the dispersion fix v?

**Algebra:**
  The dispersion relation is self-consistent for any v > 0.
  Critical wavevector: k_c = λ/v = 1/ξ_c. At k < k_c: overdamped modes.
  At k > k_c: oscillatory modes. The transition k_c depends on v/λ = ξ_c.
  No external condition fixes k_c without fixing ξ_c independently.
  
  Could causality fix v? The telegrapher equation has finite signal speed v
  (front speed). Causality requires only v > 0 (finite speed), not a
  specific value.

**Result: FAILED.** The dispersion relation is self-consistent for all v > 0.

---

## Route 7: Continuum Limit (Δx→0, Δt→0 at fixed v)

**Premise:** The PRW is defined on a lattice with h, Δt, v = h/Δt.
The continuum limit takes h→0, Δt→0 at fixed v.

**Attempt:** Does the continuum limit constrain v?

**Algebra:**
  The continuum limit is taken at fixed v and λ (A-PRW2 in C2_FOUNDATIONS.md).
  This means v is held fixed across the limit — it is an input to the limit,
  not determined by it. Any v > 0 gives a well-defined telegrapher equation
  in the limit.

**Result: FAILED.** The continuum limit presupposes v as a fixed input.

---

## Route 8: Entropy Extremization

**Premise:** The CCA has a causal entropy H_c = H + λ·r
(CCA-C3 conjecture: physically realized morphisms extremize S_causal).

**Attempt:** Does extremizing causal entropy fix v?

**Algebra:**
  H_c = −Σε(s)log ε(s) + λ_entropy · r(s)
  where λ_entropy is the weight on causal depth and r(s) is the rank.
  Extremization with respect to the probability weights ε gives a Gibbs-like
  distribution over morphisms. This determines the weights ε but not the
  propagation speed v, which enters through the rank function r(s) only as
  an overall rescaling of the depth hierarchy.

  Note: CCA-C3 is a conjecture (unproved per C2_FRONTIER_MAP.md F7).
  Even if proved, it would not constrain v.

**Result: FAILED.** Entropy extremization determines probability weights,
not the substrate speed.

---

## Route 9: Detailed Balance

**Premise:** PRW reversal satisfies detailed balance: at equilibrium,
the rate of transitions n⁺→n⁻ equals the rate n⁻→n⁺.

**Attempt:** Does detailed balance constrain v?

**Algebra:**
  At spatial uniformity, detailed balance gives λ·n⁺* = λ·n⁻*, so n⁺* = n⁻*.
  This means the equilibrium distribution has equal densities of left- and
  right-movers. This holds for any v > 0 because the reversal rate λ is
  the same in both directions (A-PRW3: Markovian flip rate).

**Result: FAILED.** Detailed balance gives n⁺* = n⁻* for all v.

---

## Route 10: Stability Conditions

**Premise:** The Q diagnostic Q = 4c²τ²|∇ ln s|² − 1 classifies stable
(Q < 0) vs. oscillatory (Q > 0) regions. The boundary Q = 0 defines ξ_c.

**Attempt:** Does stability require a specific v?

**Algebra:**
  Q = 0 ↔ |∇ ln s| = 1/(2cτ) = 1/ξ_c.
  This condition defines the coherence length ξ_c = 2cτ for a given gradient.
  But it requires knowing |∇ ln s| from the solution, which itself depends on
  boundary conditions. No intrinsic value of v is selected.

**Result: FAILED.** The stability condition defines ξ_c relative to the
field gradient, but does not fix v independently.

---

## Route 11: Causality (Signal Speed Bound)

**Premise:** Physical causality requires that information propagates at
finite speed ≤ c_light.

**Attempt:** Does this bound constrain v to a specific value?

**Algebra:**
  The constraint v ≤ c_light gives an upper bound, not a unique value.
  Any v ∈ (0, c_light] is consistent with causality.
  C2_FOUNDATIONS.md records: "CCA-IMP-3: Finite propagation speed as a
  physical ratio requires a metric. CCA provides only a counting measure
  (rank). Numerical value of c is not derivable from Ax1–Ax5 alone."

**Result: FAILED.** Causality provides only an upper bound.

---

## Route 12: Lorentz-like Invariance

**Premise:** If C2 has a Lorentz-like symmetry, the invariant speed would
be determined.

**Attempt:** Does C2 have such a symmetry?

**Status:** The Lorentz group derivation is completely open (F4 in
C2_FRONTIER_MAP.md — "no derivation from C2 foundations"). The telegrapher
equation does NOT have Lorentz invariance; it has a preferred frame
(the rest frame of the substrate). The signal speed v defines a causal
cone, but this cone is not Lorentz-invariant.

**Result: BLOCKED.** C2 does not currently have Lorentz invariance. Even if
it did (F4 resolved), the invariant speed would be the result of that
symmetry, not a constraint on v from existing equations.

---

## Route 13: Coupling to Emergent Spacetime

**Premise:** If C2 generates emergent spacetime, the metric would encode
a characteristic speed.

**Attempt:** Does the emergent spacetime fix v?

**Status:** Spacetime emergence (F4) is unproved. The Malament theorem
(C4 candidate) recovers the metric up to conformal factor from causal
order plus volume. Even if this were applied, the conformal factor would
absorb any speed rescaling. C2 has no mechanism to fix the conformal factor
from within the theory.

**Result: BLOCKED.** Emergent spacetime (F4) is unproved. Even if proved,
conformal factor is undetermined.

---

## Route 14: Coupling to the Gravitational Sector

**Premise:** C2 aims to generate gravity. Could the gravitational sector
constrain v?

**Attempt:**

The C2 gravitational sector is entirely undeveloped. No equations connecting
the substrate speed v to gravitational observables (Newton's constant G,
Schwarzschild radius, gravitational wave speed) have been derived. The
gravitational sector is not in C2_FOUNDATIONS.md at all — it is one of the
"completely open" problems (F5, F6).

**Result: BLOCKED.** No gravitational equations exist in C2 to constrain v.

---

## Route 15: Coupling to the Decoherence Sector

**Premise:** The decoherence prediction Γ_φ = k_rot·ω_rot² depends on
various substrate parameters. Could fixing Γ_φ from experiment determine v?

**Algebra:**
  k_rot = 8g²S₀r_q²τ_B / (3ℏ²)
  S₀ = (2/3)s₀²ω_rot²r_q² (from rotating-frame current variance)
  
  k_rot contains: g (free), s₀ (free substrate density), r_q (qubit radius,
  measureable), τ_B (free), ℏ (known constant).
  
  v does NOT appear in k_rot. The Markovian decoherence rate is independent
  of v. v enters only through ξ_c = 2cτ_B in the spatial correlator.
  Therefore, measuring k_rot gives a constraint on the combination
  g²s₀²τ_B, not on v.

**Result: FAILED.** Decoherence rate does not determine v.

---

## Route 16: Lattice/UV Cutoff

**Premise:** The IBM chip has a UV cutoff at lattice spacing a = 200 µm.
Could this fix v?

**Attempt:**
  The UV cutoff sets k_max = π/a, which combined with the dispersion relation
  gives a maximum frequency ω_max = √(v²k_max² − λ²) (oscillatory modes only).
  But ω_max depends on v. Setting ω_max to some physically motivated scale
  (e.g., qubit frequency ω_q) gives:
    v² = (ω_q² + λ²)/k_max²
  This would fix v IF ω_q is identified as the UV frequency of the substrate.
  But C2 makes no such identification. The qubit frequency is a qubit property,
  not a substrate property.

**Result: FAILED as derivation.** The UV cutoff provides a constraint only
if an additional identification (ω_max = ω_q) is imposed — which is an
additional physical assumption not in C2.

---

## Route 17: Fixed-Point Conditions

**Premise:** RG-like fixed points of the substrate dynamics could select v.

**Attempt:**
  The C2 transport equation is linear. Linear equations do not have
  non-trivial fixed points in the RG sense (they are themselves scale-free
  or scale-set by initial conditions). There is no nonlinear interaction
  that would generate an RG fixed point selecting v.

**Result: FAILED.** No RG fixed point condition exists in the linear C2 transport.

---

## Route 18: Self-Consistency of PRW Dynamics

**Premise:** The PRW has two parameters v and λ. Does self-consistency
of the Markovian approximation (τ_B << Γ_φ⁻¹) fix their ratio?

**Algebra:**
  The Markov condition: τ_B · Γ_φ << 1, i.e., NMP = τ_B·Γ_φ << 1.
  This is a condition on τ_B·Γ_φ, not on v.
  v and λ are both free; their ratio v/λ = ξ_c is free.
  No self-consistency condition fixes v.

**Result: FAILED.**

---

## Route 19: Action/Hamiltonian Formulation

**Premise:** If C2 has an action principle, extremizing the action might
select v.

**Status:** No action formulation of the C2 transport layer exists.
C2_FOUNDATIONS.md Theorem ME-NOV5 explicitly states: "No new variational
principles are found." CCA-C3 (causal action extremization) is a conjecture,
not a theorem. Even if proved, it would extremize over probability weights ε,
not over the speed v.

**Result: BLOCKED.** No action principle exists in C2.

---

## Route 20: Renormalization or Scale Selection

**Premise:** In QFT, RG running can select scales (dimensional transmutation).
Could C2 have an analogous mechanism?

**Status:** C2 is a classical linear transport theory. It has no interaction
terms (linear in s), no coupling constant running, no UV divergences requiring
renormalization. The RG of the substrate transport is trivial: the telegrapher
equation is scale-invariant up to the explicit scales τ and v (both free).

**Result: FAILED.** No dimensional transmutation mechanism exists in C2.

---

## Route 21: Relation Between Δt and Another Fixed Quantity

**Premise:** The PRW has a time step Δt = h/v. If Δt were fixed by some
external quantity, v would be constrained given h.

**Attempt:**
  C2_FOUNDATIONS.md states: A-PRW2 takes the continuum limit at fixed v and λ.
  This means Δt → 0 in the continuum limit. In the discrete theory, Δt is
  a free parameter of the lattice model. Nothing in C2 fixes Δt to a
  specific value.

**Result: FAILED.**

---

## Route 22: Relation Between h and Another Fixed Quantity

**Premise:** Similarly, if the step size h were fixed, and τ or λ were known,
v = h/Δt might be determined.

**Attempt:**
  h is the lattice step size. In the continuum limit h → 0. No physical
  principle in C2 identifies h with any measurable quantity (it is not the
  qubit spacing, not the Planck length, not any other specific length).

**Result: FAILED.**

---

## Route 23: Boundary Conditions

**Premise:** Could boundary conditions on the substrate field (e.g., at
the chip edges or qubit locations) fix v?

**Attempt:**
  Boundary conditions fix s(x,t) at specific locations — e.g., s = s₀ at the
  chip boundary. These constrain the solution s(x,t) but not the parameter v,
  which enters the equation, not the boundary condition.

**Result: FAILED.**

---

## Route 24: Reparameterization / Symmetry Analysis

**Premise:** If the theory has a reparameterization symmetry v → αv,
this would prove c is unphysical (gauge freedom).

**Test:**
  Consider the transformation v → αv, λ → αλ (keeping τ_B = 1/(2λ) fixed
  requires λ → αλ). Then:
  - ξ_c = v/λ → αv/(αλ) = v/λ = ξ_c   [unchanged]
  - D = v²/(2λ) → α²v²/(2αλ) = αv²/(2λ) = αD   [changes]
  - τ_B = 1/(2λ) → 1/(2αλ)   [changes]

  This is not a symmetry: both D and τ_B change.

  Alternative: v → αv, λ → λ (keeping λ fixed). Then:
  - ξ_c = v/λ → αv/λ = αξ_c   [changes]
  - τ_B = 1/(2λ)   [unchanged]
  - D = v²/(2λ) → α²v²/(2λ) = α²D   [changes]

  Observables that depend only on τ_B (e.g., S_JJ(ω), Γ_φ) are unchanged
  by this transformation. Observables that depend on ξ_c (e.g., C_JJ(r))
  change.

  Therefore: v is NOT a pure gauge freedom. It has physical content in the
  spatial sector. But it cannot be determined from the temporal sector alone.

**Result:** v is a physically meaningful but undetermined parameter.
No reparameterization makes all observables v-independent.

---

## Route 25: Any Relation Between the Decoherence and Gravitational Sectors

**Premise:** C2 aims to unify decoherence and gravity via the substrate.
Could this joint requirement fix v?

**Status:**
  The gravitational sector of C2 is completely undeveloped.
  C2_FOUNDATIONS.md has no gravitational field equations.
  C2_FRONTIER_MAP.md F5/F6 classify gauge group selection and QFT emergence
  as completely open problems with "no known approach from C2 foundations."
  Without gravitational equations, no joint constraint on v exists.

**Result: BLOCKED.** The gravitational sector does not exist in the
current C2 framework.

---

## Summary Table

| Route | Description | Result |
|-------|-------------|--------|
| 1 | Dimensional analysis | FAILED |
| 2 | Normalization of s | FAILED |
| 3 | Conservation laws | FAILED |
| 4 | Equilibrium condition | FAILED |
| 5 | Thermodynamic limit / FPUT | FAILED (identification, not derivation) |
| 6 | Dispersion relation | FAILED |
| 7 | Continuum limit | FAILED |
| 8 | Entropy extremization | FAILED |
| 9 | Detailed balance | FAILED |
| 10 | Stability conditions (Q diagnostic) | FAILED |
| 11 | Causality (upper bound only) | FAILED |
| 12 | Lorentz-like invariance | BLOCKED (unproved) |
| 13 | Coupling to emergent spacetime | BLOCKED (unproved) |
| 14 | Coupling to gravitational sector | BLOCKED (undeveloped) |
| 15 | Coupling to decoherence sector | FAILED |
| 16 | Lattice/UV cutoff | FAILED (needs extra identification) |
| 17 | RG fixed points | FAILED |
| 18 | Self-consistency of PRW | FAILED |
| 19 | Action/Hamiltonian formulation | BLOCKED (no action in C2) |
| 20 | Renormalization/dimensional transmutation | FAILED |
| 21 | Δt fixed by external quantity | FAILED |
| 22 | h fixed by external quantity | FAILED |
| 23 | Boundary conditions | FAILED |
| 24 | Reparameterization symmetry | FAILED (v is physical but undetermined) |
| 25 | Joint decoherence-gravity constraint | BLOCKED (no gravitational equations) |

**Failed:** 19/25
**Blocked (unproved prerequisite):** 5/25 (routes 12, 13, 14, 19, 25)
**Succeeded:** 0/25

---

## Why c Cannot Be Derived: Structural Proof

The failure of all 25 routes has a single underlying cause that can be
stated as a theorem:

**Claim:** v is a structurally free parameter of C2.

**Proof:**
Consider two C2 models M₁ = (v, λ) and M₂ = (αv, λ/α) for any α > 0.

In both models:
  - τ_B = 1/(2λ) for M₁;  τ_B' = α/(2λ) for M₂   [differ]
  - ξ_c = v/λ for M₁;      ξ_c' = αv/(λ/α) = α²v/λ for M₂   [differ]
  - S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²) differs between M₁ and M₂

These models are not observationally equivalent. They predict different τ_B
and different ξ_c. Therefore v is physical — it is not pure gauge.

Now consider M₁ = (v, λ) and M₁' = (αv, λ) (λ fixed, v rescaled):
  - τ_B = 1/(2λ) = τ_B'   [same]
  - S_JJ(ω) same   [same]
  - Γ_φ = k_rot·ω_rot² same   [same, because k_rot does not contain v]
  - ξ_c = v/λ ≠ αv/λ = ξ_c'   [different]

So M₁ and M₁' have identical temporal observables but different spatial
observables. Measuring temporal observables alone cannot distinguish them.
Measuring spatial observables (ξ_c) can, but requires knowing v·λ⁻¹
from data — an empirical measurement.

No equation within C2 prevents M₁ and M₁' from both being valid.
Therefore c = v cannot be derived from the temporal sector of C2, and
can only be constrained by measuring ξ_c, which requires measuring the
spatial correlation scale — which is exactly the failed experimental route.

**GAP-7 is confirmed: c is structurally free. QED.**

---

## Conclusion

All 25 independent derivation routes fail or are blocked.

GAP-7 is not a gap in derivation technique. It is a structural property
of the C2 theory: the theory describes the mathematical consequences of a
substrate with speed v without determining what v is. This is analogous to
how special relativity uses the speed of light c without deriving its value
— except that in special relativity, c is fixed empirically to a universal
constant, while in C2, no universal constant exists to fix v.

**GAP-7 STATUS: CONFIRMED FUNDAMENTAL. NOT RESOLVABLE FROM EXISTING C2.**

The only legitimate routes forward are:
A. External physical identification of the substrate medium (gives c = v_medium)
B. An additional C2 axiom that constrains v (requires new theory — must be
   explicitly documented as NEW AXIOM REQUIRED, not a derivation)
C. Experimental measurement of c = ξ_c/(2τ_B) (empirical, not theoretical)

None of A, B, C are derivations from existing C2.
