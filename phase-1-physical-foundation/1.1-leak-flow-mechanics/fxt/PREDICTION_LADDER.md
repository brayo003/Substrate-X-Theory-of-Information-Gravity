# PREDICTION_LADDER.md
## SXC-IGC/C2 — Primitive Ontology to Observables Chain

**Date:** 2026-08-22
**Purpose:** Trace every step from the C2 primitive ontology to every measurable
  observable. At each arrow, identify exactly what is derived and what is assumed.
**Label convention:** [ASSUMED] [DERIVED] [THEORY EXTENSION] [FREE] [IMPORTED]
  [CONVENTIONAL PHENOMENOLOGY] [FORWARD PREDICTION]

---

## RUNG 0 — Primitive Ontology

**What SXC-IGC claims exists:**

An information substrate — a physical field s(x,t) [information density]
propagating through space at finite speed c, reversing direction at rate λ.

The substrate is not matter, not EM radiation. It is a new degree of freedom
whose physical identity is unspecified within existing C2 beyond the FPUT
substrate model (A-FPUT1).

**Ontological primitive:** a persistent random walker (PRW) carrying information
at speed v, reversing direction at rate λ.

**Primitive parameters:**
- v [m/s]: propagation speed [FREE in existing C2; = v_s under Extension A]
- λ [s⁻¹]: reversal rate [FREE]

**No CCA/SCC axiom specifies what this substrate IS physically.** The CCA layer
provides mathematical structure; the PRW layer specifies dynamics; neither identifies
the physical medium.

Status: ASSUMED (A-FPUT1 specifies FPUT harmonic chain as substrate model)

---

## RUNG 1 — Microscopic Dynamics

**Step 1.1: PRW balance equations**

```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻     [ASSUMED: A-PRW1,2,3]
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻
```

where n⁺, n⁻ are right- and left-moving information densities.

Status: ASSUMED — these are the PRW axioms, not derived from CCA/SCC.

**Step 1.2: Macroscopic fields**

Define:
```
s = n⁺ + n⁻    [information density]
J = v(n⁺ − n⁻) [information flux]
```

Status: DEFINITION (trivial)

**Step 1.3: Macroscopic transport equations**

```
∂s/∂t + ∂J/∂x = 0           [continuity, DERIVED from PRW balance]
∂J/∂t + v² ∂s/∂x = −2λ J    [flux evolution, DERIVED from PRW balance]
```

Status: DERIVED — exact from PRW balance, no approximation.

**Derivation:**
Add the two balance equations → ∂s/∂t = −∂J/∂x (continuity).
Subtract and multiply by v → ∂J/∂t = −v²∂s/∂x − 2λJ (flux equation).

Arrow: PRW balance equations → macroscopic transport equations.
Missing: nothing — this is exact.

---

## RUNG 2 — Continuum/Effective Equations

**Step 2.1: Telegrapher equation**

