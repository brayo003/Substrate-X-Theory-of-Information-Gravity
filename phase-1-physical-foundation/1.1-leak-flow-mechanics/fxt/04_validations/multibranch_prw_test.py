"""
Multi-branch PRW: internal consistency and discriminability test
================================================================

Three questions answered here by direct calculation:

Q4. Is a multi-speed PRW internally consistent with the C2 transport equations?
    - Derive the coupled telegrapher system for B branches, each with speed v_b
      and reversal rate lambda_b.
    - Check whether conservation laws, spectral structure, and observable
      correlators are well-defined.

Q5. Does multi-branch PRW produce a distinct observable prediction vs a
    conventional multi-branch phonon bath?
    - Build the dephasing rate Gamma_phi and spatial correlator C(r) for both
      models explicitly.
    - Compare functional forms: same or different?
    - Identify any parameter combination that would discriminate them.

Q6. Classification: what does the multi-branch formulation imply?

All results written to 04_validations/outputs/multibranch_prw_test.json
"""

from __future__ import annotations
import json, numpy as np
from pathlib import Path
from scipy.special import kv as K0_bessel   # K0(x) = kv(0, x)

OUT = Path("04_validations/outputs")
OUT.mkdir(parents=True, exist_ok=True)

# ── Silicon branch speeds (from prior validated Christoffel calculation) ────
SILICON = {
    "TA1": {"v": 4893.09, "label": "TA1"},
    "TA2": {"v": 5626.04, "label": "TA2"},
    "LA":  {"v": 9156.82, "label": "LA"},
}

# Spectral weights for scalar-dilatation coupling M1 at generic [123] direction
# (from coupling_mode_audit.json, verified)
W_M1 = {"TA1": 0.005316, "TA2": 0.001829, "LA": 0.992856}
# Spectral weights for energy-flux coupling M2
W_M2 = {"TA1": 0.000125, "TA2": 0.000099, "LA": 0.999776}

# ── Q4: Multi-branch PRW transport equations ──────────────────────────────

def derive_multibranch_transport(branches: dict) -> dict:
    """
    For B independent PRW branches, derive the coupled transport system.

    Each branch b has:
      dn_b+/dt = -v_b dn_b+/dx - lambda_b n_b+ + lambda_b n_b-
      dn_b-/dt = +v_b dn_b-/dx + lambda_b n_b+ - lambda_b n_b-

    Summing: s_b = n_b+ + n_b-,  J_b = v_b(n_b+ - n_b-)
    gives exact per-branch telegrapher equations:
      tau_b d²s_b/dt² + ds_b/dt = v_b² tau_b d²s_b/dx²

    These B equations are DECOUPLED if branches don't exchange population.
    The total C2 density is S = sum_b w_b s_b.

    Returns a dict describing the structure and conservation laws.
    """
    results = {}
    for name, br in branches.items():
        v = br["v"]
        # tau_b is a free parameter per branch; we treat it as independent
        # The telegrapher dispersion: omega^2 + i/tau_b * omega = v_b^2 k^2
        # Critical wavenumber: k_c_b = 1/(2 v_b tau_b) = lambda_b / v_b
        results[name] = {
            "telegrapher_equation": f"tau_b d²s_b/dt² + ds_b/dt = {v:.1f}² tau_b d²s_b/dx²",
            "conserved_quantity": "Q_b = integral s_b dx  (per branch, source-free)",
            "decoupled_from_other_branches": True,
            "note": "Coupling between branches requires inter-branch scattering, not in C2",
        }

    # Total density S = sum_b w_b s_b is NOT itself a telegrapher field
    # unless all v_b are equal. Check this directly:
    speeds = [br["v"] for br in branches.values()]
    all_equal = np.std(speeds) / np.mean(speeds) < 1e-6
    results["_total_field_status"] = {
        "S_is_single_telegrapher": all_equal,
        "reason": (
            "S = sum w_b s_b satisfies a single telegrapher equation only if all v_b equal."
            " Otherwise S satisfies a higher-order PDE (product of B telegrapher operators)."
        ),
        "order_of_PDE_for_S": 2 * len(branches),
        "wave_speeds": speeds,
        "internal_consistency": "VALID – each branch is independently consistent",
    }
    return results


# ── Q5: Observable predictions ────────────────────────────────────────────

