# FINAL RESCUE-OR-KILL AUDIT

**Date:** 2026-08-22
**Purpose:** Determine whether ANY non-circular route from the existing SXC-IGC
substrate architecture to C± = αE exists anywhere in fxt/ history.
**Method:** Full forensic search first. No redesign. No new physics introduced.

---

## 1. Executive Verdict

**Classification: C — Original C2 closure is dead.**

No non-circular route from the existing substrate ontology to C± = αE exists
anywhere in the fxt/ history. Every candidate route either (a) imports kg/ℏ as
a new primitive, (b) chooses the energy-sector bath coupling because it produces
αE, or (c) depends on unproved conjectures (CCA-C3/F9). The PRW/FPUT architecture
contains no independent selection principle that forces energy-sector coupling
over direction-sector, coherence-sector, or information-density coupling.

**Classification D (project as a whole) is NOT warranted.** The transport sector
and the decoherence prediction Γ_φ ∝ ω² survive independently of C±. These are
genuine, validated results unaffected by the C± failure.

---

## 2. Complete Historical Architecture

The project has four distinct layers, each with a different derivational status.

**Layer 1 — PRW Transport (ESTABLISHED)**
PRW balance equations → telegrapher → diffusion. Source-free. Conserves info.
No energy variable. No quantum structure. No C±.

**Layer 2 — FPUT Projection (ESTABLISHED)**
FPUT → unique C1–C6 projection = PRW. Phases discarded (T^M torus).
Energy information (mode energies E_k = ω_k·n_k) present in FPUT but
requires particle mass m_FPUT [kg]. Not inherited by PRW.

**Layer 3 — Quantum Coupling (ESTABLISHED)**
External qubit + PRW bath → H_int = g·J·σ_z → Γ_φ = k_rot·ω².
Validated numerically. g is free (requires kg). ℏ external.
C± not part of this chain.

**Layer 4 — Source Terms (PHENOMENOLOGICAL)**
αE inserted as external forcing into PRW balance equations (microscopic_derivation.md
§1.8: "external forcing function, not a property of the particle dynamics itself").
Never derived from any microscopic process in any prior document.

**The C± gap has been open since the project began.** No document in fxt/
predates this session's audits as a derivation of C± from dynamics.

---

## 3. Quantum Parent Audit

**Every quantum structure found in fxt/ history:**

| Location | Structure | Derived from PRW/FPUT? |
|----------|-----------|----------------------|
| interaction_hamiltonian_derivation.md | H_int = g·J·σ_z, qubit ℂ², Lindblad | NO — qubit is external; PRW is the bath |
| decoherence_chain_summary.md | Full Born-Markov chain, ρ_S(t) | NO — imports ℏ, g, qubit Hilbert space |
| minimal_origin_Hilbert/ | Can ℂ-Hilbert space be forced? | NO — requires BP-1 (Local Tomography) added |
| QUANTUM_PARENT_DERIVATION.md | ℂ²_dir ⊗ ℂ²_E, unitary Q7 | NO — direction qubit assumed; energy sector new |
| FPUT projection | nₖ = |Aₖ|² action variables | NO quantum structure in PRW layer |
| C2_FOUNDATIONS.md §SCC | SCC reconstruction of QM | NO — imports O1 (complex structure) |

**Conclusion:** No quantum structure in the entire project was derived from the
PRW or FPUT layers. Every quantum structure was either (a) imported for use in
the decoherence chain (qubit as external probe), or (b) proposed as an extension.
The PRW itself produces no non-commutative algebra (proved: T PRW-IMP-1).

---

## 4. Energy Bridge Audit

**Every energy-like quantity found in fxt/ history:**

