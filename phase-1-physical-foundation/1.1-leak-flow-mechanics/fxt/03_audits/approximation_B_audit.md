# Approximation B Audit: Source-Free Approximation

**Audit objective:** Determine whether restoring source terms E, F, σ_irr produces previously discarded quantum interactions.

## B.1 Original Approximation

From UNIFIED_PERTURBATIVE_DERIVATION.md Section 1.2:

**[A2] Source-free exterior region.**
No mass-energy sources in the region of interest: E = 0, F = 0, σ_irr = 0.
Justification: the test particle and the quantum system are treated as probes; the gravitating body is a boundary condition, not a distributed source in the domain.
Effect: the right-hand side of [ME] reduces to the diffusion term only.

## B.2 Complete Master Equation with Sources (Frozen)

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) + αE + β∇·(E v_sub) + γF − σ_irr   [ME]
```

Under [A2], the source terms vanish:
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u)   [ME-source-free]
```

## B.3 Audit Question

**What source terms were discarded?**
1. **Direct energy coupling**: αE
2. **Energy flow coupling**: β∇·(E v_sub)  
3. **Force coupling**: γF
4. **Irreversible loss**: σ_irr

**Can any source term produce a previously discarded interaction?**

To answer this, I need to restore each term and analyze whether it introduces quantum coupling mechanisms.

## B.4 Restored Source Analysis

### B.4.1 Direct Energy Coupling: αE

**Term**: +αE where α = info/(J·s), E = energy density (J/m³)

**Physical meaning**: Energy density creates information density at rate α.

**Mathematical structure**: This is a **scalar source term**. E is a classical energy density field, α is a scalar coupling constant.

**Quantum coupling analysis**:
- E could represent the energy density of a quantum system: E = ⟨H_quantum⟩/V
- The term αE then becomes α⟨H_quantum⟩/V
- This creates information s proportional to the quantum energy expectation value

**Key question**: Does this introduce quantum internal coupling?

**Analysis**: The term αE creates information density s from quantum energy, but:
1. It acts as a **classical source** - it adds to the scalar field s
2. The coupling α⟨H_quantum⟩/V → s is **one-way** (energy creates information)  
3. There is no **back-action** from s to the quantum system within this term
4. The term preserves the **scalar nature** of the master equation

This is a quantum-to-classical coupling, not an internal quantum coupling that would affect quantum coherence between internal states.

### B.4.2 Energy Flow Coupling: β∇·(E v_sub)

**Term**: +β∇·(E v_sub) where β = info·s/J

**Physical meaning**: Flowing energy creates information.

**Mathematical expansion**:
```
β∇·(E v_sub) = β(v_sub·∇E + E ∇·v_sub)
```

Under approximation [A5] (incompressible), ∇·v_sub = 0:
```
β∇·(E v_sub) = β v_sub·∇E
```

**Quantum coupling analysis**:
If E = ⟨H_quantum⟩/V, then:
```
∇E = ∇(⟨H_quantum⟩/V) = (1/V)∇⟨H_quantum⟩
```

The term becomes:
```
β v_sub·∇E = (β/V) v_sub·∇⟨H_quantum⟩
```

**Analysis**: 
- This couples the **gradient** of quantum energy to substrate flow
- It's still a classical source term for the scalar field s
- No internal quantum structure (no coupling between different quantum states)
- No back-action from s to quantum system

Like the αE term, this represents quantum-to-classical energy transfer, not internal quantum coupling.

### B.4.3 Force Coupling: γF

**Term**: +γF where γ = info/(N·s), F = force density (N/m³)

**Physical meaning**: Force generates information.

**Quantum coupling analysis**:
If the force comes from a quantum system, F could represent:
1. **Quantum pressure**: F = ∇·⟨T_quantum⟩ where T is quantum stress tensor
2. **Quantum force density**: F = -∇⟨H_quantum⟩ (gradient of quantum energy)
3. **Electromagnetic force**: F = ρ_charge E_field + J_current × B_field

**Analysis of quantum force sources**:

**Case 1: F = ∇·⟨T_quantum⟩**
- This couples quantum stress to information creation
- Still a classical scalar source for s
- No internal quantum coupling

