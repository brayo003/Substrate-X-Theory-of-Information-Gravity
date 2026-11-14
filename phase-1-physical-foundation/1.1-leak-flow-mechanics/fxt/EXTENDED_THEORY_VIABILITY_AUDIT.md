# EXTENDED THEORY VIABILITY AUDIT

**Date:** 2026-08-22
**Question:** Is E_min = {η, ℏ, H_B, λ_coup} a viable physical theory with
independent predictions, or merely a quantum/bath formalism reproducing a
pre-assumed C± = αE?
**Labels:** [T]=theorem [KR]=known result [OBS]=obstruction [A]=assumption [D]=derivation

---

## 1. Executive Verdict

**Classification: B — mathematically coherent but substantially phenomenological.**

The extended chain PRW → quantum substrate → η → bath → C± = αE is
mathematically correct. The Fermi golden rule mechanism produces αE once four
new ingredients are supplied. But the extension does not explain *why* C± = αE.
It provides a formalism in which αE is reproducible after coupling the bath
specifically to the *energy sector* of the substrate quantum — a sector choice
not forced by any SXC-IGC principle. Coupling to the direction sector gives
C± ∝ s; coupling to coherence gives C± ∝ Im(χ). The correct sector is selected
by assuming the desired result.

The decoherence sector (Γ_φ ∝ ω²) and the creation sector (C± = αE) use two
unrelated couplings (g vs λ_coup) with no demonstrated connection between them.
They are not one mechanism — they are two separate empirical couplings sharing
a Hilbert space.

Three falsifiable predictions distinct from bare C± = αE exist in principle, but
all require independently measuring η, T, and λ_coup, which cannot be determined
from C2 transport quantities. Without those measurements, the extension is not
falsifiable in practice.

---

## 2. Existing-History Inventory (no duplication)

**PRW (established pre-2026-08-22)**
- Balance equations exact; telegrapher from PRW [KR T PRW-1]
- PRW = unique C1-C6 FPUT projection [T FPUT-3]
- State space = simplex Δ¹, not Bloch sphere [OBS T PRW-IMP-1]
- Observable algebra commutative; source-free PRW conserves info [OBS F4]

**Quantum parent / decoherence (established 2026-07-21)**
- H_int = g·J·σ_z unique given A-lin/A-local; Γ_φ = k_rot·ω² validated [T D]
- g requires kg ∉ D_C2; irreducibly free [OBS F2]
- Unitary Q7 (2026-08-22): C±_eff ∝ ΔN₁₁ ≠ αE [D]

**Bath/environment (established 2026-08-22)**
- PRW modes as bath: fails (no energy variable) [OBS H_B-1]
- FPUT phases as bath: fails (reverses projection, requires β≠0) [OBS H_B-1]

**η (established 2026-07-24)**
- D_C2 = {m,s}: no kg; no C2 combination produces Joules [OBS F3 T RC]
- η [J/info] = minimal mass-scale extension; logically independent of all C2 axioms
- All derivation routes for η fail (rank, Landauer, symplectic, GR, causal entropy)

**ℏ (established 2026-07-24)**
- Irreducibly independent of proved C2; HC-1 and HC-2 both fail
- C2 symplectic form has units info²/(m⁵s) ≠ J·s

**α / C± (established throughout)**
- C± = αE always phenomenological; α requires kg [OBS F3]
- Linear C± = αE is minimal *member* of admissible family, NOT forced [INTERACTION_SPACE_AUDIT]

---

## 3. Exact Microscopic Model

System: H_S = ℂ²_dir ⊗ ℂ²_E, basis {|+,e₀⟩,|+,e₁⟩,|−,e₀⟩,|−,e₁⟩}

Free Hamiltonian: H_S = I_dir ⊗ diag(ε₀,ε₁), gap Δε = ε₁−ε₀ [requires η]

Bath: H_B = Σ_k ℏω_k b_k†b_k [bosonic reservoir, physical identity unspecified]

Interaction (creation): H_int = Σ_k λ_k(b_k+b_k†) ⊗ Â_create
where Â_create operates in the many-body Fock space F(H_S), creating a new
info quantum at e₀ when a particle transitions e₁→e₀.

