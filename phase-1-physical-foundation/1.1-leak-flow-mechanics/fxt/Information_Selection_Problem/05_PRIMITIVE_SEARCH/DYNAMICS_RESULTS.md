# DYNAMICS_RESULTS
## Gate 5 Part VIII — Dynamics (Upgraded)

**Candidates:** P01 (Asymptotic Safety), P06 (Anomaly-Freedom)
**Date:** August 2026

The central question for P01: Does β > 0 imply suppression of Weyl-dominated *initial data*, or only suppression of a term in the effective action?

The central question for P06: Does anomaly-free constraint closure imply anything beyond consistency?

---

## P01 — Does β > 0 Restrict Initial Data or Just the Action?

### The distinction

There are two different claims:

**Claim A (weak):** The effective action Γ_0[g] contains a term +β∫C²√g d⁴x with β > 0. This term is larger for geometries with large Weyl curvature. Therefore, in the Euclidean path integral, geometries with large Weyl curvature have suppressed amplitude exp(−Γ_0[g]).

**Claim B (strong):** The set of classical initial data realizable via the AS-governed quantum gravity theory is restricted to configurations with small Weyl curvature.

Claim A is directly supported by β > 0 in truncated calculations. Claim B requires a further step: that the suppression in the path integral translates into a restriction on which classical initial-data configurations are produced.

### Does Claim A imply Claim B?

No, not directly. Here is why:

The path integral over all geometries suppresses high-C² configurations in the *sum*, but the dominant contributions are the *saddle points* of Γ_0. Every solution of δΓ_0/δg = 0 is a saddle point that contributes to the path integral. The question is: what are the saddle points of Γ_0 with β > 0?

**The modified equations of motion** (from δΓ_0/δg = 0):

  G_{μν} + Λg_{μν} − 4β B_{μν} + (α-terms) = 8πG T_{μν}

where B_{μν} = ∇^α∇^β C_{αμβν} + (1/2) R^{αβ} C_{αμβν} is the Bach tensor.

Kasner (Bianchi I vacuum, R_{μν} = 0, Λ = 0) satisfies these equations if B_{μν} = 0. The Bach tensor vanishes when the Weyl tensor is divergence-free: ∇^α C_{αμβν} = 0. For Kasner, the Weyl tensor is covariantly constant along the Kasner evolution: ∇^α C_{αμβν} = 0 is satisfied in the vacuum (since T_{μν} = 0 and G_{μν} = 0 together with the contracted Bianchi identity imply the Weyl tensor is divergence-free). Therefore Kasner satisfies B_{μν} = 0, and is a classical solution of the P01-modified equations even with β ≠ 0.

**This is decisive:** Kasner is a saddle point of Γ_0 for any β. It does not receive a classical (saddle-point) suppression from the β term. It receives only a quantum (off-saddle) suppression, which is the weighting described in Outcome B.

### Quantifying the quantum suppression

The saddle-point expansion around Kasner gives:

  Z[Kasner] ~ exp(−Γ_0[Kasner]) · det(δ²Γ_0/δg²)[Kasner]^{−1/2}

Γ_0[Kasner] = ∫(0 terms from G_{μν}=0, R=0, Λ=0) + β∫C²[Kasner]√g d⁴t d³x

For the Kasner metric with p₁ = 1, p₂ = p₃ = 0 (most anisotropic), and integrating over the Planck epoch t ∈ [t_Pl, t_f]:

  C²[Kasner] = 24(p₁p₂ + p₂p₃ + p₃p₁ − p₁² − p₂² − p₃²)²/(9t⁴) = 8/9t⁴

  ∫ C²√g dt d³x = ∫ (8/9t⁴) · t (a₁a₂a₃ dt d³x)

For Kasner with a_i = t^{p_i}, the volume element √g = t^{p₁+p₂+p₃} = t¹. So:

  ∫_V C²√g d⁴x ~ (8/9) ∫_{t_Pl}^{t_f} t^{-4} · t · l³ dt = (8/9) l³ ∫_{t_Pl}^{t_f} t^{-3} dt ~ (8/9) l³ · t_Pl^{-2}

In Planck units (l ~ t ~ 1 at the Planck epoch), this integral is O(1). Therefore:

  Γ_0[Kasner] ~ β · O(1) in Planck units

Compared to FLRW where Γ_0[FLRW] ~ 0 (since C = 0), the suppression of Kasner relative to FLRW is:

  Z[Kasner] / Z[FLRW] ~ exp(−β · O(1))

