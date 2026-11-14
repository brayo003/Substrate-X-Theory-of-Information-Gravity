#!/usr/bin/env python3
"""
p27_c_prw_speed_audit.py — Phase 9e
Audit: Does FPUT-3 derive c = v_s, or is v_s embedded by construction?

Key findings from source inspection:
- FPUT-3 (C2_FOUNDATIONS.md): proves telegrapher equation is the evolution,
  but does NOT state what c equals in that equation.
- P1 governing equations (projection_classification_audit.md P1(a)):
  write v_s directly, but P1 is DEFINED with n± as "right/left-moving
  phonon density" — v_s is embedded in the definition, not derived.
- nk are exact constants of motion (nk_dot = 0) — the transport of the
  action density n±(x,t) is a SEPARATE construction, not derived from nk=const.
- The Main Theorem (IV.3) step 3 says signal speed "≤ vₛ" — inequality only.
"""

import numpy as np
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT = os.path.join(BASE, "outputs", "data")
os.makedirs(DOUT, exist_ok=True)

print("=" * 70)
print("p27_c_prw_speed_audit.py — PRW Speed Derivation Audit")
print("=" * 70)

results = {}

# ─── PART 1: What FPUT-3 actually states ──────────────────────────────────
print("\nPART 1: FPUT-3 exact statement")
print("─" * 60)
print("""
Source: C2_FOUNDATIONS.md, Theorem FPUT-3:
  "The only admissible projection satisfying C1–C6 that retains only the
   action variables nₖ is the coarse-grained density
   s(x,t) = (1/N) Σₖ nₖ e^{ikx},
   whose evolution is the telegrapher equation."

What FPUT-3 proves:
  ✓ The projection type is PRW / telegrapher
  ✓ The projected variable is s(x,t) = (1/N)Σₖ nₖ e^{ikx}
  ✗ Does NOT state what c equals in τ∂²s/∂t² + ∂s/∂t = c²τ∇²s
  ✗ Does NOT prove c = v_s
  ✗ Does NOT prove c ≤ v_s (that comes from C3, separately)

FPUT-3 classification for c:  UNRESOLVED
""")

# ─── PART 2: P1 governing equations — construction vs derivation ──────────
print("PART 2: P1 governing equations — are they derived or constructed?")
print("─" * 60)
print("""
Source: projection_classification_audit.md, P1 Section

P1 DEFINITION (verbatim):
  n⁺(x) = Σₖ nₖ w⁺ₖ(x)  "right-moving phonon density at x"
  n⁻(x) = Σₖ nₖ w⁻ₖ(x)  "left-moving phonon density at x"

P1 GOVERNING EQUATIONS (verbatim):
  ∂ₜn⁺ + vₛ ∂ₓn⁺ = −γ(n⁺ − n⁻)
  ∂ₜn⁻ − vₛ ∂ₓn⁻ = +γ(n⁺ − n⁻)

CRITICAL QUESTION:
  Are these equations DERIVED from nₖ dynamics, or STATED as the
  transport model consistent with the phonon interpretation?

FINDING:
  nₖ = |Aₖ(t)|² = |Aₖ(0)|² = const exactly (harmonic chain conserves nₖ).
  The equation ṅₖ = 0 describes individual mode actions.
  The P1 transport equations describe the SPATIAL flow of action density.
  These are two different levels of description.

  The P1 governing equations are NOT derived within the audit file from
  the microscopic nₖ dynamics. They are CONSTRUCTED as the natural
  phonon-gas transport equations for right/left-moving densities.

  The appearance of vₛ in those equations reflects the DEFINITION of
  n± as acoustic phonon densities whose group velocity is vₛ.

  This is a MODEL CONSTRUCTION, not a mathematical derivation from FPUT.

STATUS:
  v_s in P1 governing equations: DEFINITIONAL (embedded in the construction
  of n± as phonon density with speed = group velocity)
  
  The governing equations are consistent with FPUT but not derived from it
  within the existing project files.
""")

results["fput3_status"] = {
    "proves_telegrapher_type": True,
    "proves_c_equals_v_s": False,
    "proves_c_leq_v_s": False,
    "c_status_in_fput3": "UNRESOLVED — FPUT-3 does not specify c",
    "P1_governing_eqs_status": "DEFINITIONAL — v_s embedded by phonon construction",
    "derivation_of_transport_from_nk": "NOT FOUND in project files"
}

