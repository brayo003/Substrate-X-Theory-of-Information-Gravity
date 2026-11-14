# 01_FAILURE_MECHANISM_TAXONOMY
## Post-Mortem: Mathematical Failure Modes of the 25 Killed Candidates

**Date:** August 2026
**Purpose:** Classify every failure by its mathematical mechanism, not by name. Identify what selection operations remain available.

---

## The Killed Candidates and Their Failure Classes

| ID | Name | Primary failure class | Secondary |
|----|------|-----------------------|-----------|
| P01 | Asymptotic safety | B (saddle inheritance) + J (β too small) + C (no state) | — |
| P02 | Rindler thermodynamic | A (GR-equation inheritance) | — |
| P03 | Causal diamond capacity | I (conclusion encoding: C_min = desired output) | — |
| P04 | Lyapunov stability | L (dynamical consistency, not selection) | — |
| P05 | Consistent histories | C (requires ρ_0 as input) | H (decoherence) |
| P06 | Anomaly freedom | A (satisfied by all GR solutions semiclassically) + K (Bianchi I has anomaly-free QM) | — |
| P07 | BMS vacuum | F (asymptotic flatness required) | — |
| P08 | Spin-foam amplitude | B (all GR solutions are saddle points) | — |
| P09 | CDT phase dominance | F (fixed S³ topology) | — |
| P10 | Viscous dissipation | K (attractor requires prior restricted basin) + J (undefined measure) | — |
| P11 | Modular Hamiltonian | C (requires quantum state ρ_Σ as input) | — |
| P12 | GSL contraction | I (S_grav ~ W²: prohibited Penrose identification) | — |
| P13 | EFT validity | L (necessary condition only; already in existing physics) | — |
| P14 | SGWB coherence | I (uses observed outcome as constraint) | — |
| P15 | Unitarity/final state | C (requires final state encoding desired evolution) | — |
| P16 | Non-commutative spectral | L (selects equations of motion, not initial data) | — |
| P17 | Superradiant instability | F (requires Kerr + reflective boundary) | — |
| P18 | Null geodesic completeness | D (restates R1 without deriving it) | — |
| P19 | Scale-factor duality | I (uses smooth post-bang as input) + F (FRW only) | — |
| P20 | Topological censorship | F (asymptotic flatness) + G (topology ≠ curvature) | — |
| P21 | QEC holography | F (AdS only) | — |
| P22 | Quantum Darwinism | H (decoherence relabeling) | — |
| P23 | Petrov type restriction | I (restricts Weyl directly — direct conclusion encoding) | — |
| P24 | Holographic complexity | F (AdS only) | — |
| P25 | Gravitational decoherence | H (decoherence) + C (selects classicality, not which classical state) | — |

---

## Failure Class Definitions

### A — GR-Equation Inheritance
The mechanism is equivalent to "satisfies Einstein's equations." Every solution of GR satisfies it. Cannot select within the GR solution space.

*Killed by this: P02 (Clausius = Einstein), P06 (anomaly-free semiclassical limit = all of Γ_GR).*

*Mathematical signature:* The selection condition δS/δg = 0 is equivalent to GR equations. No additional restriction on initial data follows.

---

### B — Path-Integral Saddle Inheritance
The mechanism selects GR saddle points of a path integral. Every classical GR solution is a saddle point of any GR-derived action. Cannot select a subset of GR solutions unless: (a) the action is not GR-derived, or (b) the weight is exponentially large, or (c) some classical solutions are non-saddle-points.

*Killed by this: P01 (β too small; Kasner is a saddle by Bianchi identity), P08 (all GR solutions are Regge saddles).*

*Mathematical signature:* The measure dμ[g] exp(−S[g]) with S[g] = S_GR + small correction. The classical solutions of S_GR are saddle points regardless of the correction.

---

### C — Quantum-State Dependence
The mechanism requires as input the quantum state (wave functional, density matrix, initial state) that it claims to select. This is circular.

*Killed by this: P05, P11, P15, P25 (partial).*

*Mathematical signature:* The selection condition involves ρ_0, |Ψ_0⟩, or Tr(ρ_0 O) — all of which encode the initial state.

---

