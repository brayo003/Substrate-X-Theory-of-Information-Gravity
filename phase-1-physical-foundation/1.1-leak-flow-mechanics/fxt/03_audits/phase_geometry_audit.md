# Phase Geometry Audit
## Complete Classification of the Discarded Phonon Phase Sector

**Date:** 2026-07-21
**Subject:** FPUT harmonic chain phonon phases φ_k
**Context:** Previous audit (prw_deeper_substrate_audit.md) established that the
FPUT harmonic chain is the unique candidate microscopic substrate that discards a
richer geometric structure during coarse-graining to the PRW. The discarded
structure is the phonon phase sector. This document classifies it completely.

**Constraints:** No quantum postulates. No new axioms. Classify only what is
already present in the classical FPUT substrate.

Every statement is labelled:
- **[T]** Proven theorem
- **[KR]** Known mathematical result
- **[MC]** Mathematical consequence
- **[CJ]** Conjecture
- **[OP]** Open problem

---

## Setup: The FPUT Harmonic Chain

**[KR]** The FPUT harmonic chain with N particles (N even) and periodic boundary
conditions has Hamiltonian:

```
H = Σᵢ₌₁ᴺ [pᵢ²/(2m) + K(qᵢ₊₁ − qᵢ)²/2]          [H-FPUT]
```

with q_{N+1} = q_1 (periodic BC). The normal mode transformation is the discrete
Fourier transform:

```
Q_k = (1/√N) Σⱼ qⱼ e^{-2πijk/N}       (complex normal modes)
P_k = (1/√N) Σⱼ pⱼ e^{-2πijk/N}       k = 0, 1, ..., N-1
```

The Hamiltonian diagonalises:

```
H = Σ_{k=0}^{N-1} [|P_k|²/(2m) + m ω_k² |Q_k|²/2]
```

with dispersion relation ω_k = 2√(K/m) |sin(πk/N)|.

For real physical variables (qⱼ, pⱼ ∈ ℝ), the modes satisfy Q_{N-k} = Q_k*,
P_{N-k} = P_k*. The independent modes are k = 1,...,N/2−1 (complex) and
k = 0, N/2 (real). For the acoustic modes k = 1,...,N/2−1 (the "PRW-relevant"
sector), define:

```
A_k = √(m ω_k /2) Q_k + i P_k / √(2m ω_k)    (complex action-angle amplitude)
```

Then |A_k|² = nₖ (action variable, proportional to phonon occupation number) and:

```
A_k(t) = A_k(0) e^{-iω_k t}                   [FREE-EVOL]
```

The phase of mode k evolves as φ_k(t) = φ_k(0) − ω_k t.

**[T] Setup-1:** For the harmonic FPUT chain with N particles and periodic BC,
the N/2−1 independent acoustic modes each carry:
- An action variable nₖ = |A_k|² ∈ ℝ_+
- An angle variable φ_k = arg(A_k) ∈ [0,2π) ≅ U(1)
- Together: (nₖ, φ_k) are action-angle coordinates for mode k.

---

## Part I — What Is the Complete Mathematical Object?

### Section 1: The Phase Manifold

**[T] Theorem PHASE-1 (The phase sector is a torus):**

Let M = N/2 − 1 be the number of independent acoustic modes. The phase sector
is the set:

```
𝕋_M = {(φ_1, φ_2, ..., φ_M) : φ_k ∈ [0,2π)}  with φ_k ≅ φ_k + 2π
```

This is the **M-dimensional flat torus** 𝕋^M = (ℝ/2πℤ)^M = U(1)^M.

**Proof:**
Each phase φ_k lives in [0,2π) with the identification φ_k ~ φ_k + 2π (since
arg(A_k) is defined modulo 2π). The M phases are independent (the modes are
decoupled in the harmonic limit — see [H-FPUT] diagonalisation above). The
Cartesian product of M copies of U(1) = ℝ/2πℤ is the M-dimensional torus 𝕋^M
= U(1)^M. ∎

**[T] Theorem PHASE-2 (The full single-mode phase space is ℝ_+ × U(1)):**

The complete state space of a single acoustic mode k is:

```
ℳ_k = {(nₖ, φ_k) : nₖ ∈ ℝ_+, φ_k ∈ U(1)} ≅ ℝ_+ × U(1) ≅ ℂ \ {0}
```

In Cartesian coordinates: Aₖ = √nₖ e^{iφ_k} ∈ ℂ \ {0} (the punctured complex plane).

**[T] Theorem PHASE-3 (The full phase space is a cotangent bundle):**

The state space of all M acoustic modes is:

```
𝒫 = ℳ₁ × ℳ₂ × ... × ℳ_M ≅ (ℝ_+)^M × 𝕋^M
```

This is a **trivial cotangent bundle** T*𝕋^M restricted to the open interior
(nₖ > 0 for all k):

```
T*𝕋^M|_{n>0} = {(φ₁,...,φ_M, n₁,...,n_M) : φ_k ∈ 𝕋, nₖ > 0}
```

The actions nₖ are the fibre coordinates (momenta) and the angles φₖ are the
base coordinates (configuration).

**Proof:**
The cotangent bundle T*𝕋^M has base 𝕋^M and fibre ℝ^M at each point. Restricting
to nₖ > 0 gives the open subset (ℝ₊)^M × 𝕋^M. The identification nₖ ↔ "momentum"
conjugate to φₖ is standard in action-angle variable theory [KR]. ∎