| Quantity | Units | Derivable from D_C2={m,s}? | Status |
|----------|-------|---------------------------|--------|
| E_sub = ½c²s²+½J² | info²/m⁴ | YES — but NOT Joules | Wrong units |
| CCA rank r | dimensionless | YES — but E=E₀·r needs free E₀ | UV catastrophe |
| Landauer k_BT·ln2 | J | NO — needs k_B, T (external) | Not in C2 |
| Causal action S_causal | nats (dimensionless) | YES — but not J·s | Wrong units |
| HC-1: ℏ = m_eff·c·ξ_c | J·s | NO — m_eff not in C2 | Relocates problem |
| HC-2: ℏ = ΔS/ω | J·s | CONDITIONAL — needs CCA-C3 (unproved) | Unproved |
| FPUT E_k = ω_k·n_k | J (classical) | NO — needs m_FPUT [kg] | Requires new primitive |
| η [J/info] | J/info | NO | New primitive (July 2026) |
| G·c⁻² (gravitational) | m/kg | NO — G has kg⁻¹ | Wrong direction |

**Every route to deriving an energy scale from C2 primitives has been tested and
failed.** The obstruction is the same in every case: kg ∉ D_C2 = {m, s}.
No dynamical mechanism internal to the massless PRW generates kg.
This is a proved theorem, not a gap in analysis.

---

## 5. Environment/Bath Audit

**Every bath/environment candidate found in fxt/ history:**

| Candidate | DoF count | Timescale separation | Energy exchange | Verdict |
|-----------|-----------|---------------------|-----------------|---------|
| PRW substrate (for decoherence chain) | ∞ modes | ✓ τ_sub << T_qubit | Via C_JJ(τ) — info units only | WORKS for decoherence, NOT for C± (no Joules) |
| FPUT discarded phases (T^M torus) | M = N/2 modes | ✓ for high-k | Requires β≠0 (anharmonicity) | FAILS — reverses projection; requires new physics |
| PRW long-wavelength modes | ∞ | ✗ SLOW (wrong direction) | None | FAILS — timescale wrong |
| v_sub drift field | 0 (prescribed) | N/A | None | FAILS — not a bath |
| External bosonic reservoir (E_min) | ∞ | ✓ | ✓ | WORKS but is external, unidentified |

**Key finding:** The PRW substrate functions as an energy bath for the
*decoherence chain* (PRW current fluctuations dephase an external qubit).
But for the *creation chain* (C± = αE), the substrate needs to exchange Joules
— and the PRW has no Joule-valued variable. The same bath that works for
decoherence fails for creation.

The discarded FPUT phases are the only internal candidate with sufficient
degrees of freedom. They fail because:
1. Reversal of the FPUT→PRW projection (Theorem FPUT-3) is required.
2. Anharmonicity β≠0 is required for thermalization (not in the harmonic PRW).
3. Mode energies E_k = ω_k·n_k require particle mass m_FPUT [kg].

**No existing SXC-IGC degree of freedom can serve as the required energy bath.**

---

## 6. Source-Term History

**Complete inventory of every prior appearance of C± in fxt/ history:**

| Document | Date | Treatment | Derived? |
|----------|------|-----------|----------|
| COMPLETE_MASTER_EQUATION.md | pre-session | αE listed as term; α defined phenomenologically | NO |
| microscopic_derivation.md §1.8 | 2026-07-20 | "external forcing function, not a property of particle dynamics" | NO |
| UNIFIED_PERTURBATIVE_DERIVATION.md | pre-session | αE appears in source-free exterior only (A2: E=0) | N/A |
| INTERACTION_SPACE_AUDIT.md | 2026-08-22 | Linear C±=αE is minimal member of admissible family; physical constraints do NOT force it | NO (not forced) |
| CONVERSION_PRW_DERIVATION.md | 2026-08-22 | Conservation law Q±=ε₀C± derived; ε₀ free | PARTIAL (conservation only) |
| QUANTUM_PARENT_DERIVATION.md | 2026-08-22 | Unitary Q7: C±_eff ∝ ΔN₁₁ (≠ αE) | NO (wrong form) |
| FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md | 2026-08-22 | Bath mechanism → αE given E_min | CONDITIONAL (needs E_min) |

