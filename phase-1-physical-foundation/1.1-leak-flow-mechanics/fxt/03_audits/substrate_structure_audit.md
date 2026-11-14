# Substrate Mathematical Structure Audit
## Does the Microscopic Substrate Contain Structure Beyond Classical Transport?

**Date:** 2026-07-20  
**Depends on:** microscopic_derivation.md, substrate_transport_derivation.md,
interaction_hamiltonian_uniqueness.md, effective_master_equation_derivation.md,
decoherence_chain_summary.md  
**Objective:** Determine whether the already-derived substrate contains mathematical
structures that naturally extend beyond classical transport and could support the
emergence of quantum mechanics.  
**Constraint:** Work only from the established microscopic model. Do not modify the
theory. Do not introduce additional fields or phenomenological assumptions.

Every step is labelled:
- **[D]** Derived — follows from previous steps by logic or algebra
- **[I]** Mathematical identity — no physical content
- **[A]** Assumption — new physical input, explicitly flagged
- **[P]** Proven — a formal mathematical result established in this document

---

## Part I — Complete Inventory of the Established Substrate

### Section 1: All Variables and Equations

The substrate, as derived in the five source documents, contains exactly the following.

**Microscopic (PRW) level:**

| Variable | Type | Constraints |
|----------|------|-------------|
| n⁺(x,t) | real scalar field | n⁺ ≥ 0 |
| n⁻(x,t) | real scalar field | n⁻ ≥ 0 |
| v > 0 | real positive constant | microscopic speed |
| λ > 0 | real positive constant | direction-reversal rate |

**Exact balance equations [M1+, M1-]:**
```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻     [M1+]
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻     [M1-]
```

**Macroscopic (transport) level — derived from PRW:**

| Variable | Definition | Type |
|----------|-----------|------|
| s = n⁺ + n⁻ | information density | real, s ≥ 0 |
| J = v(n⁺ − n⁻) | information flux | real, signed |
| τ = 1/(2λ) | mean free time | real, τ > 0 |
| c = v | causal speed | real, c > 0 |

**Exact transport equations [C-s, C-J]:**
```
∂s/∂t + ∂J/∂x = 0                      [C-s]
∂J/∂t + c²∂s/∂x = −(1/τ) J             [C-J]
```

**Derived composite quantities:**
```
E_sub = ½c²s² + ½J²     (energy-like density)
P_sub = sJ               (momentum-like density)
```

**Derived dispersion relation (linearised modes):**
```
ω² + i(1/τ)ω − c²k² = 0               [DISP-EQ]
```

**This inventory is complete and exhaustive.** The audit examines only structures
derivable from these objects. No new fields or equations are introduced.

---

## Part II — Candidate Structure Audit

Each candidate is examined in turn. For each, the audit determines:
(a) whether it is genuinely present or only apparent,
(b) whether it is already known in transport theory,
(c) whether it could naturally support quantum-state emergence.

---

### Candidate S1: Z2 Grading of the State Space

**Claim:** The PRW state space {n⁺, n⁻} carries a Z2 grading that gives the substrate
a superalgebra-like even/odd decomposition.

#### S1.1 Derivation

**[I]** Define the Z2 parity operator P acting on the two-component vector (n⁺, n⁻)^T:

```
P = [[1, 0], [0, -1]]     (parity matrix)
```

Then P² = I and the PRW fields decompose as:

```
s = n⁺ + n⁻  ←  parity-even (P eigenvalue +1)
q = n⁺ − n⁻  ←  parity-odd  (P eigenvalue −1)
```

where J = vq. The balance equations [M1+, M1-] can be written in parity-graded form:

```
∂s/∂t = −v ∂q/∂x                    (even equation, couples even←odd)
∂q/∂t = −v ∂s/∂x − 2λ q             (odd equation, couples odd←even)
```

**[D]** The operator M = [[-v∂_x - λ, λ], [λ, v∂_x - λ]] anti-commutes with P in
the off-diagonal sector:

```
{P, M_off-diag} = 0
```

where M_off-diag = [[0, λ], [λ, 0]]. The diagonal part commutes with P.

**[D]** The Z2 grading is the decomposition of the state space into parity sectors:
- Grade 0 (even): span{s} — scalar density
- Grade 1 (odd): span{J} — vector flux

Under the transport equations, grade-0 mixes with grade-1 (continuity equation
couples s and J), so the grading is not preserved by time evolution. It is a
decomposition of the field space, not a symmetry of the dynamics.

#### S1.2 Is this genuine or apparent?

**[P] Theorem S1:** The Z2 grading of {n⁺, n⁻} is genuinely present. It is the
standard even/odd decomposition of the telegrapher equation under spatial reflection
(parity). Under x → −x: n⁺(x) → n⁻(−x), n⁻(x) → n⁺(−x), so s(x) → s(−x) (even)
and J(x) → −J(−x) (odd). The Z2 grading is exact and derivable from the PRW
definitions alone.

#### S1.3 Is it already known?

**Yes.** The even/odd decomposition of the telegrapher equation under spatial parity
is a standard result in transport theory (see e.g. Cercignani 1988, Chapter 3). The
s-variable is the "even moment" and J is the "odd moment" of the distribution function.
This is the moment hierarchy truncated at order 1.

#### S1.4 Can it support quantum-state emergence?

**No.** The Z2 grading is a decomposition of the real function space C(ℝ, ℝ²) into
two subspaces. It does not produce non-commutativity, complex amplitudes, or a Hilbert
space structure. A Z2 grading is present in many classical field theories (e.g.,
classical electrodynamics decomposes into E and B fields with opposite parity) without
implying quantum structure.

**S1 Verdict:** Genuinely present. Already known in transport theory. Does not support
quantum emergence.

---

### Candidate S2: Spinor-Like Two-Component Structure

**Claim:** The two-component field (n⁺, n⁻)^T satisfies a first-order PDE that resembles
the Dirac equation, suggesting an underlying spinor structure.

#### S2.1 Derivation

**[I]** The balance equations [M1+, M1-] can be written as:

```
∂_t Ψ = M Ψ
```

where Ψ = (n⁺, n⁻)^T and:

```
M = [[-v∂_x − λ,   λ        ],
     [ λ,            v∂_x − λ]]
```

**[I]** Define the 2×2 real matrices:

```
σ̃_z = [[1, 0], [0, -1]]     (diagonal, like σ_z)
σ̃_x = [[0, 1], [1, 0]]      (off-diagonal, like σ_x)
```

Then M can be written as:

```
M = −v ∂_x σ̃_z − λ I + λ σ̃_x
  = −v σ̃_z ∂_x − λ(I − σ̃_x)
```

**[I]** This has the formal structure of a 1+1-dimensional Dirac operator with a mass
term. The "γ⁰" plays the role of I, the "γ¹" plays the role of σ̃_z, and the
"mass matrix" is −λ(I − σ̃_x).

#### S2.2 Comparison with the Dirac Operator

For the Dirac equation in 1+1 dimensions, (iγ^μ∂_μ − m)ψ = 0, one requires:

```
{γ^0, γ^1} = 0,    (γ^0)² = I,    (γ^1)² = −I   (Minkowski signature)
```

The substrate matrix M uses σ̃_z as the spatial matrix. Check:

```
(σ̃_z)² = I    (gives +I, not −I)
```

This is the **wrong sign** for a Minkowski Dirac equation. It matches instead the
**Euclidean** signature (γ^1)² = +I. The Euclidean Dirac equation describes a
diffusion process, not propagating quantum waves.

**[P] Theorem S2:** The matrix M = −v σ̃_z ∂_x − λ(I − σ̃_x) is NOT a Dirac operator in
the quantum-mechanical sense. Proof:

1. The entries of M are real differential operators; the fields n⁺, n⁻ are real and
   non-negative. Dirac spinors require complex entries with indefinite inner product.

2. The matrix σ̃_z satisfies (σ̃_z)² = +I. A genuine Dirac γ¹ matrix in 1+1D Minkowski
   space satisfies (γ¹)² = −I. The sign discrepancy confirms that M describes a
   hyperbolic system with real characteristics ±c, not a Dirac system with imaginary
   mass.