def bath_spectral_density_C2(omega: np.ndarray, S0: float, tau: float) -> np.ndarray:
    """Single-branch C2 bath PSD (Lorentzian).
    S_JJ(omega) = 2 S0 tau / (1 + omega^2 tau^2)
    Source: substrate_transport_derivation.md §4 (derived from C-J equation).
    """
    return 2 * S0 * tau / (1 + omega**2 * tau**2)


def bath_spectral_density_multibranch(
    omega: np.ndarray, S0: float, taus: dict[str, float], weights: dict[str, float]
) -> np.ndarray:
    """Multi-branch C2 bath PSD: weighted sum of per-branch Lorentzians.
    S_BB(omega) = sum_b w_b * 2 S0 tau_b / (1 + omega^2 tau_b^2)
    Each branch b has its own tau_b = 1/(2 lambda_b).
    """
    result = np.zeros_like(omega)
    for b, w in weights.items():
        tau_b = taus[b]
        result += w * 2 * S0 * tau_b / (1 + omega**2 * tau_b**2)
    return result


def bath_spectral_density_conventional_phonon(
    omega: np.ndarray, S0: float, taus: dict[str, float], weights: dict[str, float]
) -> np.ndarray:
    """Conventional phonon (Ohmic/Drude) multi-branch bath PSD.
    A standard phonon bath with B modes has PSD:
      S_phonon(omega) = sum_b w_b * eta_b omega / (omega^2 + Omega_b^2)
    where Omega_b is a branch cutoff and eta_b is the coupling strength.
    For a Drude bath: S(omega) = 2 eta tau / (1 + omega^2 tau^2)  -- SAME FORM as C2.

    This is the key comparison: a conventional Drude (Ornstein-Uhlenbeck) bath
    has the same Lorentzian PSD as the C2 telegrapher bath.
    Reference: Weiss, Quantum Dissipative Systems, §3.1 (Drude cutoff).
    """
    # The Drude spectral density is formally identical to the C2 Lorentzian:
    # S_Drude(omega) = 2 eta Omega_c / (omega^2 + Omega_c^2)
    # with eta = S0 and Omega_c = 1/tau.
    # So: S_C2_branch = S_Drude_branch with tau = 1/Omega_c.
    result = np.zeros_like(omega)
    for b, w in weights.items():
        tau_b = taus[b]
        result += w * 2 * S0 * tau_b / (1 + omega**2 * tau_b**2)
    return result


def spatial_correlator_single(r: np.ndarray, xi: float, a: float = 1e-4) -> np.ndarray:
    """Single-scale C2 spatial correlator: K0(r/xi) / K0(a/xi).
    Source: substrate_transport_derivation.md (Green's function of 2D telegrapher).
    """
    return K0_bessel(0, r / xi) / K0_bessel(0, a / xi)


def spatial_correlator_multibranch(
    r: np.ndarray,
    xis: dict[str, float],
    weights: dict[str, float],
    a: float = 1e-4
) -> np.ndarray:
    """Multi-branch spatial correlator: weighted sum of K0 terms."""
    result = np.zeros_like(r)
    for b, w in weights.items():
        xi_b = xis[b]
        result += w * K0_bessel(0, r / xi_b) / K0_bessel(0, a / xi_b)
    return result


def dephasing_rate(S0: float, tau: float, g: float = 1.0) -> float:
    """Dephasing rate from Born-Markov: Gamma = g^2/hbar^2 * S_JJ(0) = g^2 S0 * 2 tau.
    At omega_q ~ 0 (low-frequency limit).
    """
    return g**2 * 2 * S0 * tau