**Conclusion:** C± = αE was NEVER derived from dynamics before this session's
audits. It was always an external forcing function. The closest prior result
(INTERACTION_SPACE_AUDIT.md) explicitly proved that physical constraints allow
a multi-parameter family and do not force the linear form.

---

## 7. Dependency/Circularity Audit

**The only proposed mechanism that produces C± = αE:**

Bath-mediated creation via H_int = Σ_k λ_k(b_k+b_k†) ⊗ Â_create

Step-by-step classification:

| Step | What happens | Classification |
|------|-------------|---------------|
| 1. PRW particle gets direction qubit ℂ² | Assign complex structure to classical {+,−} | TARGET-INFORMED — needed to build Hilbert space |
| 2. PRW particle gets energy sector ℂ²_{e₀,e₁} | Add internal energy levels | TARGET-INFORMED — needed to couple to E |
| 3. Bath H_B assigned with modes at ω₀=Δε/ℏ | Bosonic reservoir specified | IMPORTED from standard QM |
| 4. H_int chosen to couple bath to energy sector | Three-body creation operator | TARGET-INFORMED — if direction sector chosen, gives C±∝s |
| 5. Born-Markov reduction | Standard procedure | DERIVED (given 1-4) |
| 6. High-T limit n_{e₁} ≈ e±/ε₁ | Thermal occupancy → energy density | ASSUMED (requires T >> Δε/k_B) |
| 7. C± = α·e± → C_total = αE | Functional form | DERIVED (given 1-6) |

Steps 1, 2, 4 are TARGET-INFORMED. The mechanism was constructed knowing the
desired output. The only non-circular content is: *given* the energy-sector
coupling, the functional form C± ∝ E (not ∝ s or ∝ Im(χ)) follows without
further free parameters.

**Circularity verdict:** The mechanism is partially circular. The sector choice
(Step 4) is not forced by any SXC-IGC principle. The derivation succeeds
because the desired coupling was inserted. The functional form of C± given
the coupling is a genuine result; the choice of coupling is not.

---

## 8. Sector-Selection Audit

**The critical question:** Does any existing SXC-IGC principle independently
select energy-sector coupling over direction/coherence/density coupling?

**Search result — complete inventory of selection principles in fxt/:**

For the decoherence H_int (interaction_hamiltonian_uniqueness.md), uniqueness
of H_int = g·J·σ_z was proved given four assumptions:
- A-lin-coupling (linear in J)
- A-local (coupling at qubit position)
- P-pure-dephasing (observed T₁ >> T₂)
- A1 (minimal/lowest-order)

These four conditions uniquely select σ_z. The selection works because the
*observable* T₁ >> T₂ is used as empirical input (P-pure-dephasing).

**For the creation H_int, the analogous selection would require:**
An observable or physical condition that forces coupling to the energy sector
rather than the direction sector. No such observable or condition exists in
any fxt/ document. The INTERACTION_SPACE_AUDIT.md (2026-08-22) explicitly
proved that positivity, conservation, symmetry, and detailed balance are all
insufficient — they allow the multi-parameter family.

**NO EXISTING SELECTION PRINCIPLE FOUND.**

The energy-sector coupling was chosen in FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md
because it produces C± ∝ E. There is no independent physical argument for it.

---

## 9. Decoherence/Creation Unification Audit

**Can the same microscopic structure produce both Γ_φ ∝ ω² and C± = αE?**

The decoherence chain:
- Bath = PRW substrate current fluctuations
- System = external qubit ℂ²
- Coupling = g·J·σ_z
- Result = Γ_φ = (4g²/ℏ²)·C̃_JJ(0) = k_rot·ω²

The creation chain:
- Bath = external bosonic reservoir H_B
- System = internal substrate quanta (Fock space)
- Coupling = λ_coup·(b+b†)·â†_create
- Result = C± = αE

These two chains share: Hilbert space formalism, Born-Markov approximation.
They do NOT share: the physical bath, the coupling operator, or the coupling
constant. g and λ_coup are dimensionally unrelated and independent.

