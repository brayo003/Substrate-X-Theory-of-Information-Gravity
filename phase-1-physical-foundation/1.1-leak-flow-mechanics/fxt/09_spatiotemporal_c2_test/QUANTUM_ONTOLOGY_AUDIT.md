# QUANTUM ONTOLOGY AUDIT
## Can PRW Variables Be Derived as Observables of a Quantum Microscopic State?

**Date:** 2026-08-22  
**Scope:** Determine whether the PRW variables (n⁺,n⁻,e⁺,e⁻) can be derived as
observables of a quantum microscopic state, and whether such a state supplies a
principled C±. Record hard failures explicitly.  
**Status:** Gate audit — results determine which branch the project is in.

---

## 1. The PRW State Space (Q1)

### Classical description

A single PRW particle carries: direction σ ∈ {+1,−1} and energy ε ∈ ℝ≥0.

The aggregate macroscopic state is the collection of all (σᵢ, εᵢ). The state
of the directional sector at each site is a classical probability distribution:

```
P(σ=+1) = p⁺,  P(σ=−1) = p⁻ = 1-p⁺,  p⁺ ∈ [0,1]
```

State space = probability simplex Δ¹ ⊂ ℝ².

The macroscopic densities: n⁺ = Nρ p⁺/V, n⁻ = Nρ p⁻/V.

### Minimal quantum representation

The minimal quantum system with two states is a qubit: ℋ = ℂ².

| Observable | Operator | Expectation value |
|-----------|---------|-----------------|
| Right-mover fraction | N̂⁺ = \|+⟩⟨+\| = diag(1,0) | ⟨N̂⁺⟩ = ρ₊₊ |
| Left-mover fraction | N̂⁻ = \|−⟩⟨−\| = diag(0,1) | ⟨N̂⁻⟩ = ρ₋₋ |
| Coherence | σ̂₊ = \|+⟩⟨−\| | ⟨σ̂₊⟩ = ρ₋₊ ∈ ℂ |

The PRW observables n⁺, n⁻ correspond exactly to the **diagonal elements**
ρ₊₊, ρ₋₋ of the density matrix. The **off-diagonal element** ρ₊₋ ∈ ℂ is
absent from the PRW ontology.

### What is missing

The Bloch sphere S² is the full quantum state space for a qubit. The
probability simplex Δ¹ is the **equatorial disk** of S² (ρ₊₋ = 0 sector):

```
Full qubit: ρ̂ = ½(I + r⃗·σ⃗),  r⃗ ∈ B³ (Bloch ball)
PRW states:  ρ̂ = diag(p⁺, p⁻)  ↔  r⃗ = (0, 0, p⁺-p⁻)  (z-axis only)
```

The PRW occupies a 1-dimensional subspace of the 3-dimensional Bloch sphere.

**Hard finding Q1:** The PRW state space is the classical-mixture sector of a
qubit — the zero-coherence subspace. It is not a quantum state space.

---

## 2. Superposition and Interference (Q2)

### Test

For the equal-superposition state |ψ⟩ = (|+⟩+|−⟩)/√2 vs the equal mixture
ρ̂_cl = ½|+⟩⟨+| + ½|−⟩⟨−|:

```
Quantum:   P(x-basis) = |⟨x|ψ⟩|² = 1.000   [full constructive interference]
Classical: P(x-basis) = Tr(ρ̂_cl |x⟩⟨x|) = 0.500   [no interference]
```

(verified numerically; gap = 0.500).

### What is required for superposition

A complex field ψ±(x,t) ∈ ℂ such that n⁺ = |ψ⁺|², n⁻ = |ψ⁻|², and a
phase equation for S(x,t) = arg(ψ⁺/ψ⁻).

Neither ψ± nor S appears anywhere in the current master equation.

**Hard finding Q2:** Superposition — NO. The current PRW is restricted to
classical mixtures (diagonal ρ̂). Complex amplitudes and relative phase
are not in the current ontology.

---

## 3. Phase Structure (Q3)

### Madelung decomposition attempt

Write n⁺ = R⁺², n⁻ = R⁻² with R± = √n± ∈ ℝ. Then attempt a complex
amplitude ψ = R·e^{iS}.

The PRW equation for n⁺ becomes:
```
∂ₜR⁺ + c∂ₓR⁺ = -λ(R⁺ - R⁻²/R⁺)/2
```

This is a **real** nonlinear equation for R⁺. No phase S⁺ appears and no
equation for the relative phase Δ = S⁺ − S⁻ can be derived from real equations.

The Madelung decomposition **degenerates**: the imaginary part of any would-be
complex field ψ = √n⁺ · e^{iS} is pure gauge — S does not appear in any
observable and has no equation of motion.

