# QUANTUM PARENT DERIVATION
## Q7: Minimal Quantum Parent Whose Coarse-Grained Limit Is the PRW

**Date:** 2026-08-22  
**Question:** Does there exist a minimal quantum microscopic theory whose classical
coarse-grained limit is the PRW, and does it supply a principled C±?  
**Method:** Construct explicitly. Derive exactly. Classify outcome against three
possible verdicts: failure / partial success / strong success.

---

## Q7a — Minimal Hilbert Space and Hamiltonian

### State space

The PRW has two microscopic degrees of freedom per particle: direction σ ∈ {+,−}
and energy ε ∈ ℝ≥0. The minimal quantum representation uses:

```
H_dir = ℂ²            basis: |+⟩, |−⟩
H_E   = ℂ²            basis: |e₀⟩, |e₁⟩  (two energy levels, ε₁ > ε₀)
H     = H_dir ⊗ H_E = ℂ⁴
```

Four-state basis: {|+,e₀⟩, |+,e₁⟩, |−,e₀⟩, |−,e₁⟩}.

### Observable operators

| Operator | Matrix | Expectation value |
|----------|--------|-----------------|
| N̂⁺ | \|+⟩⟨+\| ⊗ I = diag(1,1,0,0) | n⁺/N = ρ₊₀,₊₀ + ρ₊₁,₊₁ |
| N̂⁻ | \|−⟩⟨−\| ⊗ I = diag(0,0,1,1) | n⁻/N = ρ₋₀,₋₀ + ρ₋₁,₋₁ |
| Ê⁺ | \|+⟩⟨+\| ⊗ Ĥ_E | e⁺/N = ε₀ρ₊₀,₊₀ + ε₁ρ₊₁,₊₁ |
| Ê⁻ | \|−⟩⟨−\| ⊗ Ĥ_E | e⁻/N = ε₀ρ₋₀,₋₀ + ε₁ρ₋₁,₋₁ |

### Density matrix block structure

Writing ρ̂ in the dir⊗energy block form:

```
ρ̂ = [[ ρ₊₊   χ  ],    ρ₊₊, ρ₋₋ ∈ ℂ²ˣ²: population matrices
      [ χ†    ρ₋₋]]   χ = ρ₊₋ ∈ ℂ²ˣ²: directional coherence block
```

The PRW variables correspond to: n⁺/N = Tr_E(ρ₊₊), n⁻/N = Tr_E(ρ₋₋).

**The off-diagonal block χ is absent from the PRW. This is what the PRW discards.**

### Most general symmetry-compatible Hamiltonian

Requirements: Hermitian; ±-permutation symmetry (H₊₊ = H₋₋); locality.

```
H = I_dir ⊗ Ĥ_E  +  σˣ ⊗ H₊₋
```

where:
- `I_dir ⊗ Ĥ_E = diag(ε₀, ε₁, ε₀, ε₁)` — free energy evolution
- `σˣ = [[0,1],[1,0]]` — X-Pauli in direction space
- `H₊₋` — a general Hermitian 2×2 matrix in energy space (forced Hermitian by ±-symmetry)

```
H₊₋ = [[a,    g  ],    a,b ∈ ℝ,  g ∈ ℂ
        [g*,   b  ]]
```

Physical interpretation of H₊₋:
- a: direction flip without energy change (→ PRW reversal at energy level e₀)
- b: direction flip without energy change (→ PRW reversal at energy level e₁)
- g: direction flip **with** energy exchange e₀↔e₁ ← **the interaction term**

The Jaynes-Cummings case `a=b=0, g≠0` is the minimal H_int that couples direction
and energy.

Adding spatial transport:
```
H_transport = −iℏc σᶻ ⊗ I_E ∂ₓ
```

This generates rightward (+) and leftward (−) propagation at speed c.

---

## Q7b — Exact Population Equations

### Von Neumann equation

```
iℏ ∂ₜρ̂ = [H, ρ̂]
```

(No dissipation first. Dissipation added below as a physical input where justified.)

### Block equations

Writing `[H, ρ̂]` in the 2×2 block structure:

```
[H,ρ̂]₊₊ = [Ĥ_E, ρ₊₊] + H₊₋χ† − χH₊₋
[H,ρ̂]₊₋ = [Ĥ_E, χ] + H₊₋ρ₋₋ − ρ₊₊H₊₋
[H,ρ̂]₋₋ = [Ĥ_E, ρ₋₋] + H₊₋χ − χ†H₊₋
```

### Population equation for n⁺

Taking Tr_E of the ++ block:

```
iℏ ∂ₜ Tr_E(ρ₊₊) = Tr_E([Ĥ_E, ρ₊₊]) + Tr_E(H₊₋χ† − χH₊₋)
```

