#!/usr/bin/env python3
"""
TEST 5-8: Full W3 Hessian Computation in Momentum Space

Strategy:
- Work at the equatorial point of S²×S² where ḡ=I, Γ̄=0
- Perturb: h_{μν}(x) = H_{μν} exp(ip·x)  (single Fourier mode)
- ∂_μ → ip_μ  in all curvature formulas
- Extract δ²S_W3 as a quadratic form in H_{μν}
- The Hessian H^{μν,ρσ}(p) is the kernel of this quadratic form

Physics: The W3 action expanded to second order in h gives the kinetic operator.
The TT-projected piece with lowest derivative order determines K_W3 via:
  δ²S_W3|_{TT} = K_W3 ∫ d⁴x H_{μν}(-p) p^{2n} P^{μν,ρσ}_{TT} H_{ρσ}(p)

This script computes the EXACT Hessian components using:
1. Exact background Weyl components (from TEST 1-3)
2. Explicit δΓ, δR, δC formulas at the equatorial point
3. Symbolic momentum variables p_μ
4. Rational arithmetic throughout
"""

from fractions import Fraction
import sympy as sp

print("="*70)
print("TEST 5-8: W3 HESSIAN IN MOMENTUM SPACE")
print("="*70)

# ================================================================
# Setup: background quantities
# ================================================================
# Background Weyl tensor (24 non-zero components at equatorial point)
Cbar = {}
def set_Cbar(a,b,c,d,v):
    """Set Cbar with all symmetries."""
    v = Fraction(v)
    for (i,j,k,l),s in [
        ((a,b,c,d),1),((b,a,c,d),-1),((a,b,d,c),-1),((b,a,d,c),1),
        ((c,d,a,b),1),((d,c,a,b),-1),((c,d,b,a),-1),((d,c,b,a),1)
    ]:
        Cbar[(i,j,k,l)] = s*v

set_Cbar(0,1,0,1, Fraction(2,3))
set_Cbar(0,2,0,2, Fraction(-1,3))
set_Cbar(0,3,0,3, Fraction(-1,3))
set_Cbar(1,2,1,2, Fraction(-1,3))
set_Cbar(1,3,1,3, Fraction(-1,3))
set_Cbar(2,3,2,3, Fraction(2,3))

def CB(a,b,c,d): return Cbar.get((a,b,c,d), Fraction(0))

# Verify W3 = 32/9
W3_check = sum(CB(a,b,c,d)*CB(c,d,e,f)*CB(e,f,a,b)
               for a in range(4) for b in range(4) for c in range(4)
               for d in range(4) for e in range(4) for f in range(4))
print(f"\nBackground W3 = {W3_check}  (expected 32/9: {W3_check == Fraction(32,9)})")
assert W3_check == Fraction(32,9), "Background W3 check failed"

# Background Ricci and scalar curvature
def Rbar_low(a,b,c,d):
    """Background Riemann tensor (lowered)."""
    for (i,j,k,l),s in [
        ((0,1,0,1),1),((0,1,1,0),-1),((1,0,0,1),-1),((1,0,1,0),1),
        ((2,3,2,3),1),((2,3,3,2),-1),((3,2,2,3),-1),((3,2,3,2),1)
    ]:
        if (a,b,c,d) == (i,j,k,l): return Fraction(s)
    return Fraction(0)

def Ric_bar(a,b):
    """Background Ricci tensor = g_{ab} at equatorial point."""
    return Fraction(1) if a==b else Fraction(0)

R_scalar_bar = Fraction(4)

# ================================================================
# Momentum variables
# ================================================================
# Use symbolic momenta p_0, p_1, p_2, p_3
p = sp.symbols('p0 p1 p2 p3')

# ================================================================
# h_{μν}: the 10 independent components of symmetric h
# ================================================================
# Use symbolic variables H[mu][nu] = H[nu][mu]
H_sym = {}
for a in range(4):
    for b in range(a, 4):
        H_sym[(a,b)] = sp.Symbol(f'H{a}{b}')
        H_sym[(b,a)] = H_sym[(a,b)]

def H(a,b): return H_sym[(a,b)]

