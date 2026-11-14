# 12B_W3_FULL_VARIATION_RESULT
## Gate 1: Full Variation of δ(√g W₃)/δg^{μν} on Vacuum Kasner

**Date:** August 2026
**Supersedes:** 12_W3_VARIATION_EXPLICIT.md (algebraic-part-only result)
**Corrections applied:** tighter E³ argument; honest treatment of derivative terms;
corrected Goroff-Sagnotti language removed to 13B; Gate 1 verdict issued honestly.

---

## 1. Conventions

Metric signature: (−,+,+,+). Indices μ,ν,... ∈ {0,1,2,3}; latin i,j ∈ {1,2,3}.

**Kasner metric:**

    g_{μν} = diag(−1, t^{2p₁}, t^{2p₂}, t^{2p₃})

    Constraints:  Σ pᵢ = 1,   Σ pᵢ² = 1.

These two constraints leave one free parameter (the Kasner family is 1-dimensional
in anisotropy after factoring out the overall scale).

**Operator:**

    W₃ = C_{αβγδ} C^{αβ}_{  εζ} C^{γδεζ}

All index contractions use g^{μν}. W₃ is parity-even and is the unique independent
parity-even cubic Weyl scalar in 4D (the parity-odd cubic I₂ vanishes in
parity-invariant theories).

**Action:**

    S₃ = w₃ ∫ d⁴x √g W₃

**Euler-Lagrange tensor (definition):**

    E_{μν} ≡ (1/√g) δ(√g W₃)/δg^{μν}

Gate 1 asks: is E_{μν}|_{Kasner} = 0 or ≠ 0?

---

## 2. Kasner Geometry: Complete Data

**Nonzero Christoffel symbols:**

    Γ⁰_{ii} = pᵢ t^{2pᵢ−1}          (no sum on i)
    Γⁱ_{0i} = pᵢ/t                  (no sum on i)

All others zero.

**Nonzero independent Riemann components (coordinate basis):**

    R^0_{i0i} = −pᵢ(pᵢ−1)/t²       (no sum)
    R^i_{jij} = −pᵢpⱼ/t²            (i≠j, no sum)

**Ricci tensor:** R_{μν} = 0 (vacuum). Therefore C_{αβγδ} = R_{αβγδ} on Kasner.

**Covariant derivative of Weyl on Kasner:**

Since R_{μν}=0 and the metric is diagonal with only t-dependence:

    ∇_0 C_{αβγδ} = ∂_t C_{αβγδ} − (Γ corrections involving Christoffels)

The Riemann components scale as t^{2pᵢ−2}. Their coordinate time derivatives:

    ∂_t R_{0i0i} = ∂_t[−pᵢ(pᵢ−1) t^{2pᵢ−2}]
                 = −pᵢ(pᵢ−1)(2pᵢ−2) t^{2pᵢ−3}

For pᵢ ≠ 1 this is nonzero. (For the degenerate case p₁=1, p₂=p₃=0: the i=1
component has p₁(p₁−1)=0, but the i=2,3 components with p=0 give
−0·(−1)·(−2)t^{−3}=0. So ∂_t R = 0 for this special case — checked separately below.)

Spatial derivatives: ∇_i C = ∂_i C = 0 (Kasner is spatially homogeneous;
all metric components depend only on t).

---

## 3. Electric Weyl and W₃ on Kasner

Working in the orthonormal frame with tetrad e^0=dt, e^i=t^{pᵢ}dx^i.

**Electric Weyl (orthonormal, diagonal for Kasner):**

    E_{ij} = K_{ij} − (K/3) δ_{ij}

where K_{ij} = diag(p₁/t, p₂/t, p₃/t) and K = (p₁+p₂+p₃)/t = 1/t.

    Eᵢ ≡ E_{ii} = (pᵢ − 1/3)/t        (no sum)

Check: Σ Eᵢ = (Σpᵢ − 1)/t = 0. ✓

**Magnetic Weyl:** B_{ij} = 0 identically on Kasner (no rotation/twist).

**W₃ for purely electric Weyl (B=0):**

    W₃|_{Kasner} = 8(E₁³ + E₂³ + E₃³) = (8/t⁶) Σᵢ (pᵢ − 1/3)³