The first term vanishes by the cyclic property of the trace: Tr([A,B]) = 0.

```
iℏ ∂ₜ n⁺ = (N/V) Tr_E(H₊₋χ† − χH₊₋)
           = (N/V) · 2i Im(Tr_E(H₊₋ χ†))
```

**Exact result (no approximation):**

```
∂ₜ n⁺ = (2N/ℏV) · Im(Tr_E(H₊₋ χ†))
```

**Interpretation:** Population changes if and only if χ ≠ 0 AND H₊₋ ≠ 0.  
In the classical PRW limit χ = 0: the source term vanishes exactly.  
The PRW source term αE arises from non-zero quantum coherence.

---

## Q7c — Coherence Elimination and the Form of C±_eff

### Coherence equation (exact)

From the off-diagonal block:

```
iℏ ∂ₜ χ = [Ĥ_E, χ] + H₊₋ · ΔN
```

where ΔN = ρ₋₋ − ρ₊₊ (population difference matrix).

For the JC case (a=b=0, H₊₋ = [[0,g],[g*,0]]), the relevant off-diagonal component χ₀₁:

```
iℏ ∂ₜ χ₀₁ = −Δε χ₀₁ + g · ΔN₁₁
```

where Δε = ε₁ − ε₀ > 0 and ΔN₁₁ = (n⁻_high − n⁺_high)/N.

### Exact C±_eff formula

Expanding `Im(Tr_E(H₊₋ χ†))` symbolically (verified with SymPy):

```
C⁺_eff = (4N/ℏV) · Im(g* χ₀₁)
        = (4N/ℏV) · (g_r Im(χ₀₁) − g_i Re(χ₀₁))
```

where g = g_r + ig_i. This is non-zero when g ≠ 0 and χ₀₁ is complex.

### Formal solution for χ₀₁

```
χ₀₁(t) = χ₀₁(0) e^{−iΔεt/ℏ}  −  (ig/ℏ) ∫₀ᵗ e^{−iΔε(t−t')/ℏ} ΔN₁₁(t') dt'
```

### Substituting into C⁺_eff

```
C⁺_eff(t) = (4N/ℏV) Im(g* χ₀₁(0) e^{−iΔεt/ℏ})          [transient]
           + (4N|g|²/ℏ²V) ∫₀ᵗ sin(Δε(t−t')/ℏ) ΔN₁₁(t') dt'  [memory]
```

### Memory kernel

```
K(τ) = (4N|g|²/ℏ²V) sin(Δε τ/ℏ)
```

Oscillates at the Bohr frequency Δε/ℏ. Does not decay (unitary dynamics).

### Markovian limit

When the Bohr oscillation is fast relative to the population dynamics (Δε >> ℏ/τ_pop), the Sokhotski-Plemelj theorem gives:

```
∫₀ᵗ sin(Δε(t−t')/ℏ) ΔN₁₁(t') dt'  →  (πℏ/Δε) ΔN₁₁(t)
```

So in the Markovian limit:

```
C⁺_eff  →  C_Markov · ΔN₁₁
         = C_Markov · (n⁻_high − n⁺_high) / N
```

where `C_Markov = 4N|g|²π/(ℏΔε V)`.

---

## Q7d — Classification

### What emerged

The quantum parent **does** generate a source term in the population equation. The source has the exact form:

```
C⁺_eff = (4N/ℏV) Im(g* χ₀₁)
```

In the Markovian limit this becomes:

```
C⁺_eff ∝ ΔN₁₁ = (n⁻_high − n⁺_high)
```

**This is a population inversion in the high-energy directional state.**  
It is NOT proportional to E = e⁺ + e⁻.

### Comparison with the PRW master equation

The PRW master equation needs: `C⁺ ∝ αE = α(e⁺ + e⁻)`

The quantum parent gives: `C⁺_eff ∝ (n⁻_high − n⁺_high)`

These are structurally different:

| Property | PRW requirement | Quantum parent result |
|---------|----------------|----------------------|
| Sign | Always positive (C⁺ ≥ 0) | Can be negative (population inversion can go either way) |
| Dependence on E | Linear in total energy | Linear in population difference ΔN₁₁ |
| Directionality | Symmetric C⁺ = αe⁺ = αe⁻ | Asymmetric: ΔN₁₁ = n⁻_high − n⁺_high |
| Memory | Instantaneous (Markovian by assumption) | Memory kernel K(τ) = A·sin(Δε τ/ℏ) |

### Verdict: PARTIAL SUCCESS

**What the quantum parent achieves:**

