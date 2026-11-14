# Transport Summary: Dependency Graph and Unresolved Quantities

**Companion to:** `substrate_transport_derivation.md`  
**Symbolic checks:** `substrate_transport_sympy.py`  
**Numerical checks:** `substrate_transport_validation.py`

---

## 1. Dependency Graph

Each node is an equation or result. Edges point from premises to conclusions.  
Labels: **[D]** = derived (follows necessarily), **[A]** = assumption (new physical input), **[I]** = mathematical identity (no physical content), **[E]** = established in prior files.

```
══════════════════════════════════════════════════════════════════════
LAYER 0 — ESTABLISHED MICROSCOPIC ORIGIN
══════════════════════════════════════════════════════════════════════

[A] PRW-1: Information quanta carried by particles at speed v,
           reversal rate λ  (microscopic_derivation.md §1.2)
    │
    ▼
[D] Balance equations M1+, M1-  (exact)
    │
    ├──[I: add]──────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         ▼
[D] ∂s/∂t + ∂J/∂x = S_total       [C-s]     [D] ∂J/∂t + c²∂s/∂x + J/τ = S_J  [C-J]
    │                                                         │
    └─────────────────────[I: differentiate, substitute]──────┘
                                    │
                                    ▼
[D] Telegrapher equation: τ s_tt + s_t = c²τ s_xx  [TE]  ← ESTABLISHED
                                    │
                                    ▼
[D] Parameter dictionary: τ = 1/(2λ),  c = v,  D = c²τ    ← ESTABLISHED

══════════════════════════════════════════════════════════════════════
LAYER 1 — CONSERVATION LAWS  (this document, new)
══════════════════════════════════════════════════════════════════════

[C-s] + [I: integrate over space, periodic BCs]
    │
    ▼
[D] Q = ∫s dx conserved (source-free)  [CONS-1]   ← V3 ✓

[C-s] × c²s  +  [C-J] × J  +  [I: product rule]
    │
    ▼
[D] ∂E_sub/∂t + ∂(c²sJ)/∂x = −J²/τ              [ET]   ← V1 ✓
    where E_sub = ½c²s² + ½J²

[C-s] × J  +  [C-J] × s  +  [I: product rule]
    │
    ▼
[D] ∂P_sub/∂t + ∂E_sub/∂x = −P_sub/τ            [PT]   ← V2 ✓
    where P_sub = sJ

══════════════════════════════════════════════════════════════════════
LAYER 2 — SPECTRAL STRUCTURE
══════════════════════════════════════════════════════════════════════

[TE] + [A-lin: linearise around background]
    + [A-homog: uniform background]
    + [I: plane-wave ansatz exp(ikx − iωt)]
    │
    ▼
[D] Dispersion relation: ω² + (i/τ)ω − c²k² = 0   [DISP-EQ]

[DISP-EQ] + [I: quadratic formula]
    │
    ▼
[D] ω = −i/(2τ) ± √(c²k² − 1/(4τ²))              [DISP-SOL]
    │
    ├──[k > k_c]──────────────────────────────────────────────┐
    │                                                          │
    ▼                                                          ▼
[D] Propagating: Ω₁(k) = √(c²k²−1/(4τ²))  ← V4 ✓    [D] Evanescent: pure decay  ← V5 ✓
    │
    ▼
[D] Critical wavenumber: k_c = 1/(2cτ) = λ/c       [DEF-kc]  ← V10 ✓

══════════════════════════════════════════════════════════════════════
LAYER 3 — ANGULAR QUANTITIES
══════════════════════════════════════════════════════════════════════

[C-J-drift] + [I: take curl, use curl(grad s) = 0]
    │
    ▼
[D] ∂Ω_J/∂t = −(1/τ)Ω_J − (2s/τ)ω_sub            [VORT-J]

[VORT-J] + [∂Ω_J/∂t = 0]
    │
    ▼
[D] Steady state: Ω_J = −2s·ω_sub                  [VORT-SS]  ← V7 ✓

[I: rotating frame velocity transform v' = v − ω_rot×r]
    │
    ▼
[D] ω_sub|_rotating = ω_sub|_lab − ω_rot           [VORT-FRAME]

[VORT-FRAME] + [A-symm: irrotational background, ω_sub|_lab = 0]
    │
    ▼
[D] ω_rot = −ω_sub|_rotating                        [ID-omega-vorticity]

══════════════════════════════════════════════════════════════════════
LAYER 4 — CURRENT PERTURBATION AND VARIANCE
══════════════════════════════════════════════════════════════════════

J = s·v_sub  +  [I: kinematic frame transform]
    │
    ▼
[D] δJ = s₀(ω_rot × r)                             [ESTABLISHED-DJ]

[ESTABLISHED-DJ] + [I: |ω×r|² = ω²r²sin²θ] + [I: ⟨sin²θ⟩_sphere = 2/3]
    │
    ▼
[D] ⟨|δJ|²⟩ = (2/3) s₀² ω_rot² r²                 [ESTABLISHED-VAR]  ← V8 ✓

══════════════════════════════════════════════════════════════════════
LAYER 5 — DECOHERENCE   ← OBSTRUCTION POINT
══════════════════════════════════════════════════════════════════════

[ESTABLISHED-VAR]
    │
    ╔═══════╧═══════════════════════════════════════════════╗
    ║  OBSTRUCTION OB-1                                     ║
    ║  [CA-3]: Γ ∝ ⟨(δJ)²⟩                                ║
    ║  NOT derivable from [ME] or transport equations       ║
    ║  Requires: quantum-classical coupling postulate        ║
    ╚═══════════════════════════════════════════════════════╝
    │  (given CA-3)
    ▼
[D] Γ_rot = (κ/(ℏs₀²r²)) × (2/3)s₀²ω_rot²r²
          = (2κ/3ℏ) ω_rot²
    │
    ╔═══════╧═══════════════════════════════════════════════╗
    ║  OBSTRUCTION OB-2                                     ║
    ║  κ = dimensionless coupling constant                  ║
    ║  NOT determined by (v, λ, c, τ)                      ║
    ║  Requires: calibration or first-principles QM         ║
    ╚═══════════════════════════════════════════════════════╝
    │  (given κ)
    ▼
[D] Γ = Γ₀ + k_rot ω_rot²,   k_rot = 2κ/(3ℏ)       [D6]
```

