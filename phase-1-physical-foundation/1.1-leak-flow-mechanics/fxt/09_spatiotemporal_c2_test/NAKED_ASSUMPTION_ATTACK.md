# NAKED ASSUMPTION ATTACK
## Adversarial Audit of Every Load-Bearing Assumption in the C2 → Quantum Mapping

**Date:** 2026-08-21
**Standard:** Adversarial. Every assumption is attacked until it either collapses to a
theorem or is confirmed as irreducible external input. No assumption survives by being
"physically natural." No result survives by being "consistent with."

---

## ATTACK A — Can c = v_s be derived without [THERM]?

### A.1 The actual FPUT dynamics

The harmonic FPUT chain is Liouville-integrable. Mode actions nₖ = |Aₖ|² are EXACT
constants of motion. This is not approximate; it is exact for the harmonic chain.

Consequence: the action spectrum {nₖ} is set entirely by initial conditions and never
changes. Any action spectrum — flat, peaked at high-k, delta-concentrated at a single
mode, or arbitrary — is a valid solution of the FPUT dynamics.

### A.2 Explicit counterexample: c_eff ≠ v_s

Let the initial state concentrate ALL action at the zone boundary k = N/2:

    nₖ = A · δ(k - N/2)

Then v_g(N/2) = v_s · cos(π/2) = 0.

The action-weighted effective speed is:

    c_eff = Σₖ nₖ |v_g(k)| / Σₖ nₖ = 0

This is a valid harmonic FPUT state. It satisfies all six admissibility constraints C1–C6
(actions are conserved, signal speed 0 ≤ v_s, positivity holds, etc.).

Under this initial condition, the PRW coarse-grained speed is c_eff = 0, not v_s.

A second counterexample: concentrate action at k = N/4:

    nₖ = A · δ(k - N/4)   →   c_eff = v_s · cos(π/4) = v_s/√2

A third counterexample: flat spectrum nₖ = const:

    c_eff = v_s · (1/N) Σₖ cos(πk/N) → v_s · (2/π) ≈ 0.637 v_s
    (continuum integral: (1/π)∫₀^π cos u du = 0)
    Actually: (1/π)∫₀^π cos u du = [sin u]₀^π / π = 0
    So c_eff = 0 for a flat spectrum (symmetric cancellation)

Wait — the relevant quantity is |v_g(k)|, not v_g(k):

    c_eff = Σₖ nₖ |v_g(k)| / Σₖ nₖ

For k ∈ (0, N/2): v_g(k) > 0. For k ∈ (N/2, N): v_g(k) < 0 but same magnitude by
the symmetry ωₖ = ω_{N-k}. The n+ and n- densities already account for sign via the
right/left split. The effective speed entering the telegrapher equation is:

    c_eff = [Σ_{k: v_g(k)>0} nₖ v_g(k)] / [Σ_{k: v_g(k)>0} nₖ]
           = v_s · [Σ_{k=1}^{N/2} nₖ cos(πk/N)] / [Σ_{k=1}^{N/2} nₖ]

For the flat spectrum nₖ = const:

    c_eff = v_s · (2/N) Σ_{k=1}^{N/2} cos(πk/N)
           → v_s · (1/π) ∫₀^{π/2} cos u · 2 du   ... no, u = πk/N, dk/du = N/π
           = v_s · (2/π) ∫₀^{π/2} cos u du = v_s · (2/π) · 1 = (2/π) v_s ≈ 0.637 v_s

So a flat action spectrum gives c_eff = (2/π)v_s ≈ 0.637 v_s, NOT v_s.

### A.3 RESULT: NO-GO THEOREM for c = v_s without spectral condition

**Theorem (Attack A):** For the harmonic FPUT chain, c_eff is NOT uniquely determined
by the microscopic dynamics. It depends on the initial action spectrum {nₖ}.
Specifically:

    c_eff = v_s · [∫₀^{π/2} nₖ(u) cos(u) du] / [∫₀^{π/2} nₖ(u) du]

where nₖ(u) is the action spectral density at u = πk/N.

This quantity ranges continuously over (0, v_s] depending on the spectrum:
- Delta-function at k=0: c_eff = v_s (maximum)
- Delta-function at k=N/2: c_eff = 0 (minimum, zero-speed)
- Flat spectrum: c_eff = (2/π)v_s ≈ 0.637 v_s
- Thermal (classical): c_eff = v_s (infrared-divergent, see below)
- Any fixed k₀ ∈ (0,N/2): c_eff = v_s cos(πk₀/N) ∈ (0, v_s)