**Case 2: F = -∇⟨H_quantum⟩**  
- This is equivalent to the energy flow term β∇·(E v_sub) in a different form
- Same conclusion: quantum-to-classical coupling only

**Case 3: Electromagnetic force**
- If quantum system has charge/current, electromagnetic forces can act on it
- This could create position-dependent forces on quantum systems
- But the γF term in master equation creates information from force, not force from information
- Still one-way coupling: quantum electromagnetic properties → information density

**Conclusion**: The γF term allows various quantum mechanical forces to create information density, but does not introduce internal quantum coupling within the quantum system itself.

### B.4.4 Irreversible Loss: σ_irr

**Term**: -σ_irr where σ_irr = irreversible entropy production rate (info/(m³·s))

**Physical meaning**: Information is irreversibly lost (converted to entropy).

**Quantum coupling analysis**:

In quantum thermodynamics, irreversible entropy production is associated with:
1. **Decoherence processes**: Loss of quantum coherence
2. **Measurement processes**: Wavefunction collapse
3. **Open system evolution**: Coupling to environment

**Critical analysis**:

**Decoherence interpretation**: 
σ_irr could represent the rate at which quantum information is lost due to decoherence:
```
σ_irr = -d/dt S_quantum = -d/dt Tr(ρ log ρ) / volume
```

This **directly connects** to quantum decoherence mechanisms!

**Key question**: Does this represent genuine internal quantum coupling?

**Analysis**:
1. **If σ_irr = decoherence rate**: Then the master equation becomes:
   ```
   ∂s/∂t = ... + d/dt Tr(ρ log ρ) / volume
   ```
   This couples quantum decoherence to classical information dynamics.

2. **Direction of coupling**: The term -σ_irr removes information from s due to quantum decoherence. This is **quantum → classical** coupling.

3. **Back-action**: For true internal quantum coupling, we need s to affect quantum evolution. The σ_irr term shows quantum affecting s, but not s affecting quantum.

4. **Missing link**: To complete the coupling loop, we need a term showing how s affects quantum evolution (s → quantum). This term is not in the master equation.

**Conclusion for σ_irr**: This term represents quantum decoherence affecting classical information density, but lacks the reverse coupling needed for full quantum internal coupling.

## B.5 Combined Source Effects

### B.5.1 Full Source-Restored Equation

With all sources restored:
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(s v_sub + χ s u) 
                    + α⟨H_quantum⟩/V + β v_sub·∇⟨H_quantum⟩/V + γF_quantum − σ_irr,quantum
