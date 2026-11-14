# TLS_SUBSTRATE_DERIVATION.md
## Microscopic TLS Model to Coarse-Grained Transport

**Date:** 2026-08-22
**Label convention:** DERIVED | ASSUMED | FREE | DEFINITION | CONVENTIONAL | FAILED

---

## 1. Microscopic Degrees of Freedom

**Physical setting:** Amorphous dielectric (SiO₂) near superconducting qubit Josephson junctions. Two-level systems (TLS) arise from pairs of atoms that tunnel between two nearly-degenerate configurations in the amorphous solid.

**TLS Hamiltonian (standard tunneling model):**

```
H_TLS = -(1/2)(Δ σ_z + ε σ_x)
```

where:
- ε [energy]: asymmetry energy (energy bias between two wells)
- Δ [energy]: tunneling amplitude (quantum mechanical coupling between wells)
- E = √(ε² + Δ²): splitting energy

**TLS parameters from experiment (SiO₂ at mK):**
- Δ/h: 0.01 – 10 GHz (tunneling amplitude)
- ε/h: 0.01 – 10 GHz (asymmetry)
- E/h: 0.01 – 15 GHz (splitting)
- Spatial density: ρ_TLS ~ 10²⁰ – 10²¹ m⁻³ (areal: n_TLS ~ 10¹⁵ – 10¹⁶ m⁻²)
- Inter-TLS spacing: d_TLS = ρ_TLS^{-1/3} ~ 1–3 nm

These are INDEPENDENTLY MEASURABLE from dielectric loss spectroscopy and TLS-qubit coupling measurements. They are not free parameters for the purposes of this derivation.

**TLS relaxation:** Each TLS relaxes at rate γ₁ = Γ₁ (longitudinal, energy exchange with phonon bath) and dephases at rate γ₂ = Γ₂ ≥ Γ₁/2. Typical values at mK:
- Γ₁ ~ 10³ – 10⁶ s⁻¹ (T₁ ~ µs to ms)
- Γ₂ ~ 10⁴ – 10⁷ s⁻¹ (T₂ ~ 0.1–100 µs)

Status: INDEPENDENTLY MEASURABLE.

---

## 2. TLS-TLS Interaction Mechanism

For two TLS at positions r_i and r_j with electric dipole moments p_i and p_j,
the interaction is dipole-dipole coupling:

```
V_ij = (p_i · p_j - 3(p_i·r̂)(p_j·r̂)) / (4πε₀ d_ij³)
```

where d_ij = |r_i - r_j|.

For TLS density 10²⁰ m⁻³ and d ~ 2 nm:
```
V_typical / h ~ p²/(4πε₀ ε_r d³ h)
              ~ (1e-30 C·m)² / (4π × 8.85e-12 × 10 × (2e-9)³ × 6.6e-34)
              ~ 0.1 – 1 MHz
```

This interaction is real and independently established in the TLS literature (Phillips 1987, Müller et al. 2019).

**Status:** The TLS-TLS dipole interaction is CONVENTIONAL physics, independently confirmed.

---

## 3. TLS Excitation Hopping

**Mechanism:** When two TLS (i and j) are nearly resonant (|E_i - E_j| ≪ V_ij), the dipole coupling V_ij drives energy transfer:

```
|↑↓⟩ ↔ |↓↑⟩
```

The hopping rate for resonant TLS (|E_i - E_j| < γ²):
```
γ_hop,ij = V_ij² / γ_ij
```

where γ_ij = (Γ₂,i + Γ₂,j)/2 is the dephasing broadening.

For V_ij/h ~ 0.1 MHz and γ_ij ~ 1 MHz:
```
γ_hop ~ (0.1 MHz)² / (1 MHz) ~ 0.01 MHz = 10⁴ s⁻¹
```

For d ~ 2 nm and γ_hop ~ 10⁴ s⁻¹:
```
c_hop = d × γ_hop = 2×10⁻⁹ m × 10⁴ s⁻¹ = 2×10⁻⁵ m/s
```

This is extremely slow — many orders of magnitude below v_s = 6000 m/s.

**Status:** DERIVED from known TLS parameters. The speed 2×10⁻⁵ m/s is NOT a prediction — it is computed from independently known parameters. This is the key GAP-7 test result (continued in GAP7_TLS_CLOSURE.md).

---

## 4. The Persistence Question — Core Issue

Standard TLS hopping is a RANDOM walk, not a PERSISTENT random walk.

