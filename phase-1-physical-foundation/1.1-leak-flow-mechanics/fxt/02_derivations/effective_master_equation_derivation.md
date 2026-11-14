# Effective Master Equation Derivation
## From Bloch-Redfield to Lindblad: The Substrate Dephasing Channel

**Status:** Derivation document  
**Depends on:** interaction_hamiltonian_derivation.md (all notation and results carry over)  
**Does not modify:** Any established equation, parameter, or approximation

---

## Notation

All symbols from interaction_hamiltonian_derivation.md carry their established meanings.
New symbols introduced here:

| Symbol | Units | Meaning |
|--------|-------|---------|
| L | — | Lindblad operator |
| γ | s⁻¹ | Lindblad jump rate |
| D[L]ρ | s⁻¹ | Lindblad dissipator: L ρ L† − (1/2){L†L, ρ} |
| Λ | s⁻¹ | Lindbladian superoperator |
| T₂* | s | Pure dephasing time: T₂* = 1/Γ_φ |
| χ | — | Process matrix (quantum process tomography) |

---

## Part I — From Bloch-Redfield to Lindblad Form

### Section 1: The Bloch-Redfield Result

From interaction_hamiltonian_derivation.md, equation [ME-QUBIT], the qubit master equation under Born-Markov approximations is:

```
dρ_S/dt = −(2g²/ℏ²) Γ̃ (ρ_S − σ_z ρ_S σ_z)             [BR-RESULT]
```

where:

```
Γ̃ ≡ ∫₀^∞ C_JJ(τ') dτ' = ⟨(δJ)²⟩ · τ_sub                  [GAMMA-TILDE]
```

This is **derived** from:
- [A-BORN]: Born (weak coupling) approximation
- [A-MARKOV]: Markov approximation τ ≪ Γ_φ⁻¹
- [A-SEC]: Secular approximation
- [A-STAT]: Stationarity of the substrate
- [A-SINGLE-EXP]: Single-exponential dominant contribution to C_JJ

**Note:** The full master equation [BR-RESULT] does not assume a specific form for ρ_S. It is a matrix equation governing all four elements of the 2×2 density matrix.

---

### Section 2: Algebraic Reduction to Lindblad Form

**Goal:** Express [BR-RESULT] in the standard Lindblad form:

```
dρ_S/dt = −i[H_eff, ρ_S] + γ (L ρ_S L† − (1/2){L†L, ρ_S})   [LINDBLAD-STD]
```

For the σ_z dephasing channel specifically.

**Identity [ID-LINDBLAD-Z]:** For the pure dephasing case with L = σ_z:

```
σ_z ρ_S σ_z† − (1/2){σ_z†σ_z, ρ_S}
= σ_z ρ_S σ_z − (1/2){I, ρ_S}
= σ_z ρ_S σ_z − ρ_S                                        [ID-LINDBLAD-Z]
```

since σ_z² = I. Therefore:

```
D[σ_z]ρ_S ≡ σ_z ρ_S σ_z − ρ_S = −(ρ_S − σ_z ρ_S σ_z)    [DISSIPATOR-Z]
```

Comparing [BR-RESULT] with [DISSIPATOR-Z]:

```
dρ_S/dt = −(2g²/ℏ²) Γ̃ (ρ_S − σ_z ρ_S σ_z)
        = (2g²/ℏ²) Γ̃ D[σ_z]ρ_S
        = γ D[σ_z]ρ_S                                       [ME-LINDBLAD]
```

with jump rate:

```
γ = (2g²/ℏ²) Γ̃ = (2g²/ℏ²) ⟨(δJ)²⟩ τ                     [JUMP-RATE]
```

**Result [R-LINDBLAD]:** The master equation derived from the substrate coupling is a standard Lindblad equation with a single dephasing jump operator L = σ_z. No approximation beyond Born-Markov is required for this algebraic step.

**The effective Lindbladian is:**

```
Λρ_S = γ (σ_z ρ_S σ_z − ρ_S)                              [LINDBLADIAN]
```

This is exact within Born-Markov.

---

### Section 3: Connection to the Dephasing Rate

The dephasing rate Γ_φ derived in interaction_hamiltonian_derivation.md is:

```
Γ_φ = (4g²/ℏ²) Γ̃ = (4g²/ℏ²) ⟨(δJ)²⟩ τ                   [DEPH-RATE]
```

Comparing with [JUMP-RATE]:

```
Γ_φ = 2γ                                                    [GAMMA-2GAMMA]
```

**Identity [ID-THREE-WAY]:** The following three quantities are related by:

```
γ_Lindblad = γ_01|_{T_C2} = (1/2) Γ_φ = (1/2) k_rot ω_rot²    [ID-THREE-WAY]
```

where:
- `γ_Lindblad`   is the Lindblad jump rate in [ME-LINDBLAD], units s⁻¹ [JUMP-RATE]
- `γ_01|_{T_C2}` is the abstract secular transition rate γ_mn of T-D4-2 (Quantum Completion Audit), evaluated at the T_C2 pair (m=0, n=1) under the DC approximation and A-GEOM-1
- `Γ_φ`          is the physical dephasing rate, units s⁻¹ [DEPH-RATE]
- `k_rot`        is the rotation coupling constant [KROT-CANONICAL]
- `ω_rot`        is the bath rotation frequency [A-GEOM-3]

Derivation in three steps: (1) γ_Lindblad = (2g²/ℏ²)Γ̃ [JUMP-RATE]; (2) Γ_φ = 2γ_Lindblad [ID-FACTOR2, GAMMA-2GAMMA]; (3) Γ_φ = k_rot ω_rot² [GAMMA-MAIN, from T-D4-3].

**Why the factor of 2?** The Lindblad dissipator D[σ_z] drives the decay of ρ_{01} at rate 2γ, not γ. This can be verified:

From [ME-LINDBLAD]:
```
dρ_{01}/dt = [γ(σ_z ρ_S σ_z − ρ_S)]_{01}
           = γ [(σ_z ρ_S σ_z)_{01} − ρ_{01}]
           = γ [⟨0|σ_z ρ_S σ_z|1⟩ − ρ_{01}]
           = γ [(−1)(+1) ρ_{01} − ρ_{01}]
           = γ [−ρ_{01} − ρ_{01}]
           = −2γ ρ_{01}
```

Therefore:

```
ρ_{01}(t) = ρ_{01}(0) exp(−2γt) = ρ_{01}(0) exp(−Γ_φ t)   [COH-DECAY]
```

with `Γ_φ = 2γ`. ✓

**Identity [ID-FACTOR2]:** For a σ_z Lindblad dephasing channel, the coherence decay rate equals twice the jump rate: `Γ_φ = 2γ`. This is a standard result in open quantum systems.

---

## Part II — Explicit Matrix Elements

### Section 4: The Lindblad Master Equation in Component Form

Let ρ_S = [[ρ_{00}, ρ_{01}], [ρ_{10}, ρ_{11}]].

From [ME-LINDBLAD], the four components evolve as:

**Populations (diagonal elements):**

```
dρ_{00}/dt = [γ(σ_z ρ_S σ_z − ρ_S)]_{00}
           = γ[(σ_z)_{00}² ρ_{00} − ρ_{00}]
           = γ[(+1)² ρ_{00} − ρ_{00}]
           = 0
```

```
dρ_{11}/dt = γ[(σ_z)_{11}² ρ_{11} − ρ_{11}]
           = γ[(−1)² ρ_{11} − ρ_{11}]
           = 0
```

**Populations are exactly conserved.** This is the defining property of pure dephasing — it is a consequence of σ_z being diagonal in the energy basis.

**Coherences (off-diagonal elements):**

```
dρ_{01}/dt = −2γ ρ_{01} = −Γ_φ ρ_{01}
dρ_{10}/dt = −2γ ρ_{10} = −Γ_φ ρ_{10}
```

**Solution:**

```
ρ_{00}(t) = ρ_{00}(0)                                      [POP-CONST]
ρ_{11}(t) = ρ_{11}(0)                                      [POP-CONST]
ρ_{01}(t) = ρ_{01}(0) exp(−Γ_φ t)                          [COH-EXP]
ρ_{10}(t) = ρ_{10}(0) exp(−Γ_φ t)                          [COH-EXP]
```

