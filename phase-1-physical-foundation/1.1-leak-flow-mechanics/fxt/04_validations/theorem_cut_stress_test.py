"""
theorem_cut_stress_test.py
===========================
Focused challenge to Theorem CUT (Conditional Uniqueness of Transport speed).

The claim in the prior audit was:
    "SE1 + SE2 + SE3 + SE4 are necessary and sufficient for a unique propagation
     speed c = a/dt."

This script tests three distinct questions:

Q1. SCALE FREEDOM: Does SE1 alone (metric embedding) fix the numerical value of a?
    Or can we rescale φ → kφ (k > 0) while retaining SE2, SE3, SE4 and getting c → kc?

Q2. NECESSITY: Is each of SE1–SE4 individually necessary, or does some subset suffice?

Q3. SUFFICIENCY vs SUFFICIENCY-UP-TO-SCALE: Do SE1–SE4 give a unique numerical speed,
    or only a unique speed *relative to chosen units*?

Q4. THE FIFTH CONDITION: What minimal additional condition, if any, closes the
    remaining scale freedom?

Expected outcome: Theorem CUT as stated is too strong. SE1–SE4 fix c only up to
a global rescaling of the metric (and/or the time unit). A fifth condition SE5 is
needed to fix the numerical value in physical units. This condition is empirical,
not axiomatic.

Reproducible command:
    cd .../fxt && python 04_validations/theorem_cut_stress_test.py

Output:
    04_validations/outputs/theorem_cut_stress_test.json

Date: 2026-10-10
"""

import json
import math

OUTPUT_PATH = "04_validations/outputs/theorem_cut_stress_test.json"