Coarse-graining: n±/N = Tr_E(ρ±±), e±/N = Tr_E(Ĥ_E ρ±±)

Result (Born-Markov-Secular + high-T):
  C± = α·e±,  α = (2π/ℏ)|λ̄|²ρ_bath(Δε/ℏ)·f_T/ε₁
  C_total = αE  ← matches target

---

## 4. Arrow-by-Arrow Dependency Audit

| Arrow | Classification | New inputs required |
|-------|---------------|---------------------|
| PRW → quantum substrate | ASSUMED | O1 (complex structure), η, Fock space |
| quantum substrate → η | UNDEFINED/EMPIRICAL | η [J/info] not in D_C2 |
| η → system-bath coupling | ASSUMED | ρ_bath(ω) is a free function |
| coupling → bath H_B | ASSUMED + IMPORTED | bath physical identity unspecified |
| bath → energy transition e₁→e₀ | DERIVED | none (given prior assumptions) |
| energy transition → info creation | ASSUMED | 3-body H_int in Fock space |
| info creation → C± = αE | DERIVED | high-T approximation |

4 of 7 arrows ASSUMED. 2 DERIVED (conditional). 1 UNDEFINED.

The two DERIVED arrows (5 and 7) are genuine derivations *given the assumptions*.
They do not validate the assumptions.

Key structural point on Arrow 6: standard amplitude damping (e₁→e₀) conserves
particle number N. Zero new information quanta created. C± = 0. To get C± ≠ 0
requires a three-body interaction (bath mode × annihilate e₁ × create new e₀
particle). This is a separate physical assumption beyond the energy transition.

---

## 5. η Audit

η = ε₀ [J/info] = energy per information quantum.

History: identified as minimal mass-scale extension in C2_separation_theorem_audit
(2026-07-24). Models M00/M10 (independence certificate). All derivation routes
tested in C2_info_energy_bridge_audit.md fail: rank→E₀ free; Landauer→needs k_B,T;
symplectic→wrong units (info²/m⁵s); GR→gives kg⁻¹ not kg; causal entropy→no J·s.

Can η be derived from existing SXC-IGC structure? No. The dimensional obstruction
(kg ∉ D_C2) is a hard proved theorem. No new route exists in this session.

Can η be independently motivated? Physical interpretations exist (Landauer bit,
ℏω₀) but each requires external constants also absent from C2. Not a derivation.

Is η new information? No. The current chain instantiates a gap identified
in July 2026. Nothing new discovered about η.

Classification: NEW FUNDAMENTAL CONSTANT. Not derivable. Previously identified.

---

## 6. ℏ Audit

History: enters Γ_φ as dimensional factor. HC-1 relocates problem to m_eff.
HC-2 requires unproved CCA-C3. C2 symplectic form has units info²/(m⁵s) ≠ J·s.
Verdict established 2026-07-24: ℏ irreducibly independent of proved C2 mathematics.

Does the extended chain imply an action scale? No. ℏ is imported at three
points (von Neumann equation, Fermi golden rule, secular condition). It is not
derived at any of them.

Could ℏ = f(η, c, τ)? Attempt: [η·τ·n₀] = (J/info)·s·(info) = J·s = [ℏ] ✓
dimensionally. But this introduces n₀ (information content per quantum,
dimensionless but free). This relocates the problem to n₀. If n₀ = 1 by
definition, then ℏ = η·τ — but this makes ℏ dependent on τ (a transport
timescale), giving ℏ ∝ 1/λ_rev. No physical motivation for this identification
exists and it would make ℏ context-dependent (different substrates → different ℏ).

Classification: EXTERNAL QUANTUM-MECHANICAL PRIMITIVE. Not implied by SXC-IGC.

---

## 7. Quantum Substrate Audit

What must be introduced: (1) O1 — complex field extension replacing classical
{+,−} with ℂ²; (2) energy sector ℂ²_{e₀,e₁} with gap Δε = η·n₀; (3) Fock space
F(H_S) for particle creation (second quantization).

Are these properties of the PRW or an unrelated system?
The direction quantization (O1) is structurally related to the PRW direction
variable. The energy sector is not: PRW particles carry no energy degree of
freedom (state = position + direction only, per microscopic_derivation.md §1.2).
Adding ℂ²_{e₀,e₁} creates a new kind of substrate particle. The Fock space
further replaces it with a quantum field.

