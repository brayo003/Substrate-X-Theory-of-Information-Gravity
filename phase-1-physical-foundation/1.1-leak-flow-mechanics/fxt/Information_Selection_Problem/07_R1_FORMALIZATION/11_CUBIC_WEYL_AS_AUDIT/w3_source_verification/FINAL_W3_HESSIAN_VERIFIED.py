#!/usr/bin/env python3
"""
FINAL VERIFIED COMPUTATION: W3 Hessian on S²×S²
=================================================

Background: S²×S² product metric, r₁=r₂=1, equatorial point θ₁=θ₂=π/2.
  - Metric: ḡ_{μν} = diag(1,1,1,1)  (identity at equatorial point)
  - All Christoffel symbols vanish at this point: Γ̄^k_{ij} = 0
  - Background Riemann: R̄_{0101} = R̄_{2323} = 1, all others 0 (or by antisymmetry)
  - Background Ricci: R̄_{μν} = δ_{μν}  (Einstein space, R̄_{μν} = Λ g_{μν} with Λ=1)
  - Scalar curvature: R̄ = 4

Action:
  S_W3[g] = ∫ d⁴x √g  C_{abcd} C^{cdef} C_{efab}

  where C is the Weyl tensor with convention (Wald GR, eq. 3.2.28):
  C_{abcd} = R_{abcd}
             - 1/2 (g_{ac}R_{bd} - g_{ad}R_{bc} - g_{bc}R_{ad} + g_{bd}R_{ac})
             + 1/6 R (g_{ac}g_{bd} - g_{ad}g_{bc})

Method:
  1. Perturb: g_{μν} = ḡ_{μν} + ε h_{μν}
  2. In momentum space: h_{μν}(x) = H_{μν} e^{ip·x}, ∂_μ → ip_μ
  3. At equatorial point (Γ̄=0), first-order connection:
       δΓ^k_{ij} = (i/2)(p_i H_{jk} + p_j H_{ik} - p_k H_{ij})
  4. First-order Riemann:
       δR^k_{lij} = −p_i δΓ^k_{lj} + p_j δΓ^k_{li}  (the i² = -1 absorbed)
  5. The quadratic-in-h piece of the W3 action density is:
       δ²W3 = 6·δC_{abcd}·δC_{cdef}·C̄_{efab}  + (lower-derivative terms from δ²C)
  6. Extract p⁴ coefficient for TT-projected modes.

Results:
  - W3_bar = C̄_{abcd} C̄_{cdef} C̄_{efab} = 32/9  (verified by direct computation)
  - C²_bar = C̄_{abcd} C̄^{abcd} = 16/3  (verified)
  - For TT modes with p ∥ e₃:
      In-sector (h+, hx):     K_W3 = −2   (coefficient of p⁴·|h|²)
      Cross-sector (h02,h12): K_W3 = +1   (coefficient of p⁴·|h|²)

Normalization note:
  Some literature (e.g., older files in this project) cite W3=128/27 for S²×S².
  This is NOT the value of C_{abcd}C_{cdef}C_{efab}. Our direct computation gives 32/9.
  The ratio 128/27 ÷ 32/9 = 4/3 indicates a different normalization convention.
  We use the bare contraction throughout (no prefactor).

Physical note:
  The W3 action C^3 gives a p⁴ kinetic term in the Hessian — the same derivative
  order as the C² action. This is because δ²(C^3) ∼ C̄·(δC)² ∼ p⁴·h², where each
  δC ∼ p²·h (second derivative of h), and the background C̄ provides no extra p.
"""

from fractions import Fraction
import sympy as sp

print("=" * 65)
print("W3 HESSIAN COMPUTATION — FINAL VERIFIED RESULTS")
print("=" * 65)

# ---------------------------------------------------------------
# Background Weyl tensor C̄_{abcd} on S²×S² at equatorial point
# Convention: all symmetries C_{abcd} = -C_{bacd} = -C_{abdc} = C_{cdab}
# ---------------------------------------------------------------
CB_raw = {
    (0,1,0,1): Fraction(2,3),
    (0,2,0,2): Fraction(-1,3),
    (0,3,0,3): Fraction(-1,3),
    (1,2,1,2): Fraction(-1,3),
    (1,3,1,3): Fraction(-1,3),
    (2,3,2,3): Fraction(2,3),
}
CB = {}
def _set_sym(a, b, c, d, v):
    CB[(a,b,c,d)] = v
    CB[(b,a,c,d)] = -v
    CB[(a,b,d,c)] = -v
    CB[(b,a,d,c)] = v
    CB[(c,d,a,b)] = v
    CB[(d,c,a,b)] = -v
    CB[(c,d,b,a)] = -v
    CB[(d,c,b,a)] = v