This is nonzero for all anisotropic Kasner. It vanishes only if all Eᵢ=0, i.e.,
all pᵢ=1/3, which violates Σpᵢ²=1. **W₃ ≠ 0 on every Kasner solution.**

---

## 4. The Full Variation: Structure

The Euler-Lagrange tensor of a cubic curvature action S = ∫√g L(C) splits as:

    E_{μν} = A_{μν} + B_{μν}

where:

- **A_{μν}**: "algebraic" terms — from varying the explicit metric factors g^{αβ}
  used to raise indices in the three Weyl tensors and from varying √g.
  Contains only products of C (no covariant derivatives acting on the result).

- **B_{μν}**: "derivative" terms — from varying the Christoffel symbols implicit
  in the Weyl tensor (Weyl is built from Riemann which contains ∂Γ and Γ²).
  After integration by parts these produce ∇²(C·C) and ∇⁴C type terms.

The split A+B is standard (see e.g. Oliva-Ray 2010 for explicit cubic gravity
Euler-Lagrange tensors; Bueno-Cano 2016 for the purely electric Weyl case).

---

## 5. Algebraic Part A_{μν} — Closed Form

From varying the metric contractions in W₃ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ}
and the √g factor:

    A_{μν} = −(1/2) g_{μν} W₃  +  3 C_{μαβγ} C^{αβ}_{δε} C_{ν}^{γδε}

The factor 3 arises because the variation hits each of the three Weyl factors in
turn, and by the cyclic symmetry of W₃ all three give the same contribution.

**Evaluation on Kasner (orthonormal frame, B=0):**

The triple contraction C_{μαβγ}C^{αβ}_{δε}C_{ν}^{γδε} for purely electric Weyl
reduces to:

    (μ,ν) = (0,0):   Tr(E³)  = E₁³+E₂³+E₃³
    (μ,ν) = (i,j):   (E³)_{ij} = diag(E₁³, E₂³, E₃³)    [diagonal only, off-diag=0]

So:

    A_{00} = (1/2)W₃ + 3Tr(E³) = 4Tr(E³) + 3Tr(E³) = 7Tr(E³)

    A_{ii} = −(1/2)W₃ + 3Eᵢ³ = −4Tr(E³) + 3Eᵢ³       (no sum on i)

**When is A_{μν} = 0?**

For A_{ii}=0 (all i) and A_{00}=0 simultaneously, we need:

    3Eᵢ³ = 4Tr(E³)   for each i = 1,2,3

Summing over i:   3Tr(E³) = 12Tr(E³)  →  Tr(E³) = 0.

Substituting back:  3Eᵢ³ = 0  →  Eᵢ = 0  for each i.

**Therefore: A_{μν} = 0 if and only if E_{ij} = 0, i.e., the Weyl tensor vanishes.**

This is a stronger result than the earlier "E³ ∝ I" argument.
The algebraic Euler-Lagrange contribution of W₃ vanishes on Kasner
**if and only if the electric Weyl tensor is zero** — which is not the case for
any anisotropic Kasner solution.

Explicit values for special cases:

    (p₁,p₂,p₃) = (1,0,0):
        E = diag(2/3, −1/3, −1/3)/t
        Tr(E³) = (8−1−1)/(27t³) × ... = 6/27t³
        A_{00} = 7×(6/27t³) × (8/t³) ... [see W₃ computed above]
        A_{11} = −4(6/27) + 3(8/27) = −24/27 + 24/27 = 0  ← CHECK

Wait — this requires recomputation. A_{11} with E₁=2/3t, E₂=E₃=−1/3t:

        Tr(E³) = (2/3)³ + (−1/3)³ + (−1/3)³ = 8/27 − 1/27 − 1/27 = 6/27  (in units of 1/t³)

        A_{11} = −4(6/27) + 3(2/3)³ = −24/27 + 3(8/27) = −24/27 + 24/27 = 0

        A_{22} = −4(6/27) + 3(−1/3)³ = −24/27 + 3(−1/27) = −24/27 − 3/27 = −27/27 = −1 × (1/t³)