```

### B.5.2 Perturbation Analysis with Sources

Following the perturbation expansion s = s₀ + s₁ + s₂ + ... :

**Background equation (O(ε⁰))**:
```
c²τ ∇²s₀ = ∇·(s₀ v_sub) - α⟨H_quantum⟩/V - β v_sub·∇⟨H_quantum⟩/V - γF_quantum + σ_irr,quantum
```

**Key observation**: The source terms modify the background field s₀. Instead of the pure Newtonian s₀ = μ/r, we get:
```
s₀ = s₀,Newton + s₀,quantum_sources
```

The quantum source contribution s₀,quantum_sources depends on the quantum energy distribution, forces, and decoherence rate.

**First-order equation (O(ε¹))**:
```
c²τ ∇²s₁ = v·∇s₀ + quantum_source_perturbations
```

**Second-order equation (O(ε²))**:
```
c²τ ∇²s₂ = v·∇s₁ + higher_order_quantum_sources  
```

### B.5.3 Impact on δs Field

The second-order field δs = s₂ gets modified by quantum sources. Instead of:
```
δs = -μL²/(c²r³)   [pure gravitational]
```

we get:
```
δs = -μL²/(c²r³) + δs_quantum_sources   [gravitational + quantum contributions]
```

**Critical question**: Does δs_quantum_sources introduce internal quantum coupling?

**Analysis**: The quantum source terms create additional contributions to the information density field s, but they still result in a **classical scalar field**. The δs_quantum_sources represents how quantum energy, forces, and decoherence modify the information density, but:

1. **Field nature**: δs remains a classical scalar field on physical space
2. **Coupling mechanism**: The existing coupling mechanisms (gravity: F = ks v_sub, decoherence: Γ ∝ ⟨|δJ|²⟩) act on the total δs
3. **No new structure**: No new mathematical structure (operators, matrices, Hilbert spaces) emerges

## B.6 Matter Coupling Analysis

The restored sources modify how quantum systems create information density, but the coupling from information back to matter still occurs through the frozen constitutive rules:

### B.6.1 Gravity Branch
```
F_grav = k s v_sub = k (s₀ + δs_quantum_sources) v_sub
```

The quantum sources contribute to gravitational force, but through the same classical coupling mechanism.

### B.6.2 Decoherence Branch
```
Γ ∝ ⟨|δJ|²⟩ where δJ = (s₀ + δs_quantum_sources)(ω × r)
```

The quantum sources contribute to decoherence rate, but through the same classical current coupling.

## B.7 Dimensional Analysis

**Source term units check**:
- αE: (info/(J·s)) × (J/m³) = info/(m³·s) ✓
- β∇·(E v_sub): (info·s/J) × (J/m³) × (s⁻¹) = info/(m³·s) ✓  
- γF: (info/(N·s)) × (N/m³) = info/(m³·s) ✓
- σ_irr: info/(m³·s) ✓

All source terms have consistent units with ∂s/∂t.

## B.8 Verdict Analysis

**Why was the source-free approximation introduced?**
To focus on the exterior region where test particles probe the field, treating massive sources as boundary conditions rather than distributed sources.

**What mathematical terms were discarded?**
- Direct energy coupling: αE
- Energy flow coupling: β∇·(E v_sub)
- Force coupling: γF  
- Irreversible loss: σ_irr

**Can those source terms produce a previously discarded interaction?**
**PARTIALLY.** The source terms allow quantum systems to influence the information density field s through:
- Energy density → information creation (αE)
- Energy flow → information creation (β∇·(E v_sub))
- Force → information creation (γF)
- Decoherence → information loss (σ_irr)

However, these represent **one-way quantum-to-classical couplings**. They allow quantum systems to modify the classical information field, but they do not introduce **back-action** from the information field to quantum internal degrees of freedom.

**Does removing the approximation change the mathematical structure?**
**NO.** The master equation remains a linear, real-valued, classical scalar PDE. The quantum sources modify the inhomogeneity but preserve the classical nature of the field equation.

**Does it generate an operator-valued interaction?**  
**NO.** All source terms contribute scalar values to a scalar equation.

**Does it introduce a Hamiltonian naturally?**
**NO.** The equation remains dissipative and classical. The quantum sources don't change this fundamental character.

**Does it produce an experimentally controllable observable?**
**YES, PARTIALLY.** The quantum source terms modify both the gravitational force and decoherence rate:
- Gravity: F = k(s₀ + δs_quantum)v_sub - quantum energy/forces affect gravitational coupling
- Decoherence: Γ ∝ ⟨|(s₀ + δs_quantum)(ω × r)|²⟩ - quantum sources affect decoherence

But these observables are still controlled through the **same classical coupling mechanisms** - no new internal quantum coupling emerges.

## B.9 Final Conclusion

**APPROXIMATION B PARTIALLY AFFECTS QUANTUM COUPLING**

The source-free approximation removes quantum-to-classical coupling mechanisms that allow quantum systems to influence the information density field. However, these couplings are **unidirectional** - they lack the classical-to-quantum back-action needed for true internal quantum coupling.

**Key finding**: Restoring sources enables quantum systems to modify the substrate field s, which then affects both gravitational and decoherence observables through existing coupling rules. This could create **experimentally observable effects** but does not constitute the missing "internal quantum coupling" because:

1. The coupling remains mediated by the classical scalar field s
2. No direct coupling between different internal quantum states emerges
3. The quantum system affects the substrate, but the substrate coupling to quantum system still requires the existing constitutive assumptions (CA-1, CA-2, CA-3)

**Status**: Source restoration enables enhanced quantum-classical interaction but does not solve the internal quantum coupling problem.