for (a,b,c,d), v in CB_raw.items():
    _set_sym(a, b, c, d, v)

def Cb(a,b,c,d): return CB.get((a,b,c,d), Fraction(0))
def Ricbar(a,b): return Fraction(1) if a==b else Fraction(0)
Rsc = Fraction(4)

# Verify background scalars
C2_bar = sum(CB.get((a,b,c,d),Fraction(0))**2
             for a in range(4) for b in range(4)
             for c in range(4) for d in range(4))
W3_bar = sum(CB.get((a,b,c,d),Fraction(0))
             * CB.get((c,d,e,f),Fraction(0))
             * CB.get((e,f,a,b),Fraction(0))
             for a in range(4) for b in range(4)
             for c in range(4) for d in range(4)
             for e in range(4) for f in range(4))

print(f"\nBackground scalars:")
print(f"  C²_bar = C̄_{{abcd}} C̄^{{abcd}} = {C2_bar}")
assert C2_bar == Fraction(16,3), f"Expected 16/3, got {C2_bar}"
print(f"  W3_bar = C̄_{{abcd}} C̄_{{cdef}} C̄_{{efab}} = {W3_bar}")
assert W3_bar == Fraction(32,9), f"Expected 32/9, got {W3_bar}"
print("  Both verified ✓")

# ---------------------------------------------------------------
# Momentum-space perturbation machinery
# ---------------------------------------------------------------
t = sp.Symbol('t', positive=True)
pv = [sp.Integer(0), sp.Integer(0), sp.Integer(0), t]  # p = (0,0,0,t)

def build_dC(H_mat):
    """Compute first-order Weyl perturbation δC_{abcd} in momentum space.
    
    H_mat: 4x4 matrix of metric perturbation amplitudes.
    pv: momentum 4-vector (global).
    Returns: dict mapping (a,b,c,d) → sympy expression.
    """
    def dG(k, i, j):
        """δΓ^k_{ij} amplitude (real part; overall factor i extracted)."""
        return sp.Rational(1,2) * (
            pv[i]*H_mat[j][k] + pv[j]*H_mat[i][k] - pv[k]*H_mat[i][j]
        )

    def dR_up(k, l, i, j):
        """δR^k_{lij} amplitude. At Γ̄=0: = −p_i δΓ^k_{lj} + p_j δΓ^k_{li}.
        The factor i² = −1 (two derivatives) is absorbed.
        """
        return -pv[i]*dG(k,l,j) + pv[j]*dG(k,l,i)

    def dRic(a, b):
        return sum(dR_up(c, a, c, b) for c in range(4))

    def dRsc():
        return sum(dRic(a, a) for a in range(4))

    def dC_fn(a, b, c, d):
        gac = 1 if a==c else 0
        gad = 1 if a==d else 0
        gbc = 1 if b==c else 0
        gbd = 1 if b==d else 0
        v = dR_up(a, b, c, d)
        # Schouten term from h in the metric:
        v -= sp.Rational(1,2) * (
            H_mat[a][c]*Ricbar(b,d) - H_mat[a][d]*Ricbar(b,c)
            - H_mat[b][c]*Ricbar(a,d) + H_mat[b][d]*Ricbar(a,c)
        )
        # Schouten term from δRicci:
        v -= sp.Rational(1,2) * (
            gac*dRic(b,d) - gad*dRic(b,c)
            - gbc*dRic(a,d) + gbd*dRic(a,c)
        )
        # Trace term from δR_scalar:
        v += sp.Rational(1,6) * dRsc() * (gac*gbd - gad*gbc)
        # Trace term from h in R̄·g:
        v += sp.Rational(1,6) * Rsc * (
            H_mat[a][c]*gbd + gac*H_mat[b][d]
            - H_mat[a][d]*gbc - gad*H_mat[b][c]
        )
        return sp.expand(v)

    nz = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    v = dC_fn(a, b, c, d)
                    if v != 0:
                        nz[(a,b,c,d)] = v
    return nz