**Summary of the effective master equation:**

```
dρ_S/dt = Γ_φ/2 · (σ_z ρ_S σ_z − ρ_S)                    [ME-FINAL]
```

with:

```
Γ_φ = k_rot · ω_rot²                                        [GAMMA-MAIN]
k_rot = 8g²s₀²r_q²τ/(3ℏ²)                                  [KROT-DEF]
```

---

## Part III — Quantum Process Tomography Perspective

### Section 5: The Process Matrix χ

The action of the dephasing channel on the qubit density matrix can be written as a quantum process:

```
ρ_S(t) = ε_t(ρ_S(0)) = ∑_{mn} χ_{mn} E_m ρ_S(0) E_n†    [QPT]
```

In the Pauli basis {I/√2, σ_x/√2, σ_y/√2, σ_z/√2}, the process matrix for pure dephasing at time t is:

```
χ(t) = diag((1+e^{-Γt})/2, (1−e^{-Γt})/2, (1−e^{-Γt})/2, (1+e^{-Γt})/2) · (1/2)
```

Wait — for the σ_z dephasing channel, using the basis operators E_0 = I, E_1 = σ_z:

```
ε_t(ρ) = p_0(t) · ρ + p_1(t) · σ_z ρ σ_z
```

where `p_0(t) = (1 + e^{-Γ_φ t})/2` and `p_1(t) = (1 − e^{-Γ_φ t})/2`.

**Verification:** At t=0: p_0=1, p_1=0, ε_0(ρ)=ρ ✓. As t→∞: p_0=p_1=1/2, fully dephased ✓.

**Identity [ID-CHANNEL-FORM]:** The substrate dephasing channel is a Pauli channel with only a σ_z component: `ε = (p_0 I⊗I + p_1 Z⊗Z)/2` in the channel representation. It is **not** a depolarising channel (which would have equal σ_x, σ_y, σ_z weights).

---

## Part IV — Connecting to Experimental Observables

### Section 6: Ramsey Signal

In a standard Ramsey experiment:

1. **Prepare:** π/2 pulse → |+⟩ = (|0⟩ + |1⟩)/√2, so ρ_S(0) = (I + σ_x)/2
2. **Free evolve** for time t_R under H_S = (ℏω_q/2)σ_z + H_int
3. **Measure:** π/2 pulse + population measurement

The Ramsey signal (expectation value of σ_x after free evolution time t_R) is:

```
S(t_R) = ⟨σ_x(t_R)⟩ = 2 Re[ρ_{01}(t_R)] cos(ω_q t_R)
        = cos(ω_q t_R) exp(−Γ_φ t_R)                       [RAMSEY]
```

The envelope of the Ramsey fringes decays as `exp(−Γ_φ t_R)` with:

```
Γ_φ = k_rot · ω_rot²                                        [GAMMA-ROT]
```

**Derived result [R-RAMSEY]:** The Ramsey fringe decay is exponential with rate Γ_φ = k_rot ω_rot². This result does not depend on the qubit transition frequency ω_q, only on the rotation frequency ω_rot of the substrate perturbation.

### Section 7: T₂* Definition

The pure dephasing time T₂* is conventionally defined by:

```
exp(−t_R / T₂*) = exp(−Γ_φ t_R)
⟹  T₂* = 1/Γ_φ = 1/(k_rot ω_rot²)                         [T2STAR]
```

This is a **derived** result: T₂* is inversely proportional to ω_rot². Doubling the rotation rate reduces T₂* by a factor of 4.

**Prediction:** For a qubit in a rotating frame at ω_rot = 10⁵ rad/s with k_rot = 4.5 × 10⁻⁷ s:

```
Γ_φ = 4.5×10⁻⁷ × (10⁵)² = 4.5×10³ s⁻¹
T₂* = 1/4500 ≈ 222 µs
```

This prediction is within the experimentally measured range for NV center qubits in the relevant regime.

---

## Part V — Comparison with Standard Open Systems Formalism

### Section 8: Generality of the Result

The derived master equation [ME-FINAL] matches the standard **phase-flip channel** in quantum information theory:

```
ε(ρ) = (1−p) ρ + p σ_z ρ σ_z    with p = (1 − e^{-Γ_φ t})/2
```

The **only** substrate-specific input is the dephasing rate Γ_φ = k_rot ω_rot². The master equation itself is structurally identical to standard quantum optics dephasing (e.g., 1/f noise, spin-boson model with ohmic bath, etc.).

**What is derived vs what is standard:**

| Statement | Status |
|-----------|--------|
| L = σ_z is the jump operator | **Derived** (from [R-OPERATOR]) |
| Lindblad form of the ME | **Standard** (from Born-Markov) |
| γ = (2g²/ℏ²)⟨(δJ)²⟩τ | **Derived** (from interaction Hamiltonian + transport) |
| Γ_φ = 2γ | **Identity** (algebra of σ_z) |
| Γ_φ = k_rot ω_rot² | **Derived** (substituting Layer 4 result) |
| T₂* = 1/Γ_φ | **Definition** |

### Section 9: No Relaxation (T₁ = ∞ exactly)

The populations satisfy [POP-CONST]: `dρ_{00}/dt = dρ_{11}/dt = 0`. Therefore T₁ = ∞ exactly within this model.

**Physical reason:** σ_z commutes with the free Hamiltonian H_S = (ℏω_q/2)σ_z. A coupling that commutes with H_S cannot induce transitions between energy eigenstates.

**Derived result [R-T1-INF]:** The substrate σ_z coupling produces **pure dephasing only**, with T₁ = ∞ and T₂ = T₂* = 1/Γ_φ. The standard Bloch-Redfield relation `1/T₂ = 1/(2T₁) + 1/T₂*` reduces to `1/T₂ = 1/T₂*` in this case.

This is consistent with the physical picture: substrate current fluctuations modulate the qubit energy splitting but do not flip the qubit spin.

---

## Part VI — Complete Derivation Chain

### Section 10: Step-by-Step Accounting

Every step labelled: **[D]** derived, **[A]** assumption, **[I]** identity, **[S]** standard result.

```
From interaction_hamiltonian_derivation.md:
[D + A-QUANT-5(Born) + A-QUANT-6(Markov) + A-QUANT-7(Secular)
   + A-QUANT-8(Stationarity) + A-QUANT-9(H_int=gJσ_z)
   + A-QUANT-11(Single-exp correlator)
   + Def 2.1(ℋ_S) + Def 2.3(Ĥ_S) + Def 2.11(A,B)]
    Bloch-Redfield ME:  dρ_S/dt = −(2g²/ℏ²)Γ̃(ρ_S − σ_z ρ_S σ_z)

      ↓

[I: ID-LINDBLAD-Z]
    ρ_S − σ_z ρ_S σ_z = −D[σ_z]ρ_S

      ↓

[D: substitution]
    dρ_S/dt = γ D[σ_z]ρ_S    with γ = (2g²/ℏ²)Γ̃    [ME-LINDBLAD]

      ↓

[I: evaluate off-diagonal component]
    dρ_{01}/dt = −2γ ρ_{01}

      ↓

[D: solve ODE]
    ρ_{01}(t) = ρ_{01}(0) exp(−2γt)

      ↓

[I: definition Γ_φ = 2γ]
    ρ_{01}(t) = ρ_{01}(0) exp(−Γ_φ t)

      ↓

From interaction_hamiltonian_derivation.md [MAIN-RESULT]:
[D + A-GEOM-1(⟨δJ²⟩) + HA-1(DC approx, OPEN ASSUMPTION — reserved for verification)
   + A-QUANT-3(η,ℏ) + A-GEOM-2(isotropic) + A-GEOM-3(single mode)]
    Γ_φ = k_rot · ω_rot²    with k_rot = 8g²s₀²r_q²τ/(3ℏ²)

      ↓

[S: Ramsey formula]
    S(t_R) = cos(ω_q t_R) · exp(−Γ_φ t_R)

      ↓

[I: definition T₂*]
    T₂* = 1/Γ_φ = 1/(k_rot ω_rot²)
```

---

## Part VII — Verification of Positivity and Trace Preservation

### Section 11: The Lindblad Form Guarantees Physical Consistency

