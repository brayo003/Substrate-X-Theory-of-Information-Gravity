# Document 34 — C2 Quantum Branch Status
## Phase 9e: Complete Theoretical and Experimental Status

**Date:** 2026-08-21  
**Hard verdict:** C_CONDITIONALLY_PREDICTED / FROZEN

---

## 1. The Twelve Questions

**Q1. Did we actually derive c?**  
Yes — conditionally. From `projection_classification_audit.md`, the P1 (RPA) governing equations use `vₛ` as the transport speed directly. The `±` split follows from the sign of the acoustic group velocity `∂ωₖ/∂k`. In the long-wavelength limit (k→0), the group velocity equals `vₛ = a√(K/m)`. Therefore:

```
c = v_PRW = vg(k→0) = a√(K/m) = vₛ   [DERIVED — conditional on k→0 limit]
```

The condition (k→0, ℓ_CG >> a) is the standard hydrodynamic coarse-graining already embedded in the P1 construction. It is not an additional postulate.

**Q2. Where does derivation stop?**  
At the physical identification of the PRW particles with acoustic phonons. The derivation says: n± are the right/left-moving acoustic phonon action densities, their speed is the group velocity, and in the long-wavelength limit group velocity = vₛ. This requires identifying the information quanta with acoustic phonons — a physical step, not a pure theorem.

**Q3. Is c = vₛ a theorem or an extra postulate?**  
It is a physically derived result embedded in the P1 construction — neither a pure theorem nor an arbitrary postulate. It falls between: the derivation is specific and follows from the FPUT normal mode structure, but the phonon identification is a physical assumption.

**Q4. Was c = 10⁴ m/s an invalid historical assumption?**  
YES. The value 10⁴ m/s has no derivation in the theory and violates C3 (exceeds vₛ(Si) = 6000 m/s). It was chosen for experimental convenience. It must be removed from future C2 predictions.

**Q5. Does C3 provide an upper bound or an equality?**  
C3 is defined as an inequality (c ≤ vₛ). The unique admissible P1 projection saturates it at equality. Since P1 is the only admissible projection (FPUT-3), c = vₛ in the C2 theory.

**Q6. Does the variance formula provide an independent test?**  
No fully independent route exists. Steps 1–2 of the variance chain are derived without quantum postulates, but connecting to qubit observables requires CA-3. The Γφ ∝ ω_rot² scaling is confirmed but not C2-specific. A potential anisotropy test (decoherence dependence on coupling axis orientation) is a conjecture requiring further derivation.

**Q7. Is there any currently known C2-specific observable?**  
Yes — one:

The **K₀ vs. exponential spatial correlation shape** at d ~ ξ_c.

With c = vₛ = 6000 m/s:
- At τ_B ~ 1–2 µs: ξ_c ~ 1.2–2.4 cm
- IBM Eagle (127-qubit, ~14mm chip) has d_max ~ 14mm
- d_max/ξ_c ~ 0.6–1.2 → **the shape test is in principle accessible**

The K₀ shape is uniquely predicted by C2 (2D PRW spatial correlator). OU with exponential spatial correlation predicts a different functional form. This is a genuine discriminator when d/ξ_c ~ 0.1–3.

**Q8. Is the C2 quantum layer merely underdetermined, or does the theory require revision?**  
Merely underdetermined at the experimental access level, not at the theoretical level. The c derivation was always present in the project files (projection_classification_audit.md P1 governing equations) — it was not fully traced in earlier audits. The theory does not require revision; it requires better experimental access.

**Q9. Is a QPU experiment currently scientifically justified?**  
Not with current resources (no IBM or equivalent access). But the theoretical basis for the experiment IS now justified:
- c = vₛ is derived (not a free parameter)
- ξ_c is therefore predicted for each τ_B
- The K₀ vs. exp shape test is genuinely discriminating at d ~ ξ_c
- τ_B ~ 1 µs on an Eagle-class chip would make the test accessible

**Q10. What exact theoretical result would justify reopening the QPU branch?**  
Two conditions, both now partially satisfied:
1. ✓ c is independently predicted (c = vₛ = a√(K/m) from FPUT)
2. ✗ Access to a QPU where d_max ~ ξ_c (requires Eagle-class chip with τ_B ~ 1 µs)

The experiment branch is reopenable in principle. It remains frozen due to lack of hardware access.

**Q11. Was the C2/OU degeneracy resolved?**  
Not in the temporal domain. C2 and OU remain identical for all temporal/spectral observables. The degeneracy is resolved ONLY in the spatial domain via the K₀ vs. exp shape — and only when d/ξ_c ~ 1.

