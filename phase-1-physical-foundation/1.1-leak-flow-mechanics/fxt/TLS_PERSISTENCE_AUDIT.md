# TLS_PERSISTENCE_AUDIT.md
## Can Physical TLS Dynamics Generate Directional Persistence?

**Date:** 2026-08-22
**Central question:** Does standard or physically defensible TLS physics contain
  a mechanism for directional persistence in excitation hopping?
**Label:** DERIVED | ASSUMED | CONVENTIONAL | FAILED | POSSIBLE

---

## 1. What Persistence Means Here

**Temporal memory** (what TLS have): A TLS excitation has memory of its OWN state — it oscillates between |0⟩ and |1⟩ at the Rabi frequency, with dephasing time T₂. This is temporal autocorrelation of the excitation amplitude at a SINGLE SITE.

**Directional spatial persistence** (what PRW requires): An excitation moving in direction +x from site i to site j continues preferentially in the +x direction from j. It does NOT reverse to −x immediately. The reversal occurs at rate γ_rev after a mean persistence time τ_B = 1/(2γ_rev).

These are DIFFERENT. Having long T₂ at a single site does not imply directional persistence in spatial propagation.

**The PRW requires:** After a hop from i to j, the excitation's probability of next hopping in the SAME direction exceeds 1/z (where z is the coordination number of the lattice). This is directional bias in the HOP DIRECTION, not in the excitation amplitude.

---

## 2. Standard TLS Hopping: Is It Persistent?

In the standard tunneling model, a TLS excitation hops from site i to a neighboring site j via dipole-dipole coupling V_ij. The hop rate is:

```
γ_hop,ij = V_ij² / γ_ij    [Fermi's golden rule — CONVENTIONAL]
```

After the hop: the excitation is at site j. The question is: what is the probability that the NEXT hop goes to a site j' in the same direction as the i→j hop?

