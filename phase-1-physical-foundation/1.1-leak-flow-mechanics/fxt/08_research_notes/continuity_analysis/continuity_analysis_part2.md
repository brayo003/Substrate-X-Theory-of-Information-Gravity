# Part 2: Source/Sink Analysis

**Objective**: Determine precisely whether R represents creation, destruction, exchange, transport, dissipation, or something else.

## 2.1 Source Term Decomposition

From Part 1, the complete source term is:
```
R = αE + β∇·(E v_sub) + γF − σ_irr
```

We analyze each term mathematically before inferring physical meaning.

## 2.2 Mathematical Analysis of Each Term

### Term 1: Direct Energy Coupling (αE)

**Mathematical structure**: 
- Linear in E: R₁ = αE  
- Coupling constant: α [info/(J·s)]
- Energy density: E [J/m³]

**Sign analysis**: α > 0 (from frozen documents) ⟹ R₁ > 0 when E > 0

**Mathematical conclusion**: This term **creates** information density at rate proportional to energy density.

### Term 2: Energy Flow Coupling (β∇·(E v_sub))

**Mathematical structure**:
- Divergence of energy flux: ∇·(E v_sub)
- Coupling constant: β [info·s/J]  
- Energy flux: E v_sub [J/(m²·s)]

**Divergence analysis**:
```
∇·(E v_sub) = v_sub·∇E + E ∇·v_sub
```

**Sub-case 2a**: If ∇·v_sub = 0 (incompressible flow)
```
β∇·(E v_sub) = β v_sub·∇E
```

**Sub-case 2b**: If ∇·v_sub ≠ 0 (compressible flow)  
```
β∇·(E v_sub) = β v_sub·∇E + βE ∇·v_sub
```

**Sign analysis**: 
- β > 0 (from frozen documents)
- Sign depends on ∇E and ∇·v_sub locally

**Mathematical conclusion**: This term **creates** or **destroys** information depending on:
- Energy gradient direction relative to substrate flow
- Substrate flow compressibility

### Term 3: Force Coupling (γF)

**Mathematical structure**:
- Linear in force density: R₃ = γF
- Coupling constant: γ [info/(N·s)]
- Force density: F [N/m³]

**Sign analysis**: γ > 0, sign depends on F

**Mathematical conclusion**: This term **creates** information when F > 0, **destroys** when F < 0.

### Term 4: Irreversible Loss (-σ_irr)

**Mathematical structure**:
- Always negative: R₄ = -σ_irr
- Irreversible production rate: σ_irr ≥ 0 [info/(m³·s)]

**Sign analysis**: R₄ ≤ 0 always (σ_irr ≥ 0 by definition of irreversible process)

**Mathematical conclusion**: This term **always destroys** information density.

## 2.3 Net Source/Sink Classification

The total source term:
```
R = R₁ + R₂ + R₃ + R₄ = αE + β∇·(E v_sub) + γF − σ_irr
```

**Mathematical behavior**:

**Creation terms**: αE, γF (when F > 0), β∇·(E v_sub) (when locally positive)

**Destruction terms**: σ_irr (always), γF (when F < 0), β∇·(E v_sub) (when locally negative)

**Net effect**: R can be positive, negative, or zero depending on local values of E, F, ∇E, v_sub, and σ_irr.

## 2.4 Thermodynamic Character Analysis

### Reversible vs Irreversible Components

**Reversible components**: αE, β∇·(E v_sub), γF
- These terms are **algebraically reversible** (can be positive or negative)
- Represent **exchange** between energy/force and information

**Irreversible component**: σ_irr  
- This term is **thermodynamically irreversible** (always ≥ 0)
- Represents **dissipation** (one-way destruction of information)

## 2.5 Conservation Analysis

### Local Conservation
The equation can be written as:
```
τ ∂²s/∂t² + ∂s/∂t + ∇·J_eff = R
```

Where J_eff includes diffusion: J_eff = s v_sub + χ s u - c²τ ∇s

**Analysis**: This is **NOT** a local conservation law because R ≠ 0 in general.

### Total Information Change Rate
For arbitrary volume V:
```
d/dt ∫_V s dV = ∫_V (∂s/∂t) dV = ∫_V (-τ ∂²s/∂t² + ∇·J_eff + R) dV
```

**Result**: Information density is **NOT locally conserved** due to source/sink terms.

## 2.6 Equilibrium Analysis

### Steady-State Condition (∂s/∂t = ∂²s/∂t² = 0)
```
∇·J_eff = R
```

**Interpretation**: In equilibrium, information **current divergence balances sources**.

**Mathematical requirement**: R must have the spatial structure compatible with ∇·J_eff.

### Source-Free Equilibrium (R = 0)
Requires simultaneously:
- αE = 0 (no energy) OR
- β∇·(E v_sub) + γF = σ_irr (creation balances destruction)

**Special case**: If E = F = σ_irr = 0:
```
∇·(s v_sub + χ s u - c²τ ∇s) = 0
```

This is the source-free equation used in UNIFIED_PERTURBATIVE_DERIVATION.md.

## 2.7 Dimensional Consistency Verification

**αE term**: [α][E] = [info/(J·s)] × [J/m³] = [info/(m³·s)] ✓

**β∇·(E v_sub) term**: [β][E][v/L] = [info·s/J] × [J/m³] × [1/s] = [info/(m³·s)] ✓

**γF term**: [γ][F] = [info/(N·s)] × [N/m³] = [info/(m³·s)] ✓

**σ_irr term**: [σ_irr] = [info/(m³·s)] ✓

All terms have consistent units matching [∂s/∂t].

## 2.8 Mathematical Classification of R

**Primary mathematical character**: **Mixed source/sink term**

**Detailed classification**:

1. **Creation mechanisms**: 
   - Energy-to-information conversion (αE)
   - Force-to-information conversion (γF when F > 0)  
   - Energy-flow-to-information conversion (β∇·(E v_sub) when positive)

2. **Destruction mechanism**:
   - Irreversible information loss (σ_irr)
   - Force-induced destruction (γF when F < 0)
   - Energy-flow-induced destruction (β∇·(E v_sub) when negative)

3. **Exchange character**:
   - Bidirectional coupling between information and energy/force
   - Energy and forces can both create and destroy information
   - Only σ_irr is unidirectional (destruction only)

4. **Non-conserved system**:
   - Net information is NOT conserved locally
   - Sources can create information from energy/force
   - Sinks destroy information irreversibly

## 2.9 Implications for Back-Action

**Mathematical structure analysis**:

**Forward coupling** (energy/force → information): All terms in R represent how external fields (E, F) influence information density s.

**Reverse coupling** (information → energy/force): The source term R does NOT contain any mechanism by which s influences E or F.

**Mathematical conclusion**: The source structure is **unidirectional** - external fields affect information, but information does not affect external fields through R.

**Critical finding**: The source/sink analysis reveals **no mathematical basis for back-action** within the R term. Any back-action would require additional coupling mechanisms outside the source term structure.