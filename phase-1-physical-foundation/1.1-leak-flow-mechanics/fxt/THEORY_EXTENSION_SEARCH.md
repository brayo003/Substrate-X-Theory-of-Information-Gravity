# THEORY_EXTENSION_SEARCH.md
## Systematic Investigation of Extensions A and B

**Date:** 2026-08-22
**Context:** FINAL_THEORY_PREDICTIVITY_AUDIT.md identifies two possible extensions
  to close GAP-7. This document evaluates both exhaustively and honestly.
**Label convention:** DERIVATION | THEORY EXTENSION | PARAMETER FIT |
  CONSISTENCY CHECK | FORWARD PREDICTION | CONVENTIONAL PHENOMENOLOGY |
  GENUINE DISCRIMINATOR

---

## Background

GAP-7 is confirmed: c (PRW propagation speed) is structurally free within
existing C2. The only non-trivial constraint found across all routes is:

    c ≤ v_s   [DERIVATION: C3 admissibility + FPUT dispersion, inequality]

And the new C5 closure finding:

    c = v_s   [THEORY EXTENSION: conditional on A-FPUT1 substrate assumption]

Two extension routes are investigated here.

---

## EXTENSION A: A-FPUT1 + C5 → c = v_s

### A.1 Does C5 really force c = v_s under A-FPUT1?

**The C5 argument (from FINAL_THEORY_PREDICTIVITY_AUDIT.md §3.4):**

Consider n±(x) defined as right/left-moving acoustic phonon action densities.
In the FPUT chain with harmonic dispersion ωₖ = 2√(K/m)|sin(πk/N)|, modes
split naturally into right-movers (∂ωₖ/∂k > 0) and left-movers (∂ωₖ/∂k < 0).
In the long-wavelength (k→0) acoustic limit, the group velocity → v_s = a√(K/m).

For P1 to satisfy C5 (closure: ∂_t n± expressible as function of n± alone):
The balance equations require that n± remain approximately closed under time evolution.
A mode with group velocity ≠ v_PRW would carry n± density at the wrong speed,
generating non-closed leakage terms.

Formally, consider a hypothetical PRW with v_PRW = αv_s (α ≤ 1). The projected
balance equations would be:

```
∂_t n⁺ + αv_s ∂_x n⁺ = −γ(n⁺ − n⁻) + L[n±]
```

where L[n±] are leakage terms from modes with group velocity ≠ αv_s. These
leakage terms are zero ONLY when α = 1 (acoustic limit) or α = 0 (diffusion
limit, but then closure fails differently: flux J = v(n⁺−n⁻) = 0 and the
spatial correlations disappear).

**Assessment of the C5 argument:**

The argument is correct in its logical structure but contains a subtlety.
C5 requires closure in the CONTINUUM LIMIT of the FPUT chain. In the true
continuum limit k→0, ALL acoustic modes have group velocity → v_s. The claim
is therefore:

  In the acoustic branch of the FPUT chain at long wavelengths,
  the only consistent PRW speed is v_s.

This is CORRECT — it is a consequence of the k→0 limit of the acoustic dispersion.

However: this does not mean the FPUT acoustic limit is the only possible substrate
for C2. The FPUT harmonic chain with acoustic phonons is one specific physical
realisation. C2 does not require this specific realisation from its CCA/SCC axioms.
A-FPUT1 is still a THEORY EXTENSION (not a DERIVATION).

**Verdict on A.1:**
YES — C5 forces v = v_s GIVEN A-FPUT1. The forcing is genuine (not merely compatible).
Classification: CONDITIONAL DERIVATION (condition = A-FPUT1 as substrate model).

### A.2 Additional equations available under Extension A

Under A-FPUT1 (c = v_s = a√(K/m)):