### D — Boundary-Condition Relocation
The mechanism replaces one boundary condition (low Weyl) with another (no past boundary, outgoing tunneling, etc.) without deriving the new condition from independent premises.

*Killed by this: P18 (null completeness = statement of the problem).*

*Mathematical signature:* The "derivation" shows that Condition X implies Condition Y (where Y ~ low Weyl), but Condition X is not itself derived — it is a boundary condition stipulated for independent reasons.

---

### E — Background Dependence
(Not a primary kill reason for any candidate, but appears in T2 kills.)
The primitive requires a fixed background metric (FLRW, Minkowski, de Sitter) to be stated.

---

### F — Wrong Asymptotic Structure
The primitive requires asymptotically flat spacetime, AdS, fixed topology, or a specific causal boundary that the cosmological early universe does not have.

*Killed by this: P07, P09, P17, P20, P21, P24.*

*Mathematical signature:* The mechanism uses I^+, I^-, S³ topology, conformal boundary, holographic screen — none of which exist in compact or asymptotically de Sitter cosmology.

---

### G — Topological Restriction Without Curvature Selection
The mechanism restricts the topology of the spatial slice without restricting the curvature. A Bianchi IX model on S³ can have arbitrarily large Weyl curvature.

*Killed by this: P20 (topological censorship).*

*Mathematical signature:* The condition restricts π_1(Σ) or the genus of Σ, but Weyl curvature is a metric-level (not topological) property. The restriction is in the wrong stratum.

---

### H — Decoherence Relabeling
The mechanism is a variant of decoherence-based state selection. Decoherence explains the emergence of classicality from quantum superpositions but does not select which classical state is realized.

*Killed by this: P22, P25 (partial), P05 (partial).*

*Mathematical signature:* The einselection / pointer-state argument selects states stable under environmental monitoring. It explains classicality but not the specific classical state. The initial-state problem is not the "why is the universe classical" problem — it is the "why is the classical state one of low Weyl curvature" problem. Decoherence answers the former, not the latter.

---

### I — Direct Conclusion Encoding
The primitive definition contains, explicitly or implicitly, the conclusion (low Weyl, smoothness, homogeneity). The "derivation" is circular.

*Killed by this: P03 (C_min = "enough for classical structure"), P12 (S_grav ~ W²), P14 (uses observed SGWB), P19 (uses smooth post-bang), P23 (Petrov type O = C=0).*

*Mathematical signature:* After firewall substitution (replacing prohibited terms with abstract variables), the derivation no longer proceeds — the abstract variable must be interpreted as "low Weyl" for the argument to work.

---

### J — Insufficient Magnitude / Undefined Typicality
The mechanism produces a weighting or suppression, but the magnitude is too small to constitute a physical selection, OR the mechanism invokes "generic," "typical," or "probable" without defining a measure.

*Killed by this: P01 (β* too small), P10 (η/s threshold undefined, basin undefined).*

*Mathematical signature:* The suppression factor exp(−β·O(1)) with β ~ O(10^{-2}) gives ~ 1% suppression, not physical selection. Or: "over a wide basin of initial conditions" without specifying what "wide" means relative to a defined measure on Γ_GR.

---

### K — Dynamical Attractor Requiring Prior Restricted Basin
The mechanism produces an attractor that drives the state toward low Weyl, but the attractor only works from initial conditions that are already not too high-Weyl. The pre-attractor initial condition is itself the unresolved question.

*Killed by this: P06 (Bianchi I has anomaly-free quantization — the anomaly mechanism does not exclude it), P10 (η/s attractor requires prior state below BH formation threshold).*

*Note:* This is also the residual against ekpyrosis (from Gate 4 / FINAL_GATE4_STATUS).

*Mathematical signature:* The theorem is of the form "IF initial state is in basin B, THEN evolution produces low Weyl." But the question is why the initial state was in B. The mechanism shifts, not closes, R1.

---

### L — Dynamical/EFT Consistency Without Initial-State Selection
The mechanism constrains the equations of motion or the EFT, but does not restrict which solutions (initial data) are realized. The equations of motion and the initial data are logically independent.

*Killed by this: P04 (stability of evolution ≠ selection of initial state), P13 (EFT validity is necessary but selects no specific state), P16 (spectral action selects EOMs, not solutions).*