# ================================================================
# Step 1: δΓ^k_{ij} in momentum space
# At equatorial point Γ̄=0, so:
# δΓ^k_{ij} = (i/2)(p_i h_{jk} + p_j h_{ik} - p_k h_{ij})
# In real space with h = H e^{ip·x}, derivatives ∂_μ → ip_μ
# So δΓ^k_{ij} = (i/2)(p_i H_{jk} + p_j H_{ik} - p_k H_{ij}) · [e^{ip·x} factor]
# We extract the amplitude (dropping the e^{ip·x}).
# ================================================================
print("\n--- Computing δΓ (momentum space) ---")

def dGamma(k, i, j):
    """δΓ^k_{ij} amplitude (coefficient of e^{ipx}).
    = (i/2)(p_i H_{jk} + p_j H_{ik} - p_k H_{ij})
    We factor out 'i' and track it separately.
    Return the 'real' part (coeff of i): (1/2)(p_i H_{jk} + p_j H_{ik} - p_k H_{ij})
    """
    return sp.Rational(1,2) * (p[i]*H(j,k) + p[j]*H(i,k) - p[k]*H(i,j))

# ================================================================
# Step 2: δR^k_{lij} in momentum space
# At Γ̄=0:
# δR^k_{lij} = ∂_i δΓ^k_{lj} - ∂_j δΓ^k_{li}
#            = ip_i * δΓ^k_{lj} - ip_j * δΓ^k_{li}   [∂ → ip]
# Factor of i² = -1 from two derivatives:
# δR_klij = (∂_i δΓ^k_{lj} - ∂_j δΓ^k_{li})
# In momentum space the 'i' factors: δΓ ~ i·(linear in p, H)
# So δR ~ i * (ip) * (linear in p,H) = -1 * (quadratic in p) * H
# 
# More precisely: δΓ^k_{lj} = (i/2)(p_l H_{jk} + p_j H_{lk} - p_k H_{lj})
# ∂_i δΓ^k_{lj} = ip_i * δΓ^k_{lj} = (i)²/2 * p_i(p_l H_{jk}+p_j H_{lk}-p_k H_{lj})
#               = -(1/2) p_i(p_l H_{jk}+p_j H_{lk}-p_k H_{lj})
# 
# So δR^k_{lij} = -(1/2)[p_i(p_l H_{jk}+p_j H_{lk}-p_k H_{lj})
#                        - p_j(p_l H_{ik}+p_i H_{lk}-p_k H_{li})]
# Let's code this up (returning real amplitude, with -1 from i²).
# ================================================================
print("--- Computing δR (momentum space) ---")

def dR_upper(k, l, i, j):
    """δR^k_{lij} amplitude in momentum space.
    Returns the coefficient (no i factors, they give -1 overall).
    """
    # ∂_i δΓ^k_{lj} = ip_i * dGamma(k,l,j)  → contributes ip_i * (i * ...) = -p_i * ...
    # where dGamma already has the (1/2) and is "without i"
    # So: ∂_i dGamma(k,l,j) → ip_i * (i * dGamma) → -p_i * dGamma_amplitude
    # Wait, I need to be careful about factors of i.
    
    # Let me redo cleanly. In momentum space:
    # h_{μν}(x) = H_{μν} e^{ipx}
    # δΓ^k_{lj}(x) = (i/2)(p_l H_{jk} + p_j H_{lk} - p_k H_{lj}) e^{ipx}
    #              = i * G(k,l,j) * e^{ipx}
    # where G(k,l,j) = (1/2)(p_l H_{jk} + p_j H_{lk} - p_k H_{lj}) is real
    
    # ∂_i δΓ^k_{lj} = ip_i * δΓ^k_{lj} = i*ip_i * G(k,l,j) * e^{ipx} = -p_i G(k,l,j) e^{ipx}
    
    # So: δR^k_{lij} = (∂_i δΓ^k_{lj} - ∂_j δΓ^k_{li}) * e^{ipx}
    #                 = (-p_i G(k,l,j) + p_j G(k,l,i)) * e^{ipx}
    
    G_klj = dGamma(k, l, j)  # = (1/2)(p_l H_{jk} + p_j H_{lk} - p_k H_{lj})
    G_kli = dGamma(k, l, i)  # = (1/2)(p_l H_{ik} + p_i H_{lk} - p_k H_{li})
    
    return -p[i]*G_klj + p[j]*G_kli

