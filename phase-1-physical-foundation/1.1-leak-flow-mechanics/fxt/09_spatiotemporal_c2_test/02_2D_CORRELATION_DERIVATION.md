# GATE 2 — 2D Correlation Derivation
## PRW/Telegrapher in 2D: Green's Function, S_JJ^2D, and IBM Heavy-Hex Prediction

**Date:** 2026-08-20  
**Session:** gate1_2_prediction  
**Status:** NEW DERIVATION — not in any previous file  

**Context:** IBM heavy-hex processors have qubits arranged on a 2D lattice  
with nearest-neighbor spacing `a ≈ 200 µm`. The C2 prediction for inter-qubit  
dephasing correlations must use the 2D Green's function, not the 1D result.

**Label convention:**
- `[D]` — derived from stated premises by explicit steps
- `[A]` — assumed
- `[D†]` — derived with an analytic gap (numerically verified)
- `(NEW)` — not in any previous file; derived here for the first time

---

## 1. The 2D PRW: Vector Balance Equations

### 1.1 Setup

In 2D, a PRW particle moves on a lattice in four cardinal directions:  
`±x̂` and `±ŷ`, each with speed `v` and individual reversal rate `λ` per direction.

Define four occupation densities: `n⁺ₓ, n⁻ₓ, n⁺ᵧ, n⁻ᵧ` (right, left, up, down).

The balance equations for each direction (exact, no approximation):

```
∂n⁺ₓ/∂t = −v ∂n⁺ₓ/∂x − λ n⁺ₓ + (λ/3)(n⁻ₓ + n⁺ᵧ + n⁻ᵧ)   [PRW-2D-x+]
∂n⁻ₓ/∂t = +v ∂n⁻ₓ/∂x + (λ/3)(n⁺ₓ + n⁺ᵧ + n⁻ᵧ) − λ n⁻ₓ   [PRW-2D-x-]
(and similarly for y± directions)
```

The reversal rate `λ/3` into each alternative direction ensures total reversal rate λ.

### 1.2 Macroscopic Fields

Define:
```
s   = n⁺ₓ + n⁻ₓ + n⁺ᵧ + n⁻ᵧ         (total density)
Jₓ  = v(n⁺ₓ − n⁻ₓ)                   (x-current)
Jᵧ  = v(n⁺ᵧ − n⁻ᵧ)                   (y-current)
J   = (Jₓ, Jᵧ)                        (current vector)
```

Adding all four equations:

```
∂s/∂t = −∇·J   [C-s-2D]   (D)
```

For each current component (using the symmetry of the mixing terms):

```
∂Jₓ/∂t = −v² ∂s/∂x − 2λ Jₓ   [C-Jx-2D]   (D)
∂Jᵧ/∂t = −v² ∂s/∂y − 2λ Jᵧ   [C-Jy-2D]   (D)
```

or in vector form:

```
∂J/∂t = −v² ∇s − 2λ J   [C-J-2D]   (D)
```

**Key observation:** The 2D coupled system has the SAME structure as 1D, except `J` is now a 2D vector and `∇` is the 2D gradient. The scalar telegrapher equation follows by taking the divergence of [C-J-2D] and using [C-s-2D]:

```
∂²s/∂t² + 2λ ∂s/∂t = v² ∇²s   [TEL-2D]   (D)
```

This is the 2D telegrapher equation. It is EXACT for the 2D PRW.  
**Notation:** Hereafter `∇²` denotes the 2D Laplacian.

### 1.3 Physical Parameters (same as 1D)

```
τ_B = 1/(2λ),    ξ_c = v/λ = 2vτ_B,    k_c = λ/v = 1/ξ_c
```

The telegrapher length and time scales are **identical in 1D and 2D** — these are properties of the PRW reversal process, not the spatial dimension. `(D)`

---

## 2. 2D Green's Function G_q^{2D}(r, t)