---

## 2. Complete Equation Inventory

### 2.1 Derived Equations (no additional assumptions beyond listed ones)

| Label | Equation | Derives from | Numerical check |
|-------|----------|-------------|-----------------|
| [C-s] | ∂s/∂t + ∂J/∂x = S_total | M1+, M1- | S1 (symbolic) |
| [C-J] | ∂J/∂t + c²∂s/∂x + J/τ = S_J | M1+, M1- | S1 (symbolic) |
| [CONS-1] | d/dt∫s dx = 0 | [C-s] + BCs | V3 |
| [ET] | ∂E_sub/∂t + ∂(c²sJ)/∂x = −J²/τ | [C-s],[C-J] | V1 |
| [PT] | ∂P_sub/∂t + ∂E_sub/∂x = −P_sub/τ | [C-s],[C-J] | V2 |
| [DISP-EQ] | ω²+(i/τ)ω−c²k²=0 | [TE]+linearise | S3 (symbolic) |
| [DISP-SOL] | ω=−i/(2τ)±√(c²k²−1/4τ²) | [DISP-EQ] | V4, V5 |
| [DEF-kc] | k_c = λ/c | [DISP-SOL] | V10 |
| [VORT-J] | ∂Ω_J/∂t = −Ω_J/τ − 2s·ω_sub/τ | [C-J]+curl | S8 (symbolic) |
| [VORT-SS] | Ω_J = −2s·ω_sub | [VORT-J]+steady state | V7 |
| [VORT-FRAME] | ω_sub|_rot = ω_sub|_lab − ω_rot | kinematic identity | S9 (symbolic) |
| [ID-omega-vorticity] | ω_rot = −ω_sub|_rot (irrotational bg) | [VORT-FRAME]+A-symm | — |
| [ESTABLISHED-DJ] | δJ = s₀(ω_rot×r) | J=sv_sub + frame transform | S10 (symbolic) |
| [ESTABLISHED-VAR] | ⟨\|δJ\|²⟩=(2/3)s₀²ω_rot²r² | [ESTABLISHED-DJ]+∫sin²θ | V8 |
| [D6] | Γ=Γ₀+k_rot ω_rot² | given [CA-3]+[ESTABLISHED-VAR] | — |

### 2.2 Assumptions (physical input, not derivable from [ME])

| Label | Statement | Where used | Consequence if wrong |
|-------|-----------|------------|---------------------|
| [PRW-1] | Information quanta carried by PRW particles | All of Layer 0 | Entire chain collapses |
| [A-SF] | Source-free, drift-free limit | [CONS-1] | Q may not be conserved |
| [A-drift] | Uniform v_sub (slowly varying) | [C-J-drift] | Extra spatial gradient terms appear |
| [A-slow-v] | v_sub varies slowly (same as [A1]) | [ET] with drift | Extra τ∂(·)/∂t corrections |
| [A-lin] | Small perturbations δs ≪ s̄ | [DISP-EQ] | Nonlinear dispersion |
| [A-homog] | Uniform background on scale 1/k | [DISP-EQ] | Position-dependent dispersion |
| [A-symm] | Irrotational background | [ID-omega-vorticity] | ω_rot ≠ −ω_sub|_rot in general |
| [CA-3] | Γ ∝ ⟨(δJ)²⟩ | [D6] | Decoherence formula invalid |

