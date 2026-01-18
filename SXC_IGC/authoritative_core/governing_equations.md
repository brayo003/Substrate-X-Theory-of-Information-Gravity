# Governing Equations — SXC-IGC (AUTHORITATIVE LAW)

## 1. State Variable

x(t) ∈ ℝ

Scalar system excitation / instability coordinate.

Interpretation:
- x > 0  : amplifying stress
- x < 0  : dissipative relaxation
- x ≈ 0  : metastable equilibrium (not safe for r > 0)

x(t) is dimensionless after normalization.

---

## 2. Canonical Deterministic Dynamics

The SXC-IGC engine is defined by a first-order nonlinear instability equation:

dx/dt = f(x)

with drift function:

f(x) = r x + a x² − b x³

All three terms are mandatory.

---

## 3. Parameter Semantics

r : linear growth / background instability  
a : quadratic asymmetry / directional bias  
b : cubic saturation / structural constraint  

Constraints:
- r > 0   (latent instability exists)
- b > 0   (bounded dynamics)
- a ≠ 0   (symmetry breaking allowed)

---

## 4. Fixed Points

Equilibria satisfy:

f(x) = 0  
x ( r + a x − b x² ) = 0

Solutions:

x₀ = 0  

x± = ( a ± √(a² + 4 b r) ) / (2 b)

---

## 5. Stability Criterion

Stability is determined by:

f′(x) = r + 2 a x − 3 b x²

- f′(x) < 0 → stable
- f′(x) > 0 → unstable

For r > 0:
- x = 0 is unstable
- one nonzero branch is stable
- one nonzero branch is unstable

---

## 6. Stochastic Extension (Optional)

Additive noise may be included:

dx/dt = f(x) + η(t)

where:

η(t) is zero-mean noise with finite variance.

Noise modifies transition probability, not fixed-point structure.

Multiplicative noise is excluded from the canonical model.

---

## 7. Scope and Non-Claims

- This is a phenomenological instability normal form.
- No claim of first-principles universality.
- Physical meaning of x(t) is domain-dependent and defined elsewhere.

This document defines law.  
Numerical choices are defined separately.