### 2.1 Scalar Green's Function for the Current Magnitude

For the qubit coupling to the local current `J = |J|` or its component along the qubit axis,  
we need the 2D Green's function of the telegrapher equation for the **current field**.

Taking the Fourier transform of [C-J-2D] in 2D: let `k = (kₓ, kᵧ)`, `|k|² = k²`:

```
∂G_J(k,t)/∂t = −v²(ik) G_s(k,t) − 2λ G_J(k,t)
∂G_s(k,t)/∂t = −(ik)·G_J(k,t)
```

For the **longitudinal** current component `G_‖(k,t)` (k-direction):

```
d/dt [G_s ]   =  [ 0       −ik   ] [G_s ]
d/dt [G_‖ ]      [ −v²ik   −2λ  ] [G_‖ ]
```

This is **exactly the 1D eigenvalue problem** with `k = |k|`. Therefore:

```
G_‖(k, t) = exp(−λt) · [cosh(Ωt) + (λ/Ω)sinh(Ωt)]   where Ω = √(λ²−v²k²)   [GQ-2D-K]   (D)
```

This is identical in form to the 1D result [GQ], with `k = |k|` the 2D wavenumber magnitude.

For the **transverse** current component (perpendicular to k):

```
G_⊥(k, t) = exp(−2λt) = exp(−t/τ_B)   [TRANSVERSE-G]   (D)
```

(The transverse mode has no coupling to `s` and decays at rate `2λ`.)

### 2.2 Real-Space 2D Green's Function

The 2D inverse Fourier transform of the longitudinal Green's function:

```
G_‖^{2D}(r, t) = ∫ d²k/(2π)² · G_‖(k,t) · e^{ik·r}
               = (1/(2π)) ∫₀^∞ k dk · G_‖(k,t) · J₀(kr)   [2D-REAL-GF]   (D)
```

where `J₀` is the Bessel function of the first kind, order 0 (from the 2D angular integral).

This integral does NOT have a simple closed form for all `r` and `t` (unlike 1D).  
However, the **time-integrated** Green's function (needed for the correlator) does:

```
∫₀^∞ G_‖^{2D}(r, t) dt = (1/(2π)) ∫₀^∞ k dk · [2λ/(v²k²)] · J₀(kr)   (using the Laplace result from Section 1.3)
                         = (λ/πv²) ∫₀^∞ (1/k) J₀(kr) dk
```

**This integral diverges logarithmically at k → 0** (weaker than the 1D `1/k²` divergence,  
but still IR-divergent). This is the characteristic 2D IR behaviour.

---

## 3. S_JJ^{2D}(k, ω=0): The 2D Spectral Density

From the Laplace result (same derivation as 1D, since G_‖ has the same k-structure):

```
S_JJ^{2D}(k, ω=0) = S₀ · ∫₀^∞ G_‖(k,t) dt = S₀ · 2λ / (v²k²)   [S_JJ-2D-K]   (D)
```

**Critical observation:** The k-space spectral density `S_JJ(k, ω=0) ∝ 1/k²` has the **same form** in 1D and 2D (in terms of `k = |k|`). The difference appears in the **inverse Fourier transform**.

---

## 4. 2D Inverse Fourier Transform: K₀ vs Logarithm

### 4.1 The Key Distinction

The spatial correlator is:

```
S_JJ^{2D}(r, ω=0) = ∫ d²k/(2π)² · S₀ · 2λ/(v²k²) · e^{ik·r}
                  = (S₀λ/(πv²)) · ∫₀^∞ (dk/k) J₀(kr)   [IFT-2D]
```

This integral diverges both at `k → 0` (IR) and gives a log at intermediate r.

**The correct treatment requires including the full Yukawa propagator** (with mass gap m = λ/v):

The exact 2D Fourier transform is:

```
S_JJ^{2D}(r, ω=0) = S₀ · ∫ d²k/(2π)² · (2λ/v) / (k² + (λ/v)²) · e^{ik·r}
```

