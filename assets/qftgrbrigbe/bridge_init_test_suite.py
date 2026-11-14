import numpy as np

# -----------------------------
# SXC-IGC V12 Core
# -----------------------------
def v12_engine(x, r, a, b, dt=0.01):
    dx = (r * x) + (a * x**2) - (b * x**3)
    return x + dx * dt

# -----------------------------
# Phase 1: Substrate Mapping
# -----------------------------
def run_phase_1_tests():
    print("--- [SXC-IGC] Phase 1: Substrate Coupling Density Scan ---")

    # Resolution scale = effective coupling bandwidth
    resolutions = {
        "Planck-scale": 1e-35,
        "Quantum-scale": 1e-25,
        "Micro-scale": 1e-15
    }

    steps = 5000
    dt = 0.01

    for label, res in resolutions.items():
        x = 0.01
        r = 1.0
        a = 0.5
        b = 1.5

        saturation_step = None

        for i in range(steps):
            # Resolution limits coupling growth rate
            effective_r = r * (1.0 / (1.0 + res * 1e35))

            x = v12_engine(x, effective_r, a, b, dt)

            if x > 0.95:
                saturation_step = i
                break

        if saturation_step is not None:
            print(f"{label}: Saturation onset at step {saturation_step}")
        else:
            print(f"{label}: No saturation within integration window")

if __name__ == "__main__":
    run_phase_1_tests()