def dR_lower(a, b, c, d):
    """δR_{abcd} = ḡ_{ae} δR^e_{bcd} (since ḡ=I, this is δR^a_{bcd})."""
    return dR_upper(a, b, c, d)

# ================================================================
# Step 3: δR_{ab} (Ricci) and δR (scalar)
# δR_{ab} = g^{cd} δR_{cadb} = δR^c_{acb}  [at ḡ=I]
# ================================================================
print("--- Computing δRicci, δR_scalar ---")

def dRicci(a, b):
    """δR_{ab} = sum_c δR^c_{acb}."""
    return sum(dR_upper(c, a, c, b) for c in range(4))

def dR_scalar():
    """δR = g^{ab} δR_{ab} = sum_a δR_{aa}."""
    return sum(dRicci(a, a) for a in range(4))

# ================================================================
# Step 4: δ²R_{abcd} (second order in h)
# At Γ̄=0:
# δ²R^k_{lij} = δΓ^k_{im} δΓ^m_{lj} - δΓ^k_{jm} δΓ^m_{li}
# Each δΓ ~ i*G, so δΓ·δΓ ~ i²*G² = -G²
# ================================================================
print("--- Computing δ²R (second order) ---")

def d2R_upper(k, l, i, j):
    """δ²R^k_{lij} amplitude (second order in H).
    = δΓ^k_{im}δΓ^m_{lj} - δΓ^k_{jm}δΓ^m_{li}
    Each δΓ has a factor of i, so product has i²=-1.
    """
    result = sp.Integer(0)
    for m in range(4):
        G_kim = dGamma(k, i, m)  # amplitude of δΓ^k_{im}
        G_mlj = dGamma(m, l, j)  # amplitude of δΓ^m_{lj}
        G_kjm = dGamma(k, j, m)  # amplitude of δΓ^k_{jm}
        G_mli = dGamma(m, l, i)  # amplitude of δΓ^m_{li}
        result += G_kim * G_mlj - G_kjm * G_mli
    return -result  # -1 from i²

def d2R_lower(a, b, c, d):
    """δ²R_{abcd} = ḡ_{ae} δ²R^e_{bcd} = δ²R^a_{bcd} at ḡ=I."""
    return d2R_upper(a, b, c, d)

def d2Ricci(a, b):
    """δ²R_{ab} includes both: g^{cd}δ²R_{cadb} and (-h^{cd})δR_{cadb}."""
    # Full expression: δ²R_{ab} = δ(δR_{ab}) = δ(g^{cd}δR_{cadb})
    # = (-h^{cd})R̄_{cadb} + ḡ^{cd}δ²R_{cadb} + additional terms from δΓ·δΓ
    # At first order: δR_{ab} = g^{cd}δR_{cadb}|_0
    # At second order: δ²R_{ab} = sum_c d2R_upper(c,a,c,b) + (-h^{cd})R̄_{cadb}
    result = sum(d2R_upper(c, a, c, b) for c in range(4))
    # Plus the metric correction: -h^{cd} * R̄_{cadb}
    for c in range(4):
        for d_idx in range(4):
            result += -H(c,d_idx) * Rbar_low(c, a, d_idx, b)
    return result

