import numpy as np
import sys
sys.path.append('.')
from sxc_igc_core import SXC_IGC_Core

print("\n=== TEST 2: NUMERICAL STABILITY UNDER EXTREME INPUTS ===\n")

test_cases = [
    ("High Volatility Spike", {"norm_volume": np.zeros(1000), "norm_volatility": 1e6 * np.ones(1000)}),
    ("Large Co-moving Inputs", {"norm_volume": 1e3 * np.random.randn(1000), "norm_volatility": 1e3 * np.random.randn(1000)}),
    ("NaN/Inf Propagation", {"norm_volume": np.full(1000, np.nan), "norm_volatility": np.full(1000, np.inf)}),
]

for name, obs in test_cases:
    config = {
        "initial_state": np.array([0.0]),
        "observables": obs,
        "coefficients": {"alpha": 1.0, "beta": 1.0},
        "time_step": 0.01
    }
    try:
        engine = SXC_IGC_Core(config)
        engine.run(steps=100)
        history = engine.get_history()
        if np.any(np.isnan(history)) or np.any(np.isinf(history)):
            print(f"⚠️  {name}: Engine produced NaN/Inf. Unstable with pathological inputs.")
        else:
            print(f"✅ {name}: Engine remained stable (no NaN/Inf).")
    except Exception as e:
        print(f"❌ {name}: Engine crashed: {e}")
