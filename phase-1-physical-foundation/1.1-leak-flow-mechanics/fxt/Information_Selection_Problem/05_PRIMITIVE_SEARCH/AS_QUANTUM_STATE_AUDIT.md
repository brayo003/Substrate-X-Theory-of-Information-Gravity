# AS_QUANTUM_STATE_AUDIT
## Gate 6 Part III — Asymptotic Safety Quantum State Investigation

**Subject:** Whether asymptotic safety independently defines a quantum cosmological state |Ψ_AS⟩ whose support is restricted to low-Weyl configurations.
**Date:** August 2026

---

## The Question

Gap 3 from NEXT_RESEARCH_GATE.md: Does the AS framework produce an independently derived quantum state — wave functional, boundary condition, vacuum, density matrix, or measure — that selects low-Weyl configurations, independently of any saddle-point structure?

This is distinct from the weighting argument (Outcome B). The weighting arises from the path-integral measure exp(−β∫C²). Gap 3 asks whether there is an additional, independent quantum-state selection beyond the path-integral weight — one that would restrict the support of the state to low-Weyl configurations even if the saddle-point calculation puts Kasner in the physical solution space.

---

## What AS Does and Does Not Provide

### What AS provides:

1. **A renormalization group flow** on the space of effective actions. This is a deterministic flow in theory space: given initial conditions on the couplings at some scale k_0, the FRGE determines the flow to all scales k.

2. **A UV fixed point G*** where the flow terminates. At G*, the theory is scale-invariant — it defines a conformal field theory of gravity (in theory space).

3. **A renormalized trajectory** from G* to the IR. This trajectory fixes the physical values of all couplings (G_phys, Λ_phys, β_phys, ...) as functions of the measured low-energy values.

4. **An effective average action Γ_k** at each scale k. This encodes all quantum corrections at and below scale k. At k → 0, Γ_0 is the full quantum effective action.

5. **The path integral** Z = ∫Dg exp(−Γ_0[g]) in the Euclidean version, or the transition amplitude ⟨g_f|g_i⟩ = ∫Dg exp(iS_AS[g]) in Lorentzian version.

### What AS does NOT provide:

1. **A boundary condition for the path integral.** The path integral Z = ∫Dg exp(−Γ_0[g]) sums over all geometries. It does not specify the initial or final boundary conditions. The sum is over all g_{μν}, including Kasner, FLRW, Schwarzschild, and everything else.

2. **A wave functional of the universe.** The Hartle-Hawking wave function Ψ[h_ij] = ∫Dg exp(−S_E[g]) specifies boundary conditions (no past boundary). AS does not produce an analogous construction. AS modifies S_E[g] → Γ_0[g] but does not specify the boundary conditions for the integral.

3. **A vacuum state.** In QFT, the vacuum state is defined by the path integral with specific boundary conditions (Euclidean time rotation + vacuum boundary conditions). In quantum gravity, there is no established analog because diffeomorphism invariance removes the preferred time direction needed to define "vacuum."

4. **An initial density matrix.** AS does not derive ρ_0 = (initial state of the universe). The initial state question is not addressed by the RG flow — the RG flow describes the theory (the action), not the state.

5. **A measure on initial conditions.** The path integral provides a measure on field histories, not on initial data. To get a measure on (h_ij, K_ij), one must restrict the path integral to a Cauchy surface — which requires specifying boundary conditions (the no-boundary problem again).

---

## Literature Survey for AS Quantum State

### Bonanno-Reuter (2002) — "Renormalization group improved Schwarzschild black holes"

This paper applies AS to BH physics by substituting the RG-improved G(r) into the Schwarzschild metric. It produces a de Sitter core near the singularity. This is not a quantum state for cosmology — it is a semiclassical substitution.

**Does it define a state?** No. It substitutes a running coupling into a classical solution.

### Bonanno-Reuter (2002) — "Cosmology of the Planck era from a renormalization group for quantum gravity"

Phys.Rev.D 65, 043508. This applies AS-improved cosmology by substituting G(k) and Λ(k) evaluated at k ~ 1/t (the natural RG scale for a Friedmann universe) into the Friedmann equations. This produces a modified early-universe evolution that avoids the big bang singularity.