Can the direction sector alone generate C± = αE? From Q7: unitary direction-only
dynamics gives C±_eff ∝ ΔN₁₁ (population inversion) in the Markovian limit.
This ≠ αE. The energy sector is specifically required to produce C± ∝ E.
Therefore the energy sector is not optional window-dressing — it is structurally
necessary. But it is also genuinely new, not present in the PRW.

Classification: ASSUMED. The quantum substrate is a new object with internal
energy structure not present in the original PRW definition.

---

## 8. Bath/Environment Audit

What physical object is the bath? The extended theory requires H_B = Σ_k ℏω_k b_k†b_k.
No SXC-IGC document identifies a physical object playing this role.

Candidates tested in SUBSTRATE_CLOSURE_AUDIT:
- PRW high-frequency modes: fail (no energy variable; modes exchange info, not Joules)
- Discarded FPUT phases: fail (require anharmonicity β≠0; reversal of T^M projection)
- Long-wavelength PRW modes: fail (wrong timescale direction: slow, not fast)
- v_sub drift field: not a bath (no Hamiltonian, no equilibrium state)

Required bath properties:
1. Large DoF count ✓ (abstract)
2. Timescale separation τ_bath << τ_creation ✓ (requirement, not proved)
3. Correlation decay ✓ (required; not verified from substrate structure)
4. Energy exchange capability ✗ (PRW has no Joule variable)
5. Thermal equilibrium state at temperature T ✗ (T not in C2)
6. Density of states ρ_bath(ω) at ω₀ = Δε/ℏ ✗ (free function)

The bath is unidentified. It is a placeholder for "whatever physical environment
exists outside the substrate." This is physically legitimate (all real quantum
systems have environments) but is not derived from SXC-IGC structure.

Classification: ASSUMED + IMPORTED FROM STANDARD PHYSICS. Bath physical identity
is UNDEFINED within SXC-IGC.

---

## 9. Coupling λ_coup Audit

Dimensional analysis: [λ_coup] = s^{-1/2} (treating info as dimensionless).
This IS constructible from C2 primitives: e.g., c·τ^{1/2}/r_q has units s^{-1/2}.
So λ_coup is dimensionally accessible without introducing kg.

However: dimensional access ≠ derivation. The specific value of λ_coup is the
matrix element of H_int between the system state and the bath + new-particle
state. This matrix element depends on the spatial overlap integral of substrate
and bath wavefunctions — a microscopic quantity that cannot be computed from
transport parameters (c, τ, s₀, r_q) without a detailed model of the interaction.

Analogy: in quantum optics, the dipole matrix element ⟨e|r|g⟩ cannot be
computed from the diffusion coefficient of light in a medium. The transport
layer carries no information about interaction matrix elements.

Can λ_coup be constrained by existing quantities? Only in the following sense:
the Born approximation requires λ_coup² << ε₁·τ_bath/ℏ. This sets an upper
bound on λ_coup but does not determine its value.

Does λ_coup scale with g (the decoherence coupling)?
g [J·m²·s/info] = η·(c²τ/r_q)·n₀ dimensionally. λ_coup [s^{-1/2}] is
dimensionally unrelated to g. There is no dimensional argument connecting them.
They are independent free parameters.

Classification: FREE PARAMETER. Dimensionally constructible but value undetermined.

---

## 10. Energy-Conservation Audit

Before a creation event: system has N particles; bath has energy E_bath; 
external energy field has density E [J/m³].

After a creation event at rate C± = αE:
- One new info quantum created at energy ε₀
- Energy removed from the e₁ sector: Δε = ε₁ − ε₀ per event
- Energy emitted to bath: Δε − ε₀ = ε₁ − 2ε₀ per event (if ε₁ > 2ε₀)
- Energy stored in new info quantum: ε₀ per event

Conservation law (from CONVERSION_PRW_DERIVATION.md, proved):
  dQ/dt = 0   where Q_total = ∫[E + ε₀·s] dx
requires Q± = ε₀·C±. This is satisfied by construction.

What feeds E? The external energy density E is not produced by the substrate —
it is an external field (mass-energy of physical matter). The substrate extracts
from E at rate αE per unit volume. The physical picture is: substrate information
quanta are created at the expense of the local energy density.

