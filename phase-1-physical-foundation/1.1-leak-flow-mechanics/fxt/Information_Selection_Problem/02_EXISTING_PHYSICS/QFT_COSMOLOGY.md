# QFT_COSMOLOGY
## Gate 2 — QFT in Curved Spacetime and Quantum Cosmology

---

### Purpose

Assess what quantum field theory in curved spacetime (QFT-CS) and quantum cosmology (including the Wheeler-DeWitt approach) contribute to explaining the initial-state problem.

---

## Section 1: QFT in Curved Spacetime

### 1.1 What It Is
QFT-CS extends quantum field theory to curved (but fixed, not dynamical) backgrounds. The spacetime geometry is treated classically; quantum fields propagate on it.

Key results:
- Unruh effect: accelerated observers in flat spacetime detect thermal radiation
- Hawking radiation: black holes emit thermal radiation (T_H = ℏc³/8πGMk_B)
- Cosmological particle creation: expanding universe creates particles from vacuum

### 1.2 What It Explains About the Initial State

**Primordial perturbations from inflation:** QFT-CS provides the mechanism for generating the primordial power spectrum during inflation. Vacuum fluctuations of the inflaton field on the curved de Sitter background are stretched to super-horizon scales.

**Assessment:** This is a genuine contribution. The near-scale-invariant spectrum is a real QFT-CS result. However, it requires the de Sitter background (i.e., inflation) as input. The question of why inflation occurred, and with what initial state, remains.

### 1.3 What QFT-CS Cannot Address
- The backreaction of quantum fields on the geometry is not fully handled (requires quantum gravity)
- The initial state of the quantum fields during inflation is conventionally taken to be the Bunch-Davies vacuum — this is a choice, not a derivation
- The Bunch-Davies vacuum is selected by the condition that it reduces to flat-space vacuum in the infinite past. This condition is natural but not forced; other vacua exist and give different predictions

**Gate 2 verdict for QFT-CS:** EXPLAINS primordial perturbations given inflationary background and Bunch-Davies vacuum choice. Does NOT explain why inflation occurred or why the Bunch-Davies vacuum was selected.

---

## Section 2: Quantum Cosmology — Wheeler-DeWitt Equation

### 2.1 What It Is
Quantum cosmology applies the canonical quantization procedure to the entire universe. The Hamiltonian constraint of GR becomes an operator equation on the wave function of the universe Ψ[h_ij]:

```
Ĥ Ψ[h_ij] = 0    (Wheeler-DeWitt equation)
```

This is the "Schrödinger equation" for the universe, but with zero on the right (no external time).

### 2.2 The No-Boundary Proposal (Hartle-Hawking)
The wave function of the universe is given by a path integral over compact Euclidean geometries:

```
Ψ[h_ij] = ∫ Dg exp(-S_E[g])
```

summed over all compact 4-geometries with h_ij as their only boundary.

**Claims:**
- Selects a unique initial state for the universe
- Predicts a smooth, nearly homogeneous beginning
- Gives the universe "no boundary" (hence name)

**Problems:**
- Penrose has argued the no-boundary proposal predicts high-entropy initial states, not low-entropy ones (because high-entropy states dominate the Euclidean path integral)
- Recent analysis by Maldacena, Diaz, et al., and Hertog-Hawking revisited: there is ongoing disagreement about which saddle points dominate and whether the prediction is for low or high entropy
- The path integral is not rigorously defined in Lorentzian signature; the Euclidean approach has subtleties
- Predictions are sensitive to the choice of integration contour in the complex plane

**Gate 2 verdict:** The no-boundary proposal ATTEMPTS to explain the initial low-entropy state but is contested — both theoretically (which saddle dominates?) and formally (the path integral is not fully defined). It is a serious candidate but not an established solution.

### 2.3 The Tunneling Proposal (Vilenkin)
The universe tunneled from "nothing" (a state with no classical spacetime) to a de Sitter space. The tunneling amplitude selects initial conditions.

**Problems:**
- "Nothing" with a Hamiltonian is already something
- The wave function is computed with outgoing boundary conditions at the singularity, which is a choice (opposite convention to Hartle-Hawking in some regimes)
- Predictions differ from Hartle-Hawking in sign of quantum corrections to inflationary potential

**Gate 2 verdict:** The tunneling proposal CLAIMS to explain the initial state but is not formally derivable from first principles; it requires the boundary condition choice as input.

---

## Section 3: The Problem of Time in Quantum Cosmology

Both approaches face the fundamental "problem of time" in quantum gravity: the Wheeler-DeWitt equation has no time parameter. Time must emerge from correlations within the wave function (relational time).

This is a deep unresolved problem. It means quantum cosmology cannot make straightforward predictions about the time evolution of the universe without additional structure.

For Gate 2 purposes: the problem of time is registered as a structural limitation of quantum cosmology approaches, not a solved problem.

---

## Section 4: String Cosmology and Pre-Big-Bang Scenarios

String theory provides additional initial-condition proposals:
- Pre-big-bang scenarios (Gasperini-Veneziano): a contracting string-dominated phase precedes the big bang
- Ekpyrotic/cyclic models (Steinhardt-Turok): the big bang is a bounce or collision of branes
- String landscape: the universe tunnels to our vacuum from a high-energy metastable state

**Assessment for Gate 2:** These proposals exist and are serious research programs. None has established itself as the correct initial-condition explanation, and none has unique observational predictions confirmed by data. They are registered here as alternatives that Gate 3 must account for when assessing what remains unexplained.

---

## Gate 2 Verdict for QFT-CS and Quantum Cosmology

| Framework | Target Feature | Verdict |
|---|---|---|
| QFT-CS | Primordial perturbation spectrum | EXPLAINED (given inflation + Bunch-Davies) |
| No-boundary proposal | Low-entropy initial state | CONTESTED — not established |
| Tunneling proposal | Initial state selection | CLAIMED — requires boundary condition input |
| String cosmology | Initial state | SPECULATIVE — no confirmed predictions |
| Problem of time | Time emergence | UNRESOLVED |

**What survives Gate 2:** The low-entropy gravitational initial state is not explained by any established QFT-CS or quantum cosmology framework. The no-boundary proposal is the most serious candidate; its failure or success determines whether a residual survives.

---

*Document status: WORKING — Gate 2 assessment for QFT-CS and quantum cosmology*
