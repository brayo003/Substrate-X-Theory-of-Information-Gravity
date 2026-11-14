# OBSERVATIONAL_FACTS
## Gate 1 — What Is Directly Observed

---

### Purpose

This document registers empirical facts about the early cosmological state that rest on **direct measurement**, instrument-independent of any particular theoretical model.

Entries here must meet the standard: *the measurement would yield the same result regardless of which cosmological theory is assumed to interpret it.*

Where that standard fails, the item moves to THEORETICAL_FACTS.md.

Status labels:
- `OBSERVED` — Direct measurement, minimal theoretical loading
- `THEORETICALLY_INFERRED` — Requires a theoretical framework to extract from raw data
- `DISPUTED` — Contested interpretation or measurement

---

## Section 1: CMB Temperature Anisotropies

**Status: OBSERVED (at instrument level) / THEORETICALLY_INFERRED (for cosmological interpretation)**

### 1.1 Raw Observations
- The cosmic microwave background is a nearly isotropic thermal radiation field at T ≈ 2.7255 K (FIRAS/Planck)
- Temperature fluctuations at the level of ΔT/T ~ 10⁻⁵ are observed across the sky
- The power spectrum of these fluctuations has been measured to high precision (Planck 2018)
- The acoustic peak structure in the CMB power spectrum is measured (positions, amplitudes, widths)

### 1.2 What Is Directly Measured vs. Inferred
- **Directly measured:** Photon arrival directions, frequencies, and intensities at the detector
- **Theoretically inferred:** That these photons originate from a last-scattering surface at z ≈ 1100
- **Theoretically inferred:** That ΔT/T reflects primordial density perturbations
- **Theoretically inferred:** The "early universe was smooth" — this is a theoretical reconstruction, not a direct observation of the early universe

### 1.3 Model Dependence
The conversion of CMB observations into statements about the early universe requires:
- ΛCDM or equivalent cosmological framework
- An assumed transfer function connecting early perturbations to observed temperature
- An assumed recombination history

**Implication for Gate 1:** The statement "the early universe was smooth at large scales" is `THEORETICALLY_INFERRED`, not `OBSERVED`. Treating it as direct observation is a Gate 1 violation.

---

## Section 2: Large-Scale Structure (LSS)

**Status: OBSERVED (galaxy positions) / THEORETICALLY_INFERRED (cosmological implications)**

### 2.1 Raw Observations
- Galaxy surveys (2dFGRS, SDSS, DESI, etc.) measure angular positions and redshifts of ~10⁸ galaxies
- The matter power spectrum P(k) has been measured over a wide range of scales
- Baryon acoustic oscillations (BAO) are detected as a statistical feature at ~150 Mpc
- Galaxy clusters follow a mass function consistent with ΛCDM predictions

### 2.2 What Is Directly Measured vs. Inferred
- **Directly measured:** Angular positions and redshifts of individual galaxies
- **Theoretically inferred:** 3D comoving positions (requires a cosmological distance model)
- **Theoretically inferred:** The matter power spectrum (requires bias model relating galaxy to matter distribution)
- **Theoretically inferred:** That structure grew from small initial perturbations

### 2.3 Independence Note
The growth of structure from an early smooth state is a theoretical reconstruction requiring GR perturbation theory + initial conditions. It is not directly observed.

---

## Section 3: Big Bang Nucleosynthesis (BBN) Abundances

**Status: OBSERVED (elemental abundances) / THEORETICALLY_INFERRED (early-universe conditions)**

### 3.1 Raw Observations
- Primordial helium fraction: Y_P ≈ 0.247 (measured in metal-poor HII regions)
- Deuterium/hydrogen ratio: D/H ≈ 2.5 × 10⁻⁵ (measured in quasar absorption systems)
- Lithium-7 abundance: controversial (the "cosmological lithium problem")

### 3.2 What Is Directly Measured vs. Inferred
- **Directly measured:** Spectroscopic abundances of elements in low-metallicity systems
- **Theoretically inferred:** That these reflect primordial abundances (requires understanding of stellar processing)
- **Theoretically inferred:** The early universe had a specific temperature and density at t ~ 1–1000 seconds
- **Theoretically inferred:** The early universe was in thermal equilibrium during BBN epoch

### 3.3 The Lithium Problem
The predicted Li-7 abundance from standard BBN exceeds the observed value by a factor of ~3. This is a known discrepancy. Its implications for the "thermalized early universe" claim are unresolved.

---

## Section 4: Hubble Flow and Expansion

**Status: OBSERVED (recession velocities) / THEORETICALLY_INFERRED (scale factor history)**

### 4.1 Raw Observations
- Galaxies (beyond the local group) exhibit redshifts proportional to distance (Hubble's law)
- The Hubble constant H₀ is measured by multiple methods (tension exists between CMB-inferred and local distance-ladder values)
- Type Ia supernovae indicate accelerated expansion at late times (z < 0.5 approximately)

### 4.2 Hubble Tension
- CMB-inferred H₀ ≈ 67.4 km/s/Mpc (Planck 2018)
- Local distance ladder H₀ ≈ 73 km/s/Mpc (various)
- This tension (~5σ) is an unresolved observational discrepancy

**Implication:** The standard FLRW history is not observationally established to the precision sometimes assumed. The Hubble tension may indicate new physics or systematic errors.

---

## Section 5: Summary Table for Gate 1

| Early-Universe Feature | Status | Notes |
|---|---|---|
| Extremely smooth large-scale geometry | `THEORETICALLY_INFERRED` | Reconstructed from CMB + ΛCDM |
| Small primordial anisotropies (~10⁻⁵) | `OBSERVED` (amplitude) / `THEORETICALLY_INFERRED` (primordial origin) | Direct CMB measurement; cosmological interpretation requires ΛCDM |
| Thermalized matter/radiation | `THEORETICALLY_INFERRED` | BBN + CMB spectrum are consistent with thermalization; the inference requires assuming ΛCDM + standard model |
| Suppressed free gravitational DOF | `THEORETICALLY_INFERRED` / `DISPUTED` | Inferred from Weyl tensor smallness; Weyl = gravitational entropy is contested |
| Subsequent growth of gravitational structure | `OBSERVED` (structure exists) / `THEORETICALLY_INFERRED` (it grew from early smooth state) | Growth history is reconstructed, not observed |
| Macroscopic entropy increase | `THEORETICALLY_INFERRED` | Entropy increase is inferred from thermodynamic arguments; entropy of the universe is not directly measured |

---

## Section 6: Key Ambiguities to Resolve in Gate 1

1. **What does "smooth" mean precisely?** Homogeneous on what scale? Measured how? The Grishchuk-Zel'dovich effect constrains very large-scale anisotropies; CMB constrains intermediate scales; sub-horizon scales are in the "small perturbation" regime.

2. **Is thermalization a feature of the early universe or a feature of the post-BBN universe?** The CMB thermalization is a feature of the photon-baryon fluid, not necessarily of all degrees of freedom.

3. **What exactly is the gravitational entropy of the early universe?** This question must be answered in THEORETICAL_FACTS.md, not assumed here.

4. **Does the entropy increase from early to late times require a special initial state?** This is a theoretical question, not an observational one. It belongs in 04_RESIDUAL_PROBLEM/.

---

*Document status: WORKING — Gate 1 analysis in progress*
*Populated with observational framework; theoretical interpretation analysis in THEORETICAL_FACTS.md*