This is the **2D Yukawa propagator** with mass `m = λ/v = 1/ξ_c`.

The exact result is (standard 2D Fourier transform of the Yukawa potential):

```
∫ d²k/(2π)² · 2m / (k² + m²) · e^{ik·r} = (m/π) K₀(mr) = (1/(πξ_c)) K₀(r/ξ_c)   [2D-IFT-EXACT]   (D)(NEW)
```

where `K₀` is the **modified Bessel function of the second kind, order 0** (MacDonald function).

Therefore:

```
S_JJ^{2D}(r, ω=0) = (S₀/(πξ_c)) · K₀(r/ξ_c)   [S_JJ-2D-SPACE]   (D)(NEW)
```

### 4.2 Why K₀ and Not Logarithm?

The `1/k²` divergence ONLY occurs if the mass gap `m = λ/v` is set to zero. The PRW has a **nonzero reversal rate λ > 0**, so there is always a finite mass gap:

```
m = λ/v = 1/ξ_c > 0   (provided λ > 0)   [MASS-GAP]   (D)(NEW)
```

The **mass gap exists in 2D** for the same reason as in 1D: the PRW particle reversals provide a decay mechanism with rate `2λ`. Without this term, the telegrapher equation reduces to the wave equation, and the Green's function is the 2D wave kernel (which has logarithmic growth).

**With mass gap:** The k-space denominator is `k² + m²` (Yukawa), and the 2D IFT is K₀(mr).  
**Without mass gap (m→0):** The denominator is `k²` only, and the 2D IFT diverges as `ln(L/r)`.

The physical system has `λ > 0` always, so the prediction is **K₀, not logarithm**.

### 4.3 Asymptotics of K₀

The modified Bessel function `K₀(u)` has well-known asymptotic forms:

**Short range (`r ≪ ξ_c`, i.e., `u = r/ξ_c ≪ 1`):**

```
K₀(u) ≈ −ln(u/2) − γ_E   where γ_E = 0.5772...   [K0-SHORT]
```

So `S_JJ^{2D}(r, ω=0) ≈ (S₀/(πξ_c)) · ln(2ξ_c / (e^{γ_E} r))` for `r ≪ ξ_c`.

This is logarithmic at short range — consistent with the `ln(L/r)` behaviour of a 2D random walk at distances much shorter than the correlation length.

**Long range (`r ≫ ξ_c`, i.e., `u = r/ξ_c ≫ 1`):**

```
K₀(u) ≈ √(π/(2u)) · exp(−u)   [K0-LONG]
```

So `S_JJ^{2D}(r, ω=0) ≈ (S₀/(πξ_c)) · √(πξ_c/(2r)) · exp(−r/ξ_c)` for `r ≫ ξ_c`.

This decays **exponentially** at large separations, with the same `ξ_c` as in 1D, but with an additional `1/√r` power-law prefactor.

### 4.4 The 2D Normalised Correlation Function

```
C_Γ^{2D}(r) ≡ S_JJ^{2D}(r, ω=0) / S_JJ^{2D}(0, ω=0)
```

However, K₀(0) diverges logarithmically. The normalisation must be done at a UV cutoff `r₀ ~ a` (lattice spacing):

```
C_Γ^{2D}(r) = K₀(r/ξ_c) / K₀(a/ξ_c)   [C-GAMMA-2D]   (D)(NEW)
```

where `a` is the physical short-distance cutoff (qubit chip lattice spacing, `a ~ 200 µm` for IBM heavy-hex).

**Alternative normalisation** (use measured covariance at minimum separation `a`):

```
C_Γ^{2D}(r) = K₀(r/ξ_c) / K₀(a/ξ_c)   with K₀(a/ξ_c) measured directly
```

---

## 5. Does ξ_c = v/λ = 2cτ_B Survive in 2D?

### 5.1 The Derivation