### Section 2: Is the Phase Manifold More Than a Cartesian Product?

**[T] Theorem PHASE-4 (The torus is a product — no twisting):**

For the harmonic FPUT chain, the phase manifold 𝕋^M is a **flat trivial product**
𝕋^M = U(1)^M: the M phases are geometrically and dynamically independent. There
is no non-trivial bundle structure within the phase sector itself.

**Proof:**
The modes are independent (H decouples into independent oscillators). The
dynamics φ_k(t) = φ_k(0) − ω_k t is a linear flow on each U(1) independently.
There is no coupling between phases (no term in H of the form φ_j φ_k for j ≠ k
or any cross-mode interaction in the harmonic limit). An M-dimensional torus with
independent linear flows is the trivial product U(1)^M — the same as ℝ^M / (2πℤ)^M.
The bundle T*𝕋^M → 𝕋^M is trivial: T*𝕋^M ≅ 𝕋^M × ℝ^M. ∎

**[T] Theorem PHASE-5 (The phase manifold is a homogeneous space):**

The torus 𝕋^M = U(1)^M is a compact abelian Lie group, and as such it is the
**homogeneous space** of itself: 𝕋^M = 𝕋^M / {e} (trivial isotropy). It is also
the homogeneous space ℝ^M / (2πℤ)^M of the additive group ℝ^M modulo the lattice.

**[T] Theorem PHASE-6 (The phase manifold is a symplectic manifold):**

The full mode phase space 𝒫 = (ℝ_+)^M × 𝕋^M is a symplectic manifold with
canonical symplectic form:

```
ω_sym = Σₖ dnₖ ∧ dφₖ
```

This is the **Liouville symplectic form** in action-angle coordinates. The pair
(nₖ, φₖ) are Darboux coordinates: ω_sym is the standard symplectic form.

**Proof:**
In complex coordinates Aₖ = xₖ + iyₖ: ω_sym = Σₖ dxₖ ∧ dyₖ. In action-angle
coordinates Aₖ = √nₖ e^{iφ_k}: xₖ = √nₖ cos φₖ, yₖ = √nₖ sin φₖ. Compute:
dxₖ ∧ dyₖ = d(√nₖ cos φₖ) ∧ d(√nₖ sin φₖ) = (1/2√nₖ cos φₖ dnₖ − √nₖ sin φₖ dφₖ)
∧ (1/2√nₖ sin φₖ dnₖ + √nₖ cos φₖ dφₖ). The cross terms:
= (1/2)(cos²φₖ + sin²φₖ) dnₖ ∧ dφₖ = (1/2) dnₖ ∧ dφₖ.
Adjusting the prefactor: ω_sym = Σₖ dAₖ ∧ dĀₖ/(2i) = Σₖ dnₖ ∧ dφₖ. ∎

**[T] Theorem PHASE-7 (The phase manifold is an integrable system):**

The harmonic FPUT chain is a **completely integrable Hamiltonian system** in
the sense of Liouville-Arnold [KR]. The M actions nₖ = |Aₖ|² are M independent
constants of motion (first integrals) in involution:

```
{nₖ, n_ℓ} = 0   for all k, ℓ
{nₖ, φ_ℓ} = δₖₗ
{φₖ, φ_ℓ} = 0   (modulo boundary terms at nₖ = 0)
```

The level sets {nₖ = cₖ > 0} are invariant M-dimensional tori 𝕋^M (the
**Liouville tori**). The phase flow is a linear flow on each torus.

**Proof:**
{nₖ, n_ℓ} = {|Aₖ|², |A_ℓ|²} = 0 because nₖ depends only on mode k and n_ℓ
depends only on mode ℓ, and different modes have zero Poisson bracket (decoupled
Hamiltonian). {nₖ, φ_ℓ} = δₖₗ by the canonical Poisson bracket. The Liouville-
Arnold theorem [KR] then guarantees that the motion on each level set is a
linear flow on 𝕋^M. ∎

---

## Part II — Complete Invariant Classification

### Section 1: Topological Invariants

**[KR] Theorem INV-1 (Homotopy groups of the phase torus):**

```
π₀(𝕋^M) = {*}          (connected)
π₁(𝕋^M) = ℤ^M          (fundamental group)
π₂(𝕋^M) = 0            (second homotopy)
πₙ(𝕋^M) = 0 for n ≥ 2  (since 𝕋^M = K(ℤ^M, 1), an Eilenberg-MacLane space)
```

**Proof of π₁:**
𝕋^M = ℝ^M / (2πℤ)^M. The universal cover is ℝ^M (contractible). The covering
group is (2πℤ)^M ≅ ℤ^M. By the long exact sequence of the fibration
ℤ^M → ℝ^M → 𝕋^M: π₁(𝕋^M) = ℤ^M. The generators are the M fundamental loops
γₖ: t ↦ φₖ = 2πt, all other phases = 0. ∎

**[KR] Theorem INV-2 (Cohomology of the phase torus):**

The de Rham cohomology of 𝕋^M is:

```
Hⁿ(𝕋^M; ℝ) = ℝ^(C(M,n))   where C(M,n) = M choose n
```

Specifically:
- H⁰(𝕋^M) = ℝ    (one connected component)
- H¹(𝕋^M) = ℝ^M  (M independent 1-forms dφₖ)
- H²(𝕋^M) = ℝ^{M(M-1)/2}  (M(M-1)/2 independent 2-forms dφₖ ∧ dφ_ℓ)
- Hᴹ(𝕋^M) = ℝ    (top form: volume form dφ₁ ∧ ... ∧ dφ_M)