**Does it define a quantum state?** No. It produces modified Friedmann equations — a semiclassical running-coupling cosmology. The initial state is not specified; the Friedmann equations still require initial conditions.

**Does it select low-Weyl initial conditions?** No. It modifies the FLRW evolution; it does not address whether FLRW or Kasner initial conditions are selected.

### Platania (2020) — "Constraints on the inflationary era from the trans-Planckian censorship conjecture"

Universe 6, 159. Applies AS to inflationary cosmology, deriving a UV cutoff on modes. This is a constraint on the inflationary spectrum, not a selection of initial conditions.

**Does it define a state?** No.

### Platania-Wetterich (2019) — "Non-perturbative unitarity and fictitious ghosts in quantum gravity"

Phys.Lett.B 811, 135852. Studies the ghost problem in AS. Does not address the initial-state question.

### Wetterich (2019, 2020) — "Quantum scale symmetry"

Studies cosmological implications of AS and scale symmetry. Proposes that the universe near the AS fixed point is approximately scale invariant, which constrains the spectrum of fluctuations. However, the initial state selection is not addressed.

### Reuter-Saueressig (2011) — "Fractal spacetime structure in asymptotic safety"

Ann.Phys. 525, 414. Studies spectral dimension reduction at the AS fixed point. No quantum state selection.

### Falls et al. (2020, 2021) — "Asymptotic safety and the cosmological constant"

Phys.Rev.D 102, 044025. Studies Λ in AS. No state selection.

---

## The Fundamental Obstacle

Asymptotic safety is a theory of the *gravitational action* — it fixes the form of Γ_0[g] by requiring that the theory flows from a UV fixed point. It does not and cannot specify what *state* the universe is in.

The distinction is:
- The **action** (or Hamiltonian) describes the dynamics: how the system evolves.
- The **state** (or initial conditions) describes where the system starts.

AS fixes the action. R1 asks about the state. These are orthogonal questions.

An analogy: the Standard Model Lagrangian is fixed by gauge symmetry and renormalizability. This does not tell us what the initial state of the early universe was. The initial state requires additional input (inflation, no-boundary, etc.). AS is in the same position as the SM — it fixes the theory, not the state.

**Gap 3 is not merely unresolved — it identifies a category error in P01's proposed mechanism.** AS is a theory of quantum gravity dynamics. It cannot, in principle, determine the initial state without additional ingredients beyond the RG flow.

---

## Is There Any AS Mechanism That Could Select a State?

One possibility: if the AS fixed point is a conformal fixed point (scale invariant), and if the scale-invariant vacuum of the theory is unique, then the "natural" state of the universe near the fixed point is the scale-invariant vacuum. This vacuum might have specific properties.

**Does this work?**

The AS fixed point is a UV fixed point in theory space. It is analogous to the Gaussian fixed point of a free field theory or the Wilson-Fisher fixed point in condensed matter. At the fixed point, the theory has a specific symmetry (approximate scale invariance). The "vacuum" of a scale-invariant field theory is the conformal vacuum — a specific quantum state with specific correlation functions.

However:
1. The conformal vacuum of gravity near the AS fixed point has not been constructed explicitly.
2. Even if constructed, it is a state of the quantum gravity theory at scale k ~ M_Planck, not a state at scale k → 0. The RG running from k ~ M_Planck to k → 0 changes the state.
3. The conformal vacuum at the fixed point does not have zero Weyl curvature — scale-invariant theories of gravity have non-trivial two-point functions of the Weyl tensor.

This route does not produce a low-Weyl quantum state.

---

## Verdict for Gap 3

**Gap 3 is closed — against P01.**

Asymptotic safety does not provide, and cannot in principle provide (without additional non-AS ingredients), a quantum cosmological state with restricted support on low-Weyl configurations. AS fixes the action; state selection requires independent input. No AS-based state selection principle exists in the current literature. The category separation between "theory" (AS) and "state" (initial conditions) is fundamental, not technical.

---

*Document status: AS QUANTUM STATE AUDIT COMPLETE*
*Gap 3: Closed against P01 — AS fixes the action, not the state.*
*No quantum state selection mechanism exists within AS.*
*Date: August 2026*
