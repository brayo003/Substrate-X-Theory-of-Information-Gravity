import numpy as np
import json
import os
import sys

print("=== SXC-IGC UNIFIED STABILITY VALIDATION ===\n")

# --- Import the Core Engine (now in the same directory) ---
try:
    # First, try to import from the current directory
    from sxc_igc_core import SXC_IGC_Core
    print("✅ Core engine module imported successfully.\n")
except ImportError:
    # If that fails, create the core class directly in the script.
    # (We'll define the class from your earlier code as a fallback)
    print("⚠️  Could not import from file. Using inline class definition.\n")
    # We'll define it inline later if needed.

# ========== TEST 1: DETERMINISTIC REPRODUCIBILITY ==========
print("=== TEST 1: DETERMINISTIC REPRODUCIBILITY ===")
np.random.seed(42)  # Fixed seed for reproducibility

config = {
    "initial_state": np.array([0.0]),
    "observables": {
        "norm_volume": np.random.randn(1000),
        "norm_volatility": np.random.randn(1000)
    },
    "coefficients": {"alpha": 0.5, "beta": -0.2},
    "time_step": 0.01
}

# Use the local definition if import failed
if 'SXC_IGC_Core' not in locals():
    # Define the class directly (copied from your earlier code)
    import numpy as np
    import json
    import logging
    from typing import Dict, Any
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger("SXC-IGC-Core")
    class SXC_IGC_Core:
        def __init__(self, system_config: Dict[str, Any], calibration_file: str = None):
            self.system_state = system_config.get("initial_state", np.zeros(1))
            self.observables = system_config.get("observables", {})
            self.coefficients = system_config.get("coefficients", {"alpha": 1.0, "beta": 1.0})
            self.time_step = system_config.get("time_step", 1.0)
            self.history = []
            if calibration_file:
                self.load_calibration(calibration_file)
        def load_calibration(self, filepath: str):
            try:
                with open(filepath, "r") as f:
                    calibrated_coeffs = json.load(f)
                    self.coefficients.update(calibrated_coeffs)
            except Exception:
                pass
        def substrate_x(self, t: int, observables: Dict[str, np.ndarray]) -> float:
            alpha = self.coefficients.get("alpha", 1.0)
            beta = self.coefficients.get("beta", 1.0)
            norm_volume = observables.get("norm_volume", np.array([0.0]))[t]
            norm_volatility = observables.get("norm_volatility", np.array([0.0]))[t]
            return alpha * norm_volume + beta * norm_volatility
        def step(self, t: int):
            x_t = self.substrate_x(t, self.observables)
            self.system_state = self.system_state + self.time_step * x_t
            self.history.append(self.system_state.copy())
        def run(self, steps: int):
            for t in range(steps):
                self.step(t)
        def get_history(self):
            return np.array(self.history)

engine1 = SXC_IGC_Core(config)
engine2 = SXC_IGC_Core(config)

engine1.run(steps=500)
engine2.run(steps=500)

history1 = engine1.get_history()
history2 = engine2.get_history()

if np.array_equal(history1, history2):
    print("✅ PASS: Engine is perfectly deterministic. Identical inputs → identical outputs.\n")
else:
    max_diff = np.max(np.abs(history1 - history2))
    print(f"❌ FAIL: Engine is non-deterministic. Max difference: {max_diff}\n")

# ========== TEST 2: LONG-RUN STABILITY (17k+ STEPS) ==========
print("=== TEST 2: LONG-RUN STABILITY ===")
np.random.seed(123)
config_long = {
    "initial_state": np.array([0.0]),
    "observables": {
        "norm_volume": np.random.randn(20000),
        "norm_volatility": np.random.randn(20000)
    },
    "coefficients": {"alpha": 0.1, "beta": -0.05},
    "time_step": 0.001
}

engine_long = SXC_IGC_Core(config_long)
target_steps = 17547

try:
    engine_long.run(steps=target_steps)
    history_long = engine_long.get_history()
    final_state = history_long[-1]
    max_abs = np.max(np.abs(history_long))
    
    print(f"✅ Engine completed {target_steps} steps without error.")
    print(f"   Final state: {final_state[0]:.6e}")
    print(f"   Max absolute value during run: {max_abs:.6e}")
    
    if max_abs > 1e6:
        print("   ⚠️  Note: Large state drift observed, but engine did not crash.\n")
    else:
        print("   Engine remained numerically bounded.\n")
except Exception as e:
    print(f"❌ Engine crashed: {e}\n")

# ========== TEST 3: DOMAIN COEFFICIENT SANITY CHECK ==========
print("=== TEST 3: DOMAIN COEFFICIENT SANITY CHECK ===")
# Paths relative to the DCIF directory
module_paths = [
    "dcif_modules/finance_module/coefficients.json",
    "dcif_modules/seismic_module/coefficients.json",
    "dcif_modules/particle_physics_module/coefficients.json"
]

for path in module_paths:
    if os.path.exists(path):
        try:
            with open(path) as f:
                coeff = json.load(f)
            mod_coeff = coeff.get('coefficients', {})
            extreme = []
            for key, val in mod_coeff.items():
                if isinstance(val, (int, float)):
                    if abs(val) > 1e9 or (0 < abs(val) < 1e-9):
                        extreme.append((key, val))
            if extreme:
                print(f"⚠️  {path}: Contains extreme coefficients: {extreme}")
            else:
                print(f"✅ {path}: Coefficients within plausible range.")
        except Exception as e:
            print(f"❌ {path}: Error reading - {e}")
    else:
        print(f"  {path}: Not found (may be OK).")

print("\n=== VALIDATION COMPLETE ===")
print("Summary of 'stable engine' criteria:")
print("1. Deterministic: " + ("YES" if np.array_equal(history1, history2) else "NO"))
print("2. Long-run stable (no crash): " + ("YES" if 'history_long' in locals() else "NO"))
print("3. No extreme coefficients in core modules: Check above.")
print("\nA stable engine can produce meaningful results; interpretation is separate.")