Is the "environment absorbs it" justified? The bath absorbs (Δε − ε₀) per event.
This is mediated by H_int and quantified by the bath density of states. It is
not a hand-wave — it is the standard open-system heat exchange. But the bath
must have sufficient heat capacity, which requires the bath to be large (many
modes). This is assumed but consistent.

Energy conservation is satisfied provided Q± = ε₀·C±. This holds by construction.

---

## 11. C± Derivation Audit

Starting from H_total = H_S + H_B + H_int (all three specified above):

Step 1: Von Neumann equation iℏ∂ₜρ_total = [H_total, ρ_total].
Step 2: Born approximation: ρ_total ≈ ρ_S ⊗ ρ_B. Requires weak coupling λ_coup.
Step 3: Trace over bath: get Redfield equation for ρ_S.
Step 4: Markov approximation: τ_bath << τ_creation.
Step 5: Secular approximation: Δε/ℏ >> α.
Step 6: Lindblad form with jump operator L = √(Γ) â†_{σ,e₀} â_{σ,e₁}.
Step 7: Population equation for n_{e₁}^±:
  ∂ₜn_{e₁}^± = −Γ·n_{e₁}^±   where Γ = (2π/ℏ)|λ̄|²ρ_bath(Δε/ℏ)
Step 8: New info quantum created per e₁→e₀ event:
  ∂ₜs^± = +Γ·n_{e₁}^±   (one new particle per downward transition)
Step 9: High-temperature equilibrium: n_{e₁}^± ≈ e±/ε₁
  C± = Γ·e±/ε₁ = α·e±,   α = Γ/ε₁

Result: C_total = α(e⁺+e⁻) = αE. The derivation is exact given all assumptions.

Where does E enter? At Step 9 via n_{e₁}^± ≈ e±/ε₁. The high-temperature
Boltzmann distribution converts energy density into occupancy. If this
approximation is dropped, C± ∝ n_{e₁}^± (high-energy state population),
which equals e±/ε₁ only at high T with equal degeneracy.

Is α genuinely predicted? 
  α = (2π/ℏ)|λ̄|²ρ_bath(Δε/ℏ)/ε₁
This formula predicts α in terms of {ℏ, λ̄, ρ_bath, Δε, ε₁}. All five are
unknown within SXC-IGC. α is not predicted — it is renamed from five free
parameters to one observed rate. This is classification: PHENOMENOLOGICAL RENAME.

---

## 12. Detailed-Balance Audit

The bath mechanism at finite temperature satisfies the Kubo-Martin-Schwinger
(KMS) condition. For a bath at temperature T, the ratio of upward (e₀→e₁)
to downward (e₁→e₀) rates is:

  Γ_up/Γ_down = exp(−Δε/k_BT)

This imposes a destruction term alongside the creation term:
  ∂ₜs = +α·E − σ_irr

where at equilibrium σ_irr = α·E_eq. This is consistent with the existing master
equation which has both +αE and −σ_irr.

**Does detailed balance impose a relation between C⁺ and C⁻?**
In the proposed model both C⁺ and C⁻ have the same rate (symmetric bath,
no parity-breaking in the bath coupling). So C⁺ = C⁻ = αE/2 at equilibrium.
This matches the requirement from microscopic_derivation.md §1.8 (creation split
equally between ±). Detailed balance is satisfied and it is consistent.

**Is this relation present in the existing master equation?** Yes: the original
C⁺ = C⁻ = αE/2 symmetry is confirmed by the bath mechanism for an isotropic bath.

---

## 13. Positivity Audit

C± = α·e± with α ≥ 0 (rate), e± ≥ 0 (energy density ≥ 0 by definition).
Therefore C± ≥ 0 unconditionally. ✓

This is a genuine improvement over the unitary Q7 result (C±_eff ∝ Im(g*χ))
which can be negative. The bath mechanism guarantees positivity because
Γ = (2π/ℏ)|λ|²ρ_bath(ω) ≥ 0 always (squared modulus, non-negative DOS).

One edge case: if ρ_bath(Δε/ℏ) = 0 (bath has no modes at the transition
frequency), then α = 0 and C± = 0. This is physical (no creation if no available
bath modes). It does not violate positivity.

