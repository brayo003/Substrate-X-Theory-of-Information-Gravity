#!/usr/bin/env python3
"""
p29_variance_coupling_audit.py — Phase 9e
Audit the variance chain and CA-3; determine if variance constrains c.
"""
import json, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT = os.path.join(BASE, "outputs", "data")

print("=" * 70)
print("p29_variance_coupling_audit.py — Variance/CA-3 Audit")
print("=" * 70)

results = {}

print("""
VARIANCE DERIVATION CHAIN
─────────────────────────
Step 1: δJ = s₀(ω_rot × r)
  Source: substrate_transport_derivation.md [ESTABLISHED-DJ]
  Derivation: J = s·v_sub; rotating frame gives v_sub|rot = −ω_rot×r
  Status: DERIVED  [pure kinematic identity]
  Contains c? NO

Step 2: <|δJ|²> = (2/3)s₀²ω_rot²r²
  Source: [ESTABLISHED-VAR]
  Derivation: |ω_rot×r|² = ω_rot²r²sin²θ; <sin²θ>_sphere = 2/3
  Status: DERIVED  [isotropic angular average]
  Contains c? NO

Step 3: Γφ ∝ <|δJ|²>
  Source: CA-3 postulate
  Status: ASSUMED [CA-3] — explicitly labeled constitutive postulate
  Contains c? NO (proportionality constant k_rot absorbs all parameters)

Step 4: Γφ = k_rot·ω_rot²
  Status: DERIVED conditional on CA-3
  k_rot = 8g²s₀²r_q²τ/(3ℏ²)  — contains τ_B but not c directly

DOES THE VARIANCE CHAIN CONTAIN c?

  Neither δJ nor <|δJ|²> contain v, λ, c, τ_B, ξ_c, or any propagation parameter.
  The variance parameters are: s₀ [info/m³], ω_rot [rad/s], r [m].
  These are substrate density, rotation rate, and coupling radius.

  k_rot contains τ_B = 1/(2λ) — but only as a timescale, not combined with c.
  The spatial correlation length ξ_c = 2cτ_B requires c independently.

  CONCLUSION: The variance chain provides NO constraint on c.

CA-3 HIDDEN DEPENDENCE CHECK:

  CA-3: Γφ ∝ <(δJ)²>
  This says decoherence is proportional to current fluctuation variance.
  The constant of proportionality k_rot = 8g²s₀²r_q²τ/(3ℏ²) contains:
    g (free parameter)
    s₀ (free parameter)
    r_q (free parameter)
    τ = τ_B (derived as 1/(2λ))
  
  None of these are c or v_s.
  CA-3 has NO hidden dependence on c.

INDEPENDENT TEST ROUTES FROM VARIANCE:

  A. ω_rot² scaling [DONE, confirmed, NOT C2-specific]
     Any bath with <J²> ∝ ω_rot² produces this.
  
  B. Lorentzian frequency dependence [NOT yet tested]
     Γφ(ω_rot) = k_rot·ω_rot² / (1 + ω_rot²τ_B²) at high ω_rot
     This Lorentzian rolloff is C2-consistent but also OU-consistent.
  
  C. Decoherence anisotropy (qubit orientation vs rotation axis)
     δJ = s₀(ω_rot × r) is a vector — coupling to specific J component
     would give orientation-dependent Γφ.
     Status: CONJECTURE — not yet derived in project.
     If derived, potentially C2-specific via geometric structure.
""")

results["variance_chain"] = {
    "step1_derived": True, "step1_contains_c": False,
    "step2_derived": True, "step2_contains_c": False,
    "step3_assumed_CA3": True, "step3_contains_c": False,
    "step4_derived_conditional": True,
    "k_rot_contains_c": False,
    "CA3_hidden_dependence_on_c": False,
    "variance_constrains_c": False,
    "independent_test_without_CA3": False,
    "anisotropy_route": "CONJECTURE — not derived"
}

print("""
FINAL VERDICT ON VARIANCE:
  <|δJ|²> = (2/3)s₀²ω_rot²r²  — DERIVED, no CA-3 needed, no c dependence
  Γφ ∝ <|δJ|²>                  — ASSUMED [CA-3], constitutive postulate
  CA-3 has no hidden c dependence
  Variance provides NO independent constraint on c
  ω_rot² scaling confirmed but NOT C2-specific
""")

with open(os.path.join(DOUT, "variance_coupling_audit.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved: {DOUT}/variance_coupling_audit.json")
print("p29 COMPLETE")
