# PHASE_SPACE_RESULTS
## Gate 5 Part V — Phase-Space Analysis (Upgraded)

**Candidates:** P01 (Asymptotic Safety), P06 (Anomaly-Freedom)
**Date:** August 2026

Three logically distinct outcomes are distinguished:

**A. TRUE RESTRICTION:** Γ_phys ⊊ Γ_GR is derived. High-Weyl configurations are excluded.
**B. WEIGHTING ONLY:** Γ_phys = Γ_GR but configurations receive different quantum amplitudes. High-Weyl configurations are suppressed in measure but not excluded.
**C. NO RESTRICTION:** The candidate leaves Γ_GR unchanged and provides no derived selection.

B is not equivalent to A. Weighting produces a preference, not a prohibition. R1 asks why the high-Weyl sector was not realized — a weighting answer says it was merely improbable, which requires a well-defined measure and a quantitative concentration argument. A restriction answer says it was impossible.

---

## P01 — Asymptotic Safety

### What P01 actually does to Γ_GR

The asymptotic safety mechanism operates in two stages that must be kept separate:

**Stage 1: Theory-space restriction.**
The UV fixed point G* in the space of couplings T = {G(k), Λ(k), β(k), ...} constrains the renormalized trajectory. Only theories on the UV critical manifold S_UV are physically realizable. This is a restriction in *theory space*, not in *initial-data space*. It means: the effective action at k→0 is not arbitrary — it has specific values of α, β fixed by the flow from G*.

**Stage 2: Configuration weighting within the effective theory.**
Given the effective action Γ_0 with β > 0, the path-integral measure over configurations is:

  dμ[g] = Dg · exp(−Γ_0[g])

where Γ_0[g] = (1/16πG)∫√g[R − 2Λ + αR² + βC²] + ...

A configuration with large Weyl curvature has a larger action Γ_0 (since β > 0 adds a positive C² contribution) and is suppressed in the measure by exp(−β∫C²). This is a **weighting**, not an exclusion.

### Outcome classification for P01

**Outcome: B — WEIGHTING ONLY (at best)**

Here is why it cannot be A:

1. **Classical solutions are not excluded.** The path integral extremizes the action, producing equations of motion. Classical solutions of δΓ_0/δg = 0 satisfy the modified GR equations including the Bach tensor term. Kasner (Bianchi I) with B_{μν} = 0 *is* a solution of the modified equations when the Bach tensor vanishes — and the Bach tensor vanishes when the Weyl tensor is algebraically special (e.g., Petrov type D). Kasner is Petrov type D. Therefore Kasner is a classical solution of the P01-modified equations. It is not excluded.

2. **The suppression is quantitative, not absolute.** The measure suppression exp(−β∫C²√g d⁴x) is a continuous weighting. For any finite β, there exist configurations with large C² that are suppressed but not prohibited. The path integral assigns them nonzero measure.

3. **The semiclassical transition does not sharpen the weighting into a restriction.** As ℏ → 0, the path integral is dominated by the saddle but does not become a delta function on a single configuration. All saddle points of the action (all classical solutions of the modified equations) contribute. Kasner is one such saddle.

### Does the weighting produce a quantitative concentration?

This requires checking whether the weight exp(−β∫C²√g d⁴x) is sufficiently peaked around low-Weyl configurations to produce a measure-theoretically concentrated distribution.

For FLRW: C_{μνρσ} = 0 exactly, so the C² contribution is zero. The weight is exp(0) = 1.

For Kasner with anisotropy parameters (p₁,p₂,p₃): C² = (2/3)[(p₁−p₂)²+(p₂−p₃)²+(p₃−p₁)²]/t⁴ integrated over a spacetime volume V ~ t_f⁴ (from t=0 to some final time t_f). The weight is exp(−β·C̄²·V) where C̄² is the volume-average of C².

For generic Kasner, C̄² ~ O(1) in Planck units and V is the Planck-volume region where the AS mechanism is active. So the suppression factor is exp(−β·O(1)). For β ~ O(1), this is a suppression of order e⁻¹ ~ 0.37 — a factor of less than 3, not an exponential elimination.

For highly anisotropic Kasner (p₁ → 1, p₂,p₃ → 0): C² ~ 2/t⁴, giving a larger suppression. But the integral ∫C²√g dt d³x is dominated by the early time region near t → 0 where the singularity is approached — and in the AS framework, the singularity is resolved by the running of G(k). The effective suppression integrates over the Planck-epoch region only, which is a finite contribution.

**Conclusion:** The weighting is real but the suppression factor for Kasner relative to FLRW is of order exp(−β·O(1)), which for β ~ 1 is an O(1) suppression — not the exponential suppression of high-Weyl states needed to enforce an actual restriction. The measure of Γ_phys is not small relative to Γ_GR in any meaningful sense; the ratio is O(1) for typical adversarial configurations.

