# DISCRIMINATOR SEARCH
## Systematic Search for an SXC-IGC Observable That Survives Adversarial Nulls

**Date:** 2026-08-22
**Method:** Exhaustive search through all C2 theory predictions for observables
  that are (a) theory-derived, (b) not reproduced by conventional mechanisms,
  and (c) measurable on realistic hardware.

---

## Candidate Inventory

| # | Observable | SXC-IGC prediction | Free params | Derived? | Conventional alternatives | Discriminating? | Class |
|---|-----------|-------------------|-------------|----------|--------------------------|----------------|-------|
| 1 | Spatial K₀ shape | K₀(r/ξ_c) spatial covariance | ξ_c, amp | Yes (2D) | Power-law, two-bath, Matérn | No — K₀≈log≈powerlaw at r<2ξ_c | **D** |
| 2 | Spatial exp shape (1D) | exp(−r/ξ_c) | ξ_c, amp | Yes (1D) | Any OU bath | No — identical form | **D** |
| 3 | Temporal ω² scaling | Γ_φ = Γ₀ + k_rot·ω² | k_rot, Γ₀ | Yes | Any sub-Ohmic bath, filter function | No — proved non-unique | **D** |
| 4 | Non-Markovian onset | Gaussian decay at t<τ_B | τ_B | Yes | Any bath with finite τ_B | No — any non-Markovian bath | **C** |
| 5 | **P3 self-consistency** | **c = ξ_c/(2τ_B) with c≠v_sound** | **none (given measured ξ_c, τ_B)** | **Yes** | **No conventional mechanism predicts this specific ratio** | **Conditional yes** | **B** |
| 6 | Lorentzian high-freq rolloff | Γ_φ rolls off as 1/ω² above ω_c=1/τ_B | τ_B | Yes | Any Lorentzian bath | No — identical form | **C** |
| 7 | Temperature scaling of ξ_c | ξ_c(T) ∝ T^{-n} if λ∝T^n | n, T₀ | Implied not derived | Phonon bath T³ or T⁵ | Conditional — if exponent differs | **B** |
| 8 | Temperature scaling of τ_B | τ_B(T) ∝ T^{-n} correlated with ξ_c(T) | n | Implied not derived | Phonon bath | Conditional | **B** |
| 9 | Joint τ_B / ξ_c ratio vs temperature | c(T) = ξ_c(T)/(2τ_B(T)) = const | none | Yes (ratio) | Phonon: c(T) = c_sound(T), slowly varying | **If measured c << v_sound: unique** | **A** |
| 10 | Multi-qubit Γ_φ fluctuation correlation | Cov(Γ_i, Γ_j) ∝ exp(−d_ij/ξ_c) | ξ_c, amp | Yes | EM crosstalk, phonon bath | No — same form as OU bath | **C** |
| 11 | NMP = τ_B · Γ_φ (measurable) | NMP predicts non-exp Ramsey onset | τ_B | Yes | Any non-Markovian bath with same τ_B | No — identical for any bath | **C** |

---

## Analysis of Each Candidate

### Candidate 1: Spatial K₀ shape
**Status: D — REJECT**

Established by the full audit. K₀ is indistinguishable from power-law covariance
over the Brisbane geometry (11 unique r bins, SNR ≈ 2). The adversarial null family
defeats this discriminator. See ADVERSARIAL_NULL_AUDIT.md and FINAL_DESIGN_SEARCH.md.

### Candidate 2: Spatial exponential (1D)
**Status: D — REJECT**

The 1D prediction (exp(−r/ξ_c)) is identical in form to any OU bath. No shape
discrimination is possible. The theory itself acknowledges this in 00_THEORY_AUDIT.md.

### Candidate 3: Temporal ω² scaling
**Status: D — REJECT**

Proved non-unique by the stress test (C2_final_prediction_audit, Outcome A).
Any sub-Ohmic bath with the right PSD gives ω² scaling. The temporal channel
is non-discriminating. Proved analytically in p25_discrimination_test.py test1.

### Candidate 4: Non-Markovian onset (Gaussian at t < τ_B)
**Status: C — Measurable but not uniquely SXC-IGC**

Any bath with finite correlation time τ_B produces Gaussian early-time decay.
This is a consequence of the bath having memory, not a consequence of the PRW
substrate specifically. It cannot distinguish C2 from a phenomenological
non-Markovian Lindblad model.

Useful for measuring τ_B, which is then needed for P3 (Candidate 9).

### Candidate 5: P3 self-consistency c = ξ_c/(2τ_B)
**Status: B — Theory-derived, conditionally discriminating, but still c is free**

**The prediction:** From the same substrate, τ_B = 1/(2λ) controls the NM onset
and ξ_c = v/λ = 2cτ_B controls spatial correlations. Therefore:
```
c = ξ_c / (2τ_B)
```

This is a derived relation: if both τ_B and ξ_c can be measured independently,
their ratio gives c. The C2 claim is that this c should equal the substrate
propagation speed.

**What makes it conditionally discriminating:** A conventional OU bath with
exponential spatial correlation and exponential temporal correlation has NO
reason to link ξ_c = 2c_bath·τ_B with the same c. A phonon bath has c = v_sound
(~5000 m/s in Si). An EM noise source has c = c_light. Uncorrelated defect noise
has no velocity.

If the measured c ≪ v_sound (say, c < 100 m/s), no conventional mechanism
can explain the link between τ_B and ξ_c at that ratio. The substrate would
be moving at a speed with no conventional counterpart.

**Why it is class B rather than A:**
- ξ_c is free (GAP-7: c is not predicted)
- The test cannot distinguish "correct c" from "coincidence"
- If c happens to equal v_sound, the test cannot distinguish C2 from phonon bath
- The test only produces anomalous evidence if c ≪ v_sound