Positivity is satisfied unconditionally for the bath mechanism.

---

## 14. Parameter-Identifiability Audit

Free parameters introduced by the extended theory:

| Parameter | Units | Independent measurement? | Degeneracy |
|-----------|-------|--------------------------|------------|
| η = ε₀ | J/info | Must measure energy scale of info quantum | η·n₀ always appears as a pair |
| ℏ | J·s | Known from QM (1.055×10⁻³⁴) | Not degenerate |
| Δε = η·n₀ | J | Must measure energy gap | Δε/η = n₀ underdetermined |
| λ_coup | s^{-1/2} | Must measure from creation rate | Degenerate with ρ_bath |
| ρ_bath(ω₀) | s | Must characterize bath spectrum | Degenerate with λ_coup |
| T (bath temperature) | K | Must measure temperature | Degenerate with Δε via f_T |
| n₀ | dimensionless | Info content per quantum | Absorbed into η |

**Critical degeneracy:** α = (2π/ℏ)|λ_coup|²·ρ_bath(Δε/ℏ)·f_T/ε₁

The observable α is a product of λ_coup², ρ_bath(Δε/ℏ), f_T, and 1/ε₁.
Measuring α alone does not determine any individual factor. The combination
|λ_coup|²·ρ_bath can always be adjusted to give any desired α while keeping
the product constant. Similarly, f_T and ε₁ are degenerate if T is not
independently measured.

**How many independent numbers does measuring α give?**
One number (α). The microscopic theory has at least four free parameters
(λ_coup, ρ_bath, T, Δε). Measuring α gives one equation in four unknowns.
The microscopic parameters are profoundly underdetermined from α alone.

**Conclusion:** If only α can be observed, the microscopic extension is not
falsifiable beyond the original phenomenological C± = αE. It adds zero
independent constraints. This is the most serious scientific objection to
classifying this as a genuine microscopic derivation.

---

## 15. Circularity Audit

**Test:** Is C± = αE assumed before the mechanism is constructed?

In FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md §5, the interaction H_int was written as:
> H_int = Σ_k λ_k(b_k+b_k†) ⊗ (â†_{+,e₀} + â†_{-,e₀} + h.c.) × (Σ_m â†_{m,e₁}â_{m,e₁})

This H_int was constructed *to produce C± ≠ 0*. The creation operator â†_{σ,e₀}
was placed in H_int explicitly to generate information quanta. This is a
forward-engineering choice: choose H_int to reproduce the desired output.

**Is this circular?** Partially. The functional form C± ∝ e± (proportional to
energy density, not to information density or coherence) does follow from the
particular coupling chosen — it is not a free parameter of the result given
that coupling. In this sense the derivation is not purely circular.

**However:** The choice to couple the bath to the energy sector (â†_{e₀}â_{e₁})
rather than the direction sector (σ_x) or coherence sector is the choice that
produces C± ∝ E. If the bath were coupled instead to the direction sector:
  H_int ∝ σ_x ⊗ (b+b†) → C± ∝ s (info density, not energy)

The correct sector is selected by knowing the desired result. This constitutes
a weak form of circularity: the mechanism is not derived from first principles
that force the energy-sector coupling — it is designed to reproduce αE.

**Verdict:** Partial circularity confirmed. The derivation is not fully
circular (the functional form C± ∝ E follows from the sector choice without
free parameters), but the sector choice is not motivated independently of the
desired output.

---

## 16. Falsifiability Audit

**The base claim to exceed:** Postulating C± = αE with α as a free constant.

**Prediction F1 — Temperature dependence of α:**
The bath mechanism predicts α ∝ f_T(T, Δε) = n̄(Δε/ℏ,T) + 1 (Bose factor + 1).
This gives:
  α(T) = α₀ · [exp(Δε/k_BT) − 1]⁻¹ + α₀

This is a specific temperature dependence of α. If α is measured at multiple
temperatures, the Bose factor shape constrains the ratio Δε/k_BT.
**This is a genuine falsifiable prediction, distinguishable from bare C± = αE.**
However, it requires independent temperature control and measurement of α(T).