```
ξ_c = 2v_s·τ_B                    [FORWARD PREDICTION given τ_B]
D = v_s²·τ_B                       [FORWARD PREDICTION given τ_B]
ξ_c(material) = 2v_s(material)·τ_B [material-dependent, FORWARD PREDICTION]
ξ_c(T) = 2v_s(T)·τ_B(T)           [temperature-dependent, FORWARD PREDICTION]
```

Additionally, the FPUT Hamiltonian gives:

```
v_s = a√(K/m)
  Si: a = 5.43 Å, v_s ≈ 6000–8400 m/s (depending on polarization)
  Nb: v_s ≈ 3480 m/s
  Al: v_s ≈ 6420 m/s
  SiO₂: v_s ≈ 3750 m/s (longitudinal)
```

### A.3 Genuinely new quantitative predictions under Extension A

Under Extension A, the following predictions are made BEFORE measurement:

**Prediction A1: ξ_c from material properties and τ_B**

If τ_B is independently measured (from NM Ramsey curvature), the theory predicts:

```
ξ_c = 2 × v_s(material) × τ_B
```

This is a FORWARD PREDICTION — it can be tested by measuring the spatial
correlation length independently.

For Si substrate at τ_B = 1.2 µs: ξ_c = 2 × 6000 m/s × 1.2×10⁻⁶ s = 1.44 cm.

**Prediction A2: Material dependence of ξ_c**

Two identical experiments on chips with different substrate materials but
similar τ_B should give different ξ_c in proportion to v_s(material).

```
ξ_c(Si) / ξ_c(Nb) = v_s(Si) / v_s(Nb) ≈ 6000/3480 ≈ 1.72
```

This is a GENUINE FORWARD PREDICTION from Extension A.

**Prediction A3: Temperature dependence of ξ_c**

v_s(T) for Si decreases with temperature: Δv_s/v_s ≈ −6×10⁻⁵·ΔT (K⁻¹).
τ_B(T) depends on the defect/scattering rate γ(T).
The theory predicts ξ_c(T) = 2v_s(T)·τ_B(T) — both factors change with T.
If γ ∝ T^n (scattering from thermal phonons), then τ_B ∝ T^{-n} and:

```
ξ_c(T) ∝ v_s(T)·T^{-n}
```

This specific temperature dependence differs from an unconstrained bath model
(where ξ_c and τ_B can vary independently with temperature).

**Prediction A4: The causal propagation signature**

The telegrapher equation has a SHARP WAVEFRONT at r = v_s·t. Information
cannot propagate faster than v_s. An OU diffusion bath has NO wavefront —
correlations are established instantaneously. This is potentially measurable
as a finite delay in the onset of spatial correlations.

```
C_Γ(r, t) = 0    for t < r/v_s   (telegrapher causality)
C_Γ(r, t) ≠ 0   for t > r/v_s   (correlations arrive)
```

vs. the diffusion bath:

```
C_Γ(r, t) ≠ 0   for all t > 0   (instantaneous, exponentially small but nonzero)
```

This causal wavefront is a GENUINE DISCRIMINATOR between the telegrapher
substrate and any diffusion/OU bath model. It does not depend on the shape
(K₀ vs exponential) — it is a causal propagation effect.

### A.4 Are these predictions merely ordinary phonon physics?

**Critical test:** Does ordinary phonon bath decoherence predict the same
quantitative structure?

A conventional phonon bath couples qubits to phonons via the deformation
potential or piezoelectric coupling. The resulting decoherence has:
- Temporal correlation: the phonon propagator (not an OU process)
- Spatial correlation: the phonon propagator (not K₀)
- Causal propagation: YES — phonons propagate at v_s with a wavefront

**The causal wavefront (Prediction A4) is NOT distinctive:**
Conventional phonon bath models ALSO predict a causal wavefront at v_s.
A correlation between qubits mediated by phonons arrives at the speed of
sound. This is conventional phonon physics, not a C2-specific prediction.

