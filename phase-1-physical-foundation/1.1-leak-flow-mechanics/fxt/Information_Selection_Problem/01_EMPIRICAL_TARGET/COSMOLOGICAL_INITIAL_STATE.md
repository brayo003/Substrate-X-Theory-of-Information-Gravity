# COSMOLOGICAL_INITIAL_STATE
## Gate 1 — The Structure of the Initial-State Problem

---

### Purpose

This document synthesizes the Gate 1 findings about the cosmological initial state into a precise problem statement. It separates what is established, what is contested, and what the actual explanatory target is.

It explicitly avoids the shortcut: "low-entropy initial state" → demand an explanation.

---

## Section 1: What Needs to Be Explained

Drawing from OBSERVATIONAL_FACTS.md and THEORETICAL_FACTS.md, the actual items requiring explanation are:

### 1.1 The Horizon Problem (Pre-inflation framing)
Causally disconnected regions of the CMB sky have nearly identical temperatures (ΔT/T ~ 10⁻⁵). In standard FRW cosmology without inflation, these regions were not in causal contact at last scattering. The observed smoothness therefore requires either:
- An early phase that expanded the causal horizon (inflation or equivalent)
- An initial condition that was smooth across super-horizon scales (unexplained)
- A law that forces super-horizon correlations (unidentified)

**Inflation explains the horizon problem** by postulating a period of accelerated expansion. But inflation itself requires initial conditions — the inflaton field in a suitable state. It shifts the question, it does not answer it.

### 1.2 The Flatness Problem
Spatial curvature Ω_k ≈ 0 to high precision (Planck 2018: |Ω_k| < 0.001). In standard FRW without inflation, spatial flatness is an unstable fixed point — any small initial curvature grows. The observed flatness requires either:
- Inflation (which flattens the geometry)
- An initial condition that was flat to one part in ~10^60 (at Planck time)
- A law that selects flat initial conditions

**Inflation explains the flatness problem** (flatness is an attractor of inflation). Again, shifts but does not remove the initial condition dependence.

### 1.3 The Low-Entropy Initial Condition Problem (Penrose's Problem)
Regardless of inflation, the universe appears to have started in a state of anomalously low gravitational entropy. This problem is **not solved by inflation**. Inflation requires the inflaton to begin in a low-entropy, near-homogeneous state — which itself requires explanation.

Roger Penrose has argued this is the deepest unsolved problem in cosmology. The argument:
1. A "generic" initial state would have near-maximal Weyl curvature (highly inhomogeneous)
2. The observed early state had near-zero Weyl curvature
3. This is extraordinarily improbable under any "natural" measure
4. Therefore, a mechanism or law must select the low-Weyl initial state

**This problem is NOT solved by inflation.** This is the primary target.

### 1.4 The Specificity of the Problem
Note that problems 1.1 and 1.2 are solved (or addressed) by inflation. Problem 1.3 is not. They are distinct problems. Conflating them is a Gate 1 violation.

The research target of this program is specifically:

> **Why was the initial gravitational state special in the sense required for the observed cosmological evolution?**

Where "special" means: selected from a vastly smaller subset of possible states than would be expected under any natural measure on the space of cosmological configurations.

---

## Section 2: The Problem Has Multiple Non-Equivalent Formulations

The following formulations are found in the literature. They are **not equivalent**:

### Formulation A — Penrose (Weyl Curvature Hypothesis)
The early universe had C_μνρσ ≈ 0. This requires explanation as an initial boundary condition on gravitational degrees of freedom.

**Problems with this formulation:**
- Weyl = gravitational entropy is a conjecture, not a theorem (see THEORETICAL_FACTS.md §2)
- Counterexamples exist in Bianchi spacetimes
- Does not specify a mechanism, only identifies the unusual feature

### Formulation B — Statistical Mechanics / Boltzmann
The initial state was a low-entropy fluctuation in a larger ergodic system. Under Boltzmann's cosmology, we are in a fluctuation from equilibrium.

**Problems:**
- Predicts a much smaller universe (Boltzmann brain problem)
- Does not explain why the fluctuation had the specific structure observed (not just low entropy but correlated structure)
- Requires an eternal background universe (unobserved)

### Formulation C — No-Boundary Proposal (Hartle-Hawking)
The universe has no initial boundary. The wave function of the universe is defined by a path integral over compact Euclidean geometries. The "initial state" is selected by quantum gravity.

**Problems:**
- Contested whether it actually predicts low-entropy initial states (Penrose argues it predicts high entropy; recent arguments by Hertog, Hawking revise this)
- The formalism is not fully defined (requires a theory of quantum gravity)
- Multiple competing realizations give different predictions

### Formulation D — Tunneling Proposal (Vilenkin)
The universe tunneled from nothing into a de Sitter space. The initial state is selected by the tunneling probability.

**Problems:**
- Predicts inflationary initial conditions but still requires explanation of which tunneling transitions are preferred
- "Tunneling from nothing" is formally problematic (nothing has no Hamiltonian)

### Formulation E — Scale Factor Entropy (Carroll et al.)
The low entropy is the small spatial volume. Entropy increases because volume increases. The "specialness" is just the small initial size.

**Problems:**
- This is more a reframing than an explanation
- Does not explain why the universe was small with homogeneous structure rather than small with chaotic structure

### Formulation F — Information-Saturation Interface (July 2026 paper)
A structural constraint from information saturation selects FLRW geometries, suppressing Weyl curvature.

**Problems (to be analyzed in 03_INFORMATION_LITERATURE/INFORMATION_SATURATION.md):**
- Authors describe it as structural selection, not a dynamical theory
- Quantitative cosmological predictions deferred
- Whether the constraint independently selects FLRW or assumes it requires adversarial examination

---

## Section 3: What the Target Is NOT

To avoid the failure mode of solving the wrong problem, the target is explicitly **not**:

- Explaining why the universe exists (metaphysics)
- Explaining why the laws of physics are what they are (separate problem)
- Explaining the value of cosmological constants (separate problem)
- Deriving the Standard Model of particle physics
- Explaining dark matter or dark energy (though relevant context)
- Explaining why inflation happened (inflation is context, not target)

---

## Section 4: The Minimal Explanatory Target

The minimum that counts as an explanation of the cosmological initial-state problem:

> Derive, from premises that do not assume homogeneity, isotropy, FLRW geometry, or low Weyl curvature, a constraint or mechanism that:
> 1. Restricts the set of physically realizable early-universe states to a measure-zero (or strongly suppressed) subset of the space of all logically possible states
> 2. That subset includes states consistent with the observed CMB + large-scale structure
> 3. The derivation does not rely on boundary conditions that encode the answer

Bonus (not required for Gate 3 RESIDUAL EXISTS decision):
> 4. The mechanism generates a quantitative prediction distinguishable from ΛCDM

---

## Section 5: The Measure Problem (Central Unresolved Issue)

All quantitative versions of the initial-state problem require a measure on the space of initial cosmological configurations. Without such a measure, statements like "the initial state was improbable" are undefined.

The measure problem is **genuinely hard**:
- The natural Liouville measure on GR initial data space is not normalizable (infinite total volume)
- Different measures give different notions of "typicality"
- Inflation can appear natural or highly fine-tuned depending on the measure chosen

Any proposed explanation of the initial-state problem must either:
- Specify the relevant measure and justify it independently, or
- Derive a constraint that is measure-independent (would be remarkable if possible)

This is documented here as a structural constraint on any solution attempt.

---

*Document status: WORKING — Gate 1 synthesis complete (pending Gate 2 input)*