The substrate dynamics (nₖ = const) NEVER CHANGE c_eff. The initial spectrum fixes
c_eff for all time. c = v_s is NOT a theorem of the substrate dynamics.

### A.4 When does c_eff = v_s hold exactly?

Only when the action spectrum diverges at k=0 faster than any power, specifically when:

    ∫₀^ε nₖ(u) du / ∫₀^{π/2} nₖ(u) du → 1 as ε → 0

This requires infinite infrared weight — either a 1/k singularity (classical thermal
nₖ ∝ 1/ωₖ ∝ 1/sin(πk/N) ≈ N/(πk) → ∞) or stronger.

Classical thermal equilibrium does produce this singularity (see prior analysis).
But thermal equilibrium is NOT derived from harmonic FPUT dynamics —
it is an external preparation condition [THERM].

**CONFIRMED: c = v_s requires [THERM] or an equivalent spectral concentration
assumption. It is not derivable from FPUT dynamics alone.**

**Classification: [THERM] is irreducible. It cannot be removed. c = v_s is
CONDITIONAL ON [THERM]. Without [THERM], c is a free parameter in (0, v_s].**

---

## ATTACK B — Is the single-speed PRW a legitimate reduction?

### B.1 The velocity distribution problem

The FPUT acoustic branch has a continuum of group velocities:

    v_g(k) = v_s cos(πk/N),   k ∈ [0, N/2]

The standard PRW construction collapses this to a single walker speed c. This is a
moment-closure approximation, not an exact reduction.

### B.2 The moment hierarchy

Define the n-th moment of the action-weighted velocity distribution:

    M_n = Σₖ nₖ |v_g(k)|ⁿ / Σₖ nₖ = v_sⁿ · <cos^n(πk/N)>_nₖ

The exact transport equation for the action density s(x,t) requires ALL moments.

For a distribution of walkers with different speeds vⱼ and weights wⱼ:

    ∂s/∂t + ∂J/∂x = 0
    ∂J/∂t + c²_eff ∂s/∂x = -(1/τ)J + CORRECTION TERMS

The correction terms involve M_2, M_3, ... and DO NOT vanish unless the distribution
is a delta function (single speed). The telegrapher equation is exact ONLY for a
genuine single-speed PRW.

### B.3 What the moment hierarchy gives for FPUT

For the flat spectrum (counterexample):

    M_1 = (2/π)v_s            (first moment — sets c_eff)
    M_2 = (1/2)v_s²           (second moment — sets diffusivity correction)
    c²_eff = M_1² = (4/π²)v_s² ≈ 0.405 v_s²
    M_2 - c²_eff = (1/2 - 4/π²)v_s² ≈ 0.095 v_s²    (nonzero residual!)

The residual M_2 - c²_eff represents higher-moment corrections that are DROPPED when
the velocity distribution is collapsed to a single speed. The telegrapher equation
with a single c_eff is NOT exact for a multi-speed initial spectrum.

### B.4 The correct transport equation for FPUT

The exact coarse-grained dynamics of the FPUT action density with a nontrivial
velocity distribution is a GENERALIZED TELEGRAPHER EQUATION or a kinetic equation:

    ∂f(x,v,t)/∂t + v ∂f(x,v,t)/∂x = -γ f(x,v,t) + γ n(x,t) w(v)

where f(x,v,t) is the action density at position x moving at speed v, n(x,t) is the
total density, and w(v) = weight function from the mode distribution.

This reduces to the standard telegrapher ONLY when w(v) = δ(v - c) (single speed).

For FPUT with arbitrary {nₖ}, w(v) is determined by the action spectrum and is NOT
a delta function except for infrared-concentrated spectra.

### B.5 RESULT

**The passage from FPUT with dispersion → single-speed PRW is NOT an exact reduction.**

It is a phenomenological closure that:
(a) requires the velocity distribution to be infrared-concentrated (c_eff → v_s)
(b) drops all velocity-moment corrections beyond M_1
(c) is equivalent to a long-wavelength / low-temperature approximation

**Classification: The single-speed PRW is a [MODELING ASSUMPTION] that is justified
only under [THERM] or an equivalent spectral concentration condition.**

---

## ATTACK C — What uniqueness survives for H_int?

### C.1 The general coupling

The most general local linear coupling between substrate fields {s, J} and a qubit is:

    H_int = [a·s(x_q,t) + b·J(x_q,t) + c_d·∂_t J(x_q,t) + d·∂_x J(x_q,t) + ...]
            · [n₁σ_x + n₂σ_y + n₃σ_z]

where (a, b, c_d, d, ...) ∈ ℝ are arbitrary real coefficients and (n₁,n₂,n₃) ∈ S² is
an arbitrary direction on the Bloch sphere.