# ─── PART 3: C3 audit — bound or equality? ────────────────────────────────
print("PART 3: C3 — bound or equality?")
print("─" * 60)
print("""
Source: projection_classification_audit.md, C3 definition (line 84):
  "finite signal speed v_signal ≤ vₛ"  ← INEQUALITY

Source: P1 constraint table, C3 row:
  "Signal speed = vₛ (sound speed)"  ← EQUALITY stated for P1

Source: Main Theorem IV.3, step 3:
  "the evolution of n±(x) must be a PDE with signal speed ≤ vₛ"  ← INEQUALITY

ANALYSIS:
  C3 as CONSTRAINT:   c ≤ v_s   (inequality — upper bound only)
  P1 as CONSTRUCTION: c = v_s   (equality — because n± defined with v_s)

  The equality in P1 is NOT a consequence of C3.
  P1 SATISFIES C3 (because v_s ≤ v_s trivially).
  P1 is constructed with c = v_s as a design choice, then verified to pass C3.

  The question is: does C3 + FPUT-3 FORCE c = v_s, or merely allow it?

  The proof (Main Theorem IV.3, step 3) says "minimal such system consistent
  with microscopic dynamics is the PRW telegrapher equation."
  "Minimal" means: the simplest model with speed ≤ v_s that matches the
  phonon structure. The minimal choice is c = v_s (using maximum speed).
  But "minimal" is an informal argument, not a proof of necessity.

C3 VERDICT:
  C3 establishes:   c ≤ v_s   [DERIVED from C3 + FPUT acoustics]
  c = v_s:          NOT proved — requires additional identification
  Status:           CONDITIONALLY DERIVED (requires phonon identification assumption)
""")

results["C3_status"] = {
    "C3_type": "inequality: c <= v_s",
    "P1_uses_equality": True,
    "equality_derived": False,
    "equality_status": "CONDITIONALLY DERIVED — requires phonon identification as explicit assumption",
    "minimal_argument": "informal, not a proof"
}

# ─── PART 4: Complete derivation chain with honest labels ─────────────────
print("PART 4: Complete derivation chain")
print("─" * 60)

chain = [
    ("FPUT Hamiltonian",                       "ASSUMED",            "substrate model [A-FPUT1]"),
    ("ωₖ = 2√(K/m)|sin(πk/N)|",               "DERIVED",            "Fourier diagonalization"),
    ("v_s = a√(K/m) = (∂ωₖ/∂k)|_{k→0}",       "DERIVED",            "long-wavelength limit of ωₖ"),
    ("Actions nₖ = const",                      "DERIVED",            "harmonic chain integrability"),
    ("C3: signal speed ≤ v_s",                  "DERIVED",            "C3 admissibility + FPUT acoustics"),
    ("FPUT-3: evolution is telegrapher",         "DERIVED",            "C1 locality eliminates all other projections"),
    ("FPUT-3: c = ? in telegrapher",             "UNRESOLVED",         "FPUT-3 does not specify c"),
    ("n± defined as phonon densities at v_s",    "ASSUMED/DEFINITIONAL","phonon identification — not derived"),
    ("P1 governing eqs use v_s",                 "DEFINITIONAL",       "follows from n± phonon definition"),
    ("c = v_s in C2 PRW",                        "CONDITIONALLY DERIVED","IF phonon identification accepted"),
    ("τ_B = 1/(2γ)",                             "DERIVED",            "PRW relaxation"),
    ("ξ_c = 2c·τ_B",                             "DERIVED",            "given c"),
]

print(f"\n  {'Step':48s}  {'Label':25s}")
print("  " + "─"*75)
for step, label, source in chain:
    print(f"  {step[:46]:48s}  {label:25s}  [{source[:40]}]")

print("""
KEY GAP: Between "FPUT-3: telegrapher" and "c = v_s" there is
         a missing derivation. The P1 construction fills this gap
         by defining n± as phonon densities, but this definition
         is an IDENTIFICATION (physical assumption), not a theorem.
""")

results["derivation_chain"] = {
    "gap_location": "FPUT-3 → c = v_s",
    "gap_type": "Missing derivation of PRW speed from FPUT parameters",
    "gap_filled_by": "P1 phonon identification (ASSUMPTION, not theorem)",
    "final_c_status": "CONDITIONALLY DERIVED — requires explicit phonon identification assumption"
}

# ─── PART 5: Numerical audit ──────────────────────────────────────────────
print("PART 5: Numerical consequences")
print("─" * 60)

# Si substrate
m_Si  = 4.665e-26   # kg
K_Si  = 5.696e0     # N/m
a_Si  = 0.543e-9    # m
v_s   = a_Si * np.sqrt(K_Si / m_Si)