**Assessment:** This is the STRONGEST surviving discriminator from the theory,
but it is still conditional on c being anomalous. It cannot give a definitive
positive result, only a negative one (c = v_sound → consistent with phonon bath).

### Candidate 9: c(T) = ξ_c(T)/(2τ_B(T)) = constant as function of T
**Status: A — IF c can be measured at multiple temperatures**

**The prediction:** Both ξ_c and τ_B change with temperature (if λ depends on T),
but their ratio c = ξ_c/(2τ_B) remains constant because c = v is the substrate
speed, which is a property of the substrate material, not of temperature.

This is testable: measure ξ_c(T₁)/τ_B(T₁) and ξ_c(T₂)/τ_B(T₂) at two different
chip temperatures. If C2 is correct, the ratio should be the same (same c).

**Conventional conventional mechanisms:**
- Phonon bath: v_sound changes slightly with T (~0.01% per K), essentially constant
- 1/f flux noise: τ_B(T) may change; ξ_c(T) may change independently; ratio not fixed
- EM crosstalk: speed of light, temperature-independent
- Two-bath: each bath has its own speed; no global constraint

**Critical issue:** This requires two independent temperature settings on the dilution
refrigerator. IBM Open Plan does not support user-controlled temperature variation.
This experiment is NOT feasible on the current hardware access.

It is also worth noting that c being constant with temperature only distinguishes
C2 from baths where the bath parameters change with T. If c = v_sound, the experiment
again cannot separate C2 from a conventional phonon bath.

**Status: A in principle, but hardware-inaccessible with current access.**

---

## The Lorentzian Rolloff (Candidate 6 revisited)

There is one additional discriminator worth examining carefully.

**The prediction:** At ω_rot >> 1/τ_B, the C2 substrate predicts:
```
Γ_φ(ω_rot) → Γ₀ + k_rot / (ω_rot^2 · τ_B^2)
```
(Lorentzian rolloff from the PSD S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)).

**The claim:** A conventional super-Ohmic bath (S ∝ ω^n with n > 1) would not
produce a 1/ω² rolloff — it would continue growing.

**The problem:** This is only true if the conventional bath is super-Ohmic.
An OU bath (exponential memory, Lorentzian spectrum) gives EXACTLY the same
S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²). The test cannot separate C2 from a conventional
Lorentzian bath.

Furthermore, to observe the Lorentzian rolloff, we need ω_rot · τ_B >> 1:
```
ω_rot >> 1/τ_B = 2λ ≈ 2/(5 µs) = 4 × 10^5 rad/s ≈ 64 kHz
```

The existing gamma_dataset tests ω_rot up to ~10^6 rad/s. The rolloff region
is accessible in principle. But identifying the Lorentzian shape from Γ_φ(ω_rot)
still does not distinguish C2 from a conventional Lorentzian bath — they are
mathematically identical.

**Status: C — measurable but not uniquely SXC-IGC.**

---

## Summary Table

| Candidate | Class | Reason for classification |
|-----------|-------|--------------------------|
| K₀ spatial shape | D | Degenerate with power-law over Brisbane geometry |
| Exponential spatial | D | Identical to any OU bath |
| ω² temporal | D | Proved non-unique by stress test |
| NM Gaussian onset | C | Any finite-memory bath gives same result |
| P3: c = ξ_c/(2τ_B) | **B** | Discriminating if c ≪ v_sound; requires both measurements |
| Lorentzian rolloff | C | Identical to Lorentzian bath |
| T-dependent ξ_c | B | Discriminating if exponent known; λ(T) not derived |
| T-dependent τ_B | B | Same issue |
| c(T) = const | **A** | Valid discriminator but requires T-variation hardware |

---

## The Strongest Available Discriminator

**P3 self-consistency test:**

```
Measure τ_B from NM Ramsey curvature.
Measure ξ_c from spatial decoherence correlation.
Compute c = ξ_c / (2τ_B).
Compare c to v_sound(Si) ≈ 5000–8000 m/s.
```

This is not a parameter-free prediction — c is free. But it is the only
available test that asks a question conventional physics cannot answer in advance:
what is the ratio ξ_c/(2τ_B)?

**Discriminating outcome:** If c_measured << v_sound, the substrate propagates
much slower than any known phonon mode. This would be anomalous.

**Non-discriminating outcomes:**
- c_measured ≈ v_sound → consistent with phonon bath
- τ_B is not measurable (NMP too small) → test fails

**Current NMP on Brisbane:** NMP = τ_B · Γ_φ = 5×10⁻⁶ × 6667 = 0.033.
This is well below the NMP > 0.1 threshold for reliable τ_B measurement.
The Ramsey curvature is too small to extract τ_B from the Gaussian onset.

**Therefore:** The P3 test is also not currently executable on Brisbane.
Not because the spatial measurement fails, but because τ_B is not measurable
from the NM Ramsey curvature at the current NMP = 0.033.

---

## Conclusion

No class-A observable exists that is both theory-derived and immediately
executable on the current Brisbane hardware within the 10-minute budget.

The strongest surviving candidate (P3, class B) requires:
1. Measurement of ξ_c (currently problematic due to K₀/power-law degeneracy)
2. Measurement of τ_B from NM curvature (currently impossible at NMP = 0.033)
3. Comparison to v_sound (possible once c is extracted)

Both measurements require hardware conditions not currently available:
- ξ_c measurement: larger spatial range (K₀/power-law resolution)
- τ_B measurement: higher NMP (needs shorter T₂ or longer τ_B qubits, or lower-T operation)