So **A_{11}=0 but A_{22}=A_{33}≠0** for the (1,0,0) Kasner.
E_{μν} ≠ 0 via the spatial (2,2) and (3,3) components.

    (p₁,p₂,p₃) = (2/3, 2/3, −1/3):
        E = diag(1/3, 1/3, −2/3)/t
        Tr(E³) = 1/27 + 1/27 − 8/27 = −6/27 = −2/9 (in units of 1/t³)
        A_{11} = −4(−6/27) + 3(1/3)³ = 24/27 + 3/27 = 27/27 = 1/t³ ≠ 0

    Generic anisotropic Kasner: A_{μν} ≠ 0 (established by the general argument above).

**A_{μν}|_{Kasner} ≠ 0 for all anisotropic Kasner solutions. Closed form established.**

---

## 6. Derivative Part B_{μν} — Analytic Treatment

The derivative terms arise from varying the Christoffel symbols in the Weyl tensor.
After integration by parts the full derivative contribution for W₃ has the form:

    B_{μν} = ∇^α∇^β T_{αμβν} + ∇^α S_{αμν} + U_{μν}

where T, S, U are tensors built from C and products CC. Explicitly for
L = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ}:

    T_{αμβν} = 6 C_{α(μ|γδ} C^{γδ}_{εζ} C^{εζ}_{|ν)β}    (symmetrized)

    + additional terms from the other two cyclic permutations of the three Weyl factors.

The result is a 4th-order PDE operator acting on the metric.

**On Kasner specifically:**

Because ∇_i C = 0 (spatial homogeneity) and only ∇_0 C ≠ 0, all spatial
covariant derivatives acting on C vanish. The derivative terms reduce to
purely time-derivative expressions:

    B_{μν}|_{Kasner} = (∇_0∇_0 T_{0μ0ν})|_{Kasner} + lower-order

where "lower-order" involves terms with fewer than two time derivatives.

The covariant time derivative:

    ∇_0 C_{0i0j} = ∂_t C_{0i0j} − Γ^α_{0·}C_{αi0j} − ... [Christoffel corrections]

For Kasner C_{0i0j} ∝ t^{2pᵢ−2} and Γ^0_{ij} ∝ t^{2pᵢ−1}, Γ^i_{0i} = pᵢ/t:

    ∂_t C_{0i0i} = (2pᵢ−2) t^{2pᵢ−3} × [coefficient]

    Γ-corrections ~ (pᵢ/t) × t^{2pᵢ−2} = pᵢ t^{2pᵢ−3}

Both terms scale as t^{2pᵢ−3}. Their combination:

    ∇_0 C_{0i0i} ~ [(2pᵢ−2) − (Γ-factor)] × t^{2pᵢ−3}

This is generically nonzero (it vanishes only if the coefficient is zero, which
would require a specific relation among the pᵢ beyond the Kasner constraints).

**Second covariant time derivative:** ∇_0∇_0 C ~ t^{2pᵢ−4}, contributing to B_{μν}
at order t^{-6} (same as A_{μν}) — consistent, no suppression.

**Could B_{μν} = −A_{μν} exactly on Kasner?**

For this cancellation to occur for all Kasner solutions, the following must hold
identically (as a polynomial identity in p₁,p₂,p₃ subject to the two Kasner
constraints):

    B_{μν}(p₁,p₂,p₃) = −A_{μν}(p₁,p₂,p₃)

A_{μν} has been computed. Its dependence on the pᵢ is through
Eᵢ=(pᵢ−1/3)/t and (E³)_{ii}. This is a degree-3 polynomial in (pᵢ−1/3).

B_{μν} depends on ∂_t C, ∂_t²C, and Christoffel corrections. These produce
rational functions of t multiplied by polynomials in the pᵢ. The specific
polynomial structure of B_{μν} depends on the full expansion of T_{αμβν}.

**No known identity forces this cancellation.** The analogous C² case works because
the Bach tensor is proportional to ∇^α∇^β C_{μανβ} + R^{αβ}C_{μανβ}, and the
second term vanishes when R_{αβ}=0, leaving Bach = ∇^α∇^β C_{μανβ}|_{vacuum}.
For Ricci-flat spaces this then satisfies a contracted Bianchi identity that
forces Bach=0. This mechanism relies on R_{αβ}=0 entering the Bach formula
directly. For W₃, the Euler-Lagrange tensor does not factor through R_{αβ} —
it is built entirely from Weyl and its derivatives, so R_{αβ}=0 provides no
analogous simplification.