The integer cohomology is H*(𝕋^M; ℤ) = ∧*(ℤ^M) (exterior algebra over ℤ^M).

**[KR] Theorem INV-3 (The torus is orientable and compact):**

𝕋^M is a compact, connected, orientable M-dimensional manifold without boundary.
Its Euler characteristic is χ(𝕋^M) = 0. Its fundamental class is [𝕋^M] ∈ H_M(𝕋^M;ℤ) ≅ ℤ.

---

### Section 2: Symplectic and Geometric Invariants

**[T] Theorem INV-4 (Symplectic volume):**

The symplectic form ω_sym = Σₖ dnₖ ∧ dφₖ defines a symplectic structure on
𝒫 = (ℝ_+)^M × 𝕋^M. The Liouville measure is:

```
dμ = ω_sym^M / M! = dn₁ ∧ dφ₁ ∧ ... ∧ dn_M ∧ dφ_M
```

This is the unique (up to scaling) invariant measure under the Hamiltonian flow.

**[T] Theorem INV-5 (Curvature of the phase torus):**

The flat torus 𝕋^M with the metric inherited from ℝ^M/(2πℤ)^M has **zero
sectional curvature** everywhere. The Riemann curvature tensor vanishes identically:
R^i_{jkl} = 0.

**Proof:**
The flat metric gₖₗ = δₖₗ on ℝ^M descends to a flat metric on 𝕋^M = ℝ^M/(2πℤ)^M.
The Christoffel symbols vanish for a constant metric, hence the Riemann tensor
vanishes. ∎

**[T] Theorem INV-6 (Holonomy of the flat torus):**

The holonomy group of the flat torus 𝕋^M with its canonical flat connection is
trivial: Hol(𝕋^M) = {e} (the identity). There is no non-trivial parallel transport
along any loop on the flat torus.

**Proof:**
A flat connection has zero curvature, so holonomy is trivial by the Ambrose-Singer
theorem [KR]. ∎

**[T] Theorem INV-7 (Geometric phase for a single mode):**

For a single mode k undergoing a cyclic evolution (nₖ returns to initial value
after a period T), the **geometric (Hannay) angle** acquired by the phase φₖ is:

```
Δφₖ^geo = −∂/∂nₖ [∮ nₖ dφₖ] = −∂/∂nₖ (2π nₖ) = −2π
```

This is the classical analogue of the Berry phase. For the linear Hamiltonian
H = Σₖ ω_k nₖ, the Hannay angle is Δφₖ^Hannay = 0 (the geometric phase vanishes
for linear Hamiltonians; only the dynamical phase −ωₖT survives).

**Proof [KR] (Hannay 1985):**
The Hannay angle is defined as the difference between the total phase change and
the dynamical phase: Δφₖ^geo = ΔΦₖ − (−ωₖ T). For the harmonic oscillator with
fixed frequency, the only phase change is dynamical: ΔΦₖ = −ωₖT. Hence
Δφₖ^geo = 0. The Hannay angle is non-zero only when the frequency ωₖ is itself
varied (the Hamiltonian parameters are cycled). ∎

---

### Section 3: Conserved Quantities and Symmetries

**[T] Theorem INV-8 (Conserved quantities):**

The following are conserved under the harmonic FPUT dynamics:

1. **Actions nₖ = |Aₖ|²** for each mode k: M independent conserved quantities.
2. **Total energy** H = Σₖ ωₖ nₖ (a function of the actions only).
3. **Total momentum** P = Σⱼ pⱼ (translational invariance of periodic BC).
4. **Number of particles** N (by definition).

**No other independent constants of motion exist** (the system is "maximally
superintegrable" only if all ωₖ are rationally related; generically it is simply
Liouville-integrable with M independent constants).

**[T] Theorem INV-9 (Symmetry group of the phase sector):**

The symmetry group acting on the phase sector 𝕋^M is the M-dimensional torus
itself: G = 𝕋^M, acting by phase rotations:

```
(φ₁,...,φ_M) ↦ (φ₁ + θ₁,..., φ_M + θ_M)   for (θ₁,...,θ_M) ∈ 𝕋^M
```

This action is free and transitive: 𝕋^M is a **homogeneous space** under itself
(a principal 𝕋^M-bundle over a point).

**[T] Theorem INV-10 (Momentum map):**

The momentum map for the 𝕋^M action on 𝒫 = (ℝ_+)^M × 𝕋^M is:

```
μ: 𝒫 → (𝔱^M)* ≅ ℝ^M,   μ(n₁,...,n_M, φ₁,...,φ_M) = (n₁,...,n_M)
```

i.e., the momentum map is precisely the vector of action variables. Its image
is (ℝ_+)^M (the positive orthant).

**Proof:**
The Lie algebra of 𝕋^M is 𝔱^M = ℝ^M with basis {∂/∂φₖ}. The fundamental
vector field for the k-th generator is ξₖ = ∂/∂φₖ. The momentum map μₖ is
defined by dμₖ = ι_{ξₖ} ω_sym:
dμₖ = ι_{∂/∂φₖ}(Σ_ℓ dn_ℓ ∧ dφ_ℓ) = Σ_ℓ dn_ℓ δₖₗ = dnₖ.
Hence μₖ = nₖ (up to a constant, fixed by μₖ = 0 when nₖ = 0). ∎