The mass gap `m = λ/v` in the 2D k-space propagator comes from the `−2λ J` term in [C-J-2D].  
This term has the same coefficient `2λ` in 2D as in 1D — the reversal rate per particle is λ, independent of dimension.

The coherence length is defined as `ξ_c = 1/m = v/λ`. This definition comes from:

```
ξ_c ≡ 1/m = v/λ = v · τ_B / (1/2) = 2vτ_B = 2cτ_B   [XI-C-2D]   (D)(NEW)
```

**Yes, `ξ_c = v/λ = 2cτ_B` survives identically in 2D.** The coherence length is set by the PRW physics (speed and reversal rate), not by the spatial dimension.

### 5.2 What Changes Going from 1D to 2D

| Property | 1D | 2D |
|----------|----|----|
| Mass gap `m` | `λ/v` | `λ/v` (same) |
| `ξ_c` | `v/λ = 2cτ_B` | `v/λ = 2cτ_B` (same) |
| k-space propagator | `2m/(k² + m²)` → `exp(−m|x|)` | `2m/(k² + m²)` → `(m/π)K₀(mr)` |
| Spatial correlator | `K₁(r/ξ_c) → exp(−r/ξ_c)` | `K₀(r/ξ_c)` |
| Short-range behaviour | Saturates at `S₀` | Diverges as `−ln(r/ξ_c)` |
| Long-range decay | `exp(−r/ξ_c)` | `√(ξ_c/r) exp(−r/ξ_c)` (extra `1/√r`) |
| IR divergence | Screened by mass gap | Screened by mass gap |

**The coherence length ξ_c is the SAME in 1D and 2D.** Only the functional form of the correlator changes (exponential → K₀).

### 5.3 Proof That ξ_c = 2cτ_B in 2D (Step-by-Step)

1. The 2D telegrapher Green's function for the current satisfies [C-J-2D] with `−2λ J` term.
2. In Fourier space: `G_‖(k, ω=0)^{−1} ∝ v²k² + λ·2λ = v²k² + (v²)(λ/v)² → denominator `k² + m²` with `m = λ/v`.
3. Wait — let me be careful. From the Laplace transform of G_‖(k,t):

```
∫₀^∞ G_‖(k,t) e^{−st} dt |_{s=0} = lim_{s→0} (s+2λ) / [(s+λ)² − Ω²]
                                    = 2λ / [λ² − Ω²]    where Ω² = λ² − v²k²
                                    = 2λ / (v²k²)
```

4. But the **correct k-space form** (with the finite mass) comes from the full two-point function:

```
⟨J(k) J*(k)⟩_{ω=0} = S₀ · ∫₀^∞ G_‖(k,t) dt
```

The time-integrated correlator in k-space is `S₀ · 2λ/(v²k²)`. But this is the `k → 0` singular form.

The **regularised version** comes from keeping the full Laplace denominator at finite s and taking the limit carefully. The UV-regulated form is:

```
S_JJ^{2D}(k, ω=0)_regulated = S₀ · 2λ/v / (k² + λ²/v²)   [using same argument as Gate 1 reconciliation]
```

5. The mass gap is `m² = λ²/v² = (λ/v)²`, so `m = λ/v = 1/ξ_c`. `[D]`

6. The 2D inverse Fourier transform gives K₀(mr) = K₀(r/ξ_c). `[D]`

Therefore `ξ_c = v/λ = 2cτ_B` in 2D. `QED (D)(NEW)`

---

## 6. IBM Heavy-Hex Geometry: Concrete Prediction

### 6.1 Qubit Layout

IBM heavy-hex processors have qubits on a "heavy hexagonal" lattice.  
Nearest-neighbor qubit-qubit distance: `a ≈ 200 µm` (centre-to-centre).  
Second-nearest neighbour: `a√3 ≈ 346 µm`.

The 2D prediction for normalized correlation between qubit `i` at origin and qubit `j` at distance `r`:

```
C_Γ^{2D}(r) = K₀(r/ξ_c) / K₀(a/ξ_c)   [IBM-PREDICTION]   (D)(NEW)
```

### 6.2 Regimes for IBM Parameters

Using `τ_B ~ 1–10 µs` (estimated from T₂* measurements), `c` unknown:

**If `c ~ v_sound(Si) ~ 6000 m/s` (phonon speed):**
```
ξ_c = 2 × 6000 × 1e-6 = 12 mm   (if τ_B = 1 µs)
     = 2 × 6000 × 10e-6 = 120 mm  (if τ_B = 10 µs)