**Prediction F2 — Frequency-dependent decoherence correction:**
The bath that drives C± also back-acts on the direction sector (Lamb shift and
damping from H_B coupling). This predicts a small additional damping term in
the direction dynamics:
  Γ_direction_extra ~ (λ_coup)² · ρ_bath(0) / ℏ

This correction to Γ_φ is distinct from the existing k_rot·ω² prediction.
**Falsifiable in principle** if λ_coup is not zero — but the correction may be
below experimental sensitivity if λ_coup << g.

**Prediction F3 — Threshold suppression of C± at low T:**
At low temperature (Δε >> k_BT), the Bose factor → 0 and α → α_spontaneous only
(the zero-temperature spontaneous emission rate). At high temperature α grows
linearly with T. This thermal threshold is absent from bare C± = αE.
**Falsifiable** by measuring α at low T and testing for threshold suppression.

**Assessment of falsifiability:**
All three predictions (F1, F2, F3) require: (a) independent measurement of T,
(b) knowledge of Δε, and (c) ability to vary these parameters. If the substrate
is a fixed physical environment where T and Δε cannot be independently varied,
none of these predictions can be tested. The extension is then empirically
equivalent to bare C± = αE.

---

## 17. Relationship to the Decoherence Sector

The existing decoherence prediction uses:
  H_int^decoherence = g · J(x_q,t) · σ_z^qubit

This couples the substrate *current* J to the qubit *Pauli operator* σ_z.
The bath in the decoherence sector IS the PRW substrate itself (the substrate
current fluctuations).

The proposed creation sector uses:
  H_int^creation = Σ_k λ_k(b_k+b_k†) ⊗ â†_{create}

This couples an external bosonic bath to a Fock space creation operator.
The bath in the creation sector is NOT the PRW substrate.

**Are these two mechanisms unified?**
No. They use:
- Different bath objects (PRW current vs external bosonic reservoir)
- Different coupling operators (σ_z vs â†)
- Different coupling constants (g [J·m²·s/info] vs λ_coup [s^{-1/2}])
- Different physical processes (dephasing of external qubit vs internal creation)

**Can both Γ_φ ∝ ω² and C± ∝ E emerge from the same H_total?**
In principle yes: H_total = H_qubit + H_substrate + H_int^decoherence
                           + H_system + H_bath + H_int^creation

But these are additive independent terms. There is no cross-term connecting
g to λ_coup. The two mechanisms coexist in the same formalism but make no
contact. This is not theoretical unification — it is theoretical juxtaposition.

**Classification:** The extended theory contains the decoherence sector unchanged
and adds the creation sector independently. They share a Hilbert space structure
but are otherwise unrelated. This is consistent but not unified.

---

## 18. Minimal-Extension Analysis

**What is strictly necessary for C± = αE?**

Strictly necessary (cannot be removed):
1. η [J/info]: dimensional gateway; without it C± ∝ E is dimensionally impossible.
2. A bath with modes at ω₀ = Δε/ℏ: without it the emission rate = 0.
3. A creation mechanism in H_int (Fock space, three-body coupling): without it
   amplitude damping produces no new particles.

Possibly removable:
- ℏ separately: if ℏ = η·τ·n₀ by definition (relocates problem; does not
  reduce free parameter count), keep ℏ as independent.
- Separate Δε and ε₁: if ε₀ = 0 (ground state at zero energy), then Δε = ε₁
  and only one energy scale is needed. This reduces parameters by one.
- Bath temperature T: if T→∞ (high-T limit taken from the start), T drops out
  and f_T = 1. The prediction α = const becomes exact, simplifying the model.

**Minimal viable extension:**
E_min_reduced = { η [J/info], H_B (bath modes at ω₀), λ_coup (creation coupling) }

with ℏ imported from standard QM (known empirically) and T treated in the
high-T limit. This is three new ingredients: one dimensional constant + one
environmental specification + one free parameter. Fewer than the original E_min.

**Categorize each:**
- η: fundamental constant (must be measured or imported from particle physics)
- H_B / ρ_bath: environmental specification (contextual; varies by physical setting)
- λ_coup: model parameter (free; calibrated from α measurement)

---

## 19. Strongest Remaining Objections

