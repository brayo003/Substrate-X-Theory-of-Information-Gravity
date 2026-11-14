# Document 23 — Decision and Verdict
## Phase 9: All 20 Questions Answered

**Date:** 2026-08-21  
**Platform:** Pure simulation  
**Experiment type:** Synthetic C2 joint d_c + τ_B test, 7-qubit heavy-hex geometry

---

## The 20 Questions

**Q1. What hardware was actually used?**  
Pure Python/NumPy simulation. No QPU. IBM access is unavailable (confirmed constraint). The simulation uses the exact C2 coherence formula [EXACT-PHI] with realistic shot noise (binomial, 8192 shots/point) and per-qubit parameter spread.

**Q2. Was it real hardware or simulation?**  
Simulation. This means results are self-consistent by construction (the model that generated the data also wins the fit) and cannot be treated as hardware evidence. All claims are qualified accordingly.

**Q3. How many qubits?**  
7 qubits (Q00–Q06), IBM Falcon r5 heavy-hex layout, 200 µm lattice spacing.

**Q4. How many shots?**  
8,192 shots per Ramsey delay point (main experiment). 4,096 in synthetic recovery.

**Q5. How many delay points?**  
50 log-spaced from 100 ns to 500 µs.

**Q6. How many repeated spatial measurements?**  
500 noise realizations for the phase-noise correlation matrix.

**Q7. What was the physical qubit geometry?**  
Heavy-hex: Q00–Q02 on row 1, Q03–Q05 on row 2, Q06 on row 3. Nearest-neighbor spacing 200 µm. Maximum separation 632 µm.

**Q8. What τ_B values were actually constrained?**  
τ_B = 4.59 – 6.38 µs across 7 qubits (injected: 5.00 µs). CV = 0.10. All 7 qubits yielded valid, unbounded τ_B fits. Mean = 5.34 µs, bias = +6.8%.

**Q9. What d_c values were actually measured?**  
d_c = 11.3 ± 218.1 µm from exponential spatial fit. However, the null model (flat correlation) is preferred over exponential (ΔAIC = −9.88). The d_c estimate is **not reliable** — it is off from injection value (50,000 µm) by a factor of ~4,400, with 1923% fractional uncertainty. d_c is not measurable on this geometry.

**Q10. Was K0 statistically preferred?**  
K0 was not fitted as a separate model (K0 requires the 2D PRW derivation; at d/ξ_c << 1 it reduces to exponential). The exponential model was not preferred over null. K0 would fare no better.

**Q11. Was exponential (spatial) statistically preferred?**  
No. Null model preferred by ΔAIC = 9.88 units. The spatial correlation is too flat to fit a decay length.

**Q12. Was null rejected?**  
No. Null is the preferred spatial model. The spatial signal is dominated by common-mode noise.

**Q13. How much correlation was common-mode?**  
Mean off-diagonal correlation = 0.9972. Essentially 100% of the observed inter-qubit correlation is consistent with common-mode noise. The injected spatial-decay component (amplitude ~0.008 at max separation) is undetectable above the common-mode floor.

**Q14. What is c_C2 = d_c/τ_B?**  
Measured: ~2.1 m/s (mean across qubits, from unreliable d_c estimate).  
Injected: 1.0 × 10⁴ m/s.  
The measured value is off by a factor of ~4,700 due to d_c being unresolved.  
**The joint test cannot be completed with this geometry.**

**Q15. What is its uncertainty?**  
Fractional uncertainty on c_C2: 1,923%. The uncertainty is dominated entirely by the spatial fit. This is not a statistical fluctuation — it is a structural limitation.

**Q16. Is it stable across independent subsets?**  
Internally consistent: half1 = 2.34 m/s, half2 = 2.00 m/s, ratio = 1.17 (within 2×). But consistency here means both halves are consistently wrong by the same factor. Internal consistency does not indicate correctness when d_c is unresolved.

**Q17. Do conventional OU/noise models explain the same result?**  
Yes, completely. The OU colored-noise coherence function is mathematically identical to C2 [EXACT-PHI]. AIC for OU ≈ AIC for C2-exact on all qubits (differences are optimizer artifacts, not model differences). Common-mode noise explains all spatial correlations. No observable in this experiment distinguishes C2 from a conventional noise model.

**Q18. Does this experiment falsify C2?**  
No. The geometric constraint prevents the decisive test from being executed. The null result on spatial d_c is a consequence of ξ_c >> chip size, not a falsification of the spatial prediction. C2 is not contradicted; it is untested on the spatial observable.

**Q19. Does it provide evidence for C2?**  
No. The C2-exact model wins 7/7 qubits by BIC, but this is expected in simulation (the true model wins). The OU model (indistinguishable from C2) would win equally well. The non-Markovian decay shape is confirmed but is equally consistent with OU. No evidence specific to C2 was produced.

**Q20. Or is it merely C2-compatible?**  
Yes, C2-compatible (as is OU, as is any model that produces non-Markovian dephasing). The data is consistent with C2 on the temporal observable, but the experiment was not diagnostic. The result is: **COMPATIBLE / UNDERDETERMINED.**

---

## Summary Verdict

**C2 QUANTUM LAYER: COMPATIBLE / UNDERDETERMINED**

### What this experiment established:

| Finding | Status |
|---------|--------|
| τ_B measurable at NMP ~ 1–2 | ✓ Confirmed (τ_B accurate to 7%) |
| Non-Markovian decay shape present | ✓ Confirmed on 7/7 qubits |
| C2-exact preferred over exponential | ✓ ΔBIC > 6000 |
| C2-exact preferred over stretched-exp | ✓ Marginal (ΔBIC ~5–20) |
| d_c measurable on 7-qubit chip | ✗ Not measurable (ξ_c >> chip) |
| Joint test c = d_c/τ_B completable | ✗ Not completable |
| C2 distinguished from OU | ✗ Impossible (identical formula) |
| Spatial signal above common-mode | ✗ Null model preferred |

### What remains unresolved:

The decisive test is `c_C2 = d_c / τ_B` measured on the same chip. This requires either:
1. A QPU with qubit spacing comparable to ξ_c (not available at this c_C2 scale)
2. A different prediction regime where ξ_c < 1 mm (requires c < ~100 m/s or τ_B < 5 ns)
3. A non-Ramsey experiment (e.g., two-qubit noise cross-correlation spectroscopy in frequency domain)

Without this, the project remains frozen at:

> **C2 QUANTUM LAYER: FROZEN — NOT FALSIFIED — NOT CONFIRMED**