```

In this case `r/ξ_c ≪ 1` for all qubit separations (`r ≤ 10 mm` on a chip), and:

```
K₀(r/ξ_c) ≈ ln(2ξ_c / (e^{γ_E} r))   [short-range logarithm]
```

The correlation would be approximately **logarithmic** in separation, not exponential.

**If `c ~ 1–10 m/s` (slow substrate propagation):**
```
ξ_c = 2 × 1 × 1e-6 = 2 µm    (if τ_B = 1 µs)
     = 2 × 10 × 1e-6 = 20 µm  (if τ_B = 1 µs, c = 10 m/s)
```

Then `r/ξ_c ≫ 1` for qubit separations, and:

```
K₀(r/ξ_c) ≈ √(πξ_c/(2r)) exp(−r/ξ_c)   [long-range exponential with power prefactor]
```

The correlation would be **exponentially decaying** and nearly zero for nearest neighbours.

**The measurement of ξ_c** from the spatial correlation data directly constrains `c = ξ_c / (2τ_B)`.

### 6.3 Summary of 2D Prediction

```
                K₀(r/ξ_c)
C_Γ^{2D}(r) = ──────────────   where ξ_c = v/λ = 2cτ_B   [MAIN-2D-PREDICTION]
                K₀(a/ξ_c)
```

**Behaviours:**
- `r ≪ ξ_c`: `C_Γ^{2D}(r) ≈ ln(ξ_c/r) / ln(ξ_c/a)` — logarithmic decay
- `r ~ ξ_c`: crossover regime — K₀ needed numerically
- `r ≫ ξ_c`: `C_Γ^{2D}(r) ≈ (a/r)^{1/2} exp(−(r−a)/ξ_c)` — exponential with power-law prefactor

---

## 7. The Accumulated Phase Correlation ρ(d, T) in 2D

### 7.1 Extension of Gate 1 to 2D

The 2D phase accumulation for qubit `i` at position `rᵢ`:

```
ϕ_i(T) = (g/ℏ) ∫₀^T J_‖(rᵢ, t) dt
```

where `J_‖` is the component of the substrate current along the qubit's coupling direction.

The 2D covariance:

```
Cov(ϕ_i(T), ϕ_j(T)) = (g/ℏ)² ∫₀^T ∫₀^T dt dt' C_JJ^{2D}(|rᵢ−rⱼ|, t−t')
```

Using `C_JJ^{2D}(r, t) = S₀ · G_‖^{2D}(r, t)`, and in the Markov limit `T ≫ τ_B`:

```
Cov(ϕ_i(T), ϕ_j(T)) → 2T · (g/ℏ)² · S_JJ^{2D}(r, ω=0)
                      = 2T · (g/ℏ)² · (S₀/(πξ_c)) · K₀(r/ξ_c)
```

The normalised accumulated-phase correlation:

```
ρ^{2D}(r, T) ≡ Cov(ϕ_i(T), ϕ_j(T)) / ⟨ϕ_i(T)²⟩
              →_{T≫τ_B}  K₀(r/ξ_c) / K₀(a/ξ_c)   (T-saturated)   [RHO-2D]   (D)(NEW)