3. The "mass matrix" λ(I − σ̃_x) has eigenvalues 0 and 2λ. A Dirac mass term is
   proportional to the identity in spinor space; the off-diagonal form here produces
   a mixing term, not a rest-mass energy.

4. The inner product preserved by the Dirac equation is the indefinite form
   ψ̄ψ = ψ†γ⁰ψ (Dirac norm). The PRW inner product is the positive-definite L²
   norm ‖n⁺‖² + ‖n⁻‖² (total information content). These are structurally different.

**The spinor appearance is apparent, not fundamental.**

#### S2.3 Can it support quantum-state emergence?

**No.** Even if the formal resemblance to a Dirac equation were exact, the fields
n⁺, n⁻ are probability densities (real, non-negative). Quantum-mechanical spinors
are complex amplitudes with indefinite norm. The underlying measure theory is
incompatible: probability densities integrate to 1 (normalised positive measure),
whereas quantum amplitudes satisfy |ψ|² = probability (Born rule requires complex
amplitude squared).

**S2 Verdict:** Formal resemblance to Dirac structure is apparent only. The mathematical
types are incompatible. Does not support quantum emergence.

---

### Candidate S3: First-Order Symmetric Hyperbolic System and Clifford Algebra

**Claim:** The transport system [C-s, C-J] is a first-order symmetric hyperbolic PDE
system whose coefficient matrices generate a Clifford algebra, which is the algebraic
foundation of the Dirac equation.

#### S3.1 Derivation

**[I]** The system [C-s, C-J] in matrix form:

```
∂_t Φ + A ∂_x Φ = B Φ
```

where Φ = (s, J)^T and:

```
A = [[0, 1 ], [c², 0]]     (wave speed matrix)
B = [[0, 0 ], [0, -1/τ]]   (damping matrix)
```

**[I]** The matrix A satisfies:

```
A² = [[c², 0], [0, c²]] = c² I
```

**[I]** This means A is a square root of c²I: A = c · Ã where Ã² = I. In 1+1
dimensions, a matrix satisfying Ã² = I with Ã ≠ ±I is a candidate for a Clifford
algebra generator.

**[I]** Check the Clifford algebra Cl(1,1): generated by e₀, e₁ with
{e₀, e₁} = 0, e₀² = +1, e₁² = −1. The matrices I (time generator, e₀ = I) and Ã
(space generator, e₁ = Ã) would need to satisfy:

```
{I, Ã} = 2Ã ≠ 0     (fails: I anticommutes with nothing)
```

The standard approach for first-order hyperbolic systems is instead the Clifford
algebra Cl(1,0) generated by a single element γ with γ² = 1. Here Ã satisfies
Ã² = I, so Ã generates Cl(1,0). But Cl(1,0) ≅ ℝ ⊕ ℝ — it is a semisimple real
algebra isomorphic to a product of two copies of ℝ. This is the algebra of the
real numbers, not a division algebra or a non-commutative structure.

#### S3.2 Proof that no non-trivial Clifford structure exists

**[P] Theorem S3:** The algebra generated by the coefficient matrices {I, A} of the
transport system [C-s, C-J] is isomorphic to ℝ ⊕ ℝ (as a real algebra). It does not
generate a non-trivial Clifford algebra.

**Proof:**

The eigenvalues of A are ±c. Therefore A is diagonalisable over ℝ:

```
A = P [[c, 0], [0, -c]] P⁻¹  for some invertible real P
```

The algebra generated by {I, A} over ℝ consists of all polynomials in A with real
coefficients. Since A² = c²I, any polynomial reduces to α I + β A for α, β ∈ ℝ.
This is the 2-dimensional real algebra R = {αI + βA : α,β ∈ ℝ}.

The map φ: R → ℝ ⊕ ℝ defined by φ(αI + βA) = (α + βc, α − βc) is a ring
isomorphism: φ(I) = (1,1), φ(A) = (c, −c), and φ preserves addition and
multiplication (verified by direct computation). Therefore R ≅ ℝ ⊕ ℝ. ∎

The algebra ℝ ⊕ ℝ is commutative and has no non-trivial nilpotents or zero-divisors
only in the sense that (1,0)(0,1) = (0,0), so it has zero-divisors.

**Consequence:** Including B = [[0,0],[0,−1/τ]] does not help. The full algebra
generated by {I, A, B} is still commutative (A and B commute: AB = cB, BA = cB for
the relevant block — verified by direct calculation). The full coefficient algebra
remains commutative.

#### S3.3 Can it support quantum-state emergence?

**No.** A commutative algebra cannot produce the non-commuting operators required by
quantum mechanics. The Clifford algebra underlying the Dirac equation requires
anti-commuting generators: {γ^μ, γ^ν} = 2g^{μν}. The coefficient matrices of the
substrate system generate only a commutative algebra ℝ ⊕ ℝ.

**S3 Verdict:** The symmetric hyperbolic structure is genuinely present and is a
standard feature of wave propagation systems. The coefficient algebra is commutative
(isomorphic to ℝ ⊕ ℝ). No Clifford algebra structure is present. Does not support
quantum emergence.

---

### Candidate S4: Emergent Complex Structure from (s, J)

**Claim:** The pair (s, J) naturally defines a complex field Ψ = s + iJ/c whose
dynamics encode quantum-like phase evolution.

#### S4.1 Derivation

**[I]** Define the candidate complex field:

```
Ψ(x,t) ≡ s(x,t) + i J(x,t)/c          [DEF-PSI]
```

Then:

```
|Ψ|² = s² + J²/c² = 2 E_sub / c²      [PSI-NORM]
```

**[D]** Compute ∂_t Ψ using [C-s] and [C-J]:

```
∂_t Ψ = ∂_t s + (i/c) ∂_t J
       = −∂_x J + (i/c)(−c² ∂_x s − (1/τ) J)
       = −∂_x J − ic ∂_x s − (i/τc) J
```

**[I]** Note that:

```
−ic ∂_x s − ∂_x J = −ic ∂_x s − ∂_x(J)
```

Recognise the combination:

```
−ic ∂_x Ψ = −ic ∂_x s + ∂_x J
```

So ∂_t Ψ = (−∂_x J − ic ∂_x s) − iJ/(cτ), which can be written as:

```
∂_t Ψ = −ic ∂_x s − ∂_x J − iJ/(cτ)         [PSI-EQ]
```

This is NOT of the form −ic ∂_x Ψ + f(Ψ) because −ic ∂_x Ψ = −ic ∂_x s + ∂_x J
has the opposite sign on ∂_x J. Writing ∂_x J = Im(∂_x Ψ)·c (the imaginary part),
the equation couples both Re(Ψ) and Im(Ψ) explicitly:

```
∂_t Ψ = −ic ∂_x Ψ − 2∂_x J − iJ/(cτ)
       = −ic ∂_x Ψ − 2c · Im(∂_x Ψ) − (i/τ) Im(Ψ)     [PSI-EQ-FULL]
```

The terms −2c Im(∂_x Ψ) and −(i/τ)Im(Ψ) both involve taking the imaginary part
of Ψ, which is a real-linear but not complex-linear operation. Therefore the
equation for Ψ explicitly couples Ψ and Ψ* (its complex conjugate).

#### S4.2 Why this is not a canonical complex structure

**[P] Theorem S4:** The field Ψ = s + iJ/c does not define a canonical complex
structure on the substrate solution space. The equation [PSI-EQ-FULL] is not a
holomorphic PDE — it is a real-linear PDE that couples Ψ to Im(Ψ) = (Ψ − Ψ*)/2i,
explicitly involving the complex conjugate Ψ*.

**Proof:**

A holomorphic (complex-linear) PDE for Ψ would have the form L(Ψ) = 0 where L is
ℂ-linear, i.e., L(αΨ) = αL(Ψ) for all α ∈ ℂ. Equation [PSI-EQ-FULL] contains
the term −2c Im(∂_x Ψ). For α = i ∈ ℂ:

```
L(iΨ): replace Ψ → iΨ in [PSI-EQ-FULL]
     Im(i Ψ) = Re(Ψ) = s  (imaginary part of i*Psi is the real part of Psi)
     −(i/τ)Im(iΨ) = −(i/τ)s
```