Subject to: Hermitian (satisfied for any real coefficients and any nᵢσᵢ combination),
dimensional consistency (fixed by appropriate units of each coefficient), locality.

### C.2 What the substrate symmetries constrain

Time-reversal T:
- s: T-even, J: T-odd (derived from PRW definitions)
- All Pauli operators σᵢ: T-odd (standard QM)

A T-invariant H_int satisfies T H_int T⁻¹ = H_int. This requires:
- T-odd × T-odd = T-even: J coupling to any σᵢ → T-even ✓
- T-even × T-odd = T-odd: s coupling to any σᵢ → T-odd ✗ (violates T-invariance)
- T-odd × T-odd = T-even: ∂_t J coupling to any σᵢ → T-even ✓
- T-even × T-odd = T-odd: ∂_x J coupling to any σᵢ → T-odd
  (∂_x is spatial, T-even; J is T-odd; so ∂_x J is T-odd × T-even = T-odd → T-odd ✓)

Result: T-invariance eliminates s-couplings but leaves J-couplings (and ∂_t J, etc.).

Parity P (x → -x):
- s: P-even. J: P-odd.

These constraints together select J-type couplings IF both T and P are imposed.
But: neither T nor P invariance of H_int is derivable from the substrate equations.
The telegrapher equation has a dissipative term -(1/τ)J which is T-odd and P-odd.
The substrate itself breaks both T and P.

**Imposing T or P invariance on H_int while the substrate breaks T and P is
an additional inconsistency that requires explicit justification.**

### C.3 The surviving family after ALL stated constraints

After applying: Hermiticity + locality + dimensional consistency + linearity in fields:

    H_int = g · J(x_q,t) · (n·σ)    for any n ∈ S²,  any g ∈ ℝ\{0}

This is a 3-parameter family (S² × ℝ). The direction n is unconstrained by the
substrate theory. The project's existing uniqueness document confirms this.

After adding pure-dephasing criterion [P-deph] (phenomenological, not derived):
    n = ẑ,   H_int = g J σ_z   (unique up to sign of g)

### C.4 The T-invariance loophole

The project uses T-invariance to select J over s. But:
- The substrate breaks T (due to the J/τ dissipation term)
- Imposing T on H_int while the substrate is T-breaking is inconsistent UNLESS the
  qubit is treated as a T-invariant subsystem coupled to a T-breaking bath

This is a coherent physical setup (T-breaking is in the bath, not the system
Hamiltonian), and it IS standard in open quantum systems. But it requires stating
explicitly that H_int is required to be T-invariant independently of the bath dynamics.
That is an additional assumption not present in the substrate equations.

### C.5 RESULT

**No uniqueness theorem for H_int exists within the substrate theory.**

The coupling form J σ_z requires three external inputs:
1. Linearity in J [modeling assumption]
2. Pure dephasing / σ_z selection [phenomenological, from experiment]
3. The value of g [empirically determined]

None of these is derivable from {s, J, ∂_t s, ∂_x J, τ, c}.

**Classification: H_int = g J σ_z is [MODELING ASSUMPTION] + [EMPIRICAL INPUT].
It is not a theorem of the substrate theory.**

---

## ATTACK D — Can g be derived?

### D.1 Dimensional analysis

    [g] = J·m²·s/info = kg·m⁴/s / info

The substrate parameters: {v [m/s], λ [s⁻¹], s₀ [info/m³], a [m], K [N/m], m [kg]}

No combination of these produces kg·m⁴/s / info. The unit "info" is itself
dimensionless (information is dimensionless in natural units). So:

    [g] = kg·m⁴/s = J·m²·s = ℏ · (m²/info_natural_unit)

This requires ℏ (quantum of action), which is NOT in the substrate theory.

### D.2 Energy scale matching

The substrate has no energy scale at the quantum level. The FPUT chain energy is:
    E_k = ωₖ nₖ    (mode energy in action units)

To connect to qubit energy splitting ℏω_q, one needs a conversion factor between
"action units" (info) and "energy units" (J). This conversion is g itself.

### D.3 RESULT

**g is an irreducible free parameter. It encodes the quantum-classical interface and
has no derivation from the substrate transport equations.**

Any prediction involving k_rot = 8g²s₀²r_q²τ/3ℏ² inherits this freedom.
No C2 prediction involving the magnitude of decoherence is parameter-free.

**Classification: g is [EMPIRICAL INPUT] — irreducible.**

---

## ATTACK E — Does K₀ survive the full assumption audit?

### E.1 Assumptions required for C_Γ(r) = K₀(r/ξ_c)

