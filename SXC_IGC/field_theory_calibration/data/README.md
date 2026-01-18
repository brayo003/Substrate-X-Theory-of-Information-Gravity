# Data Directory

This directory contains simulation outputs in NPZ format. The files follow this naming convention:

- `galaxy_<TAG>_k_<k_eff>.npz`: Raw simulation data for a galaxy
  - TAG: Galaxy identifier (Dwarf, M31, M33, MW)
  - k_eff: Coupling parameter value (e.g., 3.00e-01 for 0.3)

- `galaxy_rotation_<TAG>_k_<k_eff>.png`: Rotation curve plot
- `galaxy_summary_<TAG>_k_<k_eff>.json`: Summary statistics

## Example Data

- Dwarf galaxy (k_eff = 0.3): `galaxy_Dwarf_k_3.00e-01.npz`
- Andromeda (M31) galaxy: `galaxy_M31_k_3.00e-01.npz`
- Triangulum (M33) galaxy: `galaxy_M33_k_3.00e-01.npz`
- Milky Way simulations with different k_eff values

## Data Format

NPZ files contain numpy arrays with the following structure:
- `radius`: Radial distance from center (kpc)
- `velocity`: Rotation velocity (km/s)
- `velocity_newt`: Newtonian prediction (km/s)
- `density`: Mass density profile (M_sun/kpc^3)
- `time`: Simulation timesteps (Gyr)
