# QUANTUM / ENVIRONMENT HISTORY AUDIT
## Did the Project Already Contain the Architecture: Quantum Substrate → PRW → Environment → C±?

**Date:** 2026-08-22  
**Scope:** Full forensic search of fxt/ (all .md, .py, .txt, .json)  
**Method:** Grep for all quantum/bath/coherence/source terms; read every relevant file; classify all prior work.

---

## 1. Executive Verdict

**YES — PARTIAL: the architecture existed in prior work, but C± was never derived from it.**

The project already contained, in files dated 2026-07-21 through 2026-07-25, a substantially complete chain:

```
Classical substrate (PRW)
    ↓ [interaction Hamiltonian: H_int = g J σ_z]
Quantum qubit (ℂ²)
    ↓ [Born-Markov-Secular approximation]
Lindblad master equation (bath = substrate current fluctuations)
    ↓ [Γ_φ = k_rot · ω_rot²]
Qubit decoherence prediction
```

This chain is fully written up in `02_derivations/interaction_hamiltonian_derivation.md`, `decoherence_chain_summary.md`, and `effective_master_equation_derivation.md`. It was validated in `04_validations/interaction_hamiltonian_validation.py`, `effective_master_equation_validation.py`, and numerically confirmed in `05_simulations/decoherence_prediction.py`.

**What was NOT in this prior work:**
The prior architecture treats the substrate as the *environment/bath* acting on an external qubit. The substrate creates decoherence of an independently introduced qubit. The substrate itself does not have a quantum parent — the PRW is still the substrate, and C± (the information creation source term) is absent from this chain entirely. The C± term was treated as a separate, unrelated issue.

**Therefore:**
- Continuing Q7 (quantum parent → PRW → C±) is NOT redundant with the prior work.
- The prior work answers a different question: "how does the classical PRW substrate decohere a qubit?"
- Q7 asks: "can the PRW itself be derived as the coarse-grained limit of a quantum microscopic theory, and does that theory supply C±?"
- These are structurally related but mathematically distinct questions.

**Q7 is the completion of unfinished prior work — specifically of the chain from the microscopic foundation (not the decoherence chain).**

---

## 2. Historical Timeline

| Date | File | Mechanism | Status |
|------|------|-----------|--------|
| 2026-07-21 | `02_derivations/interaction_hamiltonian_derivation.md` | H_int = g J σ_z, Born-Markov, Lindblad | EQUATIONS, not C± derivation |
| 2026-07-21 | `02_derivations/interaction_hamiltonian_uniqueness.md` | Uniqueness/non-uniqueness of H_int | DERIVATION — proves H_int not derivable from substrate alone |
| 2026-07-21 | `02_derivations/decoherence_chain_summary.md` | Complete PRW → Lindblad → Γ_φ chain | DERIVATION — but C± is not in this chain |
| 2026-07-21 | `02_derivations/effective_master_equation_derivation.md` | Bloch-Redfield → Lindblad reduction | DERIVATION — qubit ME, not substrate C± |
| 2026-07-21 | `09_archived_tests/minimal_origin_Hilbert/minimal_origin_of_complex_Hilbert_spaces_audit.md` | Can complex Hilbert space be forced from first principles? | AUDIT — foundational, not C± |
| 2026-07-21 | `03_audits/prw_deeper_substrate_audit.md` | Does a deeper microscopic theory generate PRW? | AUDIT — tests BGK, LBM, quantum walk. Quantum walk forbidden by explicit assumption |
| 2026-07-24 | `03_audits/C2_structural_obstruction_audit.md` | Five structural failures of C2 | AUDIT — correctly identifies F3 (no info-energy bridge), F4 (no complex structure) |
| 2026-07-24 | `01_foundations/C2_MISSING_PRINCIPLES.md` | Minimal missing principles for C2 | AUDIT — correctly states ℏ is missing, g is undetermined |
| 2026-07-25 | `01_foundations/C2_FOUNDATIONS.md` | Complete C2 status | SUMMARY — correctly records all failures |
| 2026-08-21 | `09_spatiotemporal_c2_test/QUANTUM_MAPPING_NO_GO.md` | No-go for qubit coupling derivation | AUDIT — OB-A,B,C correctly stated |
| 2026-08-21 | `09_spatiotemporal_c2_test/34_C2_QUANTUM_BRANCH_STATUS.md` | Complete quantum branch status | AUDIT — frozen, no QPU access |
| 2026-08-22 | `09_spatiotemporal_c2_test/QUANTUM_ONTOLOGY_AUDIT.md` | PRW is classical, property table | NEW — Q1–Q6 |
| 2026-08-22 | `09_spatiotemporal_c2_test/QUANTUM_PARENT_DERIVATION.md` | Minimal quantum parent, C±_eff | NEW — Q7, partial success |

