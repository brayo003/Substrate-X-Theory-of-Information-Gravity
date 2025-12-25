# Substrate X Theory of Information Gravity

This repository contains the implementation and verification of the Substrate X Theory of Information Gravity, including numerical solvers and galaxy-scale simulations.

## Repository Structure

- `src/`: Core implementation of the PDE solver and numerical methods
- `galaxy_simulations/`: Scripts for running galaxy-scale simulations
- `notebooks/`: Jupyter notebooks for demonstration and analysis
- `data/`: Simulation outputs and results (not included in git, see data/README.md)

## Getting Started

1. Install dependencies:
```bash
pip install -r galaxy_simulations/requirements.txt
```

2. Run a galaxy simulation:
```bash
python galaxy_simulations/galaxy_scale_sim.py --tag Dwarf --m-star 1e8 --r-eff 1 --k-eff 0.3 --sigma 2
```

## Key Results

- Dwarf galaxy rotation curves with k_eff = 0.3
- M31 (Andromeda) and M33 galaxy simulations
- Milky Way simulations with different k_eff values
- Raw NPZ output files for verification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
