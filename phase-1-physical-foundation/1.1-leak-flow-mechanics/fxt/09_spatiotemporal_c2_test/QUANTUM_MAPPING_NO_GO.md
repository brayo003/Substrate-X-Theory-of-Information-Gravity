# QUANTUM MAPPING: NO-GO ANALYSIS
## Is the C2 → Qubit Coupling Uniquely Determined?

**Date:** 2026-08-21

---

## The Three Obstructions (confirmed from existing project document)

The project's `interaction_hamiltonian_uniqueness.md` already establishes these
correctly. They are confirmed here.

### OB-A: No Hilbert Space in the Substrate

The substrate is a classical field theory over real commutative fields {s, J}.
No Hilbert space ℂ² appears anywhere in:

    ∂_t s + ∂_x J = 0
    ∂_t J + c²∂_x s = -(1/τ)J

The qubit Hilbert space must be inserted as external input. There is no functor
from a commutative real algebra to a non-commutative *-algebra that is derivable
from those two equations.

### OB-B: No Preferred Direction in Qubit Space

Even with ℂ² inserted by hand, the coupling direction n ∈ S² (which Pauli operator)
is unconstrained. The substrate fields are real scalars — they carry no information
about the qubit's internal structure.

T-invariance argument: J is T-odd, all σᵢ are T-odd, so J·(n·σ) is T-even for any n.
This selects J-coupling over s-coupling but does NOT select any direction on S².
Furthermore, the substrate itself breaks T (via the -(1/τ)J dissipation), so
imposing T-invariance on H_int while the substrate breaks T is an additional
assumption, not a consequence of the substrate.

Pure-dephasing criterion (which selects n = ẑ → σ_z) is empirical: it matches
the observed T₁ = ∞ in Ramsey experiments. Not derivable from {s, J}.

### OB-C: g Is Not Determined

    [g] = kg·m⁴/s/info

This requires ℏ for its natural scale. ℏ does not appear in the substrate
equations. g is absent from every substrate equation. g is a free parameter
fixed only by empirical calibration.

---

## What IS Uniquely Determined (given H_int accepted)

Once H_int = g J σ_z is accepted as input (not derived), the following are theorems:

- Lindblad operator A = σ_z is unique [HC-3]
- T₁ = ∞, T₂ = 1/Γ [HC-4]
- Γ_φ = (g²/ℏ²) S_JJ(ω=0) [standard Born-Markov-secular]
- S_JJ(ω) = S₀ τ/(1+ω²τ²) — Lorentzian [from telegrapher autocorrelation]
- C_JJ(r) ~ K₀(r/ξ_c) in 2D — [from 2D telegrapher Green's function, conditional]

All five are conditional on H_int being accepted. None is derivable from the
substrate alone.

---

## Additional No-Go Results

**N-Q1:** The PRW state space is the classical simplex Δ₁ = [0,1].
The qubit state space is the Bloch sphere CP¹ ≅ S².
These are not isomorphic. The substrate cannot generate the qubit state space.
[Confirmed: C2_FOUNDATIONS.md, F3, Theorem PRW-IMP-1]

**N-Q2:** Born-Markov validity is marginal.
At τ_B ~ 5 µs (measured) and Γ_φ ~ 50 kHz: τ_B · Γ_φ = 0.25.
The Markovian approximation requires this to be << 1. At 0.25 it is marginal.
The derived Lindblad equation is an approximation, not exact.

**N-Q3:** g cannot be fixed by the substrate (confirmed OB-C above).
Any prediction involving absolute magnitude of decoherence inherits this freedom.

---

## Verdict

The quantum mapping is NOT uniquely determined by the substrate theory.
OB-A, OB-B, and OB-C are each independently sufficient to block derivation.

The strongest available statement is conditional:

    IF [A-lin] + [A-local] + [P-deph] are accepted,
    THEN H_int = g J σ_z is the unique coupling form (up to sign of g).

This is a theorem about the coupling space given three external inputs.
It is not a derivation from the substrate of why those inputs hold.

**The quantum mapping remains: [MODELING ASSUMPTION] + [EMPIRICAL INPUT].**