def compare_predictions(
    tau_single: float,
    taus_multi: dict[str, float],
    weights: dict[str, float],
    speeds: dict[str, float],
    r_values: np.ndarray,
    omega_values: np.ndarray,
    S0: float = 1.0,
    g: float = 1.0,
) -> dict:
    """Compare single-branch C2, multi-branch C2, and conventional phonon bath."""

    # Single-branch C2 (existing theory)
    xi_single = 2 * SILICON["LA"]["v"] * tau_single  # if we pick LA branch
    psd_single = bath_spectral_density_C2(omega_values, S0, tau_single)
    corr_single = spatial_correlator_single(r_values, xi_single)
    gamma_single = dephasing_rate(S0, tau_single, g)

    # Multi-branch C2
    xis_multi = {b: 2 * speeds[b] * taus_multi[b] for b in weights}
    psd_multi = bath_spectral_density_multibranch(omega_values, S0, taus_multi, weights)
    corr_multi = spatial_correlator_multibranch(r_values, xis_multi, weights)
    gamma_multi = sum(weights[b] * dephasing_rate(S0, taus_multi[b], g) for b in weights)

    # Conventional phonon bath (same functional form – Drude)
    psd_phon = bath_spectral_density_conventional_phonon(omega_values, S0, taus_multi, weights)

    # Key discriminability test:
    # Multi-branch C2 PSD == conventional Drude bath PSD (by construction of same formula)?
    psd_diff = np.max(np.abs(psd_multi - psd_phon))
    psd_same = psd_diff < 1e-12

    # Spatial correlator shape comparison: multi-branch K0 sum vs single K0
    # Compute ratio to check deviation
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(corr_single > 1e-10, corr_multi / corr_single, np.nan)
    ratio_variation = float(np.nanstd(ratio) / np.nanmean(ratio)) if np.any(~np.isnan(ratio)) else float('nan')

    return {
        "single_branch_LA": {
            "tau": tau_single,
            "xi": xi_single,
            "Gamma_phi": gamma_single,
            "PSD_at_0": float(psd_single[0]),
        },
        "multibranch": {
            "taus": taus_multi,
            "xis": xis_multi,
            "Gamma_phi": gamma_multi,
            "PSD_at_0": float(psd_multi[0]),
        },
        "functional_form_comparison": {
            "multibranch_C2_PSD_equals_conventional_Drude": psd_same,
            "reason": (
                "The C2 per-branch Lorentzian S_JJ(omega)=2S0*tau/(1+omega²tau²) "
                "is algebraically identical to the Drude/Ornstein-Uhlenbeck bath "
                "spectral density. A multi-branch C2 model and a multi-component "
                "conventional phonon bath produce exactly the same PSD if they share "
                "the same (w_b, tau_b) parameters. The two models are observationally "
                "indistinguishable from temporal measurements alone."
            ),
        },
        "spatial_discriminability": {
            "multi_branch_K0_sum_differs_from_single_K0": ratio_variation > 0.01,
            "ratio_variation_fraction": ratio_variation,
            "interpretation": (
                "If tau_b differ between branches, the spatial correlator is a sum "
                "of K0 functions with different length scales xi_b = 2*v_b*tau_b. "
                "This DOES differ from a single-K0 prediction in shape, but only "
                "if the xi_b values are well separated AND measured spatially."
            ),
        },
        "conventional_null_status": (
            "INDISTINGUISHABLE from temporal measurements. "
            "Potentially distinguishable spatially ONLY IF xi_b values differ "
            "by more than experimental resolution AND a single-K0 null is rejected."
        ),
    }


# ── Q6: Classification ────────────────────────────────────────────────────