The derivation in 02_2D_CORRELATION_DERIVATION.md uses the following, classified here:

| Assumption | Type | Required for K₀? |
|-----------|------|-----------------|
| 2D geometry (qubits in a plane) | [MODELING ASSUMPTION] | YES — 1D gives exp, 3D gives exp with power |
| Isotropic PRW (equal speeds ±x, ±y) | [MODELING ASSUMPTION] | YES — anisotropy breaks rotational symmetry, K₀ → directional |
| Single-speed PRW (c = const) | [MODELING ASSUMPTION] see Attack B | YES — multi-speed gives different Green's function |
| Stationary correlator (ω=0 limit) | [MODELING ASSUMPTION] | YES — finite ω gives different functional form |
| Infinite 2D domain (no boundaries) | [MODELING ASSUMPTION] | YES — finite chip with edges needs Neumann/Dirichlet corrections |
| Longitudinal coupling (J_∥ not J_⊥) | [ASSUMPTION] labeled in file | YES — transverse gives K₀ asymptotically but different prefactor |
| c > 0 (positive propagation speed) | Derived from nₖ > 0 | YES — needed for mass gap |
| λ > 0 (positive reversal rate) | Substrate definition | YES — needed for mass gap, K₀ vs. log |
| H_int = g J σ_z (coupling form) | [MODELING ASSUMPTION] | YES — K₀ is the correlator of J, so coupling to J is needed |

### E.2 Can a generic bath reproduce K₀?

YES. Any 2D stationary Gaussian random field with power spectrum S(k) ∝ 1/(k² + m²)
produces the K₀(mr) spatial correlator. This is a generic Yukawa-screened 2D field.

Concrete null model: Take a 2D Ornstein-Uhlenbeck field ψ(x,y,t) satisfying:

    τ ∂ψ/∂t = D∇²ψ - ψ + noise

This is a scalar field. Its equal-time spatial correlator is:

    <ψ(r)ψ(0)> ∝ K₀(r/ξ)    where ξ = √(Dτ)

This is K₀ — without any PRW, without any FPUT, without any c. The Yukawa
propagator is the Green's function of the screened Laplacian (-∇² + m²), which
appears in ANY scalar field theory with a mass gap in 2D.

**K₀(r/ξ_c) is NOT a unique C2 signature. It is the generic 2D spatial
correlator of any massive scalar field theory.**

### E.3 What K₀ does NOT discriminate

The null model (2D OU scalar field) can reproduce K₀ with ONE free parameter ξ.
C2 predicts the SAME K₀ with ξ_c = 2cτ_B. There is no K₀ shape test that can
distinguish C2 from the null model — only the NUMERICAL VALUE of ξ_c from
independently measured c and τ_B could distinguish them.

But c and τ_B are not jointly predicted without [THERM] + [PHON]. So:

**K₀ as a functional form is NOT C2-specific.**
**K₀ with a numerically fixed ξ_c WOULD be C2-specific, but requires [THERM] + [PHON].**

### E.4 RESULT

**K₀ is not a genuine discriminator at the level of functional form.**
**It becomes a discriminator only if ξ_c = 2cτ_B is independently fixed.**
**Since c requires [THERM] + [PHON] (external conditions), the discriminability
is CONDITIONAL, not substrate-derived.**

---

## Summary: The Full Assumption Register

| Assumption | Label | Derivable? | Removable? |
|-----------|-------|-----------|-----------|
| FPUT Hamiltonian is the substrate | [A-FPUT] | NO — postulate | NO |
| Admissibility constraints C1–C6 | [A-C] | NO — design choice | NO |
| c = v_s (PRW speed = sound speed) | [THERM]+[PHON] | NO — requires initial state | NO |
| Single-speed PRW | [CLOSURE] | NO — moment approximation | YES if multi-speed used |
| 2D geometry for K₀ | [GEOM-2D] | NO — hardware choice | YES |
| Isotropic PRW | [ISO] | NO — 4-direction assumption | YES |
| H_int linear in J | [A-lin] | NO — minimal coupling postulate | NO |
| H_int = g J σ_z | [P-deph]+[A-lin] | NO — empirical+postulate | NO |
| Born-Markov-secular approximations | [A-HC1-3] | Partially (weak coupling) | NO |
| g value | [EMPIRICAL] | NO — fit only | NO |
| Longitudinal coupling | [A-long] | NO — explicit assumption | YES |
| Thermal equilibrium of substrate | [THERM] | NO — integrable chain | NO |

Every load-bearing assumption between FPUT and the quantum prediction is
either a modeling assumption, an empirical input, or a physical identification
that requires external data.

**None of them can be removed by mathematics alone.**