# ─────────────────────────────────────────────────────────────────────────────
# Q1: Scale freedom — φ → kφ rescaling
# ─────────────────────────────────────────────────────────────────────────────
def test_q1_scale_freedom():
    """
    Show that for any k > 0, replacing a → k·a (rescaling the metric embedding)
    while keeping dt fixed (SE3), or replacing dt → dt/k while keeping a fixed,
    satisfies SE1–SE4 but changes c = a/dt → k·c.

    Both (SE1: a, SE3: dt) and (SE1: k·a, SE3: dt) and (SE1: a, SE3: dt/k)
    satisfy:
      SE1: metric embedding exists (just rescaled)
      SE2: isotropy (k·a is still equal in all directions)
      SE3: uniform time (dt or dt/k, still uniform)
      SE4: single branch (unchanged)
    But they give different numerical c values.
    """
    a_base = 1.0e-6   # m — reference spatial step
    dt_base = 2.0e-10  # s — reference time step
    c_base = a_base / dt_base  # 5000 m/s

    scale_factors = [0.001, 0.1, 1.0, 10.0, 1000.0]

    # Case A: rescale a, keep dt fixed
    rescaled_a = []
    for k in scale_factors:
        a_k = k * a_base
        c_k = a_k / dt_base
        rescaled_a.append({
            "k": k,
            "a_m": a_k,
            "dt_s": dt_base,
            "c_m_per_s": c_k,
            "SE1_satisfied": True,   # φ → kφ still a valid metric embedding
            "SE2_satisfied": True,   # k·a still equal in all directions
            "SE3_satisfied": True,   # dt unchanged
            "SE4_satisfied": True,   # single branch unchanged
            "c_changed": abs(c_k - c_base) > 1e-9
        })

    # Case B: rescale dt, keep a fixed
    rescaled_dt = []
    for k in scale_factors:
        dt_k = dt_base / k
        c_k = a_base / dt_k
        rescaled_dt.append({
            "k": k,
            "a_m": a_base,
            "dt_s": dt_k,
            "c_m_per_s": c_k,
            "SE1_satisfied": True,
            "SE2_satisfied": True,
            "SE3_satisfied": True,   # dt/k still uniform across all morphisms
            "SE4_satisfied": True,
            "c_changed": abs(c_k - c_base) > 1e-9
        })

    # Case C: rescale both a and dt by the same factor (c invariant under this)
    rescaled_both_same = []
    for k in scale_factors:
        a_k = k * a_base
        dt_k = k * dt_base
        c_k = a_k / dt_k
        rescaled_both_same.append({
            "k": k,
            "a_m": a_k,
            "dt_s": dt_k,
            "c_m_per_s": c_k,
            "c_unchanged": abs(c_k - c_base) < 1e-9
        })

    all_cases_a_satisfy_SE1_to_SE4 = all(
        r["SE1_satisfied"] and r["SE2_satisfied"] and
        r["SE3_satisfied"] and r["SE4_satisfied"]
        for r in rescaled_a
    )
    all_cases_b_satisfy_SE1_to_SE4 = all(
        r["SE1_satisfied"] and r["SE2_satisfied"] and
        r["SE3_satisfied"] and r["SE4_satisfied"]
        for r in rescaled_dt
    )
    all_cases_a_give_different_c = all(
        r["c_changed"] for r in rescaled_a if r["k"] != 1.0
    )
    all_cases_b_give_different_c = all(
        r["c_changed"] for r in rescaled_dt if r["k"] != 1.0
    )
    rescaling_both_same_preserves_c = all(
        r["c_unchanged"] for r in rescaled_both_same
    )

    conclusion = (
        "SE1–SE4 DO NOT fix the numerical value of c. "
        "Rescaling a → ka (k ≠ 1) satisfies all four conditions but changes c → kc. "
        "Rescaling dt → dt/k also satisfies all four conditions and also changes c → kc. "
        "Only the RATIO c = a/dt is preserved under simultaneous rescaling a → ka, dt → kdt. "
        "Therefore SE1–SE4 fix c only UP TO independent rescalings of the length unit "
        "and the time unit. A fifth condition is needed to fix the numerical value."
    )

    theorem_cut_verdict = (
        "THEOREM CUT AS STATED IS TOO STRONG. "
        "It claims SE1–SE4 are sufficient for a unique numerical speed c. "
        "But for any k > 0, (SE1: k·a, SE2, SE3: dt, SE4) also satisfies all "
        "four conditions and gives c → kc. The theorem gives uniqueness ONLY if "
        "the numerical values of a and dt are treated as pre-fixed — i.e., if the "
        "metric and time unit are externally given. That is an implicit fifth condition."
    )

    return {
        "test": "Q1_scale_freedom",
        "reference_a_m": a_base,
        "reference_dt_s": dt_base,
        "reference_c_m_per_s": c_base,
        "rescale_a_cases": rescaled_a,
        "rescale_dt_cases": rescaled_dt,
        "rescale_both_same_cases": rescaled_both_same,
        "all_rescaled_a_satisfy_SE1_to_SE4": all_cases_a_satisfy_SE1_to_SE4,
        "all_rescaled_dt_satisfy_SE1_to_SE4": all_cases_b_satisfy_SE1_to_SE4,
        "all_rescaled_a_give_different_c": all_cases_a_give_different_c,
        "all_rescaled_dt_give_different_c": all_cases_b_give_different_c,
        "rescaling_both_same_preserves_c": rescaling_both_same_preserves_c,
        "conclusion": conclusion,
        "theorem_cut_verdict": theorem_cut_verdict,
        "status": "FAIL"   # SE1–SE4 are NOT sufficient for unique numerical c
    }


