# GAP7_TLS_CLOSURE.md
## Can c Be Derived from TLS Parameters? Is c << v_s Physically Possible?

**Date:** 2026-08-22
**Depends on:** TLS_SUBSTRATE_DERIVATION.md, TLS_PERSISTENCE_AUDIT.md
**Label:** DERIVED | ASSUMED | FREE | FAILED | CONVENTIONAL

---

## 1. Summary of Inputs

From TLS_SUBSTRATE_DERIVATION.md:
- c_hop = d_TLS × γ_hop ≈ 2×10⁻⁵ m/s (from known TLS parameters)
- For PRW to hold, a persistence reversal rate γ_rev must exist
- γ_rev is a NEW FREE PARAMETER — not in standard TLS physics

From TLS_PERSISTENCE_AUDIT.md:
- Standard TLS hopping is purely diffusive (simple random walk)
- No physical mechanism generates directional persistence in amorphous TLS
- Verdict: FAILS physically

---

## 2. GAP-7 Test for the TLS Substrate

GAP-7 asks: can c be derived from independently known parameters without
fitting c to experimental data?

**Under the PRW assumption (persistence hypothesis):**

```
c_PRW = c_hop = d_TLS × γ_hop
```

where:
- d_TLS ~ 1–3 nm (INDEPENDENTLY MEASURABLE from TLS density)
- γ_hop ~ V_ij²/Γ₂ (DERIVED from dipole coupling and dephasing rate)

Numerical estimate:
```
V_ij ~ p²/(4πε₀ ε_r d³) ~ 0.1 MHz  (for d=2nm, p=1e-30 C·m, ε_r=4)
Γ₂ ~ 1 MHz  (typical TLS dephasing)
γ_hop ~ (0.1MHz)²/(1MHz) = 0.01 MHz = 10⁴ s⁻¹
c_hop = 2×10⁻⁹ m × 10⁴ s⁻¹ = 2×10⁻⁵ m/s
```

This is ≪ v_s = 6000 m/s by a factor of ~3×10⁸. The speed IS anomalously slow.

**BUT:** The full PRW propagation speed is:
```
c_PRW = c_hop = d × γ_hop   (this is the hop speed, also the PRW speed in the telegrapher)
τ_B = 1/(2γ_rev)            (persistence time — FREE parameter)
ξ_c = c_PRW / γ_rev = d × γ_hop / γ_rev
```

The propagation speed c_PRW = c_hop is determinable from TLS parameters.
**BUT: τ_B and ξ_c both require γ_rev, which is FREE.**

---

## 3. Is c Genuinely Derivable Without Fitting?

**c_hop = d_TLS × γ_hop:**

- d_TLS: INDEPENDENTLY MEASURABLE (from TLS areal density n_TLS ~ 10¹⁵–10¹⁶ m⁻², d = n^{-1/2})
- γ_hop: DERIVED from V_ij and Γ₂, both of which are independently measurable

**Conclusion on c:** YES — c_hop can be derived from independently measurable TLS parameters WITHOUT fitting to decoherence data.

**Numerical range from literature parameters:**

| TLS density | d_TLS | γ_hop | c_hop |
|------------|-------|-------|-------|
| 10¹⁵ m⁻² (low) | 3.2 nm | 10³ s⁻¹ | 3×10⁻⁶ m/s |
| 10¹⁶ m⁻² (high) | 1.0 nm | 10⁵ s⁻¹ | 10⁻⁴ m/s |

Range: c_hop ~ 10⁻⁶ to 10⁻⁴ m/s — spanning 2 orders of magnitude, but ALL values are c ≪ v_s.

**This is a genuine forward prediction of the ORDER OF MAGNITUDE of c, derivable from TLS parameters, without fitting to decoherence data.**

However, this prediction carries a critical caveat: it only holds if the PRW/persistence assumption is valid. Since TLS_PERSISTENCE_AUDIT.md established that persistence FAILS in standard TLS, this prediction is moot.