**The material scaling (Prediction A2) is NOT distinctive:**
Any model where ξ_corr = v_acoustic·τ_corr would predict ξ_c ∝ v_s(material).
This is a consequence of phonon physics, not C2 specifically.

**The K₀ spatial shape IS distinctive (relative to OU bath):**
The K₀ shape differs from the phonon-bath Green's function. The phonon bath
spatial correlator is:

For a 2D phonon field: C_phonon(r) ∝ K₀(r/ξ_phonon) — SAME FORM as C2.

Wait — the phonon bath Green's function in 2D IS K₀. This means:

**A 2D acoustic phonon bath decoherence model gives EXACTLY the K₀ spatial
correlator predicted by C2.**

This is not a coincidence — it is because C2 is formally equivalent to a
classical random field (the telegrapher equation) propagating in 2D, and
the Green's function of the 2D telegrapher is K₀. The acoustic phonon
bath with the same geometry gives the same Green's function.

**Conclusion on Extension A:**

Extension A (c = v_s from A-FPUT1 + C5) produces:
- Correct and specific numerical predictions
- Material dependence (ξ_c ∝ v_s(material))
- Temperature dependence (ξ_c = 2v_s(T)·τ_B(T))
- Causal propagation signature (wavefront at v_s)

But NONE of these predictions distinguish C2 from a conventional 2D
acoustic phonon bath model. The K₀ spatial shape, the material scaling,
the causal wavefront, and the Lorentzian temporal spectrum are ALL
reproduced by a conventional phonon bath with the same geometry.

**Extension A Classification: CONVENTIONAL PHENOMENOLOGY**

Extension A makes C2 a specific conventional theory (acoustic phonon bath
with telegrapher/K₀ spatial correlations). This is physically well-motivated
and produces testable predictions. But it does not produce a GENUINE
DISCRIMINATOR between C2 and conventional phonon physics.

Extension A outcome: **Outcome B — C2 can become predictive, but its
predictions remain conventionally equivalent.**

---

## EXTENSION B: c ≪ v_s — Search for a Slow-Mode Substrate

### B.1 Requirement for Extension B

For c ≪ v_s, a substrate satisfying C2/C5 must have:
1. A physical degree of freedom propagating at c ≪ v_s
2. C5 closure: n± fields closed under the dynamics at this speed
3. Coupling to qubit dephasing as J·σ_z (or equivalent)
4. Sufficient amplitude to produce measurable decoherence correlation
5. Temperature/material dependence differing from ordinary phonons

If such a substrate exists, the P3 test (c = ξ_c/(2τ_B) ≪ v_s) would be
GENUINELY ANOMALOUS — no conventional phonon or EM mechanism produces
a substrate propagating at ~10–500 m/s.

### B.2 The C5 closure requirement for slow modes

For a PRW at speed c ≪ v_s to satisfy C5, the n± fields must be approximately
closed under the dynamics. This means:

The physical degrees of freedom making up n± must propagate at speed ≈ c.
If n± is defined over modes with a specific group velocity c, then C5 holds
for that definition, provided those modes form an approximately closed set.

**For what mode types is this possible?**

In condensed matter, modes with group velocity ≪ v_acoustic include:
1. FLAT-BAND modes: optical modes, Einstein modes (v_g ≈ 0)
2. TOPOLOGICAL edge modes: can be slow with specific dispersion
3. DEFECT-MEDIATED HOPPING: random walk of excitations between defect sites
4. LONG-WAVELENGTH OPTICAL PHONONS: v_g → 0 at zone boundary
5. SOFT MODES near phase transitions: v_g → 0 at critical point
6. SPIN WAVES (magnons) in ferromagnets: v_g ~ c·(a·k)/1 ≪ v_s at low k
7. SUBSTRATE POLARITONS: phonon-photon coupled modes with small group velocity
8. TWO-LEVEL SYSTEM (TLS) tunneling: classical random walk between TLS states
9. QUASIPARTICLE DIFFUSION: fermionic quasiparticles in BCS-like description