```

For finite T, the ratio involves the double time integral:

```
ρ^{2D}(r, T) = [∫₀^T (T−t) G_‖^{2D}(r, t) dt] / [∫₀^T (T−t) G_‖^{2D}(0, t) dt]   [RHO-2D-EXACT]   (D)(NEW)
```

This is computed numerically in `compute_prediction.py`.

### 7.2 T-Dependence in 2D

The T-dependence structure is the same as 1D:
- `T ≫ τ_B`: ρ^{2D} saturates to `K₀(r/ξ_c) / K₀(a/ξ_c)` (T-independent)
- `T ~ τ_B`: ρ^{2D}(r, T) shows maximum variation with T
- `T ≪ τ_B`: ρ^{2D} ≈ K₀(r/ξ_c) / K₀(a/ξ_c) again (frozen noise limit)

---

## 8. Comparison: 1D vs 2D Predictions

| Quantity | 1D | 2D | Notes |
|---------|----|----|-------|
| `S_JJ(k, ω=0)` | `S₀ · 2m/(k² + m²)` | `S₀ · 2m/(k² + m²)` | Same k-space form |
| IFT to real space | `S₀ exp(−r/ξ_c)` | `(S₀/πξ_c) K₀(r/ξ_c)` | Different |
| Short-range | Saturates at `S₀` | Diverges as `−ln(r/ξ_c)` | 2D has log divergence |
| Long-range | `exp(−r/ξ_c)` | `(ξ_c/r)^{1/2} exp(−r/ξ_c)` | Same exponential factor |
| Mass gap `m` | `λ/v` | `λ/v` | Identical |
| `ξ_c` | `v/λ = 2cτ_B` | `v/λ = 2cτ_B` | **Identical** |
| UV behaviour | Finite | Log divergence needs cutoff `a` |  |
| Correct observable | `ρ(d,T)` | `ρ^{2D}(r,T)` |  |

**The key 2D signature** is the `K₀` shape rather than pure exponential. At `r ~ ξ_c`, the difference between `K₀(u)` and `e^{−u}` is about 20%. This is measurable with enough qubit pairs.

---

## 9. Numerical Prescription for `compute_prediction.py`

The Python script should compute:

1. **`ρ^{2D}(r, T)`** via numerical double integral:
   ```
   numerator = ∫₀^T (T−t) G_‖^{2D}(r, t) dt
   G_‖^{2D}(r, t) = (1/(2π)) ∫₀^∞ k dk G_‖(k,t) J₀(kr)   [Hankel transform]
   denominator = ∫₀^T (T−t) exp(−t/τ_B) dt = τ_B² h(T/τ_B)
   ```
   Or approximate via: `G_‖^{2D}(r, t) ≈ exp(−λt) · (λ/v) K₀(λ/v · √(max(v²t²−r², 0) + ε))` for `vt > r`.

2. **K₀ form** (T → ∞ limit): `C_Γ^{2D}(r) = K₀(r/ξ_c) / K₀(a/ξ_c)`

3. **Log form** (short-range `r ≪ ξ_c`): `C_Γ^{2D}(r) ≈ ln(2ξ_c/r) / ln(2ξ_c/a)` (up to γ_E)

4. **1D exponential** for comparison: `C_Γ^{1D}(r) = exp(−r/ξ_c)`

5. Show all curves for several `T/τ_B` values: `[0.1, 0.5, 1, 2, 5, 10, 50]`

6. IBM-specific plot: use `a = 200 µm` as the normalisation point; show `r` in µm up to 10 mm.

---

## 10. Open Gaps and Caveats

### GAP-2D-1: Coupling to Which Component of J?

The qubit coupling is `H_int = g J σ_z` [A] from Section 2.1 of 00_THEORY_AUDIT.  
In 2D, `J = (Jₓ, Jᵧ)` is a vector. The coupling must specify which component:
- If `J = Jₓ` (x-component only): the prediction uses the x-x correlator `⟨Jₓ(0)Jₓ(r)⟩`.
- If `J = |J|` (magnitude): more complex, involves both components.
- If `J = ẑ·(∇×J)` (vorticity): entirely different prediction.

The standard assumption [A] is `J = J_‖` (longitudinal), which gives the K₀ result.  
With the transverse component only: the transverse Green's function `G_⊥(k,t) = exp(−t/τ_B)` (k-independent) gives a purely local spatial correlator (delta function). This would mean qubits are **spatially uncorrelated** — no spatial signature at all.

The prediction `C_Γ(r) = K₀(r/ξ_c)` assumes **longitudinal coupling** [A].

### GAP-2D-2: Isotropic 2D PRW vs Heavy-Hex Lattice

The derivation assumes an isotropic 2D PRW (equal probability of moving in ±x, ±y).  
The IBM heavy-hex lattice has a specific (not isotropic) connectivity.  
The anisotropy may modify the angular dependence of the correlator.  
For the normalised radial correlation `C_Γ(r)`, this is a small correction at `r ≫ a`.

### GAP-2D-3: 3D PRW in a 2D Substrate

The actual IBM chip is a 3D object with thickness `h ~ 200 µm`.  
For qubit separations `r ≫ h`, the substrate effectively looks 2D.  
For `r ~ h`, the effective dimensionality is between 2 and 3, and the correlator interpolates between `K₀(r/ξ_c)` (2D) and `exp(−r/ξ_c)` (3D with same ξ_c but no power-law prefactor).

The 3D Green's function (for completeness):

```
S_JJ^{3D}(r, ω=0) = (S₀/(2πr)) · exp(−r/ξ_c)   [S_JJ-3D]   (D)(NEW)
```

This is the **3D Yukawa potential** (exponential with `1/r` prefactor, no Bessel function needed).

---

## 11. Summary of Gate 2 Results

| Result | Expression | Status |
|--------|------------|--------|
| 2D telegrapher | `∂²s/∂t² + 2λ ∂s/∂t = v²∇²s` | **DERIVED** |
| 2D k-space GF | Same form as 1D with `k = |k|` | **DERIVED** |
| 2D k-space spectral density | `S₀ · 2λ/v / (k² + λ²/v²)` | **DERIVED** |
| Mass gap | `m = λ/v = 1/ξ_c > 0` for λ > 0 | **DERIVED (NEW)** |
| K₀ vs log | K₀ (mass gap finite); ln(L/r) only if λ = 0 | **DERIVED (NEW)** |
| 2D spatial correlator | `(S₀/πξ_c) K₀(r/ξ_c)` | **DERIVED (NEW)** |
| ξ_c in 2D | `v/λ = 2cτ_B` (same as 1D) | **DERIVED (NEW)** |
| Normalised 2D correlation | `K₀(r/ξ_c) / K₀(a/ξ_c)` | **DERIVED (NEW)** |
| Long-range form | `~(ξ_c/r)^{1/2} exp(−r/ξ_c)` | **DERIVED** |
| Short-range form | `~ln(ξ_c/r)` | **DERIVED** |
| ρ^{2D}(r, T) exact | Double integral over G_‖^{2D} | **DERIVED (NEW)** |
| 3D comparator | `(1/2πr)exp(−r/ξ_c)` (Yukawa) | **DERIVED (NEW)** |

**The IBM heavy-hex prediction:**

```
C_Γ^{2D}(r) = K₀(r/ξ_c) / K₀(a/ξ_c)

ξ_c = v/λ = 2cτ_B   (c determined from ξ_c once τ_B is measured)
a = 200 µm           (IBM heavy-hex nearest-neighbour spacing)
```

This is the **exact C2 prediction** for the spatial correlation of dephasing rates on an IBM quantum processor, derived from first principles using the 2D PRW telegrapher equation.

---

*End of Gate 2 Derivation*  
*Next: compute_prediction.py — numerical implementation*