**Hard finding Q3:** Phase structure — NO. The PRW equations are real-valued.
No phase variable S(x,t) exists or can be derived from them. The Madelung
decomposition produces a real equation, not a complex wave equation.

---

## 4. Unitary Sector (Q4)

### Norm conservation

In the source-free PRW: ∂ₜs + ∂ₓJ = 0 → ∫s dx = const.

Total information is conserved — analogous to quantum norm conservation.

### Can the reversible part be written as iℏ∂ₜ|ψ⟩ = H|ψ⟩?

The reversible (τ→∞) limit gives the wave equation:
```
∂ₜs = −∂ₓJ
∂ₜJ = −c²∂ₓs
```

The generator matrix [[0,−∂ₓ],[−c²∂ₓ,0]] is **anti-Hermitian** in real space.
For a Schrödinger equation, the generator must be i×(Hermitian) with a
**complex** state vector.

Complexification attempt: let Ψ = n⁺ + in⁻. The resulting equation for ∂ₜΨ
does not simplify to iHΨ with any Hermitian H. The sign structure of the
n⁺ and n⁻ transport terms is incompatible: n⁺ advects rightward (+c) while
n⁻ advects leftward (−c), preventing a uniform complex-frequency description.

**Hard finding Q4:** No unitary sector proper. Norm is conserved, but:
- The state is real, not complex
- The reversible generator is anti-Hermitian
- The wave equation is not a Schrödinger equation
- Naive complexification fails
- The dissipative 1/τ term breaks unitarity in any case

A wave equation (2nd-order real, hyperbolic) is not the same as the
Schrödinger equation (1st-order complex, parabolic in time).

---

## 5. C± from a Quantum Master Equation (Q5)

### Lindblad framework

The general Markovian open-system master equation:
```
dρ̂/dt = −i[H,ρ̂] + Σₖ γₖ(Lₖ ρ̂ Lₖ† − ½{Lₖ†Lₖ, ρ̂})
```

### Can C± = αe⁺ be derived?

The jump operator L = √α · |+⟩⟨e⁺| on the extended space ℋ = ℂ² ⊗ ℋ_energy
produces the population equation:
```
dρ₊₊/dt += α·⟨e⁺|ρ̂|e⁺⟩ = α·e⁺ = C⁺  ✓
```

This formally represents C± = αe± as a Lindblad jump process.

### What this does NOT accomplish

Choosing the jump operator L = √α·|+⟩⟨e⁺| is **exactly equivalent** to
choosing C± = αe± directly. The Lindblad framework is a quantum language
for the same choice — it does not derive it.

What would derive L (and therefore C±) is a physical interaction Hamiltonian
H_int coupling the information and energy sectors, from which L is obtained
via the system-bath weak-coupling limit (Born-Markov approximation).
H_int is not specified in the current project.

**Hard finding Q5:** The Lindblad framework can represent C± as a jump
process. It does not derive it. Specifying the Lindblad jump operator L
requires the same information as specifying C± directly. The quantum
formulation repackages the underdetermination without resolving it.

---

## 6. Hard Failure Summary (Q6)

### Three arguments for irreducible classicality

**Argument 1 — Simultaneous definite values:**
The PRW assigns each particle a definite σ and a definite ε simultaneously.
In quantum mechanics, σ and phase are complementary. The PRW has no
complementarity and no uncertainty. The PRW variables are commuting
classical observables — equivalent to a fully decoherent qubit.

**Argument 2 — Bloch sphere geometry:**
PRW state (n⁺,n⁻) corresponds to the z-axis of the Bloch sphere (pure
diagonal density matrices). The off-equatorial states — quantum superpositions
— are absent. The PRW cannot violate any Bell inequality.

**Argument 3 — No ℂ anywhere:**
Real quantum mechanics (Stueckelberg 1960) is consistent but cannot reproduce
all bipartite correlations (Renou et al. 2021). Classical probabilities are
weaker still. The inclusion relations are:
```
Classical probabilities ⊂ real QM ⊂ complex QM
```
The PRW is in the leftmost set. Both extensions require adding degrees of
freedom not currently in the ontology.

### Complete property table

