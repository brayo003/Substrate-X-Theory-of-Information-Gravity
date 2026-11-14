"""Test candidate elastic-mode couplings against the existing C2 interaction.

The existing C2 coupling is H_int = g J_C2(x_q, t) sigma_z.  C2 does not
define J_C2 as a function of a silicon displacement field u, so that coupling
alone has no calculable Christoffel-mode matrix elements.

This script records that obstruction and evaluates a separate, explicitly
conditional completion: a scalar dilatational observable B = kappa div(u).
For a plane-wave eigenmode u = e_b q_b exp(i k n dot x), its coupling amplitude
is proportional to n dot e_b.  This tests whether scalar-density coupling
eliminates transverse branches in anisotropic cubic silicon.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


OUT = Path("04_validations/outputs")
OUT.mkdir(parents=True, exist_ok=True)


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        raise ValueError("zero direction")
    return vector / norm


def christoffel_cubic(n: np.ndarray, c11: float, c12: float, c44: float) -> np.ndarray:
    l, m, p = n
    return np.array(
        [
            [c11 * l * l + c44 * (m * m + p * p), (c12 + c44) * l * m, (c12 + c44) * l * p],
            [(c12 + c44) * l * m, c11 * m * m + c44 * (l * l + p * p), (c12 + c44) * m * p],
            [(c12 + c44) * l * p, (c12 + c44) * m * p, c11 * p * p + c44 * (l * l + m * m)],
        ],
        dtype=float,
    )


def branch_name(eigenvector: np.ndarray, n: np.ndarray, transverse_index: int) -> tuple[str, int]:
    if abs(float(np.dot(eigenvector, n))) > 0.8:
        return "LA", transverse_index
    transverse_index += 1
    return f"TA{transverse_index}", transverse_index


def modes_for_direction(
    label: str, raw_direction: np.ndarray, c11: float, c12: float, c44: float, rho: float
) -> list[dict]:
    n = normalize(raw_direction)
    eigenvalues, eigenvectors = np.linalg.eigh(christoffel_cubic(n, c11, c12, c44))
    transverse_index = 0
    modes = []
    for index in np.argsort(eigenvalues):
        eigenvector = eigenvectors[:, index]
        branch, transverse_index = branch_name(eigenvector, n, transverse_index)
        longitudinal_amplitude = abs(float(np.dot(n, eigenvector)))
        modes.append(
            {
                "direction": label,
                "branch": branch,
                "speed_m_per_s": float(np.sqrt(eigenvalues[index] / rho)),
                "polarization_alignment_abs": longitudinal_amplitude,
                "scalar_dilatation_weight": longitudinal_amplitude**2,
            }
        )
    return modes


def main() -> int:
    constants = {"C11_GPa": 165.7, "C12_GPa": 63.9, "C44_GPa": 79.6, "rho_kg_m3": 2330.0}
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
    modes = [
        mode
        for label, direction in directions.items()
        for mode in modes_for_direction(label, direction, c11, c12, c44, rho)
    ]
    generic = [mode for mode in modes if mode["direction"] == "generic_[123]"]
    coupled_generic = [mode for mode in generic if mode["scalar_dilatation_weight"] > 1e-12]
    transverse_leakage = [mode for mode in generic if mode["branch"].startswith("TA")]

    if len(coupled_generic) != 3:
        raise RuntimeError("unexpected scalar-dilatation coupling classification")
    if not all(mode["scalar_dilatation_weight"] > 1e-12 for mode in transverse_leakage):
        raise RuntimeError("generic transverse leakage unexpectedly vanished")

    result = {
        "existing_c2_interaction": {
            "operator": "H_int = g J_C2(x_q,t) sigma_z",
            "status": "J_C2_TO_ELASTIC_FIELD_MAP_ABSENT",
            "consequence": "existing assumptions do not determine any branch matrix element",
        },
        "conditional_completion": {
            "new_assumption": "B(x,t) = kappa div(u(x,t)) replaces the unspecified C2 current observable",
            "plane_wave_matrix_element": "B_b proportional to i k kappa (n dot e_b) q_b",
            "weight": "w_b(n) = |n dot e_b(n)|^2",
            "status": "NEW_CONSTITUTIVE_IDENTIFICATION_NOT_DERIVED_FROM_C2",
        },
        "constants": constants,
        "modes": modes,
        "generic_direction_result": {
            "direction": "[123]",
            "coupled_branches": coupled_generic,
            "transport_outcome": "MULTIPLE_SPEEDS",
            "reason": "both transverse weights are nonzero in anisotropic cubic silicon",
        },
        "high_symmetry_result": {
            "result": "transverse scalar-dilatation weights vanish only on sampled high-symmetry directions",
            "interpretation": "longitudinal-only coupling is geometry-dependent, not an exact material-wide selection",
        },
        "verdict": "NO_UNIQUE_C_FROM_EXISTING_COUPLING; CONDITIONAL_SCALAR_COMPLETION_HAS_GENERIC_TRANSVERSE_LEAKAGE",
    }

    output = OUT / "coupling_mode_audit.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Coupling-mode audit")
    print("===================")
    print("Existing C2 current-to-elastic map: absent")
    print("Conditional scalar-dilatation weights for generic [123]:")
    for mode in generic:
        print(
            f"  {mode['branch']}: v={mode['speed_m_per_s']:.3f} m/s, "
            f"w={mode['scalar_dilatation_weight']:.8f}"
        )
    print("Effective result: MULTIPLE_SPEEDS")
    print(f"Verdict: {result['verdict']}")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