Each must be evaluated against the C5 closure requirement.

### B.3 Candidate analysis

**Candidate B.1: Optical phonon modes**

Dispersion: flat band near zone boundary, v_g → 0.
Group velocity near zone center: v_optical ≈ (∂²ωₖ/∂k²)·k → 0 at k=0.
For Si: optical branch has v_g ≈ 0 at k→0.

C5 closure test: Can n± be defined for optical modes?
Optical phonons have alternating displacement pattern (n± = right/left displacement).
The k→0 group velocity is zero — the mode is non-propagating in this limit.

A non-propagating mode (v_g = 0) would give c = 0, not c ≪ v_s.
For finite k: v_g ≠ 0 but the mode description is not covariant (not a PRW
on the chip scale — the spatial scale is the unit cell).

**Status: FAILS C5 for a useful PRW. Optical modes at k→0 give v = 0 (diffusion),
not a finite slow speed. REJECTED.**

**Candidate B.2: Defect-mediated random walk**

In a 2D chip substrate with two-level system (TLS) defects, excitations can
hop between TLS sites. The effective propagation speed of such a random walk is:

```
c_TLS = d_TLS² · γ_hop / d_TLS = d_TLS · γ_hop
```

where d_TLS is the inter-defect spacing and γ_hop is the hopping rate.

For TLS in amorphous SiO₂ with d_TLS ~ 1–10 nm and γ_hop ~ 10⁸–10¹⁰ s⁻¹:
c_TLS ~ 0.1–100 m/s — this is in the range c ≪ v_s.

C5 closure test: Do TLS excitation density fields n± close under the dynamics?

In a random walk model on a 1D chain of TLS, the continuum limit gives the
diffusion equation (τ → 0, c → 0 with D = c²τ fixed). Not a telegrapher
equation. For the telegrapher to emerge from TLS, the hop must be persistent
(correlated direction) — a TLS where the excitation retains its propagation
direction for τ_B before reversing.

Is this physically motivated? A TLS excitation that propagates preferentially
in one direction would require a spatial bias or coherence. In an isotropic
amorphous substrate, TLS hopping is isotropic with no preferred direction.
Therefore the TLS random walk is a simple (non-persistent) random walk → diffusion,
not a telegrapher.

For persistent random walk to emerge from TLS, each TLS would need to
"remember" its previous hop direction for time τ_B. This is equivalent to
saying the TLS has memory — i.e., the TLS excitation is a coupled quantum-classical
object, not a simple hop process.

**Assessment:** TLS defects can produce c ≪ v_s effective speeds, but the
PRW/telegrapher structure (which gives K₀, not Gaussian/diffusive correlations)
requires persistent hopping with memory τ_B. This is not ruled out but is
also not derived from existing C2 — it would require a model of TLS dynamics
that produces persistent random walk. This is a new physical model not in C2.

**Status: POSSIBLE physically, NOT DERIVED from existing C2. Requires new model.**

**Candidate B.3: Topological edge modes**

Topological insulators and certain quantum matter have edge/surface modes
with specific group velocities. In 2D topological systems, chiral edge modes
propagate at v_edge.

For a superconducting chip substrate: the chip is not a topological material.
No topological edge modes are expected in Si, Al, or Nb under the relevant
conditions. This is speculative and has no motivation from existing C2.

**Status: SPECULATIVE. No motivation from C2. REJECTED.**

**Candidate B.4: Soft modes near a critical point**

Near a structural phase transition, acoustic modes soften: v_g → 0 at the
critical temperature T_c. This gives c ≪ v_s in the vicinity of T_c.

For superconducting chips: Si has no relevant structural phase transition
near the dilution refrigerator operating temperature (~15 mK). Nb has a
superconducting transition at ~9 K, but this is an electronic phase transition,
not a structural one.

