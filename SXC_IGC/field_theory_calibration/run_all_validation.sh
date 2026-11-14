#!/bin/bash
python3 galaxy_simulations/galaxy_scale_sim.py --m-star 1e11 --r-eff 4 --k-eff 0.1 --tag MW
python3 galaxy_simulations/analyze_dwarf_galaxy.py