When a TLS excitation hops from site i to site j, it has NO memory of the direction it came from. The next hop from j is equally likely in any direction — to any of the neighbors of j with approximately equal probability.

For a PERSISTENT random walk (PRW) to emerge, the excitation must preferentially continue in the same direction for a characteristic time τ_B before reversing. This is the fundamental requirement for the telegrapher equation rather than the diffusion equation.

**Is there a physical mechanism for persistence in TLS?**

This is the critical question. The derivation of the transport equation depends entirely on whether persistence exists. Proceeding to derive the transport equations assuming persistence is assumed first, followed by the persistence audit in TLS_PERSISTENCE_AUDIT.md.

For the purposes of this derivation document, I introduce persistence as a HYPOTHESIS and derive what follows from it. The validity of the hypothesis is assessed separately.

---

## 5. Coarse-Grained Transport Derivation

**Setup:** A 2D network of TLS sites on a substrate at positions {r_i}. An excitation (excited TLS) hops between sites. Define:

- p^+(r,t): density of excitations moving in direction θ ∈ [0, π) (right-ward in 1D)
- p^-(r,t): density of excitations moving in direction θ ∈ [π, 2π) (left-ward in 1D)

In 1D, the master equation for a PRW with hop speed c = d·γ_hop and reversal rate γ_rev is:

```
∂p⁺/∂t = −c ∂p⁺/∂x − γ_rev p⁺ + γ_rev p⁻   [ASSUMED: PRW form]
∂p⁻/∂t = +c ∂p⁻/∂x + γ_rev p⁺ − γ_rev p⁻
```

This is IDENTICAL in form to the C2 PRW balance equations with:
- c → c_TLS = d_TLS × γ_hop
- λ → γ_rev (persistence reversal rate)
- τ_B = 1/(2γ_rev)
- ξ_c = c_TLS / γ_rev = d_TLS × γ_hop / γ_rev

Eliminating p⁻:
```
τ_B ∂²ρ/∂t² + ∂ρ/∂t = c_TLS² τ_B ∇²ρ    [DERIVED from PRW form — telegrapher equation]
```

where ρ = p⁺ + p⁻.

**CRITICAL STATUS:** This derivation assumes the PRW form of the master equation. If TLS hopping is a SIMPLE random walk (not persistent), the equation is instead:

```
∂ρ/∂t = D ∇²ρ,   D = d²γ_hop/2    [DERIVED from simple random walk — diffusion]
```

The transition from diffusion to telegrapher depends entirely on whether persistence is real. The telegrapher equation is NOT derived from TLS physics — it is derived assuming the PRW is the right model.

---

## 6. Parameter Identification

If the PRW assumption holds, parameter identification gives:

| C2 parameter | TLS expression | Status |
|-------------|---------------|--------|
| c | d_TLS × γ_hop | DERIVED (given PRW assumption) |
| τ_B | 1/(2γ_rev) | DERIVED (given PRW assumption) |
| ξ_c | d_TLS × γ_hop / γ_rev | DERIVED (given PRW assumption) |
| γ_rev | reversal rate of hop direction | ASSUMED (hypothesis) |
| d_TLS | inter-TLS spacing | INDEPENDENTLY MEASURABLE |
| γ_hop | TLS-TLS energy transfer rate | DERIVED from V_ij and Γ₂ |

**The PRW assumption introduces γ_rev as a new parameter.** This is the persistence reversal rate — it is NOT the same as the TLS relaxation rate Γ₁ or dephasing rate Γ₂. It is a new physical quantity with no established experimental value.

---

## 7. Summary: What This Derivation Establishes

1. Standard TLS physics (dipole coupling, energy transfer) gives a DIFFUSION equation for excitation propagation. This is conventional.

2. IF persistence is assumed, the PRW/telegrapher equation follows with c = d_TLS × γ_hop.

3. The persistence assumption introduces a new free parameter γ_rev (reversal rate).

4. Without γ_rev determined independently, c remains a function of two quantities: d_TLS × γ_hop (computable from TLS literature) and the reversal rate γ_rev (unknown).

5. The full expression c_TLS = d_TLS × γ_hop gives c ~ 10⁻⁵ m/s for typical parameters — which IS ≪ v_s. But this is the HOP speed, not the PRW speed. The PRW propagation speed equals the hop speed only in the ballistic limit (γ_rev → 0). For finite γ_rev, the mean free path is ℓ = c/γ_rev = d_TLS × γ_hop/γ_rev.

**The derivation cannot be completed without resolving the persistence question.**

Status: BLOCKED pending TLS_PERSISTENCE_AUDIT.md.
