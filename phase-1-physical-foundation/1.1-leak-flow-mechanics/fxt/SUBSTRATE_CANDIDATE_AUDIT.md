# SUBSTRATE_CANDIDATE_AUDIT.md
## Physical Candidate Substrates for Extension B (c ≪ v_s)

**Date:** 2026-08-22
**Question:** Does any physically motivated substrate satisfy C2/C5 with c ≪ v_s,
  and if so, does it produce a genuinely discriminating prediction?
**Source:** THEORY_EXTENSION_SEARCH.md §B, PREDICTION_LADDER.md, C2_FOUNDATIONS.md

**C5 closure requirement:** The n±(x) fields must be approximately closed under
the substrate dynamics at propagation speed c. For c ≪ v_s, this requires a
physical degree of freedom that propagates at c and forms a persistent random
walk (not simple diffusion).

---

## Candidate 1: Acoustic Phonons (Extension A baseline)

**Speed:** c = v_s ≈ 3000–8400 m/s depending on material and polarization
**C5 closure:** YES — this is the natural FPUT P1 projection
**Coupling to qubits:** YES — deformation potential, piezoelectric
**Discriminating prediction:** NO — phonon bath gives identical observables
**Verdict:** CONVENTIONAL PHENOMENOLOGY. Rejected as discriminator.

---

## Candidate 2: TLS Defect Hopping (classical persistent random walk)

**Mechanism:** Two-level systems (TLS) in amorphous SiO₂ near Josephson junctions.
Excitations hop between TLS sites at rate γ_hop. If the hopping is persistent
(excitation retains direction for time τ_B), a PRW emerges with:

```
c_TLS = d_TLS · γ_hop
```

For d_TLS ~ 1–10 nm and γ_hop ~ 10⁶–10⁹ s⁻¹: c_TLS ~ 10⁻³–10 m/s.

**C5 closure:** REQUIRES persistent hopping. In isotropic amorphous SiO₂, TLS
hopping is random (not persistent) → diffusion equation, not telegrapher.
For persistent hopping, each TLS must preferentially transfer to its same-direction
neighbor — this is a new physical model, not in existing C2.

**Coupling to qubits:** YES — TLS are the dominant decoherence source in SC qubits
**Conventional null:** TLS-induced 1/f noise is well-characterized. The specific
persistent-PRW structure would need to produce K₀ correlations that standard
TLS models do not.

**Critical problem:** If TLS hopping is purely diffusive (the standard model),
the correlator is Gaussian/exponential, not K₀. A K₀ correlator requires
the telegrapher, which requires persistent hopping. This is an additional
physical assumption with no direct evidence.

**Verdict:** PHYSICALLY POSSIBLE at the right speed range. REQUIRES NEW MODEL
for persistent hopping dynamics. Not derivable from existing C2. If this model
were constructed and verified, it could produce c ≪ v_s with K₀ correlations.
This is the most promising Extension B direction but is a full new theory.

**Classification:** NEW THEORY EXTENSION — not derivable from existing C2.

---

## Candidate 3: Substrate Polariton Modes

**Mechanism:** In polar semiconductor substrates, phonon-photon hybridization
creates polariton modes with group velocities much less than either phonon or
photon speed. Near the phonon-polariton resonance: v_g → 0.

For typical polar semiconductors: v_polariton ≈ 100–10,000 m/s depending on
frequency and proximity to resonance.

**Hardware relevance:** Si is non-polar — no phonon polaritons. GaAs and other
III-V semiconductors are polar but not used in standard SC qubit chips.
Not applicable to IBM-style Si/Al/Nb chips.

**C5 closure:** Unknown — requires constructing the polariton PRW model.
**Verdict:** NOT APPLICABLE to current hardware. Requires different chip materials.

---

## Candidate 4: Surface Acoustic Waves (SAW)

**Mechanism:** Rayleigh surface acoustic waves propagate at v_SAW ≈ 0.9·v_s
for Si. This is not ≪ v_s. However, for dispersive SAW in periodic structures
(phononic crystals), group velocity can be reduced significantly.

**Speed:** v_SAW_bare ≈ 5080 m/s (Si, [110] direction) — not slow enough.
In phononic crystal: v_g can be reduced by factor ~10–100 → 50–500 m/s.

