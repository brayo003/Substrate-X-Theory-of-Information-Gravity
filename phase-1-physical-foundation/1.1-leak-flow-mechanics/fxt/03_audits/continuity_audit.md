# Continuity Audit: Substrate X Theory
## Mathematical Theorem-Proving Audit of the Frozen Master Equation

**Audit date:** 2026-07-20  
**Documents audited (frozen, unmodified):**  
- `COMPLETE_MASTER_EQUATION.md`  
- `UNIFIED_PERTURBATIVE_DERIVATION.md`  

**Research question:** Does the existing master equation already imply that the substrate stores anything? Is there a conserved quantity, memory variable, or accumulation mechanism capable of supporting future back-action?

---

## Notation (verbatim from frozen documents)

| Symbol | Units | Meaning |
|--------|-------|---------|
| s | info/m³ | Information density |
| τ | s | Damping time constant |
| c | m/s | Causal propagation speed |
| v_sub | m/s | Substrate flow velocity |
| χ | m/s | Coherence transport coefficient |
| u | — | Coherent propagation direction (unit vector) |
| α | info/(J·s) | Information–energy coupling |
| β | info·s/J | Energy-flow coupling |
| γ | info/(N·s) | Force coupling |
| E | J/m³ | Mass–energy density |
| F | N/m³ | Force density |
| σ_irr | info/(m³·s) | Irreversible loss rate, σ_irr ≥ 0 |
| D = c²τ | m²/s | Effective diffusivity |

**The frozen master equation [ME]:**

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr
```

No symbol is redefined. No new postulate is introduced at any point in this document.

---

## Part 1 — Continuity Structure

### 1.1 Objective

Rewrite [ME] into divergence form wherever mathematically possible. Determine whether an equation of the form

```
∂s/∂t + ∇·J = R
```

or equivalent exists. If so, derive J and R explicitly and interpret every term.

### 1.2 Rearrangement of [ME]

Begin from the exact master equation:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr
```

Move all terms to one side and group by structure. Observe that c²τ ∇²s = ∇·(c²τ ∇s) because c and τ are constants (they do not depend on x or t in the frozen theory).

Rearrange:

```
∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr − τ ∂²s/∂t²
```

Write c²τ ∇²s = ∇·(c²τ ∇s):

```
∂s/∂t = ∇·(c²τ ∇s) − ∇·(s v_sub + χ s u) + β∇·(E v_sub) + αE + γF − σ_irr − τ ∂²s/∂t²
```

Combine all divergence terms:

```
∂s/∂t + ∇·J = R                                                         [C1]
```

where:

```
J ≡ −c²τ ∇s + s v_sub + χ s u − β E v_sub                              [J-def]
```

```
R ≡ αE + γF − σ_irr − τ ∂²s/∂t²                                        [R-def]
```

**This is a continuity equation of the standard form ∂s/∂t + ∇·J = R.**

### 1.3 Term-by-Term Identification of J

**J = −c²τ ∇s + s v_sub + χ s u − β E v_sub**

| Term | Sign | Mathematical character | Role |
|------|------|----------------------|------|
| −c²τ ∇s | negative gradient | Fickian diffusion flux | Diffusion current: s flows from high to low density |
| s v_sub | advection | Transport by substrate flow | Substrate carries information |
| χ s u | directed transport | Coherent directed flux | Coherence channel, direction u |
| −β E v_sub | energy-flow contribution | Energy-density weighted substrate flux | Energy transport modifies information current |

All four terms are purely spatial: J depends on the instantaneous values of s, ∇s, v_sub, E at position x and time t. **J contains no time integral, no memory kernel, no history dependence.**

### 1.4 Term-by-Term Identification of R

**R = αE + γF − σ_irr − τ ∂²s/∂t²**

| Term | Sign | Mathematical character | Role |
|------|------|----------------------|------|
| αE | positive | Local source | Energy creates information |
| γF | sign of F | Local source/sink | Force density generates information |
| −σ_irr | negative (since σ_irr ≥ 0) | Local sink | Irreversible information loss |
| −τ ∂²s/∂t² | sign depends on field | Inertial term | Second-time-derivative correction from telegrapher structure |

### 1.5 The Inertial Term

The term −τ ∂²s/∂t² in R deserves careful treatment. It arises because [ME] is second-order in time (telegrapher equation), not first-order. It can be moved to the left side to give an alternative form:

```
τ ∂²s/∂t² + ∂s/∂t + ∇·J_reduced = R_reduced                           [C1']
```

where:

```
J_reduced ≡ −c²τ ∇s + s v_sub + χ s u − β E v_sub                     (same J)
R_reduced ≡ αE + γF − σ_irr
```

In the form [C1'], R_reduced contains no time derivatives of s. This is the cleaner decomposition for source/sink analysis in Part 2.

### 1.6 Theorem 1 (Continuity Structure)

**Theorem 1:** The master equation [ME] is exactly equivalent to the generalized continuity equation

```
τ ∂²s/∂t² + ∂s/∂t + ∇·J = R_net
```

with

```
J = −c²τ ∇s + s v_sub + χ s u − β E v_sub
R_net = αE + γF − σ_irr
```

**Proof:** Direct algebraic rearrangement of [ME], using only ∇·(c²τ ∇s) = c²τ ∇²s (valid since c, τ are constants). No approximation is made. ∎

**Corollary 1.1:** If τ → 0 (diffusion limit), [C1'] reduces to the standard first-order continuity equation ∂s/∂t + ∇·J = R_net, recovering the diffusion limit stated in COMPLETE_MASTER_EQUATION.md.

**Corollary 1.2:** J contains no integral operators, no time-delay operators, and no nonlocal terms. It is a purely local, instantaneous flux.

---

## Part 2 — Source/Sink Analysis

### 2.1 Objective

Classify each term in R_net = αE + γF − σ_irr. Determine whether each term represents creation, destruction, exchange, transport, or dissipation. Do not infer physical meaning until the mathematics is established.

### 2.2 Mathematical Classification of Each Term

**Term αE:**

- α > 0 (stated in frozen documents: α = info/(J·s), a positive coupling constant)
- E ≥ 0 by definition (energy density is non-negative)
- Therefore αE ≥ 0 at every point x and every time t

Mathematical classification: **local source**. This term creates s at rate αE per unit volume per unit time. It does not transport s. It does not depend on the current value of s (it is not a feedback term). It is a forcing function driven by an external field E.

**Term γF:**

- γ is a coupling constant [info/(N·s)]
- F is force density [N/m³]; its sign is not constrained by the frozen documents
- Therefore γF can be positive or negative depending on the sign of F

Mathematical classification: **local source or local sink**, depending on the sign of γF at each point. When γF > 0 it creates s; when γF < 0 it destroys s. Like αE, it does not depend on the current value of s.

**Term −σ_irr:**

- σ_irr ≥ 0 (explicitly stated in COMPLETE_MASTER_EQUATION.md: "Irreversible entropy production rate")
- The coefficient is −1 (negative sign in the master equation)
- Therefore −σ_irr ≤ 0 at every point x and every time t

Mathematical classification: **local sink, irreversible, unconditional**. This term always removes s. It never replenishes s. The constraint σ_irr ≥ 0 is strict: the frozen documents permit σ_irr = 0 (lossless limit) but never σ_irr < 0. This makes the sink term a one-way drain.

### 2.3 Net Source Character

The net local source/sink is:

```
R_net = αE + γF − σ_irr
```

The sign of R_net is not fixed globally. It depends on the relative magnitudes of the three contributions at each point and time. However:

- The irreversible sink −σ_irr always acts to reduce s
- The sources αE and γF can temporarily overcome the sink if sufficiently large
- But once E and F are removed (source-free region), R_net = −σ_irr ≤ 0

**Theorem 2 (Source-Free Monotonicity):** In a source-free region (E = 0, F = 0), R_net = −σ_irr ≤ 0. Therefore, in such a region, the local rate equation (ignoring flux) satisfies ∂s/∂t ≤ ∇·(−J), i.e., the only mechanism that changes the local integral of s is boundary flux and the irreversible drain.

**Proof:** Set E = 0 and F = 0 in R_net = αE + γF − σ_irr. Since σ_irr ≥ 0, the result R_net ≤ 0 follows immediately. ∎

### 2.4 Dependence of R_net on s

A critical observation for the memory analysis (Part 4): **none of the three terms in R_net depends on s itself**.

- αE depends on E, not on s
- γF depends on F, not on s
- σ_irr is an independent field (irreversible loss rate), not a function of s in the frozen equations

This means R_net is a **forcing term external to s**, not a feedback or self-coupling. There is no term of the form f(s) · s or ∫ K(t−t') s(t') dt' in R_net.

---

## Part 3 — Global Integral

### 3.1 Objective

Integrate the continuity equation over an arbitrary volume V with boundary ∂V. Apply the divergence theorem. Determine whether ∫_V s dV is conserved, monotonically decreasing, monotonically increasing, or dependent on boundary flux.

### 3.2 Setup

Integrate [C1'] over volume V:

```
∫_V [τ ∂²s/∂t² + ∂s/∂t + ∇·J] dV = ∫_V R_net dV
```

Exchange differentiation and integration (assuming V is fixed and s is sufficiently smooth):

```
τ d²/dt² ∫_V s dV + d/dt ∫_V s dV + ∫_V ∇·J dV = ∫_V R_net dV
```

Define the global information content:

```
S(t) ≡ ∫_V s dV
```

Apply the divergence theorem to the flux term:

```
∫_V ∇·J dV = ∮_∂V J · n̂ dA ≡ Φ_out(t)
```

where Φ_out is the net outward flux of information through the boundary ∂V, and n̂ is the outward unit normal.

The integrated equation becomes:

```
τ S̈(t) + Ṡ(t) + Φ_out(t) = ∫_V R_net dV                              [G1]
```

### 3.3 Decomposition of the Integral

Define:

```
Q_source(t) ≡ ∫_V (αE + γF) dV      (net source integral, sign indefinite)
Q_sink(t)   ≡ ∫_V σ_irr dV ≥ 0      (net irreversible sink integral, non-negative)
```

Then ∫_V R_net dV = Q_source(t) − Q_sink(t), and [G1] becomes:

```
τ S̈(t) + Ṡ(t) = −Φ_out(t) + Q_source(t) − Q_sink(t)                  [G2]
```

### 3.4 Conservation Analysis

**Is S(t) conserved?** Conservation would require S(t) = constant, i.e., Ṡ = 0 and S̈ = 0 for all t, which [G2] shows requires:

```
Φ_out(t) = Q_source(t) − Q_sink(t)   for all t
```

This is a constraint on the boundary flux and external sources. It is not a structural property of the equation. **S(t) is not generally conserved.**

**Theorem 3 (No Global Conservation):** There is no combination of boundary conditions and source-free assumptions under which S(t) is identically conserved in the frozen theory, unless Q_sink = 0 (lossless limit) and Φ_out = Q_source (flux exactly matches sources). These are special cases, not the general case.

**Proof:** From [G2], S̈ = Ṡ = 0 requires Φ_out = Q_source − Q_sink. Since Q_sink ≥ 0 and is not zero in general, and since Φ_out depends on the boundary geometry and field configuration, these two independent quantities cannot in general be equal. ∎

### 3.5 Isolated Volume (No Boundary Flux)

Set Φ_out = 0 (closed volume, no flux through boundary). Then [G2] becomes:

```
τ S̈(t) + Ṡ(t) = Q_source(t) − Q_sink(t)                               [G3]
```

**Source-free isolated volume** (E = 0, F = 0, Φ_out = 0):

```
τ S̈(t) + Ṡ(t) = −Q_sink(t) ≤ 0                                        [G4]
```

**Theorem 4 (Irreversible Loss in Isolation):** In a source-free closed volume, S(t) is governed by the damped second-order ODE τ S̈ + Ṡ = −Q_sink ≤ 0. The function S(t) is strictly non-increasing when the initial conditions satisfy Ṡ(0) ≤ 0 (system relaxing) and strictly decreasing whenever Q_sink > 0.

**Proof:** From [G4], τ S̈ + Ṡ ≤ 0. This is a linear first-order ODE for P ≡ Ṡ: τ Ṗ + P ≤ 0. The homogeneous solution is P(t) = P(0) exp(−t/τ). With P(0) ≤ 0 and forcing ≤ 0, P(t) ≤ 0 for all t > 0. Since P = Ṡ ≤ 0, S(t) is non-increasing. When Q_sink > 0 (strict), P(t) < 0 and S(t) strictly decreases. ∎

### 3.6 Behavior with Active Sources

When Q_source > Q_sink (sources dominate), [G3] gives τ S̈ + Ṡ > 0, meaning S can increase. When Q_source = Q_sink, the equation is τ S̈ + Ṡ = 0, admitting oscillatory relaxation toward a steady state. **In all cases, the long-time behavior is controlled by the balance of sources, sinks, and boundary flux — not by any internally conserved quantity.**

**Theorem 5 (Boundary Flux Dependence):** The time evolution of S(t) is not determined by the internal dynamics of s alone. It explicitly depends on Φ_out (boundary flux) and Q_source, Q_sink (external fields). There is no autonomous conservation law for S.

**Proof:** Equation [G2] shows S(t) depends explicitly on Φ_out, Q_source, and Q_sink, all of which are independent of S itself. ∎

---

## Part 4 — Memory Analysis

### 4.1 Objective

Determine whether the substrate possesses any state capable of storing past interactions. Candidates: persistent perturbations, long-lived field configurations, conserved currents, delayed response, relaxation modes, residual field energy. If none exist, prove they do not exist within the frozen equations.

### 4.2 Definition of Memory

A dynamical system has memory if its future evolution depends on the history of inputs, not merely on the current state. Mathematically, this requires either:

(a) An integro-differential equation with a kernel K(t−t') ≠ 0, or  
(b) An auxiliary state variable z(t) satisfying its own evolution equation whose solution retains information about past inputs, or  
(c) A neutrally stable mode (eigenvalue with zero real part) that preserves perturbation amplitude indefinitely.

### 4.3 Inspection of the Frozen Equations for Memory Structures

**Is there a memory kernel?**

The master equation [ME] is:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr
```

This is a local PDE. Every term evaluated at time t depends only on s(x,t), ∇s(x,t), ∂s/∂t(x,t), ∂²s/∂t²(x,t), and the external fields at time t. There is no term of the form ∫_{-∞}^{t} K(t−t') s(x,t') dt'. **There is no memory kernel.**

**Is there an auxiliary state variable?**

The frozen documents define no auxiliary variable z(t) with its own evolution equation beyond the master equation itself. The system state is completely specified by (s, ∂s/∂t) at each point x — a standard Cauchy data pair for a second-order PDE. **There is no auxiliary state variable.**

**Is there a conserved current?**

From Part 1, J = −c²τ ∇s + s v_sub + χ s u − β E v_sub. For J to be conserved, we would need ∂J/∂t = 0 or ∇×J = 0 (conservation of a charge carried by J). Neither condition is structurally imposed by the frozen equations. J evolves as s evolves. **There is no independently conserved current in the frozen equations.**

**Are there long-lived relaxation modes?**

To determine mode lifetimes, linearize [ME] about a background s₀. Let s = s₀ + δs with |δs| ≪ s₀. The linearized equation (in the simplest case: constant s₀, v_sub = 0, E = 0, F = 0, σ_irr treated as a constant σ₀ ≥ 0) is:

```
τ ∂²(δs)/∂t² + ∂(δs)/∂t = c²τ ∇²(δs)
```

Seek plane-wave solutions δs ∝ exp(ik·x + λt):

```
τ λ² + λ + c²τ k² = 0
```

Solving for λ:

```
λ = [−1 ± √(1 − 4c²τ²k²)] / (2τ)
```

For k = 0 (uniform mode): λ = 0 or λ = −1/τ.

- λ = 0 is the neutrally stable (non-decaying) uniform mode
- λ = −1/τ < 0 is the decaying mode

For k ≠ 0: the discriminant is 1 − 4c²τ²k². 

- If 4c²τ²k² < 1: both roots are real and negative (overdamped decay)
- If 4c²τ²k² = 1: repeated root λ = −1/(2τ) < 0 (critically damped)
- If 4c²τ²k² > 1: complex conjugate roots with Re(λ) = −1/(2τ) < 0 (oscillating decay)

**In all cases with k ≠ 0, Re(λ) < 0. All spatial modes decay.**

The λ = 0 mode (k = 0, uniform) is the constant background itself. It does not decay, but it also does not encode any information about past perturbations — it is merely the conserved background level in the absence of sources and sinks.

When σ_irr > 0 is included, the k = 0 uniform mode also develops a negative shift. Let σ_irr = σ₀ > 0 constant. The linearized uniform equation becomes:

```
τ λ² + λ = −σ₀/s₀  (negative right-hand side from the sink)
```

Both roots of τλ² + λ + σ₀/s₀ = 0 have negative real part when σ₀ > 0, since by Vieta's formulas the product of roots is σ₀/(τs₀) > 0 and the sum of roots is −1/τ < 0. **The λ = 0 mode is destroyed by the irreversible sink.** All modes decay.

### 4.4 Theorem 6 (No Memory in the Frozen Equations)

**Theorem 6:** The frozen master equation [ME] contains no memory structure. Specifically:

(a) There is no memory kernel.  
(b) There is no auxiliary state variable beyond (s, ∂s/∂t).  
(c) There is no conserved current that retains information independently of s.  
(d) All linearized plane-wave modes with k ≠ 0 have Re(λ) < 0 and therefore decay.  
(e) The k = 0 (uniform) mode decays whenever σ_irr > 0.  
(f) The only surviving mode at σ_irr = 0 is the uniform constant background, which carries no information about past perturbations.

**Proof:** Established by direct inspection of [ME] (items a–c) and by the characteristic root analysis above (items d–f). ∎

### 4.5 Persistence of Perturbations from the δs Field

The UNIFIED_PERTURBATIVE_DERIVATION document derives δs = −μL²/(c²r³) under approximations [A1]–[A7], including [A1] steady state. This δs is a steady-state field, not a dynamical memory. It exists only while the source (mass M at the origin) is present and the steady-state approximation holds. It does not accumulate over time. It does not change in response to past interactions with the substrate beyond what is determined instantaneously by L and r. **δs is a static potential, not a memory variable.**

---

## Part 5 — Dynamical Stability

### 5.1 Objective

Study the evolution operator. Determine whether perturbations decay, persist, propagate, oscillate, diffuse, or converge. Support every statement mathematically.

### 5.2 The Linear Evolution Operator

Linearize [ME] about a spatially uniform steady state s₀ > 0 in the source-free region (E = 0, F = 0, σ_irr = σ₀ ≥ 0, v_sub = v₀ = constant, χ = 0 for simplicity). Let s = s₀ + ε(x,t) with |ε| ≪ s₀:

```
τ ∂²ε/∂t² + ∂ε/∂t = c²τ ∇²ε − (v₀·∇)ε − σ₀                         [L1]
```

The constant −σ₀ shifts the background and is absorbed by the steady state condition; the linearized equation for the perturbation ε about a new equilibrium is:

```
τ ∂²ε/∂t² + ∂ε/∂t = c²τ ∇²ε − (v₀·∇)ε                              [L2]
```

This is a damped telegrapher equation with advection.

### 5.3 Fourier Analysis

Take the Fourier transform in space: ε(x,t) = ε̂(k,t) exp(ik·x). Equation [L2] becomes the ODE:

```
τ ε̂'' + ε̂' + (c²τ k² + i v₀·k) ε̂ = 0                               [F1]
```

where primes denote d/dt. This is a second-order linear ODE with constant coefficients. The characteristic equation is:

```
τ λ² + λ + (c²τ k² + i v₀·k) = 0                                      [CE]
```

### 5.4 Roots of the Characteristic Equation

Define ω_k ≡ c²τ k² + i v₀·k (complex in general). The roots are:

```
λ± = [−1 ± √(1 − 4τ ω_k)] / (2τ)
```

Write k = (k_x, k_y, k_z) with k² = |k|². For the real part of ω_k: Re(ω_k) = c²τ k² ≥ 0.

**Real part of λ:** Using the identity Re(√(z)) for complex z = A + iB where A = 1 − 4c²τ²k²:

The sum of the two roots is:

```
λ+ + λ− = −1/τ
```

The product of the two roots is:

```
λ+ · λ− = ω_k / τ = c²k² + i(v₀·k)/τ
```

Since Re(λ+ · λ−) = c²k² ≥ 0 and Re(λ+ + λ−) = −1/τ < 0, both roots have Re(λ) ≤ 0. More precisely, since their sum has negative real part and their product has non-negative real part, at least one root has strictly negative real part, and neither can have positive real part. **Both roots satisfy Re(λ) ≤ −1/(2τ) < 0 for k ≠ 0** (from the Vieta's formula argument: real part of sum = −1/τ, so average Re(λ) = −1/(2τ)).

### 5.5 Behavior of Perturbations

From the characteristic root analysis:

**Propagation:** The imaginary part of λ is nonzero when Im(ω_k) = v₀·k ≠ 0 (i.e., when there is advection and k has a component along v₀). These modes propagate as waves while decaying.

**Decay:** Re(λ±) ≤ −1/(2τ) < 0 for all k. Every Fourier mode decays on a timescale no longer than 2τ.

**Diffusion:** In the limit τ → 0 (or equivalently, at long times t ≫ τ), the dominant term is Ṡ ≈ D∇²ε − (v₀·∇)ε, a diffusion-advection equation. Solutions spread and decay.

**Oscillation:** When 4c²τ²k² > 1, the modes are underdamped: they oscillate while decaying with envelope ∝ exp(−t/(2τ)).

**Convergence:** As t → ∞, every perturbation ε → 0. The system returns to the background state s₀ (modulo any shift from active sources).

### 5.6 Theorem 7 (Asymptotic Stability of Perturbations)

**Theorem 7:** All spatially varying perturbations of the master equation [ME] linearized about a uniform background decay to zero as t → ∞. The decay rate satisfies Re(λ) ≤ −1/(2τ) for all k ≠ 0. The system is asymptotically stable: perturbations do not persist indefinitely.

**Proof:** From the characteristic equation [CE], the roots satisfy Re(λ+) + Re(λ−) = −1/τ and Re(λ+)·Re(λ−) ≥ 0. Therefore both Re(λ±) ≤ 0 and their average is −1/(2τ) < 0. For k ≠ 0, the product Re(λ+·λ−) = c²k² > 0 ensures neither root is exactly zero. Hence both roots have strictly negative real parts. All perturbation modes decay exponentially. ∎

**Corollary 7.1:** The decay timescale is set by τ (the damping time constant). There is no slow manifold, no marginally stable mode, and no algebraically growing mode in the frozen equations.

**Corollary 7.2:** The substrate has no permanent response to a transient perturbation. Once the perturbing source is removed, the field s relaxes back to background on timescale O(τ).

---

## Part 6 — Back-Action Readiness

### 6.1 Objective

Without introducing new mathematics, determine whether the frozen equations already contain any mathematical object that could participate in reciprocal coupling (back-action). Identify it precisely if it exists. Prove why it does not exist if it does not.

### 6.2 What Back-Action Requires Mathematically

Reciprocal coupling (back-action) requires at minimum one of the following structural elements in the equations:

**(BA-1) A retained state variable that records the effect of a source on s**, and whose value then enters the equation of motion of that source. This would appear as a term in both the s equation and the source equation.

**(BA-2) A conserved quantity that is exchanged between s and the source**. Conservation means the gain of one is the loss of the other, i.e., a coupling of the form ∂s/∂t ∋ −g(s, q) and ∂q/∂t ∋ +g(s, q) for some coupling function g.

**(BA-3) A non-decaying mode of s that feeds back into source dynamics**. This requires a marginally stable or unstable eigenvalue in the evolution operator — a neutral mode that accumulates amplitude.

### 6.3 Structural Inspection of [ME] for Back-Action Elements

**BA-1 inspection:** The master equation [ME] is a single equation for s. It contains E, F, and σ_irr as **inputs**. The frozen documents provide no equation of motion for E or F that contains s as a term. There is no bidirectional coupling: s responds to E, F, but E and F do not respond to s. The Gravitational Force Law F_grav = k s v_sub in the frozen documents defines F in terms of s, but this is a one-way constitutive rule applied to compute the force on a test particle from s — it is not a back-reaction of s onto its own sources. **BA-1 is absent.**

**BA-2 inspection:** As established in Part 3, there is no conserved quantity for s. Theorem 3 proves that S(t) = ∫s dV is not conserved. Since there is no conserved quantity for s, there is no quantity that could be exchanged between s and a source in a zero-sum fashion. **BA-2 is absent.**

**BA-3 inspection:** As established in Part 5, Theorem 7, all spatially varying modes have Re(λ) < 0. The only neutrally stable mode is the k = 0 uniform mode, which exists only in the lossless limit σ_irr = 0. This mode carries no spatial information about where a perturbation was applied, by whom, or when. It cannot encode which source produced it. **BA-3 is absent.**

### 6.4 The One-Way Structure of the Frozen Theory

The frozen equations impose a strictly one-way information flow:

```
External sources (E, F) → s equation → s evolves
                                    ↓
                           s affects test particles (constitutive rule CA-2)
                           but this is output, not feedback into s
```

There is no arrow returning from the test particle to the source (E, F). The source is not modified by the value of s. The substrate s decays toward zero in the absence of sources (Theorem 7). There is no state variable within the frozen equations that accumulates a history of what has coupled to s.

### 6.5 Theorem 8 (No Back-Action in the Frozen Equations)

**Theorem 8:** The frozen master equation [ME] does not contain any mathematical object that could participate in reciprocal coupling (back-action) without extending the theory.

**Proof by exhaustion of structural candidates:**

(i) No memory kernel exists (Theorem 6a). Therefore no past history of coupling is retained in s.

(ii) No conserved quantity exists (Theorem 3). Therefore no exchange law can be written.

(iii) No neutral or growing mode exists (Theorem 7). Therefore no perturbation can accumulate amplitude over time.

(iv) The source terms E, F, σ_irr are inputs to s, not outputs from s. The frozen documents contain no equation for ∂E/∂t or ∂F/∂t that contains s on the right-hand side (no closed-loop equation is present in the frozen documents).

(v) The steady-state perturbation field δs = −μL²/(c²r³) is determined instantaneously by L and r. It does not integrate past interactions. It vanishes when M is removed. It carries no state beyond what is determined by the current configuration.

All five structural requirements for back-action are absent. ∎

### 6.6 The Only Candidate Object and Why It Fails

The strongest candidate for a back-action carrier is the perturbation field δs. It has a spatial structure, is sourced by mass M, and acts on test particles via the constitutive rule CA-1 (F ∝ −∇δs). However:

- δs is algebraically determined by (μ, L, r): it has no independent dynamics
- δs does not appear in the equation of motion for M (the frozen documents contain no equation for Ṁ or M̈ involving δs)
- δs is derived under steady-state assumption [A1]; it has no time derivative, no relaxation time, no storage capacity

δs is a slave field: it follows the source instantaneously, stores nothing, and records no history. It is a potential, not a state variable.

---

## Summary of All Theorems

| Theorem | Statement | Implication |
|---------|-----------|-------------|
| **T1** | [ME] is exactly equivalent to τS̈ + Ṡ + ∇·J = R_net | Continuity form exists |
| **T2** | In source-free region, R_net ≤ 0 | Local drain is unconditional |
| **T3** | S(t) = ∫s dV is not conserved | No global conservation law |
| **T4** | In source-free closed volume, S(t) is non-increasing | Substrate loses information irreversibly |
| **T5** | S(t) depends on external boundary flux and sources | No autonomous conservation |
| **T6** | [ME] contains no memory structure of any kind | No stored state, no history |
| **T7** | All perturbation modes decay; Re(λ) ≤ −1/(2τ) < 0 | Asymptotic stability, no accumulation |
| **T8** | No mathematical object in [ME] can support back-action | Reciprocal coupling requires theory extension |

---

## Explicit Answers to the Research Questions

| Question | Answer |
|----------|--------|
| Is there a conservation law? | **No.** Theorem 3 proves S(t) is not conserved. |
| Is there a continuity equation? | **Yes** (Theorem 1), but with a net sink R_net ≤ 0 in source-free conditions. |
| Is there an accumulated quantity? | **No.** All modes decay (Theorem 7). Nothing accumulates. |
| Is there a memory variable? | **No.** Theorem 6 proves absence of memory kernel, auxiliary variables, and neutral modes. |
| Is information locally conserved? | **No.** The term −σ_irr ≤ 0 is a strictly local sink. |
| Is information globally conserved? | **No.** Theorem 3 and Theorem 4. |
| Is information irreversibly destroyed? | **Yes.** By −σ_irr ≤ 0, unconditionally. |
| Is there a mathematically unavoidable state variable capable of mediating future back-action? | **No.** Theorem 8. |

---

## Final Conclusion

> **The frozen theory is mathematically an irreversible sink with no stored state capable of future back-action.**

Every theorem in this document has been derived from the frozen master equation [ME] without introducing new postulates, new variables, new operators, or new physical assumptions. The master equation has continuity form, but the continuity equation has a net sink term that is unconditionally non-positive in source-free conditions. No conserved quantity exists. No memory structure exists. All perturbations decay on timescale τ. The steady-state perturbation field δs is a slave field with no independent dynamics and no capacity to store the history of past interactions. Reciprocal coupling is not possible without extending the frozen theory to include at least one of: a memory kernel, an auxiliary state variable with its own evolution equation, or a closed-loop coupling between s and its sources.

---

*Audit produced from frozen documents only. No new physics introduced.*