1. ✓ PRW populations (n⁺, n⁻) emerge as coarse-grained diagonal moments of ρ̂
2. ✓ The source term in ∂ₜn⁺ is NOT free — it is determined by H_int and χ
3. ✓ C±_eff is derived from the coherence dynamics, not stipulated
4. ✓ The PRW classical limit (χ=0) gives C±=0 exactly — classicality is recovered
5. ✓ ℏ enters the microscopic level and can be suppressed in the classical limit
6. ✓ Memory terms appear naturally from the quantum dynamics

**What the quantum parent does NOT achieve:**

1. ✗ C⁺_eff ∝ ΔN₁₁, not ∝ αE — wrong functional form for the existing master equation
2. ✗ The positivity C⁺ ≥ 0 is not guaranteed: ΔN₁₁ can be negative (if n⁺_high > n⁻_high)
3. ✗ H_int = g (the coupling constant) is still a free parameter — not derived from ontology

### Classification

```
OUTCOME: PARTIAL SUCCESS (Branch 2)
```

A quantum parent exists and the PRW emerges as its decoherent classical limit.
The source term C± emerges from coherence dynamics rather than being freely stipulated.

However, the functional form of C±_eff is not αE. It is ΔN₁₁ — a population
inversion in the energy-direction sector. The two are related but not identical:
- αE requires: energy density drives creation regardless of direction asymmetry
- ΔN₁₁ requires: directional imbalance in the high-energy state drives creation

They coincide only if n⁻_high >> n⁺_high (strong population inversion in one direction),
which is a special case, not the general case.

---

## What H_int Is Required

For C⁺_eff = αE exactly, the quantum parent would need a source proportional to
the total high-energy population (not the difference):

```
C⁺_eff ∝ ρ₋₋,₁₁ + ρ₊₊,₁₁  (total high-energy population)
```

rather than the difference. This would require a **non-unitary** (dissipative)
jump process — specifically a Lindblad jump that creates information from energy
without requiring population inversion:

```
L_creation = √α |+,e₀⟩⟨+,e₁|   (right-mover drops from e₁ to e₀, info created)
```

This is a dissipative process, not a coherent one. It would emerge from
coupling to an environment, not from the unitary quantum dynamics of H_int alone.

**The honest conclusion:**

The coherent quantum parent (unitary H) generates a source term with
memory and population-inversion structure. The αE Markovian source of
the original master equation is not a unitary quantum effect — it requires
dissipative (Lindblad-type) dynamics driven by an environment.

This means C± = αE is not a coherence effect. It is a thermalization effect:
energy relaxes into information via coupling to an environmental reservoir.

---

## Summary Table

| Q7 question | Answer |
|-------------|--------|
| Minimal Hilbert space? | ℂ² ⊗ ℂ² (dir qubit × 2-level energy) |
| Most general H? | I_dir⊗Ĥ_E + σˣ⊗H₊₋ (JC structure) |
| PRW populations as QM observables? | YES — n±/N = Tr_E(ρ₊₊), Tr_E(ρ₋₋) |
| Does coherence χ generate C±? | YES — C⁺_eff = (4N/ℏV) Im(g* χ₀₁) |
| Does C±_eff match αE? | NO — C±_eff ∝ ΔN₁₁ (population inversion), not αE |
| Is C±_eff always positive? | NO — can be negative |
| Memory terms present? | YES — K(τ) = A·sin(Δε τ/ℏ) |
| ℏ enters microscopically? | YES |
| Is C± still a free parameter? | PARTIALLY — g is free; form of C± is constrained |
| Outcome classification | PARTIAL SUCCESS (Branch 2) |

---

## The Gap That Remains Open

The quantum parent is:

```
quantum ρ̂ (ℂ² ⊗ ℂ²)
    ↓ [decoherence: χ → 0]
PRW (n⁺, n⁻, e⁺, e⁻) with C⁺_eff ∝ ΔN₁₁
```

The original master equation needs C⁺ ∝ αE.

Bridging this gap requires one of:

1. **A dissipative environment** that makes the high-energy state decay and
   feeds the information sector. This would make C± = αE emerge from a
   system-bath model, with α determined by the bath coupling strength.
   This is physically natural — it is the standard quantum optical gain model.

2. **A different H_int** that couples total energy to direction creation
   (not energy-difference). This might exist for a different choice of
   energy-direction interaction — requiring a more detailed microscopic model.

3. **A reinterpretation of E**: in the quantum parent, what is called E in the
   master equation might correspond to ΔN₁₁ rather than e⁺+e⁻. If the
   substrate's "energy density" is actually the population inversion (not the
   total energy), the two forms agree. This requires redefining E, which
   changes the dimensional structure of the master equation.

Option 1 (dissipative bath) is the most physically standard path and makes
the αE term a thermalization rate — well-defined, derivable from a Hamiltonian,
with α = 2π|g|²/Δε · (bath density of states).

This would be a genuine derivation of αE, not a stipulation.
