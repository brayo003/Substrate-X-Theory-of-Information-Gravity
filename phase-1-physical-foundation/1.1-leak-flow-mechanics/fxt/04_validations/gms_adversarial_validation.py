"""
gms_adversarial_validation.py
=============================

Adversarial validation of GMS (Gapless Minimal-Support Selection).

Purpose:
  Verify elastic-mode speed non-uniqueness in a physically justified 3D
  substrate. Cubic silicon supports one longitudinal and two transverse
  acoustic branches for each propagation direction, all gapless in the
  long-wavelength elastic limit.

Scope limit:
  This calculation does not independently establish GMS distinguishability,
  minimal support, or a microscopic PRW reversal process. Those are separate
  analytical/kinetic assumptions. It verifies distinct elastic eigenmodes and
  their unequal long-wavelength speeds.

The script uses the Christoffel equation for a cubic elastic medium:

    Gamma_ij(n) u_j = rho v^2 u_i

with standard room-temperature silicon constants. The result is a constructive
counterexample to uniqueness for GMS as stated.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


OUT = Path("04_validations/outputs")
OUT.mkdir(parents=True, exist_ok=True)


def christoffel_cubic(n: np.ndarray, c11: float, c12: float, c44: float) -> np.ndarray:
    """Christoffel matrix for cubic symmetry in Voigt constants."""
    l, m, p = n
    return np.array(
        [
            [c11 * l * l + c44 * (m * m + p * p), (c12 + c44) * l * m, (c12 + c44) * l * p],
            [(c12 + c44) * l * m, c11 * m * m + c44 * (l * l + p * p), (c12 + c44) * m * p],
            [(c12 + c44) * l * p, (c12 + c44) * m * p, c11 * p * p + c44 * (l * l + m * m)],
        ],
        dtype=float,
    )


def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm == 0:
        raise ValueError("zero direction")
    return v / norm


def classify_mode(eigenvector: np.ndarray, n: np.ndarray) -> str:
    alignment = abs(float(np.dot(eigenvector, n)))
    return "LA" if alignment > 0.8 else "TA"


def prw_equation(branch: str, direction: str, speed: float) -> dict:
    return {
        "branch": branch,
        "direction": direction,
        "speed_m_per_s": speed,
        "right_left_mapping": [
            f"d n_+ / dt + {speed:.3f} d n_+ / ds = -gamma (n_+ - n_-)",
            f"d n_- / dt - {speed:.3f} d n_- / ds = +gamma (n_+ - n_-)",
        ],
        "telegrapher_speed": speed,
    }


def main() -> int:
    # Silicon, approximate room-temperature elastic constants.
    # Units: Pa and kg/m^3.
    constants = {
        "C11_GPa": 165.7,
        "C12_GPa": 63.9,
        "C44_GPa": 79.6,
        "rho_kg_m3": 2330.0,
    }
    c11 = constants["C11_GPa"] * 1e9
    c12 = constants["C12_GPa"] * 1e9
    c44 = constants["C44_GPa"] * 1e9
    rho = constants["rho_kg_m3"]

    directions = {
        "[100]": np.array([1.0, 0.0, 0.0]),
        "[110]": np.array([1.0, 1.0, 0.0]),
        "[111]": np.array([1.0, 1.0, 1.0]),
        "generic_[123]": np.array([1.0, 2.0, 3.0]),
    }

    rows = []
    candidate_modes = []
    for label, raw in directions.items():
        n = normalize(raw)
        gamma = christoffel_cubic(n, c11, c12, c44)
        eigvals, eigvecs = np.linalg.eigh(gamma)
        order = np.argsort(eigvals)
        transverse_index = 0
        for idx in order:
            speed = float(np.sqrt(eigvals[idx] / rho))
            vec = eigvecs[:, idx]
            family = classify_mode(vec, n)
            if family == "LA":
                branch = "LA"
            else:
                transverse_index += 1
                branch = f"TA{transverse_index}"
            mode = {
                "direction": label,
                "branch": branch,
                "speed_m_per_s": speed,
                "gapless_in_elastic_limit": speed > 0.0,
                "distinguishability_status": "NOT_TESTED_BY_EIGENVALUE_CALCULATION",
                "minimal_support_status": "NOT_TESTED_BY_EIGENVALUE_CALCULATION",
                "prw_mapping_status": "CONDITIONAL_BRANCH_RESOLVED_KINETIC_ASSUMPTION",
                "polarization_alignment_abs": abs(float(np.dot(vec, n))),
            }
            rows.append(mode)
            candidate_modes.append(mode)

    speeds = [m["speed_m_per_s"] for m in candidate_modes]
    unique_speeds = sorted({round(v, 6) for v in speeds})

    # Counterexample: for a generic direction TA1 and LA are non-degenerate,
    # distinct gapless minimal sectors with different velocities.
    counterexample = [
        m
        for m in candidate_modes
        if m["direction"] == "generic_[123]" and m["branch"] in {"TA1", "LA"}
    ]
    # Keep the selected non-degenerate transverse and longitudinal branches.
    picked = []
    seen = set()
    for m in counterexample:
        if m["branch"] not in seen:
            picked.append(m)
            seen.add(m["branch"])

    if len(picked) != 2 or not all(m["gapless_in_elastic_limit"] for m in picked):
        raise RuntimeError("selected sectors are not distinct gapless elastic branches")
    if np.isclose(picked[0]["speed_m_per_s"], picked[1]["speed_m_per_s"]):
        raise RuntimeError("counterexample sectors do not have distinct speeds")

    max_speed = max(speeds)
    min_speed = min(speeds)
    tau_reference_s = 1e-6

    prw_maps = [
        prw_equation(m["branch"], m["direction"], m["speed_m_per_s"])
        for m in picked
    ]

    result = {
        "constants": constants,
        "operational_gms_tests": {
            "gapless": "omega_b(k) = v_b(n)|k| + O(k^2), so omega_b(0)=0",
            "distinguishability": "NOT TESTED: requires a coarse-grained observable map",
            "minimal_support": "NOT TESTED: requires a branch-resolved kinetic closure",
            "prw_mapping": "NOT DERIVED: requires reciprocal branch-preserving scattering",
        },
        "mode_count_tested": len(candidate_modes),
        "gapless_elastic_mode_count": sum(m["gapless_in_elastic_limit"] for m in candidate_modes),
        "unique_speed_count": len(unique_speeds),
        "speed_range_m_per_s": [min_speed, max_speed],
        "coherence_length_at_tau_1us_mm": [
            2 * min_speed * tau_reference_s * 1e3,
            2 * max_speed * tau_reference_s * 1e3,
        ],
        "modes": rows,
        "counterexample": picked,
        "prw_maps_for_counterexample": prw_maps,
        "verdict": "ELASTIC_MODE_SPEED_NONUNIQUENESS",
        "bound_audit": {
            "derived_from_elasticity": f"branch speeds lie in [{min_speed:.3f}, {max_speed:.3f}] m/s for sampled directions",
            "not_derived_from_gms": "c <= v_s requires an independent definition of v_s as a maximum admissible signal speed",
            "recommended_bound": "c <= v_max, where v_max is the maximum group/front speed over all allowed branches and directions",
        },
    }

    out_path = OUT / "gms_adversarial_validation.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("GMS adversarial validation")
    print("==========================")
    print(f"Gapless elastic sectors tested: {len(candidate_modes)}")
    print(f"Unique speeds among tested sectors: {len(unique_speeds)}")
    print(f"Speed range: {min_speed:.3f} m/s to {max_speed:.3f} m/s")
    print("Counterexample sectors:")
    for m in picked:
        print(
            f"  {m['direction']} {m['branch']}: "
            f"v={m['speed_m_per_s']:.3f} m/s, "
            f"alignment={m['polarization_alignment_abs']:.3f}"
        )
    print(f"Verdict: {result['verdict']}")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
