# 07_R1_REFORMULATIONS
## Alternative Precise Formulations of R1

**Date:** August 2026

Each formulation is evaluated for: mathematical precision, faithfulness to the original physical problem, tractability, and strength.

---

## Current Formulation (R1-original)

"There is no derivation, from independent premises, of why the gravitational degrees of freedom of the early universe occupied an extremely small region of their available phase space, corresponding to suppression of gravitational/Weyl degrees of freedom."

**Assessment:**
- Uses "extremely small region of phase space" — requires undefined measure (02_MEASURE_AUDIT.md)
- Uses "gravitational degrees of freedom" / "Weyl suppression" — partially tied to Penrose WCH (03_WEYL_ENTROPY_AUDIT.md)
- "No derivation from independent premises exists" — this part is clean and epistemological
- Mathematical precision: MEDIUM. The target is clear (near-FLRW) but "small region" is not defined.

---

## R1-A: Quantum State Concentration

"No mechanism derives, from independent premises, why the quantum state of the gravitational field at the Planck epoch had support concentrated on semiclassical geometries with C_{αβγδ} << M_Planck² g_{αβγδ} (schematically)."

**Strength:** Strong — directly identifies the quantum state as the object to be derived.

**Weakness:** Requires specifying what "support concentrated" means (still a measure question, now on Hilbert space rather than phase space). Also uses a specific threshold C << M_Planck² which is a quantitative claim requiring justification.

**Mathematical precision:** MEDIUM-HIGH. The Hilbert space of quantum gravity is better-defined (in principle) than the classical phase space measure. But the concentration statement requires a measure on Hilbert space.

**Is it the original problem?** YES — this is the quantum version of R1, appropriate if quantum gravity is the relevant framework.

---

## R1-B: Probability Distribution Over Initial Data

"No physical theory derives a probability distribution P(h_ij, K_ij) over gravitational initial data such that P assigns the overwhelming majority of probability to configurations with near-zero Weyl curvature, without the distribution P encoding low Weyl as an input."

**Strength:** Explicitly incorporates the measure problem — it asks for a derived probability distribution, not just the existence of a measure.

**Weakness:** Still requires a probability measure on Γ_GR — merely relocates the question to "where does P come from?" Any P that assigns high weight to FLRW is already solving the problem by fiat unless it is derived.

**Mathematical precision:** HIGH — explicitly requires a probability measure derived from first principles.

**Is it the original problem?** YES — this is the most direct statement of what needs to be derived.

---

## R1-C: Dynamical Inaccessibility

"No mechanism establishes that high-Weyl initial data is dynamically inaccessible — i.e., that no physical process can produce a cosmological initial state with C² >> ε for independently determined threshold ε."

**Strength:** Frames R1 as a dynamical question. Does not require a measure. Requires only that high-Weyl initial data be excluded from physical preparation/production.

**Weakness:** "Dynamically inaccessible" must be defined. What determines whether a configuration is accessible? If the universe had no prior epoch, every configuration is equally "accessible" — the notion requires a prior dynamical history, which is part of what R1 is trying to explain.

**Mathematical precision:** MEDIUM. The concept of dynamical inaccessibility is not precisely defined for cosmological initial conditions.

**Is it the original problem?** PARTIALLY — this is the Category 2 (dynamical) framing. It is weaker than the original R1, which asks about initial-data selection (Category 1).

---

## R1-D: Physical Theory Has Restricted Initial-Data Sector

"The correct theory of quantum gravity has, as a consequence, a physical initial-data sector Γ_phys ⊊ Γ_GR that consists only of configurations with small Weyl curvature. No existing theory derives this sector."

**Strength:** Clean mathematical statement. Avoids the measure problem (it says Γ_phys ⊊ Γ_GR without requiring a measure on the complement). States what needs to be derived.

**Weakness:** "Small Weyl curvature" still requires quantification. What counts as small? The answer depends on the physical context and energy scale.

**Mathematical precision:** HIGH (modulo the "small" quantification).

**Is it the original problem?** YES — this is the closest to the original formulation without the measure language.

---

## R1-E: Probability Under Physically Justified Measure

"The observed early-universe geometry is overwhelmingly more probable than generic GR initial data under a physically justified measure. No such measure has been derived."

**Strength:** Incorporates "physically justified" — demands that the measure itself be derived, not assumed.

**Weakness:** Still requires a measure. The requirement that it be "physically justified" is a qualitative constraint that needs formalization.

**Mathematical precision:** MEDIUM.

**Is it the original problem?** CLOSE — this is the probabilistic framing that is closest to the Penrose original motivation.

---

## R1-F: Explanatory Gap (Measure-Free)

"No derivation from independent premises explains why the cosmological initial configuration was (h_ij ≈ a²δ_ij, K_ij ≈ Hδ_ij + small perturbations) rather than a Kasner, Bianchi IX, or strongly inhomogeneous configuration."

**Strength:** Completely avoids gravitational entropy, Weyl curvature as an endpoint, and the measure problem. States the empirical gap directly.

**Weakness:** Does not quantify "small" or specify what counts as an explanation. Weaker than R1-D in that it does not require Γ_phys ⊊ Γ_GR — just an explanation for the specific realized configuration.

**Mathematical precision:** LOW-MEDIUM. Clear target (near-FLRW realized vs. alternatives not realized) but no formal mathematical structure for the "explanation."

**Is it the original problem?** CLOSEST TO PENROSE'S ORIGINAL MOTIVATION — simply: why was the universe smooth when it didn't have to be?

---

## Comparison Table

| Formulation | Measure required? | WCH required? | Mathematical precision | Faithfulness to original | Tractability |
|-------------|------------------|--------------|----------------------|--------------------------|-------------|
| R1-original | YES (undefined) | Partially | MEDIUM | HIGH | MEDIUM |
| R1-A (quantum state) | On Hilbert space | NO | MEDIUM-HIGH | HIGH | LOW (no QG Hilbert space) |
| R1-B (probability) | YES (must derive it) | NO | HIGH | HIGH | LOW |
| R1-C (dynamical) | NO | NO | MEDIUM | PARTIAL | MEDIUM |
| R1-D (restricted sector) | NO | Partially | HIGH | HIGH | MEDIUM |
| R1-E (justified measure) | YES | NO | MEDIUM | HIGH | LOW |
| R1-F (explanatory gap) | NO | NO | LOW-MEDIUM | HIGHEST | HIGH |

---

## Recommended Formulation

**R1-D** is the strongest mathematically precise formulation that avoids the measure problem:

"The correct theory of quantum gravity has a physical initial-data sector Γ_phys ⊊ Γ_GR consisting only of configurations with C² << C²_threshold at the Planck epoch, where C²_threshold is determined by the theory. No existing theory derives this sector."

This formulation:
- Does not require the Penrose WCH
- Does not require a canonical measure on Γ_GR
- Requires only that the theory identify a restricted sector
- Requires the threshold to be derived from the theory (not assumed)
- Is falsifiable: any proposed theory either produces the sector or does not

The C²_threshold is not a free parameter — it is derived from the physical theory (e.g., the Planck scale M_Planck² if the AS mechanism operated near the fixed point). The question becomes: which physical theory produces Γ_phys that is specifically the low-C² sector?

---

*Document status: R1 REFORMULATIONS COMPLETE*
*Recommended formulation: R1-D — restricted initial-data sector without measure or WCH.*
*Date: August 2026*
