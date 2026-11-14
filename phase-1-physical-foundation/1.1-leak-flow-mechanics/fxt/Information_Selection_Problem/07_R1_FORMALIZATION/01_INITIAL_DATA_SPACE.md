# 01_INITIAL_DATA_SPACE
## Precise Mathematical Description of the GR Initial-Data Space

**Date:** August 2026

---

## Level 1 — Raw Initial Data

A Cauchy initial-data set for GR consists of:

  (Σ, h_ij, K_ij, ψ, π_ψ)

where:
- Σ is a smooth connected 3-manifold (the spatial slice)
- h_ij is a Riemannian metric on Σ (positive definite, smooth)
- K_ij is a symmetric tensor on Σ (the extrinsic curvature)
- ψ represents matter fields
- π_ψ represents their conjugate momenta

The raw data space is:

  R = Riem(Σ) × Sym²(T*Σ) × (matter field space)

where Riem(Σ) is the space of all smooth Riemannian metrics on Σ.

This space is a Fréchet manifold — infinite-dimensional, with no canonical measure or finite volume.

---

## Level 2 — Constraint Surface

The GR constraint equations (energy constraint and momentum constraint) must be satisfied:

  H(h,K,ψ,π_ψ) ≡ R_Σ + K² − K_{ij}K^{ij} − 16πGρ(ψ,π_ψ) = 0
  H_i(h,K,ψ,π_ψ) ≡ −2∇_j(K^j_i − δ^j_i K) + 8πG J_i(ψ,π_ψ) = 0

The constraint surface is:

  C ≡ {(h,K,ψ,π_ψ) ∈ R | H = 0 and H_i = 0}

C is a sub-Fréchet-manifold of R. It is the space called Γ_GR in this program.

**Critical note:** Not every (Σ, h_ij, K_ij) satisfies the constraints. The constraints are an underdetermined elliptic PDE system. Solutions exist under conditions on the Yamabe class of h_ij and the magnitude of K (Isenberg 1995, Choquet-Bruhat 1952). However, for each reasonable choice of free data, solutions exist.

**The dimension of C:** For compact Σ without boundary, the constraint surface has codimension 4 per point in R (the constraints H and H_i impose 4 real conditions). However, R itself is infinite-dimensional, and C is also infinite-dimensional.

---

## Level 3 — Gauge-Equivalent Data

The diffeomorphism group Diff(Σ) acts on C by:

  φ · (h_ij, K_ij, ψ, π_ψ) = (φ*h_ij, φ*K_ij, φ*ψ, φ*π_ψ)

Two initial-data sets are gauge-equivalent (physically identical) if they are related by a diffeomorphism of Σ. The gauge group is Diff₀(Σ) (the connected component of the identity).

The set of gauge-equivalent classes is the quotient:

  C/Diff(Σ)

This is the "superspace" of York (1973) — not to be confused with supersymmetric theories.

---

## Level 4 — Reduced Phase Space

Superspace C/Diff(Σ) still has infinitely many degrees of freedom. For a compact spatial section without boundary, the constraint-reduced, diffeomorphism-reduced phase space is:

  Γ_red = C/Diff(Σ)

This is the true physical phase space. It carries a symplectic form ω inherited from the canonical symplectic form ω_can = ∫_Σ δπ^{ij} ∧ δh_{ij} d³x on R.

**Γ_GR in this program denotes C/Diff(Σ) — the constraint surface modulo spatial diffeomorphisms.** Every point in Γ_GR is a physical initial-data set for GR.

---

## Level 5 — Matter Degrees of Freedom

The matter fields (ψ, π_ψ) contribute to the constraints H and H_i via the energy density ρ and momentum density J_i. For the purposes of R1, the gravitational degrees of freedom are the primary concern. The matter sector is assumed to be in a thermal state (near-equilibrium) — the thermalization is explained by standard reheating. The unexplained residual is the gravitational sector.

**The gravitational reduced phase space** is obtained by further restricting to vacuum (ρ = 0, J_i = 0) or by tracing out the matter degrees of freedom:

  Γ_grav ⊂ Γ_GR (vacuum initial data)

R1 specifically concerns the gravitational sector. For the purposes of the primitive search, we have been working with Γ_grav — the space of vacuum initial data satisfying H_vac = 0 and H_i = 0 with T_{μν} = 0.

---

## Level 6 — Boundary and Asymptotic Conditions

The topology and boundary conditions on Σ matter for what initial data is possible:

**Compact Σ (e.g., S³, T³):** No boundary. The constraints are globally coupled PDEs. The Yamabe class of the metric determines which constraint solutions exist (Isenberg 1995).

**Non-compact Σ (e.g., R³):** Asymptotic flatness conditions are imposed: h_{ij} → δ_{ij} + O(r^{-1}), K_{ij} → O(r^{-2}) as r → ∞. The ADM mass and momentum are defined. The Kasner metric on R³ is in this class (with appropriate falloff of the anisotropy), though strictly Kasner is on a flat spatial section.

**The problem uses both:** Kasner is typically stated on R³; FLRW is stated on S³, T³, or R³ depending on spatial curvature. For R1, the relevant comparison is between (i) the smooth, near-homogeneous initial data of our observable universe and (ii) generic GR initial data — which includes both compact and non-compact cases.

---

## Level 7 — What Γ_GR Is Not

Γ_GR is NOT:
- A probability space (it has no canonical probability measure)
- A finite-dimensional manifold (it is infinite-dimensional)
- A Hilbert space (it is a classical phase space)
- A well-defined topological space without specification of the appropriate function space (Sobolev, Hölder, smooth)

These non-properties are important for the measure audit (file 02).

---

## The Object That R1 References

Current R1 uses "Γ_GR" and "extremely small region of phase space." This implicitly treats Γ_GR as a measure space. But as established here, Γ_GR = C/Diff(Σ) carries a symplectic form but no canonical probability measure.

The phrase "extremely small region of phase space" requires:
1. A topology or metric on Γ_GR
2. A measure μ on Γ_GR
3. A definition of the "physically realized region" Γ_phys ⊂ Γ_GR
4. A calculation showing μ(Γ_phys)/μ(Γ_GR) << 1

None of these four elements has been specified in the current R1 formulation. This is the subject of the measure audit.

---

*Document status: INITIAL DATA SPACE FORMALIZATION COMPLETE*
*Key result: Γ_GR = C/Diff(Σ) has a symplectic form but no canonical probability measure.*
*Date: August 2026*
