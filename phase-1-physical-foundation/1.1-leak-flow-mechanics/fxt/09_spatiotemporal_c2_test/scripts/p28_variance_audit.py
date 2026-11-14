#!/usr/bin/env python3
"""
p28_variance_audit.py — Phase 9e
Audit the variance <|δJ|²> for independent experimental routes.
"""

import numpy as np
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT = os.path.join(BASE, "outputs", "data")

print("=" * 70)
print("p28_variance_audit.py — Variance Independent Test Audit")
print("=" * 70)

results = {}

# ─── Chain audit ───────────────────────────────────────────────────────────
print("""
VARIANCE DERIVATION CHAIN:

Step 1: δJ = s₀(ω_rot × r)
  Source: substrate_transport_derivation.md [ESTABLISHED-DJ]
  Basis: kinematic frame transformation J = s·v_sub, v_sub|_rotating = −ω_rot×r
  Status: DERIVED (pure kinematics — no physical assumption)

Step 2: <|δJ|²> = (2/3)s₀²ω_rot²r²
  Source: [ESTABLISHED-VAR]
  Basis: |ω_rot × r|² = ω_rot²r²sin²θ, then <sin²θ>_sphere = 2/3
  Status: DERIVED (angular average — no physical assumption)

Step 3: Γφ ∝ <|δJ|²>
  Source: CA-3 postulate
  Status: ASSUMED [CA-3] — NOT derived from transport equations
  This step requires quantum-classical coupling postulate.

Step 4: Γφ = k_rot · ω_rot²
  Status: DERIVED conditional on CA-3
""")

# ─── Independent test check ────────────────────────────────────────────────
print("─"*60)
print("Can the variance be tested independently of CA-3?")
print("─"*60)

print("""
  TEST A: Direct substrate flow measurement
    Observable: substrate current J at a point
    Prediction: J = s₀ · (ω_rot × r)  — tangential flow
    Depends on CA-3: NO
    Depends on g: NO
    Depends on s₀: YES (s₀ must be known)
    Practical: NOT accessible (substrate is not directly observable in QPU)

  TEST B: ω_rot² scaling of dephasing rate
    Observable: Γφ vs ω_rot measured on actual qubits
    C2 prediction: Γφ = k_rot · ω_rot²
    OU prediction: any Γ(ω_rot) is possible (no substrate constraint)
    Depends on CA-3: YES — step 3 of the chain
    Distinguishability: CONDITIONAL on CA-3

    This test exists (gamma_dataset on IBM): 7 data points
    Result: Γφ ∝ ω_rot² confirmed within measurement precision
    BUT: ω_rot² scaling is also consistent with:
      - Any super-Ohmic bath: S(ω) ∝ ω² → Γφ ∝ ω²
      - Any bath with variance ∝ ω_rot²
    C2-specific: NOT unique (other models reproduce ω² scaling)

  TEST C: k_rot = 8g²s₀²r_q²τ/(3ℏ²) — substrate parameter extraction
    This would extract individual (g, s₀, r_q, τ) from k_rot
    STATUS: NON-IDENTIFIABLE (Fisher matrix rank deficiency established in
    STRESS_TEST.md — eigenvalue = 0)
    g, s₀, r_q are not separately extractable from Γφ(ω_rot) data

  TEST D: Ratio test — Γφ(T₁)/Γφ(T₂) vs temperature
    C2 prediction: τ_B(T) = 1/(2γ(T)), so Γφ ∝ ω_rot²τ_B(T)
    IF γ has a known T-dependence: Γφ(T) is predicted
    This is CONDITIONALLY C2-specific if γ(T) is independently derived
    STATUS: γ(T) not currently derived in C2 theory

CONCLUSION ON VARIANCE:
  The variance formula itself (Steps 1-2) is DERIVED without CA-3.
  It predicts substrate flow kinematics, not qubit decoherence.
  The connection to qubit observables REQUIRES CA-3 (Step 3).
  The ω_rot² scaling of Γφ is NOT uniquely C2 (other bath models reproduce it).
  No independent test route exists that is both C2-specific AND avoids CA-3.
""")