For β ~ 1 (which is the natural Planck-scale value), this ratio is ~ e⁻¹ ≈ 0.37.

**This is an O(1) suppression, not an exponential elimination.** Kasner is suppressed by a factor of ~3 relative to FLRW, not by a factor of 10^{100} or e^{-N} for large N. This is insufficient to explain why Kasner-type initial data was not realized.

### What would produce a true restriction?

For Claim B to hold, one of the following would be needed:

1. β >> 1 (β is parametrically large, making the suppression exp(−β·N) with large β·N). But β is fixed by the AS fixed point — it is O(1) in Planck units in current calculations. It is not a free parameter.

2. The integration region extends over many Planck volumes (N >> 1), so the total action β·N is large. But the relevant region is the Planck epoch, which is a single Planck volume per Hubble patch. N ~ O(1).

3. A non-perturbative mechanism that excludes Kasner saddle points entirely — for example, if Kasner has an imaginary part of the Euclidean action that causes destructive interference. No such mechanism is established.

4. A separate argument that the AS trajectory produces initial conditions that are not classical saddle points of the modified action — i.e., the AS mechanism produces a specific quantum state that is not well-described by any classical geometry. This is speculative but not ruled out.

**Dynamics verdict for P01:** β > 0 suppresses the path-integral weight of Kasner relative to FLRW by an O(1) factor. This is not a restriction (Outcome A) and is a weak weighting (Outcome B). The mechanism does not produce Claim B from Claim A by any established mathematical route.

---

## P06 — Does Anomaly-Free Closure Imply Anything Beyond Consistency?

### The question

Anomaly-free closure means: the quantum constraint algebra closes without a remainder term. In symbols:

  [Ĥ[N], Ĥ[M]]|phys⟩ = iĤ_i[q(N,M)]|phys⟩

where q(N,M) = h^{ij}(N∂_jM − M∂_jN).

What does this imply for the space of physical states H_phys?

### It implies consistency, not selection

The anomaly-free condition is a condition on the *quantization procedure*, not on the *states*. Given H_phys = ker(Ĥ) ∩ ker(Ĥ_i), the anomaly-free condition says that this kernel is invariant under the quantum constraint algebra. This is a property of the *operators*, not of the *states*.

In particular:
- H_phys is determined by which states are annihilated by Ĥ and Ĥ_i.
- Anomaly freedom says the algebra of these operators is consistent.
- But H_phys in the semiclassical limit corresponds to the classical constraint surface Γ_GR — all of it.

**There is no mechanism in anomaly freedom that selects a subset of Γ_GR.** The selection would have to come from the *size of the kernel* being smaller than expected — but the only way the kernel is smaller than all of Γ_GR is if some classical configurations do not lift to quantum states. This is the content of a possible Weyl exclusion theorem, which does not exist.

### The Bianchi I counter-example

Ashtekar-Wilson-Ewing (2009) explicitly constructed the physical Hilbert space for the Bianchi I model in LQC. Result: H_phys for Bianchi I is non-empty. The anomaly-free condition is satisfied. High-Weyl initial data (Kasner) has a quantum state in H_phys.

This is a decisive counter-example. It shows that anomaly-free quantization does not exclude Kasner initial data.

**Dynamics verdict for P06:** Anomaly-free closure implies mathematical consistency of the quantum theory. It does not imply selection of initial data. P06 produces no dynamical mechanism for restricting Γ_GR. The Bianchi I counter-example is established.

---

## New Parameters

**P01:** α, β — both fixed by the AS renormalized trajectory. Neither is a free parameter given the AS framework. Both have independent motivation (Stelle 1977 one-loop gravity). Ghost at M_ghost ~ M_Planck/√β — unresolved.

**P06:** No new parameters. The area gap Δ in LQC is the only new input, with independent motivation from LQG minimum area.

---

## Summary

| | P01 | P06 |
|--|-----|-----|
| Equations of motion modified? | Yes (Bach tensor term) | No change to classical EOMs |
| New saddle points introduced? | No — Kasner remains a saddle | N/A |
| Weyl suppression in path integral? | Yes, factor exp(−β·O(1)) | No |
| Sufficient to restrict Γ_GR? | No — O(1) suppression only | No |
| Ghost problem? | Yes (unresolved) | N/A |
| Decisive obstruction | Kasner is a saddle of the modified action | Bianchi I is in H_phys |

---

*Document status: DYNAMICS UPGRADED*
*P01: Weyl suppression real but O(1); insufficient. P06: No dynamical mechanism.*
*Date: August 2026*