def d2R_scalar():
    """δ²R = δ²(g^{ab}R_{ab}) at ε=0.
    = h^{ab}h^{cd}R̄_{abcd} - h^{ab}δR_{ab}|_0 - h^{ab}δR_{ab}|_0 
      + g^{ab}δ²R_{ab}|_0
    Actually: δ²R = -h^{ac}h_{c}^b R̄_{ab} + h^{ab}h^{cd}... (complex)
    Let me use the simpler: δ²R = sum_a d2Ricci_corrected(a,a) 
    including h-inverse correction.
    """
    # Full: (g_0+εg_1)^{ab}(R0+εR1+ε²R2)_{ab} expanded to ε²
    # g^{ab}(ε) = δ^{ab} - εh^{ab} + ε²(h²)^{ab}
    # So δ²R = sum_ab [-(h²)^{ab}(-1) * R̄_{ab} ... ]
    # Let me use trace formula directly:
    # δ²R = g^{(2)ab}R̄_{ab} + 2*g^{(1)ab}δR_{ab} + g^{(0)ab}δ²R_{ab}
    # = sum_a [(h²)_{aa} * 1 - 2*h_{ab}*δR_{ab}^{b} + δ²R_{aa}]
    
    # (h²)^{ab} = sum_c H(a,c)*H(c,b)
    # g^{(2)ab} = +(h²)^{ab}  (second order inverse metric coefficient)
    
    result = sp.Integer(0)
    # g^{(2)} * Rbar term
    for a in range(4):
        for b in range(4):
            h2_ab = sum(H(a,c)*H(c,b) for c in range(4))
            result += h2_ab * Ric_bar(a,b)
    # 2*g^{(1)} * δR term
    for a in range(4):
        for b in range(4):
            result += 2*(-H(a,b))*dRicci(a,b)
    # g^{(0)} * δ²R term
    for a in range(4):
        for b in range(4):
            result += d2Ricci(a,b) * (1 if a==b else 0)
    
    return result

# ================================================================
# Step 5: δC_{abcd} (first order)
# δC_{abcd} = δR_{abcd} 
#           - (1/2)(h_{ac}R̄_{bd} - h_{ad}R̄_{bc} - h_{bc}R̄_{ad} + h_{bd}R̄_{ac})
#           - (1/2)(ḡ_{ac}δR_{bd} - ḡ_{ad}δR_{bc} - ḡ_{bc}δR_{ad} + ḡ_{bd}δR_{ac})
#           + (1/6)(δR)(ḡ_{ac}ḡ_{bd}-ḡ_{ad}ḡ_{bc})
#           + (1/6)R̄(h_{ac}ḡ_{bd}+ḡ_{ac}h_{bd}-h_{ad}ḡ_{bc}-ḡ_{ad}h_{bc})
# At ḡ=I, R̄_{ab}=δ_{ab}, R̄=4:
# ================================================================
print("--- Computing δC (first order) ---")

def dC(a, b, c, d):
    """First order Weyl tensor perturbation δC_{abcd}."""
    dR_ab = dR_lower(a, b, c, d)
    
    # Schouten contribution with h (from g variation of metric in Weyl formula)
    g_ac = 1 if a==c else 0
    g_ad = 1 if a==d else 0
    g_bc = 1 if b==c else 0
    g_bd = 1 if b==d else 0
    
    # Variation from h in the metric terms (R̄_{ab} = δ_{ab} at our point):
    schouten_h = sp.Rational(1,2)*(
        H(a,c)*Ric_bar(b,d) - H(a,d)*Ric_bar(b,c)
        - H(b,c)*Ric_bar(a,d) + H(b,d)*Ric_bar(a,c)
    )
    
    # Variation from δR in the Schouten:
    dR_bd = dRicci(b,d); dR_bc = dRicci(b,c)
    dR_ad = dRicci(a,d); dR_ac = dRicci(a,c)
    schouten_dR = sp.Rational(1,2)*(
        g_ac*dR_bd - g_ad*dR_bc - g_bc*dR_ad + g_bd*dR_ac
    )
    
    # Variation from δR in the R term:
    dR_scal = dR_scalar()
    trace_g = sp.Rational(1,6)*dR_scal*(g_ac*g_bd - g_ad*g_bc)
    
    # Variation from h in the R·g·g term (R̄=4):
    trace_h = sp.Rational(1,6)*R_scalar_bar*(
        H(a,c)*g_bd + g_ac*H(b,d) - H(a,d)*g_bc - g_ad*H(b,c)
    )
    
    return dR_ab - schouten_h - schouten_dR + trace_g + trace_h

