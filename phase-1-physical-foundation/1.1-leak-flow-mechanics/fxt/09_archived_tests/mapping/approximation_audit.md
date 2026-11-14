# Approximation Audit: Did Any Derivation Step Discard the Quantum Coupling?

**Status:** Theory laboratory — audit branch  
**Frozen references (immutable):**
- `COMPLETE_MASTER_EQUATION.md`
- `UNIFIED_PERTURBATIVE_DERIVATION.md`
- `mapping/mapping_derivation.md`
- `mapping/extension_derivation.md`

**Date:** 2026-07-20  
**Question:** The derivation made seven approximations [A1]–[A7] to arrive at
`δJ = s₀(ω×r)` and `Γ = Γ₀ + k_rot ω²`. Each approximation was justified for its
original purpose (orbital gravity, precession). This document asks a different question
for each one: **Was the approximation also valid for quantum systems, or did it
accidentally remove a coupling term that acts on internal quantum degrees of freedom?**

---

## Audit Methodology

For each approximation [Ak]:

1. **State the term(s) discarded** — exactly, from [ME].
2. **State the original justification** — why it was applied.
3. **Identify the discarded term's quantum relevance** — does it contain structure that could couple to internal (spin/phase) degrees of freedom differently from spatial rotation?
4. **Test the validity condition** — compare the characteristic scale of the discarded term against the characteristic scale of quantum coherence effects.
5. **Verdict** — one of:
   - **VALID FOR QUANTUM SYSTEMS:** The approximation is equally valid for quantum systems. The term it discards is negligible in the quantum regime.
   - **INVALID — TERM SURVIVES:** The approximation discards a term that may be non-negligible in the quantum regime. The full term must be carried.
   - **INVALID — TERM CARRIES NEW STRUCTURE:** The discarded term introduces qualitatively new structure absent in the surviving terms.

The audit does not modify any equation. It determines whether retaining the full
un-approximated equation changes the coupling to quantum systems.

---

## Master Equation (Reference)

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u)
                    + αE + β∇·(E v_sub) + γF − σ_irr    [ME]