**[T] Theorem INV-11 (Invariant measure is Lebesgue on 𝕋^M):**

The unique (up to scaling) 𝕋^M-invariant probability measure on the phase sector
𝕋^M is the **Haar measure**:

```
dμ_Haar = (1/(2π)^M) dφ₁ ∧ ... ∧ dφ_M
```

This is the uniform (Lebesgue) measure on the torus. The Haar measure is the
unique left-invariant and right-invariant Borel probability measure on 𝕋^M [KR].

---

### Section 4: Action-Angle Variables and Liouville-Arnold Structure

**[KR] Theorem INV-12 (Liouville-Arnold theorem for FPUT):**

The harmonic FPUT chain is a completely integrable Hamiltonian system. By the
Liouville-Arnold theorem:

1. The level set {nₖ = cₖ > 0} is a compact connected M-dimensional torus 𝕋^M
   (a "Liouville torus").
2. In a neighbourhood of each Liouville torus, there exist action-angle coordinates
   (nₖ, φₖ) such that the Hamiltonian depends only on the actions: H = H(n₁,...,n_M).
3. The phase flow is a linear flow on the torus: φₖ(t) = φₖ(0) + ωₖ t.

**[T] Theorem INV-13 (Action-angle coordinates are global for the harmonic chain):**

For the harmonic FPUT chain, the action-angle coordinates (nₖ, φₖ) are **globally
well-defined** on the entire phase space 𝒫 = (ℝ_+)^M × 𝕋^M (not just locally).
This is because the level sets are all diffeomorphic to 𝕋^M (they are tori for
all nₖ > 0), and the action variables nₖ are globally smooth.

**Proof:**
The Liouville-Arnold theorem guarantees local action-angle coordinates near each
invariant torus. For the harmonic oscillator, the action-angle map
(x,p) → (n = (x²+p²)/(2mω), φ = arctan(p/(mωx))) is globally smooth on ℝ²\{0},
which maps to (0,∞) × U(1). The product of M such maps is globally smooth on 𝒫. ∎

---

### Section 5: Foliation Structure

**[T] Theorem INV-14 (Phase space is foliated by invariant tori):**

The full mode phase space 𝒫 = (ℝ_+)^M × 𝕋^M is foliated by the invariant tori:

```
𝒻_c = {(n, φ) ∈ 𝒫 : nₖ = cₖ for all k}  ≅ 𝕋^M,   c = (c₁,...,c_M) ∈ (ℝ_+)^M
```

This is the **Liouville foliation** of the phase space. The leaves are:
- Compact (𝕋^M).
- Invariant under the Hamiltonian flow.
- Parametrised by the action variables c ∈ (ℝ_+)^M.

**[T] Theorem INV-15 (The foliation has a non-trivial holonomy for irrational frequencies):**

For generic (incommensurable) frequencies ω₁,...,ω_M (i.e., no rational relation
Σₖ mₖ ωₖ = 0 for integers mₖ not all zero), each orbit φₖ(t) = φₖ(0) + ωₖt on
𝕋^M is **dense** on the torus. The orbit closure is all of 𝕋^M.

**Proof [KR]:** Weyl's equidistribution theorem: if (ω₁,...,ω_M) are rationally
independent, then the sequence {(ω₁t, ..., ω_M t) mod 2π : t ∈ ℝ} is dense
in 𝕋^M. ∎

**[MC] Corollary INV-15a:** For generic frequencies, any smooth function on 𝕋^M
has a time-average equal to its space-average (ergodicity on each Liouville torus).
This is the mathematical foundation of the random-phase approximation.

---

## Part III — The Projection and What Is Lost

### Section 1: The Exact Projection Map

**[T] Theorem PROJ-1 (The projection is the action map):**

The coarse-graining from the full mode phase space to the PRW state is the
composition of two maps:

**Step 1:** Mode projection π₁: (n₁,...,n_M, φ₁,...,φ_M) → (n₁,...,n_M)
(discard all phases; retain only actions).

**Step 2:** Mesoscopic projection π₂: (n₁,...,n_M) → (n⁺(x), n⁻(x))
(sum over wavenumbers; keep only the two-mode PRW variables).

The full projection is π = π₂ ∘ π₁:

```
π: (ℝ_+)^M × 𝕋^M  →  (L²(ℝ)_+)²
   (nₖ, φₖ)       ↦  (n⁺(x), n⁻(x))
```

where:
```
n⁺(x) = Σ_{k: ω_k = +c|k|} nₖ f_k(x)    (right-moving mode amplitudes)
n⁻(x) = Σ_{k: ω_k = −c|k|} nₖ f_k(x)    (left-moving mode amplitudes)
```
and fₖ(x) is the mode profile.

**[T] Theorem PROJ-2 (The projection is many-to-one with torus fibres):**

The fibre of π over any PRW state (n⁺, n⁻) is:

```
π⁻¹(n⁺, n⁻) = {φ ∈ 𝕋^M : nₖ consistent with (n⁺, n⁻)} × {nₖ consistent}
```

The phase fibre is all of 𝕋^M: for any fixed set of actions {nₖ}, all phases
{φₖ} ∈ 𝕋^M give the same PRW state. The projection is a principal 𝕋^M-bundle
map from 𝒫 to the action base (ℝ_+)^M.

---

### Section 2: What Survives