**Status: Not applicable to typical chip operating conditions. REJECTED.**

**Candidate B.5: Diffusion-like transport with effective "persistence"**

In strongly disordered systems, diffusion can cross over to sub-diffusion.
The mean-square displacement follows ⟨x²(t)⟩ ∝ t^α with α < 1 (anomalous
diffusion). This produces a characteristic spatial scale related to the diffusion
coefficient D_eff.

The effective "speed" in anomalous diffusion: c_eff = D_eff / ξ_corr.
For highly disordered substrates: D_eff ≪ D_phonon, giving c_eff ≪ v_s.

But: anomalous diffusion does NOT produce the telegrapher/PRW structure.
It gives a fractional diffusion equation, not the telegrapher equation.
The correlator would be a stretched exponential or power-law, not K₀.
C5 closure would fail for the PRW structure.

**Status: Produces c_eff ≪ v_s but NOT the telegrapher equation. REJECTED for C5.**

**Candidate B.6: Spin-wave (magnon) modes**

In ferromagnetic materials, spin waves have dispersion ωₖ = Dk² (quadratic,
low-k) or ωₖ = v_sw·k (linear for antiferromagnets). For ferromagnets:

```
v_g = ∂ωₖ/∂k = 2Dk → 0 as k → 0
```

The spin-wave speed at the relevant macroscopic scale is zero — diffusive.
In antiferromagnets: v_g ≈ v_sw = J·S·a/ℏ ≈ 10³–10⁴ m/s, which is in the
interesting range.

However: superconducting chips use Al, Nb, Si, and SiO₂ — none of which
are ferromagnetic or antiferromagnetic. Spin waves are not relevant for
current quantum computing hardware.

**Status: Not applicable to standard chip materials. REJECTED for hardware relevance.**

**Candidate B.7: Slow substrate via circuit-mediated coupling**

In a superconducting circuit chip, microwave photons propagate at c_MW ≈ 10⁸ m/s
(slowed by dielectric) in transmission lines. This is too fast for c ≪ v_s.

But: circuit-mediated coupling between distant qubits through resonators
creates an effective interaction that propagates at the group velocity of
the resonator mode. For heavily loaded resonators: v_eff = c_MW/√(1+χ) where
χ is the dispersive coupling. For strong coupling: v_eff can be significantly
reduced.

Typical values: v_eff ~ 10⁷–10⁸ m/s. Still >> v_s by 4–5 orders of magnitude.
Not in the c ≪ v_s range of interest.

**Status: v_eff >> v_s. REJECTED.**

**Candidate B.8: Thermal diffusion**

Heat diffusion in the chip follows ∂T/∂t = D_T ∇²T where D_T = κ/(ρC_p).
For Si at 15 mK: κ ≈ 0.01 W/(m·K), ρ = 2330 kg/m³, C_p ≈ 10⁻⁶ J/(kg·K).
D_T ≈ 4 m²/s.

Thermal diffusion is not a wave process — it has no wavefront.
The "speed" of thermal diffusion to scale L: v_thermal = D_T/L.
For L = 1 mm: v_thermal ~ 4000 m/s ≈ v_s. Not interesting.
For L = 1 cm: v_thermal ~ 400 m/s — in the interesting range.

But: thermal diffusion is a diffusion equation, not a telegrapher.
No persistent random walk → no K₀ correlator.
Also: thermal fluctuations at 15 mK are negligibly small for decoherence purposes.

**Status: Not a telegrapher structure. REJECTED for C5.**

**Candidate B.9: TLS coherent tunneling — quantum slow modes**

Individual TLS in amorphous substrates tunnel coherently between two positions.
The coherent tunneling can produce a standing-wave-like spatial correlation.
The effective speed of quantum TLS tunneling: v_TLS ~ Δ·d/ℏ where Δ is the
tunnel splitting and d is the TLS size (~Å scale).