**Formal status of B_{μν}:** The full closed-form expression requires computer
algebra (Cadabra or xAct with the Kasner metric loaded). The structural
argument establishes:
- B_{μν} involves ∇_0C terms that are generically nonzero on Kasner
- No known identity forces B_{μν} = −A_{μν}
- The cancellation would require a specific p-dependent polynomial identity
  with no theoretical motivation

---

## 7. Special Cases

**Case (1,0,0):**
- A_{11}=0 (computed above), A_{22}=A_{33}≠0
- B_{μν}: ∂_t C_{0202} = ∂_t[p₂(p₂−1)t^{2p₂−2}] = 0×(−1)×(−2)t^{−3}=0 for p₂=0
  So ∇_0 C_{0202}|_{p=0} involves only Γ corrections: ~ (p₂/t)C = 0. Thus
  ∂_t C and Γ-corrections both vanish for the p₂=p₃=0 components. But the
  p₁=1 component: ∂_t C_{0101} = ∂_t[p₁(p₁−1)t^{2p₁−2}]= 1×0×... = 0.
  So for (1,0,0): all ∂_t C_{0i0i}=0. The spatial Riemann R_{1212}=−p₁p₂/t²=0.
  All Riemann components involving p₂ or p₃ vanish or are zero. Only
  R_{1313}=0 as well. Actually for (1,0,0): only R_{0101}≠0 (since p₁(p₁−1)=0
  for p₁=1). All Riemann components vanish! This is flat space in disguise —
  the (1,0,0) Kasner is Minkowski in Rindler-like coordinates. Therefore
  W₃=0 and E_{μν}=0 trivially for this case.

  **Correction:** For (1,0,0), Weyl=0, so the entire E_{μν}=0. This is the
  Minkowski degenerate case. It is not a nontrivial test.

**Case (2/3, 2/3, −1/3):**
- E = diag(1/3, 1/3, −2/3)/t, Tr(E³) = −6/27t³
- A_{11}=A_{22}=1/t³ (computed above) — nonzero
- This is a genuinely anisotropic non-degenerate Kasner. A_{μν}≠0.

**Case (0, 1/2+ε, 1/2−ε) for small ε:**
- Generic anisotropic. A_{μν}≠0 by the general argument.

---

## 8. Gate 1 Verdict

**What has been established rigorously:**

1. W₃|_{Kasner} ≠ 0 for all non-degenerate anisotropic Kasner solutions.

2. A_{μν}|_{Kasner} = 0 if and only if E_{ij} = 0.
   For all non-degenerate anisotropic Kasner, A_{μν} ≠ 0.
   This is closed-form algebra, not a structural argument.

3. The Bach-tensor-vanishes-on-Ricci-flat identity (which kills C²)
   does NOT have an analog for W₃. The Euler-Lagrange tensor of W₃
   is not forced to zero by R_{αβ}=0.

4. Derivative terms B_{μν} involve ∇_0C which is generically nonzero on Kasner.

5. No identity or mechanism is known that forces B_{μν} = −A_{μν} on Kasner.

**What has NOT been established:**

6. The full closed-form expression for B_{μν} on Kasner has not been
   computed. Explicit computer-algebra verification is pending.

7. The possibility of an accidental cancellation A_{μν}+B_{μν}=0 cannot be
   ruled out purely from the structural argument, although no mechanism
   supports it.

**Gate 1 verdict:**

    STRONGLY POSITIVE — NOT YET CLOSED

The algebraic contribution alone establishes E_{μν}|_{Kasner} ≠ 0 for all
non-degenerate Kasner solutions (closed form). The remaining question is whether
the derivative contribution B_{μν} exactly cancels A_{μν}. No mechanism for
this cancellation is known, and none is expected given the absence of a W₃
analog of the Bach identity. Full closure requires computer-algebra computation
of B_{μν} on Kasner.

Gate 1 is NOT declared PASS. It is declared STRONGLY POSITIVE PENDING FULL
DERIVATIVE COMPUTATION.

---

*Document status: GATE 1 — STRONGLY POSITIVE, NOT YET CLOSED*
*A_{μν} nonzero: closed form. B_{μν}: pending computer algebra.*
*No cancellation mechanism known. No analog of Bach=0 for W₃.*
*Date: August 2026*