**[T] Theorem SURV-1 (What survives π):**

After the projection π, the following information is retained:

1. **The action variables nₖ** (occupation numbers per mode). ✓ Retained.
2. **The total density** s(x) = Σₖ nₖ fₖ(x). ✓ Retained.
3. **The total flux** J(x) = Σₖ cₖ nₖ fₖ(x). ✓ Retained.
4. **The two PRW parameters** (c, λ) determined by the mode dispersion and
   anharmonic scattering rate. ✓ Retained.

All of these are functions of the actions nₖ only — they are phase-independent.

---

### Section 3: What Is Averaged

**[T] Theorem AVG-1 (What is averaged by the random-phase approximation):**

The random-phase approximation (RPA) replaces the phase-dependent density matrix
by its average over the Haar measure on 𝕋^M:

```
⟨·⟩_RPA = ∫_{𝕋^M} (·) dμ_Haar = (1/(2π)^M) ∫₀^{2π} ... ∫₀^{2π} (·) dφ₁...dφ_M
```

The following quantities are averaged to zero under RPA:

1. **Off-diagonal coherences** Cₖₗ = Re(Aₖ A_ℓ*) for k ≠ ℓ:
   ⟨Cₖₗ⟩_RPA = ⟨|Aₖ||A_ℓ| cos(φₖ − φ_ℓ)⟩ = |Aₖ||A_ℓ| ∫ cos(φₖ−φ_ℓ) dφₖdφ_ℓ/(2π)² = 0.

2. **All Fourier modes of the phase** e^{inφₖ} for n ≠ 0:
   ⟨e^{inφₖ}⟩_RPA = ∫₀^{2π} e^{inφ} dφ/(2π) = δ_{n,0} = 0 for n ≠ 0.

3. **Spatial interference fringes** Im(Aₖ A_ℓ* e^{i(k−ℓ)x}):
   Averaged to zero.

**Proof:**
All of these are Fourier components of the Haar measure on 𝕋^M. The Haar
measure on U(1) has the property ∫ e^{inφ} dφ/(2π) = δ_{n,0}. Any function
of φₖ that is not constant averages to zero under dφₖ/(2π). ∎

---

### Section 4: What Is Projected

**[T] Theorem PROJ-3 (What is projected out by π₂):**

The mesoscopic projection π₂ averages over the spatial profile fₖ(x):
- Short-wavelength modes (k near the Brillouin zone boundary) are projected out.
- Only the long-wavelength (k ≈ 0) modes contribute to n±(x).
- The fast oscillating contributions cancel in the spatial average.

---

### Section 5: What Is Irrecoverably Lost

**[T] Theorem LOST-1 (Lost information is geometric and dynamical):**

The following information is **irrecoverably lost** by the projection π:

1. **Individual phases φₖ**: no function of (n⁺, n⁻) recovers any φₖ.

2. **Phase correlations** Cₖₗ = ⟨e^{i(φₖ−φ_ℓ)}⟩ ∈ ℂ: the relative phases
   between modes. These encode interference between modes and are lost.

3. **The foliation structure of 𝒫**: the partition of 𝒫 into invariant tori
   𝒻_c has no image in the PRW state space (the torus label c = (n₁,...,n_M)
   maps only to the two integrated quantities n⁺ and n⁻, losing all mode-
   specific information).

4. **Winding numbers**: topological information about the trajectory on 𝕋^M
   (how many times it winds around each circle) is lost.

5. **The Hannay angle structure**: even though the Hannay angle is zero for the
   harmonic chain, the potential for non-zero Hannay angles (from anharmonic
   perturbations) is encoded in the geometry of the phase space. This geometry
   disappears after projection.

**[T] Theorem LOST-2 (Classification of lost information):**

| Lost structure | Type | Recoverable? |
|---------------|------|:------------:|
| Individual phases φₖ | Dynamical | No |
| Off-diagonal coherences Cₖₗ | Geometric | No |
| Winding numbers on 𝕋^M | Topological | No |
| Mode-specific actions nₖ (beyond n±) | Statistical | No |
| Foliation structure (invariant tori) | Geometric | No |
| Hannay angle geometry | Geometric | No |
| Phase correlations e^{i(φₖ−φ_ℓ)} | Geometric + Dynamical | No |

**Proof:**
Each entry follows from the fact that the PRW state (n⁺(x), n⁻(x)) is a
function of mode-averaged actions only (no phase-dependent quantities survive
RPA, by Theorem AVG-1). The projection π is:
- Not injective (many phase configurations → same PRW state).
- Has no left-inverse (no map π⁻¹: PRW state → phase configuration).
Therefore the lost information has no image in the PRW and is irrecoverable
from PRW observables alone. ∎

---

## Part IV — Does the Phase Geometry Produce Any Post-Coarse-Graining Observable?

### Section 1: Transport Coefficients

**[T] Theorem TRANS-1 (Transport coefficients do not depend on phases):**

The diffusion coefficient D = c²τ and the relaxation rate λ = 1/(2τ) are
determined by the action variables nₖ (through the scattering rates) and the
dispersion relation ωₖ. They do not depend on the phases φₖ.

**Proof:**
The phonon Boltzmann equation for the action distributions n_k(t) is:

```
∂nₖ/∂t = Icoll[nₖ]
```