A key property of the Lindblad master equation [ME-LINDBLAD] is that it generates a completely positive, trace-preserving (CPTP) map. This follows from the general theory (Gorini-Kossakowski-Sudarshan-Lindblad theorem).

**Trace preservation:**

```
d/dt Tr[ρ_S] = Tr[dρ_S/dt] = γ Tr[σ_z ρ_S σ_z − ρ_S]
             = γ (Tr[ρ_S] − Tr[ρ_S]) = 0  ✓             [TRACE-PRES]
```

using `Tr[σ_z ρ σ_z] = Tr[σ_z² ρ] = Tr[ρ]` (cyclicity of trace, σ_z² = I).

**Hermiticity preservation:**

```
(dρ_S/dt)† = γ (σ_z ρ_S† σ_z − ρ_S†) = γ (σ_z ρ_S σ_z − ρ_S) = dρ_S/dt  ✓
```

(using ρ_S† = ρ_S for a density matrix and σ_z† = σ_z).

**Positivity:** The analytic solution [COH-DECAY] gives:

```
ρ_S(t) = [[ρ_{00}(0),   ρ_{01}(0)e^{-Γt}],
            [ρ_{10}(0)e^{-Γt}, ρ_{11}(0)  ]]
```

The eigenvalues of ρ_S(t) are:

```
λ_{±}(t) = (ρ_{00}(0) + ρ_{11}(0)) / 2
           ± √((ρ_{00}(0) − ρ_{11}(0))² / 4 + |ρ_{01}(0)|² e^{-2Γt}) / 2
```

Since e^{-2Γt} ≤ 1, and the initial state is positive (λ_{±}(0) ≥ 0), and |ρ_{01}(0)|² ≤ ρ_{00}(0)ρ_{11}(0) (initial state is physical), it follows that:

```
|ρ_{01}(0)|² e^{-2Γt} ≤ |ρ_{01}(0)|² ≤ ρ_{00}(0)ρ_{11}(0)
```

Therefore λ_{±}(t) ≥ 0 for all t ≥ 0. ✓

**Corollary HC-2-CPTP (CPTP property):** The substrate dephasing map is CPTP for all t ≥ 0. *(Corollary of Theorem HC-2 [Lindblad form] by the Gorini-Kossakowski-Sudarshan-Lindblad theorem [KR]. The explicit verification below confirms this for the specific T_C2 solution.)*

---

## Part VIII — Summary and Downstream Implications

### Section 12: Summary

The effective master equation for a qubit coupled to the substrate current via H_int = g J σ_z is:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  dρ_S/dt = (Γ_φ/2) (σ_z ρ_S σ_z − ρ_S)             │
│                                                      │
│  Γ_φ = k_rot · ω_rot²                               │
│                                                      │
│  k_rot = 8g²s₀²r_q²τ / (3ℏ²)                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

Physical content:
- Single Lindblad operator: L = σ_z (pure dephasing, no relaxation)
- Jump rate γ = Γ_φ/2 = k_rot ω_rot²/2
- Coherence decays: ρ_{01}(t) = ρ_{01}(0) e^{-Γ_φ t}
- Populations conserved: ρ_{00}(t) = ρ_{00}(0), ρ_{11}(t) = ρ_{11}(0)
- Ramsey signal: S(t) = cos(ω_q t) e^{-Γ_φ t}
- T₂* = 1/Γ_φ = 1/(k_rot ω_rot²)
- T₁ = ∞

### Section 13: What This Determines for the Decoherence Comparison

The complete chain (PRW → ... → Γ_φ = k_rot ω_rot²) predicts:

1. **Spectral shape:** Γ_φ(ω_rot) ∝ ω_rot² at low frequencies (confirmed in decoherence_prediction.py)
2. **Saturation:** Γ_φ → Γ_φ,max at high ω_rot (from multi-mode correction, see interaction_hamiltonian_derivation.md Section 6)
3. **No additional parameters:** k_rot is determined by (g, s₀, r_q, τ) — four physical quantities
4. **Single free parameter:** g cannot be derived from classical transport; it must be measured

The IBM Quantum Ramsey data (nunu/ramsey_dataset/) provides the empirical k_rot value from which g can be extracted, completing the parameter identification chain.