For an ISOTROPIC random network of TLS sites (amorphous solid): the neighbors of j are randomly distributed in all directions. The coupling to each neighbor j' is V_{jj'} ∝ 1/d_{jj'}³. The probability of hopping in direction θ from j is:

```
P(θ) ∝ Σ_k V_{jk}² δ(θ - θ_{jk}) / γ_{jk}
```

In an isotropic amorphous solid, this distribution is UNIFORM over all directions. Therefore:

**P(same direction as i→j) = P(any other direction)**

**There is NO directional preference.** The hopping is a SIMPLE random walk, not a persistent random walk.

**Status: STANDARD TLS HOPPING IS NOT PERSISTENT. This is not an approximation — it is a consequence of the isotropy of the amorphous solid.**

---

## 3. Could Any Physical Mechanism Cause Persistence?

For directional persistence to exist, one of the following must be true:

### Mechanism 3.1: Momentum conservation

If the hopping carries momentum (like a phonon), momentum conservation would enforce forward preference — a phonon moving in direction +x tends to scatter forward, not backward.

**TLS reality:** TLS are localized atomic configurations. They have no well-defined momentum. Each TLS site is fixed in space. The "excitation" (which atom is in the excited configuration) carries no momentum — it cannot be deflected by momentum conservation.

**Status: INAPPLICABLE to TLS. TLS excitations are not quasiparticles with momentum.**

### Mechanism 3.2: Retarded interactions / propagator structure

In quantum electrodynamics, photon-mediated interactions have a retarded propagator that carries directionality. Could the TLS-TLS interaction have a similar structure?

The TLS-TLS interaction is dipole-dipole coupling through the dielectric medium. In the near field (d ≪ λ_photon), this is the instantaneous Coulomb interaction — not retarded. For TLS at d ~ nm and frequencies ~ GHz: λ_photon ~ 30 mm ≫ d. The interaction is purely near-field and instantaneous.

**Status: NO retarded propagator effect at the relevant scales.**

### Mechanism 3.3: Chain-like geometry (1D TLS array)

If TLS were arranged in a 1D chain with stronger nearest-neighbor coupling than next-nearest-neighbor, the hop would be preferentially along the chain. In 1D, "forward" is the only available direction after a hop.

**Physical reality:** TLS in amorphous SiO₂ are randomly positioned, not in a 1D chain. The 2D/3D random geometry makes this mechanism inapplicable to real chip substrates. An engineered 1D TLS chain would be a different, non-standard material.

**Status: INAPPLICABLE to amorphous solid TLS. Would require engineered substrate.**

### Mechanism 3.4: Coherent tunneling produces directed motion

If TLS tunneling is coherent (quantum, not classical), Rabi oscillations could produce directed motion through interference. In a perfectly ordered array, coherent tunneling gives Bloch oscillations with group velocity v_g = dE/dk — directed propagation.

**Physical reality:** In amorphous SiO₂, TLS sites are randomly positioned and randomly coupled. The disorder destroys coherence between sites — Anderson localization suppresses coherent transport. The mean free path for coherent transport is typically 1–2 lattice spacings before localization.

For localization NOT to occur, one needs either: (a) extremely weak disorder (inconsistent with amorphous solid), or (b) strong coupling between ALL TLS (inconsistent with sparse density ρ_TLS).

**Status: ANDERSON LOCALIZATION kills coherent directed transport in amorphous TLS.**

### Mechanism 3.5: Persistence from energy gradient

If TLS at site j has slightly lower energy than its neighbors in the backward direction (toward i), the excitation prefers to continue forward. This is a drift term, not persistence.

A drift breaks the random walk symmetry but does not produce the telegrapher equation — it produces an advection-diffusion equation. Drift ≠ persistence.

**Status: Drift does not produce the telegrapher equation. INAPPLICABLE.**

### Mechanism 3.6: Phonon-assisted directed hopping

Phonon-assisted TLS hopping occurs when TLS energy mismatch is compensated by phonon emission/absorption. A phonon moving in direction +x could preferentially assist hops in the +x direction (stimulated emission/absorption), creating apparent directionality.

**Analysis:** The phonon emission/absorption probability depends on the phonon density of states, not on the phonon's propagation direction. At thermal equilibrium (all phonon modes equally occupied), there is no preferred direction for phonon-assisted hopping.

For NON-EQUILIBRIUM conditions (e.g., a phonon pulse propagating in +x), there WOULD be preferential +x hopping. But this is conventional phonon-mediated transport — the directionality comes from the phonon, not from a novel TLS substrate.

**Status: Phonon-assisted persistence is CONVENTIONAL PHONON PHYSICS, not a new TLS substrate effect.**

---

## 4. Formal Proof That Standard TLS Hopping Is Not Persistent

**Theorem:** In an isotropic amorphous solid, the velocity autocorrelation function of a TLS excitation decays to zero with NO persistent component.

**Proof sketch:**
The velocity autocorrelation C_v(t) = ⟨v(0)·v(t)⟩ determines whether transport is diffusive (C_v integrable → finite D) or persistent (C_v has a non-decaying component → ballistic).

For an isotropic random network with symmetric hopping rates (γ_hop,ij = γ_hop,ji), by detailed balance and the isotropy of the disorder:

```
C_v(t) = (d²γ_hop) · exp(−2γ_hop·t)   [decays exponentially]
```

The integral ∫₀^∞ C_v(t) dt = d²/2 gives the diffusion constant D = d²γ_hop/2.

There is NO persistent component. The Green-Kubo formula gives a purely diffusive result.

For a PRW, C_v(t) would have a component that decays at rate γ_rev ≪ γ_hop. This would require a separation of timescales: the persistence time τ_B = 1/(2γ_rev) ≫ 1/γ_hop. No physical mechanism in standard TLS creates this separation.

**Status: STANDARD TLS HOPPING IS PURELY DIFFUSIVE. Persistence FAILS.**

---

## 5. Could a Non-Standard TLS Model Be Constructed?

One could DEFINE a TLS model with persistence by hand:
- Each TLS site has an additional "direction" quantum number σ = ±1
- σ is preserved during hops and reverses at rate γ_rev
- The hop rate preferentially proceeds in direction σ

This REPRODUCES the PRW mathematically. But:
1. There is no known physical mechanism that gives TLS excitations a spatial direction quantum number
2. This would require TLS to have momentum-like quantum numbers, which they do not in the standard tunneling model
3. Even if constructed formally, the direction quantum number γ_rev would be a FREE parameter with no physical determination

**Status: A persistence mechanism CAN be postulated but CANNOT be derived from standard or physically defensible TLS physics.**

---

## 6. Verdict

**The TLS persistence mechanism FAILS physically.**

Standard TLS hopping in amorphous solids is a simple random walk (isotropic, no directional memory). No known physical mechanism in TLS dynamics generates the directional spatial persistence required by the PRW/C2 substrate model.

The specific failure modes:
1. Isotropy of amorphous solid → no directional preference
2. No momentum for TLS excitations → no momentum conservation persistence
3. Anderson localization → no coherent directed transport
4. Phonon-assisted directionality → conventional phonon physics, not TLS substrate

**Classification: T-D — TLS persistence mechanism fails physically.**

The TLS extension route must be abandoned UNLESS a new, physically motivated mechanism for directional persistence can be identified. The burden of proof is: demonstrate a specific physical process in TLS that is NOT equivalent to phonon transport and that generates persistent directional hopping across the chip scale.

No such mechanism has been found in this audit.