**Is there a common microscopic object linking them?**

The PRW substrate current J appears in the decoherence coupling (g·J·σ_z)
and in the PRW balance equations. J does NOT appear in the creation coupling.
No common coupling, bath, or conservation law links the two sectors.

H_total = H_decoherence + H_creation is formal addition of two independent
interaction terms. There is no cross-term, no shared parameter, no derived
relation between g and λ_coup.

**Verdict: NO UNIFICATION EXISTS.** The two mechanisms coexist in the same
formalism but make no contact. This is juxtaposition, not unification.

---

## 10. Strongest Existing Route

The strongest route found in the full fxt/ history is:

```
PRW substrate current J(x,t) [EXISTING]
    ↓ [A] assign quantum structure to direction sector
direction qubit ℂ²_dir [ASSUMED]
    ↓ [A] add energy sector with gap Δε = η·n₀
energy qubit ℂ²_E [ASSUMED + requires η]
    ↓ [A] introduce bosonic bath H_B
bath H_B [IMPORTED from standard QM]
    ↓ [TARGET-INFORMED] couple bath to energy sector specifically
H_int = λ(b+b†) ⊗ â†_create [TARGET-INFORMED]
    ↓ [D] Born-Markov-Secular reduction
Lindblad with rate Γ = (2π/ℏ)|λ|²ρ_bath [DERIVED, uses ℏ]
    ↓ [ASSUMED] high-temperature limit n_{e₁} ≈ e±/ε₁
C± = α·e± [DERIVED given prior]
    ↓ [D] sum over directions
C_total = αE [DERIVED given prior]
```

Arrow classification summary:

| Arrow | Status |
|-------|--------|
| PRW → direction qubit | ASSUMED |
| Direction qubit → energy qubit | ASSUMED + requires η |
| Energy qubit → bath | IMPORTED |
| Bath → energy-sector H_int | TARGET-INFORMED |
| H_int → Lindblad | DERIVED (standard) |
| Lindblad → C± | DERIVED (given high-T assumption) |

Only 2 of 6 arrows are derived. The critical arrow (bath → energy-sector H_int)
is TARGET-INFORMED — it is the step where the desired result is assumed.

---

## 11. Why That Route Fails

The route fails at Arrow 4 (bath → energy-sector coupling).

The interaction H_int = λ(b+b†) ⊗ â†_{e₀}â_{e₁} was constructed specifically
because it produces C± ∝ e± → αE. An equally valid construction
H_int = λ(b+b†) ⊗ σ_x^dir would produce C± ∝ direction-flip rate ∝ s.
Another construction H_int = λ(b+b†) ⊗ σ_z^dir would produce C± ∝ n⁺−n⁻.

The project contains no physical argument that selects the energy-sector operator
â†_{e₀}â_{e₁} over any other Hermitian operator in the system Hilbert space.
The INTERACTION_SPACE_AUDIT.md proves that positivity, conservation, symmetry,
and detailed balance cannot make this selection.

Therefore the route is circular at Arrow 4: it assumes the result (αE arises
from energy) by choosing a coupling that is proportional to energy occupancy.

Additionally, the route fails at Arrow 2 because η is required but not derived —
the same gap proved in July 2026. And it fails at Arrow 1 because no quantum
structure is derived from the PRW; the O1 extension must be assumed.

---

## 12. No-Go Results

All of the following are proved results in the fxt/ history:

| No-go | Proof location | Status |
|-------|---------------|--------|
| kg ∉ D_C2 | C2_structural_obstruction_audit.md | PROVED [OBS F3] |
| ℏ independent of C2 | C2_MISSING_PRINCIPLES.md §2 | PROVED |
| C± never derived from dynamics | All pre-session documents | FORENSIC FINDING |
| PRW observable algebra commutative | C2_FOUNDATIONS.md | PROVED [OBS F4] |
| No selection principle forces energy-sector coupling | INTERACTION_SPACE_AUDIT + this audit | PROVED |
| PRW cannot be energy bath | SUBSTRATE_CLOSURE_AUDIT §5 | PROVED [OBS H_B-1] |
| FPUT phases cannot serve as bath without reversing projection | SUBSTRATE_CLOSURE_AUDIT §5 | PROVED |
| g is irreducibly free | OP3_coupling_constant_audit.md | PROVED [G-IND] |
| Second law (F9) independent of C2 | F9A_investigation.md | PROVED [F9A-MASTER] |

