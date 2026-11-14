# Document 33 — Variance Independent Test Audit
## Phase 9e: Can <|δJ|²> Provide an Independent Test Route?

**Date:** 2026-08-21  
**Script:** `scripts/p28_variance_audit.py`

---

## 1. Three-Step Chain

```
Step 1: δJ = s₀(ω_rot × r)                  DERIVED — kinematic frame transform
Step 2: <|δJ|²> = (2/3)s₀²ω_rot²r²          DERIVED — isotropic angular average
Step 3: Γφ ∝ <|δJ|²>                         ASSUMED [CA-3] — not derivable
Step 4: Γφ = k_rot · ω_rot²                  DERIVED conditional on CA-3
```

Steps 1–2 are fully derived without quantum postulates. Step 3 (CA-3) is where the chain becomes an assumption. This distinction must not be collapsed.

---

## 2. Does the Variance Constrain c?

No. The variance `<|δJ|²> = (2/3)s₀²ω_rot²r²` contains only s₀, ω_rot, r.
It has no dependence on c, λ, τ_B, or ξ_c. The variance and the propagation speed live in independent parts of the theory.

---

## 3. Independent Test Routes

| Test | Observable | C2-specific? | CA-3 required? | Accessible? |
|------|-----------|-------------|----------------|-------------|
| Γφ ∝ ω_rot² | Ramsey at varied ω_rot | NO — shared with any ω² bath | YES | YES (done) |
| k_rot vs. substrate prediction | Compare fitted k_rot to 8g²s₀²r_q²τ/3ℏ² | NO — 4 non-identifiable params | YES | NO |
| Γφ(T) vs. temperature | Ramsey at varied T | CONDITIONAL — needs γ(T) derived | YES | NO (fixed T) |
| Decoherence anisotropy vs. qubit orientation | Varied angle between r and ω_rot | POTENTIALLY YES | YES | NOT DEMONSTRATED |
| Direct substrate flow | Measure J(x,t) directly | YES — but substrate unobservable | NO | NO |

---

## 4. The Anisotropy Route (New Candidate)

The δJ = s₀(ω_rot × r) prediction is a vector, not a scalar. If the qubit couples to a specific component of J (e.g., the component along ẑ), the decoherence rate would depend on the angle between ω_rot and the qubit's coupling axis:

```
Γφ ∝ |ω_rot × r|² · sin²(θ)   where θ = angle between ẑ and (ω_rot × r)
```

For isotropic baths: Γφ is independent of orientation.  
For C2: Γφ has geometric dependence on coupling axis orientation.

This is POTENTIALLY C2-specific and does not require spatial correlation measurements.

**Status:** Conjecture — requires a more detailed derivation of the coupling geometry. Not yet in the project. If derived, this could provide an independent test route distinct from both the spatial correlator and the temporal shape.

---

## 5. Conclusion

The variance derivation (Steps 1–2) is solid and requires no new assumptions. The connection to qubit observables requires CA-3. No independent test route from the variance is currently established. The anisotropy route is a potential new direction but remains a conjecture.