**Objection 1 (Sector Selection):**
The functional form C± ∝ E is not derived — it is a consequence of coupling the
bath to the energy sector of the substrate quantum. Coupling to the direction
sector gives C± ∝ s. Coupling to the coherence sector gives C± ∝ Im(χ). No
SXC-IGC principle forces the energy-sector coupling. The extension selects the
correct sector by knowing the desired answer.

**Objection 2 (Bath Identity):**
The bath has no identified physical object within SXC-IGC. It is a Caldeira-
Leggett placeholder attached to the theory without a derivation of what physical
degrees of freedom constitute it. The theory says "the environment drives
information creation" without specifying what the environment is.

**Objection 3 (Parameter Degeneracy):**
α = f(λ_coup, ρ_bath, T, Δε, ℏ). Measuring α constrains only this combination.
The individual microscopic parameters are underdetermined. The extension adds
no falsifiable constraints beyond α unless T and Δε can be independently measured.

**Objection 4 (Not a Derivation of η):**
The extension requires η as a fundamental constant. η has no derivation within
C2. It is the same gap identified in July 2026. The current session confirms
this gap and instantiates it, but does not close it. η is still unexplained.

**Objection 5 (Two Unrelated Mechanisms):**
Γ_φ ∝ ω² (substrate as bath for external qubit) and C± = αE (external bath for
internal substrate creation) are two independent empirical couplings (g and
λ_coup) with no connection. The theory is not unified. It is two separate
calibrated mechanisms attached to the same substrate label.

---

## 20. Final Classification

### A — viable extended physical theory with nontrivial independent predictions
### B — mathematically coherent but substantially phenomenological/underdetermined ← THIS
### C — internally inconsistent
### D — equivalent to merely postulating C± = αE

**Classification: B**

**Justification:**

The extended theory is NOT C: there are no internal inconsistencies. Energy is
conserved, positivity holds, detailed balance is satisfied, units are consistent
after the extensions are applied.

The extended theory is NOT D: the functional form C± ∝ E (rather than ∝ s, ∝ Im(χ),
or ∝ ΔN) does follow from a specific sector coupling without being a free
parameter of the result. The mechanism is not a trivial rename of the postulate.

The extended theory is NOT A: the three falsifiable predictions (temperature
dependence of α, thermal threshold, Lamb-shift correction to Γ_φ) require
independent measurement of bath temperature T and energy gap Δε, which cannot
be determined from C2 transport parameters alone. Without those measurements
the predictions are not sharp and the extension adds no empirical content beyond
the original C± = αE postulate.

The extended theory IS B because:
1. Four of seven derivation arrows are ASSUMED (sector choice, bath identity,
   creation mechanism, η).
2. α is a rename of four underdetermined microscopic parameters.
3. The bath has no identified physical object within SXC-IGC.
4. η is required but not derived — the same gap known since July 2026.
5. The decoherence and creation sectors are not unified.

**What has actually been demonstrated:**
- The functional form C± ∝ E follows from coupling an energy-sector bath to
  substrate information quanta, via standard Fermi golden rule. [GENUINE RESULT]
- Positivity of C± is guaranteed by the bath mechanism. [GENUINE RESULT]
- Detailed balance is consistent with the existing master equation. [GENUINE RESULT]
- The energy sector is structurally necessary (direction sector alone gives ΔN,
  not αE). [GENUINE RESULT]

**What remains empirical/assumed:**
- η is not derived [OPEN GAP, known since 2026-07-24]
- Bath physical identity within SXC-IGC is unspecified [OPEN]
- λ_coup is a free calibrated parameter [FREE PARAMETER]
- Sector choice (energy vs direction vs coherence) is not derived [ASSUMPTION]
- Decoherence and creation sectors are independent empirical mechanisms [NOTED]

**The precise scientific status of C± = αE after this audit:**

The extended theory provides a microscopic *story* for αE that is physically
natural (spontaneous emission analogue) and mathematically consistent. It upgrades
αE from "phenomenological with no mechanism" to "phenomenological with a named
mechanism, but with four underdetermined parameters replacing one." This is
progress in physical understanding but not scientific closure.

---

*End of EXTENDED_THEORY_VIABILITY_AUDIT.md*
*Date: 2026-08-22*
*No C2 structure was modified in the course of this audit.*
*All classifications follow from the established project record.*