---

## 13. Surviving Results

The following results are NOT affected by the C± failure and survive:

| Result | Status | Evidence |
|--------|--------|----------|
| PRW → telegrapher equation | ESTABLISHED | T PRW-1, KR Goldstein-Kac |
| PRW = unique C1–C6 FPUT projection | ESTABLISHED | T FPUT-3 |
| H_int = g·J·σ_z uniqueness (given 4 assumptions) | ESTABLISHED | interaction_hamiltonian_uniqueness.md |
| Γ_φ = k_rot·ω² from Born-Markov chain | ESTABLISHED | decoherence_chain_summary.md, validated numerically |
| Spatial decoherence correlator Γ(r) ~ K₀(r/ξ_c) | ESTABLISHED | 09_spatiotemporal_c2_test/ |
| k_rot = 4.5×10⁻⁷ s empirical fit | ESTABLISHED | 06_datasets/ |
| Born rule from Gleason (given complex Hilbert space) | ESTABLISHED [KR] | C2_FOUNDATIONS.md |
| F3 dimensional obstruction | ESTABLISHED | C2_structural_obstruction_audit.md |
| Independence of η and O1 | ESTABLISHED | C2_separation_theorem_audit.md |

The transport and decoherence sectors are genuine, validated science. They do
not depend on C±. They survive the C± failure completely.

---

## 14. Exact Status of Original C2

**What C2 was claimed to be:**
A self-contained substrate theory in which transport, quantum decoherence,
and information creation all arise from a single minimal microscopic principle.

**What C2 actually is:**

The original C2 framework is a well-posed classical information transport theory
(PRW/telegrapher) with:
- One phenomenological quantum coupling (g, undetermined) attached to an external qubit
- One phenomenological energy source (αE, undetermined and undetected) inserted as external forcing
- One proved transport/decoherence prediction (Γ_φ ∝ ω²) conditional on g and ℏ

The claim of self-containedness fails at two independent points:
1. g requires kg, which is not in D_C2. [OBS F2, proved 2026-07-24]
2. αE requires kg and a microscopic creation mechanism neither of which is in C2. [OBS F3, this audit]

C2 is not a closed theory. It is a transport theory with two empirical quantum
add-ons. Both add-ons are physically plausible, but neither is derived from the
substrate.

---

## 15. Exact Status of SXC-IGC as a Whole

SXC-IGC has three layers with different scientific statuses:

**Layer A — Transport/Decoherence (SCIENTIFICALLY VALID)**
- PRW transport: derived, mathematically rigorous
- Qubit decoherence prediction: conditional on {g, ℏ, H_int form}, but internally consistent
- Spatial correlator K₀: derived, a genuine non-trivial prediction
- These results stand on their own as a coherent open-system model

**Layer B — Information Creation C± = αE (NOT DERIVED)**
- C± = αE is phenomenological throughout the entire project history
- No microscopic mechanism has ever produced it without target-informed inputs
- The F3 dimensional obstruction (kg absent from D_C2) is the root cause
- This layer is currently empty of derived content

**Layer C — Foundational Architecture (PARTIALLY ESTABLISHED)**
- CCA framework, SCC reconstruction, GPT approach: mathematically developed
- Several conjectures (CCA-C3, F8, F9) remain unproved
- The foundational layer supports Layer A but does not rescue Layer B

---

## 16. Final Classification

**C — Original C2 closure is dead.**

