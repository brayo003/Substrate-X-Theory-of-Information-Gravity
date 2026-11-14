# DECOHERENCE_ROLE_AUDIT.md
## Is SXC-IGC Actually a Theory of Decoherence, or Something Else?

**Date:** 2026-08-22

---

## The Chain: SXC-IGC Ontology → Decoherence

Tracing each step with the exact axiom that introduces new content:

```
Step 1: Primitive ontology — "information substrate" with PRW dynamics
        [A-FPUT1, A-PRW1-3: AXIOMS]
        ↓
Step 2: Telegrapher equation for s(x,t)
        [B: DERIVED exactly — Goldstein-Kac theorem]
        ↓
Step 3: Substrate current J(x,t) = v(n⁺−n⁻)
        [C: DEFINITION]
        ↓
Step 4: Coupling Hamiltonian H_int = g·J(x_q,t)·σ_z
        [A-HC5, A-HC6: NEW AXIOMS — NOT derived from Steps 1-3]
        ↓
Step 5: Born, Markov, secular approximations applied
        [A-HC1, A-HC2, A-HC3: NEW AXIOMS — standard open-system assumptions]
        ↓
Step 6: Lindblad master equation dρ/dt = (Γ_φ/2)(σ_z ρ σ_z − ρ)
        [B: DERIVED from Steps 4-5 by standard quantum optics]
        ↓
Step 7: Γ_φ = g²S_JJ(ω_rot)/ℏ² = k_rot·ω_rot²
        [B: DERIVED from Steps 4-6 given telegrapher S_JJ]
        ↓
Step 8: Ramsey decay W(t) = exp(−Φ(t))
        [B: DERIVED — Kubo formula]
```

---

## Where Does Distinctive SXC-IGC Content Enter?

**Step 1→2:** The telegrapher equation follows from the PRW. This step is
genuine C2 content. However, the telegrapher equation is mathematically
identical to the Maxwell-Cattaneo / EIT equation. No distinctive content.

**Step 2→3:** J is defined from the PRW variables. No distinctive content —
J is just the flux in any transport equation.

**Step 3→4:** This is the CRITICAL STEP. The coupling H_int = g·J·σ_z is
ASSUMED, not derived. It requires TWO new independent axioms (A-HC5, A-HC6)
plus a free parameter g. This is where the theory transitions from substrate
dynamics to quantum decoherence.

**Distinctive SXC-IGC content that enters at Step 4:** NONE beyond what is
already assumed. The form H_int = g·J·σ_z is the standard spin-boson coupling
of open quantum systems (Leggett et al. 1987). It is not unique to SXC-IGC.

**Step 4→6:** Pure quantum optics. No substrate content enters.

**Step 6→7:** S_JJ(ω) = 2S₀τ/(1+ω²τ²) from the telegrapher enters here.
This is the one place substrate dynamics affects the decoherence prediction.
But: S_JJ is Lorentzian → also produced by OU bath with same τ.
The substrate dynamics are observationally equivalent to an OU bath.

---

## Classification of Decoherence Role

**A. Is decoherence the fundamental prediction of SXC-IGC?**

NO. Decoherence appears at Step 4 via an independently assumed coupling.
The substrate (Steps 1-3) does not generate decoherence on its own.
Decoherence is not a fundamental prediction — it is a conditional consequence
of the coupling assumption.

**B. Is decoherence merely one readout channel for substrate dynamics?**

PARTIALLY YES. The qubit acts as a sensor of substrate fluctuations via J.
But since S_JJ is conventionally equivalent to an OU bath, the "readout"
reveals nothing about the SXC-IGC substrate specifically.

**C. Is decoherence an incidental consequence shared by conventional open-system physics?**

YES. The decoherence structure (Lindblad, T₂≤2T₁, Γ_φ = k_rot·ω_rot²)
follows entirely from standard Born-Markov-secular open-system theory applied
to ANY bath with Lorentzian PSD. SXC-IGC adds no distinctive quantum structure.

**D. Is decoherence NOT actually a distinctive prediction at all?**

YES. This is the correct classification.

The decoherence predictions (Γ_φ scaling, W(t) form, spatial K₀ correlations)
are all reproduced by conventional open-system physics with an OU bath or
acoustic phonon bath. No prediction is distinctive to SXC-IGC.

---

## The Decisive Point: Step 4 Is Where the Theory Connects to Qubits

The connection between the C2 substrate and quantum decoherence rests entirely
on the assumed form H_int = g·J·σ_z. This is:

1. NOT derived from the PRW/telegrapher
2. NOT derived from the CCA/C2 foundational axioms
3. Identical in form to the standard spin-boson coupling
4. Introducing a free parameter g with no physical determination

If H_int = g·J·σ_z is removed, C2 has zero connection to quantum decoherence.
If H_int = g·J·σ_z is retained, the resulting decoherence is identical to
spin-boson / OU bath decoherence.

Either way: no distinctive content.

---

## Final Answer

The SXC-IGC empirical program as currently formulated has accidentally become
a generic quantum-noise experiment. The chain:

    PRW substrate → telegrapher J(x,t) → H_int = gJσ_z → Lindblad → Γ_φ

contains no step that introduces content unique to the SXC-IGC ontology.
Every step is either:
- Mathematically equivalent to a conventional framework (telegrapher = EIT)
- Introduced as an independent assumption (H_int form)
- Standard quantum optics (Born-Markov-secular)

**The decoherence measurement is a measurement of S_JJ(ω), not of the SXC-IGC ontology.**
S_JJ being Lorentzian is consistent with C2 but equally consistent with any
OU/phonon/TLS bath. The ontology is not tested.
