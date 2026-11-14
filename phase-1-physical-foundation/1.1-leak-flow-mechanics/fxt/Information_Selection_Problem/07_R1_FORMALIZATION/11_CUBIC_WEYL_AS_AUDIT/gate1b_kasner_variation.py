#!/usr/bin/env python3
"""
GATE 1B: Complete Euler-Lagrange tensor for W3 action on vacuum Kasner.

Computes E_{mu nu} = (1/sqrt(-g)) * delta(sqrt(-g)*W3) / delta g_{mu nu}
for the cubic Weyl action W3 = C_{abcd} C^{ab}_{ef} C^{cdef} on Kasner spacetime.

Method: Full Euler-Lagrange formula for spatially homogeneous metric:
    E_{mm} = (1/sqrt(-g)) * [dL/da - d/dt(dL/da') + d^2/dt^2(dL/da'')]
where a(t) = g_{mm}(t) is the varied metric component and L = sqrt(-g)*W3.

This captures ALL contributions including derivative terms.

Control test: Same machinery applied to C2 = int sqrt(g) C^2 gives Bach=0 on Kasner.

Results:
    E_11 = E_22 = 3968/(243 t^{22/3})   [NONZERO]
    E_33 = 6272/(243 t^{16/3})           [NONZERO]
    Bach_11 = Bach_22 = Bach_33 = 0      [control, C2 action]

Gate 1B: PASSED
"""

import sympy as sp
from sympy import Function, diff, simplify, expand, Rational, sqrt

t = sp.Symbol('t', positive=True)