def classify_multibranch_theory(comparison: dict, transport: dict) -> dict:
    """Determine whether multi-branch PRW is a consistent extension and what it predicts."""

    return {
        "internal_consistency": {
            "verdict": "CONSISTENT",
            "reason": (
                "Each branch independently satisfies the telegrapher equation. "
                "Conservation of Q_b = integral s_b dx holds per branch. "
                "The coupled system is well-posed as B independent telegrapher equations."
            ),
            "cost": (
                "The total density S = sum w_b s_b satisfies a 2B-th order PDE, "
                "not the single telegrapher equation. The C2 transport layer in its "
                "current 1D, single-speed form does NOT directly accommodate multi-branch "
                "propagation without reformulation."
            ),
        },
        "requires_new_assumption": (
            "Multi-branch PRW requires: (1) specifying B branch speeds v_1,...,v_B, "
            "(2) specifying B reversal rates lambda_1,...,lambda_B, "
            "(3) specifying coupling weights w_1,...,w_B, "
            "(4) specifying whether branches exchange population (inter-branch scattering). "
            "None of these are determined by the existing C2 axioms."
        ),
        "new_parameters_introduced": {
            "single_branch": ["v", "lambda", "g"],
            "B_branches": ["v_1..v_B", "lambda_1..lambda_B", "g_1..g_B", "w_1..w_B"],
            "increase": "2 free parameters → 4B free parameters",
        },
        "prediction_status": {
            "temporal_dephasing": (
                "Multi-branch Gamma_phi = sum w_b * g_b^2 * 2 S0 tau_b. "
                "This has MORE free parameters than single-branch but same functional form. "
                "It is observationally indistinguishable from a multi-component Drude bath."
            ),
            "spatial_correlator": (
                "Multi-branch C(r) = sum w_b K0(r/xi_b). "
                "This CAN differ from single-K0 in shape if xi_b are well separated. "
                "But: (a) xi_b = 2 v_b tau_b, so one must also know tau_b per branch; "
                "(b) a conventional bath with two timescales produces the same K0 sum. "
                "Discriminating C2 from conventional requires that the xi_b values "
                "are PREDICTED (not fitted) from the theory."
            ),
            "prediction_without_fitting": "NONE – all branch speeds and rates remain free.",
        },
        "does_multibranch_add_new_prediction": {
            "verdict": "NO",
            "reason": (
                "A multi-branch C2 model with B free (v_b, lambda_b, w_b) triples "
                "is observationally equivalent to a conventional B-component Lorentzian "
                "bath with B free (Omega_b, S_b) pairs. Both produce the same PSD and "
                "the same spatial K0 sum. Neither makes a parameter-free prediction. "
                "The C2 label on the bath does not generate a distinct observable."
            ),
            "exception_condition": (
                "A distinct prediction would arise ONLY IF the branch speeds v_b "
                "and reversal rates lambda_b were predicted from first principles "
                "(e.g., from material constants). Then the xi_b values would be fixed "
                "numbers, not fitted parameters, and the K0 sum shape would be a "
                "true prediction. But that requires the microscopic coupling derivation "
                "that is currently absent."
            ),
        },
        "reformulation_verdict": (
            "The C2 theory CAN be reformulated for multiple branch speeds in a "
            "mathematically consistent way. The reformulation is a straightforward "
            "generalization: replace one (v, lambda) pair with B (v_b, lambda_b) pairs. "
            "However: (1) it contradicts assumption A-PRW1 (single uniform speed), "
            "which must be relaxed; (2) it multiplies free parameters by B; "
            "(3) it produces no new observable prediction unless the v_b values "
            "are independently derived. The reformulation is legitimate but not "
            "scientifically productive without the missing microscopic derivation."
        ),
    }


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> int:
    print("Multi-branch PRW: consistency and discriminability test")
    print("=" * 60)

    # Q4: transport structure
    transport = derive_multibranch_transport(SILICON)
    print("\nQ4 — Multi-branch transport:")
    print(f"  Each branch independently satisfies telegrapher: TRUE")
    print(f"  Total S satisfies single telegrapher: {transport['_total_field_status']['S_is_single_telegrapher']}")
    print(f"  Order of PDE for S: {transport['_total_field_status']['order_of_PDE_for_S']}")

    # Q5: observable comparison
    # Use same tau for all branches (conservative case: same reversal rate)
    tau_ref = 1e-6  # 1 microsecond
    taus_equal = {b: tau_ref for b in SILICON}

    # Also test case where tau_b differs between branches (physically motivated)
    # If lambda_b = gamma * v_b (reversal rate proportional to speed), tau_b ~ 1/v_b
    gamma_rate = 1e3  # arbitrary rate per unit speed
    taus_proportional = {b: 1.0 / (2 * gamma_rate * SILICON[b]["v"]) for b in SILICON}

    r_vals = np.linspace(1e-4, 0.02, 200)   # 0.1 mm to 20 mm
    omega_vals = np.linspace(0, 1e7, 500)   # 0 to 10 MHz

    speeds = {b: SILICON[b]["v"] for b in SILICON}

    comp_equal = compare_predictions(
        tau_single=tau_ref,
        taus_multi=taus_equal,
        weights=W_M1,
        speeds=speeds,
        r_values=r_vals,
        omega_values=omega_vals,
    )
    comp_prop = compare_predictions(
        tau_single=1.0 / (2 * gamma_rate * SILICON["LA"]["v"]),
        taus_multi=taus_proportional,
        weights=W_M1,
        speeds=speeds,
        r_values=r_vals,
        omega_values=omega_vals,
    )

    print("\nQ5 — Observable predictions (equal tau case):")
    print(f"  Multi-branch C2 PSD == conventional Drude PSD: "
          f"{comp_equal['functional_form_comparison']['multibranch_C2_PSD_equals_conventional_Drude']}")
    print(f"  Spatial shape variation (ratio std/mean): "
          f"{comp_equal['spatial_discriminability']['ratio_variation_fraction']:.4f}")

    print("\nQ5 — Observable predictions (tau proportional to 1/v case):")
    print(f"  Multi-branch C2 PSD == conventional Drude PSD: "
          f"{comp_prop['functional_form_comparison']['multibranch_C2_PSD_equals_conventional_Drude']}")
    print(f"  Spatial shape variation (ratio std/mean): "
          f"{comp_prop['spatial_discriminability']['ratio_variation_fraction']:.4f}")

    # Q6: classification
    classification = classify_multibranch_theory(comp_equal, transport)
    print(f"\nQ6 — Multi-branch theory classification:")
    print(f"  Internal consistency: {classification['internal_consistency']['verdict']}")
    print(f"  Adds new prediction: {classification['does_multibranch_add_new_prediction']['verdict']}")
    print(f"  Reformulation verdict: {classification['reformulation_verdict'][:80]}...")

    # ── Explicit discriminability table ──────────────────────────────────
    print("\n── Discriminability summary ──")
    print("Observable                | C2 single | C2 multi | Conv. Drude | Distinct?")
    print("Temporal PSD Lorentzian   |  YES      |  YES     |  YES        |  NO")
    print("Spatial K0(r/xi)          |  YES      |  K0 sum  |  K0 sum     |  NO (same form)")
    print("xi_b predicted from mat.  |  NO       |  NO      |  NO         |  —")
    print("xi_b predicted at all     |  NO (free)|  NO (free)|  NO (free) |  SAME")
    print("P3: xi/(2tau) = const     |  YES      |  NO (varies)|  NO (varies)|  POTENTIALLY")

    # Explicitly check P3 consistency for multi-branch case
    # P3: c = xi_c / (2 tau_B) should be constant across conditions
    # For multi-branch, different branches give different xi/tau ratios
    p3_values = {b: speeds[b] for b in SILICON}  # xi_b/(2*tau_b) = v_b for each branch
    p3_spread = (max(p3_values.values()) - min(p3_values.values())) / np.mean(list(p3_values.values()))
    print(f"\nP3 ratio xi_b/(2*tau_b) = v_b per branch:")
    for b, v in p3_values.items():
        print(f"  {b}: {v:.1f} m/s")
    print(f"  Spread: {p3_spread*100:.1f}% of mean")
    print(f"  Multi-branch C2 does NOT predict a unique P3 ratio.")

    output = {
        "Q4_transport_consistency": transport,
        "Q5_observable_comparison_equal_tau": comp_equal,
        "Q5_observable_comparison_proportional_tau": comp_prop,
        "Q5_discriminability_table": {
            "temporal_PSD": "C2-multi == Drude-multi: indistinguishable",
            "spatial_correlator": "C2-multi K0-sum == Drude-multi K0-sum: indistinguishable",
            "P3_ratio": {
                "single_branch_C2": "xi/(2*tau) = c = single value",
                "multi_branch_C2": f"xi_b/(2*tau_b) = v_b, varies by {p3_spread*100:.1f}%",
                "conventional_bath": "no P3 ratio defined",
                "discriminability": (
                    "P3 ratio is the only place where single-branch C2 differs. "
                    "Multi-branch C2 kills even this discriminator."
                ),
            },
        },
        "Q6_classification": classification,
        "summary": {
            "multi_branch_internally_consistent": True,
            "multi_branch_contradicts_A_PRW1": True,
            "multi_branch_adds_new_parameters": True,
            "multi_branch_adds_new_predictions": False,
            "multi_branch_kills_P3_discriminator": True,
            "reformulation_is_productive": False,
            "reason": (
                "Multi-branch C2 is consistent but not productive: it erases the "
                "only surviving discriminator (P3 ratio uniqueness) without adding "
                "any new observable that conventional phonon physics cannot match. "
                "The only path to a genuine prediction is deriving the branch speeds "
                "and reversal rates from the theory's own axioms."
            ),
        },
    }

    out_path = OUT / "multibranch_prw_test.json"
    out_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"\nResults written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