def Q_W3(H_mat):
    """Leading kinetic contribution to δ²S_W3:
    Q = 6·δC_{abcd}·δC_{cdef}·C̄_{efab}
    Returns sympy polynomial in t.
    """
    nz = build_dC(H_mat)
    Q = sp.Integer(0)
    for (a,b,c,d), v1 in nz.items():
        for (c2,d2,e,f), v2 in nz.items():
            if (c2,d2) != (c,d):
                continue
            cb = Cb(e, f, a, b)
            if cb == 0:
                continue
            Q += 6 * v1 * v2 * cb
    return sp.expand(Q)

# ---------------------------------------------------------------
# TT mode analysis
# ---------------------------------------------------------------
print("\nHessian computation: Q = 6·δC_{abcd}·δC_{cdef}·C̄_{efab}")
print("Momentum: p = (0, 0, 0, t),  p² = t²")
print()

# True TT modes for p ∥ e₃:
#   h+  = diag(1,−1,0,0): traceless (tr=0), transverse (h_{3ν}=0)
#   hx  = h_{01}+h_{10}:  off-diagonal, transverse
#   h02 = h_{02}+h_{20}:  cross-sector (S²₁ × S²₂)
#   h12 = h_{12}+h_{21}:  cross-sector

TT_modes = [
    ("h+ (in-sector)",    [[1,0,0,0],[0,-1,0,0],[0,0,0,0],[0,0,0,0]]),
    ("hx (in-sector)",    [[0,1,0,0],[1,0,0,0],[0,0,0,0],[0,0,0,0]]),
    ("h02 (cross-sector)",[[0,0,1,0],[0,0,0,0],[1,0,0,0],[0,0,0,0]]),
    ("h12 (cross-sector)",[[0,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,0]]),
]

print(f"{'Mode':<25} {'|h|²':>5} {'Q₀ (mass)':>10} {'Q₄ (kinetic)':>13} {'K_W3':>7}")
print("-" * 65)
results = {}
for name, H in TT_modes:
    norm2 = sum(H[a][b]**2 for a in range(4) for b in range(4))
    Q = Q_W3(H)
    poly = sp.Poly(Q, t)
    c0 = int(poly.nth(0))
    c4 = int(poly.nth(4))
    K = Fraction(c4, norm2)
    results[name] = {"norm2": norm2, "Q0": c0, "Q4": c4, "K": K}
    print(f"  {name:<22} {norm2:>5} {c0:>10} {c4:>13}   {K}")

print()

# Assertions
assert results["h+ (in-sector)"]["K"] == Fraction(-2), "h+ K_W3 should be -2"
assert results["hx (in-sector)"]["K"] == Fraction(-2), "hx K_W3 should be -2"
assert results["h02 (cross-sector)"]["K"] == Fraction(1), "h02 K_W3 should be +1"
assert results["h12 (cross-sector)"]["K"] == Fraction(1), "h12 K_W3 should be +1"
print("All assertions passed ✓")

print()
print("=" * 65)
print("SUMMARY")
print("=" * 65)
print()
print("Background:")
print(f"  W3_bar = C̄_{{abcd}} C̄_{{cdef}} C̄_{{efab}} = 32/9  (exact)")
print(f"  C²_bar = C̄_{{abcd}} C̄^{{abcd}}           = 16/3  (exact)")
print()
print("W3 Hessian on TT sector (S²×S², p² = t²):")
print("  δ²S_W3 = K_W3 · p⁴ · h^{TT}_{μν} h^{μν,TT}  (+ p-independent mass term)")
print()
print("  K_W3 = −2   for in-sector graviton modes (h+, hx)")
print("  K_W3 = +1   for cross-sector graviton modes (h02, h12)")
print()
print("Derivative structure:")
print("  W3 = C^3 has 6 metric derivatives in the action density.")
print("  The Hessian δ²(C^3) ~ C̄·(δC)² ~ p⁴·h².")
print("  Leading kinetic term is p⁴ (same order as C² action).")
print()
print("Normalization note:")
print("  W3=128/27 cited in some prior files = (4/3)·(32/9).")
print("  This reflects a different prefactor convention, NOT a calculation error.")
print("  Our convention: S_W3 = ∫ d⁴x √g · C_{abcd}C^{cdef}C_{ef}^{ab}")
print("  with no extra prefactor. Coupling constant w₃ absorbs any convention.")