```

---

## Audit A1 — Steady-State Approximation (∂s/∂t = 0, ∂²s/∂t² = 0)

### A1.1 Terms Discarded

Setting all time derivatives to zero removes the entire left-hand side of [ME]:

```
Discarded: τ ∂²s/∂t² + ∂s/∂t                           [A1-disc]
```

These are the inertia term (τ ∂²s/∂t²) and the relaxation term (∂s/∂t).

### A1.2 Original Justification

For orbital mechanics, the relevant timescale is the orbital period T_orb. For Mercury, T_orb ≈ 88 days. The substrate relaxation time τ is asserted to satisfy:

```
τ ≪ T_orb
```

so the system relaxes to quasi-static equilibrium at each orbital phase. The steady-state approximation is valid when ωτ ≪ 1 where ω here means the orbital angular frequency.

### A1.3 Quantum Relevance

A quantum system has characteristic internal timescales:
- **Larmor precession period:** T_L = 2π/ω_q where ω_q is the qubit transition frequency, typically 2π × 5 GHz ⟹ T_L ≈ 0.2 ns.
- **Coherence time:** T₂ ≈ 10 μs–1 ms for state-of-the-art superconducting qubits.
- **Gate timescale:** T_gate ≈ 10–100 ns.

The validity condition for [A1] applied to a quantum system is:

```
τ ≪ T_quantum_internal
```

**If τ ≫ T_L (qubit precession period):** The steady-state approximation fails. The substrate field does not relax between qubit precession cycles. In this regime, the substrate field oscillates at the qubit frequency and the time-derivative terms generate resonant driving of the substrate field.

**Estimating τ:** The frozen theory does not provide an independent measurement of τ. The only constraint is τ ≪ T_orb ~ 10⁷ s, which is satisfied by any τ ≲ 10⁶ s. This is compatible with τ ≫ T_L ~ 10⁻¹⁰ s.

**The audit finding:** If τ ≳ T_L, then the substrate field does not relax between qubit oscillation cycles. The [A1]-discarded terms become:

```
τ ∂²s/∂t² + ∂s/∂t  →  −τ ω_q² s₁e^{iω_q t} + iω_q s₁e^{iω_q t}    [A1-qm]
```

for a field oscillating at ω_q. These are non-negligible when τ ω_q ≳ 1, i.e.:

```
τ ≳ 1/ω_q ≈ 3 × 10⁻¹¹ s   (for 5 GHz qubit)                         [A1-cond]
```

This is a very weak condition. Any τ larger than ~30 picoseconds would make the time-derivative terms relevant at qubit frequencies.

### A1.4 What the Retained Terms Produce

Retaining [A1-disc] for a field component oscillating at ω_q gives the full equation for the oscillating part s_q(r) e^{iω_q t}:

```
(−τ ω_q² + iω_q) s_q = c²τ ∇²s_q − ∇·(s_q v_sub)                   [A1-full]
```

Compared to the steady-state equation c²τ ∇²s_q = ∇·(s_q v_sub), the left-hand side adds an effective frequency-dependent mass:

```
m_eff(ω_q) = τ ω_q² − iω_q                                           [A1-meff]
```

This modifies the dispersion relation of the substrate field. At frequencies ω_q ≫ 1/τ, the field equation changes character: from a diffusion-dominated regime (slow relaxation) to an oscillation-dominated regime (substrate stores and releases energy at the qubit frequency).

**Does this produce a quantum coupling?** The field s_q(r) is still a classical scalar. The oscillation at ω_q is imposed by the quantum system's energy (through the αE source term, if retained — see A2 audit). Retaining [A1-disc] changes the *amplitude* and *phase* of the substrate response at ω_q but does not by itself introduce operator structure.

**However:** The combination of retaining [A1-disc] AND retaining the αE source term (which [A2] discards) creates a resonant substrate response at the qubit frequency. This is audited in A2.

### A1.5 Verdict on A1

**INVALID FOR QUANTUM SYSTEMS — TERM SURVIVES.**

The steady-state approximation is valid for orbital mechanics (τ ≪ T_orb). It is not automatically valid for quantum systems where ω_q τ ≳ 1 is physically plausible. Retaining [A1-disc] changes the substrate response at quantum frequencies, but does not by itself introduce a new structural coupling. The full effect requires retaining A2 simultaneously.

**Scale at which A1 becomes relevant:**
```
ω_q τ ≳ 1  ⟹  τ ≳ 1/ω_q ≈ 3×10⁻¹¹ s                               [A1-scale]
```

---

## Audit A2 — Source-Free Approximation (E = 0, F = 0, σ_irr = 0)

### A2.1 Terms Discarded

Setting all sources to zero removes:

```
Discarded: αE + β∇·(E v_sub) + γF − σ_irr                           [A2-disc]
```

### A2.2 Original Justification

The quantum system (qubit) is treated as a probe — it has negligible mass-energy compared to the gravitating body. In the exterior region surrounding the gravitating body, there are no distributed sources; the mass-energy is a boundary condition at the source, not a distributed term in the domain. The approximation is justified by the scale separation between the gravitating body (GM/c² ≈ 1.5 km for the Sun) and the orbital scale (~10¹¹ m).

### A2.3 Quantum Relevance

A quantum system has a rest energy E_q = ℏω_q per quantum of excitation. At a qubit frequency ω_q = 2π × 5 GHz, this corresponds to:

```
E_q = ℏω_q ≈ 1.055 × 10⁻³⁴ × 3.14 × 10¹⁰ ≈ 3.3 × 10⁻²⁴ J         [A2-Eq]
```

The coupling strength of this energy to the substrate field is:

```
α E_q ≈ α × 3.3 × 10⁻²⁴ J                                           [A2-src]
```

where α has units info/(J·s). The source term α E_q has units info/(m³·s) — the same as ∂s/∂t — so it is the rate at which the qubit's energy creates information density.

**Critical observation:** The source term αE is NOT negligible for a quantum system even when it is negligible for a test particle in an orbital context. The orbital justification was that the test particle (e.g., Mercury) is a *probe* that does not disturb the background. But a quantum system that *transitions between energy eigenstates* changes its energy density E at the transition frequency ω_q. This change is:

```
ΔE_q(t) = ℏω_q |⟨e|ψ(t)⟩|² × (1/V_eff)                            [A2-delta-E]
```

where V_eff is the effective volume of the quantum system. This is a *time-oscillating* energy source at frequency ω_q.

**The discarded source term for a transitioning qubit:**

```
αE → α (ℏω_q/V_eff) |⟨e|ψ(t)⟩|² = (α ℏω_q/V_eff) P_e(t)          [A2-src-qm]
```

where P_e(t) = |⟨e|ψ(t)⟩|² is the excited-state population. This oscillates at frequency ω_q during a Rabi drive: P_e(t) = sin²(Ω_R t / 2).

**This is NOT negligible.** It is the rate at which the qubit creates information density in the substrate at the Rabi frequency. It was discarded in [A2] because there was no quantum source in the original orbital problem. For a quantum system, the source is real and time-varying.

### A2.4 The Retained A2 Source Equation

With A2 source terms retained, the substrate equation for the qubit-frequency component is (combining with [A1-full]):

```
(−τ ω_q² + iω_q) s_q(r) = c²τ ∇²s_q − ∇·(s_q v_sub) + α ℏω_q P_e / V_eff
                                                                      [A2-full]