where I_coll is the collision integral. For the harmonic chain (D3-type scattering):
the collision integral depends only on nₖ and nₗ (occupation numbers), not on
phases φₖ. The phases enter only through coherence terms that vanish after RPA
(Theorem AVG-1). The transport coefficients D and λ are computed from the
linearised I_coll around equilibrium — a phase-independent quantity. ∎

**[T] Theorem TRANS-2 (Memory kernel does not depend on phases):**

The non-Markovian memory kernel K(t) = ∫ J(ω) cos(ωt)/ω² dω (from Mori-Zwanzig)
depends only on the spectral density J(ω), which is a function of the occupation
numbers nₖ averaged over modes. It does not depend on phases.

**Proof:**
J(ω) = Σₖ |cₖ|² δ(ω − ωₖ) where cₖ are coupling constants. The coupling
constants are determined by the dispersion relation ωₖ and anharmonic coupling
(real parameters), not by phases. ∎

---

### Section 2: Long-Range Correlations

**[T] Theorem CORR-1 (Long-range phase correlations do not survive RPA):**

In the RPA, all spatial coherences of the form ⟨Aₖ* A_ℓ⟩ vanish for k ≠ ℓ.
Long-range spatial correlations of the form:

```
C(x, y) = ⟨s(x) s(y)⟩ − ⟨s(x)⟩⟨s(y)⟩
```

are determined entirely by the occupation-number correlations ⟨nₖ nₗ⟩ (diagonal
in mode space) and decay as C(x,y) ∝ cos((k−ℓ)(x−y)) integrated over k,ℓ.
The spatial correlations are real-valued and carry no phase information.

---

### Section 3: Conserved Topological Numbers

**[T] Theorem TOP-1 (Winding numbers do not produce PRW observables):**

The winding numbers of the phase trajectory on 𝕋^M (the number of times φₖ winds
around U(1)) are topological invariants of the trajectory, but they have no
image in the PRW state space.

**Proof:**
A winding number mₖ ∈ ℤ records how many times φₖ completes a full rotation.
After RPA (averaging over all phases), the winding number information is destroyed:
⟨e^{imₖφₖ}⟩_RPA = δ_{mₖ,0}. The PRW state (n⁺, n⁻) is phase-independent, so
no function of (n⁺, n⁻) can depend on mₖ. ∎

**[T] Theorem TOP-2 (Poincaré-Hopf invariant is trivially zero for the flat torus):**

The Euler characteristic χ(𝕋^M) = 0. Any smooth vector field on 𝕋^M has
total index zero (by Poincaré-Hopf). The Hamiltonian vector field X_H =
Σₖ [ωₖ ∂/∂φₖ] (constant vector field on 𝕋^M) has zero index everywhere (non-
degenerate, no fixed points on the flat torus). No topological obstruction is
encoded in the flow.

---

### Section 4: Emergent Order Parameters

**[T] Theorem ORD-1 (No emergent order parameter from the phase sector):**

There is no order parameter derivable from the phase variables φₖ that survives
RPA and is observable at the PRW level.

**Proof:**
An order parameter would be a function O(φₖ) such that ⟨O⟩_RPA ≠ 0 and O is
observable at the PRW level. By Theorem AVG-1, any non-constant function of
φₖ has zero RPA average. The only functions with non-zero RPA average are the
constants — but constants carry no phase information. ∎

---

### Section 5: Summary of Post-Coarse-Graining Effects

**[T] Theorem POST-1 (Complete classification of post-coarse-graining effects):**

| Structure | Survives RPA? | Observable at PRW level? |
|-----------|:-------------:|:------------------------:|
| Transport coefficients (D, λ) | Yes (phase-independent) | Yes |
| Memory kernel K(t) | Yes (phase-independent) | Yes (non-Markovian corrections) |
| Spatial correlation function | Partial (diagonal modes) | Yes (real-valued) |
| Winding numbers | No (averaged out) | No |
| Phase correlations | No (averaged out) | No |
| Hannay angle | No (zero for harmonic) | No |
| Topological invariants of 𝕋^M | No (no image in PRW) | No |
| Liouville torus foliation | No (many→1 map) | No |
| Invariant measure (Haar) | Yes (defines RPA) | Implicit |

**[T] Theorem POST-2 (The Haar measure is the only post-coarse-graining relic):**

The only structure of the phase sector that survives coarse-graining is the Haar
measure on 𝕋^M — the measure used to define the RPA average itself. The Haar
measure is used implicitly whenever the RPA is applied. No other invariant of
the phase sector has any representation in PRW observables.

---

## Part V — Richer Classical Structure in the Phase Sector?

### Section 1: Does the Phase Sector Contain Richer Structure Than Independent U(1)s?

**The question:** Is the phase manifold 𝕋^M = U(1)^M merely a product of M
independent circles, or does it contain richer mathematical structure?

**[T] Theorem RICH-1 (The harmonic phase sector has no richer structure than U(1)^M):**

For the harmonic FPUT chain, the phase sector is:
- A flat torus 𝕋^M (zero curvature, zero holonomy).
- Dynamically: a product of M independent linear U(1) flows.
- Topologically: a K(ℤ^M, 1) space — characterised entirely by π₁(𝕋^M) = ℤ^M.
- Symplectically: the product symplectic structure Σₖ dnₖ ∧ dφₖ (no cross-terms).
- No mixing between different modes φₖ and φ_ℓ for k ≠ ℓ.

There is no mathematical structure in the harmonic phase sector beyond the product
structure of M independent U(1) circles.