---

## 3. Prior Quantum Structure

The project contained extensive prior quantum structure — but in the direction *substrate acts on qubit*, not *qubit-like substrate generates PRW*.

### In 02_derivations/interaction_hamiltonian_derivation.md (2026-07-21)

Complete construction of:
- Qubit Hilbert space ℂ²
- Free Hamiltonian H_S = ½ℏω_q σ_z
- Interaction Hamiltonian H_int = g·J(x_q,t)·σ_z
- Born approximation: ρ_total = ρ_S ⊗ ρ_B
- Markov approximation: τ_corr << Γ⁻¹
- Secular approximation
- Full Lindblad master equation with L = σ_z

### In 02_derivations/decoherence_chain_summary.md (2026-07-21)

Complete 8-level chain: PRW → telegrapher → transport → current variance → H_int → Born-Markov → Lindblad → Γ_φ = k_rot·ω_rot²

Every step labelled [D]/[A]/[I]/[E]. Density matrices ρ_S(t), ρ_B used explicitly. Coherence ρ₀₁(t) = ρ₀₁(0)·exp(−Γ_φ·t) written down.

### In 09_archived_tests/minimal_origin_Hilbert (2026-07-21)

Full investigation of whether complex Hilbert spaces are forced by physical principles PR1–PR10. Multiple candidate theories tested (classical mechanics, KvN, Caldeira-Leggett, quantum walks). Result: ℂ-Hilbert space requires Local Tomography (BP-1) as the additional principle.

---

## 4. Prior Coarse-Graining

### In 03_audits/prw_deeper_substrate_audit.md (2026-07-21)

Full investigation of candidate microscopic theories generating PRW:
- D1: BGK kinetic theory → PRW exactly (isomorphic, no hidden structure)
- D2: Multi-velocity LBM → PRW only when rest particles removed
- D3 and beyond: explored

**Critical finding in this document:** The audit explicitly FORBIDS quantum starting points:

> "Forbidden starting assumptions: Hilbert spaces, wavefunctions, operators, commutators, M₂(ℂ), Moyal deformation, ℏ, decoherence, quantum walks, interaction Hamiltonians."

This is the moment the project explicitly blocked the quantum parent route. The PRW deeper substrate audit was restricted to classical candidates only.

### In 01_foundations/C2_FOUNDATIONS.md (2026-07-24–25)

Records coarse-graining in the context of FPUT → phonons → PRW:
- Theorem FPUT-3: PRW is the unique local coarse-grained projection of FPUT acoustic modes
- Coarse-graining of phase information φₖ produces PRW density s(x,t)

---

## 5. Prior Environment/Bath

The prior work contains an explicit, fully developed environment/bath mechanism — but it goes in the direction: substrate = bath → qubit decoherence.

### In 02_derivations/interaction_hamiltonian_derivation.md

The substrate current J(x,t) is the bath field. The qubit ρ_S is the system. The coupling H_int = g·J·σ_z makes the substrate fluctuations act as a stochastic field that dephases the qubit.

- Bath = substrate current fluctuations with autocorrelation C_JJ(τ) = ⟨δJ²⟩·exp(−|τ|/τ_sub)
- System = qubit ρ_S ∈ M₂(ℂ)
- Born-Markov: ρ_total ≈ ρ_S ⊗ ρ_B (factorization assumed)
- Result: Lindblad dephasing at rate Γ_φ = (4g²/ℏ²)·C̃_JJ(0)

This is a **complete, derived, validated** chain. It is distinct from what Q7 was asked.

The PRW acts as the bath. The qubit is the system. C± is not involved.

---

## 6. Prior C± Derivation

**No prior derivation of C± exists.** The history of C± in the project is:

### In 02_derivations/microscopic_derivation.md
C± = αE is introduced as an external source term in the PRW equations. The microscopic derivation treats αE as an externally supplied creation rate. It is not derived — it is noted as "external forcing."

### In 02_derivations/COMPLETE_MASTER_EQUATION.md
C± = αE is one of eight terms in the master equation. No derivation — it is a parameter of the model.