**Q12. Does the variance formula provide a route independent of c?**  
No. The variance formula does not contain c. The connection to testable predictions (decoherence anisotropy) requires a more detailed coupling geometry derivation not yet in the project.

---

## 2. Complete Status Table

| Quantity | Current status | Why |
|----------|----------------|-----|
| τ_B | MEASURABLE (NM regime, NMP~1) | Ramsey trace shape, bias <7% |
| d_c (spatial) | NOT MEASURABLE (current chips) | ξ_c >> chip for τ_B > 1 µs |
| c | CONDITIONALLY DERIVED | c = vₛ = a√(K/m) from FPUT P1 |
| v_PRW | = c = vₛ | Long-wavelength group velocity of FPUT acoustic branch |
| v_s = a√(K/m) | DERIVED from FPUT | Si: 6000 m/s |
| ξ_c | PREDICTED given τ_B | ξ_c = 2vₛ·τ_B; for τ_B=5µs: 6 cm |
| variance <\|δJ\|²> | DERIVED (Steps 1–2) | Kinematic, no CA-3 needed |
| Γφ coupling | ASSUMED [CA-3] | Not derivable from transport equations |
| C2 vs OU (temporal) | DEGENERATE | C2 coherence ≡ OU coherence (all orders) |
| C2 vs OU (spatial) | DISCRIMINATING at d~ξ_c | K₀ vs exp shape when d/ξ_c ~ 1 |
| C2-specific observable | K₀ shape at d~ξ_c | Unique 2D spatial correlator |
| QPU justification | NOT CURRENTLY | Access to Eagle-class chip needed with τ_B~1µs |

---

## 3. The Decisive Experiment (Theory Now Supports It)

With c = vₛ now derived, the decisive experiment is:

**Measure the spatial correlation C_Γ(r) across a 127-qubit chip, fit K₀(r/ξ_c) vs exp(−r/ξ_c), and compare.**

Prediction:
- C2 (2D): `C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)` with `ξ_c = 2vₛτ_B`
- OU: `C_Γ(r) = exp(−r/ξ_c)` with ξ_c as a free parameter

At τ_B = 1 µs on a 14mm chip: ξ_c = 1.2 cm, d_max/ξ_c = 1.2 → shape discrimination AUC ~ 1.0.

**Requirements:**
1. IBM Eagle (127-qubit) or equivalent access
2. τ_B ~ 1 µs (fast bath, NMP ~ 0.4 — identifiable but less optimal than NMP~1)
3. Simultaneous Ramsey traces on all qubits (for τ_B extraction)
4. Spatial correlation measurement (correlated Ramsey residuals across qubit pairs)

**Condition to reopen:** IBM credentials or equivalent cloud QPU with >50 qubits and full topology access.

---

## 4. Hard Verdict

```
C2 QUANTUM LAYER STATUS:

Theoretical:  C_CONDITIONALLY_PREDICTED
              c = v_s = a√(K/m) derived from FPUT P1 projection
              ξ_c = 2v_s·τ_B predicted once τ_B measured

Experimental: FROZEN — NOT FALSIFIED — NOT CONFIRMED
              No QPU access to execute the decisive test
              Decisive test: K₀ vs exp shape on Eagle-class chip

Change from previous status:
  31_C_DERIVATION_AUDIT: C_PARAMETER_DEPENDENT
  32_C_FIRST_PRINCIPLES_DERIVATION: C_CONDITIONALLY_PREDICTED  ← UPGRADED
  Experimental verdict: unchanged (FROZEN)

Condition to change experimental verdict:
  IBM Eagle or equivalent access + τ_B measurement confirming ~1 µs
  on the same chip as the spatial correlation measurement
```

---

## 5. What Would Each Outcome Mean

**If K₀ preferred over exp (ΔBIC > 6 on >50% of pairs):**  
C2 SPATIALLY SUPPORTED — first evidence specific to C2 substrate model.

**If exp preferred over K₀:**  
C2 SPATIAL PREDICTION DISFAVORED — does not falsify C2 entirely (could be 3D or 1D regime, or τ_B mismatch), but damages the 2D prediction.

**If both models fit equally (|ΔBIC| < 2):**  
COMPATIBLE / UNDERDETERMINED — insufficient spatial resolution.

**If τ_B measurement fails (parameter at bound):**  
TECHNICALLY INCONCLUSIVE — experiment not interpretable.

**If neither K₀ nor exp is preferred, but spatial correlations are clearly non-flat:**  
NEW OBSERVABLE — investigate the actual shape; may indicate different effective dimension.