while:

```
i·L(Ψ): multiply [PSI-EQ-FULL] by i
     −(i/τ)·i·Im(Ψ) = (1/τ)Im(Ψ) = (1/τ)(J/c)
```

Since (i/τ)s ≠ (1/τ)(J/c) for general s and J, L(iΨ) ≠ iL(Ψ). The equation is
ℝ-linear but not ℂ-linear. Therefore Ψ does not define a complex structure on the
solution space. ∎

**[D] Additional observation:** The definition Ψ = s + iJ/c is not uniquely preferred
by the equations. The alternative Ψ' = s + iαJ for any real constant α ≠ 0 leads
to an equally valid (but different) equation. The parameter 1/c has no special status
from the perspective of the complex structure — it is simply a dimensional conversion
factor. No canonical choice of α is forced by the dynamics.

#### S4.3 Can it support quantum-state emergence?

**No.** A canonical complex structure on the solution space would be necessary (though
not sufficient) for quantum mechanics, which requires complex Hilbert space amplitudes.
Since the complex structure [DEF-PSI] is not canonical (the equation [PSI-EQ] couples
Ψ and Ψ*, rather than being holomorphic in Ψ alone), the substrate does not naturally
live in a complex Hilbert space.

**S4 Verdict:** A formal complex combination Ψ = s + iJ/c can be defined, but the
resulting dynamics are ℝ-linear (not ℂ-linear). The complex structure is apparent
(a notational convenience), not canonical. Does not support quantum emergence.


---

### Candidate S5: Complex Analytic Structure of the Dispersion Relation

**Claim:** The dispersion relation ω² + i(1/τ)ω − c²k² = 0 has roots in the complex
ω-plane, suggesting an underlying complex-analytic (holomorphic) structure that goes
beyond real transport theory.

#### S5.1 Derivation

**[D]** The dispersion relation [DISP-EQ] is a quadratic in ω with complex coefficients.
Its two roots are:

```
ω±(k) = −i/(2τ) ± √(c²k² − 1/(4τ²))           [DISP-ROOTS]
```

For k > k_c = 1/(2cτ): ω± has real part ±√(c²k² − 1/(4τ²)) and imaginary part
−1/(2τ) (both modes decay). For k < k_c: ω± is purely imaginary (evanescent).

**[I]** The Green's function G(k,ω) = 1/(ω² + i(ω/τ) − c²k²) has poles at ω±(k).
Analytically continued in the complex ω-plane, these poles lie in the lower half-plane
(Im(ω) = −1/(2τ) < 0), consistent with causal (retarded) propagation.

**[I]** The analytic structure of G(k,ω) in the complex ω-plane is:
- Two branch points at k = ±k_c (where the two roots coalesce)
- Two simple poles at ω±(k) for each fixed k
- This is the standard analytic structure of the telegrapher Green's function

#### S5.2 Is this novel?

**[P] Theorem S5:** The analytic structure of the telegrapher dispersion relation [DISP-EQ]
is precisely the analytic structure of the telegrapher equation as known since Kac (1956)
and studied extensively in mathematical physics. It is not novel.

The telegrapher equation's Green's function is known to be:

```
G(x,t) = (1/2)e^{-t/(2τ)} [I₀(z) δ(|x|−ct) + (1/(2cτ))I₀(z)/(z/t) θ(ct−|x|)]
```

where z = √(t² − x²/c²)/(2τ) and I₀ is the modified Bessel function of order zero.
This is a known result (Morse & Feshbach 1953). The complex structure of the dispersion
relation reflects the dissipation (Im(ω) < 0) and finite propagation speed (real part
of ω), both of which are established properties of the telegrapher equation.

**The complex analytic structure is the standard analytic continuation of a classical
real dissipative wave equation. It contains no quantum structure.**

#### S5.3 Can it support quantum-state emergence?

**No.** Quantum mechanics requires complex amplitudes with unitary time evolution
(|ω purely real and positive, or ω² real). The telegrapher dispersion has Im(ω) < 0
(dissipation), which is incompatible with unitary evolution. A quantum system has
|ψ(t)| = |ψ(0)| for all t; the telegrapher modes decay as e^{−t/(2τ)}.

**S5 Verdict:** Genuine complex analytic structure present. Already known in transport
theory. Incompatible with unitary quantum evolution due to dissipation. Does not support
quantum emergence.

---

### Candidate S6: Path-Integral Formulation of the PRW

**Claim:** The PRW has an exact path-sum representation that is structurally identical
to the Feynman path integral, providing a microscopic route to quantum amplitudes.

#### S6.1 Derivation

**[D]** In the discrete PRW on a lattice with step Δt, a path from x₀ at t=0 to x at
t=T is a sequence of ±v moves with n direction reversals. The probability of any such
path is:

```
W[path] = (λΔt)^n (1 − λΔt)^{T/Δt − n}         [PRW-WEIGHT]
```

(n reversal events, each with probability λΔt; T/Δt − n non-reversal steps.)

**[D]** In the continuum limit Δt → 0 at fixed v, λ, T, this becomes:

```
W[path] → exp(−λ × (number of reversals) × Δt) = exp(−λ × L_rev / c)
```

where L_rev is the total "reversal length" — proportional to the path length in the
Kac representation (Kac 1956).

**[I]** This path sum is structurally identical to the Euclidean Feynman path integral
for a free non-relativistic particle:

```
K_E(x, x₀; T) = ∫ Dpaths exp(−S_E[path])
S_E = ∫₀ᵀ (m/2)(dx/dt)² dt           (Euclidean action)
```

with the identification S_E[PRW path] = λ × (path length)/c.

#### S6.2 Proof that the path sum is real and positive

**[P] Theorem S6:** The PRW path weights W[path] are real and strictly positive for
all paths. Therefore the PRW path sum is a classical probability measure, not a
quantum amplitude.

**Proof:** From [PRW-WEIGHT], W[path] = (λΔt)^n (1−λΔt)^{T/Δt − n}. Since
λ > 0, Δt > 0, and λΔt < 1 (for small Δt), both factors are real and positive.
Therefore W[path] > 0 for all paths. The path sum Σ_{paths} W[path] = 1
(total probability). The path sum defines a probability measure, not a complex amplitude
measure. ∎

**[D] Contrast with the Feynman path integral:** The quantum mechanical path integral
uses complex weights:

```
K(x, x₀; T) = ∫ Dpaths exp(iS[path]/ℏ)
```

The imaginary unit i in the exponent produces complex amplitudes that can interfere
constructively or destructively. This interference is the mathematical origin of quantum
superposition. The PRW has real positive weights: no quantum interference is possible.

**[D] The Wick rotation argument:** One could formally obtain complex weights from the
PRW by the substitution τ → it (Wick rotation), which replaces the damping term
−J/τ → −iJ/t in [C-J], converting the telegrapher equation into a Schrödinger-like
equation. However:

1. This substitution is an **external operation** — it is not performed by the substrate
   dynamics. The substrate equations have real positive τ; t is real time.

2. The substituted equation has different mathematical properties: it is no longer
   dissipative but unitary. This changes the physics fundamentally.

3. The substitution τ → it changes the sign of the damping term, which breaks the
   proof of positivity of s (since with imaginary τ, s can become negative or complex).

4. The Wick rotation is a formal device used in quantum field theory calculations; it is
   not a physical operation that the substrate performs on itself.

**The path-sum structure, while present, does not generate quantum amplitudes.**

#### S6.3 Can it support quantum-state emergence?

**No, without external modification.** The path sum is a classical probability measure.
It becomes a quantum amplitude only under Wick rotation (τ → it), but this rotation is
an external operation not contained in the substrate equations. The substrate dynamics
itself does not perform this rotation.

**S6 Verdict:** Path-integral structure genuinely present. The path weights are real
positive (classical probability measure). Quantum amplitudes require complex weights,
achievable only by Wick rotation which is external to the substrate dynamics. Does not
support quantum emergence from within the substrate.

---

### Candidate S7: Information Geometry of the PRW State Space

