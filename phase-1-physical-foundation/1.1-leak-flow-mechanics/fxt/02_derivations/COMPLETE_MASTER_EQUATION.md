Complete Master Equation of Substrate X Theory
Final Corrected Form (Causal)

The complete master equation with all dimensional corrections applied:
τ∂2s∂t2+∂s∂t=c2τ∇2s−∇⋅(svsub+χsu)+αE+β∇⋅(Evsub)+γ_F F−σirr
τ∂t2∂2s​+∂t∂s​=c2τ∇2s−∇⋅(svsub​+χsu)+αE+β∇⋅(Evsub​)+γ_F F−σirr​
Term-by-Term Breakdown
Left-Hand Side: Information Transport
1. Time Evolution (Causal, Damped)
τ∂2s∂t2+∂s∂t
τ∂t2∂2s​+∂t∂s​

    s: Information density (info/m³)

    τ: Damping time constant (s)

    Physical meaning: Telegrapher form with inertia and relaxation

2. Diffusion
c2τ∇2s
c2τ∇2s

    c: Speed of light (m/s)

    Physical meaning: Information diffuses with effective diffusivity D = c²τ

Right-Hand Side: Information Transport & Sources
3. Advection
−∇⋅(svsub)
−∇⋅(svsub​)

    v_sub: Substrate flow velocity (m/s)

    Physical meaning: Information transported by substrate motion

4. Coherence Transport
−∇⋅(χsu)
−∇⋅(χsu)

    χ: Coherence transport coefficient (m/s)

    u: Coherent propagation direction (unit vector)

    Physical meaning: Directed coherent transport of information

5. Direct Energy Coupling
+αE
+αE

    α: Information–energy coupling constant [info/(J·s)]

    E: Mass–energy density [J/m³]

    Physical meaning: Energy creates information

6. Energy Flow Coupling
+β∇⋅(Evsub)
+β∇⋅(Evsub​)

    β: Energy flow coupling constant [info·s/J]

    Physical meaning: Energy transport creates information

7. Force Coupling
+γ_F F
+γ_F F

    γ_F: Force coupling constant [info/(N·s)]

    F: Force density [N/m³]

    Physical meaning: Forces generate information

8. Irreversible Loss
−σirr
−σirr​

    σ_irr: Irreversible entropy production rate [info/(m³·s)]

    Physical meaning: Information loss through irreversible processes

Covariant Form
τ∂μ∂μs+∂μJμ=S−σirr
τ∂μ​∂μs+∂μ​Jμ=S−σirr​

where:

    J^μ = (c s, s\mathbf{v}_{\text{sub}} + \chi s \mathbf{u})

    S = \alpha E + \beta \nabla\cdot(E\mathbf{v}_{\text{sub}}) + \gamma_F F

Key Physical Constants


Constant	Units	Physical Meaning

α	info/(J·s)	Information per unit energy per time

β	info·s/J	Information from energy flow

γ_F	info/(N·s)	Information from force

χ	m/s	Coherence speed

τ	s	Damping time constant

c	m/s	Causal propagation speed

σ_irr	info/(m³·s)	Irreversible loss

D = c²τ	m²/s	Effective diffusivity


Special Cases


Steady State (∂s/∂t = ∂²s/∂t² = 0)

c2τ∇2s=∇⋅(svsub+χsu)−αE−β∇⋅(Evsub)−γ_F F+σirr

c2τ∇2s=∇⋅(svsub​+χsu)−αE−β∇⋅(Evsub​)−γ_F F+σirr​

Weak-Field Limit (∇²s → 0, spatial variations small)

∇⋅(svsub)≈αE

∇⋅(svsub​)≈αE

Diffusion Limit (τ → 0)

∂s∂t=D∇2s−∇⋅(svsub+χsu)+αE+β∇⋅(Evsub)+γ_F F−σirr

∂t∂s​=D∇2s−∇⋅(svsub​+χsu)+αE+β∇⋅(Evsub​)+γ_F F−σirr​

where D = c²τ
Regularized Forms (Point Mass)

Information density:
s(r)=s0Rr+Rmin⁡
s(r)=s0​r+Rmin​R​

Substrate flow:
vflow(r)=−r^2GMr+Rmin⁡
vflow​(r)=−r^r+Rmin​2GM​
​

with:
Rmin⁡=2GMc2
Rmin​=c22GM​
Gravitational Force Law
Fgrav=ksvsub
Fgrav​=ksvsub​

    k: Gravitational coupling constant [kg·m³/(info·s)]

    k = 2.71 × 10⁻²¹ (empirical calibration)

Decoherence Prediction
Γ=Γ0+krotω21+(ω/ωmax⁡)2
Γ=Γ0​+krot​1+(ω/ωmax​)2ω2​

    Γ₀: Base decoherence rate (s⁻¹)

    k_rot = 4.5 × 10⁻⁷ s  (empirical value; symbolic formula: k_rot = 8g²s₀²r_q²τ/(3ℏ²) [KROT-CANONICAL, interaction_hamiltonian_derivation.md])

    ω_max ≈ 10⁶ rad/s

**Dimensional check for g (g-DC-1):**
  [H_int] = J (energy required)
  [H_int] = [g][J_sub][σ_z]
  [J_sub] = info/(m²·s)  (substrate current, A-TRANS-4)
  [σ_z]   = dimensionless
  Therefore: [g] = J / (info/(m²·s)) = J·m²·s/info = kg·m⁴·s⁻¹/info  ✓

Complete System Summary

Master equation:
τ∂2s∂t2+∂s∂t=c2τ∇2s−∇⋅(svsub+χsu)+αE+β∇⋅(Evsub)+γ_F F−σirr
τ∂t2∂2s​+∂t∂s​=c2τ∇2s−∇⋅(svsub​+χsu)+αE+β∇⋅(Evsub​)+γ_F F−σirr​

Gravitational force:
Fgrav=ksvsub
Fgrav​=ksvsub

---

**Dimensional remark (ME-DR-1):** The master equation [ME] spans two dimensional domains:

(1) Transport-only core (no mass unit kg required — operates within D_C2 = {m, s}):
    τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) − σ_irr

(2) Energy-coupling extension (mass unit kg required via A-QUANT-3, the η extension):
    + α E + β ∇·(E v_sub) + γ_F F

The decoherence prediction Γ_φ = k_rot ω_rot² is derived from the quantum layer (C2_FOUNDATIONS.md §Subsystem 4) and is separate from the [ME] energy-coupling terms above.