The specific target C± = αE cannot be derived from the existing ontology without:
1. Adding kg to D_C2 (via η or equivalent)
2. Adding ℏ as an independent quantum constant
3. Choosing the energy-sector bath coupling (circular with respect to αE)
4. Introducing an unidentified physical bath

Points 1 and 2 are proved impossible from the original ontology. Point 3 is
circular. Point 4 is a free additional assumption.

No existing SXC-IGC document contains a non-circular route. The forensic search
found no previously overlooked mechanism. The failure is structural, not a
gap in the analysis.

**D is NOT warranted.** Layers A (transport) and C (foundations) survive
independently. The decoherence prediction Γ_φ ∝ ω² is a valid scientific
result with physical content distinct from generic Lindblad decoherence.

---

## 17. What Would Have to Be Added If C2 Is Dead

If the project is to be extended to explain C± = αE, the minimal required
additions are:

**Addition 1: η [J/info]**
One new fundamental constant: the energy cost per information quantum.
This introduces kg into D_C2. It cannot be derived; it must be measured.
Physical interpretation: η is the Planck-scale energy per bit, or equivalently
a material-specific coupling between information degrees of freedom and energy.

**Addition 2: A bath identification**
The physical object constituting the thermal reservoir must be specified.
Candidates outside the PRW: electromagnetic vacuum, phonon field of a specific
material, or thermodynamic environment. The bath is context-dependent and
cannot be derived from the substrate alone.

**Addition 3: A sector selection principle**
A physical reason why the bath couples to the *energy sector* of the substrate
quantum rather than the direction or coherence sector. Without this, the
functional form C± ∝ E is assumed, not derived. A candidate principle: if
detailed balance requires C± to vanish when E → 0 (no energy available for
creation), this selects C± ∝ E uniquely among linear terms. But detailed balance
in the existing master equation already includes σ_irr as the destruction term,
and does not force the specific functional form of C± through energy alone.

**Addition 4: A value for λ_coup**
The creation coupling constant. Free parameter, calibrated empirically.
Analogous in status to g for decoherence.

**The resulting theory** (PRW + η + external bath + λ_coup) is scientifically
coherent. It would be Model M11 from C2_separation_theorem_audit.md with an
explicit bath specification. It would be an EXTENDED theory, not original C2.

---

## 18. Decision: PROCEED / STOP / PIVOT

**PIVOT.**

**Rationale:**

STOP is not warranted. Layers A and C produce valid science. The transport and
decoherence results are real, non-trivial, and partially validated.

PROCEED (continuing to attempt closure of C± within the original ontology) is
not warranted. Five independent no-go theorems are proved. No new argument
has been found. The closure path is blocked by a hard dimensional obstruction.

PIVOT means: accept that C± = αE is phenomenological and not derivable from
the original C2 ontology in its current form. Treat it honestly as what it is:
a coupling between the substrate and an external physical energy field, with
a rate constant α that must be measured. Then pursue the three surviving
directions where the project has genuine content:

1. **Experimental test of K₀ vs exp decoherence correlator** (34_C2_QUANTUM_BRANCH_STATUS.md):
   This prediction does not require C± at all. It requires only the spatial
   decoherence chain, which is fully derived. This is the most immediately
   testable result. Status: frozen for lack of IBM Eagle-class QPU access.

2. **Identification of η from an independent measurement**: If a physical
   experiment can constrain the energy-per-info-quantum scale (e.g., from
   measuring α at multiple temperatures and fitting the Bose factor), then
   η becomes an empirical constant rather than a logical gap. The bath
   mechanism then becomes predictive rather than merely descriptive.

3. **Formal extension to Model M11**: Explicitly document that the extended
   theory (PRW + η + ℏ + bath) is a distinct, named theory from the original
   C2, with its own axiom set and its own testable predictions distinct from
   the phenomenological αE postulate.

---

*End of FINAL_RESCUE_OR_KILL_AUDIT.md*
*Date: 2026-08-22*
*Verdict: C — Original C2 closure is dead. Transport/decoherence sectors survive.*
*Recommendation: PIVOT.*