```

This is a driven wave equation for the substrate field at the qubit frequency. The source is the qubit's instantaneous excited-state population P_e(t) = |⟨e|ψ(t)⟩|².

**This equation contains quantum information.** The source term depends on P_e(t), which is determined by the qubit's quantum state |ψ(t)⟩. The substrate field s_q(r,t) is therefore *driven by the quantum state of the qubit*.

**The back-action question:** The substrate field s_q then feeds back onto the qubit through the force coupling γF (if F ≠ 0) or through the constitutive coupling rules CA-1, CA-2, CA-3 of the frozen theory. But those back-action terms are in the source-free region that [A2] also discards.

**Important structural finding:** Even without the back-action, the substrate field carries quantum information (P_e oscillates according to the quantum state). A second quantum system interacting with the same substrate field at overlapping spatial support would be affected by the first system's state through the substrate. This is a substrate-mediated quantum coupling — but it requires both retaining [A2-disc] AND specifying the spatial mode overlap.

### A2.5 The γF Term Specifically

The force coupling γF is of particular interest. In the decoherence derivation, the force F is the force on the quantum system. For a rotating quantum system:

```
F = m ω × (ω × r) + ...  (centrifugal) + m ω̇ × r  (Euler)         [A2-force]
```

These are classical frame forces. But for a quantum system in a superposition of energy eigenstates, there is also a quantum force arising from the gradient of the potential energy:

```
F_q = −∇⟨ψ|H_q|ψ⟩                                                   [A2-Fq]
```

where H_q is the qubit Hamiltonian. This force depends on the quantum state |ψ⟩ and is not zero even for a stationary qubit. It was discarded by [A2] along with all other F terms.

If γF is retained with F = F_q, the substrate equation gains a source term proportional to −∇⟨ψ|H_q|ψ⟩, which depends on the quantum state through the expectation value of H_q.

### A2.6 Verdict on A2

**INVALID FOR QUANTUM SYSTEMS — TERM CARRIES NEW STRUCTURE.**

The source-free approximation [A2] was justified for orbital test particles that do not have time-oscillating energy densities. A quantum system in a superposition of energy eigenstates has a time-oscillating energy density at the transition frequency ω_q. Retaining [A2-disc] reveals:

1. The substrate field is driven by the qubit's excited-state population P_e(t).
2. The force term γF, if retained, carries a quantum-state-dependent force F_q = −∇⟨ψ|H_q|ψ⟩.
3. The combination produces a substrate-mediated coupling between quantum systems occupying the same spatial region.

**This does not automatically produce a back-action Hamiltonian** (the extension audit found that back-action requires P3). But it establishes that the substrate field is *informed* by the quantum state in a way that [A2] completely erases.

**The specific discarded coupling:**

```
Γ∗-correction = γ ⟨F_q⟩ × (substrate response function)            [A2-miss]
```

This correction to the decoherence rate depends on the gradient of the qubit energy — a term absent from the frozen derivation because [A2] removes all force sources.

---

## Audit A3 — Coherence Transport Neglected (χsu dropped)

### A3.1 Terms Discarded

```
Discarded: −∇·(χ s u)                                               [A3-disc]
```

This is the directed coherence transport term. The full current is J = s v_sub + χ s u; [A3] retains only J = s v_sub.

### A3.2 Original Justification

The justification in the frozen derivation is:

> "χ/|v_sub| is assumed small in the Newtonian regime (supported by the weak-field hierarchy in master-equation-first-principles.md)."

This is a magnitude argument: the coherence speed χ is small compared to the substrate flow speed |v_sub| ≈ μ/r² in the orbital regime.

### A3.3 What χsu Physically Encodes

The term −∇·(χsu) represents directed coherent transport of information density in direction u. The direction u is a unit vector field. Its divergence ∇·u measures the spreading of the coherence direction field.

The key question is: **what is u?**

In `COMPLETE_MASTER_EQUATION.md`, u is defined as the "coherent propagation direction (unit vector)." It is not further specified in the frozen derivation. The extension audit (Candidate B) found that for a classical, fixed u field, the term χsu is purely classical.

**However:** For a quantum system, the coherence direction u is not arbitrary. It should be associated with the direction in which quantum coherence propagates. For a qubit in a superposition state |ψ⟩ = α|0⟩ + β|1⟩, the Bloch vector:

```
n̂ = ⟨ψ|σ̂|ψ⟩ = (⟨σ_x⟩, ⟨σ_y⟩, ⟨σ_z⟩)                             [A3-bloch]
```

is the natural quantum coherence direction. It is a unit vector (for a pure state) that rotates on the Bloch sphere at the Larmor frequency.

**The audit question:** Is u ≡ n̂ (the Bloch vector) a valid identification within the master equation, and if so, what does −∇·(χ s n̂) contribute to the decoherence calculation?

### A3.4 If u = n̂ (Bloch Vector)

If the coherence direction u is identified with the qubit's Bloch vector n̂, then:

```
−∇·(χ s u) = −∇·(χ s n̂)
            = −χ(∇s · n̂ + s ∇·n̂)                                  [A3-qm]
