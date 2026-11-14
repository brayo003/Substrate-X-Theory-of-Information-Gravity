# CONVERSION-EXTENDED PRW DERIVATION
## Energy-Information Conversion: Microscopic Origin of the αE Term

**Date:** 2026-08-22  
**Status:** Working derivation — all steps exact unless labelled [APPROX] or [OPEN]  
**Supersedes:** SUBSTRATE_CLOSURE_REPORT.md (which made one unjustified approximation)

---

## 0. Correction to Previous Report

`SUBSTRATE_CLOSURE_REPORT.md` claimed that `E = Ω₀s` is a "derived, not assumed" closure. That claim was too strong. The derivation silently dropped the spatial transport terms `c∂ₓΩ±` and the nonlinearity `n⁻/n⁺` in the Ω equations, reducing a spatiotemporal PDE system to a set of ODEs. The corrected statement is:

> The closure `E = Ω₀s` holds **only** for the source-free (α=0) elastic PRW with initially uniform Ω fields, near equilibrium.

For the driven system with αE sources, a new microscopic mechanism must be specified. That is the subject of this document.

---

## 1. The Core Inconsistency in the Original Master Equation

The original master equation contains:
```
∂ₜs + ∂ₓJ = αE + ...
```

But the PRW microscopics give exactly:
```
∂ₜs + ∂ₓJ = 0   (source-free)
```

These are different systems. The αE term requires a microscopic process in which **energy is converted into information at rate αE**. Without specifying that process, αE is purely phenomenological. The previous audit identified this as the fundamental incompleteness of the substrate.

---

## 2. The Conversion-Extended PRW

### 2.1 Microscopic State

Each site carries four fields:

| Field | Units | Meaning |
|-------|-------|---------|
| n⁺(x,t) | info/m³ | Right-mover information density |
| n⁻(x,t) | info/m³ | Left-mover information density |
| e⁺(x,t) | J/m³ | Right-mover energy density |
| e⁻(x,t) | J/m³ | Left-mover energy density |

### 2.2 Microscopic Evolution (Exact)

Introduce conversion rates C±(e,n) [info/(m³·s)] and energy removal rates Q±(e,n) [J/(m³·s)]:

```
∂ₜn⁺ + c∂ₓn⁺ = -λ(n⁺ - n⁻) + C⁺(e,n)     [n+]
∂ₜn⁻ - c∂ₓn⁻ = +λ(n⁺ - n⁻) + C⁻(e,n)     [n-]
∂ₜe⁺ + c∂ₓe⁺ = -λ(e⁺ - e⁻) - Q⁺(e,n)     [e+]
∂ₜe⁻ - c∂ₓe⁻ = +λ(e⁺ - e⁻) - Q⁻(e,n)     [e-]
```

### 2.3 The Conservation Constraint

Define the total substrate budget:
```
Q_total = ∫ [E + ε₀ s] dx
```
where ε₀ [J/info] is the energy cost per information quantum.

**Claim:** dQ_total/dt = 0 if and only if Q± = ε₀ C±.

**Proof:** 
```
dQ/dt = ∫ [∂ₜE + ε₀ ∂ₜs] dx
      = ∫ [-∂ₓP - (Q⁺+Q⁻) + ε₀(-∂ₓJ + C⁺+C⁻)] dx
```
Boundary terms vanish. Remaining:
```
dQ/dt = ∫ [ε₀(C⁺+C⁻) - (Q⁺+Q⁻)] dx = 0  iff  Q± = ε₀ C±
```

The conservation law is satisfied for **any** C±(e,n), provided Q± = ε₀C±. Conservation alone does not determine the functional form of C±.

### 2.4 Minimal Conversion Mechanism

Dimensional requirements:
- [C±] = info/(m³·s)
- [e±] = J/m³, [α] = info/(J·s)
- [α e±] = info/(m³·s) ✓

The **minimal local linear mechanism** is:
```
C⁺(e,n) = α e⁺        [creation rate proportional to right-mover energy]
C⁻(e,n) = α e⁻        [creation rate proportional to left-mover energy]
Q⁺(e,n) = ε₀ α e⁺     [energy cost, right]
Q⁻(e,n) = ε₀ α e⁻     [energy cost, left]
```

This is the microscopic realization of the master equation's αE source term:
```
C⁺ + C⁻ = α(e⁺+e⁻) = αE  ✓
```

---

## 3. Coarse-Graining to Macroscopic Fields (Exact)