print(f"\n  v_s(Si) = a√(K/m) = {v_s:.0f} m/s  [DERIVED from FPUT acoustics]")
print(f"  c range: (0, {v_s:.0f}] m/s  [DERIVED from C3]")
print(f"  c = {v_s:.0f} m/s  [CONDITIONALLY DERIVED — phonon identification]")
print(f"  c = 10^4 m/s  [INVALID — exceeds v_s, no derivation]")

print(f"\n  ξ_c = 2c·τ_B for c = v_s = {v_s:.0f} m/s:")
print(f"  {'τ_B':12s}  {'ξ_c':15s}  {'d/ξ_c (7q 632µm)':20s}  {'d/ξ_c (Eagle 14mm)':20s}")
print("  " + "─"*70)

targets = {
    "632 µm": 632e-6, "1 mm": 1e-3, "10 mm": 10e-3, "14 mm": 14e-3, "1 cm": 10e-3
}
tau_vals = [0.05e-6, 0.1e-6, 0.5e-6, 1e-6, 1.2e-6, 5e-6, 10e-6, 50e-6]
xi_c_results = {}
for tau_b in tau_vals:
    xi_c = 2 * v_s * tau_b
    r7 = 632e-6 / xi_c
    re = 14e-3 / xi_c
    print(f"  {tau_b*1e6:8.2f} µs    {xi_c*100:12.4f} cm    {r7:18.4f}    {re:18.4f}")
    xi_c_results[f"{tau_b*1e6:.2f}us"] = {"xi_c_cm": xi_c*100, "d_7q": r7, "d_eagle": re}

print(f"\n  τ_B needed for ξ_c ≈ target size:")
for name, target in targets.items():
    tau_needed = target / (2 * v_s)
    print(f"  ξ_c ~ {name}: τ_B ~ {tau_needed*1e6:.3f} µs")

results["numerical"] = {
    "v_s_Si_m_per_s": float(v_s),
    "c_valid_range": f"(0, {v_s:.0f}] m/s",
    "c_equals_v_s_status": "CONDITIONALLY DERIVED",
    "c_1e4_status": "INVALID (no derivation, violates C3)",
    "xi_c_at_tau5us_cm": float(2 * v_s * 5e-6 * 100),
    "tau_for_eagle_us": float(14e-3 / (2 * v_s) * 1e6),
    "xi_c_results": xi_c_results
}

# ─── FINAL CLASSIFICATION ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FINAL CLASSIFICATION")
print("=" * 70)
print("""
  B. C_CONDITIONALLY_PREDICTED

  c = v_s = a√(K/m) follows IF the following explicit assumption is accepted:

    [PHON]: The PRW particles in the C2 coarse-grained theory are identified
            with the acoustic phonons of the FPUT substrate, whose long-
            wavelength group velocity is v_s = a√(K/m).

  This identification is:
  - Physically natural (acoustic phonons are the long-wavelength excitations)
  - Consistent with P1 construction (n± defined as phonon densities)
  - Used implicitly throughout the project (P1 governing equations)
  - NOT a theorem proved within the existing files
  - NOT stated as an explicit postulate in any project document

  Without [PHON]: c is bounded by v_s but otherwise undetermined → C_PARAMETER_DEPENDENT
  With    [PHON]: c = v_s = 6000 m/s (Si) → C_CONDITIONALLY_PREDICTED

  EXPERIMENTAL CONSEQUENCE:
  Under c = v_s = 6000 m/s (strongest justified value):
    At τ_B = 5 µs:   ξ_c = 6.0 cm >> all current chips → BLOCKED
    At τ_B = 1.2 µs: ξ_c = 1.4 cm ~ Eagle 14mm chip  → CONDITIONALLY OPEN
    τ_B ~ 1.2 µs requires NMP ~ 0.47 — identifiable but suboptimal
""")

results["final"] = {
    "classification": "C_CONDITIONALLY_PREDICTED",
    "condition": "[PHON]: PRW particles identified with FPUT acoustic phonons",
    "condition_in_existing_files": False,
    "condition_implicit": True,
    "c_value_under_condition_m_per_s": float(v_s),
    "without_condition": "C_PARAMETER_DEPENDENT (c bounded by v_s, otherwise free)",
    "experimental_branch": "CONDITIONALLY OPEN at tau_B ~ 1.2 us on Eagle-scale chip"
}

with open(os.path.join(DOUT, "c_prw_speed_audit.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {DOUT}/c_prw_speed_audit.json")
print("p27 COMPLETE")
