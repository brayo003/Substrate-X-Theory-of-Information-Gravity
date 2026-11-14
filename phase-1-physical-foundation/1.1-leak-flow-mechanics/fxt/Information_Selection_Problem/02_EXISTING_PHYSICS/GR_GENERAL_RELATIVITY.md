# GR_GENERAL_RELATIVITY
## Gate 2 — What General Relativity Explains About the Initial State

---

### Purpose

Assess what General Relativity, as a standalone framework (without inflation, quantum gravity, or additional fields), contributes to explaining the cosmological initial-state problem.

Assessment matrix entry: `GR × [each target feature]`

---

## Section 1: What GR Provides

General Relativity is a classical field theory. Its fundamental object is the spacetime metric g_μν, governed by:

```
G_μν + Λg_μν = 8πG T_μν
```

It provides:
- A dynamical theory of spacetime geometry
- The Friedmann equations as the cosmological limit (given FLRW symmetry as input)
- Geodesic deviation and curvature propagation
- The Raychaudhuri equation governing expansion and focusing of geodesic congruences
- Singularity theorems (Penrose, Hawking) establishing conditions for geodesic incompleteness

GR does **not** provide:
- A theory of initial conditions
- A measure on the space of solutions
- A selection principle among the space of possible spacetime histories
- A derivation of why any particular solution is realized

---

## Section 2: Assessment Matrix

| Target Feature | GR Explains? | What GR Actually Does |
|---|---|---|
| Large-scale geometric smoothness | **Reframes, does not explain** | FLRW is a solution of GR with homogeneity/isotropy imposed as input. GR does not select FLRW over non-FLRW solutions. |
| Small primordial anisotropies (~10⁻⁵) | **Does not explain** | GR perturbation theory propagates perturbations; it does not set their initial amplitude. |
| Thermalized matter/radiation | **Does not address** | GR is a theory of geometry; matter thermalization is governed by QFT + standard model, not GR. |
| Suppressed gravitational DOF | **Does not explain** | GR permits all values of Weyl curvature. Nothing in the Einstein equations selects low Weyl initial data. |
| Subsequent growth of structure | **Explains (given initial conditions)** | GR perturbation theory correctly describes gravitational collapse and structure formation given the measured initial power spectrum. |
| Macroscopic entropy increase | **Does not explain** | GR is time-symmetric (time-reversal symmetric solutions exist). It does not select a direction for entropy increase. |

---

## Section 3: The Initial Value Problem in GR

GR is a well-posed initial value theory. Given initial data (3-metric h_ij, extrinsic curvature K_ij) on a spacelike hypersurface satisfying the constraint equations:

```
R - K_ijK^ij + (K^i_i)² = 16πG ρ    [Hamiltonian constraint]
∇_j(K^ij - h^ij K) = 8πG j^i        [Momentum constraint]
```

...the evolution is determined (up to gauge freedom) by the Einstein equations.

**Key point:** The constraint equations are conditions on the initial data, not selection principles. They rule out some initial data but admit a vast space of valid configurations. The observed early universe occupies a tiny corner of this space. GR does not explain why that corner was selected.

The set of solutions to the constraint equations is essentially infinite-dimensional. FLRW initial data is a measure-zero set. GR is silent on why it was chosen.

---

## Section 4: The Weyl Curvature and GR

The Weyl tensor C_μνρσ encodes the trace-free part of the Riemann curvature. It propagates gravitational radiation and represents "free" gravitational degrees of freedom not determined by local matter.

GR's Bianchi identity ensures:
```
∇^ρ C_μνρσ = ∇_[μ(R_ν]σ - g_ν]σ R/6)
```

This is a propagation equation, not a selection principle. The Weyl tensor at early times is determined by the initial data plus the matter distribution. GR does not constrain the Weyl tensor to be small at early times. Any initial Weyl curvature (subject to constraint equations) is a valid GR solution.

**Verdict:** GR permits, but does not select, the observed low-Weyl initial state.

---

## Section 5: What GR Cannot Do (Formal Statement)

**Theorem (informal):** The space of GR initial data satisfying the constraint equations is infinite-dimensional. The observed early universe corresponds to initial data in a measure-zero subset (in any reasonable measure). GR as a dynamical theory evolves all initial data forward; it does not select among them.

Therefore: **GR alone does not and cannot explain the cosmological initial-state problem.**

This is not a failure of GR. It is a correct characterization of what GR is and what it does.

---

## Section 6: What GR Does Contribute (Positively)

GR provides:
1. The mathematical framework (spacetime manifolds, curvature tensors) for formulating the initial-state problem precisely
2. The Friedmann equations as the dynamical context for evolution once initial conditions are specified
3. The perturbation theory framework for connecting initial conditions to observables
4. Singularity theorems that establish the early universe was geometrically special (geodesically incomplete past) — but this is a consequence of the initial conditions, not an explanation of them
5. The ADM decomposition of spacetime which gives the natural phase space for initial-state analysis

---

## Gate 2 Verdict for GR

| Feature | GR verdict |
|---|---|
| Smoothness | NOT EXPLAINED (FLRW is input, not output) |
| Perturbation amplitude | NOT EXPLAINED (initial amplitude is free data) |
| Thermalization | NOT ADDRESSED |
| Gravitational DOF suppression | NOT EXPLAINED (Weyl curvature is unconstrained) |
| Structure growth (given ICs) | EXPLAINED |
| Entropy increase | NOT EXPLAINED |

**Summary:** GR explains structure growth given initial conditions. It does not explain any feature of those initial conditions. The problem must be addressed elsewhere.

---

*Document status: WORKING — Gate 2 assessment for GR*
