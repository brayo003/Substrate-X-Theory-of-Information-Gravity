# THEORETICAL_FACTS
## Gate 1 — What Is Established via Theoretical Inference

---

### Purpose

This document registers facts about the early cosmological state that are established by **theoretical inference from observational data**, not by direct measurement.

Each item carries an explicit inference chain: `[data] → [theory] → [claim]`, and notes the sensitivity of the claim to the theory's assumptions.

Theoretical inference is legitimate science. But knowing which claims are inferred, and from what, is essential for Gate 1.

---

## Section 1: The Smoothness of the Early Universe

### 1.1 The Claim
The universe at t_recombination (z ≈ 1100) was extremely homogeneous and isotropic on scales larger than ~100 Mpc, with density perturbations δρ/ρ ~ 10⁻⁵.

### 1.2 Inference Chain
```
CMB temperature anisotropies ΔT/T ~ 10⁻⁵
    → [ΛCDM transfer function + Boltzmann equations + standard recombination history]
    → primordial perturbation spectrum P(k) ~ k^(n_s - 1), n_s ≈ 0.965
    → [backward integration of ΛCDM Friedmann equations]
    → density field at t_recombination was nearly homogeneous
```

### 1.3 Theory Sensitivity
- Assumes ΛCDM as the correct transfer function. Modified gravity alters the mapping.
- Assumes standard recombination. Non-standard early dark energy or extra radiation would shift the last scattering surface.
- Assumes the CMB is a last-scattering surface, not substantially re-scattered (reionization corrections are model-dependent).

### 1.4 Status
`THEORETICALLY_INFERRED (strong)` — Robust within ΛCDM. The claim holds *conditional on ΛCDM being approximately correct at z ~ 1100*.

---

## Section 2: Gravitational Entropy and the Weyl Tensor

### 2.1 The Claim (Penrose)
The early universe had anomalously low gravitational entropy, quantified by suppressed Weyl curvature: C_μνρσ ≈ 0.

### 2.2 Inference Chain
```
Observed large-scale smoothness (Section 1)
    → [Penrose conjecture: gravitational entropy ∝ Weyl curvature invariants]
    → Low Weyl curvature ⟹ low gravitational entropy
    → The early universe was in a gravitationally low-entropy state
```

### 2.3 Published Criticisms — Gate 1 Requirement

The following published criticisms must be registered before this claim is used as a premise anywhere in this workspace:

**a) Clifton, Ellis & Tavakoli (2013):** Showed the Weyl tensor can be small in highly anisotropic Bianchi spacetimes under certain conditions, challenging the direct Weyl ↔ gravitational entropy identification.

**b) Buchert, Hosoya et al. (various 2004–2010):** Proposed morphological information entropy measures that do not reduce to Weyl curvature. Argued Penrose's measure misidentifies the relevant quantity for cosmological irreversibility.

**c) Wallace (2010), Wald (2006):** Argued gravitational entropy is not uniquely defined. Penrose's identification conflates geometric order with thermodynamic entropy without a derivation connecting the two.

**d) The scale factor argument:** Multiple authors argue the dominant low-entropy feature is the small spatial volume (small scale factor), not Weyl curvature. Under this reading, Weyl curvature suppression is a secondary or derived feature.

### 2.4 Status
`THEORETICALLY_INFERRED (contested)` — Penrose's Weyl-entropy identification is a **conjecture**, not a theorem. It is an uncontested entropy definition nowhere in this workspace.

---

## Section 3: Thermalization of Matter/Radiation

### 3.1 The Claim
Matter and radiation were in thermal equilibrium through the BBN epoch and until recombination.

### 3.2 Inference Chain
```
BBN light element abundances consistent with standard predictions
    + CMB black-body spectrum (FIRAS: |Δμ| < 9×10⁻⁵)
    → [Standard Model particle physics + thermal statistical mechanics]
    → Photon-baryon plasma was thermalized at T ~ 10⁹–10¹⁰ K during BBN
    → Photon-baryon fluid remained thermalized until z ≈ 1100
```