results["variance_chain"] = {
    "step1_dJ": "DERIVED (kinematic frame transform)",
    "step2_variance": "DERIVED (isotropic angular average)",
    "step3_ca3": "ASSUMED (CA-3 postulate)",
    "step4_gamma": "DERIVED conditional on CA-3",
    "independent_test_without_ca3": False,
    "omega_rot_squared_c2_specific": False,
    "k_rot_identifiable": False,
    "T_dependence_c2_specific": "CONDITIONAL — gamma(T) not derived"
}

# ─── Check if variance gives independent c constraint ─────────────────────
print("─"*60)
print("Does the variance constrain c independently?")
print("─"*60)

print("""
  The variance <|δJ|²> = (2/3)s₀²ω_rot²r²

  Contains: s₀ [info/m³], ω_rot [rad/s], r [m]
  Does NOT contain: c, v, λ, τ_B, ξ_c

  The PRW speed c = v enters through:
    s₀ = background density (independent of c)
    ω_rot = externally controlled (independent of c)
    r = qubit geometry (independent of c)

  Therefore: The variance formula has NO dependence on c.
  The variance does NOT constrain c.

  The ONLY connection between the variance and c is through CA-3:
    Γφ ∝ <|δJ|²> ∝ ω_rot²  (via CA-3)
    τ_B = 1/(2λ) = 1/(2γ)   (from PRW)
    ξ_c = 2c·τ_B             (from spatial correlator)

  These connect through separate derivation chains, not through the variance.
""")

results["variance_c_constraint"] = {
    "variance_constrains_c": False,
    "reason": "Variance formula contains s0, omega_rot, r — not c, lambda, tau_B"
}

# ─── Search for other C2-specific predictions ─────────────────────────────
print("─"*60)
print("Other potential C2-specific predictions")
print("─"*60)

predictions = {
    "Gamma_phi ∝ omega_rot²": {
        "c2_prediction": True,
        "c2_specific": False,
        "reason": "Reproduced by any ω² bath (super-Ohmic, rotational coupling)"
    },
    "Non-Markovian Ramsey shape (EXACT-PHI)": {
        "c2_prediction": True,
        "c2_specific": False,
        "reason": "Identical to OU colored noise (proven degenerate)"
    },
    "Spatial K0 correlation": {
        "c2_prediction": True,
        "c2_specific": "CONDITIONALLY",
        "reason": "Distinguishable from exponential OU only when xi_c ~ chip size"
    },
    "xi_c = 2c*tau_B (joint constraint)": {
        "c2_prediction": True,
        "c2_specific": "CONDITIONALLY",
        "reason": "C2-specific if c is independently predicted; now c=v_s is derived"
    },
    "c = v_s = a√(K/m) (substrate acoustic speed)": {
        "c2_prediction": True,
        "c2_specific": "YES",
        "reason": "c is derived from FPUT — OU has no such constraint on spatial correlation speed"
    },
    "T-dependence: xi_c(T)/tau_B(T) = const = 2v_s": {
        "c2_prediction": True,
        "c2_specific": "CONDITIONALLY",
        "reason": "C2 predicts ratio is T-independent; OU does not. Requires T-variable platform."
    },
    "D = c²τ_B (diffusivity-speed-time relation)": {
        "c2_prediction": True,
        "c2_specific": "CONDITIONALLY",
        "reason": "Connects c, τ_B, D. Testable if D measured independently."
    }
}

print(f"\n  {'Prediction':45s}  {'C2-specific?':15s}  Reason")
for pred, info in predictions.items():
    print(f"  {pred[:43]:45s}  {str(info['c2_specific']):15s}  {info['reason'][:60]}")

results["predictions"] = predictions

with open(os.path.join(DOUT, "variance_test_audit.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {DOUT}/variance_test_audit.json")
print("p28 COMPLETE")
print("=" * 70)