### 2.3 Mathematical Identities (zero physical content)

| Identity | Statement | Used in |
|----------|-----------|---------|
| ∇×∇s = 0 | Curl of gradient is zero | [VORT-J] |
| ∇×(ω×r) = 2ω | For uniform ω | [VORT-FRAME] |
| ⟨sin²θ⟩ = 2/3 | Sphere average | [ESTABLISHED-VAR] |
| Product rule for divergence | c²s∂J/∂x + c²J∂s/∂x = c²∂(sJ)/∂x | [ET] |
| Quadratic formula | Applied to [DISP-EQ] | [DISP-SOL] |
| Divergence theorem | ∫∂J/∂x dx = [J]_boundary | [CONS-1] |

---

## 3. Angular Quantities: Identification and Fate

Three angular quantities arise independently. Only one survives to the decoherence formula.

| Symbol | Definition | Origin | Enters Γ? | Notes |
|--------|-----------|--------|-----------|-------|
| Ω₁(k) | √(c²k²−1/(4τ²)) | Dispersion relation [DISP-SOL] | **No** | Oscillation frequency of substrate mode k; fully determined by (k,c,τ) |
| ω_sub | (1/2)∇×**v**_sub | Substrate vorticity [DEF-omega-sub] | **Indirectly** | Equal to −ω_rot in rotating frame for irrotational background |
| ω_rot | External frame rotation rate | Kinematic transform [RF] | **Yes** | The ω in Γ = Γ₀ + k_rot ω² |

**Why Ω₁ does not appear in Γ:**  
The decoherence perturbation δJ = s₀(ω_rot×r) is linear in **r**, which has support at all wavenumbers. No single mode k is selected by the rotation. Therefore Ω₁(k) for a specific k cannot be identified with ω_rot without a mode-selection mechanism that is not present in the theory.

**Why ω_sub is equivalent to ω_rot (for irrotational backgrounds):**  
By [VORT-FRAME], ω_sub|_rot = −ω_rot when the background is irrotational. This is an exact kinematic identity, not an assumption. It means ω_rot and |ω_sub|_rot| are the same quantity measured with opposite sign conventions.

---

## 4. Unresolved Quantities

### 4.1 Obstruction OB-1: The Constitutive Coupling [CA-3]

**What it is:**  
The postulate Γ ∝ ⟨(δJ)²⟩, connecting information-current variance to quantum decoherence rate.

**Why it cannot be derived from the transport equations:**  
The transport equations [C-s, C-J] are classical field equations for the information density and flux. They describe how the substrate field evolves. They do not contain any quantum operator, any Hilbert space, or any description of a quantum system coupled to the substrate. The decoherence rate Γ is a property of a quantum system; the current variance ⟨(δJ)²⟩ is a property of the classical field. The connection between them requires specifying the quantum-classical coupling Hamiltonian H_int = f(s, J) × (quantum operator), from which Γ follows by standard Fermi's golden rule or Lindblad theory.

**What is needed to resolve it:**  
An explicit interaction Hamiltonian H_int that couples the substrate field (s or J) to the quantum system's Hilbert space. This is a quantum gravity / quantum information postulate that lies outside classical transport theory.

**What can be said without resolving it:**  
The transport theory establishes that the relevant classical quantity is ⟨(δJ)²⟩ ∝ ω_rot², so if any linear coupling exists between field variance and decoherence rate, the result Γ ∝ ω_rot² is guaranteed. The functional form is derived; only the coefficient requires the coupling.

### 4.2 Obstruction OB-2: The Coupling Constant κ

**What it is:**  
The dimensionless number in k_rot = 2κ/(3ℏ). Currently calibrated to give k_rot = 4.5×10⁻⁷ s, which implies κ ≈ 7.1×10⁻⁴¹.

**Why it cannot be derived:**  
κ is the ratio of the quantum-classical coupling strength to the quantum of action ℏ. Determining it requires knowledge of the microscopic quantum substrate interaction, which is not specified by the PRW or the transport equations.