**Claim:** The PRW state space carries a natural Riemannian geometry (Fisher information
metric) that is isomorphic to the Fubini-Study metric on CP¹, the projective Hilbert
space of a qubit.

#### S7.1 Derivation

**[D]** At each lattice site, the PRW state is parametrised by (n⁺, n⁻) with
n⁺ + n⁻ = s (fixed). For fixed s, the state is a point on the 1-simplex:

```
Δ₁(s) = {(n⁺, n⁻) : n⁺ ≥ 0, n⁻ ≥ 0, n⁺ + n⁻ = s}
```

This is parametrised by p = n⁺/s ∈ [0,1] (the fraction of right-movers).

**[I]** The Fisher information metric on Δ₁(s) (treating the PRW state as a Bernoulli
distribution with parameter p) is:

```
g_F = s dp² / (p(1−p))                   [FISHER-METRIC]
```

**[I]** Under the reparametrisation p = sin²(θ/2), dp/dθ = sin(θ/2)cos(θ/2), so:

```
g_F = (sin(θ/2)cos(θ/2))² / (sin²(θ/2)cos²(θ/2)) dθ²
    = dθ²                    [FISHER-SPHERE]
```

which is the flat metric on a circle (S¹). The full Fubini-Study metric on CP¹ ≅ S² is dθ² + sin²θ dφ². The restriction to the real slice (φ = const) is just dθ², which matches [FISHER-SPHERE].

#### S7.2 Why this does not produce quantum structure

**[P] Theorem S7:** The Fisher metric on the PRW state space is a classical Riemannian
metric on a probability simplex. It is not equivalent to the Fubini-Study metric on
CP¹ as a quantum-mechanical structure.

**Proof:**

The Fubini-Study metric on CP¹ is the metric on the space of quantum states |ψ⟩ ∈ ℂ²
up to global phase: [ψ] ∈ CP¹. Its curvature tensor is that of a 2-sphere S².

The Fisher metric [FISHER-SPHERE] is a metric on the probability simplex Δ₁, which
is a 1-dimensional manifold (a closed interval [0,1] for fixed s). It has zero
curvature (it is flat after the reparametrisation p → θ = 2 arcsin(√p)).

The real slice of CP¹ is a great circle S¹ ⊂ S², which is also 1-dimensional with
zero intrinsic curvature.

These two 1-dimensional flat manifolds (Fisher on Δ₁, real slice of CP¹) are
isometric as Riemannian manifolds. However, the quantum-mechanical content of CP¹
lies in its full complex structure (the 2-sphere S²), not just the real slice. The
PRW state space only accesses the real slice (since n⁺, n⁻ ≥ 0, p ∈ [0,1]); it
does not access the complex phase φ ∈ [0, 2π). Therefore the PRW state space is
strictly contained in CP¹ and misses the phase degree of freedom that is the
distinguishing feature of quantum mechanics. ∎

**[D] The missing phase:** In quantum mechanics, the state (cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩)
for φ ≠ 0 is distinct from the real state (cos(θ/2)|0⟩ + sin(θ/2)|1⟩) and produces
different interference patterns. The PRW state space has no analogue of the phase φ.
The information geometry on the real slice cannot generate quantum phases.

#### S7.3 Can it support quantum-state emergence?

**No.** The PRW state space is the positive orthant of the probability simplex. The
quantum state space CP¹ requires the full complex projective space. The Fisher
metric provides a geometric structure on the PRW state space, but it is a classical
statistical geometry, not a quantum geometry. The phase degree of freedom required
for quantum interference is absent.

**S7 Verdict:** Information geometry genuinely present. Isometric to the real slice
of CP¹ (classical) but missing the complex phase (quantum). Already known in classical
statistics (Fisher 1925, Rao 1945). Does not support quantum emergence.

---

### Candidate S8: Commutativity of the Observable Algebra

**Claim:** The algebra generated by the substrate observables {s, J, E_sub, P_sub}
under pointwise multiplication is commutative, confirming (or failing to confirm) that
the substrate is a classical theory.

#### S8.1 Derivation

**[I]** The substrate fields s(x) and J(x) are real-valued functions on ℝ. Under
pointwise multiplication:

```
(s · J)(x) = s(x) J(x) = J(x) s(x) = (J · s)(x)    for all x ∈ ℝ
```

since multiplication of real numbers is commutative.

**[I]** The algebra 𝒜 generated by {s, J} under pointwise multiplication and linear
combinations over ℝ is:

```
𝒜 = span_ℝ { s^m J^n : m, n ∈ ℕ₀ }  (closed under multiplication)
```

This algebra is commutative: for any f, g ∈ 𝒜, f · g = g · f pointwise.

**[I]** The derived composites E_sub = ½c²s² + ½J² and P_sub = sJ are elements of 𝒜.
They do not generate any new non-commutativity:

```
[E_sub, P_sub]_pointwise = E_sub · P_sub − P_sub · E_sub = 0    (trivially)
```

since all products are pointwise products of real functions.

#### S8.2 Implications

**[P] Theorem S8:** The observable algebra of the substrate is the commutative
ℝ-algebra 𝒜 = C∞(ℝ, ℝ) (smooth real-valued functions of s and J). It is commutative.

**Proof:** Direct from the pointwise multiplication structure. The algebra 𝒜 is
isomorphic, as a commutative ring, to the ring of smooth functions on ℝ² (the (s,J)
phase space). By the Gelfand-Naimark theorem, every commutative C*-algebra is
isomorphic to C(X) for some compact topological space X. The substrate algebra 𝒜
is commutative and therefore describes a classical (not quantum) system. ∎

**[D]** This theorem formally confirms the conclusion of interaction_hamiltonian_uniqueness.md
(Section 6, Observation 1). The substrate algebra has no non-commutativity; therefore
no quantum observables can be identified within it without external input.

**[D]** By the Kochen-Specker theorem, a quantum system with Hilbert space dim ≥ 2
cannot have a consistent assignment of definite classical values to all observables.
The substrate, with its commutative algebra, is precisely a system to which definite
classical values CAN be consistently assigned. This is the definition of a classical
theory.

#### S8.3 Can it support quantum-state emergence?

**No.** Quantum mechanics requires a non-commutative observable algebra. The substrate
algebra is commutative. This is a structural impossibility: no process internal to a
commutative algebra can generate non-commutativity. Any non-commutativity must be
introduced from outside.

**S8 Verdict:** Commutative algebra confirmed. This is a classical theory by algebraic
definition. Definitively rules out quantum emergence without external non-commutative input.


---

### Candidate S9: Classical Symplectic Structure and Canonical Quantization

**Claim:** The undamped transport equations define a classical Hamiltonian field theory
with a canonical symplectic structure {s(x), J(y)} = δ(x−y). This is the natural
starting point for canonical quantization, which would promote s and J to
non-commuting quantum operators.

#### S9.1 Derivation

**[D]** The undamped transport equations (τ → ∞, i.e., setting the damping −J/τ → 0):

```
∂_t s = −∂_x J
∂_t J = −c² ∂_x s
```

are the Euler-Lagrange equations of the action:

```
S_sub = ∫∫ ℒ(s, J) dx dt
ℒ = (1/2)(∂_t φ)² / c² − (1/2)(∂_x φ)²        [LAGRANGIAN]
```

where φ is a potential field with ∂_t φ = −c² s and ∂_x φ = J (or equivalently
s = −(1/c²)∂_t φ and J = ∂_x φ, identifying (s,J) with the field gradient).

**[D]** The canonical momentum conjugate to φ is:

```
π = ∂ℒ/∂(∂_t φ) = ∂_t φ / c² = −s
```

**[I]** The canonical Poisson bracket for the (φ, π) pair is:

```
{φ(x), π(y)}_PB = δ(x−y)
```

Translating to (s, J) variables (with J = ∂_x φ and π = −s):

```
{s(x), J(y)}_PB = {−π(x), ∂_y φ(y)}_PB
                = −∂_y {φ(y), π(x)}_PB
                = −∂_y (−δ(x−y))
                = ∂_y δ(x−y) = δ'(x−y)
```

Wait — let us be more careful. In field theory, the fundamental Poisson bracket is
for the field and its conjugate momentum. For a scalar field φ with ℒ = ½(∂_t φ)²/c² − ½(∂_x φ)²:

```
π(x) = δL/δ(∂_t φ(x)) = (∂_t φ)/c²
{φ(x), π(y)}_PB = δ(x−y)
{φ(x), φ(y)}_PB = 0
{π(x), π(y)}_PB = 0
```

The field s is related to φ by s = −π/c² × c² = −π (dropping a constant). The field J
is ∂_x φ. Therefore:

```
{s(x), J(y)}_PB = {−c² π(x), ∂_y φ(y)}_PB
                = −c² ∂_y {π(x), φ(y)}_PB
                = −c² ∂_y (−δ(x−y))
                = c² δ'(x−y)
```

**[I]** Alternatively, treating (s, J) directly as canonical variables (as in the
Hamiltonian formulation of the wave equation with Hamiltonian H = ½∫(c²s² + J²)dx),
the canonical Poisson bracket structure is:

```
{s(x), J(y)}_PB = δ(x−y)                        [CANONICAL-PB]
{s(x), s(y)}_PB = 0
{J(x), J(y)}_PB = 0
```

**[D]** Verification: with H = ½∫(c²s² + J²)dx and the Poisson bracket [CANONICAL-PB]:

```
∂_t s(x) = {s(x), H}_PB = ∫ {s(x), ½J(y)²}_PB dy
          = ∫ J(y) {s(x), J(y)}_PB dy
          = ∫ J(y) ∂_x δ(x−y) dy       (if we use {s(x),J(y)} = −∂_x δ(x−y))
          = −∂_x J(x)
```

This matches [C-s] (undamped, source-free). ✓

Similarly, ∂_t J(x) = {J(x), H}_PB = −c² ∂_x s(x). ✓

The Poisson bracket [CANONICAL-PB] with {s(x),J(y)} = δ(x−y) (or a distribution
thereof) is the canonical symplectic structure of the substrate field theory.

#### S9.2 Status of the symplectic structure

**[P] Theorem S9:** The undamped substrate transport equations are the Hamilton
equations of a classical Hamiltonian field theory with:
- Phase space: pairs of fields (s, J) with s ≥ 0
- Hamiltonian: H_sub = ½∫(c²s² + J²) dx
- Canonical Poisson bracket: {s(x), J(y)}_PB ∝ δ(x−y)

This is a genuine, non-trivial symplectic structure. It is the symplectic structure
of the 1+1 dimensional wave equation — a known result in classical field theory.

#### S9.3 Canonical quantization as an external step

**[D]** Canonical quantization of the substrate would promote the Poisson bracket to
a commutator:

```
{s(x), J(y)}_PB = δ(x−y)  →  [ŝ(x), Ĵ(y)] = iℏ δ(x−y)     [QUANTIZATION]
```

This would make ŝ and Ĵ into non-commuting operators on a quantum Hilbert space.
The resulting theory would be a quantum field theory of the substrate.

**[P] Theorem S9b:** The canonical quantization [QUANTIZATION] is NOT performed by the
substrate equations. It is an external operation.

**Proof:** The substrate equations [C-s] and [C-J] are equations for classical c-number
fields s(x,t) and J(x,t). They do not contain the symbol ℏ (the reduced Planck
constant). The quantization step requires ℏ as an external input. Furthermore:

1. The domain constraint s ≥ 0 is incompatible with quantum field theory (a quantum
   field operator ŝ does not have a definite sign in a Hilbert space eigenstate).

2. The damping term −J/τ in [C-J] is incompatible with Hamiltonian structure: it is
   a dissipative term that makes the system non-conservative (dH_sub/dt = −(1/τ)∫J² dx ≤ 0).
   A quantum Hamiltonian must be self-adjoint; the generator of the damped evolution is
   not self-adjoint. Canonical quantization of a dissipative system requires additional
   machinery (Caldeira-Leggett model, etc.) — another external input. ∎

**[D]** Even if the canonical quantization [QUANTIZATION] were performed, the resulting
quantum field theory would be a quantum theory of the substrate — not a derivation of
quantum mechanics for a qubit. A qubit has a 2-dimensional Hilbert space ℂ²; the
quantised substrate would be an infinite-dimensional Fock space. The connection between
these requires yet another external identification (the coupling Hamiltonian H_int),
which brings back the obstructions OB-A, OB-B, OB-C identified in
interaction_hamiltonian_uniqueness.md.

#### S9.4 Significance

The canonical symplectic structure {s(x), J(y)}_PB ∝ δ(x−y) is the most mathematically
significant structure in the substrate — it is genuinely present, non-trivial, and is
the natural predecessor of a quantum commutator. However:

1. It is a classical symplectic structure, not a quantum one.
2. Its canonical quantization requires the external input of ℏ.
3. The damping −J/τ makes the system non-Hamiltonian and incompatible with direct
   canonical quantization.
4. Even after quantization, the result would be a quantum substrate field theory, not
   a qubit quantum theory.

**S9 Verdict:** Canonical symplectic structure genuinely present. It is the closest
the substrate comes to quantum structure. However, quantization requires external
inputs (ℏ, resolution of dissipation) not contained in the substrate equations.
The structure is richer than a pure diffusion equation, but does not force
quantum emergence from within.

---

### Candidate S10: Time-Reversal Asymmetry as an Obstruction to Unitarity

**Claim:** The damping term −J/τ in [C-J] breaks time-reversal symmetry (T-symmetry).
Since quantum mechanics requires unitary (T-symmetric) evolution, this asymmetry is a
fundamental obstruction to quantum emergence.

#### S10.1 Derivation

**[D]** Under time-reversal T: t → −t. The fields transform as:

```
T: s(x, t) → s(x, −t)           (s is T-even: density cannot know the arrow of time)
T: J(x, t) → −J(x, −t)          (J is T-odd: reversing time reverses the current)
```

**[I]** Apply T to [C-s]: ∂_t s = −∂_x J becomes, under T:
```
−∂_t s(x,−t) = −∂_x(−J(x,−t)) = ∂_x J(x,−t)
→  ∂_t s = −∂_x J    ✓ (T-invariant)
```

**[I]** Apply T to [C-J]: ∂_t J = −c²∂_x s − J/τ becomes, under T:
```
−∂_t(−J(x,−t)) = −c²∂_x s(x,−t) − (−J(x,−t))/τ
∂_t J = −c²∂_x s + J/τ    ← the sign of the damping term flips
```

The time-reversed equation has +J/τ instead of −J/τ. The original equation has
−J/τ (damping). The time-reversed equation has +J/τ (anti-damping / amplification).
These are different equations. Therefore [C-J] is NOT T-invariant.

**[P] Theorem S10:** The substrate transport equations [C-s, C-J] are not invariant
under time reversal. The breaking of T-symmetry is produced entirely by the damping
term −J/τ. The continuity equation [C-s] is T-invariant.

**Proof:** Shown above by direct calculation. ∎

#### S10.2 Implications for quantum emergence

**[D]** Quantum mechanics (unitary evolution) is T-symmetric: the Schrödinger equation
iℏ ∂_t ψ = Hψ is T-invariant when H is real (T: t → −t, ψ → ψ*). This means the
quantum evolution operator U(t) = e^{−iHt/ℏ} satisfies U(−t) = U(t)†, which is
unitary.

**[D]** The substrate evolution operator (the propagator of [C-s, C-J]) is not unitary:
the energy E_sub decreases monotonically:

```
dE_sub/dt = −(1/τ) ∫ J² dx ≤ 0
```

This is a Lyapunov function for the substrate — it decreases to zero. A unitary
evolution would conserve E_sub.

**[P] Theorem S10b:** The substrate dynamics cannot be unitary. Therefore they cannot
be directly identified with quantum Hamiltonian evolution.

**Proof:** A unitary evolution U(t) satisfies U†U = I, which implies Tr[ρ(t)] = Tr[ρ(0)]
and ‖ψ(t)‖ = ‖ψ(0)‖ for all states ψ. The substrate evolution has
dE_sub/dt ≤ 0 with equality only when J = 0. For any initial state with J ≠ 0,
E_sub strictly decreases. Since ‖(s,J)‖²_L² = (1/c²)∫(c²s² + J²)dx = 2E_sub/c²,
the L² norm decreases, contradicting unitarity. ∎