```

For a spatially uniform quantum system (qubit localized at one point), n̂ does not vary in space, so ∇·n̂ = 0. The surviving term is:

```
−χ ∇s · n̂                                                           [A3-qm2]
```

This term directs information transport along the Bloch vector. Its contribution to the substrate equation is:

```
Retained A3 term in [SS]: +χ (∇s · n̂)                              [A3-SS]
```

In the perturbation hierarchy, at first order this adds a source to [P1]:

```
c²τ ∇²s₁ = −v·∇s₀ − χ (∇s₀ · n̂)                                  [A3-P1]
```

The additional source is χ (∇s₀ · n̂) = χ (−μ/r²) (r̂ · n̂) — a dipole source aligned with n̂ instead of v.

**The new structure:** The frozen derivation has s₁ aligned with v (the particle velocity direction). Retaining [A3-disc] adds a component of s₁ aligned with n̂ (the Bloch vector direction). These are generally different directions:
- v is in the orbital plane.
- n̂ rotates on the Bloch sphere at the Larmor frequency ω_q.

The coherence-transport-driven component of s₁ is:

```
s₁^{(χ)} ~ (χ μ / c²τ r) (r̂ · n̂)                                  [A3-s1chi]
```

This has the same angular structure as the frozen s₁ but oriented along n̂ rather than v.

### A3.5 Scale Comparison: χ Term vs Orbital Term

The frozen derivation discards [A3-disc] when χ/|v_sub| ≪ 1. But for the quantum coherence calculation, the relevant comparison is different:

**For orbital mechanics:** The source term v·∇s₀ ∼ v μ/r². The discarded term χ ∇s₀·n̂ ∼ χ μ/r². Their ratio is χ/v — the [A3] condition.

**For quantum coherence:** The relevant coupling is through the current perturbation δJ. The frozen δJ = s₀(ω×r) comes from the rotating-frame term. The coherence-transport contribution to δJ is:

```
δJ^{(χ)} = χ s₁^{(χ)} n̂ ~ (χ²μ/c²τr) n̂                           [A3-dJ]
```

For the decoherence rate, what matters is whether δJ^{(χ)} is comparable to the frozen δJ = s₀(ω×r):

```
|δJ^{(χ)}| / |δJ| ~ (χ²μ/c²τr) / (s₀ ωr) = χ²/(c²τωr)           [A3-ratio]
```

For a laboratory quantum system, ω ~ 10²–10⁶ rad/s, r ~ 10⁻⁶ m (qubit scale). If χ is of order the coherence speed in the quantum vacuum (possibly large), the ratio [A3-ratio] could be significant.

**The audit finding:** The term [A3-disc] introduces a component of the substrate current directed along the Bloch vector n̂. If n̂ is a valid identification for u, this term produces a decoherence contribution proportional to χ²|n̂|² that depends on the orientation of the Bloch vector — i.e., on the qubit's quantum state.

### A3.6 The Validity Condition for A3 in the Quantum Regime

The condition χ/|v_sub| ≪ 1 was established for orbital scales where |v_sub| = μ/r² ≈ GM_sun/r²_Mercury ≈ 4 × 10⁻³ m/s² × r.

For a laboratory quantum system, there is no large gravitating body. The substrate flow v_sub at the laboratory is dominated by Earth's gravity: |v_sub| ~ GM_Earth/r²_Earth ≈ 9.8 m/s² × τ ~ 9.8τ m/s. For τ ~ 10⁻¹⁰ s, |v_sub| ~ 10⁻⁹ m/s — extremely small.

In this regime, χ/|v_sub| is NOT necessarily small. If χ has any finite value, the coherence transport term dominates the advection term in the laboratory, precisely reversing the hierarchy assumed in [A3].

### A3.7 Verdict on A3

**INVALID FOR QUANTUM SYSTEMS — TERM CARRIES NEW STRUCTURE.**

The justification for discarding χsu (χ/|v_sub| ≪ 1) applies to the orbital regime where v_sub is large. In the laboratory quantum regime, v_sub is negligibly small (Earth gravity only), and χ/|v_sub| may be much larger than 1. The discarded term introduces:

1. A substrate current component directed along the coherence direction u.
2. If u = n̂ (Bloch vector), this component is quantum-state-dependent.
3. The resulting decoherence contribution depends on the qubit's quantum state, not just on the mechanical rotation ω.

**This is the most significant finding of the audit.** The coherence transport term was discarded with a justification that is valid for gravity but invalid for laboratory quantum systems. The term contains qualitatively new structure (quantum-state orientation of u) that is absent from δJ = s₀(ω×r).

---

## Audit A4 — Low-Velocity Expansion (|v|/c ≪ 1, |v_sub|/c ≪ 1)

### A4.1 Terms Discarded

[A4] permits expanding s in powers of ε = v/c. Keeping only ε ≤ 2:

```
Discarded: s₃, s₄, ... — all terms O(v³/c³) and above             [A4-disc]
```

### A4.2 Original Justification

Mercury's orbital speed ≈ 48 km/s ≪ c = 3×10⁸ m/s gives ε ≈ 1.6×10⁻⁴. Terms of order ε³ are smaller by an additional factor of 1.6×10⁻⁴ — negligible for precession calculations.

### A4.3 Quantum Relevance

For a quantum system with an effective "velocity" v_q = ℏ/m_eff r (de Broglie velocity), the relevant small parameter is:

```
ε_q = v_q/c = ℏ/(m_eff r c)                                         [A4-eps]
```

For an electron in a hydrogen-like atom: ε_q ≈ α_fine ≈ 1/137 (fine structure constant). For a superconducting qubit (mass ~ electron mass, confined in ~100 nm box):

```
ε_q ≈ ℏ/(m_e × 10⁻⁷ × 3×10⁸) ≈ 10⁻³⁴ / (9×10⁻³¹ × 3×10) ≈ 4×10⁻⁶
```

This is even smaller than Mercury's ε. So the truncation is well-justified for the center-of-mass motion of the qubit.

**However:** For internal transitions, the relevant velocity is not the center-of-mass velocity but the velocity associated with the photon field. A qubit emitting a photon at ω_q has an energy flux that propagates at c. The relevant dimensionless parameter for the photon-substrate coupling is ω_q r/c, where r is the system size:

```
ε_photon = ω_q r/c ≈ (3×10¹⁰ rad/s × 10⁻⁷ m) / (3×10⁸ m/s) = 10⁻⁵   [A4-ph]
```

This is small, so [A4] is valid for photon-scale effects too.

### A4.4 Verdict on A4

**VALID FOR QUANTUM SYSTEMS.**

The low-velocity expansion is valid for all known quantum systems because ε_q ≪ 1 is well-satisfied for both center-of-mass motion and internal transition photon fields. The discarded O(ε³) terms are smaller by at least 10⁻⁴–10⁻⁶ relative to the retained O(ε²) terms. This approximation does not discard any coupling relevant to quantum systems.

**Caveat:** This conclusion holds for non-relativistic quantum systems. For relativistic quantum fields (e.g., quantum electrodynamics vacuum fluctuations), ε ~ 1 and the expansion would break down. But for the qubit systems under consideration, the non-relativistic limit is well justified.

---

## Audit A5 — Incompressible Substrate Flow (∇·v_sub ≈ 0)

### A5.1 Terms Discarded

Applying ∇·v_sub = 0 to the advection divergence:

```
∇·(s v_sub) = v_sub·∇s + s ∇·v_sub  →  v_sub·∇s   (∇·v_sub term dropped)
```

Discarded:

```
Discarded: s ∇·v_sub                                                [A5-disc]
```

### A5.2 Original Justification

For a Keplerian orbit, the substrate flow v_sub = −(μ/r²) r̂ has divergence:

```
∇·v_sub = (1/r²) d/dr(r² × (−μ/r²)) = (1/r²) d/dr(−μ) = 0   (for r > 0)
```

The flow is exactly divergence-free away from the origin. [A5] is exact for the Newtonian background flow, not an approximation.

### A5.3 Quantum Relevance

The substrate flow in a laboratory setting (no large gravitating body nearby) is dominated by Earth's gravitational field. For a qubit on Earth's surface:

```
v_sub ≈ −(GM_Earth/r_Earth²) r̂ × τ ≈ −9.8τ r̂   (m/s)
```

The divergence of this uniform-direction radial field at the qubit location (treating Earth as a boundary condition) is approximately zero at the qubit scale.

For any substrate flow that is the gradient of a potential (v_sub = ∇Φ for some Φ), the incompressibility condition requires ∇²Φ = 0. At points away from mass sources, this is satisfied exactly by the Newtonian potential. At the qubit location, there are no local mass sources, so ∇·v_sub = 0 holds exactly.

### A5.4 Verdict on A5

**VALID FOR QUANTUM SYSTEMS.**

The incompressibility condition ∇·v_sub = 0 is exact (not an approximation) at any point away from a gravitating mass, which includes all laboratory qubit locations. The discarded term s ∇·v_sub is identically zero in the source-free exterior region. This approximation does not discard any coupling.

---

## Audit A6 — Second-Order Truncation (O(v³/c³) and above dropped)

### A6.1 Terms Discarded

```
Discarded: s₃, s₄, ... (all perturbation orders above ε²)          [A6-disc]
```

### A6.2 Original Justification

The leading orbital correction is O(ε²) with ε ≈ 1.6×10⁻⁴ for Mercury. The next order O(ε³) is smaller by ε ≈ 10⁻⁴ — below any observable threshold.

### A6.3 Quantum Relevance

This is essentially the same question as A4 for the perturbation series. The question is whether any O(ε³) term for a quantum system is unexpectedly large.

From the extension audit (Candidate A), s₃ was computed:

```
s₃ ~ μL³/(c²r⁴) × angular factor                                   [A6-s3]
```

The ratio s₃/s₂ ~ L/(cr) = v⊥/c = ε ≪ 1 for all accessible quantum systems.

The only way an O(ε³) term could matter is if it couples to a quantum degree of freedom in a way that the O(ε²) term does not. The extension audit showed that s₃ is a classical scalar with the same ℓ=2 angular structure as s₂ but with sin(2θ) dependence. It does not introduce qualitatively new quantum coupling.

### A6.4 Verdict on A6

**VALID FOR QUANTUM SYSTEMS.**

The O(ε³) truncation is valid by the same argument as [A4]: ε ≪ 1 for all known quantum systems. No qualitatively new quantum coupling appears at O(ε³).

---

## Audit A7 — Angular Average (v² → v⊥² = L²/r²)

### A7.1 Terms Discarded

The angular averaging replaces the full velocity-squared v² = ṙ² + v⊥² with only the transverse component:

```
Discarded: ṙ² contribution to the source of s₂                     [A7-disc]
```

The justification is that ṙ averages to zero over a complete Keplerian orbit (ṙ is odd under time reversal of the orbital phase).

### A7.2 Original Justification

For a closed Keplerian orbit, the radial velocity ṙ satisfies ∫ ṙ dt = 0 over one period. Therefore ∫ ṙ² dt ≠ 0 in general, but the contribution to δs from ṙ² is a rapidly oscillating term at the orbital frequency that averages to zero in the secular (orbit-averaged) force. Only the time-averaged force contributes to precession.

### A7.3 Quantum Relevance

For a quantum system, there is no orbital period. The quantity v² in the substrate equation [SRC2] refers to the velocity of the quantum system through the substrate. For a qubit sitting still in the laboratory, v = 0 identically — so [A7] is irrelevant (both ṙ and v⊥ are zero).

For a rotating qubit (on a spinning platform), v⊥ = ωr and ṙ = 0 exactly (circular rotation). The angular average is exact, not an approximation.

The only case where [A7] discards something non-trivial is a qubit on an elliptical path — which is not a standard experimental configuration.

### A7.4 Verdict on A7

**VALID FOR QUANTUM SYSTEMS** (in all standard experimental configurations).

For a qubit in a rotating frame, ṙ = 0 and the angular average is exact. The discarded radial contribution ṙ² is zero. For a qubit at rest, both ṙ and v⊥ are zero and the entire perturbation v·∇s₁ term is zero anyway.

---

## Observable Identification Audit — The Mapping Step

### OI.1 What Was Assumed

Beyond the seven field-equation approximations, the decoherence derivation makes one additional identification. After computing δJ = s₀(ω×r), the frozen theory connects δJ to the decoherence rate through constitutive assumption CA-3:

```
Γ ∝ ⟨(δJ)²⟩    [CA-3]
```

This is not an approximation of [ME] — it is an independent postulate. It is not audited here (it was already classified as constitutive in the frozen derivation). The audit focuses only on the field-equation approximations [A1]–[A7].

### OI.2 The Rotating-Frame Step

The step that produces δJ = s₀(ω×r) uses the kinematic identity:

```
v_sub' = v_sub + ω×r    [RF]
```

This is exact — no approximation is involved. It is a consequence of the definition of a rotating frame. The audit finds no issue here.

### OI.3 The s ≈ s₀ Step

In going from δJ = s(ω×r) to δJ = s₀(ω×r), the full field s = s₀ + δs is approximated by s₀. This uses δs/s₀ = (ωr/c)² ≪ 1, which is valid for all laboratory rotation rates.

**But:** If [A1] and [A2] are not applied, the substrate field s also contains quantum-driven components s_q (from [A2-full]). The full current perturbation is then:

```
δJ = (s₀ + s_q + δs)(ω×r)                                          [OI-full]
```

The term s_q(ω×r) was discarded because [A2] set s_q = 0. If s_q ≠ 0 (quantum source retained), this term produces a decoherence contribution that depends on both ω AND P_e(t) (the quantum state).

This is not a new approximation error — it is the direct consequence of the A2 finding: once [A2] is invalid, the full field s must be used, which includes the quantum-driven component s_q.

---

## Summary Table

| Approx | Terms Discarded | Valid for Orbital | Valid for Quantum | Quantum-Relevant Structure Discarded? |
|--------|----------------|-------------------|-------------------|---------------------------------------|
| A1 | τ∂²s/∂t² + ∂s/∂t | Yes (τ≪T_orb) | **No** (τω_q≳1 plausible) | Changes substrate response at ω_q; no new operator structure alone |
| A2 | αE + β∇·(Ev_sub) + γF − σ_irr | Yes (test particle) | **No** (qubit has oscillating E at ω_q) | **Yes** — discards αE∝P_e(t) and γF_q = −γ∇⟨H_q⟩ |
| A3 | −∇·(χsu) | Yes (χ≪v_sub orbital) | **No** (χ≫v_sub laboratory) | **Yes** — if u=n̂, introduces quantum-state-dependent current |
| A4 | s₃,s₄,... (v/c expansion) | Yes | Yes (ε_q≪1) | No |
| A5 | s∇·v_sub | Yes (exact=0) | Yes (exact=0) | No |
| A6 | O(ε³) truncation | Yes | Yes | No |
| A7 | ṙ² orbital average | Yes (orbit avg) | Yes (ṙ=0 for rotation) | No |

---

## Final Verdict

```
Result:
Three approximations (A1, A2, A3) are valid for orbital mechanics
but invalid — or not established as valid — for quantum systems.

