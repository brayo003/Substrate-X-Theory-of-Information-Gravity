#!/usr/bin/env bash
set -e

# Run from the repository root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Mercury perihelion precession
python github/validation/solar_system/mercury_precession_fit.py

# Binary pulsar orbital decay
python github/validation/binary_tests/binary_pulsar_decay_test.py

# Single galaxy rotation-curve run
python github/galaxy_simulations/galaxy_scale_sim.py --m-star 1e11 --r-eff 4 --k-eff 0.1
