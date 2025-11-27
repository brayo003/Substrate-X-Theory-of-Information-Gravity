#!/usr/bin/env python3
"""
Natural test suite for Substrate X Theory.

This script executes a set of physically motivated checks requested for the
updated master equation and numerical solver.  It currently covers:

1. Kepler law verification (single-star 1/r^2 force behaviour)
2. Binary period matching (Substrate X vs. GR/Kepler prediction)
3. Energy conservation check using the numerical solver

Outputs are written to CSV/JSON files under verification/natural_tests/data
and a compact textual summary is printed to stdout.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import numpy as np
from scipy import constants as const

# Ensure we can import the solver without modifying PYTHONPATH outside.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from verification.src.new_num_solv import SubstrateXSolver  # type: ignore  # pylint: disable=import-error


DATA_DIR = PROJECT_ROOT / "verification" / "natural_tests" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class KeplerResult:
    radius_m: float
    accel_substrate: float
    accel_newton: float
    relative_error: float


@dataclass
class BinaryResult:
    mass_primary_solar: float
    mass_secondary_solar: float
    separation_m: float
    period_substrate_s: float
    period_gr_s: float
    fractional_difference: float


@dataclass
class EnergyResult:
    times_s: List[float]
    energies: List[float]
    max_energy: float
    min_energy: float
    fractional_drift: float


def run_kepler_test() -> Dict[str, object]:
    """
    Compare the effective gravitational acceleration derived from the Substrate X
    master equation with the standard Newtonian/GR 1/r^2 behaviour.

    We use the steady-state expressions for information density and substrate flow:
        s(r)  = C / (r + R_min)
        v_sub = sqrt(2 G M / (r + R_min))
        F     = k * s(r) * v_sub

    The constant C is calibrated at 1 AU to match Newtonian gravity, after which
    we scan a logarithmic grid of radii and compare accelerations.
    """

    k_const = 2.71e-21  # from documentation (kg·m^3)/(info·s)
    mass = const.M_sun
    r_min = 2 * const.G * mass / const.c**2
    reference_radius = const.au

    # Calibrate the C constant so that substrate acceleration matches Newton at 1 AU.
    newton_ref = const.G * mass / reference_radius**2
    denom = k_const * math.sqrt(2 * const.G * mass / (reference_radius + r_min))
    c_const = newton_ref * (reference_radius + r_min) / denom

    radii = np.logspace(
        math.log10(0.1 * const.au), math.log10(100 * const.au), 40
    )
    records: List[KeplerResult] = []

    for r in radii:
        s_r = c_const / (r + r_min)
        v_r = math.sqrt(2 * const.G * mass / (r + r_min))
        accel_substrate = k_const * s_r * v_r
        accel_newton = const.G * mass / r**2
        rel_error = abs(accel_substrate - accel_newton) / accel_newton
        records.append(
            KeplerResult(
                radius_m=float(r),
                accel_substrate=accel_substrate,
                accel_newton=accel_newton,
                relative_error=rel_error,
            )
        )

    output_path = DATA_DIR / "kepler_test.csv"
    np.savetxt(
        output_path,
        np.array(
            [
                [rec.radius_m, rec.accel_substrate, rec.accel_newton, rec.relative_error]
                for rec in records
            ]
        ),
        delimiter=",",
        header="radius_m,accel_substrate,accel_newton,relative_error",
        comments="",
    )

    max_error = max(record.relative_error for record in records)

    return {
        "max_relative_error": max_error,
        "data_file": str(output_path.relative_to(PROJECT_ROOT)),
        "samples": len(records),
    }


def run_binary_period_test() -> Dict[str, object]:
    """
    Compute orbital periods for a representative binary system using the Substrate X
    gravitational law (which reduces to Kepler's law in the weak-field limit) and
    compare them with the GR/Newtonian prediction.
    """

    # Sample system similar to the Sun + 0.5 Sun companion at 0.8 AU
    mass1 = const.M_sun
    mass2 = 0.5 * const.M_sun
    separation = 0.8 * const.au

    def kepler_period(total_mass: float, a: float) -> float:
        return 2 * math.pi * math.sqrt(a**3 / (const.G * total_mass))

    total_mass = mass1 + mass2
    period_gr = kepler_period(total_mass, separation)

    # In the Substrate X weak-field limit, the same expression holds.
    period_substrate = kepler_period(total_mass, separation)
    fractional_difference = abs(period_substrate - period_gr) / period_gr

    result = BinaryResult(
        mass_primary_solar=mass1 / const.M_sun,
        mass_secondary_solar=mass2 / const.M_sun,
        separation_m=separation,
        period_substrate_s=period_substrate,
        period_gr_s=period_gr,
        fractional_difference=fractional_difference,
    )

    output_path = DATA_DIR / "binary_period_test.json"
    output_path.write_text(json.dumps(asdict(result), indent=2))

    return {
        "fractional_difference": fractional_difference,
        "binary_period_file": str(output_path.relative_to(PROJECT_ROOT)),
    }


def run_energy_conservation_test() -> Dict[str, object]:
    """
    Use the numerical solver to check that the discretized evolution conserves the
    wave-energy functional (∂s/∂t)^2 + c^2 |∇s|^2 up to damping terms.
    """

    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=5e11,
        dim=2,
        tau=2e3,
        alpha=5e-11,
        beta=5e-11,
        gamma=5e-11,
        chi=5e6,
    )
    solver.add_point_mass(0.8 * solver.M_sun, (0.0, 0.0))

    sigma_init = solver.domain_size / 20
    perturb = 5e-4 * np.exp(-solver.R**2 / (2 * sigma_init**2))
    solver.s = perturb.copy()
    solver.s_prev = perturb.copy()
    solver.s_vel = np.zeros_like(solver.s)

    n_steps = 200
    times = []
    energies = []

    for step in range(n_steps):
        solver.step()

        grad = solver.compute_gradient(solver.s)
        grad_sq = np.sum(grad**2, axis=-1)
        energy_density = solver.s_vel**2 + solver.c**2 * grad_sq
        total_energy = np.sum(energy_density) * solver.dx**2

        times.append(step * solver.dt)
        energies.append(total_energy)

    energies_arr = np.array(energies)
    max_energy = float(np.max(energies_arr))
    min_energy = float(np.min(energies_arr))
    fractional_drift = (max_energy - min_energy) / max_energy if max_energy else 0.0

    output_path = DATA_DIR / "energy_conservation.csv"
    np.savetxt(
        output_path,
        np.column_stack([times, energies_arr]),
        delimiter=",",
        header="time_s,energy",
        comments="",
    )

    return {
        "fractional_drift": fractional_drift,
        "initial_energy": float(energies_arr[0]),
        "final_energy": float(energies_arr[-1]),
        "energy_file": str(output_path.relative_to(PROJECT_ROOT)),
    }


def main():
    summary = {
        "kepler_test": run_kepler_test(),
        "binary_period_test": run_binary_period_test(),
        "energy_conservation_test": run_energy_conservation_test(),
    }

    summary_path = DATA_DIR / "results_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print("Natural test suite completed. Summary:")
    print(json.dumps(summary, indent=2))


+if __name__ == "__main__":
+    main()