**What is needed to resolve it:**  
A first-principles calculation of the substrate–qubit coupling energy, analogous to how the fine structure constant α relates the electron charge to fundamental constants. Until then κ is an empirical input, as acknowledged in UNIFIED_PERTURBATIVE_DERIVATION.md §7.3 (CJ-3).

### 4.3 Unresolved: The Saturation Frequency ω_max

**Context:**  
The full decoherence model in COMPLETE_MASTER_EQUATION.md contains:
```
Γ = Γ₀ + k_rot ω²/(1+(ω/ω_max)²)
```
The transport theory derivation (Section 5) produces a dispersion cutoff at frequency c·k_c = 1/(2τ) = λ. The candidate identification is:

```
ω_max = c·k_c = λ = 1/(2τ)    [CANDIDATE]
```

**What the transport theory says:**  
For ω < c·k_c: the corresponding substrate mode is evanescent (no propagating wave). For ω > c·k_c: the mode propagates. The coupling of a rotating system to substrate modes would be suppressed below c·k_c.

**Why this identification is not yet established:**  
The identification [CANDIDATE] would require showing that:  
(a) the decoherence rate is dominated by resonant coupling to propagating modes, and  
(b) the coupling amplitude is proportional to the mode frequency ω (not to k or to the group velocity).

Neither (a) nor (b) follows from the current transport equations without additional mode-coupling assumptions. The identification remains a hypothesis, not a derivation.

**Quantitative check:**  
If ω_max = λ = 1/(2τ), then using ω_max = 10⁶ rad/s gives:
```
λ = 10⁶ s⁻¹    →    τ = 5×10⁻⁷ s    →    D = c²τ
```
For c = 3×10⁸ m/s: D = (3×10⁸)²×(5×10⁻⁷) = 4.5×10¹⁰ m²/s — physically unreasonable for a substrate diffusivity. For a sub-luminal substrate speed c_sub ≪ c_light, the numbers can be reconciled, but c_sub is then a free parameter.

---

## 5. What Is and Is Not Microscopically Defined

| Quantity | Status | Microscopic expression |
|----------|--------|----------------------|
| τ | ✓ Fully defined | 1/(2λ) |
| c | ✓ Fully defined | v (particle speed) |
| D | ✓ Fully defined | c²τ = v²/(2λ) |
| k_c | ✓ Fully defined | λ/c |
| Ω₁(k) | ✓ Fully defined | √(c²k²−1/(4τ²)) |
| ω_rot | ✓ Fully defined (external) | Frame rotation rate — imposed, not derived from substrate |
| ω_sub | ✓ Fully defined | (1/2)∇×**v**_sub |
| ω_rot vs ω_sub | ✓ Equivalent (irrot. bg) | ω_rot = −ω_sub\|_rot |
| k_rot functional form | ✓ Functional form derived | Γ ∝ ω_rot² — derived |
| k_rot magnitude | ✗ Not defined | k_rot = 2κ/(3ℏ) — κ is empirical |
| ω_max | ✗ Not defined | Candidate: λ, but requires mode-coupling argument |
| [CA-3] | ✗ Postulate | Γ ∝ ⟨(δJ)²⟩ — not derivable from [ME] |

---

## 6. Minimum Additional Input to Complete the Chain

To close the remaining gaps, exactly two additional physical inputs are needed:

**Input 1 (resolves OB-1):** A quantum interaction Hamiltonian specifying how the substrate information current J couples to a two-level quantum system. Concretely:

```
H_int = g · J(x_qubit) · σ_z
```

for some coupling constant g [J·m²·s/info]. From H_int, the decoherence rate follows by second-order perturbation theory:

```
Γ = (g²/ℏ²) × ∫₀^∞ ⟨J(x,t)J(x,0)⟩ dt
```

The current correlator ⟨J(t)J(0)⟩ can be computed from the transport equations. This would replace [CA-3] with a derivation and simultaneously determine κ in terms of g. 

**Input 2 (resolves OB-2 and the saturation):** A spectral density of the substrate current fluctuations S_J(ω), computed from the transport equations:

```
S_J(ω) = ∫_{-∞}^{∞} ⟨J(t)J(0)⟩ exp(iωt) dt
```

From the dispersion relation [DISP-SOL], the spectral density of a substrate in thermal equilibrium at temperature T would have a Lorentzian form with the natural cutoff at ω = c·k_c. This would simultaneously determine ω_max and the ω-dependence of Γ, replacing both the Lorentzian ansatz and ω_max as free parameters with derived quantities.

Both inputs are standard tools of open quantum systems theory (system-bath coupling, spectral density calculation). Neither requires new physics — only the application of existing quantum machinery to the substrate transport field.

---

*Document complete. All gaps precisely identified. No quantities invented to fill them.*