For typical TLS: Δ ~ 1–100 GHz, d ~ 0.1–1 nm:
v_TLS ~ (10¹⁰ s⁻¹ × 10⁻¹⁰ m) ~ 1 m/s

This is extremely slow — in the range c ≪ v_s.

However: a single TLS produces a standing wave, not a propagating mode.
For a PROPAGATING mode from TLS, one needs a chain of TLS that can transfer
excitations coherently. This requires a mechanism for TLS-TLS coupling that
preserves phase. In amorphous substrates, TLS-TLS coupling is weak and
incoherent at the ~mm scale relevant for qubit-qubit correlations.

**Status: Individual TLS give c ~ 1 m/s but not a propagating 2D field.
No mechanism for spatial propagation across chip scale. WEAKLY MOTIVATED.**

---

### B.4 Summary of Extension B candidates

| Candidate | c range | C5 closure | Mechanism | Status |
|-----------|---------|------------|-----------|--------|
| Optical phonons | 0 (flat band) | No (non-propagating) | Flat dispersion | REJECTED |
| TLS defect hopping | 0.1–100 m/s | No (diffusion) | Random walk | REQUIRES NEW MODEL |
| Topological modes | Unknown | Unknown | No chip motivation | REJECTED |
| Soft mode at T_c | 0 near T_c | Possible | Not at chip conditions | REJECTED |
| Anomalous diffusion | Effective slow | No (fractional PDE) | Disordered substrate | REJECTED |
| Spin waves | 10³–10⁴ m/s | Possible | Not in chip materials | REJECTED |
| Circuit slow modes | 10⁷–10⁸ m/s | Unknown | Too fast | REJECTED |
| Thermal diffusion | Effective slow | No (diffusion PDE) | Diffusion, not wave | REJECTED |
| TLS coherent tunneling | ~1 m/s | No (not 2D propagating) | No spatial propagation | WEAKLY MOTIVATED |

**No candidate passes all requirements simultaneously.**

The closest candidate is TLS-mediated propagation (Candidate B.2/B.9), which
can produce c ~ 1–100 m/s. But it requires a new model (persistent random walk
from TLS with spatial memory) not derivable from existing C2. This would be
a NEW THEORY EXTENSION, not a derivation.

---

## Overall Assessment of Extensions A and B

**Extension A:**
- c = v_s is conditionally derived (A-FPUT1 + C5)
- Produces specific predictions: ξ_c = 2v_s·τ_B, material scaling, causal wavefront
- ALL predictions are reproduced by conventional 2D acoustic phonon bath models
- Outcome: CONVENTIONAL PHENOMENOLOGY (Outcome B from decision tree)
- The K₀ spatial correlator IS the 2D phonon bath Green's function — they are identical

**Extension B:**
- No physically motivated substrate with c ≪ v_s AND C5 closure AND chip relevance found
- TLS-based mechanisms are possible but require a new model with persistent hop dynamics
- That new model would be a different theory extension, not a consequence of existing C2
- Outcome: No physically credible extension found from existing C2 structure

**The Gap-7 problem under Extension B is not solved by Extension A.**
Extension A produces the wrong c for a genuinely discriminating measurement.
Extension B finds no mechanism.

---

## Conclusion

**Neither Extension A nor Extension B produces a GENUINE DISCRIMINATOR** — a
prediction that distinguishes SXC-IGC from all physically plausible conventional
mechanisms.

Extension A makes C2 physically equivalent to a conventional 2D acoustic phonon
bath model with telegrapher (not diffusion) dynamics.

Extension B finds no physically credible mechanism for c ≪ v_s within existing C2.

Decision tree result: **Outcome B** (Extension A) and **Outcome E** (Extension B).

The combined outcome of both extensions is: **Outcome B/E** — C2 can become
predictive (Extension A) but its predictions remain conventionally equivalent,
and no physically credible extension producing genuine discrimination was found.