*Mathematical signature:* The selection condition is of the form δS/δg = 0 (EOM) or R_max < M_UV² (EFT validity). These constrain which theories or configurations are self-consistent, not which solutions of a given theory are realized.

---

### M — Emergent-Spacetime State-Input Circularity
The mechanism claims to derive spacetime geometry from an information-theoretic or algebraic substrate, but requires the initial quantum state of the substrate — which encodes the geometry to be derived.

*(No primary kill in the 25, but this was the failure mode for Zheng 2026 in the Gate 4 audit and for several holographic candidates.)*

*Mathematical signature:* G_{μν} = F(ρ_{AB}) where ρ_{AB} is the quantum state of subsystems A, B. But ρ_{AB} is not independently derived — it encodes the geometry.

---

## The Common Mathematical Feature of All Failures

Every failure reduces to one of two fundamental problems:

**Problem α — The GR solution space is too large.**
Any mechanism that is equivalent to "satisfies GR's equations" or "is a GR saddle point" inherits the full GR solution space, which includes Bianchi I, Bianchi IX, Schwarzschild, and every other high-Weyl solution. The GR solution space is precisely what needs to be restricted.

**Problem β — The selection rule encodes the desired output.**
Any mechanism that explicitly or implicitly requires smoothness, homogeneity, or low Weyl as input is laundering the conclusion. The definition contains the answer.

These two problems between them account for all 25 failures. The only candidates that avoided both problems (P01, P06) ran into quantitative failure (P01: β too small, Kasner saddle) or categorical failure (P06: Bianchi I in the anomaly-free sector; AS fixes action not state).

---

## What Selection Operations Remain Mathematically Available?

The failed mechanisms span the following operation types:

| Operation type | Status |
|----------------|--------|
| Path-integral saddle selection | Failed (B) |
| EOM/action modification | Failed (L, B) |
| Quantum constraint kernel | Failed (A, K) |
| Boundary condition | Failed (D) |
| Thermodynamic consistency | Failed (A) |
| Decoherence/einselection | Failed (H, C) |
| Topological restriction | Failed (G, F) |
| Holographic/AdS duality | Failed (F) |
| Asymptotic symmetry | Failed (F) |
| EFT validity | Failed (L) |
| Quantum state selection | Failed (C) |
| Weighting in undefined measure | Failed (J) |

**Operations NOT yet seriously tested:**

1. **Selection by global inextendibility / singularity structure.** The Penrose incompleteness theorem gives conditions for singularities. The converse — that globally inextendible, singularity-free spacetimes form a restricted subset — has not been examined as a selection principle.

2. **Selection by symplectic/geometric-quantization conditions.** The symplectic structure of GR phase space has specific properties. Geometric quantization of Γ_GR places conditions on which states can be quantized. Whether these conditions restrict the classical initial-data space is not explored.

3. **Selection by constraint-propagation consistency in fully inhomogeneous quantum gravity.** Not minisuperspace — the full theory. The constraint-propagation conditions (stability of the constraint surface under the Hamiltonian flow) place conditions on initial data that have not been fully worked out for inhomogeneous quantum gravity.

4. **Selection by discrete-to-continuum emergence conditions.** If spacetime is fundamentally discrete (causal sets, spin networks, CDT), the continuum limit may not exist for all initial data configurations — only those satisfying specific regularity conditions. This has not been developed as a selection mechanism.

5. **Selection by relational observables / Dirac observables.** In canonical GR, Dirac observables are invariant under all gauge transformations. The space of Dirac observables may be smaller than Γ_GR. Whether this space specifically favors low-Weyl initial data has not been examined.

6. **Selection by functional-analytic conditions on the constraint surface.** The GR constraint equations are an elliptic PDE system on the initial slice. Not all smooth 3-manifolds admit solutions to the GR constraint equations with given matter content. Whether there exist functional-analytic conditions (Sobolev regularity, conformal factor existence) that specifically restrict to low-Weyl data has not been examined.

These six operation types are genuinely unexplored for R1. They define the search space for Phase II.

---

*Document status: FAILURE MECHANISM TAXONOMY COMPLETE*
*6 unexplored selection operation types identified.*
*Date: August 2026*