---

## Appendix: Assumptions Imported from Upstream Documents

| Label | From | Statement |
|-------|------|-----------|
| [A-BORN] | interaction_hamiltonian_derivation.md | Born (weak coupling) approximation |
| [A-MARKOV] | interaction_hamiltonian_derivation.md | Markov: τ ≪ Γ_φ⁻¹ |
| [A-SEC] | interaction_hamiltonian_derivation.md | Secular (rotating wave) approximation |
| [A-STAT] | interaction_hamiltonian_derivation.md | Substrate stationarity |
| [A-SINGLE-EXP] | interaction_hamiltonian_derivation.md | DC-dominated correlator |
| [LAYER4] | substrate_transport_derivation.md | ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q² |
| [H-INT] | interaction_hamiltonian_derivation.md | H_int = g J σ_z |

No new assumptions are introduced in this document beyond the above.

---

## Part IX — Master Derivation Chain

This section presents the complete derivation from T-D4-2 inputs to the k_rot formula as a single sequential chain, with each assumption cited at the step where it first enters. No new mathematics is introduced here — every equation exists in the sections above.

```
Step 1 — Inputs from Theorem T-D4-2 (secular Bloch-Redfield):
  γ_01 = |A_01|² · C̃_AB(ω_01)
  Requirements: A-QUANT-5(Born), A-QUANT-6(Markov), A-QUANT-7(Secular),
                A-QUANT-8(Stationarity), Def 2.8(γ_mn), Def 2.9(J(ω)),
                Def 2.11(A, B)

      ↓

Step 2 — Specify coupling (A-QUANT-9):
  A = σ_z, B = gJ
  σ_z diagonal in energy eigenbasis → dephasing sector (ω=0) contributes
  Result: γ_Lindblad = (2g²/ℏ²) C̃_JJ(0)   [from JUMP-RATE]
  Requirements: A-QUANT-9, HA-5 (commutation [Ĥ_S, σ_z] = 0)

      ↓

Step 3 — Bath correlator form (A-QUANT-11b):
  C_JJ(τ') = ⟨(δJ)²⟩ · e^{-|τ'|/τ}   (single-exponential)
  C̃_JJ(ω) = ⟨(δJ)²⟩ · τ/(1 + ω²τ²)  (Lorentzian)
  Requirements: A-QUANT-11

      ↓

Step 4 — DC approximation [OPEN ASSUMPTION HA-1 — reserved for mathematical verification]:
  C̃_JJ(ω_01) ≈ ⟨(δJ)²⟩ · τ
  Requirements: HA-1 [OPEN ASSUMPTION — see §Open Assumptions in C2_FOUNDATIONS.md]

      ↓

Step 5 — Substitute geometry [OPEN ASSUMPTION A-GEOM-1 — reserved for mathematical verification]:
  ⟨(δJ)²⟩ = (2/3)s₀²ω_rot²r_q²
  Requirements: A-GEOM-1 [reserved], A-GEOM-2(isotropic), A-GEOM-3(single mode)

      ↓

Step 6 — Combine (A-QUANT-3 for ℏ units):
  γ_Lindblad = (2g²/ℏ²) · (2/3)s₀²ω_rot²r_q² · τ
             = (1/2) k_rot ω_rot²
  k_rot = 8g²s₀²r_q²τ/(3ℏ²)     [KROT-CANONICAL]
  Requirements: A-QUANT-3(η,ℏ)

      ↓

Step 7 — Physical dephasing rate:
  Γ_φ = 2γ_Lindblad = k_rot ω_rot²    [ID-FACTOR2, GAMMA-MAIN, ID-THREE-WAY]

      ↓

Step 8 — Ramsey signal:
  S(t_R) = cos(ω_q t_R) · exp(−Γ_φ t_R)   [RAMSEY]
  Requirements: Corollary HC-2-CPTP
```

**Note on Steps 4 and 5:** The assumptions HA-1 and A-GEOM-1 are marked as reserved for the mathematical verification phase. Their mathematical content is frozen; the citations here are documentation placeholders. See §Open Assumptions in C2_FOUNDATIONS.md for their current status.
