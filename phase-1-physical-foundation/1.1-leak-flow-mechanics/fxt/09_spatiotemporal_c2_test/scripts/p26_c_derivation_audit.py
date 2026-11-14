#!/usr/bin/env python3
"""
p26_c_derivation_audit.py — Phase 9, c Derivation Audit

Numerically verifies all velocity-related quantities derivable from the
C2/PRW/FPUT theory without fitting c to experimental data.

Questions answered:
  1. What velocities appear in the FPUT dispersion relation?
  2. What is the PRW c in terms of FPUT parameters?
  3. What does ξ_c = 2cτ_B predict for chip-scale separations?
  4. Is the constraint C3 (signal speed ≤ v_s) binding for c?
  5. What dimensional combinations in {v, λ, s0, g, ℏ} have units [m/s]?
  6. Does the variance formula <|δJ|²> predict a velocity?
  7. Internal consistency: what τ_B implies ξ_c for each candidate c?

Output: outputs/data/c_derivation_audit.json
"""

import numpy as np
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOUT = os.path.join(BASE, "outputs", "data")
os.makedirs(DOUT, exist_ok=True)

print("=" * 70)
print("p26_c_derivation_audit.py — c_C2 Derivation Audit")
print("=" * 70)

results = {}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: FPUT dispersion and acoustic speed
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 1: FPUT dispersion relation and acoustic speed")
print("─"*60)

# FPUT chain: H = Σ [p²/2m + K(q_{i+1}-q_i)²/2]   (harmonic, β=0)
# Normal modes: ω_k = 2√(K/m) |sin(πk/N)|
# Long-wavelength limit (k→0): ω_k ≈ 2√(K/m) · πk/N = (2π/N)√(K/m) · k
# In continuum: ω = v_s · k where v_s = a·√(K/m), a = lattice spacing

# Constraint C3: signal speed ≤ v_s  (from C2_FOUNDATIONS.md SUBSYSTEM 2)
# PRW speed c = v = microscopic particle speed
# C3 sets c ≤ v_s

# Representative FPUT parameters (IBM qubit chip context: silicon substrate)
# Si at 15 mK: K/m ≈ (v_sound/a)²  where v_sound(Si) ≈ 6000 m/s, a ≈ 0.54 nm
m_Si   = 4.665e-26   # kg (Si atom mass)
a_Si   = 0.543e-9    # m  (Si lattice constant)
K_Si   = m_Si * (6000.0 / a_Si)**2  # N/m from v_s = a*sqrt(K/m)

v_s_Si = a_Si * np.sqrt(K_Si / m_Si)  # should recover 6000 m/s

print(f"\nSilicon substrate parameters:")
print(f"  m_Si  = {m_Si:.3e} kg")
print(f"  a_Si  = {a_Si:.3e} m")
print(f"  K_Si  = {K_Si:.3e} N/m")
print(f"  v_s   = a√(K/m) = {v_s_Si:.1f} m/s")
print(f"  C3 constraint: c ≤ {v_s_Si:.1f} m/s  (acoustic speed of Si)")

# FPUT dispersion: compute for a range of k
N_modes = 1000
k_norm  = np.linspace(0, 0.5, N_modes)  # k in units of 1/a (from 0 to π/a)
omega_k = 2 * np.sqrt(K_Si / m_Si) * np.abs(np.sin(np.pi * k_norm))

# Phase velocity and group velocity
dk = k_norm[1] - k_norm[0]
k_abs = k_norm / a_Si   # convert to SI: 1/m
omega_si = omega_k      # rad/s

# v_phase = omega/k, v_group = d_omega/dk
v_phase = np.where(k_abs > 0, omega_si / k_abs, v_s_Si)
domega_dk = np.gradient(omega_si, k_abs)
v_group = domega_dk

print(f"\nFUPT dispersion velocities:")
print(f"  Phase velocity at k→0:   {v_s_Si:.1f} m/s  (= v_s, by construction)")
print(f"  Group velocity at k→0:   {v_s_Si:.1f} m/s  (= v_s, long-wavelength limit)")
print(f"  Group velocity at k=π/2a: {float(v_group[N_modes//2]):.1f} m/s")
print(f"  Max group velocity:      {float(v_group.max()):.1f} m/s  (= v_s, at k→0)")
print(f"  Min group velocity (zone boundary): {float(v_group[-5]):.1f} m/s  (→0)")