Define: s = n⁺+n⁻, J = c(n⁺−n⁻), E = e⁺+e⁻, P = c(e⁺−e⁻).

**Add n-equations:**
```
∂ₜs + ∂ₓJ = α(e⁺+e⁻) = αE                        [S]
```

**Subtract n-equations (×c):**
```
∂ₜJ + c²∂ₓs = -(1/τ)J + α·c(e⁺-e⁻) = -(1/τ)J + αP   [J]
```

**Add e-equations:**
```
∂ₜE + ∂ₓP = -ε₀α(e⁺+e⁻) = -ε₀αE                  [E]
```

**Subtract e-equations (×c):**
```
∂ₜP + c²∂ₓE = -(1/τ)P - ε₀α·c(e⁺-e⁻) = -(1/τ+ε₀α)P  [P]
```

### The Exact 4-Field System

```
∂ₜs + ∂ₓJ = αE                                     [S]
∂ₜJ + c²∂ₓs = -(1/τ)J + αP                         [J]  ← NEW
∂ₜE + ∂ₓP = -ε₀αE                                  [E]
∂ₜP + c²∂ₓE = -(1/τ + ε₀α)P                        [P]
```

**No approximation has been made. This is exact given C± = αe±.**

### What is genuinely new

The **original master equation** had:
```
∂ₜJ + c²∂ₓs = -(1/τ)J
```

The **microscopically derived system** has:
```
∂ₜJ + c²∂ₓs = -(1/τ)J + αP
```

The `αP` term — energy flux driving information flux — was **absent from the original master equation**. It arises because conversion of right-mover energy into right-mover information creates a flux imbalance. This is a structural correction to the original formulation.

---

## 4. Structure of the 4-Field System

### 4.1 Block-Triangular Form

The system has lower-left zero block (E,P do not depend on s,J):

```
∂ₜ [s]   [   0    -∂ₓ     α      0    ] [s]
∂ₜ [J] = [-c²∂ₓ  -1/τ    0      α    ] [J]
∂ₜ [E]   [   0     0    -ε₀α   -∂ₓ   ] [E]
∂ₜ [P]   [   0     0   -c²∂ₓ -1/τ-ε₀α] [P]
```

The (E,P) block is **autonomous** — it evolves independently of (s,J).

### 4.2 Dispersion Relations

**Fourier ansatz** s,J,E,P ~ exp(i(kx−ωt)) gives characteristic polynomial:

```
det(M) = det(A_sJ) × det(D_EP) = 0
```

**Information sector** det(A_sJ) = 0:
```
ω² - iω/τ - c²k² = 0
ω_s = i/(2τ) ± √[c²k² - 1/(4τ²)]      [standard telegrapher — unchanged]
```

**Energy sector** det(D_EP) = 0:
```
ω² + i(1/τ + 2ε₀α)ω - c²k² - ε₀α(1/τ + ε₀α) = 0
```
Discriminant: Δ_E = c²k² − 1/(4τ²) (same as information sector — verified algebraically)
```
ω_E = -i(1/(2τ) + ε₀α) ± √[c²k² - 1/(4τ²)]    [telegrapher + extra decay ε₀α]
```

### 4.3 One-Directional Coupling

The coupling is strictly **one-directional**:
```
(E,P) → drives → (s,J)
(s,J) does NOT back-react on (E,P)
```

This means the system can be **solved sequentially**:
1. Solve (E,P) first — autonomous decaying telegrapher
2. Use E(x,t), P(x,t) as known forcing to solve (s,J)

### 4.4 Can E Be Eliminated?

**No.** E evolves dynamically (telegrapher with decay). Attempting to substitute gives 0=0 — s and E are genuinely coupled, but the coupling is non-algebraic (it requires time integration of E).

**However**, because (E,P) is autonomous, the complete solution is:

```
E(x,t) = [solution of decaying telegrapher with IC E(x,0), P(x,0)]
P(x,t) = [same system]

s(x,t) = [solution of forced telegrapher, forced by αE(x,t)]
J(x,t) = [same system, also forced by αP(x,t)]
```

The (s,J) system is a **telegrapher equation with known time-dependent forcing** — solvable by Duhamel's principle / Green's function of the standard telegrapher.

---

## 5. Information Content of the Result

### 5.1 What the derived system contains that the original did not