### In 03_audits/C2_structural_obstruction_audit.md
F3 explicitly identifies the missing physics: "No information→energy bridge. The C2 primitive unit set does not contain kg. Physical energy has units J = kg·m²·s⁻². No combination of C2 quantities produces Joules."

This confirms: C± was never derived. The project knew it was missing and documented the gap precisely.

### In the current session (2026-08-22)
INTERACTION_SPACE_AUDIT.md, CONVERSION_PRW_DERIVATION.md, and QUANTUM_PARENT_DERIVATION.md are the first attempts to actually derive C± from a microscopic mechanism.

---

## 7. C2 Genealogy

### Origin of C2

C2 appears in the project as the C2 observable: a specific prediction of correlated decoherence across a quantum device. The name does not refer to a creation term C± — it refers to a spatial correlation observable.

The project has two distinct uses of "C":
- "C2" = the spatial correlation observable Γ(r) that C2 theory predicts has K₀ shape
- "C±" = the information creation source terms C⁺, C⁻ in the master equation

The current session's Q7 work was about C± (source terms). The prior `34_C2_QUANTUM_BRANCH_STATUS.md` was about C2 (the spatial correlation observable). These are different objects.

### Is Q7 completing an existing C2 idea?

**No, not directly.** The prior C2 architecture (substrate = bath → qubit decoherence) is a well-developed chain that makes experimental predictions. Q7 is asking a deeper question: can the classical PRW itself emerge from a quantum parent?

The prior work explicitly ruled out quantum parents for the PRW (prw_deeper_substrate_audit.md forbade quantum starting assumptions). Q7 reopened that question.

---

## 8. Code Evidence

### 05_simulations/decoherence_prediction.py (dated 2026-07-17)
**EXECUTED quantum mechanism.** Implements:
- Qubit density matrix ρ_S (2×2 complex matrix)
- Lindblad dephasing evolution with L = σ_z
- Computes Γ_φ = k_rot·ω_rot² from substrate parameters
- Fits to IBM Quantum Ramsey data

This is a working implementation of the quantum-substrate-bath chain. It does NOT implement C± or energy-information conversion.

### 05_simulations/extension_qutip.py
**Uses QuTiP.** Implements open quantum system evolution using `qutip.mesolve`. This is an actual quantum simulation of the substrate-as-bath model, not just a textual description.

### 05_simulations/stage3_qutip_ramsey_fixed.py
**Uses QuTiP for Ramsey simulation.** Implements qubit evolution under dephasing Lindblad operator, generates Ramsey fringe pattern.

### 04_validations/interaction_hamiltonian_validation.py, effective_master_equation_validation.py
Both use complex matrices explicitly (NumPy complex arrays). Both implement density matrix evolution. These are live code that implements the quantum mechanism.

### No code implements C± from coherence dynamics. No code implements the quantum parent (ρ̂ = [[ρ₊₊, χ],[χ†, ρ₋₋]]) with off-diagonal evolution that generates source terms. The Q7 derivation has no code counterpart in the project.

---

## 9. Redundancy Test

| Prior chain | Current Q7 | Classification |
|-------------|-----------|---------------|
| PRW (classical substrate) → H_int = g J σ_z → Bath → Lindblad → Γ_φ | PRW ← quantum parent (ρ̂) via coarse-graining → C±_eff | **DIFFERENT** — opposite direction |
| Substrate acts as environment on external qubit | Internal quantum structure of substrate generates PRW and C± | **DIFFERENT** — different question |
| ℏ, g entered as external parameters | ℏ enters microscopically in quantum parent dynamics | **EXTENSION** — Q7 attempts to give ℏ a home |
| C± is phenomenological external input | C±_eff derived from coherence Im(g*χ₀₁) | **EXTENSION** — Q7 attempts a derivation that prior work did not |

---

## 10. What We Actually Know

### ESTABLISHED
- The PRW is a classical stochastic system. Its state space is the probability simplex Δ¹. (Multiple audits, unanimously.)
- The substrate acts as a bath that dephases an externally introduced qubit via H_int = g·J·σ_z. (decoherence_chain_summary.md, all validations pass.)
- ℏ does not appear in the substrate transport equations. (C2_MISSING_PRINCIPLES.md, interaction_hamiltonian_uniqueness.md.)
- g is not determinable from the substrate equations. (interaction_hamiltonian_uniqueness.md, C2_structural_obstruction_audit.md F2.)
- C± = αE is a phenomenological source term with no microscopic derivation. (microscopic_derivation.md, C2_structural_obstruction_audit.md F3.)
- The minimal quantum parent (ℂ²⊗ℂ²) generates a source term C±_eff = (4N/ℏV)·Im(g*χ₀₁) from coherence dynamics. (QUANTUM_PARENT_DERIVATION.md, current session.)
- In the Markovian limit, C±_eff ∝ ΔN₁₁ (population inversion), NOT ∝ αE. (QUANTUM_PARENT_DERIVATION.md.)