# Telegrapher equation dispersion (PRW):
# ω² + (i/τ)ω − c²k² = 0
# For real k, two solutions: propagating (k > k_c) and evanescent (k < k_c)
# Critical wavenumber k_c = 1/(2cτ) = λ/v

# The characteristic velocity of the telegrapher PDE is c = v (PRW speed)
# This equals the FPUT acoustic speed v_s under C3 identification
print(f"\nTelegrapher equation characteristics:")
print(f"  c = v = PRW particle speed  [DERIVED: c = v from PRW → telegrapher]")
print(f"  Under C3: c ≤ v_s = {v_s_Si:.1f} m/s")
print(f"  C3 is an INEQUALITY, not an equation: c ∈ (0, v_s]")
print(f"  C3 does not uniquely fix c.")

results["part1_fput"] = {
    "v_s_Si_m_per_s": float(v_s_Si),
    "c_equals": "v = PRW particle speed",
    "C3_constraint": "c <= v_s (INEQUALITY, not equation)",
    "c_uniquely_determined_by_C3": False,
    "status": "C3 gives upper bound, not unique value"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: Telegrapher dispersion relation — all velocities
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 2: Telegrapher dispersion — all candidate velocities")
print("─"*60)

# Telegrapher: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
# Plane wave ansatz s ~ exp(ikx - iωt):
# -τω² - iω + c²τk² = 0
# ω² + (i/τ)ω - c²k² = 0
# Solutions: ω = -i/(2τ) ± √(c²k² - 1/(4τ²))

# Case 1: k > k_c = 1/(2cτ)  →  propagating
# Real part of ω: Ω_r = √(c²k² - 1/(4τ²))
# Imaginary part: -1/(2τ)  (uniform damping, independent of k)
# Phase velocity: v_p = Ω_r / k = √(c² - 1/(4τ²k²))
# Group velocity: v_g = dΩ_r/dk = c²k / Ω_r
# As k→∞: v_p → c, v_g → c   (high-k limit: propagates at c)
# As k→k_c: v_p → 0, v_g → 0  (long-wave cutoff)

# Case 2: k < k_c  →  evanescent (purely imaginary Ω)
# No propagation, pure decay

# Signal/front velocity (Brillouin/Sommerfeld):
# The wavefront propagates at exactly c (the characteristics of the PDE)
# This is the maximum signal speed of the telegrapher equation.

# Using sample values
c_val  = 6000.0   # m/s (= v_s_Si, maximum allowed by C3)
tau_val = 5e-6    # s   (= τ_B from Ramsey, representative)

k_c = 1 / (2 * c_val * tau_val)
print(f"\nUsing c = v_s = {c_val:.0f} m/s, τ = {tau_val*1e6:.1f} µs:")
print(f"  k_c = 1/(2cτ) = {k_c:.2e} m⁻¹  (λ_c = {2*np.pi/k_c*1e3:.2f} mm)")

k_test = np.linspace(0, 10 * k_c, 1000)
k_prop = k_test[k_test > k_c]

Omega_r  = np.sqrt(c_val**2 * k_prop**2 - 1/(4*tau_val**2))
v_phase_tel = Omega_r / k_prop
v_group_tel = c_val**2 * k_prop / Omega_r

print(f"\n  High-k limit: v_phase → {v_phase_tel[-1]:.1f} m/s  (→ c = {c_val:.0f})")
print(f"  High-k limit: v_group → {v_group_tel[-1]:.1f} m/s  (→ c = {c_val:.0f})")
print(f"  At k = 2*k_c: v_phase = {v_phase_tel[len(v_phase_tel)//3]:.1f} m/s, v_group = {v_group_tel[len(v_group_tel)//3]:.1f} m/s")

print(f"\n  Telegrapher characteristic velocity:")
print(f"  Front velocity = c = v = PRW particle speed = {c_val:.0f} m/s  [by definition]")
print(f"  This is the ONLY velocity uniquely identified by the telegrapher PDE.")
print(f"  It equals the PRW step-speed v, which equals v_s under C3.")
print(f"  v_phase and v_group are k-dependent and do NOT give a unique c.")

# The correlation spreading velocity:
# From the Green's function, signals spread as wavefronts at ±c.
# The spatial correlation length ξ_c = v/λ = 2cτ uses THIS front velocity c.
xi_c_Si = 2 * c_val * tau_val
print(f"\n  Correlation length ξ_c = 2cτ:")
print(f"  At c = v_s = {c_val:.0f} m/s, τ = {tau_val*1e6:.1f} µs:")
print(f"  ξ_c = 2 × {c_val:.0f} × {tau_val*1e6:.1f}µs = {xi_c_Si*100:.2f} cm")

results["part2_dispersion"] = {
    "telegrapher_characteristic_velocity": "c = v = PRW front speed",
    "v_phase": "k-dependent, not unique",
    "v_group": "k-dependent, not unique",
    "front_velocity": "c (unique, k-independent)",
    "xi_c_at_c_equals_v_s_Si": float(xi_c_Si),
    "xi_c_cm": float(xi_c_Si * 100)
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: Dimensional analysis — all [m/s] combinations in C2 parameters
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 3: Dimensional analysis — all [m/s] combinations")
print("─"*60)

print("""
C2 theory parameters and their dimensions:

  v  [m/s]              — PRW particle speed               ASSUMED [A-PRW1]
  λ  [s⁻¹]             — PRW reversal rate                 ASSUMED [A-PRW1]
  s₀ [info/m³]         — background information density    ASSUMED
  g  [J·m²·s/info]     — quantum-classical coupling        FREE PARAMETER
  ℏ  [J·s]             — Planck constant                   EMPIRICAL
  r_q [m]              — effective qubit radius            FREE PARAMETER
  m  [kg]              — FPUT particle mass                FPUT input
  K  [N/m = kg/s²]     — FPUT spring constant              FPUT input
  a  [m]               — FPUT lattice constant             FPUT input

All independent velocity combinations:
""")

# Enumerate all combinations with dimensions [m/s]:
velocities = {}

# v itself
velocities["v"] = {
    "formula": "v",
    "derivation": "PRW particle speed — ASSUMED in A-PRW1",
    "status": "ASSUMED",
    "depends_on_c3": "No (v is input, C3 constrains it)"
}

# v_s = a*sqrt(K/m) from FPUT
velocities["v_s = a*sqrt(K/m)"] = {
    "formula": "a * sqrt(K/m)",
    "derivation": "FPUT acoustic speed — DERIVED from FPUT harmonic chain",
    "status": "DERIVED from FPUT inputs (a, K, m)",
    "numerical_Si": float(v_s_Si),
    "units_check": "[m] * sqrt([kg/s²]/[kg]) = [m/s] ✓"
}

# D/τ has units [m²/s / s] = [m/s]²... not [m/s]
# D alone: [m²/s] — not velocity
# sqrt(D/τ) = sqrt(c²τ/τ) = c — reduces to c
velocities["sqrt(D/tau)"] = {
    "formula": "sqrt(c²τ/τ) = c",
    "derivation": "Reduces to c — same parameter",
    "status": "TRIVIAL IDENTITY"
}

# λ * ξ_c = λ * v/λ = v — same
velocities["lambda * xi_c"] = {
    "formula": "λ × ξ_c = λ × (v/λ) = v",
    "derivation": "Reduces to v — same parameter",
    "status": "TRIVIAL IDENTITY"
}

# From variance: <|δJ|²> = (2/3)s₀²ω_rot²r_q²
# This has dimensions [info/(m²·s)]² · [rad/s]² · [m]² = ...
# Let me check: s₀ [info/m³], J [info/(m²·s)], so <|δJ|²> [info²/(m⁴·s²)]
# ω_rot²r² has [rad²/s² · m²] = [m²/s²]
# So (2/3)s₀²ω_rot²r_q² has [(info/m³)² · m²/s²] = [info²·m²/(m⁶·s²)·m²]
# Wait: s₀² has [info²/m⁶], ω²r² has [m²/s²]
# Product: [info²·m²/(m⁶·s²)] = [info²/(m⁴·s²)] — same as J² ✓
# The variance does NOT have units [m/s] directly.
# To get a velocity from variance: v ~ sqrt(<J²>) / s₀ = sqrt(s₀²v²/2) / s₀ = v/√2
velocities["sqrt(<J²>)/s₀"] = {
    "formula": "sqrt(<J²>) / s₀ = sqrt(s₀²v²/2) / s₀ = v/√2",
    "derivation": "Reduces to v/√2 — same PRW speed",
    "status": "TRIVIAL (proportional to v)"
}

# From PRW equipartition: <J²> = s₀v²/2
# This gives only v, already counted.

# ξ_c/τ_B = v/λ × 2λ = 2v — same
velocities["xi_c / tau_B"] = {
    "formula": "ξ_c/τ_B = (v/λ)/(1/(2λ)) = 2v",
    "derivation": "= 2v = 2c (the factor in ξ_c = 2cτ_B)",
    "status": "TRIVIAL IDENTITY — just names 2c"
}

# g/ℏ has units [J·m²·s/info / J·s] = [m²/info] — NOT [m/s]
# s₀·g/ℏ has [info/m³ · m²/info] = [1/m] — NOT [m/s]
# ω_q has units [rad/s] — not [m/s]
# ω_q · r_q has [rad/s · m] = [m/s] — this IS a velocity!
velocities["omega_q * r_q"] = {
    "formula": "ω_q × r_q",
    "derivation": "Qubit transition frequency × effective qubit radius",
    "status": "NOT DERIVED — ω_q is empirical, r_q is FREE PARAMETER",
    "note": "Gives tangential speed of qubit 'surface' — physical meaning unclear"
}

# Γ_M * r_q² / τ_B has units [s⁻¹ · m² / s] = [m²/s²] → sqrt → [m/s]
# But this mixes Γ_M (which requires CA-3 to relate to c) — circular
velocities["sqrt(Gamma_M * r_q^2 / tau_B)"] = {
    "formula": "sqrt(Γ_M × r_q² / τ_B)",
    "derivation": "CIRCULAR: Γ_M ∝ s₀²v²τ_B/ℏ² × r_q² via CA-3",
    "status": "CIRCULAR — reduces to v × (r_q × constants) / ℏ"
}

print(f"  {'Combination':35s}  {'Status':30s}  {'Value (Si)'}")
for name, info in velocities.items():
    val = info.get("numerical_Si", "—")
    val_str = f"{val:.1f} m/s" if isinstance(val, float) else val
    print(f"  {name:35s}  {info['status']:30s}  {val_str}")

print(f"""
  KEY FINDING:
  The ONLY velocity with genuine [m/s] dimensions that is independently
  defined by the C2/PRW/FPUT theory (without fitting) is:

    c = v = PRW particle speed  [ASSUMED in A-PRW1]

  with the FPUT-derived upper bound:

    c ≤ v_s = a√(K/m)          [DERIVED from FPUT + C3]

  No combination of the other parameters (s₀, g, ℏ, r_q, λ) gives a
  velocity that is independent of v.
""")

results["part3_dimensional"] = {
    "velocities_found": list(velocities.keys()),
    "independent_velocity": "c = v (ASSUMED A-PRW1)",
    "derived_upper_bound": "c <= v_s = a*sqrt(K/m) [FPUT + C3]",
    "C3_gives_upper_bound_only": True,
    "unique_velocity_from_dynamics": False
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: Does C3 uniquely fix c?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 4: Does C3 uniquely fix c?")
print("─"*60)

print("""
  C3 states: "Signal speed ≤ acoustic sound speed v_s"

  This is an INEQUALITY: c ≤ v_s.

  Interpretations:
    (a) C3 as upper bound only: c ∈ (0, v_s]. Any c up to v_s is admissible.
    (b) C3 as equality (saturation): c = v_s is the unique admissible value
        IF the PRW is required to propagate at the maximum allowed speed.

  Saturation argument:
    In the PRW, the microscopic particles travel at exactly c between reversals.
    The reversals introduce damping (τ = 1/(2λ)).
    If the PRW particles are identified with the FPUT phonons in the acoustic
    branch, then c = v_s is the natural identification (phonon group speed at k→0).
    There is no mechanism in the theory that would select c < v_s.

  However: the FPUT → PRW projection (Theorem FPUT-3) projects out the phase
  information. The projection retains only the action variables nₖ.
  The resulting PRW has particle speed v. Theorem FPUT-3 does NOT derive
  a specific value of v — it proves the uniqueness of the projection type,
  not the value of v within that projection class.

  Therefore:
    C3 gives:  c ≤ v_s  (upper bound, DERIVED from FPUT + C3)
    C3 alone:  c = v_s  ONLY IF saturation is postulated separately
    Theory:    v is a FREE PARAMETER of the PRW [A-PRW1]

  SATURATION ASSUMPTION (not in current C2 theory):
    If one additionally assumes that the PRW maximally saturates C3 (c = v_s),
    then c = a√(K/m) is determined by FPUT parameters.
    This would make c a derived quantity.
    But this saturation assumption is NOT present in the existing theory files.
    It would be a new assumption.

  CONCLUSION:
    C3 constrains c but does not uniquely determine c from first principles.
    The value c = v_s is a natural candidate but requires a saturation postulate.
""")

results["part4_C3"] = {
    "C3_type": "inequality: c <= v_s",
    "C3_uniquely_fixes_c": False,
    "saturation_c_equals_v_s": "Requires additional postulate not in current theory",
    "c_as_free_parameter": True,
    "status_under_saturation": "c = a*sqrt(K/m) — DERIVED if saturation postulated"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: ξ_c predictions for all justified c values
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 5: ξ_c predictions for representative c values")
print("─"*60)

tau_B = 5e-6  # s — representative τ_B from Ramsey fits
chip_max = 632e-6  # m — IBM 7-qubit chip max separation

print(f"\n  Using τ_B = {tau_B*1e6:.1f} µs (representative Ramsey value)")
print(f"  Chip max separation = {chip_max*1e6:.0f} µm")
print(f"  Condition for resolvable test: ξ_c < 2 × chip_max = {2*chip_max*1e6:.0f} µm\n")

c_candidates = {
    "c = v_s(Si) [FPUT C3 saturation]": v_s_Si,
    "c = 10^4 m/s [prev assumed]": 1e4,
    "c = 10^3 m/s": 1e3,
    "c = 10^2 m/s": 1e2,
    "c = 10^1 m/s": 1e1,
    "c = 10^0 m/s": 1.0,
    "c = D/ξ_c [requires circular]": None,
}

print(f"  {'c (m/s)':35s}  {'ξ_c = 2cτ_B':15s}  {'d/ξ_c at chip':15s}  {'Resolvable?'}")
print(f"  {'─'*80}")

for name, c in c_candidates.items():
    if c is None:
        print(f"  {name:35s}  {'UNDEFINED':15s}  {'─':15s}  CIRCULAR")
        continue
    xi_c = 2 * c * tau_B
    d_over_xi = chip_max / xi_c
    resolvable = d_over_xi > 0.1  # need d/ξ_c > 0.1 for shape test
    print(f"  {name:35s}  {xi_c*1e3:12.3f} mm  {d_over_xi:15.4f}  "
          f"{'YES' if resolvable else 'NO (ξ_c >> chip)'}")

print(f"""
  KEY RESULT:
  At c = v_s(Si) = {v_s_Si:.0f} m/s:
    ξ_c = {2*v_s_Si*tau_B*100:.1f} cm >> chip ({chip_max*1e6:.0f} µm)
    The spatial test is NOT resolvable.

  For ξ_c to be resolvable (ξ_c ~ 1 mm):
    c must be < {0.5e-3 / (2*tau_B):.1f} m/s
    This is far below any physical prediction from C2 or FPUT.

  Even if c is postulated as c = v_s(Si) = 6000 m/s, the test is inaccessible.
""")

results["part5_xi_c_predictions"] = {
    "tau_B_us": float(tau_B * 1e6),
    "chip_max_um": float(chip_max * 1e6),
    "c_v_s_Si": {"c_m_s": float(v_s_Si), "xi_c_cm": float(2*v_s_Si*tau_B*100),
                 "d_over_xi": float(chip_max/(2*v_s_Si*tau_B))},
    "c_1e4": {"c_m_s": 1e4, "xi_c_cm": float(2*1e4*tau_B*100),
              "d_over_xi": float(chip_max/(2*1e4*tau_B))},
    "c_for_resolvable_mm": float(0.5e-3 / (2*tau_B)),
    "resolvable_requires_c_less_than_m_s": float(0.5e-3 / (2*tau_B))
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: CA-3 dependency of c
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 6: Does deriving c require CA-3?")
print("─"*60)

print("""
  CA-3: Γφ ∝ <(δJ)²>

  The PRW particle speed c = v does NOT require CA-3.
  c is defined at the microscopic PRW level [A-PRW1], before any
  connection to quantum decoherence is made.

  The FPUT acoustic speed v_s = a√(K/m) does NOT require CA-3.
  v_s is purely a classical mechanical result from the FPUT chain.

  C3 (c ≤ v_s) does NOT require CA-3.
  C3 is an admissibility constraint on projections, not a decoherence result.

  CONCLUSION:
  Deriving c does NOT require CA-3.
  c = v is defined at the PRW microscopic level.
  c ≤ v_s is derived from FPUT + C3.

  CA-3 IS REQUIRED for:
    - Connecting c to Γφ (decoherence rate)
    - Connecting c to any qubit observable
    - Inferring c from measured Γφ data

  Since c cannot be measured from quantum decoherence data without CA-3,
  and CA-3 is a postulate, c remains empirically unconstrained
  even if theoretically bounded by v_s.
""")

results["part6_ca3"] = {
    "c_requires_ca3": False,
    "c_upper_bound_requires_ca3": False,
    "empirical_constraint_of_c_requires_ca3": True,
    "conclusion": "c is theoretically bounded by v_s without CA-3, but empirically unconstrained"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: Variance analysis — does <|δJ|²> predict a velocity?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 7: Variance <|δJ|²> = (2/3)s₀²ω_rot²r² — velocity content")
print("─"*60)

print("""
  The variance <|δJ|²> = (2/3)s₀²ω_rot²r² [ESTABLISHED-VAR]

  Dimensions:
    s₀  [info/m³]
    ω_rot [rad/s]
    r   [m]
    <|δJ|²> [(info/(m²·s))²] = [info²/(m⁴·s²)]

  The variance is a measure of current fluctuation power.
  Current J = s·v_sub has units [info/(m²·s)] = [info·m⁻²·s⁻¹].

  Can we extract a velocity from the variance?

  Method 1: √(<|δJ|²>) / s₀ = √((2/3)) × ω_rot × r
    This has units [m/s] — it is an orbital velocity ω_rot × r.
    It is the tangential speed of substrate flow in the rotating frame.
    This is NOT the PRW particle speed c.
    It is an OBSERVABLE quantity (if ω_rot and r are known).

  Method 2: <|δJ|²> / s₀²
    Has units [m²/s²] = v² — square of a velocity.
    sqrt(<|δJ|²> / s₀²) = √(2/3) × ω_rot × r  [same as above]

  Method 3: From PRW equipartition <J²> = s₀v²/2
    This directly gives v = √(2<J²>/s₀) — the PRW speed c.
    But this requires knowing s₀ independently, which is a free parameter.

  CONCLUSION:
  The variance formula DOES contain velocity information:
    - ω_rot × r  = tangential frame velocity  [OBSERVABLE if r_q is known]
    - v = c      = PRW speed                  [ASSUMED free parameter]

  Neither gives a unique prediction for c.
  The ratio (ω_rot × r) / c = ω_rot × r_q / c is dimensionless
  and is the ratio of the rotating-frame speed to the substrate speed.
  This ratio is not derived from first principles.
""")

results["part7_variance"] = {
    "velocity_from_variance": "omega_rot * r (tangential) or c (PRW speed)",
    "tangential_velocity_observable": True,
    "tangential_velocity_equals_c": False,
    "c_from_variance": "CIRCULAR (requires s0 which is free parameter)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PART 8: Internal consistency check
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "─"*60)
print("PART 8: Internal consistency — previous assumption c=10^4 m/s")
print("─"*60)

c_prev = 1e4  # m/s — previously assumed value
print(f"\n  Previously assumed: c = {c_prev:.0e} m/s")
print(f"  C3 constraint: c ≤ v_s(Si) = {v_s_Si:.0f} m/s")
print(f"  Consistency: {c_prev:.0e} < {v_s_Si:.0f} → {'CONSISTENT with C3' if c_prev < v_s_Si else 'VIOLATES C3'}")
print(f"  But: c = {c_prev:.0e} m/s has NO derivation from C2 theory.")
print(f"  It was chosen to make ξ_c = 2cτ_B ~ cm scale for an experiment.")
print(f"  This is parameter choice for experimental convenience, not a prediction.")

print(f"\n  Under c = v_s(Si) = {v_s_Si:.0f} m/s (C3 saturation):")
xi_c_1 = 2 * v_s_Si * tau_B
print(f"    ξ_c = {xi_c_1*100:.1f} cm  >>  chip = {chip_max*1e6:.0f} µm")
print(f"    Spatial test: NOT accessible")

print(f"\n  Under c = v_s(Si)/10 = {v_s_Si/10:.0f} m/s:")
xi_c_2 = 2 * (v_s_Si/10) * tau_B
print(f"    ξ_c = {xi_c_2*100:.2f} cm  >>  chip = {chip_max*1e6:.0f} µm")
print(f"    Spatial test: STILL NOT accessible")

print(f"\n  Required c for ξ_c ~ 1mm (marginally accessible):")
c_required = 1e-3 / (2 * tau_B)
print(f"    c = ξ_c/(2τ_B) = 1mm / (2×{tau_B*1e6:.0f}µs) = {c_required:.1f} m/s")
print(f"    This is {c_required/v_s_Si*100:.4f}% of v_s(Si) — physically implausible")

results["part8_consistency"] = {
    "c_prev_assumed": float(c_prev),
    "c_prev_violates_C3": bool(c_prev > v_s_Si),
    "c_prev_has_derivation": False,
    "c_prev_chosen_for": "experimental convenience",
    "c_v_s_Si_gives_xi_c_cm": float(xi_c_1 * 100),
    "c_for_mm_scale_xi_c_m_per_s": float(c_required),
    "c_required_over_v_s_Si": float(c_required / v_s_Si)
}

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("FINAL CLASSIFICATION")
print("="*70)

print("""
  The C2 theory establishes:

    (A) c = v (PRW speed) — ASSUMED in A-PRW1, not derived
    (B) c ≤ v_s = a√(K/m) — DERIVED from FPUT + C3 (upper bound only)
    (C) c = v_s under a saturation postulate — NOT in current theory

  The theory does NOT derive a unique value or range for c.

  CLASSIFICATION: C_PARAMETER_DEPENDENT

  Specifically:
    c is bounded above by the FPUT acoustic speed v_s (DERIVED from C3),
    but the specific value of c within (0, v_s] is a free parameter.

    A unique c emerges ONLY if the additional postulate is added:
      "The PRW saturates C3 (c = v_s)"
    which is not currently in the C2 theory files.

  Under the natural saturation assumption c = v_s = 6000 m/s:
    ξ_c = 2 × 6000 × 5µs = 6 cm >> chip size (632 µm)
    The spatial discrimination test remains inaccessible.
    This conclusion is INDEPENDENT of which value of c is used,
    as long as c is a physically reasonable velocity (>> 100 m/s).

  What is needed to reopen the experimental branch:
    1. Derive c from FPUT parameters without the saturation postulate, OR
    2. Add the saturation postulate explicitly and justify it physically, AND
    3. Explain why ξ_c ~ cm → spatial test feasible on a different platform, OR
    4. Find a C2 parameter regime where c << 100 m/s (physically implausible)
""")

classification = "C_PARAMETER_DEPENDENT"
print(f"  FINAL CLASSIFICATION: {classification}")

results["final"] = {
    "classification": classification,
    "c_derived": False,
    "c_upper_bound_derived": True,
    "c_upper_bound": "v_s = a*sqrt(K/m)",
    "c_upper_bound_Si_m_per_s": float(v_s_Si),
    "saturation_postulate_needed": True,
    "saturation_postulate_in_current_theory": False,
    "xi_c_at_v_s_Si_cm": float(2 * v_s_Si * tau_B * 100),
    "spatial_test_accessible": False,
    "condition_to_reopen": "Add saturation postulate c=v_s explicitly, then obtain platform with d~cm or larger chip"
}

# Save
with open(os.path.join(DOUT, "c_derivation_audit.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {DOUT}/c_derivation_audit.json")
print("p26 COMPLETE")
print("=" * 70)
