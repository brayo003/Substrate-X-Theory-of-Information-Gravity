#!/usr/bin/env python3
"""Minimal quick-start script for Substrate X.

Runs a very short 2D single-star simulation using the main SubstrateXSolver
implementation in verification/src/new_num_solv.py, without plotting or
analysis. Its only job is to demonstrate that the solver imports and runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Locate solver implementation
REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "verification" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from new_num_solv import SubstrateXSolver  # type: ignore  # noqa: E402


def main() -> None:
    # Small grid and very short run for a fast sanity check
    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=2e12,
        dim=2,
        tau=1e3,
        alpha=1e-10,
        beta=1e-10,
        gamma=1e-10,
        chi=1e7,
    )

    # Single solar-mass point at the origin
    solver.add_point_mass(1.0 * solver.M_sun, (0.0, 0.0))

    # Short, non-interactive run (no plots, no analysis files)
    solver.simulate(
        n_steps=100,
        plot_interval=10_000,
        enable_plots=False,
        analyze=False,
    )

    print("[quick_start] SubstrateXSolver import + short run completed.")


if __name__ == "__main__":
    main()