**C5 closure:** In principle possible if the slow SAW mode forms a persistent walk.
**Hardware relevance:** Standard IBM chips have no phononic crystal structure.
  This would require specially engineered chip geometry.
**Conventional null:** Slow SAW in phononic crystals is conventional phonon engineering.
  The prediction would still be conventional acoustic physics.
**Verdict:** REQUIRES ENGINEERED HARDWARE and is still conventional acoustic physics.
  Not a discriminator for SXC-IGC ontology.

---

## Candidate 5: Magnon (Spin Wave) Modes

**Mechanism:** Antiferromagnetic spin waves have linear dispersion with
v_magnon = J·S·a/ℏ. For transition metal oxides: v_magnon ~ 10³–10⁴ m/s.

**Hardware relevance:** Standard SC qubit chips (Si, Al, Nb) are not magnetic.
No magnon modes exist in these materials at operating conditions.

**Verdict:** NOT APPLICABLE to current hardware.

---

## Candidate 6: Quasiparticle Diffusion in Superconductor

**Mechanism:** Unpaired quasiparticles in the Al or Nb superconducting films
diffuse with diffusion constant D_qp ≈ 10⁻² m²/s. Effective speed to scale L:
v_qp_eff = D_qp/L.

For L = 1 mm: v_qp_eff ≈ 10 m/s — in interesting range.
For L = 1 cm: v_qp_eff ≈ 1 m/s.

**C5 closure:** Quasiparticle diffusion is a DIFFUSION equation, not a telegrapher.
No persistent random walk → no K₀ correlator → C5 fails for the PRW structure.

**Conventional null:** Quasiparticle-induced decoherence is well-studied and gives
diffusion-type spatial correlations (Gaussian/exponential), not K₀.

**Verdict:** WRONG DYNAMICS (diffusion, not telegrapher). REJECTED.

---

## Candidate 7: Flux Noise Propagation via Kinetic Inductance

**Mechanism:** In superconducting films, flux noise can propagate via kinetic
inductance effects. The propagation speed is reduced relative to c_EM by the
kinetic inductance factor: v_KI = c_EM / √(1 + L_k/L_g).

For high kinetic inductance materials (NbN, granular Al): L_k >> L_g,
v_KI ≪ c_EM but typically still >> v_s.

**Speed:** v_KI ~ 10⁶–10⁸ m/s — much too fast.
**Verdict:** Speed too high. NOT USEFUL for c ≪ v_s discrimination.

---

## Summary: All Candidates

| Candidate | Speed range | C5 closure | Discriminating | Status |
|-----------|------------|------------|---------------|--------|
| Acoustic phonons | 3000–8400 m/s | YES | NO — conventional | CONVENTIONAL |
| TLS persistent walk | 10⁻³–10 m/s | REQUIRES NEW MODEL | POSSIBLE | NEW THEORY EXT |
| Substrate polaritons | 100–10,000 m/s | UNKNOWN | POSSIBLE | WRONG MATERIAL |
| Slow SAW (phononic) | 50–500 m/s | POSSIBLE | NO — conventional | ENGINEERED HW |
| Magnon modes | 10³–10⁴ m/s | POSSIBLE | NO — wrong material | WRONG MATERIAL |
| Quasiparticle diffusion | 1–10 m/s | NO (diffusion PDE) | NO | WRONG DYNAMICS |
| Kinetic inductance | 10⁶–10⁸ m/s | UNKNOWN | NO — speed wrong | TOO FAST |

---

## Conclusion

**No currently known physical substrate satisfies all three requirements
simultaneously:**
1. c ≪ v_s (anomalously slow propagation)
2. C5 closure (persistent random walk, not diffusion)
3. Chip-relevant (present in standard SC qubit hardware)

**The TLS persistent random walk (Candidate 2) is the most promising direction.**
It can produce c ~ 0.001–10 m/s and couples naturally to qubit dephasing.
But it requires a new physical model (persistent, not random, TLS hopping) that
is not derivable from existing C2 and has no established experimental support.

**Extension B outcome: NO physically credible substrate found.**
A motivated candidate exists (TLS persistent walk) but requires building a new
physical theory from scratch. That work is outside the scope of existing C2.

**Decision tree classification: Outcome E — No physically credible extension was found
from existing C2 structure.**

The TLS direction is documented here as a potential future research target, not
as an existing C2 prediction.