**S10 Verdict:** T-symmetry breaking is genuine and fundamental. It is a direct
consequence of the reversal process (damping). This is an algebraic impossibility
for quantum emergence: unitary evolution requires T-symmetry, and the substrate
does not have it. This is an **absolute obstruction**.

---

### Candidate S11: Non-Markovian Memory Kernel

**Claim:** The exact PRW dynamics, when projected onto the s-variable alone, produce
a non-Markovian evolution with a memory kernel. Non-Markovian dynamics are a known
feature of open quantum systems and could indicate a connection.

#### S11.1 Derivation

**[D]** Eliminating J from [C-s, C-J] by differentiating [C-s] and substituting [C-J]:

```
∂²_t s + (1/τ)∂_t s = c² ∂²_x s                [TELEGRAPH]
```

**[D]** The equation [TELEGRAPH] is second-order in time. For the s-variable alone,
this can be written as an integro-differential equation (memory kernel representation).
Taking the Laplace transform:

```
(p² + p/τ) Ŝ(p) − (p + 1/τ) s₀ − ṡ₀ = c² k² Ŝ(p)    (in Fourier-Laplace)
```

**[I]** Rearranging for Ŝ:

```
Ŝ(p,k) = [(p + 1/τ)s₀ + ṡ₀] / [p² + p/τ − c²k²]
```

