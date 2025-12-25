# Environment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Mercury

python github/validation/solar_system/mercury_precession_fit.py
stdout: "Predicted precession : ... arcsec/century"
stdout: "Observed  precession : 43.00 arcsec/century"
exit: 0

# Binary pulsar

python github/validation/binary_tests/binary_pulsar_decay_test.py
stdout: (empty)
exit: 0

# Galaxy

python github/galaxy_simulations/galaxy_scale_sim.py --m-star 1e11 --r-eff 4 --k-eff 0.1
stdout: "Simulation complete. Key numbers:"
files: github/galaxy_simulations/results/galaxy_scale/galaxy_*.npz
files: github/galaxy_simulations/results/galaxy_scale/galaxy_rotation_*.png
files: github/galaxy_simulations/results/galaxy_scale/galaxy_summary_*.json
exit: 0
