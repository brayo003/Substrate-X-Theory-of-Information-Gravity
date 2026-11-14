# EXPERIMENTAL_TARGET_REDESIGN.md
## Best Measurement Target from Surviving Theory

**Date:** 2026-08-22
**Constraint:** Do not assume decoherence. Derive the best experiment from
  the surviving theoretical predictions.
**Sources:** DISCRIMINATOR_RECONSTRUCTION.md, SUBSTRATE_CANDIDATE_AUDIT.md,
  THEORY_EXTENSION_SEARCH.md, PREDICTION_LADDER.md

---

## What Survives from Theory

From DISCRIMINATOR_RECONSTRUCTION.md, exactly two candidates partially survive:

1. **Causal wavefront** — discriminates C2 from diffusion-type baths.
   Does NOT discriminate from phonon bath (phonon bath also has wavefront).

2. **P3 anomalous c** — discriminates if c_measured ≪ v_s.
   Theory does not predict what c will be. Requires NMP ≥ 0.1.

From THEORY_EXTENSION_SEARCH.md:
- Extension A (c = v_s) collapses C2 into conventional acoustic phonon physics.
- Extension B: no physically credible slow-mode substrate found.

**The surviving experiment must:**
- Measure the propagation SPEED of decoherence correlations directly
- Not assume the K₀ shape (shape test is not discriminating)
- Distinguish a finite-speed causal substrate from diffusion-type noise
- Be feasible in principle on realistic hardware

---

## The Measurement Target: Propagation Speed of Correlation Onset

**Physical observable:**
The TIME at which spatial decoherence correlations first become non-zero
between two qubits separated by distance r.

In the C2/telegrapher model: correlations arrive at t_onset = r/c.
In a diffusion bath: correlations are formally non-zero for all t > 0.
In a phonon bath: correlations arrive at t_onset = r/v_s.

**This is a causal propagation measurement, not a shape test.**

### Protocol

**Step 1:** Prepare both qubits in |+⟩ = (|0⟩+|1⟩)/√2 simultaneously.
**Step 2:** Wait for time t_wait.
**Step 3:** Measure both qubits in X basis (simultaneous parity measurement).
**Step 4:** Compute C_ij(t_wait) = ⟨σ_x,i σ_x,j⟩ / (⟨σ_x,i⟩⟨σ_x,j⟩).
**Step 5:** Repeat for many values of t_wait from 0 to ~T₂.
**Step 6:** For each qubit pair (i,j) at separation r_ij, plot C_ij(t_wait).
**Step 7:** Extract the onset time t_onset(r) — the first t where C_ij > threshold.
**Step 8:** Plot t_onset vs r. Measure the slope: c_measured = r / t_onset.

### What the result tells us

| Outcome | Interpretation |
|---------|---------------|
| t_onset ∝ r with slope c_measured ≈ v_s | Extension A — phonon bath or C2 equivalent |
| t_onset ∝ r with slope c_measured ≪ v_s | Anomalous — no conventional mechanism (Extension B territory) |
| t_onset = 0 for all r | Diffusion/OU bath — no causal front |
| t_onset varies non-monotonically with r | Circuit-mediated coupling, not substrate |

### Discrimination power

**vs. OU/diffusion bath:** STRONG. Diffusion has no wavefront; C2 has a sharp onset.
**vs. phonon bath:** CONDITIONAL. Phonon bath gives onset at v_s. If c_measured = v_s, not discriminating.
**vs. EM coupling:** CONDITIONAL. EM gives onset at c_EM ≈ 10⁸ m/s (instantaneous at chip scale).

---

## Hardware Requirements

| Requirement | Value | Current status |
|------------|-------|---------------|
| Qubit T₂ | ≥ 50 µs | Brisbane T₂ ~ 150 µs — SUFFICIENT |
| Qubit pairs | ≥5 unique separations spanning 0.2–5 mm | Brisbane has this — SUFFICIENT |
| Time resolution | ≤ 0.5 µs steps | IBM Ramsey allows fine t_wait — SUFFICIENT |
| Simultaneous readout | Joint parity measurement | Corrected estimator verified — SUFFICIENT |
| Statistical power | ~1000 shots per (pair, t_wait) | Within 10-min budget — MARGINAL |

**Critical hardware question:** Can the onset time be measured reliably?

For c = v_s = 6000 m/s and r = 1 mm: t_onset = 0.17 µs.
For c = 100 m/s and r = 1 mm: t_onset = 10 µs (within T₂).
For c = 10 m/s and r = 1 mm: t_onset = 100 µs (exceeds T₂ — not measurable).

**Minimum measurable c on Brisbane:** c_min ≈ r/T₂ = 1mm/150µs ≈ 7 m/s.

At c = v_s = 6000 m/s: the onset at r = 1 mm occurs at t = 0.17 µs, which
is above the minimum detectable time step (~0.01 µs). The onset IS detectable
in principle even for the acoustic phonon case.

However: at c = v_s, the signal amplitude at t_onset is very small (just above
the noise floor). Detecting the precise onset time requires careful statistical
analysis.

---

## Why This Is Better Than the K₀ Shape Test

The K₀ shape test failed because:
- The K₀ shape is degenerate with power-law over 11 bins
- Requires fitting 2 free parameters simultaneously
- Shape SNR ≈ 2 (not enough)

The causal onset test:
- Measures a single number per qubit pair (t_onset)
- Does not require fitting a spatial shape
- Tests a binary property (is there a causal front or not?)
- The measured quantity (c = r/t_onset) is independent of spatial shape

**This is a fundamentally different discriminator from the shape test.**

---

## Experimental Status

**Can this experiment be run on current Brisbane hardware?**

In principle: YES — the hardware has sufficient T₂, qubit separation range,
and time resolution.

**Is this experiment authorized by the RESCUE_GATE?**

NO — the RESCUE_GATE forbids IBM QPU execution until both:
1. A theoretical precondition is satisfied (theory extension resolving GAP-7)
2. A hardware precondition is satisfied

The theoretical precondition is NOT satisfied: the theory does not predict
what c will be. Running this experiment without a prior theoretical prediction
of c is a PARAMETER FIT, not a theory test.

**The causal onset experiment is the correct experimental design IF the
theory first provides a prediction for c.** Under Extension A (c = v_s),
the prediction exists — but the result would not distinguish C2 from a
phonon bath. Under Extension B, the prediction does not exist yet.

---

## Conclusion

**The best measurement target from surviving theory is:**
The causal propagation speed c = r/t_onset, measured from the onset of
spatial decoherence correlations as a function of qubit separation and wait time.

**Why:** This test bypasses the K₀/power-law shape degeneracy entirely.
It directly measures the propagation speed of the substrate, which is the
central unknown quantity (GAP-7).

**When it becomes valid:** After the theory predicts c.
- Extension A predicts c = v_s ≈ 6000 m/s for Si — testable but not discriminating.
- Extension B has not produced a prediction — experiment cannot be designed.

**Hardware readiness:** Technically feasible on Brisbane-class hardware.
**Theoretical readiness:** NOT READY — c is not predicted by current C2.
**Authorization:** NOT AUTHORIZED — RESCUE_GATE preconditions unmet.