# ================================================================
# Step 6: Build the W3 second variation
# W3[g+εh] = C̄·C̄·C̄ + ε·3·δC·C̄·C̄ + ε²·[3·δ²C·C̄·C̄ + 6·δC·δC·C̄] + ...
# (using symmetry of the cubic under permutation of the three C's)
# 
# The Hessian density (ε² coefficient of √g · W3[g+εh]) is:
# H_density = 3·δ²C_{abcd}·C̄^{cdef}·C̄_{ef}^{ab}
#           + 6·δC_{abcd}·δC^{cdef}·C̄_{ef}^{ab}   [from W3 variation]
#           + (1/4(trh)² - 1/2 tr(h²))·W̄3           [from √g variation]
#           + 2·(trh/2)·3·δC_{abcd}·C̄^{cdef}·C̄_{ef}^{ab} [cross term]
# 
# We focus on the KINETIC PART (terms with two derivatives of h = two powers of p)
# which comes from the δC·δC·C̄ term.
# ================================================================
print("--- Computing W3 second variation ---")
print("(Computing the kinetic kernel: δC·δC·C̄ term)")
print("This is the leading-derivative piece of the Hessian.")
print()

# The kinetic contribution: 6 * δC_{abcd} δC_{cdef} C̄_{efab}
# where each δC contains one derivative of h (→ one factor of p in momentum space)
# So this term is quadratic in both p and H.

# Let's compute this term explicitly for specific components.
# Instead of computing the full 10×10 Hessian symbolically (which would be slow),
# we use the finite-basis reconstruction method.
# 
# The quadratic form Q(h) = 6 ∫ δC_{abcd}[h] δC_{cdef}[h] C̄_{efab} d⁴x
# in momentum space (for single Fourier mode) is:
# Q(H,p) = 6 Σ_{abcdef} δC_{abcd}[H,p] * δC_{cdef}[H,p] * C̄_{efab}

# For the TT-projected Hessian, we want the coefficient of p² H^{TT}² in Q(H,p).
# But first let's compute Q(H,p) for general H and specific p.

# Choose p = (0, 0, 0, p_0) → p_3 = p, all others 0 (momentum along direction 3)
# This is a legitimate choice since we want the p-dependence.

print("Computing Q(H,p) with p = (0,0,0,p) (momentum in direction 3)...")
print("Using the 10-basis vector reconstruction method.")
print()

# Set up: p = (0, 0, 0, t) where t is a symbol
t = sp.Symbol('t', positive=True)
p_vec = [sp.Integer(0), sp.Integer(0), sp.Integer(0), t]
# Override the global p
p_save = p
p = p_vec

# Basis vectors for h_{μν}: e^{(ij)} with H_{ab} = δ_{a,i}δ_{b,j}+δ_{a,j}δ_{b,i} (for i<j) 
# or δ_{a,i}δ_{b,i} (for i=j)
# 10 basis vectors total for 4x4 symmetric matrix