| Feature | Original ME | Derived 4-field system |
|---------|------------|----------------------|
| ∂ₜs + ∂ₓJ = αE | [A] assumed | [D] derived from C±=αe± |
| ∂ₜJ + c²∂ₓs = -(1/τ)J | [A] assumed | [D] derived — BUT incomplete |
| **∂ₜJ + c²∂ₓs = -(1/τ)J + αP** | ABSENT | [D] derived — new term |
| ∂ₜE + ∂ₓP = -ε₀αE | ABSENT (E was external) | [D] derived |
| ∂ₜP + c²∂ₓE = -(1/τ+ε₀α)P | ABSENT | [D] derived |

The original master equation was **inconsistent**: it had αE as a source for s but did not specify what happened to E. The derived 4-field system is self-consistent: E is consumed at rate ε₀αE, and this consumption drives information creation.

### 5.2 Is this system novel?

The **individual components** are known:
- Two coupled telegraphers with source terms: studied in mathematical physics
- Forced telegrapher (s driven by decaying source E): classical Green's function problem
- Linear decay of E: standard exponential relaxation

The **specific combination** — two telegraphers coupled by a conservation law Q = E + ε₀s, with one-directional αP coupling in the flux equation — does not appear as a named equation in the standard PDE literature. However:

- It is a **linear** system
- All modes are known (telegrapher dispersion with shifted decay)
- The solution method is standard (block-triangular → sequential solution)
- The qualitative behavior (information grows as energy decays) is physically obvious

**Classification: F2** — The derivation correctly closes a gap in the original formulation and identifies a new coupling term (αP in the J equation). The mathematical object is not novel in its dynamics, but the microscopic derivation is cleaner and more honest than what preceded it.

### 5.3 What remains genuinely open

| Open question | Status | What would resolve it |
|--------------|--------|----------------------|
| Nonlinear C±(e,n): what if C± depends on n± too? | [O] | Derive and analyze; could produce density-dependent feedback |
| KL-divergence definition of s | [O] | Explicit derivation of evolution equation for s_KL; might produce nonlinear system |
| Inelastic flip: n⁺→n⁻ changes energy carried | [O] | Modifies the Ω± equations; the E-sector becomes coupled to s-sector (feedback restored) |
| Two-way coupling: C±(e,n) depends on n± | [O] | If C± = αe±·f(n±/n_total), the conservation law becomes f-dependent and the system nonlinear |

The most structurally interesting open question is **two-way coupling**: if conversion depends on the current occupancy n± (e.g., stimulated conversion), then (s,J) feeds back into (E,P) and the one-directional structure breaks. The resulting system would be genuinely coupled in both directions, with the possibility of sustained oscillations, limit cycles, or pattern formation.

---

## 6. Honest Classification Summary

| Claim | Status | Evidence |
|-------|--------|---------|
| E = Ω₀s is a first-principles closure | [F] FALSE | Only valid for α=0, uniform Ω, near equilibrium |
| αE is microscopically justified by C±=αe± | [D] DERIVED | Dimensional analysis + conservation law Q=E+ε₀s |
| αP appears in the J equation | [D] DERIVED | Exact coarse-graining — absent from original ME |
| (s,J,E,P) are irreducibly coupled | [D] DERIVED | Block-triangular structure; E cannot be eliminated |
| The 4-field system produces novel dynamics | [F] FALSE | Linear; all modes are known telegrapher type |
| s = n⁺+n⁻ is Shannon information | [F] FALSE | It is occupation number with unit relabeling |
| KL-divergence s_KL changes the problem | [C] CONDITIONAL | Would introduce nonlinearity; requires derivation |
| Two-way coupling C±(e,n) breaks block structure | [C] CONDITIONAL | Depends on specific form of C±(n); requires derivation |

---

## 7. The Corrected Research Program

The previous program was approximately:
```
PDE → interpretation → simulation
```

The corrected program, starting from what has actually been established:

```
1. SPECIFY microscopic ontology: (n⁺,n⁻,e⁺,e⁻) with conversion C±,Q±
2. IMPOSE conservation: Q± = ε₀ C±  (closes the energy bookkeeping)
3. CHOOSE C±(e,n): this is where physics enters — justify from principles
   Current: C± = αe± (linear, one-way)  →  known linear PDE
   Open:    C± = αe±·g(n±)              →  nonlinear, possibly novel
   Open:    s defined as s_KL           →  nonlinear from the start
4. DERIVE macroscopic equations exactly (no approximation)
5. TEST equivalence to known systems before claiming novelty
6. ANALYZE solutions only after step 5
```

The one step where genuinely new mathematics could enter is step 3 — the choice of C±(e,n) guided by a physical principle that is not just dimensional convenience.