Eliminate J from the two equations above:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
```

where τ = 1/(2λ), c = v, D = c²τ.

Status: DERIVED — exact consequence of PRW balance. [Goldstein-Kac KR]

**Step 2.2: Limiting cases**

BGK (diffusion) limit: τ → 0 with D = c²τ fixed:
```
∂s/∂t = D ∇²s    [DERIVED as τ→0 limit]
```

Wave limit: τ → ∞ with c fixed:
```
∂²s/∂t² = c² ∇²s    [DERIVED as τ→∞ limit]
```

Arrow: PRW balance → telegrapher equation → limits.
Missing: nothing for the formal derivation. The PHYSICAL identification of
c and τ with material properties requires Extension A.

**Step 2.3: Dispersion relation**

```
ω(k) = −iλ ± √(v²k² − λ²)
```

Critical wavevector: k_c = λ/v = 1/ξ_c.
For k > k_c: oscillatory modes (propagating).
For k < k_c: overdamped modes (evanescent).

Status: DERIVED from telegrapher equation.

**Step 2.4: Coherence length ξ_c**

```
ξ_c = v/λ = 2cτ    [DERIVED from PRW parameters — definition]
```

Physical meaning: the mean free path of a PRW particle.
This is the spatial scale at which the substrate transitions from
propagating to evanescent behavior.

Status: DERIVED as parameter combination. Value is FREE (depends on v and λ).
Under Extension A: ξ_c = 2v_s·τ_B [FORWARD PREDICTION given τ_B].

---

## RUNG 3 — Propagating Modes and Correlations

**Step 3.1: Local current autocorrelation**

The substrate current J(x,t) at a fixed point has autocorrelation:

```
C_JJ(t) = S₀ · exp(−t/τ_B)    [DERIVED from PRW OU argument]
```

where τ_B = 1/(2λ) and S₀ = s₀v²/2 (equilibrium variance).

Status: DERIVED — follows from OU structure of J at k=0.

**Step 3.2: Power spectral density**

```
S_JJ(ω) = 2S₀τ_B / (1 + ω²τ_B²)    [DERIVED via Wiener-Khinchin]
```

Status: DERIVED — exact Fourier transform of exponential autocorrelation.

This is a Lorentzian spectrum.

**Step 3.3: Spatial current correlator (1D)**

```
S_JJ(Δx, ω=0) = S₀ · exp(−|Δx|/ξ_c)    [DERIVED — 1D telegrapher Green's function]
```

Status: DERIVED — from telegrapher propagator at ω=0.

**Step 3.4: Spatial current correlator (2D)**

```
S_JJ(r, ω=0) ∝ K₀(r/ξ_c)    [DERIVED — 2D telegrapher static Green's function]
```

where K₀ is the modified Bessel function of second kind, order 0.

Status: DERIVED (analytic step partially incomplete — numerical verification exists).

**Step 3.5: Spatiotemporal correlator**

For the full (r, t) correlator at the level of the telegrapher equation:

```
C_JJ(r, t) = f(r/ξ_c, t/τ_B)    [DERIVED — structure only]
```

The exact form involves a Bessel function integral (telegrapher propagator).
The static (t→∞) limit is K₀(r/ξ_c).

Status: DERIVED in structure; exact form is an integral expression.

Arrow: PRW transport → substrate correlations.
Missing: analytic proof of 2D K₀ formula (numerically confirmed).

---

## RUNG 4 — Coupling to Quantum Systems

**Step 4.1: Interaction Hamiltonian**

```
H_int = g · J(x_q, t) · σ_z    [ASSUMED: A-HC5, A-HC6]
```

g = quantum-classical coupling constant [FREE — GAP-7 F10].
J(x_q, t) = substrate current at qubit position.
σ_z = Pauli Z operator of the qubit.

Status: ASSUMED — this coupling form is postulated, not derived from the
transport layer or from CCA/SCC. It is the simplest linear local coupling.

**Step 4.2: Effective dephasing under Born-Markov approximation**

Using A-HC1 (Born), A-HC2 (Markov: τ_B ≪ Γ_φ⁻¹), A-HC3 (secular), A-HC4 (stationary):

```
dρ_S/dt = (Γ_φ/2)(σ_z ρ_S σ_z − ρ_S)
Γ_φ = (2g²/ℏ²) · S_JJ(ω=0) = 4g²S₀τ_B/ℏ²    [DERIVED conditional]
```

Status: DERIVED given A-HC1 through A-HC6 and H_int. Conditional on ≥6 assumptions.

**Step 4.3: Non-Markovian (exact) dephasing**

Without the Markov approximation:

```
W(t) = exp(−Φ(t))
Φ(t) = Γ_Markov·τ_B·[t/τ_B − 1 + exp(−t/τ_B)]    [DERIVED exactly]
```

Status: DERIVED — exact for Gaussian noise (Kubo formula).

Arrow: Substrate correlations + coupling → qubit decoherence.
Missing at this step: derivation of g (remains FREE).

---

## RUNG 5 — Measurable Observables

**Step 5.1: Single-qubit Ramsey signal**

```
W(t) = ⟨σ_x(t)⟩ = exp(−Φ(t))
```

Markov limit: W(t) = exp(−Γ_φ·t) — pure exponential.
Non-Markov correction: Gaussian onset for t < τ_B.

Observable: Ramsey fringe decay as a function of wait time t.
Measured by: single-qubit X-basis measurement after wait time t.

**Step 5.2: Decoherence rate vs rotation frequency**

For a qubit rotating at frequency ω_rot:

```
Γ_φ(ω_rot) = k_rot · ω_rot²
k_rot = 8g²S₀r_q²τ_B/(3ℏ²)    [DERIVED conditional — rotating frame calculation]
```

Observable: Γ_φ measured at multiple ω_rot values → fit k_rot.

**Step 5.3: Power spectral density (Ramsey spectroscopy)**

By measuring Γ_φ at many ω_rot values, one traces S_JJ(ω_rot) via:

```
Γ_φ(ω_rot) ∝ ∫ S_JJ(ω) · F(ω, ω_rot) dω
```

where F is the filter function. For rotating-frame: F peaks at ω = ω_rot.

Observable: S_JJ(ω) reconstructed from Γ_φ(ω_rot) sweep.

**Step 5.4: Spatial decoherence correlation**

For two qubits at separation r, simultaneous Ramsey measurement gives:

```
C_Γ(r) = C_ij(t) / (W_i(t)·W_j(t)) → K₀(r/ξ_c)    [DERIVED conditional]
```

Observable: parity-based two-qubit correlation extracted from joint measurement.

**Step 5.5: Bath correlation time τ_B**

From the NM Ramsey curvature (short-time deviation from exponential):

```
τ_B = Φ''(0) / Φ'(0)² ∝ (curvature of ln W(t) at t=0)
```

Observable: time-resolved Ramsey measurement at short times (t ~ τ_B).
Requires NMP = τ_B · Γ_φ ≥ 0.1 for reliable extraction.

Arrow: Substrate coupling → qubit observables.
Missing: derivation of g (free). NMP constraint limits current hardware.

---

## RUNG 6 — Quantitative Predictions

**Prediction 1: Lorentzian temporal spectrum**

```
S_JJ(ω) = 2S₀τ_B / (1 + ω²τ_B²)
```

Parameters: (S₀, τ_B) — both free.
Status: DERIVED. CONVENTIONAL PHENOMENOLOGY (any OU bath gives same form).

**Prediction 2: ω_rot² Ramsey scaling**

```
Γ_φ(ω_rot) = k_rot · ω_rot²
```

Parameter: k_rot — free (contains g·s₀·τ_B).
Status: DERIVED conditional. CONVENTIONAL PHENOMENOLOGY.

**Prediction 3: Gaussian non-Markovian onset**

```
W(t) ≈ exp(−Γ_φ t − G t²/2)  for t ≪ τ_B
```

Parameter: G = k_rot·ω_rot²/τ_B — free.
Status: DERIVED. CONVENTIONAL PHENOMENOLOGY (any finite-memory bath).

**Prediction 4: K₀ spatial shape**

```
C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)
```

Parameter: ξ_c — free (unless Extension A).
Status: DERIVED (2D). CURRENTLY NOT DISCRIMINATING (M7/M9 degenerate on hardware).

**Prediction 5 [Extension A only]: ξ_c from material properties**

```
ξ_c = 2 · v_s(material) · τ_B
```

Parameters: v_s is fixed by material (Si: 6000 m/s), τ_B measured independently.
Status: THEORY EXTENSION (requires A-FPUT1). FORWARD PREDICTION conditional on
Extension A. CONVENTIONAL PHENOMENOLOGY (phonon bath gives same prediction).

**Prediction 6: P3 self-consistency**

```
c = ξ_c / (2τ_B) = constant across conditions
```

Status: DERIVED (tautology of kinetic theory). CONDITIONAL DISCRIMINATOR if c ≪ v_s.
Not a FORWARD PREDICTION — c is not predicted before measurement.

**Prediction 7 [telegrapher-specific]: Causal propagation wavefront**

```
C_Γ(r, t) = 0    for t < r/c
C_Γ(r, t) ≠ 0   for t > r/c
```

vs. any diffusion/OU bath (no wavefront — instantaneous correlations).

Status: DERIVED from telegrapher equation. POTENTIALLY DISCRIMINATING vs diffusion.
However: conventional PHONON BATH also has a causal wavefront at v_s.
Only discriminating vs. diffusion-type conventional models, not vs. phonon bath.

---

## RUNG 7 — Conventional Nulls (Per Prediction)

| Prediction | Conventional null | Null equivalent? |
|-----------|------------------|-----------------|
| Lorentzian S_JJ(ω) | OU bath (M2) | YES — identical |
| ω_rot² Ramsey | Flat-PSD bath | YES — identical |
| Gaussian NM onset | Any finite-memory bath | YES — identical |
| K₀ spatial shape | Power-law M7, two-bath M9 | YES — degenerate on hardware |
| ξ_c = 2v_s·τ_B | Acoustic phonon bath | YES — phonon bath gives same |
| P3 consistency (anomalous c) | None if c ≪ v_s | CONDITIONAL NO |
| Causal wavefront | Phonon bath (same wavefront) | YES for phonon null |

---

## RUNG 8 — Discriminating Experiment (Theory-First Design)

From the prediction ladder, the ONE surviving potential discriminator is:

**P3 consistency with anomalous c:**

IF the measured c = ξ_c/(2τ_B) is anomalously slow (≪ v_s = 6000 m/s for Si),
then no conventional mechanism explains it. But the theory does not predict
what c will be.

Under Extension A (c = v_s), P3 is NOT discriminating (phonon bath gives same ratio).

**For a discriminating experiment, the required theory-level step is:**

Find a physically motivated reason why c ≪ v_s — i.e., why the substrate
propagates much slower than acoustic phonons. This requires Extension B,
which found no credible candidate from existing C2.

**The prediction ladder breaks at Rung 0:**
The primitive ontology ("information substrate") is not identified with a
physical degree of freedom that would fix c to an anomalous value.
Until this identification is made (and is NOT the acoustic phonon),
the ladder produces only conventional phonon bath phenomenology under Extension A,
or remains underdetermined under the original C2.

---

## Summary of Chain Quality

| Rung | Content | Chain quality | Limiting step |
|------|---------|--------------|---------------|
| 0 | Primitive ontology | ASSUMED (A-FPUT1) | c, λ free |
| 1 | PRW dynamics | DERIVED (exact) | — |
| 2 | Telegrapher equation | DERIVED (exact) | — |
| 3 | Substrate correlations | DERIVED (2D analytic gap) | ξ_c free |
| 4 | Quantum coupling | ASSUMED (H_int form, g free) | g free |
| 5 | Qubit observables | DERIVED conditional | NMP hardware limit |
| 6 | Quantitative predictions | FREE parameters enter | No parameter-free prediction |
| 7 | Conventional nulls | All predictions matched | P3 conditionally survives |
| 8 | Discriminating experiment | Not reachable from current ontology | Need c ≪ v_s mechanism |

**The ladder is internally consistent and mathematically correct.**
**The critical break is at Rung 0: the substrate has no identified physical medium.**
**Under Extension A (acoustic phonons), the ladder terminates at Outcome B.**
**Under Extension B (slow modes), no ladder exists — the rung-0 identification is missing.**