---

## 4. C5 Closure Test for TLS PRW

From TLS_SUBSTRATE_DERIVATION.md: the coarse-grained TLS transport gives DIFFUSION, not telegrapher, under standard physics.

**Does C5 closure help or hurt?**

C5 requires n±(x) to be approximately closed under the dynamics. For TLS diffusion:

```
∂n/∂t = D ∇²n    (diffusion)
```

The diffusion equation does NOT factorize into right- and left-moving components n±. There is no C5-compliant PRW structure from standard TLS.

If we hypothetically impose persistence (γ_rev as a free parameter), C5 would be satisfied because the PRW balance equations are closed by construction. But this is circular: C5 is satisfied only by assuming the PRW structure, not by deriving it from TLS physics.

**For the acoustic FPUT case:** C5 forced c = v_s because the acoustic modes naturally factorize into n± (right/left phonons), and C5 closure held at exactly c = v_s.

**For TLS:** The diffusion equation has NO natural n± factorization. C5 is not satisfied by standard TLS diffusion. To force C5 closure at c = c_hop ≪ v_s, one must POSTULATE the PRW structure — which is exactly what TLS_PERSISTENCE_AUDIT.md showed has no physical basis.

**C5 Status for TLS:** FAILS for standard TLS diffusion. Cannot be rescued without the persistence assumption, which itself FAILS.

---

## 5. Could c ≪ v_s Be Real Even If TLS Fails?

**Direct question:** Is c ≪ v_s physically achievable under ANY substrate satisfying C5?

The FPUT analysis (Extension A) showed: for the harmonic FPUT chain, C5 forces c = v_s. Can a non-FPUT lattice give C5 with c ≪ v_s?

**General argument against c ≪ v_s with C5:**

C5 closure requires the n±(x) fields to evolve at speed c without leaking into other modes. If the physical substrate has modes at ALL speeds from 0 to v_s (as any solid does via its phonon spectrum), then defining n± at speed c ≪ v_s would mean:

- Modes with speed > c would NOT be captured by n±
- These fast modes would leak into the field description
- C5 would be violated

This is the same argument that killed c < v_s in the FPUT analysis: any speed c < v_s is incompatible with C5 in a real physical medium that has acoustic modes at v_s.

**The only way to avoid this is:** A substrate that has NO modes at speeds between c and v_s. Such a substrate would need a gap in its dispersion relation — modes at c ≪ v_s but NO modes at intermediate speeds.

Do any physical systems have such a gap? In principle: a system with a "slow mode" (e.g., a heavy impurity band) separated from the acoustic band by a gap. This would require specific engineered material, not standard amorphous SiO₂.

**Status:** c ≪ v_s with C5 is POSSIBLE in principle in specially engineered materials with a spectral gap. Not achievable in standard chip materials.

---

## 6. Final Answer to GAP-7 for TLS

| Question | Answer |
|----------|--------|
| Is c derivable from TLS parameters? | YES — c_hop = d × γ_hop is derivable |
| Is c ≪ v_s for these parameters? | YES — c_hop ~ 10⁻⁵ m/s ≪ 6000 m/s |
| Is the PRW/telegrapher valid for TLS? | NO — standard TLS gives diffusion |
| Does C5 closure hold for TLS? | NO — diffusion has no n± factorization |
| Is c_hop the same as c_PRW? | Only if persistence exists (it doesn't) |
| Is GAP-7 resolved by TLS? | NO — persistence assumption introduces γ_rev as free |

**GAP-7 is NOT resolved by the TLS route.** c_hop can be computed from TLS parameters, but c_hop is the diffusive hop speed, not the PRW propagation speed. The PRW structure requires persistence, which fails, and introduces γ_rev as a free parameter.

**The TLS route produces an anomalously small speed (c_hop ≪ v_s) but cannot make that speed the PRW propagation velocity because the PRW structure itself does not arise from TLS physics.**