| Property | Status | Evidence |
|----------|--------|---------|
| Superposition \|ψ⟩=a\|+⟩+b\|−⟩ | **NO** | n± ∈ ℝ≥0 only; no complex amplitude |
| Off-diagonal coherence ρ₊₋ | **NO** | Absent from all PRW equations |
| Complex phase S(x,t) | **NO** | Madelung decomposes to real equation only |
| Interference \|ψ₁+ψ₂\|² terms | **NO** | No mechanism; numerical gap = 0.5 |
| Unitary evolution iℏ∂ₜ\|ψ⟩=H\|ψ⟩ | **NO** | Generator anti-Hermitian; state real |
| Norm conservation | **YES** | ∂ₜs+∂ₓJ=0 → ∫s dx=const |
| Born rule P=\|ψ\|² | **NO** | n⁺ is density, not \|amplitude\|² |
| ℏ in equations | **ABSENT** | No ℏ anywhere |
| C± from H_int | **NO** | Lindblad repackages the choice; H_int absent |
| Bell inequality violation | **NO** | Classical state; cannot violate |

**Overall verdict: The PRW is irreducibly classical. Branch 1 applies.**

---

## 7. Branch Classification

### Branch 1 — Quantum structure cannot be derived (CURRENT STATUS)

The PRW is a classical substrate. The variables (n⁺,n⁻,e⁺,e⁻) are
classical occupation densities on the probability simplex. No quantum
structure is present or emergent from the current equations.

**Consequences:**
- The project is a classical information-theoretic substrate theory
- It may still produce emergent gravity (classical field theory route)
- It cannot produce quantum mechanics from the current ontology
- Claims of quantum emergence from the current equations are unfounded

### What Branch 2 would require

Branch 2: Quantum structure exists but C± remains underdetermined.

Required additions:
1. Replace n± with complex amplitudes ψ±(x,t) ∈ ℂ
2. Add a phase equation: ∂ₜS = f(ρ, ∂ₓρ, ...) — this is where ℏ would enter
3. Identify a Hilbert space for the information+energy sector jointly
4. Show the PRW transport corresponds to evolution in that Hilbert space
5. C± would then be constrained by the Hamiltonian structure of that space

**Minimum new content for Branch 2:**
A complex field equation of the form:
```
iℏ∂ₜψ = [−ℏ²c²∂ₓₓ/m + V(x,t)]ψ
```
where n = |ψ|² and J = (ℏ/m)Im(ψ*∂ₓψ). This is the Madelung/quantum
hydrodynamics formulation — it EXISTS mathematically, but it requires
introducing ℏ as a new physical constant with no current counterpart in
the PRW.

### What Branch 3 would require

Branch 3: Quantum structure AND interaction derived from first principles.

In addition to Branch 2 requirements:
- H_int derived from the same substrate principles that give the transport
- C± emerging from H_int via Born-Markov or exact diagonalization
- No free parameters not already in the microscopic ontology

This is a substantially harder program. It would require identifying what
physical process at the substrate level corresponds to the energy-information
conversion, and deriving H_int for that process from first principles.

---

## 8. What the Audit Establishes

The following are now established facts about the current project:

1. **The PRW state space is the classical-mixture sector of a qubit.** The off-diagonal coherence is absent. This is a mathematical fact about the current equations, not an interpretive judgment.

2. **Phase structure is absent.** The Madelung decomposition is trivial (real equation, no phase dynamics). There is no analogue of S in the current ontology.

3. **The Lindblad/quantum-master-equation route to C± is circular.** It repackages the underdetermination in quantum language but does not resolve it. A selection principle for C± still requires a physical H_int.

4. **ℏ is absent.** The PRW contains no natural length or action scale analogous to ℏ. Introducing quantum mechanics requires adding ℏ as a new fundamental constant.

5. **Norm is conserved** in the source-free PRW — this is one genuine structural parallel with quantum mechanics, but it is shared with any conservative classical field theory. It is not specifically quantum.

---

## 9. The Genuine Open Question

The audit has established that the **current PRW is classical**. This is a
hard result, not a soft assessment.

The genuine open question — the one worth investigating — is:

> Is there a quantum microscopic substrate of which the PRW variables (n⁺,n⁻)
> are the diagonal moments, and from which a complex coherence field ρ₊₋(x,t)
> naturally emerges with its own dynamics?

If yes: the PRW becomes a COARSE-GRAINED DESCRIPTION of a quantum substrate,
and the project's structure is:
```
quantum microscopic state ρ̂(x,t)
  ↓ (coarse-grain: take diagonal)
PRW variables (n⁺, n⁻, e⁺, e⁻)
  ↓ (hydrodynamic limit)
master equation + C± + source terms
```

In this case, C± would be derived from the off-diagonal dynamics of ρ̂ — the
very component that the PRW currently discards. The information carried by
ρ₊₋(x,t) might be what drives C±.

This is a research direction, not a result. It requires constructing an explicit
quantum substrate and showing the coarse-graining explicitly. That has not been done.