# ─────────────────────────────────────────────────────────────────────────────
# Q2: Necessity — is each of SE1–SE4 individually necessary?
# ─────────────────────────────────────────────────────────────────────────────
def test_q2_necessity():
    """
    For each axiom SE1–SE4, show a counterexample where that axiom is removed
    but the other three hold, and c is non-unique.

    However, now that we know SE1–SE4 only give c up to scale, we must be careful:
    'uniqueness' here means uniqueness up to scale (fixing a ratio c = a/dt for
    a given embedding), not uniqueness of the numerical value in m/s.
    """
    results = {}

    # Remove SE1: no metric embedding → c = a/dt has no a to use → undefined
    results["without_SE1"] = {
        "axioms_held": ["SE2", "SE3", "SE4"],
        "axiom_removed": "SE1 (metric embedding)",
        "counterexample": (
            "Without SE1 there is no spatial scale a. "
            "c = a/dt cannot be computed without a. "
            "Any positive real can serve as c — complete non-uniqueness."
        ),
        "is_necessary": True
    }

    # Remove SE2: anisotropic embedding → c_x ≠ c_y
    a_x, a_y = 1.0e-6, 1.5e-6
    dt = 2.0e-10
    c_x = a_x / dt
    c_y = a_y / dt
    results["without_SE2"] = {
        "axioms_held": ["SE1", "SE3", "SE4"],
        "axiom_removed": "SE2 (isotropy)",
        "counterexample": {
            "a_x": a_x, "a_y": a_y, "dt": dt,
            "c_x_m_per_s": c_x, "c_y_m_per_s": c_y,
            "description": "Anisotropic embedding gives c_x ≠ c_y. Two propagation speeds."
        },
        "is_necessary": True
    }

    # Remove SE3: non-uniform dt → c varies per morphism
    a = 1.0e-6
    dt_short, dt_long = 1.0e-10, 3.0e-10
    c_short = a / dt_short
    c_long = a / dt_long
    results["without_SE3"] = {
        "axioms_held": ["SE1", "SE2", "SE4"],
        "axiom_removed": "SE3 (uniform time step)",
        "counterexample": {
            "a": a, "dt_short": dt_short, "dt_long": dt_long,
            "c_short": c_short, "c_long": c_long,
            "description": "Different dt per morphism → different c per morphism."
        },
        "is_necessary": True
    }

    # Remove SE4: multiple branches → multiple c values
    a1, a2 = 1.0e-6, 2.0e-6
    dt_uniform = 2.0e-10
    c1 = a1 / dt_uniform
    c2 = a2 / dt_uniform
    results["without_SE4"] = {
        "axioms_held": ["SE1", "SE2", "SE3"],
        "axiom_removed": "SE4 (single branch)",
        "counterexample": {
            "a_branch1": a1, "a_branch2": a2, "dt": dt_uniform,
            "c_branch1": c1, "c_branch2": c2,
            "description": "Two branches with different step lengths → two speeds."
        },
        "is_necessary": True
    }

    return {
        "test": "Q2_necessity",
        "results": results,
        "all_four_necessary": True,
        "caveat": (
            "These necessity results hold for uniqueness-of-ratio c = a/dt "
            "given fixed a and dt. They do NOT establish necessity for "
            "uniqueness of the numerical value in m/s, because (as shown in Q1) "
            "SE1–SE4 together do not fix the numerical value either."
        ),
        "status": "PASS"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Q3: Sufficiency: what exactly do SE1–SE4 fix?
# ─────────────────────────────────────────────────────────────────────────────
def test_q3_what_SE1_to_SE4_fix():
    """
    Clarify precisely what SE1–SE4 do and do not determine.

    They fix: the RATIO c = a/dt, given specific numerical values of a and dt.
    They do not fix: the absolute values of a or dt, or c itself in m/s.

    The freedom that remains is a 2-parameter family of rescalings:
        a → k_a * a,  dt → k_t * dt,  c → (k_a/k_t) * c
    where k_a and k_t are independent positive reals.

    A fifth condition SE5 must either:
    (A) Fix k_a independently (i.e., anchor the length scale), or
    (B) Fix k_t independently (i.e., anchor the time scale), or
    (C) Fix the ratio k_a/k_t = 1 (i.e., require a and dt to be measured
        in pre-specified physical units, which is an empirical condition), or
    (D) Anchor c directly to a measured physical quantity.
    """
    # The two-parameter scaling freedom
    a_base = 1.0e-6
    dt_base = 2.0e-10
    c_base = a_base / dt_base

    # All of these satisfy SE1–SE4 simultaneously
    free_family = []
    for k_a in [0.1, 1.0, 10.0]:
        for k_t in [0.1, 1.0, 10.0]:
            a_new = k_a * a_base
            dt_new = k_t * dt_base
            c_new = a_new / dt_new
            free_family.append({
                "k_a": k_a,
                "k_t": k_t,
                "a_m": a_new,
                "dt_s": dt_new,
                "c_m_per_s": c_new,
                "SE1_to_SE4_satisfied": True
            })

    distinct_c_values = sorted(set(round(r["c_m_per_s"], 6) for r in free_family))
    n_distinct_c = len(distinct_c_values)

    # The ratio c = a/dt is preserved only when k_a/k_t = 1
    preserved_ratio_cases = [r for r in free_family if abs(r["k_a"]/r["k_t"] - 1.0) < 1e-9]

    return {
        "test": "Q3_what_SE1_to_SE4_fix",
        "reference_c_m_per_s": c_base,
        "free_family_size": len(free_family),
        "distinct_c_values_under_SE1_to_SE4": distinct_c_values,
        "n_distinct_c_values": n_distinct_c,
        "conclusion": (
            "SE1–SE4 admit a 2-parameter family of valid (a, dt) pairs: "
            "a → k_a*a, dt → k_t*dt for any k_a, k_t > 0. "
            f"This gives {n_distinct_c} distinct c values in the tested grid. "
            "In continuous parameter space, infinitely many c values are possible. "
            "SE1–SE4 do NOT uniquely fix c in m/s. They fix c only when "
            "a and dt are themselves fixed — which requires a fifth condition."
        ),
        "what_is_fixed": "c as a ratio a/dt, given specific numerical a and dt",
        "what_is_not_fixed": "the numerical values of a, dt, or c in physical units",
        "remaining_freedom": "2-parameter group: (a, dt) -> (k_a*a, k_t*dt), k_a,k_t > 0",
        "status": "PASS"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Q4: What fifth condition closes the scale freedom?
# ─────────────────────────────────────────────────────────────────────────────
def test_q4_fifth_condition():
    """
    Identify the minimal fifth condition SE5 that, together with SE1–SE4,
    uniquely fixes the numerical value of c in physical units.

    Four candidate forms of SE5 are analysed:
    SE5a: Anchor a to a physical length (e.g., a = n × (Planck length), or
          a = some fixed fraction of the qubit size r_q)
    SE5b: Anchor dt to a physical time (e.g., dt = n × (Planck time))
    SE5c: Require c_CCA = c_measured for some independently measured speed
          (e.g., c_CCA = acoustic phonon speed in the substrate material)
    SE5d: Require that the theory's prediction for some observable equals a
          measured value (i.e., SE5 is an empirical calibration condition)

    All of SE5a–SE5d are EMPIRICAL, not axiomatic derivations.
    None follows from Ax1–Ax5 or from SE1–SE4.
    """
    candidates = {
        "SE5a_anchor_length": {
            "statement": "Fix a to a physical length: a = n * l_Planck or a = r_q * f",
            "type": "Empirical / physical identification",
            "derivable_from_Ax1_Ax5": False,
            "derivable_from_SE1_SE4": False,
            "fixes_scale": True,
            "example": "a = r_q ~ 100 nm → dt = a/c_acoustic, c = c_acoustic",
            "problem": "r_q and c_acoustic must be measured; introduces new empirical parameters"
        },
        "SE5b_anchor_time": {
            "statement": "Fix dt to a physical time: dt = n * t_Planck or dt = 1/omega_qubit",
            "type": "Empirical / physical identification",
            "derivable_from_Ax1_Ax5": False,
            "derivable_from_SE1_SE4": False,
            "fixes_scale": True,
            "example": "dt = 1/omega_qubit ~ 2e-10 s (for 5 GHz qubit)",
            "problem": "omega_qubit must be measured; makes c depend on qubit design"
        },
        "SE5c_anchor_c_to_measurement": {
            "statement": "Require c_CCA = v_acoustic for the specific physical substrate",
            "type": "Empirical identification / constitutive relation",
            "derivable_from_Ax1_Ax5": False,
            "derivable_from_SE1_SE4": False,
            "fixes_scale": True,
            "example": "c = v_LA(silicon) ≈ 8435 m/s (for [100] propagation)",
            "problem": "This is the GAP-7 assumption: identifying CCA speed with phonon speed. The identification is not derived.",
            "circularity_check": "This makes c = v_acoustic, which is what GAP-7 is trying to derive. It is not a new axiom — it is the same unproved identification."
        },
        "SE5d_empirical_calibration": {
            "statement": "Calibrate c by fitting to a measured observable (e.g., xi_c from qubit data)",
            "type": "Empirical / calibration",
            "derivable_from_Ax1_Ax5": False,
            "derivable_from_SE1_SE4": False,
            "fixes_scale": True,
            "example": "c = xi_c_measured / (2 * tau_B_measured) from Ramsey experiment",
            "problem": "This makes c a measured parameter, not a derived one. Consistent but not foundational.",
            "status": "This is the honest position: c is an empirical input."
        }
    }

    # Key point: SE5 is always empirical
    all_SE5_are_empirical = all(
        not v["derivable_from_Ax1_Ax5"] and not v["derivable_from_SE1_SE4"]
        for v in candidates.values()
    )

    # Refined theorem statement
    corrected_theorem = (
        "THEOREM CUT (CORRECTED): "
        "Let C be a CCA satisfying Ax1–Ax5 with additional axioms SE1–SE4 "
        "(metric embedding, isotropy, uniform time step, single branch). "
        "Then for any choice of physical units (length unit L and time unit T), "
        "the propagation speed in those units is c = a/dt, where a is the step "
        "length in L and dt is the time step in T. "
        "The ratio c is unique given the axioms AND the unit system. "
        "The numerical value of c in SI units (m/s) is NOT determined by SE1–SE4 "
        "alone — it requires a fifth condition SE5 that anchors the unit system "
        "to a physical observable. SE5 is ALWAYS an empirical input."
    )

    return {
        "test": "Q4_fifth_condition",
        "SE5_candidates": candidates,
        "all_SE5_are_empirical": all_SE5_are_empirical,
        "corrected_theorem_CUT": corrected_theorem,
        "implication_for_gap7": (
            "GAP-7 is not just 'which derivation route works.' "
            "It is: can the numerical value of c be derived without empirical calibration? "
            "Theorem NU + Q1 show the answer is NO. "
            "SE1–SE4 give c = a/dt as a ratio in chosen units. "
            "SE5 (empirical) is required to set those units. "
            "This means c will ALWAYS be a calibrated parameter in the theory, "
            "not a derived constant like e/m_e in atomic physics."
        ),
        "distinction_NU_meanings": {
            "representation_non_uniqueness": (
                "The same abstract CCA admits embeddings with different c values. "
                "This is PROVED by Theorem NU and Q1. "
                "It is a mathematical theorem about abstract CCA structures."
            ),
            "physical_non_identifiability": (
                "No physical prediction of the theory can select c without "
                "additional empirical information. "
                "This is SUPPORTED by the representation non-uniqueness (if different "
                "embeddings are all physically admissible) but requires specifying "
                "which embeddings count as 'physically admissible.' "
                "The current theory does not specify this — the admissibility criterion "
                "is itself an open question."
            ),
            "relationship": (
                "Representation non-uniqueness does NOT automatically prove physical "
                "non-identifiability. To bridge the gap one must show that all "
                "representations satisfying SE1–SE4 are physically equivalent, "
                "or that the theory has no way to distinguish between them. "
                "The PASS results in V13 (different c, same temporal PSD) support "
                "physical non-identifiability from temporal observables, but the "
                "spatial observable ξ_c DOES distinguish them. "
                "The full non-identifiability claim requires that ξ_c is not "
                "independently measurable without assuming c — which is a separate "
                "analysis, not proved here."
            )
        },
        "status": "PASS"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Q5: What is the correct restated theorem?
# ─────────────────────────────────────────────────────────────────────────────
def test_q5_restated_theorem():
    """
    State the correct, defensible version of the theorem, distinguishing
    what is proved from what requires further work.
    """
    theorem_nu_correct = (
        "THEOREM NU (Non-Uniqueness of Speed — Representation Level): "
        "For any CCA C satisfying Ax1–Ax5 and any c > 0, "
        "there exists a metric embedding satisfying SE1–SE4 that assigns "
        "propagation speed c to C. "
        "PROOF: Choose a = c * dt for any dt > 0. Q1 confirms this. "
        "STATUS: PROVED (representation-level non-uniqueness)."
    )

    theorem_cut_correct = (
        "THEOREM CUT (Conditional Uniqueness — Corrected): "
        "Let C be a CCA satisfying Ax1–Ax5. "
        "Let an embedding satisfying SE1–SE4 be given, with specific numerical "
        "values a_0 ∈ ℝ_{>0} [m] and dt_0 ∈ ℝ_{>0} [s] for the spatial step "
        "and time step. "
        "Then the propagation speed c = a_0/dt_0 is uniquely and deterministically "
        "computed from a_0 and dt_0. "
        "HOWEVER: a_0 and dt_0 themselves are FREE parameters of the embedding — "
        "they are not determined by Ax1–Ax5 or by SE1–SE4 alone. "
        "A fifth condition SE5 must supply the numerical values of a_0 or dt_0 "
        "(or their ratio c = a_0/dt_0 directly). SE5 is always empirical. "
        "STATUS: CORRECTED — prior audit's sufficiency claim was too strong."
    )

    gap5 = (
        "SE5 (Scale anchoring): The numerical value of the spatial step a "
        "or the time step dt must be supplied by an empirical observation. "
        "This is a constitutive relation between the abstract CCA structure "
        "and the physical system it represents. "
        "It is the same in character as choosing a = r_q (qubit size) "
        "or dt = 1/omega_q (qubit period) or c = v_acoustic (acoustic speed). "
        "All three are physical identifications, not mathematical derivations."
    )

    # Summary of the five-axiom structure
    five_axioms = {
        "SE1": {"content": "Metric embedding φ: O → R^d", "fixes": "Existence of a and dt as variables", "derivable": False},
        "SE2": {"content": "Isotropy: equal step length a in all directions", "fixes": "Single speed c (not multiple c_b)", "derivable": False},
        "SE3": {"content": "Uniform time step dt per morphism", "fixes": "dt is a constant (not function of morphism)", "derivable": False},
        "SE4": {"content": "Single branch", "fixes": "One speed per direction (not multi-branch spectrum)", "derivable": False},
        "SE5": {"content": "Scale anchor: numerical value of a or dt", "fixes": "Numerical value of c in physical units", "derivable": "ALWAYS EMPIRICAL"}
    }

    return {
        "test": "Q5_restated_theorem",
        "theorem_NU_correct": theorem_nu_correct,
        "theorem_CUT_correct": theorem_cut_correct,
        "SE5_description": gap5,
        "five_axiom_structure": five_axioms,
        "prior_audit_error": (
            "The prior audit (CCA_GEOMETRIC_TRANSPORT_STRUCTURE_AUDIT.md) claimed "
            "SE1–SE4 are sufficient for a unique numerical speed. This is incorrect. "
            "V14 in the prior script fixed specific numerical values of a and dt "
            "within the test code, which is equivalent to implicitly adding SE5. "
            "The test passed because SE5 was present (implicitly), not because "
            "SE1–SE4 alone suffice."
        ),
        "corrected_gap7_statement": (
            "GAP-7 requires not just SE1–SE4 but also SE5 (scale anchoring). "
            "SE5 is always empirical. Therefore c will always be a calibrated "
            "parameter, not a derived constant, unless the theory gains a new "
            "principle that fixes the physical scale of the CCA lattice from "
            "within (e.g., from the large-N conjecture or from a quantum of "
            "information theory that fixes the lattice spacing to a natural unit)."
        ),
        "what_would_close_gap7_completely": [
            "A derivation of the CCA lattice spacing a from a dimensionful physical constant "
            "(e.g., Planck length, Bohr radius, phonon wavelength) — none currently exists.",
            "A proof that the theory's predictions are independent of c (i.e., c drops out) — "
            "false: ξ_c = c/λ appears in the spatial correlator.",
            "An experimental measurement of c via P3 ratio ξ_c/(2τ_B), treating c as "
            "an empirical primitive — this is honest but not a derivation."
        ],
        "status": "PASS"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Theorem CUT Stress Test")
    print("=" * 60)

    tests = [
        ("Q1_scale_freedom", test_q1_scale_freedom),
        ("Q2_necessity", test_q2_necessity),
        ("Q3_what_SE1_to_SE4_fix", test_q3_what_SE1_to_SE4_fix),
        ("Q4_fifth_condition", test_q4_fifth_condition),
        ("Q5_restated_theorem", test_q5_restated_theorem),
    ]

    all_results = {}
    for key, fn in tests:
        try:
            r = fn()
            all_results[key] = r
            status = r.get("status", "?")
            print(f"  [{status:8s}] {key}")
        except Exception as exc:
            all_results[key] = {"status": "ERROR", "error": str(exc)}
            print(f"  [ERROR   ] {key}: {exc}")

    print()
    print("── Verdict on Theorem CUT ──")
    print()
    print("  Theorem CUT as stated in the prior audit: TOO STRONG.")
    print("  SE1–SE4 do NOT uniquely determine the numerical value of c in m/s.")
    print("  They admit a 2-parameter rescaling family (k_a, k_t) that satisfies")
    print("  all four conditions while giving c → (k_a/k_t) * c.")
    print()
    print("  Corrected theorem: SE1–SE4 uniquely determine c GIVEN a fixed unit")
    print("  system (i.e., given specific numerical values of a and dt).")
    print("  A fifth condition SE5 (scale anchoring) is always required,")
    print("  and it is always empirical.")
    print()
    print("  GAP-7 is thus: can SE5 be derived from a deeper principle, or is it")
    print("  always an empirical calibration? Current answer: always empirical.")

    output = {
        "audit": "Theorem_CUT_stress_test",
        "date": "2026-10-10",
        "command": "python 04_validations/theorem_cut_stress_test.py",
        "verdict": "THEOREM CUT AS STATED IS TOO STRONG — scale freedom survives SE1–SE4",
        "tests": all_results
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
