import numpy as np
import sys
sys.path.append('.')  # Adjust path to your core engine
# Assuming your core class is accessible
from sxc_igc_core import SXC_IGC_Core

print("=== TEST 1: DETERMINISTIC REPRODUCIBILITY ===\n")
# Create identical configuration
config = {
    "initial_state": np.array([0.0]),
    "observables": {
        "norm_volume": np.random.randn(1000),
        "norm_volatility": np.random.randn(1000)
    },
    "coefficients": {"alpha": 0.5, "beta": -0.2},
    "time_step": 0.01
}

# Run engine twice with identical config
engine1 = SXC_IGC_Core(config)
engine2 = SXC_IGC_Core(config)

engine1.run(steps=500)
engine2.run(steps=500)

history1 = engine1.get_history()
history2 = engine2.get_history()

# Check if outputs are bitwise identical
if np.array_equal(history1, history2):
    print("✅ PASS: Engine is perfectly deterministic. Identical inputs → identical outputs.")
else:
    max_diff = np.max(np.abs(history1 - history2))
    print(f"❌ FAIL: Engine is non-deterministic. Max difference: {max_diff}")