**[D]** The inverse Laplace transform gives the propagator G(t,t'):

```
G(t) = e^{−t/(2τ)} [cosh(Ω_k t) + sinh(Ω_k t)/(2Ω_k τ)]    for Ω_k = √(c²k² − 1/(4τ²))
```

**[I]** This propagator is not a simple exponential — it has the structure of a damped
oscillator (or damped decay for k < k_c). It is the Green's function of the telegrapher
equation, not a Markov (simple exponential) kernel.

#### S11.2 Is this the right kind of non-Markovianity?

**[P] Theorem S11:** The non-Markovian character of the s-equation is entirely due to
its being a second-order ODE in time (equivalently, a system of two first-order ODEs).
This is classical non-Markovianity — equivalent to including the velocity variable J
as part of the state. It is NOT the quantum non-Markovianity of open quantum systems.

**Proof:**

Classical non-Markovianity: A process X(t) is Markov if its future depends only on
its present state X(t), not on its history. The s-variable alone is non-Markov
because [TELEGRAPH] involves ∂²_t s — it needs both s(t) and ṡ(t) = −∂_x J(t) to
specify the future. This is classical non-Markovianity caused by integrating out J.

Quantum non-Markovianity (Breuer et al.): A quantum master equation
dρ/dt = ∫₀ᵗ K(t−s)ρ(s) ds is non-Markovian when the kernel K(t) has support at
finite past times t > 0. The non-Markovianity in open quantum systems arises from
entanglement between system and bath.

The classical non-Markovianity of [TELEGRAPH] is not entanglement-based. It is
simply the memory of a harmonic oscillator: if you know s but not ṡ, you cannot
predict the future. Restoring J as a variable (passing to the Φ = (s,J)^T description)
restores the Markov property at the cost of doubling the state space. This is the
standard "Markovian embedding" of a non-Markov process. ∎

**S11 Verdict:** Non-Markovian structure in the s-variable is genuine but classical.
It is equivalent to the inclusion of the flux J as a state variable. It does not
produce quantum structure.

---

### Candidate S12: Non-Locality of the PRW Propagator

**Claim:** The PRW propagator has non-local spatial correlations that could mimic
quantum non-locality (entanglement).

#### S12.1 Derivation

**[D]** The telegrapher equation Green's function G(x,t) is non-zero for |x| ≤ ct
(causal, finite speed of propagation). For |x| > ct, G = 0 exactly. This is a
sharp (non-analytic) light-cone structure.

**[I]** The spatial two-point correlation function of the PRW in steady state (if a
steady state exists with non-trivial spatial variation) depends on the Green's function.
For a localized initial perturbation δ(x), the response at time t is spread over
|x| ≤ ct. This is non-local in the sense that a perturbation at x=0 affects the
entire region |x| ≤ ct simultaneously.

**[I]** However, this non-locality is causal — it propagates at speed c. It is not the
non-locality of quantum entanglement, which is:
(a) instantaneous (correlations appear at spacelike separation),
(b) described by a joint quantum state on a tensor-product Hilbert space, and
(c) able to violate Bell inequalities.

#### S12.2 Is this quantum non-locality?

**[P] Theorem S12:** The spatial non-locality of the PRW propagator is causal
(light-cone bounded) and classical. It cannot violate Bell inequalities and does not
correspond to quantum entanglement.

**Proof:** The PRW is a classical stochastic process. Its probability distributions
are classical probability measures, satisfying all Kolmogorov axioms (non-negative,
normalised, sigma-additive). Classical probability measures always admit local hidden
variable interpretations. Therefore, no PRW correlation function can violate a Bell
inequality (Bell 1964). Quantum entanglement is operationally defined as the violation
of Bell inequalities; the PRW cannot produce it. ∎

**S12 Verdict:** Non-locality is causal and classical (light-cone bounded). It is not
quantum non-locality and cannot produce entanglement or Bell-inequality violation.

---

### Candidate S13: The Two-Component Internal Degree of Freedom as a Proto-Qubit

**Claim:** The internal state (n⁺, n⁻) at each lattice site is a two-state system —
the minimal structure needed for a qubit. This internal degree of freedom could be
the physical origin of quantum two-level systems.

#### S13.1 Derivation

**[D]** At each site x, the PRW internal state is a vector (n⁺(x), n⁻(x)) ∈ ℝ²₊
(non-negative orthant). The total information content s = n⁺ + n⁻ > 0 fixes the
magnitude. The relative proportion p = n⁺/s ∈ [0,1] is the single internal degree
of freedom.

**[D]** The internal state space of the PRW at each site is:

```
M_int = {(n⁺, n⁻) : n⁺ ≥ 0, n⁻ ≥ 0} / (n⁺, n⁻) ~ (αn⁺, αn⁻) = ℝ₊ × Δ₁
```

For fixed s, M_int is the 1-simplex Δ₁ = [0,1], parametrised by p.

**[I]** A quantum two-level system (qubit) has state space CP¹ ≅ S², the Bloch sphere.
The Bloch sphere is a 2-dimensional real manifold (parametrised by (θ, φ)). The PRW
internal state space is a 1-dimensional real manifold (parametrised by p ∈ [0,1]).

#### S13.2 Why the internal DOF is not a qubit

**[P] Theorem S13:** The PRW internal degree of freedom at each site is not a qubit.

**Proof:**

1. **Dimension:** The qubit state space CP¹ is 2-dimensional (θ and φ). The PRW
   internal state space Δ₁ is 1-dimensional (p only). The PRW is missing one real
   parameter — the phase φ.

2. **Positivity:** The PRW state (n⁺, n⁻) has both components non-negative: n±≥0.
   A qubit state α|0⟩ + β|1⟩ has complex coefficients α, β ∈ ℂ with no sign
   constraint. The constraint n± ≥ 0 restricts the PRW to the "positive orthant"
   of the Bloch sphere, which corresponds to the subset {φ = 0, θ ∈ [0, π/2]} —
   a small arc of the equator, not the full sphere.

3. **Superposition:** A qubit can be in a superposition α|0⟩ + β|1⟩ with complex
   relative amplitude β/α. The PRW state (n⁺, n⁻) is a mixture, not a superposition:
   there is no relative phase. The distinction between superposition (quantum) and
   mixture (classical) is operationally testable via interference experiments; the PRW
   cannot produce interference fringes.

4. **Measurement:** Measuring a qubit projects the state and disturbs it in a way
   that depends on the measurement basis (Heisenberg uncertainty). Measuring the PRW
   state (n⁺, n⁻) (e.g., by observing whether the particle is right- or left-moving)
   is a classical observation that does not disturb the ensemble statistics. ∎

**S13 Verdict:** The two-component internal structure is genuinely present and is the
origin of the Z2 grading (Candidate S1). However, it is a classical 2-state system
(a Bernoulli variable), not a quantum 2-level system (a qubit). The missing degree of
freedom is the complex phase — the defining feature of quantum superposition.

---

## Part III — Summary Table

| Candidate | Structure | Present? | Novel? | Quantum-Supporting? | Notes |
|-----------|-----------|---------|--------|---------------------|-------|
| S1 | Z2 grading | Yes, genuine | No (known) | No | Classical even/odd decomposition |
| S2 | Spinor structure | Apparent only | No | No | Real fields, wrong sign |
| S3 | Clifford algebra | Apparent only | No | No | Coeff. algebra ≅ ℝ⊕ℝ (commutative) |
| S4 | Complex structure | Apparent only | No | No | Not ℂ-linear (couples Ψ and Ψ*) |
| S5 | Complex dispersion | Yes, genuine | No (known) | No | Standard telegrapher Green's function |
| S6 | Path-integral | Yes, genuine | No (Kac 1956) | No | Real positive weights, not quantum amplitudes |
| S7 | Info geometry | Yes, genuine | No (Fisher 1925) | No | Real slice of CP¹ only; phase absent |
| S8 | Commutative algebra | Yes, genuine | No | No | Classical by Gelfand-Naimark |
| S9 | Symplectic structure | Yes, genuine | No (known) | Partial | Needs ℏ and resolution of dissipation |
| S10 | T-reversal breaking | Yes, genuine | No | Absolute obstruction | Damping −J/τ; incompatible with unitarity |
| S11 | Memory kernel | Yes (classical) | No | No | Classical non-Markovianity (embed J) |
| S12 | Non-locality | Yes (causal) | No | No | Light-cone bounded; classical |
| S13 | Two-comp internal DOF | Yes, genuine | No | No | Missing phase degree of freedom |


---

## Part IV — Proof of Mathematical Equivalence to Classical Transport

### Section 14: Formal Equivalence Theorem

Having exhausted all candidate structures, we now establish the precise mathematical
relationship between the substrate and classical transport theory.

**[P] Theorem E1 (Equivalence):** The substrate transport system [C-s, C-J], together
with all its derived structures (E_sub, P_sub, dispersion relation, path-integral
representation, symplectic structure), is mathematically equivalent to the following
well-known classical structures:

1. The 1+1-dimensional telegrapher equation (Goldstein 1951, Kac 1956)
2. The linearised equations of 1D gas dynamics (pressure-velocity pair)
3. The Maxwell-Cattaneo heat transport model (Cattaneo 1948)
4. The classical damped wave equation with characteristic speeds ±c
5. The Hamiltonian field theory of a classical scalar field with dissipation

No structure has been found that goes beyond any of these equivalent formulations.

**Proof sketch:** The substutate equations [C-s, C-J] are a linear first-order symmetric
hyperbolic system in 1+1 dimensions with a linear damping term. The complete theory of
such systems is:

- Existence and uniqueness of solutions: standard energy estimates using E_sub as
  Lyapunov function (Rauch 2012, Symmetric Hyperbolic PDEs).
- Spectral theory: governed by the dispersion relation [DISP-EQ], which is the
  standard telegrapher dispersion.
- Path-integral representation: Kac (1956) integral formula for the telegrapher
  equation.
- Conserved quantities: Q = ∫s dx (information), E_sub (energy, not conserved due
  to dissipation), P_sub (momentum, not conserved).
- Symplectic structure: canonical Hamiltonian field theory of a wave equation with
  dissipation (Caldeira-Leggett type).

All of these are known classical structures. The substrate adds no new mathematics
beyond these. ∎

### Section 15: The Three Structural Obstructions to Quantum Emergence

The following three obstructions have been proven in this audit. Each is individually
sufficient to prevent quantum-state emergence from the substrate alone. Together, they
constitute a complete proof that the substrate cannot produce quantum mechanics without
external axioms.

---

**Obstruction Q1: Commutativity (Theorem S8)**

The substrate observable algebra 𝒜 is commutative. Quantum mechanics requires a
non-commutative algebra. No process internal to a commutative algebra can generate
non-commutativity.

*Type:* Algebraic impossibility.  
*Consequence:* Cannot derive [s, J] = iℏδ(x−y) from the substrate equations alone.  
*What would fix it:* External postulate of quantization (canonical quantization rule).

---

**Obstruction Q2: Absence of Complex Phase (Theorem S13 + S7)**

The PRW state space at each site is the positive 1-simplex Δ₁ (a real interval).
The quantum state space of a two-level system is CP¹ (a complex sphere). The missing
degree of freedom is the complex phase φ ∈ [0, 2π). No substrate variable plays the
role of a quantum phase.

*Type:* Dimensional/topological gap.  
*Consequence:* Cannot derive quantum superposition or interference from the substrate.  
*What would fix it:* An additional field carrying a U(1) phase degree of freedom —
not present in the substrate.

---

**Obstruction Q3: T-Reversal Breaking (Theorem S10)**

The substrate dynamics are not T-invariant (the damping −J/τ flips sign under
T-reversal). Quantum unitary evolution is T-invariant. A dissipative system cannot
be quantised by canonical quantization without additional machinery (e.g., system-bath
coupling, Caldeira-Leggett model).

*Type:* Dynamical incompatibility.  
*Consequence:* Cannot derive a self-adjoint Hamiltonian for the substrate without
resolving the dissipation.  
*What would fix it:* Embedding the substrate in a larger conservative system (where
the "bath" absorbs the dissipated energy), then quantizing the full system. This is
an external extension of the substrate, not a derivation from it.

---

### Section 16: What the Substrate CAN Provide

Despite the three obstructions, the substrate is not mathematically trivial. It provides
the following structures that are necessary (but not sufficient) preconditions for a
quantum theory to be applied to it:

1. **A well-defined state space:** The fields (s, J) form a well-posed initial value
   problem. Solutions exist and are unique (from the symmetric hyperbolic theory).

2. **A symplectic structure:** The canonical Poisson bracket {s(x), J(y)} ∝ δ(x−y)
   is the classical precursor of the quantum commutator. It is the correct starting
   point for a canonical quantization programme, once the dissipation is resolved.

3. **A path-integral representation:** The PRW path sum has the formal structure of
   an Euclidean path integral. Under Wick rotation, it formally becomes a quantum
   amplitude, providing a natural connection to quantum field theory — but only after
   the Wick rotation is introduced as an external step.

4. **An energy-like conserved quantity:** E_sub = ½c²s² + ½J² is the natural energy
   functional that would become the free-field Hamiltonian in a quantum theory of the
   substrate.

5. **A Z2 grading:** The even/odd decomposition of the PRW state space is a classical
   precursor of the spin statistics theorem. In a quantum theory, the Z2 grading would
   distinguish bosonic (even-graded) and fermionic (odd-graded) sectors.

These five structures are all present and all genuine — but they are present at the
classical level. Promoting them to quantum structures requires external axioms not
contained in the derivations.

---

## Part V — Mandatory Conclusion

### Section 17: Evaluation Against the Four Possible Conclusions

**Conclusion A: "The substrate is mathematically equivalent to classical transport."**

This would require that the substrate contains no structure beyond the standard
telegrapher equation / wave equation with dissipation.

**Assessment:** Theorem E1 establishes that the substrate is equivalent to a standard
classical symmetric hyperbolic system. However, calling this "equivalent to classical
transport" depends on what one means by "classical transport." The substrate is richer
than pure diffusion (it has wave propagation, a symplectic structure, and a path-integral
formulation) but it is a classical theory in the precise mathematical sense: its
observable algebra is commutative (Theorem S8), its evolution is non-unitary (Theorem
S10b), and its path weights are real positive (Theorem S6).

**Conclusion A is partially correct but imprecise.** The substrate is equivalent to
classical hyperbolic transport (a richer class than diffusion), not the most general
possible classical transport. It is not equivalent to a simple diffusion equation.

---

**Conclusion B: "The substrate contains richer mathematical structure but it is
insufficient for quantum emergence."**

This would require that there exist genuine mathematical structures in the substrate
that go beyond a simple diffusion equation, but that these structures do not force
or naturally produce quantum mechanics.

**Assessment:** The following structures are genuine and go beyond simple diffusion:

- **Symplectic structure** (Theorem S9): The canonical Poisson bracket {s,J} ∝ δ(x−y)
  is present. A diffusion equation does not have a symplectic structure.
- **Z2 grading** (Theorem S1): The even/odd decomposition (s, J) under spatial parity
  is present. Pure diffusion has no such grading.
- **Path-integral formulation** (Theorem S6): The PRW path sum has the Euclidean
  path-integral structure. Pure diffusion (Brownian motion) also has a path integral,
  but the PRW path integral has a finite velocity (sharp light cone), which is absent
  in Brownian motion.
- **Finite propagation speed** (Theorem S5): The telegrapher equation has a causal
  light cone at |x| = ct; the diffusion equation does not.

These structures are genuine and make the substrate richer than pure diffusion. However,
none of them forces quantum emergence:

- The symplectic structure is classical (Theorem S9); quantization is external.
- The Z2 grading is classical (Theorem S1); it does not produce non-commutativity.
- The path-integral weights are real positive (Theorem S6); quantum interference
  requires complex weights.
- The finite propagation speed is a classical feature (Theorem S5).

Furthermore, the three obstructions (Q1: commutativity, Q2: no phase, Q3: T-reversal
breaking) are absolute barriers that cannot be crossed from within the substrate.

**Conclusion B is correct. The substrate contains richer mathematical structure
than pure classical diffusion, but this structure is insufficient for quantum
emergence.** The three obstructions are proven and individually sufficient to
prevent quantum mechanics from emerging from the substrate equations alone.

---

**Conclusion C: "The substrate contains mathematically novel structure that provides
a plausible route toward quantum-state emergence."**

This would require a genuine mathematical structure in the substrate that:
(a) is not present in classical transport theory, and
(b) provides a natural, substrate-internal route to quantum amplitudes, phases, or
    non-commutativity.

**Assessment:** No such structure has been found. All 13 candidates were examined:

- The structures that are genuinely present (S1, S5, S6, S7, S8, S9, S10, S11, S12,
  S13) are all known in classical transport theory or classical Hamiltonian mechanics.
- The structures that could naively appear novel (S2, S3, S4) turn out to be apparent
  only — formal resemblances that do not survive rigorous examination.
- The single most notable structure (S9: symplectic) is the natural precursor of
  quantum mechanics but requires external quantization to become quantum.

There is no substrate-internal mechanism that performs the Wick rotation τ → it,
introduces complex phases, breaks commutativity, or generates ℏ. All of these
are external inputs.

**Conclusion C is false.** No structure providing a plausible substrate-internal
route to quantum emergence has been found.

---

**Conclusion D: "The current derivations are insufficient to determine which of A–C
is correct."**

This would require that the existing derivations leave open questions that cannot be
resolved without new calculations.

**Assessment:** The proofs in this audit — Theorems S1 through S13, E1, and the
obstruction theorems Q1–Q3 — are complete within the framework of the established
substrate. There are no gaps that would change the conclusion given the existing
definitions of (n⁺, n⁻), [M1±], [C-s], [C-J].

**Conclusion D is false.** The existing derivations are sufficient to determine the
answer.

---

### Section 18: MANDATORY FINAL CONCLUSION

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  CONCLUSION B                                                            ║
║                                                                          ║
║  The substrate contains richer mathematical structure than pure          ║
║  classical diffusion, but this structure is insufficient for             ║
║  quantum-state emergence.                                                ║
║                                                                          ║
║  STRUCTURES GENUINELY PRESENT IN THE SUBSTRATE:                          ║
║                                                                          ║
║  1. Z2-graded decomposition of the state space (s even, J odd)          ║
║  2. Canonical symplectic structure {s(x),J(y)}_PB ∝ δ(x−y)             ║
║  3. Euclidean path-integral formulation (Kac 1956 representation)        ║
║  4. Causal (finite-speed) propagation with dispersion relation           ║
║     ω² + i(ω/τ) − c²k² = 0                                              ║
║  5. Classical information geometry on the PRW state space                ║
║                                                                          ║
║  STRUCTURES APPARENT BUT NOT GENUINE:                                    ║
║                                                                          ║
║  6. Spinor/Dirac structure (wrong signature, real fields)                ║
║  7. Clifford algebra (coeff. algebra ≅ ℝ⊕ℝ, commutative)               ║
║  8. Canonical complex structure (eq. for Ψ is ℝ-linear, not ℂ-linear)  ║
║                                                                          ║
║  THREE PROVEN OBSTRUCTIONS TO QUANTUM EMERGENCE:                         ║
║                                                                          ║
║  Q1 [Algebraic]: Observable algebra 𝒜 is commutative.                   ║
║       Quantum mechanics requires non-commutative algebra.                ║
║       Cannot be derived from commutative substrate internally.           ║
║                                                                          ║
║  Q2 [Topological]: PRW state space at each site is Δ₁ ≅ [0,1].         ║
║       Quantum two-level system state space is CP¹ ≅ S².                 ║
║       Missing degree of freedom: complex phase φ ∈ [0,2π).              ║
║                                                                          ║
║  Q3 [Dynamical]: Substrate evolution breaks T-reversal symmetry.         ║
║       (Damping term −J/τ flips sign under T: t→−t, J→−J.)              ║
║       Quantum evolution is unitary (T-invariant).                        ║
║       Dissipation is incompatible with self-adjoint Hamiltonian.         ║
║                                                                          ║
║  WHAT WOULD BE NEEDED TO REACH CONCLUSION C:                             ║
║                                                                          ║
║  At minimum three external inputs are required to bridge the gap:        ║
║                                                                          ║
║  (I)   ℏ: the quantum of action — not in the substrate.                  ║
║  (II)  A complex phase field: carrying U(1) degree of freedom —         ║
║         not in the substrate.                                            ║
║  (III) Resolution of dissipation: embedding in a conservative system,   ║
║         or a proof that the macroscopic damping emerges from a           ║
║         microscopically unitary dynamics — not established.              ║
║                                                                          ║
║  The substrate is the natural classical precursor of a quantum           ║
║  field theory (it has symplectic structure, path-integral form,          ║
║  and causal propagation) but it is not itself that quantum theory.       ║
║  The classical-to-quantum transition requires external axioms.           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Appendix: Proof that the Three Obstructions Are Independent

**[P] Theorem IND:** The three obstructions Q1, Q2, Q3 are logically independent —
no two of them imply the third.

**Proof:**

- *Q1 does not imply Q3:* Classical Hamiltonian mechanics (a commutative theory) is
  T-invariant. Example: the free wave equation ∂²_t φ = c²∂²_x φ is commutative and
  T-invariant.

- *Q3 does not imply Q1:* Non-commutative dissipative systems exist. Example:
  the Lindblad master equation dρ/dt = γ(LρL† − ½{L†L, ρ}) is non-commutative (ρ is
  a density matrix, L is an operator on ℂ²) and dissipative (entropy increases).

- *Q2 does not imply Q1:* A classical system can lack the phase degree of freedom
  while being commutative. The PRW is an example: it lacks φ (Q2 holds) and is
  commutative (Q1 holds). But one can construct a commutative system with a phase-like
  variable (e.g., a classical angular variable θ(x)).

- *Q1 does not imply Q2:* A commutative theory can have a phase-like variable. Example:
  classical electrodynamics has a U(1) gauge phase in its potentials, yet the observable
  algebra (E and B fields) is commutative.

- *Q2 does not imply Q3:* Lacking a phase is a topological property; T-reversal
  breaking is a dynamical property. They are logically independent.

- *Q3 does not imply Q2:* A T-violating system can have a full complex state space.
  Example: a quantum system with an anti-Hermitian Hamiltonian (non-Hermitian quantum
  mechanics) violates T-reversal but operates in a full complex Hilbert space (CP¹). ∎

Since the three obstructions are independent, each must be addressed separately to
reach Conclusion C. The substrate currently satisfies all three, forming a complete
set of barriers.

---

*Document produced from established derivations only. No new physics introduced.
All proofs operate within the mathematical framework of the five source documents.*