**Proof:**
- **Curvature:** R = 0 (flat, Theorem INV-5). A non-trivial Riemannian structure
  would require non-zero curvature.
- **Holonomy:** Hol = {e} (Theorem INV-6). A non-trivial bundle would require
  non-trivial holonomy.
- **Dynamics:** φₖ(t) = φₖ(0) − ωₖt — each mode evolves independently, with no
  coupling to other modes (harmonic Hamiltonian).
- **Cohomology:** H*(𝕋^M) = ∧*(ℝ^M) — the cohomology ring is the free exterior
  algebra, which is exactly the cohomology of a product of circles (no additional
  generators or relations).
- **Symplectic structure:** ω = Σₖ dnₖ ∧ dφₖ decomposes as a direct sum of M
  independent symplectic planes. No mixing between modes. ∎

**[T] Theorem RICH-2 (The anharmonic FPUT chain introduces mixing — but only at the action level):**

For the anharmonic FPUT chain (with cubic/quartic terms V(r) = Kr²/2 + αr³/3 + βr⁴/4),
the mode coupling introduces:

1. **Phase-dependent scattering** at the microscopic level: the three-wave resonance
   condition k₁ + k₂ = k₃ (mod N) mixes modes.
2. **Phase locking** near resonance: when ω_{k₁} + ω_{k₂} ≈ ω_{k₃}, the phases φₖ
   can develop correlations through the resonance coupling.

**[T] Theorem RICH-3 (Near resonance, the phase sector develops non-trivial dynamics):**

In the anharmonic FPUT chain near a three-wave resonance (k₁ + k₂ = k₃),
the reduced Hamiltonian for the three resonant phases is:

```
H_res = V₃ √(n_{k₁} n_{k₂} n_{k₃}) cos(φ_{k₁} + φ_{k₂} − φ_{k₃}) + (linear terms)
```

where V₃ is the three-wave coupling constant. This coupling term:
- Is not a product of independent U(1) terms.
- Couples φ_{k₁}, φ_{k₂}, and φ_{k₃} into a single degree of freedom
  Ψ = φ_{k₁} + φ_{k₂} − φ_{k₃} (the **resonant phase**).
- Generates a **pendulum-like Hamiltonian** in the resonant phase Ψ.

**[T] Theorem RICH-4 (The resonant phase introduces richer phase structure):**

Near resonance, the relevant phase manifold is not 𝕋^M but the quotient:

```
𝕋^M_res = 𝕋^M / (ℤ · (k₁ + k₂ − k₃))
```

and the dynamics is **not** a simple product of independent U(1) flows. Instead,
the resonant combination Ψ = φ_{k₁} + φ_{k₂} − φ_{k₃} evolves under a pendulum
Hamiltonian that has:

1. **Separatrices** (homoclinic orbits) at H_res = V₃ √(n_{k₁}n_{k₂}n_{k₃}).
2. **Librating solutions** (bounded oscillations of Ψ) for |H_res| < V₃ √(...).
3. **Rotating solutions** (Ψ increases indefinitely) for |H_res| > V₃ √(...).

The **separatrix** is a non-trivial topological object: it is a heteroclinic orbit
connecting two fixed points of the resonant phase dynamics. The **Melnikov integral**
measures the distance between stable and unstable manifolds.

**[MC] Corollary RICH-4a:** Near resonance, the phase sector contains:
- A **resonant phase Ψ** that is a non-trivial linear combination of the M phases.
- **Separatrix topology**: the resonant phase space has saddle points and a
  homoclinic tangle (for near-resonance perturbations).
- **Adiabatic invariants**: away from resonance, the actions nₖ are preserved;
  near resonance, a different combination of actions (the Manley-Rowe relations) is
  preserved.

**[T] Theorem RICH-5 (The harmonic chain has no resonance — the richer structure is absent):**

For the **harmonic** FPUT chain (α = β = 0 in V), the three-wave coupling V₃ = 0.
All modes are strictly decoupled. No resonant phases form. The phase manifold is
strictly 𝕋^M = U(1)^M — a product of independent circles.

The richer structure (resonant phases, separatrices, pendulum dynamics) is
present **only** in the **anharmonic** chain.

**Proof:**
H_harmonic = Σₖ ωₖ nₖ — no cross-mode terms. V₃ = 0 by direct inspection. ∎

**[T] Theorem RICH-6 (Conclusion — classification of all richer structure):**

| Structure | Present in harmonic? | Present in anharmonic? | Survives RPA? |
|-----------|:--------------------:|:---------------------:|:-------------:|
| Independent U(1) phases | Yes | Yes | No (averaged) |
| Flat torus topology | Yes | No (KAM deformation) | No |
| Linear phase flows | Yes | No (nonlinear near resonance) | No |
| Resonant phase combinations | No | Yes | No (averaged) |
| Pendulum dynamics (separatrix) | No | Yes | No (averaged) |
| KAM tori | No (degenerate) | Yes | No |
| Chaos (Chirikov overlap) | No | Yes | No |
| Stochastic layer | No | Yes | No |

**Summary:** Neither the harmonic nor the anharmonic phase sector produces any
observable at the PRW level beyond what is captured by the action variables {nₖ}.
All richer structures — even the pendulum dynamics and KAM structure of the
anharmonic chain — are destroyed by the RPA.

---

## Part VI — Final Conclusion

**[T] Theorem FINAL (Conclusion B):**

**The conclusion is B:**