Of these:

  A2 and A3 discard qualitatively new quantum-relevant structure.

  A2 discards: α E_q ∝ P_e(t) — a time-oscillating substrate source
               driven by the qubit's excited-state population.
               γ F_q = −γ∇⟨ψ|H_q|ψ⟩ — a quantum-state-dependent
               force source.

  A3 discards: −∇·(χ s u) where u may equal the Bloch vector n̂.
               This introduces a substrate current directed along n̂,
               producing a decoherence contribution proportional to
               χ² that depends on the qubit's quantum state orientation.
               The justification χ/|v_sub| ≪ 1 is REVERSED in the
               laboratory: v_sub ~ 9.8τ m/s is negligibly small,
               making χ/|v_sub| potentially ≫ 1.

  A1 discards: τ ∂²s/∂t² + ∂s/∂t — changes the substrate response
               at quantum frequencies but does not alone introduce
               new operator structure. Amplifies A2 effect when
               τω_q ≳ 1.

  A4, A5, A6, A7: valid for quantum systems. No coupling discarded.

The coupling already exists implicitly in the master equation [ME].
It was discarded not because it is zero, but because the
approximations that were valid for orbital mechanics were applied
without verifying their validity in the quantum regime.

The minimum required to recover the quantum coupling:

  Step 1. Retain [A2]: αE and γF source terms for the quantum system.
          The substrate field gains a quantum-state-dependent source.
          The field component s_q satisfies [A2-full].

  Step 2. Retain [A3]: The coherence transport term −∇·(χ s u).
          If u is identified with the Bloch vector n̂, the substrate
          current acquires a component directed along n̂.

  Step 3. Identify u = n̂ (Bloch vector) — this is a new identification
          that must be justified from the definition of u in [ME].
          It is not a modification of [ME]; it is a specification of
          what u represents for a quantum system.

  Step 4. Specify the back-action (how s_q feeds back onto the qubit).
          This is postulate P3 from the extension audit. It remains
          the one step that [ME] does not determine.

Therefore the conclusion of the extension audit is refined but not
overturned:

  The coupling exists implicitly, removed by approximations A2 and A3
  that are not valid in the quantum regime. Recovering it requires:
    - No new postulates for the forward direction (A2+A3 retained).
    - One new postulate for the back-action direction (P3).

  This is a weaker requirement than the extension audit found:
  instead of three new postulates (P1, P2, P3), only P3 is new.
  P1 and P2 (Hilbert space and commutation relations for s) are not
  required for the forward coupling. They are required only if one
  seeks to quantise the substrate field itself.
```