### The decisive gap: weighting vs. restriction

P01 achieves outcome B at best. The path-integral weighting with β > 0 assigns lower amplitude to high-Weyl configurations, but:
- Does not exclude any classical GR solution
- Does not produce an exponentially small weight for Bianchi I Kasner
- Does not establish a well-defined probability measure on the space of initial data (the path integral over all geometries requires ultraviolet regularization, which the AS program attempts but has not completed)

**P01 Phase-Space Verdict: OUTCOME B — WEIGHTING ONLY. The mechanism suppresses high-Weyl configurations in the quantum path-integral measure but does not derive a true restriction Γ_phys ⊊ Γ_GR. The suppression factor for generic Kasner is O(1), insufficient to produce a physically meaningful concentration around low-Weyl initial data.**

---

## P06 — Constraint-Algebra Anomaly-Freedom

### What P06 actually does to Γ_GR

The Dirac physical Hilbert space is:

  H_phys = ker(Ĥ[N]) ∩ ker(Ĥ_i[N^i])

for all lapse functions N and shift vectors N^i. The anomaly-free condition requires additionally:

  [Ĥ[N], Ĥ[M]]|phys⟩ = iĤ_i[h^{ij}(N∂_jM − M∂_jN)]|phys⟩

without additional terms on the right-hand side.

In the semiclassical limit, states in H_phys correspond to geometries satisfying the classical constraint equations:

  H = (16πG)(π^{ij}π_{ij} − π²/2)/√h − √h R/16πG = 0
  H_i = −2∇_j π^j_i = 0

These are precisely the GR initial-data constraint equations. Every point in Γ_GR satisfies them. Therefore H_phys, in its semiclassical limit, corresponds to all of Γ_GR — not a restricted subset.

The anomaly-free condition adds a consistency requirement on the *quantum algebra*, but in the semiclassical limit, this condition is automatically satisfied because the classical Poisson bracket algebra is already consistent (the Dirac algebra closes without anomaly at the classical level).

### Outcome classification for P06

**Outcome: C — NO RESTRICTION**

1. **Semiclassical limit recovers all of Γ_GR.** Every classical geometry satisfying H = 0, H_i = 0 is a point in Γ_GR. The anomaly-free condition places no additional restriction on which classical geometries are included — it only requires that the quantization be consistent. This is a *meta-condition* on the theory, not a selection of initial data.

2. **Bianchi I has anomaly-free quantization.** Ashtekar-Wilson-Ewing (2009) explicitly constructed the anomaly-free LQC quantization of Bianchi I. This is a high-Weyl sector (Kasner has nonzero Weyl) that is not excluded.

3. **The kernel condition is too weak.** The kernel ker(Ĥ[N]) is infinite-dimensional in the full theory. Anomaly freedom narrows it from the kinematic Hilbert space to the physical Hilbert space — but the physical Hilbert space still contains an infinite-dimensional family of semiclassical geometries, including all of Γ_GR in the classical limit.

4. **No quantitative Weyl suppression is derived.** P06 produces no amplitude, no weight, no suppression factor for any class of initial data. It is a binary condition (consistent/inconsistent), not a continuous measure.

### Does P06 produce a weighting?

No. P06 is a hard algebraic condition. States are either in H_phys or not. There is no amplitude associated with being in H_phys beyond the standard Born rule for quantum states. No weighting of different classical initial data follows from the anomaly-free condition.

**P06 Phase-Space Verdict: OUTCOME C — NO RESTRICTION. The anomaly-free constraint algebra is satisfied by all classical GR solutions in the semiclassical limit. No weighting, suppression, or restriction of Γ_GR is derived. Bianchi I is explicitly in the physical Hilbert space.**

---

## Summary

| Candidate | Outcome | Weyl suppressed? | Restriction derived? | Measure? | Verdict |
|-----------|---------|-----------------|----------------------|---------|---------|
| P01 | B — Weighting only | Yes, factor ~exp(−β·O(1)) | No | Gaussian in perturbation theory only | CONDITIONAL — weighting insufficient |
| P06 | C — No restriction | No | No | None | KILLED for R1 purposes |

**P06 is functionally killed for R1.** It achieves Outcome C and provides no mechanism. It should not proceed further.

**P01 achieves Outcome B.** This is not sufficient for R1 but is not nothing. The question is whether B can be upgraded to A — and what mathematical result would achieve that. The weighting with β > 0 is real; the gap is that the suppression factor for Kasner is O(1), not exponentially small.

---

*Document status: UPGRADED — A/B/C classification applied*
*P01: Outcome B (weighting only). P06: Outcome C (no restriction).*
*Date: August 2026*