def compute_EL_component(vary_idx, P_vals, action='W3'):
    """
    Compute the (vary_idx, vary_idx) diagonal EL component on Kasner.

    Parameters
    ----------
    vary_idx : int
        Spatial component to vary: 1, 2, or 3.
    P_vals : list of 3 sympy Rationals
        Kasner exponents [p1, p2, p3].
    action : str
        'W3' for cubic Weyl action, 'C2' for quadratic Weyl action (Bach tensor).
    """
    p = P_vals
    a = Function('a')(t)  # the varied g_{vary_idx, vary_idx}

    def g_dn(mu, nu):
        if mu != nu: return sp.Integer(0)
        if mu == 0: return sp.Integer(-1)
        if mu == vary_idx: return a
        return t ** (2 * p[mu - 1])

    def g_up(mu, nu):
        if mu != nu: return sp.Integer(0)
        if mu == 0: return sp.Integer(-1)
        if mu == vary_idx: return 1 / a
        return t ** (-2 * p[mu - 1])

    def Chr(upper, al, be):
        result = sp.Integer(0)
        for k in range(4):
            guk = g_up(upper, k)
            if guk == 0: continue
            term = sp.Integer(0)
            if al == 0: term += diff(g_dn(k, be), t)
            if be == 0: term += diff(g_dn(k, al), t)
            if k == 0:  term -= diff(g_dn(al, be), t)
            if term != 0:
                result += Rational(1, 2) * guk * term
        return result

    def Rup(rho, sig, mu, nu):
        result = sp.Integer(0)
        if mu == 0: result += diff(Chr(rho, nu, sig), t)
        if nu == 0: result -= diff(Chr(rho, mu, sig), t)
        for lam in range(4):
            t1 = expand(Chr(rho, mu, lam))
            t2 = expand(Chr(lam, nu, sig))
            if t1 != 0 and t2 != 0: result += t1 * t2
            t3 = expand(Chr(rho, nu, lam))
            t4 = expand(Chr(lam, mu, sig))
            if t3 != 0 and t4 != 0: result -= t3 * t4
        return result

    def Rdn(al, be, ga, de):
        res = sp.Integer(0)
        for e in range(4):
            if g_dn(al, e) == 0: continue
            res += g_dn(al, e) * Rup(e, be, ga, de)
        return expand(res)

    # Cache nonzero Riemann components
    R_cache = {}
    for al in range(4):
        for be in range(4):
            for ga in range(4):
                for de in range(4):
                    v = Rdn(al, be, ga, de)
                    if v != 0:
                        R_cache[(al, be, ga, de)] = v

    if action == 'W3':
        # W3 = C_{abcd} C^{ab}_{ef} C^{cdef} using C=R (vacuum)
        scalar = sp.Integer(0)
        for (a_, b_, c_, d_), v1 in R_cache.items():
            ga = g_up(a_, a_); gb = g_up(b_, b_)
            for e_ in range(4):
                for f_ in range(4):
                    v2 = R_cache.get((a_, b_, e_, f_), sp.Integer(0))
                    if v2 == 0: continue
                    ge = g_up(e_, e_); gf = g_up(f_, f_)
                    gc = g_up(c_, c_); gd = g_up(d_, d_)
                    v3 = R_cache.get((c_, d_, e_, f_), sp.Integer(0))
                    if v3 == 0: continue
                    scalar += expand(v1 * (ga * gb * v2) * (gc * gd * ge * gf * v3))
    elif action == 'C2':
        # C2 = C_{abcd} C^{abcd}
        scalar = sp.Integer(0)
        for (a_, b_, c_, d_), v1 in R_cache.items():
            ga = g_up(a_, a_); gb = g_up(b_, b_)
            gc = g_up(c_, c_); gd = g_up(d_, d_)
            v2 = R_cache.get((a_, b_, c_, d_), sp.Integer(0))
            if v2 == 0: continue
            scalar += expand(v1 * ga * gb * gc * gd * v2)

    scalar = expand(scalar)

    # sqrt(-g) for diagonal metric
    others = [t ** (2 * p[i]) for i in range(3) if i != vary_idx - 1]
    sqrtg = sqrt(a * others[0] * others[1])
    L = expand(sqrtg * scalar)

    # Euler-Lagrange
    ap = diff(a, t)
    app = diff(a, t, 2)
    EL = expand(diff(L, a) - diff(diff(L, ap), t) + diff(diff(L, app), t, 2))

    # Substitute Kasner background
    a0 = t ** (2 * p[vary_idx - 1])
    subs = [(app, diff(a0, t, 2)), (ap, diff(a0, t)), (a, a0)]
    EL_bg = simplify(EL.subs(subs))

    sqrtg_bg = simplify(sqrt(t ** (2 * p[0]) * t ** (2 * p[1]) * t ** (2 * p[2])))
    return simplify(EL_bg / sqrtg_bg)


if __name__ == '__main__':
    P = [Rational(2, 3), Rational(2, 3), Rational(-1, 3)]
    print(f"Kasner p = {P}")
    print(f"  sum = {sum(P)},  sum of squares = {sum(x**2 for x in P)}")

    print("\n" + "=" * 60)
    print("W3 EL TENSOR E_{mu nu} on Kasner")
    print("=" * 60)
    for idx in [1, 2, 3]:
        print(f"Computing E_{idx}{idx}...", end=' ', flush=True)
        E = compute_EL_component(idx, P, action='W3')
        status = "NONZERO" if E != 0 else "ZERO"
        print(f"E_{idx}{idx} = {E}  [{status}]")

    print("\n" + "=" * 60)
    print("CONTROL: C2 BACH TENSOR on Kasner (should be zero)")
    print("=" * 60)
    all_zero = True
    for idx in [1, 2, 3]:
        print(f"Computing Bach_{idx}{idx}...", end=' ', flush=True)
        B = compute_EL_component(idx, P, action='C2')
        status = "ZERO ✓" if B == 0 else "NONZERO ✗ (ERROR!)"
        print(f"Bach_{idx}{idx} = {B}  [{status}]")
        if B != 0:
            all_zero = False

    print()
    if all_zero:
        print("Control: Bach=0 on Kasner confirmed ✓")
        print("GATE 1B: PASSED — W3 EL tensor is NONZERO on Kasner")
    else:
        print("ERROR: Control test failed — Bach != 0 (check the computation)")