### DERIVED
- H_int = g·J·σ_z is the unique coupling form given four external assumptions [A-lin, A-local, P-pure-dephasing, A1]. (interaction_hamiltonian_uniqueness.md.)
- Γ_φ = k_rot·ω_rot² from PRW transport + current variance + Born-Markov. (decoherence_chain_summary.md, validated numerically.)
- Coherence χ generates C±_eff if and only if H_int ≠ 0 and χ ≠ 0. (QUANTUM_PARENT_DERIVATION.md.)
- PRW is the classical (decoherent) limit of the quantum parent. (QUANTUM_PARENT_DERIVATION.md.)

### ASSUMED
- The substrate (PRW) describes a physical substrate that influences quantum systems.
- H_int = g·J·σ_z (three external inputs required).
- Born-Markov validity (marginal: τ_B·Γ_φ ~ 0.25, not << 1).
- αE term in master equation is a legitimate physical source.

### OPEN
- Can C±_eff ∝ αE be derived from the quantum parent (requires dissipative bath, not unitary H)?
- What physical process determines g?
- Does the quantum parent architecture generate ℏ from a first-principles mechanism?
- Can the KL-divergence s_KL provide a closed nonlinear information variable?
- Does the PJ flux-flux coupling produce dynamics inequivalent to known systems?

---

## 11. Project Status

**Direct answers to the six required questions:**

**1. Are we tap-dancing/rebuilding an old idea?**  
Partially. The decoherence chain (PRW as bath → qubit → Lindblad) was fully built in July 2026. The Q7 quantum parent direction (PRW ← quantum microscopic state) was NOT previously developed — in fact the `prw_deeper_substrate_audit.md` explicitly forbade quantum starting points. Q7 is genuinely new in direction, but it builds on the same framework.

**2. Did the project already have the environment → C± route?**  
No. The project had the environment → Γ_φ route (substrate as bath → qubit decoherence). The environment → C± route (environment/coherence → information creation source) did not previously exist. These are different routes.

**3. Did the project already derive C± from a microscopic mechanism?**  
No. C± = αE was always a phenomenological source term. The current session's CONVERSION_PRW_DERIVATION.md and QUANTUM_PARENT_DERIVATION.md are the first attempts at derivation.

**4. Is Q7 a genuine advance or mostly rediscovery?**  
Q7 is a genuine advance in the quantum-parent direction, which was explicitly excluded from prior work. The finding — that C±_eff ∝ ΔN₁₁ (not αE) from unitary quantum dynamics — is new, not in any prior document. The identification that αE requires a dissipative (not unitary) bath is new.

**5. Is there still a technically coherent route to the original C2 objective?**  
The original C2 objective (spatial correlation K₀ vs exp discrimination on QPU) is technically coherent and well-specified in `34_C2_QUANTUM_BRANCH_STATUS.md`. It requires:
- IBM Eagle-class access (currently unavailable)
- τ_B ~ 1 µs measurement
- c = vₛ already derived
- ξ_c = 2vₛτ_B predicted

The quantum parent / C± question is orthogonal to this experimental objective. The QPU test does not require C± to be derived.

**6. What exact unresolved equation prevents closure?**  
There are two distinct blocking equations:

**For the C± derivation:**
```
C±_eff (unitary quantum parent) ∝ ΔN₁₁ = (n⁻_high − n⁺_high)
C± (master equation requires)   ∝ αE = α(e⁺ + e⁻)
```
These are unequal. Bridging requires a dissipative bath with jump operator L = √α·|+,e₀⟩⟨+,e₁|, for which α = 2π|g|²/Δε·(bath density of states) — a standard quantum optical result. This requires specifying the bath Hamiltonian H_bath, which is not in the current substrate ontology.

**For the g derivation:**
```
[g] = J·m²·s/info  requires  kg  ∈ unit system
C2 unit system = {m, s, info}  has no  kg
```
(C2_structural_obstruction_audit.md, F2, F3 — established 2026-07-24.) This cannot be resolved without introducing a mass scale or a new physical principle.

The project is not blocked arbitrarily. It has two precisely identified gaps, both known since July 2026.