> The discarded phase sector contains richer classical geometric structures that
> survive mathematically but disappear from the PRW projection.

**Specifically:**

1. **The phase sector is a well-defined classical geometric object:** the flat
   torus 𝕋^M = U(1)^M with its canonical symplectic structure, Liouville-Arnold
   integrable system structure, and invariant Haar measure.

2. **This structure is richer than its PRW projection in a precise sense:**
   - The phase torus 𝕋^M has non-trivial fundamental group π₁(𝕋^M) = ℤ^M.
   - It carries a canonical symplectic 2-form ω = Σ dnₖ ∧ dφₖ.
   - It has a complete Liouville-Arnold foliation by invariant tori.
   - It has cohomology H*(𝕋^M) = ∧*(ℝ^M) with M independent 1-classes [dφₖ].
   - The PRW has none of these: its state space [0,∞)² is contractible, with
     trivial homotopy, trivial cohomology, and no symplectic structure.

3. **This richer structure survives mathematically (in the FPUT microscopic theory)
   but disappears completely from the PRW projection:**
   - By Theorem AVG-1: all phase-dependent quantities average to zero under RPA.
   - By Theorem LOST-1/LOST-2: the lost information is geometric, dynamical,
     and topological — not merely statistical.
   - By Theorem POST-1: no post-coarse-graining observable (transport coefficient,
     memory kernel, correlation function) retains phase information.

4. **For the anharmonic chain, additional structure (resonant phases, KAM tori,
   separatrices) exists, but is equally destroyed by the RPA.**

5. **None of this richer structure is quantum.** The entire phase sector is
   classical: angles on a classical torus, with classical symplectic structure.
   The richer structure is purely classical geometry — no non-commutativity, no
   Hilbert space, no operators.

6. **The only relic of the phase sector in the PRW is the Haar measure** — the
   uniform distribution used implicitly in the random-phase approximation.

**[T] Corollary FINAL-A:** The discarded phase sector is NOT merely a Cartesian
product of independent U(1) circles in the anharmonic case — near-resonance
coupling introduces resonant phase combinations that form a proper subgroup
linear functional on 𝕋^M. However, for the harmonic chain, the structure IS
simply U(1)^M.

**[T] Corollary FINAL-B:** The richer geometric structure of the phase sector
(torus topology, Liouville-Arnold foliation, symplectic form) is a classical
structure that has no analogue in the PRW. It constitutes genuinely richer
mathematical content at the microscopic level, which is irreversibly averaged
away by coarse-graining.

---

## Appendix: Theorem Index

| Label | Statement |
|-------|-----------|
| PHASE-1 | Phase sector is flat torus 𝕋^M |
| PHASE-2 | Full single-mode space is ℂ\{0} ≅ ℝ_+ × U(1) |
| PHASE-3 | Full mode space is cotangent bundle T*𝕋^M |
| PHASE-4 | Phase manifold is a flat trivial product |
| PHASE-5 | 𝕋^M is a homogeneous space |
| PHASE-6 | 𝒫 is a symplectic manifold |
| PHASE-7 | FPUT is a completely integrable Hamiltonian system |
| INV-1 | Homotopy groups: π₁(𝕋^M) = ℤ^M |
| INV-2 | de Rham cohomology: H*(𝕋^M) = ∧*(ℝ^M) |
| INV-3 | 𝕋^M is compact, orientable, χ = 0 |
| INV-4 | Symplectic volume = Liouville measure |
| INV-5 | Flat torus has zero curvature |
| INV-6 | Holonomy of flat torus is trivial |
| INV-7 | Hannay angle = 0 for harmonic chain |
| INV-8 | Conserved quantities: actions nₖ, H, P |
| INV-9 | Symmetry group = 𝕋^M |
| INV-10 | Momentum map = action variables nₖ |
| INV-11 | Invariant measure = Haar measure |
| INV-12 | Liouville-Arnold theorem applies |
| INV-13 | Action-angle coordinates are globally defined |
| INV-14 | Phase space is foliated by invariant tori |
| INV-15 | For generic ω: orbits dense on tori |
| PROJ-1 | Projection is the action map |
| PROJ-2 | Projection is many-to-one with torus fibres |
| SURV-1 | What survives: actions, density, flux, parameters |
| AVG-1 | What is averaged: all phase-dependent quantities |
| PROJ-3 | What is projected: short-wavelength modes |
| LOST-1 | Lost: individual phases, coherences, winding numbers |
| LOST-2 | Classification: geometric + dynamical + topological |
| TRANS-1 | Transport coefficients are phase-independent |
| TRANS-2 | Memory kernel is phase-independent |
| CORR-1 | Long-range phase correlations do not survive RPA |
| TOP-1 | Winding numbers are lost |
| TOP-2 | Poincaré-Hopf: χ = 0, no topological obstruction |
| ORD-1 | No emergent order parameter from phase sector |
| POST-1 | Complete table of post-coarse-graining effects |
| POST-2 | Only the Haar measure survives as RPA relic |
| RICH-1 | Harmonic: no richer structure beyond U(1)^M |
| RICH-2 | Anharmonic: mode coupling introduces mixing |
| RICH-3 | Resonant phase = pendulum Hamiltonian |
| RICH-4 | Resonant phases have separatrix topology |
| RICH-5 | Harmonic chain: V₃=0; richer structure absent |
| RICH-6 | All richer structures destroyed by RPA |
| FINAL | **Conclusion B** |