### 3.3 Theory Sensitivity
- The BBN inference assumes standard model particle physics at T ~ few MeV.
- The CMB black-body constraint applies to photons; neutrino sector thermalization is inferred, not directly measured.
- The cosmological lithium problem (Li-7 observed ≈ 1/3 of predicted) is unresolved and may indicate non-standard BBN physics.

### 3.4 Status
`THEORETICALLY_INFERRED (strong for photon-baryon sector; uncertain for other DOF)`

---

## Section 4: Suppressed Gravitational Degrees of Freedom

### 4.1 The Claim
The early universe had anomalously few excited gravitational degrees of freedom relative to a "typical" state.

### 4.2 Why This Is Inferred
There is no direct measurement of gravitational DOF. The claim is inferred from:
- Observed smoothness → low curvature fluctuations → few gravitational wave modes excited
- CMB power spectrum → perturbation spectrum is nearly scale-invariant, not a thermal graviton distribution
- Absence of detected primordial gravitational wave background (current sensitivity limits this inference)

### 4.3 The Typicality Problem
The claim that early-universe gravitational DOF were "suppressed" requires comparison to a "typical" state. This requires a well-defined measure on the space of early-universe configurations.

**No such measure is agreed upon.** Different choices give different notions of typicality. Without a specified measure, claims about the state being "special" are relative to an unspecified background — which means they are not yet well-defined physical claims.

This is not a philosophical complaint. It is a structural gap in the problem.

### 4.4 Status
`THEORETICALLY_INFERRED (weak — depends on unresolved measure question)`

---

## Section 5: The Scale Factor Low-Entropy Argument

### 5.1 The Argument
The dominant low-entropy feature of the early universe is the **small spatial volume** (small scale factor), not the Weyl tensor. Under this view:
- Entropy increases as the universe expands because available phase space grows with volume.
- The Weyl curvature story is secondary or derived.

### 5.2 Advocates
Carroll and collaborators have developed this line; Penrose himself discusses it but favors Weyl. The two framings are **not equivalent** and lead to different explanatory targets.

### 5.3 Status
`THEORETICALLY_INFERRED (contested, active debate)` — Must be tracked as a distinct hypothesis from the Weyl-entropy argument.

---

## Section 6: Macroscopic Entropy Increase

### 6.1 The Claim
Thermodynamic entropy increases from the early universe to the present.

### 6.2 The Circularity Risk
The entropy increase argument assumes the early universe was in a low-entropy state. If the low-entropy claim is `DISPUTED`, using entropy increase to establish the specialness of the early state is circular. The observed macroscopic irreversibility (thermodynamic arrow) is real; its *explanation* requires the initial condition question to be answered, not assumed.

### 6.3 Status
- Macroscopic entropy increase: `OBSERVED`
- Explanation of why: `THEORETICALLY_INFERRED` (requires establishing low initial entropy independently)

---

## Section 7: Gate 1 Summary — Distinct Claims

After Gate 1 analysis, the following are **distinct** claims, not a unified "low-entropy early universe":

| # | Claim | Status |
|---|---|---|
| 1 | Large-scale geometric smoothness at z ≈ 1100 | THEORETICALLY_INFERRED (strong) |
| 2 | Primordial perturbation amplitude δρ/ρ ~ 10⁻⁵ | OBSERVED (amplitude) / THEORETICALLY_INFERRED (primordial origin) |
| 3 | Photon-baryon thermalization | THEORETICALLY_INFERRED (strong for photons) |
| 4 | Gravitational DOF suppression | THEORETICALLY_INFERRED (weak — measure unresolved) |
| 5 | Weyl curvature smallness as gravitational entropy | THEORETICALLY_INFERRED (contested conjecture) |
| 6 | Scale factor as dominant low-entropy feature | THEORETICALLY_INFERRED (contested alternative) |
| 7 | Macroscopic entropy increase | OBSERVED (macroscopic) / THEORETICALLY_INFERRED (explanation) |

**These seven items are not equivalent. Explaining any one does not explain the others.**

Gate 2 analysis must address each independently.

---

*Document status: WORKING — Gate 1 analysis in progress*