basis_labels = [(0,0),(1,1),(2,2),(3,3),(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]

def make_H_basis(mu, nu):
    """Return H symbol for basis element e^{(mu,nu)}."""
    H_dict = {}
    for a in range(4):
        for b in range(4):
            H_dict[(a,b)] = sp.Integer(0)
    H_dict[(mu,nu)] = sp.Integer(1)
    H_dict[(nu,mu)] = sp.Integer(1)
    return H_dict

# To compute the Hessian matrix M_{(ij),(kl)} we use:
# M_{(ij),(kl)} = [Q(e^{(ij)} + e^{(kl)}) - Q(e^{(ij)}) - Q(e^{(kl)})] / 2
# where Q(h) is the quadratic form evaluated on basis vector h

def compute_dC_basis(basis_H_dict, p_vec):
    """Compute δC_{abcd} for a specific h given as a dict and momentum p."""
    p_loc = p_vec
    results = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    # Override H to use basis_H_dict
                    val = dC_with_H(a,b,c,d, basis_H_dict, p_loc)
                    if val != 0:
                        results[(a,b,c,d)] = val
    return results

def dC_with_H(a, b, c, d, Hd, p_loc):
    """δC_{abcd} with H replaced by Hd dictionary and p replaced by p_loc."""
    def H_loc(i,j): return Hd.get((i,j), sp.Integer(0))
    def p_loc_fn(i): return p_loc[i]
    
    # δΓ^k_{ij}
    def dG(k, i, j):
        return sp.Rational(1,2)*(p_loc_fn(i)*H_loc(j,k) + p_loc_fn(j)*H_loc(i,k) - p_loc_fn(k)*H_loc(i,j))
    
    # δR^k_{lij}
    def dR_up(k,l,i,j):
        G_klj = dG(k,l,j)
        G_kli = dG(k,l,i)
        return -p_loc_fn(i)*G_klj + p_loc_fn(j)*G_kli
    
    def dR_lo(a,b,c,d):
        return dR_up(a,b,c,d)
    
    def dRic(a,b):
        return sum(dR_up(c,a,c,b) for c in range(4))
    
    def dRsc():
        return sum(dRic(a,a) for a in range(4))
    
    g_ac = 1 if a==c else 0
    g_ad = 1 if a==d else 0
    g_bc = 1 if b==c else 0
    g_bd = 1 if b==d else 0
    
    result = dR_lo(a,b,c,d)
    result -= sp.Rational(1,2)*(
        H_loc(a,c)*Ric_bar(b,d) - H_loc(a,d)*Ric_bar(b,c)
        - H_loc(b,c)*Ric_bar(a,d) + H_loc(b,d)*Ric_bar(a,c)
    )
    result -= sp.Rational(1,2)*(
        g_ac*dRic(b,d) - g_ad*dRic(b,c) - g_bc*dRic(a,d) + g_bd*dRic(a,c)
    )
    result += sp.Rational(1,6)*dRsc()*(g_ac*g_bd - g_ad*g_bc)
    result += sp.Rational(1,6)*R_scalar_bar*(
        H_loc(a,c)*g_bd + g_ac*H_loc(b,d) - H_loc(a,d)*g_bc - g_ad*H_loc(b,c)
    )
    return result

# ================================================================
# Compute the KINETIC quadratic form
# Q_kinetic(H) = 6 * Σ_{abcdef} δC_{abcd}[H] δC_{cdef}[H] C̄_{efab}
# ================================================================
print("Computing Q_kinetic for all 10 basis vectors...")

def compute_Q_kinetic(H_dict, p_loc):
    """Compute 6 * sum_{abcdef} δC_{abcd} * δC_{cdef} * C̄_{efab}."""
    # First compute all δC components
    dC_vals = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    v = dC_with_H(a,b,c,d, H_dict, p_loc)
                    v = sp.expand(v)
                    if v != 0:
                        dC_vals[(a,b,c,d)] = v
    
    # Now compute the contraction
    result = sp.Integer(0)
    for (a,b,c,d), v1 in dC_vals.items():
        for (c2,d2,e,f), v2 in dC_vals.items():
            if (c2,d2) != (c,d): continue  # need c2=c, d2=d
            cb_ef_ab = CB(e,f,a,b)
            if cb_ef_ab == 0: continue
            result += 6 * v1 * v2 * cb_ef_ab
    
    return sp.expand(result)

# Compute Q for each basis vector
print("Computing diagonal entries Q(e^{ij},e^{ij})...")
Q_diag = {}
for (i,j) in basis_labels:
    H_dict = make_H_basis(i,j)
    Q = compute_Q_kinetic(H_dict, p_vec)
    Q_diag[(i,j)] = sp.collect(sp.expand(Q), t)
    print(f"  Q(e^{{{i}{j}}}) = {Q_diag[(i,j)]}")

print()
print("Extracting p² coefficients (coefficient of t²)...")
print()

def get_t2_coeff(expr):
    """Extract coefficient of t² from a polynomial in t."""
    p_poly = sp.Poly(sp.expand(expr), t)
    coeffs = p_poly.all_coeffs()
    degree = p_poly.degree()
    if degree < 2:
        return sp.Integer(0)
    # coeffs are from highest to lowest degree
    # coefficient of t^2 is at position degree-2 from start
    idx = degree - 2
    if idx < 0 or idx >= len(coeffs):
        return sp.Integer(0)
    return coeffs[idx]

print("t² (kinetic) coefficients of Q(e^{ij}):")
for (i,j) in basis_labels:
    c2 = get_t2_coeff(Q_diag[(i,j)])
    print(f"  Q_kinetic[{i}{j},{i}{j}] = {c2}")
