# Canonical Numerical Instance — SXC-IGC (REFERENCE)

This file defines the **reference numerical instantiation** of the SXC-IGC law.
It is not a physical claim. It is an execution standard.

---

## 1. Time Discretization

Discrete-time Euler integration:

x_{t+1} = x_t + Δt · f(x_t) + η_t

Δt controls numerical stability only.

Constraint:

Δt · max |f′(x)| < 1 over explored state range.

---

## 2. Reference Step Size

Δt = 0.05

Chosen to ensure stability for:
- |x| = O(1)
- r ≈ 0.15
- a, b = O(1)

---

## 3. Reference Parameters

r = 0.153267  
a = 1.0  
b = 1.0  

These values define the canonical operating point.

---

## 4. Noise Model

η_t ~ 𝒩(0, σ²)

Constraints:
- σ ≪ Δt · max |f(x)| within metastable basin
- σ > 0 to allow stochastic tipping

Noise is additive only.

---

## 5. Minimal Canonical Instance

x_{t+1} = x_t + 0.05 ( 0.153267 x_t + x_t² − x_t³ ) + η_t

This equation fully specifies the **reference SXC-IGC engine**.

---

## 6. Control Parameters (Meta-Layer)

These modify experiments, not governing law:

- Parameter drift: r(t), a(t), b(t)
- Noise scheduling: σ(t)
- Boundary policy: reflecting / absorbing
- Initialization ensemble: distribution of x₀

---

## 7. Valid Operating Regime

Interpretability requires:

- r > 0
- a ≠ 0
- b > 0
- σ small but nonzero
- Δt stable under Euler integration

Outside this regime, numerical output is not physically meaningful.

